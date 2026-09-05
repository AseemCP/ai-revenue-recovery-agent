def generate_recovery_message(payment, recovery_action):

    amount = payment["amount"]/100

    if recovery_action == "ask_user_to_retry_payment":
        return (
            f"Your payment of ₹{amount:.2f} could not be completed. "
            "Please try the payment again using the link below."
        )

    if recovery_action == "suggest_alternative_payment_method":
        return (
            f"Your payment of ₹{amount:.2f} could not be completed "
            "because the current payment method may not have sufficient funds. "
            "Please try another payment method."
        )

    if recovery_action == "update_payment_method":
        return (
            f"Your payment of ₹{amount:.2f} could not be completed "
            "because there may be an issue with your card. "
            "Please update your payment method and try again."
        )

    if recovery_action == "manual_review":
        return (
            "We couldn't complete your payment. "
            "Our team will review the issue and get back to you."
        )

    return "Please contact support regarding your payment."