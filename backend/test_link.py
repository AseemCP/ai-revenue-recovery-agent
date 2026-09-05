from payment_link import create_retry_payment_link
print("payment link")
payment = {
    "amount": 500000,
    "currency": "INR",
    "email": "void@razorpay.com",
    "contact": "+919999999912"
}

link = create_retry_payment_link(payment)

print(link)