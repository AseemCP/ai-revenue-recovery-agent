from ai_message import generate_ai_message
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import FastAPI, Request
import os
import razorpay
from models import FailedPayment, RecoveryAttempt, RecoveryDecision
from database import SessionLocal
from recovery import get_recovery_action, classify_test_payment
from payment_link import create_retry_payment_link, find_payment_link_by_description
from dotenv import load_dotenv
from sqlalchemy import func

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

razorpay_client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)

class OrderRequest(BaseModel):
    amount : float


@app.get("/")
def home():
    return {"message": "Revenue Recovery API is running"}


@app.post("/create-order")
def create_order(order : OrderRequest):
    order.amount = order.amount*100

    order_data = {
        "amount": order.amount,
        "currency": "INR",
        "receipt": "rzp_reciept_1"
    }

    razorpay_order = razorpay_client.order.create(data=order_data)

    return {
        "order_id": razorpay_order["id"],
        "amount": razorpay_order["amount"],
        "currency": razorpay_order["currency"],
        "key_id": os.getenv("RAZORPAY_KEY_ID")
    }

@app.post("/webhook/razorpay")
async def razorpay_webhook(request:Request):
    data = await request.json()

    event = data.get("event")

    if event == "payment.failed":

        payment = data["payload"]["payment"]["entity"]

        payment_id = payment["id"]
        order_id = payment["order_id"]
        amount = payment["amount"]
        currency = payment["currency"]
        email = payment["email"]
        contact = payment["contact"]
        error_code = payment["error_code"]
        error_description = payment["error_description"]
        error_reason = payment["error_reason"]

        print(payment)

        db = SessionLocal()
        
        existing_payment = db.query(FailedPayment).filter(FailedPayment.payment_id == payment_id).first()

        if existing_payment:
            print(f"Payment {payment_id} already exists. Skipping duplicate webhook.")
            db.close()
            return {"status": "ok", "message": "already processed"}

        retry_payment_link_id = find_payment_link_by_description(payment.get("description"))
        print(f"Possible retry Payment Link ID: {retry_payment_link_id}")

        if retry_payment_link_id:

            print("======Retry payment Failed======")
            print(f"Retry payment id : {payment_id}")
            print(f"Retry order id : {order_id}")
            print(f"Payment link id : {retry_payment_link_id}")

            attempt = (
                db.query(RecoveryAttempt).filter(RecoveryAttempt.retry_payment_link_id == retry_payment_link_id, RecoveryAttempt.status.in_(["pending", "failed"])).first()
            )

            if attempt:
                attempt.retry_payment_id = payment_id
                attempt.retry_count += 1
                attempt.status = "failed"

                db.commit()

                print("Retry payment marked as failed")
                print("Existing payment link will be reused")
                

                db.close()

                return {
                    "status" : "ok",
                    "message" : "retry payment failed",
                    "payment link id" : retry_payment_link_id
                }
            print("Payment link found, But No pending recovery attempt was found.")

        failed_payment = FailedPayment(
            payment_id = payment_id,
            order_id = order_id,
            amount = amount,
            currency = currency,
            email = email,
            contact = contact,
            error_code = error_code,
            error_description = error_description,
            error_reason = error_reason
        )
        db.add(failed_payment)

        classified_reason = classify_test_payment(payment)

        print("================================")
        print("PAYMENT CLASSIFICATION")
        print(f"Original reason : {error_reason}")
        print(f"Error code      : {error_code}")
        print(f"Classified reason: {classified_reason}")
        print("================================")

        decision = get_recovery_action(classified_reason, error_code)
        recovery_action = decision["action"]
        
        print(f"Recovery Action : {recovery_action}")
        print(f"Priority : {decision["priority"]}")
        print(f"Reason : {decision["reason"]}")

        retry_link_id = None
        retry_link_url = None

        if recovery_action == "ask_user_to_retry_payment":

            retry_link = create_retry_payment_link(payment)
            
            retry_link_id = retry_link["id"]
            retry_link_url = retry_link["short_url"]
            
                    
            attempt = RecoveryAttempt(
                    original_payment_id = payment["id"],
                    retry_payment_link_id = retry_link_id,
                    retry_link_url = retry_link_url,
                    retry_reference_id = payment_id,
                    retry_payment_id = None,
                    amount = amount,
                    status = "pending",
                    retry_count = 0
                    )
                            
            db.add(attempt)
            db.flush()

        else:

            attempt = RecoveryAttempt(
                    original_payment_id = payment["id"],
                    retry_payment_link_id = None,
                    retry_link_url = retry_link_url,
                    retry_reference_id = None,
                    retry_payment_id = None,
                    amount = amount,
                    status = "pending"
                    )
                                        
            db.add(attempt)
            db.flush()

        ai_message = generate_ai_message(payment,recovery_action,retry_link_url)
        print(f"Ai Recovery Message: {ai_message}")
        
        recovery_decision = RecoveryDecision(
            original_payment_id = payment_id,
            recovery_attempt_id = attempt.id,

            action = decision['action'],
            priority = decision['priority'],
            reason = decision['reason'],
            ai_message = ai_message
        )

        db.add(recovery_decision)

        db.commit()
        db.close()

        
        print(f"Retry Link : {retry_link_url}")
        
        
        
                
        
        print("=========================")
        print("RAZORPAY WEBHOOK RECIEVED")
        print("=========================")
        print(f"payment id : {payment_id}")
        print(f"order id : {order_id}")
        print(f"amount : {amount} paise")
        print(f"amount rs : {amount/100} rs")
        print(f"currency : {currency}")
        print(f"email : {email}")
        print(f"contact : {contact}")
        print(f"error_code : {error_code}")
        print(f"error_description : {error_description}")
        print(f"error_reason : {error_reason}")


    elif event == "payment_link.paid":

        payment_link = data["payload"]["payment_link"]["entity"]
        payment = data["payload"]["payment"]["entity"]

        print(payment_link)
        print(payment)

        retry_payment_link_id = payment_link["id"]
        retry_order_id = payment_link["order_id"]
        retry_payment_id = payment["id"]

        print(f"Payment ID : {retry_payment_id}")
        print(f"Retry Payment link ID : {retry_payment_link_id}")

        db = SessionLocal()

        attempt = (
            db.query(RecoveryAttempt).filter(RecoveryAttempt.retry_payment_link_id == retry_payment_link_id, RecoveryAttempt.status.in_(["pending","failed"])).first()
        )

        if not attempt:
            print(f"No pending recovery attempt found for Payment Link {retry_payment_link_id}")
            db.close()

            return {
                "status": "ok",
                "message": "Recovery attempt not found"
            }

        # Save the new Razorpay payment ID
        attempt.retry_order_id = retry_order_id
        attempt.retry_payment_id = retry_payment_id
        attempt.status = "successful"

        # Find the ORIGINAL failed payment
        original_payment = (
            db.query(FailedPayment)
            .filter(
                FailedPayment.payment_id == attempt.original_payment_id
            )
            .first()
        )

        if original_payment:
            original_payment.status = "successful"
            print("Original payment marked as Successful")
        else:
            print(
                f"Original payment {attempt.original_payment_id} "
                f"not found"
            )

        db.commit()

        print("Recovery Successful!")
        print(f"Original payment: {attempt.original_payment_id}")
        print(f"Retry payment: {attempt.retry_payment_id}")

        db.close()

        
    return {"status":"ok"}

