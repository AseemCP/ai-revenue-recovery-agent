def classify_test_payment(payment):

    card = payment.get("card") or {}

    # Razorpay returns the last 4 digits separately,
    # so combine the known test-card prefix with last4.
    token_iin = card.get("token_iin")
    last4 = card.get("last4")

    test_cards = {
        # Visa
        ("410028000", "0000"): "payment_timed_out",
        ("410028000", "0001"): "insufficient_fund",
        ("410028000", "0002"): "payment_cancelled",
        ("410028000", "0003"): "card_declined",
        ("410028000", "0006"): "card_disabled_for_online_payments",
        ("410028000", "0007"): "gateway_technical_error",
        ("410028000", "0008"): "card_number_invalid",
        ("410028000", "0009"): "authentication_failed",
    }

    return test_cards.get(
        (token_iin, last4),
        payment.get("error_reason")
    )

def get_recovery_action(error_reason, error_code=None):

    error_reason = (error_reason or "").strip().lower()
    error_code = (error_code or "").strip().upper()

    if error_reason == "payment_timed_out":
        return {
            "action": "ask_user_to_retry_payment",
            "priority": "HIGH",
            "reason": "Payment timed out due to a temporary issue; retry may succeed"
        }

    if error_reason == "insufficient_fund":
        return {
            "action": "suggest_alternative_payment_method",
            "priority": "HIGH",
            "reason": "Insufficient funds detected; another payment method may succeed"
        }

    if error_reason == "payment_cancelled":
        return {
            "action": "ask_user_to_retry_payment",
            "priority": "MEDIUM",
            "reason": "Payment was cancelled; the customer can try the payment again"
        }

    if error_reason == "card_declined":
        return {
            "action": "suggest_alternative_payment_method",
            "priority": "HIGH",
            "reason": "Card was declined; another payment method may succeed"
        }

    if error_reason == "card_disabled_for_online_payments":
        return {
            "action": "suggest_alternative_payment_method",
            "priority": "HIGH",
            "reason": "Card is disabled for online payments; another payment method should be used"
        }

    if error_reason == "card_number_invalid":
        return {
            "action": "update_payment_method",
            "priority": "MEDIUM",
            "reason": "The card number appears to be invalid; the customer should check or update the payment method"
        }

    if error_reason == "gateway_technical_error":
        return {
            "action": "ask_user_to_retry_payment",
            "priority": "MEDIUM",
            "reason": "A temporary gateway issue occurred; retrying the payment may succeed"
        }

    if error_reason == "authentication_failed":
        return {
            "action": "ask_user_to_retry_payment",
            "priority": "HIGH",
            "reason": "Payment authentication failed; the customer can try again"
        }

    # Normal Razorpay failure
    if error_reason == "payment_failed":
        return {
            "action": "ask_user_to_retry_payment",
            "priority": "HIGH",
            "reason": "Payment authorization failed; retry may succeed"
        }

    if error_reason in ["card_expired", "expired_card"]:
        return {
            "action": "update_payment_method",
            "priority": "MEDIUM",
            "reason": "The customer's card appears to be expired"
        }

    if error_code == "BAD_REQUEST_ERROR":
        return {
            "action": "ask_user_to_retry_payment",
            "priority": "MEDIUM",
            "reason": "Payment request was rejected and retry may succeed"
        }

    return {
        "action": "manual_review",
        "priority": "MEDIUM",
        "reason": "Unknown payment failure requires further investigation"
    }