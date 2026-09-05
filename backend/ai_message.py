from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GENAI_API_KEY")
)


def generate_ai_message(payment, recovery_action, payment_link=None):

    amount = payment["amount"] / 100
    error_reason = payment["error_reason"]

    prompt = f"""
You are a payment recovery assistant.

Generate a short, polite and helpful message for a customer
whose payment failed.

Payment amount: ₹{amount:.2f}
Failure reason: {error_reason}
Recovery action: {recovery_action}
Payment retry link: {payment_link}

Rules:
- Do not blame the customer.
- Do not expose technical error codes.
- Keep the message under 50 words.
- Do not invent information.
- Do not invent a payment link.
- Only include the payment link if one is provided.
- Do not mention an account dashboard.
- Do not claim that money was debited unless that information is provided.
- Do not claim that a refund was issued unless that information is provided.

Follow the recovery action exactly:

1. If the action is "ask_user_to_retry_payment":
   Ask the customer to retry the payment.
   Include the payment link naturally if one is provided.

2. If the action is "suggest_alternative_payment_method":
   Tell the customer the payment could not be completed.
   Suggest trying another card or payment method.
   Do not tell them to retry the same payment method.

3. If the action is "ask_user_to_correct_card_details":
   Tell the customer that the card details may be incorrect.
   Ask them to check and correct the card details before trying again.

4. If the action is "wait_and_retry_later":
   Explain that there appears to be a temporary issue.
   Ask the customer to try again later.
   Do not provide a retry link unless one is provided.

5. If the action is "manual_review":
   Tell the customer that the payment could not be completed
   and requires further review.
   Do not invent a resolution or provide a retry link unless one is provided.

Return only the customer-facing message.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    return response.text.strip()