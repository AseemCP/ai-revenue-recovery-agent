# AI Revenue Recovery Agent

An AI-powered payment recovery system that automatically analyzes failed Razorpay payments, determines an appropriate recovery strategy, generates a customer-friendly recovery message, and provides actionable recovery options.

## Overview

Failed payments can lead to lost revenue and abandoned transactions. Different payment failures require different recovery strategies.

For example:

- A temporary payment timeout can be retried.
- Insufficient funds may require another payment method.
- A declined card may require an alternative payment method.
- A card disabled for online payments should not simply be retried.
- Authentication failures may require the customer to authenticate again.

This project automates this decision-making process using a combination of Razorpay webhooks, rule-based payment classification, AI-generated messaging, and a recovery dashboard.

---

## Problem

Payment failures are not all the same.

A generic "Please try again" message may not be appropriate for every failure. Sending the wrong recovery action can reduce the chance of successfully recovering the payment.

The goal of this project is to automatically:

1. Detect failed payments.
2. Identify the reason for the failure.
3. Determine the best recovery action.
4. Generate a personalized customer message.
5. Provide a retry payment link when appropriate.
6. Track recovery attempts and outcomes.

---

## Solution

The AI Revenue Recovery Agent processes payment failures through an automated pipeline.

`
                    Razorpay
                       |
                       v
                Payment Webhook
                       |
                       v
                  FastAPI API
                       |
                       v
             Payment Classification
                       |
                       v
             Recovery Decision Engine
                       |
             +---------+---------+
             |                   |
             v                   v
       Recovery Action      AI Message
             |                   |
             +---------+---------+
                       |
                       v
                Recovery Attempt
                       |
                       v
                  Dashboard


### BLOCK 4 — Key Features + Payment Detection

``
## Key Features

### Payment Failure Detection

Razorpay payment failure events are received through a webhook and processed by the backend.

The system extracts information such as:

- Payment ID
- Order ID
- Amount
- Currency
- Payment method
- Card information
- Error code
- Error reason
- Error description

### Payment Failure Classification

The system can classify Razorpay test payment scenarios into specific failure types.

Supported scenarios include:

- `payment_timed_out`
- `insufficient_fund`
- `payment_cancelled`
- `card_declined`
- `card_disabled_for_online_payments`
- `card_number_invalid`
- `gateway_technical_error`
- `authentication_failed`

For Razorpay test payments, the system uses the test card information to identify the simulated failure scenario.

---

## Recovery Decision Engine

After classification, the system selects an appropriate recovery action.

| Failure | Recovery Action |
|---|---|
| Payment timed out | Ask user to retry payment |
| Insufficient funds | Suggest alternative payment method |
| Payment cancelled | Ask user to retry payment |
| Card declined | Suggest alternative payment method |
| Card disabled for online payments | Suggest alternative payment method |
| Invalid card number | Update payment method |
| Gateway technical error | Ask user to retry payment |
| Authentication failed | Ask user to retry payment |

Each recovery decision also contains:

- Action
- Priority
- Reason

This allows the system to explain why a particular recovery strategy was selected.

---

## AI Recovery Messages

The project uses Google's Gemini API to generate short, customer-friendly recovery messages.

The AI message generator receives information such as:

- Payment amount
- Failure reason
- Recovery action
- Payment retry link

The generated message follows rules such as:

- Do not expose technical error codes.
- Do not blame the customer.
- Keep the message concise.
- Do not invent payment information.
- Include the retry link when one is available.
- Recommend an alternative payment method when appropriate.

Example:

> We're sorry, but your payment could not be completed. Please try using a different card or an alternative payment method to complete your transaction.

---

## Retry Payment Links

When the selected recovery action is:

`ask_user_to_retry_payment`

the backend creates a Razorpay payment link.

The link is:

- Created for the failed payment.
- Stored with the recovery attempt.
- Included in the AI-generated customer message.
- Displayed in the recovery dashboard.

This allows the customer to attempt the payment again without manually recreating the transaction.

---

## Recovery Dashboard

The frontend provides a monitoring dashboard for payment recovery.

The dashboard displays:

- Failed payments
- Recovery attempts
- Successful recoveries
- Failed retries
- Pending recoveries
- Recovery rate
- Total amount recovered
- Recovery statistics
- AI recovery messages
- Recovery decisions
- Priority
- Failure reason
- Retry count
- Payment retry links

The dashboard automatically refreshes recovery information periodically so that new webhook events and recovery attempts appear without manually refreshing the page.

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Razorpay API
- Razorpay Webhooks
- Google Gemini API

### Frontend

- HTML
- CSS
- JavaScript
- Chart.js

### Development

- Git
- GitHub
- Uvicorn

---

## Backend Architecture

backend/
│
├── main.py
├── database.py
├── models.py
├── recovery.py
├── ai_message.py
├── message_generator.py
├── payment_link.py
├── test_link.py
└── createtables.py

##Main Components
main.py

Contains the FastAPI application, webhook handling, dashboard APIs, and recovery processing.

models.py

Contains SQLAlchemy database models for:

Failed payments
Recovery attempts
Recovery decisions
recovery.py

Contains the recovery decision logic and payment failure classification.

message_generator.py

Generates customer-facing recovery messages using Gemini.

payment_link.py

Handles creation of Razorpay payment links.

database.py

Configures the SQLAlchemy database connection.



## Database

The system stores recovery information in PostgreSQL.

### Failed Payments

Stores information about failed Razorpay payments.

### Recovery Attempts

Tracks recovery attempts, including:

- Original payment
- Retry payment link
- Retry payment
- Amount
- Retry count
- Recovery status

### Recovery Decisions

Stores:

- Recovery action
- Priority
- Reason
- AI-generated customer message
- Associated recovery attempt

---

## Getting Started

### 1. Clone the repository

``
git clone https://github.com/AseemCP/ai-revenue-recovery-agent.git
cd ai-revenue-recovery-agent

2.Create a Python virtual environment
python -m venv venv

Activate it on Windows:
venv\Scripts\activate

3. Install backend dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv razorpay google-genai


### 4. Configure environment variables

Create:

``
backend/.env
Example:
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
GENAI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_database_url

Never commit .env or API keys to GitHub.

5. Start the backend

From the project directory:
uvicorn backend.main:app --reload
The backend runs locally at:
http://127.0.0.1:8000

6. Start the frontend

Open the frontend using the project's frontend setup.
The frontend communicates with the FastAPI backend to retrieve dashboard information.


## Razorpay Webhook

For local development, Razorpay needs an externally accessible webhook endpoint.

A tunneling service can be used to expose the local FastAPI server.

Example flow:


Razorpay
    |
    v
Public Webhook URL
    |
    v
Local Tunnel
    |
    v
FastAPI
    |
    v
Recovery Agent

The tunnel is required for Razorpay to reach the locally running backend.



## Example Recovery Flow

Consider a simulated insufficient-funds payment.

Payment Failed
      |
      v
Razorpay Webhook
      |
      v
Card/Test Payment Classification
      |
      v
insufficient_fund
      |
      v
suggest_alternative_payment_method
      |
      v
HIGH Priority
      |
      v
Gemini generates customer message
      |
      v
Recovery decision stored
      |
      v
Dashboard updated

For a retryable payment failure:

Payment Failed
      |
      v
Failure Classification
      |
      v
ask_user_to_retry_payment
      |
      v
Create Razorpay Payment Link
      |
      v
Generate AI Recovery Message
      |
      v
Display Retry Payment button


## Dashboard

The dashboard provides a centralized view of payment recovery activity.

It allows the recovery process to be monitored through:

- Recovery metrics
- Recovery statistics chart
- AI decisions
- Recovery priorities
- Failure reasons
- Recovery status
- Retry counts
- Retry payment links
- AI-generated customer messages

---

## Challenges & Technical Obstacles

### Handling Different Payment Failures

A major challenge was that Razorpay test payments can expose generic failure information while the test cards represent different simulated scenarios.

The project therefore uses the available test-card information to classify the simulated payment failure before selecting the recovery action.

### Choosing the Correct Recovery Strategy

Different failures require different actions.

Instead of applying one recovery strategy to every failed payment, the recovery decision engine maps each failure scenario to an appropriate action.

### AI Message Generation

The AI must generate useful customer messages without exposing internal payment errors or inventing information.

The prompt therefore restricts the AI's output based on the selected recovery action.

---

### Payment Link Integration

Retryable failures require an actual payment recovery path rather than only a message.

The system creates a Razorpay payment link and associates it with the recovery attempt.

### Dashboard Synchronization

The frontend periodically requests updated recovery data from the backend so that newly processed payment failures appear automatically.

---

## Future Improvements

Potential future improvements include:

- Automated email/SMS/WhatsApp delivery of recovery messages
- More advanced ML-based failure prediction
- Customer-level recovery strategy optimization
- Recovery success probability scoring
- Automated retry scheduling
- Multi-payment-method recovery orchestration
- Production-grade webhook security and deployment
- Advanced recovery analytics
- A/B testing of recovery messages

---

## Project Status

The project currently demonstrates an end-to-end payment recovery workflow using Razorpay test payments:

Payment Failure
      ↓
Webhook Detection
      ↓
Failure Classification
      ↓
Recovery Decision
      ↓
AI Message Generation
      ↓
Payment Link / Alternative Method
      ↓
Recovery Tracking
      ↓
Dashboard


Author

Aseem C P

AI Revenue Recovery Agent

Razorpay AI Builder Internship 2026
