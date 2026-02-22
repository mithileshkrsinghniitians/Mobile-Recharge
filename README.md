# Mobile-Recharge

Mobile Recharge App - Scalable Cloud Programming

## Overview

A cloud-native mobile recharge application that allows users to top up mobile numbers with secure payment processing, real-time SMS notifications, and automated invoice generation.

## Architecture Diagram

![Mobile Recharge Application Architecture](Architect%20Diagram/Mobile%20Recharge%20Application%20Architect%20Diagram.jpeg)

## Architecture

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python) deployed on AWS Elastic Beanstalk via Docker
- **Payment Processing:** AWS Lambda + Stripe API (with automatic stub fallback)
- **Invoice Generation:** AWS Lambda (generates PDF invoices)
- **Database:** Amazon DynamoDB (user profiles and payment records)
- **SMS Notifications:** Amazon SNS
- **Admin Authentication:** Salesforce OAuth
- **CI/CD:** GitHub Actions (Docker build, push to Docker Hub, deploy to Elastic Beanstalk)

## Application Flow

1. User verifies mobile number and creates a profile (stored in DynamoDB)
2. User enters mobile number and recharge amount (€10 - €100)
3. Payment is processed through Stripe API via AWS Lambda
4. SMS notification is sent to the user via Amazon SNS
5. User can download a PDF invoice generated via the Invoice API

## Project Structure

```
├── backend/
│   ├── app.py                  # Flask application
│   ├── templates/
│   │   └── index.html          # Main UI
│   ├── requirements.txt
│   └── Dockerfile
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js              # Recharge and payment validation
│       └── profile.js          # User profile management
└── .github/
    └── workflows/
        └── deploy.yml          # CI/CD pipeline
```

## AWS Services Used

- **Elastic Beanstalk** - Hosts the Flask application
- **Lambda** - Serverless payment and invoice processing
- **API Gateway** - REST API endpoints for Lambda functions
- **DynamoDB** - NoSQL database for users and payments
- **SNS** - SMS notifications
- **S3** - Invoice PDF storage

## API Documentation

### Base URLs

| Service | Base URL |
|---------|----------|
| Payment API (Lambda) | `https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod` |
| Invoice API (Lambda) | `https://di8irmc06g.execute-api.us-east-1.amazonaws.com` |
| User Management (Flask) | Your deployed Elastic Beanstalk URL |

---

### 1. Process Payment

Processes a mobile recharge payment through Stripe.

**Endpoint:** `POST /payments`

**Base URL:** `https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod`

**Headers:**

| Header | Value |
|--------|-------|
| Content-Type | `application/json` |

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mobileNumber` | string | Yes | Mobile number with country code (e.g. `+353871234567`) |
| `amount` | number | Yes | Recharge amount in EUR (min: 10, max: 100, decimals allowed) |

**Example Request:**

```bash
curl -X POST https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod/payments \
  -H "Content-Type: application/json" \
  -d '{
    "mobileNumber": "+353871234567",
    "amount": 22.50
  }'
```

**Success Response (200):**

```json
{
  "paymentId": "pay_a1b2c3d4e5",
  "status": "SUCCEEDED"
}
```

**Error Responses:**

| Status | Response | Reason |
|--------|----------|--------|
| 400 | `{"message": "Amount must be a number"}` | Non-numeric amount provided |
| 400 | `{"message": "Amount must be between 10 and 100"}` | Amount out of range |
| 400 | `{"message": "Invalid mobile number format. Use + followed by 6–15 digits."}` | Invalid mobile format |
| 502 | `{"paymentId": "pay_xxx", "message": "Payment gateway rejected the request"}` | Stripe rejected the payment |
| 500 | `{"message": "Payment processing failed"}` | Internal server error |

**Notes:**
- Amount is converted to cents internally (e.g. `22.50` becomes `2250` cents) before sending to Stripe
- On successful payment, an SMS notification is sent to the mobile number via Amazon SNS
- If Stripe is unreachable (network issue/timeout), a stub response is used automatically as fallback
- Payment records are stored in DynamoDB with status tracking (`PENDING` → `SUCCEEDED` / `FAILED`)

---

### 2. Generate Invoice

Generates a PDF invoice for a completed payment.

**Endpoint:** `POST /invoice`

**Base URL:** `https://di8irmc06g.execute-api.us-east-1.amazonaws.com`

**Headers:**

| Header | Value |
|--------|-------|
| Content-Type | `application/json` |

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `paymentId` | string | Yes | Payment ID returned from the payment API |
| `amount` | number | Yes | Recharge amount in EUR |
| `mobileNumber` | string | Yes | Mobile number with country code |

**Example Request:**

```bash
curl -X POST https://di8irmc06g.execute-api.us-east-1.amazonaws.com/invoice \
  -H "Content-Type: application/json" \
  -d '{
    "paymentId": "pay_a1b2c3d4e5",
    "amount": 22.50,
    "mobileNumber": "+353871234567"
  }'
```

**Success Response (200):**

```json
{
  "pdf_url": "https://s3.amazonaws.com/bucket-name/invoice.pdf"
}
```

**Error Response:**

| Status | Response | Reason |
|--------|----------|--------|
| 500 | `{"error": "Invoice generation failed"}` | Internal server error |

**Notes:**
- The `pdf_url` is a link to the generated PDF invoice stored on S3
- Call this API only after a successful payment (`status: "SUCCEEDED"`)

---

### 3. Check Mobile Number

Checks if a mobile number already has a profile in the system.

**Endpoint:** `GET /check-mobile`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `mobile` | string | Yes | Mobile number to check |

**Example Request:**

```bash
curl "https://your-app-url/check-mobile?mobile=353871234567"
```

**Responses:**

```json
// User exists
{"exists": true}

// User does not exist
{"exists": false}

// Invalid input (400)
{"error": "Invalid mobile number"}
```

---

### 4. Create User Profile

Creates a new user profile in DynamoDB. Required for first-time users before making a payment.

**Endpoint:** `POST /create-profile`

**Headers:**

| Header | Value |
|--------|-------|
| Content-Type | `application/json` |

**Request Body:**

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `firstName` | string | Yes | Letters only (A-Z, a-z), max 100 characters |
| `lastName` | string | Yes | Letters only (A-Z, a-z), max 100 characters |
| `email` | string | Yes | Valid email format |
| `mobile` | string | Yes | Mobile number with country code |

**Example Request:**

```bash
curl -X POST https://your-app-url/create-profile \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@email.com",
    "mobile": "+353871234567"
  }'
```

**Responses:**

```json
// Success (200)
{"status": "success"}

// Missing fields (400)
{"error": "Missing required fields"}

// Server error (500)
{"error": "Unable to create profile"}
```

---

### Quick Integration Example (JavaScript)

```javascript
// Step 1: Process Payment
const paymentResponse = await fetch(
  "https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod/payments",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mobileNumber: "+353871234567",
      amount: 22.50
    })
  }
);
const paymentData = await paymentResponse.json();
console.log(paymentData.paymentId); // "pay_a1b2c3d4e5"
console.log(paymentData.status);    // "SUCCEEDED"

// Step 2: Generate Invoice (only after successful payment)
if (paymentData.status === "SUCCEEDED") {
  const invoiceResponse = await fetch(
    "https://di8irmc06g.execute-api.us-east-1.amazonaws.com/invoice",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        paymentId: paymentData.paymentId,
        amount: 22.50,
        mobileNumber: "+353871234567"
      })
    }
  );
  const invoiceData = await invoiceResponse.json();
  window.open(invoiceData.pdf_url, "_blank"); // Opens PDF
}
```