@app.get("/dashboard/summary")
def dashboard_summary():

    db = SessionLocal()

    try:
        total_failed_payments = db.query(FailedPayment).count()

        total_recovery_attempts = db.query(RecoveryAttempt).count()

        successful_recoveries = (
            db.query(RecoveryAttempt)
            .filter(RecoveryAttempt.status == "successful")
            .count()
        )

        failed_retries = (
            db.query(func.coalesce(func.sum(RecoveryAttempt.retry_count), 0))
            .scalar()
        )


        pending_recoveries = (
            db.query(RecoveryAttempt)
            .filter(RecoveryAttempt.status == "pending")
            .count()
        )

        recovered_amount = (
            db.query(RecoveryAttempt.amount)
            .filter(RecoveryAttempt.status == "successful")
            .all()
        )

        total_amount_recovered = sum(
            amount[0] for amount in recovered_amount
        )

        recovery_rate = (
            (successful_recoveries / total_recovery_attempts) * 100
            if total_recovery_attempts > 0
            else 0
        )

        return {
            "total_failed_payments": total_failed_payments,
            "total_recovery_attempts": total_recovery_attempts,
            "successful_recoveries": successful_recoveries,
            "failed_retries": failed_retries or 0,
            "pending_recoveries": pending_recoveries,
            "total_amount_recovered_paise": total_amount_recovered,
            "total_amount_recovered_inr": total_amount_recovered / 100,
            "recovery_rate": round(recovery_rate, 2)
        }

    finally:
        db.close()

@app.get("/dashboard/recovery-attempts")
def recovery_attempts():

    db = SessionLocal()

    try:
        attempts = (
            db.query(RecoveryAttempt, RecoveryDecision)
            .outerjoin(
                RecoveryDecision,
                RecoveryDecision.recovery_attempt_id == RecoveryAttempt.id
            )
            .order_by(RecoveryAttempt.id.desc())
            .all()
        )

        result = []

        for attempt, decision in attempts:

            result.append({
                "payment_id": attempt.original_payment_id,
                "amount": attempt.amount / 100,

                "action": (
                    decision.action
                    if decision else "N/A"
                ),

                "priority": (
                    decision.priority
                    if decision else "N/A"
                ),

                "reason": (
                    decision.reason
                    if decision else "N/A"
                ),

                "ai_message": (
                    decision.ai_message
                    if decision else "N/A"
                ),


                "status": attempt.status,

                "retry_count": attempt.retry_count or 0,

                "retry_link" : attempt.retry_link_url
            })

        return result

    finally:
        db.close()