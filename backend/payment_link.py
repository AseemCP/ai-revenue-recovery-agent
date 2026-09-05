import os
import razorpay
from dotenv import load_dotenv
load_dotenv()

razorpay_client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET")
    )
)

def create_retry_payment_link(payment):

    amount = payment["amount"]

    data = {
        "amount" : amount,
        "currency" : payment["currency"],
        "reference_id" : payment["id"],
        "description" : "Retry failed payment",
        "customer" : {
            "email" : payment["email"],
            "contact" : payment["contact"]
        }
    }

    payment_link = razorpay_client.payment_link.create(data)

    return {
        "id": payment_link["id"],
        "short_url": payment_link["short_url"]
    }


def find_payment_link_by_refrence_id(reference_id):
    payment_links = razorpay_client.payment_link.all()

    for link in payment_links["items"]:
        if link.get("reference_id") == reference_id:
            return {
                "id" : link["id"],
                "short_url" : link["short_url"],
                "reference_id" : link["reference_id"]
            }

def find_payment_link_by_description(description):

    if not description:
        return None

    if description.startswith("#"):
        return "plink_"+description[1:]

    return None