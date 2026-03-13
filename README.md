# Mobile Recharge Application

**Scalable Cloud Programming — National College of Ireland**

A cloud-native mobile top-up platform with Stripe payment processing, automated invoice generation, CAPTCHA verification, SMS notifications, Salesforce-authenticated admin panel, and real-time AWS CloudWatch monitoring.

---

## Architecture Diagram

![Mobile Recharge Application Architecture](Architect%20Diagram/Mobile%20Recharge%20Application%20Architect%20Diagram.jpeg)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.11 — Flask (Gunicorn) |
| Containerisation | Docker → Docker Hub |
| Hosting | AWS Elastic Beanstalk (Amazon Linux 2023) |
| Database | Amazon DynamoDB |
| Payment | AWS Lambda + Stripe API |
| Invoice | AWS Lambda → S3 (PDF) |
| CAPTCHA | AWS Lambda (custom image CAPTCHA) |
| SMS | Amazon SNS |
| Admin Auth | Salesforce OAuth 2.0 (username-password flow) |
| CI/CD | GitHub Actions |
| Monitoring | AWS CloudWatch (dashboards + alarms) |
| Code Quality | SonarQube, Pylint, Bandit |
| Testing | pytest (22 unit tests) |

---

## Project Structure

```
Mobile Recharge/
├── backend/
│   ├── app.py                    # Flask application — all routes
│   ├── requirements.txt          # Python dependencies
│   └── templates/
│       ├── index.html            # Main recharge UI
│       ├── pay.html              # Hosted payment page
│       ├── login.html            # Admin login form
│       ├── admin.html            # Admin dashboard (CRUD)
│       └── .env                  # Environment variables
├── static/
│   ├── css/
│   │   └── style.css             # Shared styles (all pages)
│   └── js/
│       ├── app.js                # Recharge form validation
│       ├── profile.js            # Profile modal logic
│       └── login.js              # Admin login fetch + redirect
├── tests/
│   ├── conftest.py               # Fixtures (mock DynamoDB, auth clients)
│   └── test_routes.py            # 22 pytest unit tests
├── Architect Diagram/
│   └── Mobile Recharge Application Architect Diagram.jpeg
├── Dockerfile                    # Python 3.11-slim, Gunicorn on port 8080
├── sonar-project.properties      # SonarQube configuration
├── .elasticbeanstalk/
│   └── config.yml                # EB app: Mobile Recharge, env: recharge-prod
└── .github/
    └── workflows/
        └── deploy.yml            # CI/CD pipeline
```

---

## AWS Services

| Service | Purpose |
|---|---|
| **Elastic Beanstalk** | Hosts the Dockerised Flask app (Docker Compose, Amazon Linux 2023) |
| **API Gateway** | REST endpoints routing traffic to Lambda functions |
| **Lambda** | Serverless payment processing, invoice generation, CAPTCHA |
| **DynamoDB** | NoSQL — `Users` table (PK: `mobile` as integer) |
| **S3** | Stores generated PDF invoices |
| **SNS** | Sends SMS confirmation to the recharged mobile number |
| **CloudWatch** | Dashboards, alarms, and log insights for monitoring |
| **IAM** | Roles and policies for Lambda and EB service access |

---

## Application Flow

```
User visits app
      │
      ▼
[Profile Modal]
  Enter mobile → /check-mobile (DynamoDB lookup)
  ├─ Exists → dismiss modal, proceed
  └─ New user → fill form → /create-profile → DynamoDB

      │
      ▼
[Recharge Form]
  Enter mobile + amount (€10–€100)
  Card details appear (Stripe.js)
  CAPTCHA verification (custom Lambda)

      │
      ▼
[Payment — 3-step]
  Step 1: POST /payments       → Lambda creates Stripe PaymentIntent
  Step 2: stripe.confirmCardPayment() → Stripe processes card
  Step 3: POST /payments/finalize → Lambda updates DynamoDB + triggers SNS SMS

      │
      ▼
[Invoice]
  POST /invoice → Lambda generates PDF → stores in S3 → returns S3 URL
  User clicks Download Invoice → PDF opens in new tab
```

---

## Environment Variables

Create `backend/templates/.env` with the following:

```env
AWS_REGION=us-east-1
FLASK_SECRET_KEY=your-secret-key-here
SALESFORCE_CLIENT_ID=your-sf-client-id
SALESFORCE_CLIENT_SECRET=your-sf-client-secret
SALESFORCE_AUTH_URL=https://login.salesforce.com/services/oauth2/token
STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
```

GitHub Actions Secrets required for CI/CD:

| Secret | Purpose |
|---|---|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `AWS_REGION` | `us-east-1` |
| `EB_APPLICATION_NAME` | `Mobile Recharge` |
| `EB_ENVIRONMENT_NAME` | `recharge-prod` |
| `SALESFORCE_CLIENT_ID` | Salesforce connected app |
| `SALESFORCE_CLIENT_SECRET` | Salesforce connected app |
| `SALESFORCE_AUTH_URL` | Salesforce OAuth token URL |

---

## Local Development Setup

**Prerequisites:** Python 3.11+, Docker (optional)

```bash
# Clone the repository
git clone https://github.com/mithileshkrsinghniitians/Mobile-Recharge.git
cd mobile-recharge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Create .env file (see Environment Variables section above)

# Run the Flask app
cd backend
python app.py
# App runs at http://localhost:5000
```

**Run with Docker:**

```bash
docker build -t mobile-recharge-app .
docker run -p 8080:8080 --env-file backend/templates/.env mobile-recharge-app
# App runs at http://localhost:8080
```

---

## API Reference

### Base URLs

| Service | Base URL |
|---|---|
| Flask App (local) | `http://localhost:5000` |
| Flask App (production) | Your Elastic Beanstalk URL |
| Payment API | `https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod` |
| Invoice API | `https://di8irmc06g.execute-api.us-east-1.amazonaws.com` |
| CAPTCHA API | `https://6wy6qva0yd.execute-api.us-east-1.amazonaws.com` |

---

### Flask Application Endpoints

#### `GET /check-mobile`

Checks if a mobile number has a registered profile in DynamoDB.

**Query Parameters:**

| Parameter | Type | Required | Example |
|---|---|---|---|
| `mobile` | string | Yes | `353871234567` |

**Responses:**

```json
// 200 — user found
{ "exists": true }

// 200 — user not found
{ "exists": false }

// 400 — non-numeric input
{ "error": "Invalid mobile number" }
```

---

#### `POST /create-profile`

Creates a new user profile in DynamoDB. Call only when `/check-mobile` returns `false`.

**Headers:** `Content-Type: application/json`

**Request Body:**

| Field | Type | Validation |
|---|---|---|
| `firstName` | string | Letters only, max 100 chars |
| `lastName` | string | Letters only, max 100 chars |
| `email` | string | Valid email format |
| `mobile` | string | With country code e.g. `+353871234567` |

**Example:**

```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@email.com",
  "mobile": "+353871234567"
}
```

**Responses:**

```json
// 200 — success
{ "status": "success" }

// 400 — missing fields
{ "error": "Missing required fields" }

// 500 — server error
{ "error": "Unable to create profile" }
```

---

#### `POST /login`

Authenticates admin via Salesforce OAuth 2.0 (username-password flow). Sets `sf_access_token` in session.

**Headers:** `Content-Type: application/json`

**Request Body:**

```json
{
  "username": "admin@yourdomain.com",
  "password": "SalesforcePassword+SecurityToken"
}
```

**Responses:**

```json
// 200 — success (session cookie set)
{ "status": "success" }

// 400 — missing credentials
{ "error": "Username and password are required" }

// 401 — bad credentials
{ "error": "authentication failure" }

// 503 — Salesforce unreachable
{ "error": "Unable to reach Salesforce. Please try again." }
```

---

#### `GET /admin/dashboard` *(Session required)*

Returns all registered users from DynamoDB. Redirects to `/admin` if not authenticated.

#### `POST /admin/update` *(Session required)*

Updates a user's first name, last name, or email.

**Request Body:**

```json
{
  "mobile": "353871234567",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@email.com"
}
```

#### `POST /admin/delete` *(Session required)*

Deletes a user record from DynamoDB.

**Request Body:**

```json
{ "mobile": "353871234567" }
```

#### `GET /logout`

Clears session and redirects to `/admin`.

---

### Payment API (AWS Lambda via API Gateway)

The payment flow is **3 steps**: create intent → Stripe client-side confirmation → finalise.

#### Step 1: `POST /payments` — Create Payment Intent

Creates a Stripe PaymentIntent and returns a `clientSecret` for client-side card confirmation.

**URL:** `https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod/payments`

**Headers:** `Content-Type: application/json`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `mobileNumber` | string | Yes | Mobile with country code e.g. `+353871234567` |
| `amount` | number | Yes | Amount in EUR, min €10, max €100 |

**Example:**

```json
{
  "mobileNumber": "+353871234567",
  "amount": 25.00
}
```

**Success Response (200):**

```json
{
  "paymentId": "pay_a1b2c3d4e5f6",
  "clientSecret": "pi_3abc_secret_xyz",
  "stripePaymentIntentId": "pi_3abc123"
}
```

**Error Responses:**

| Status | Response | Reason |
|---|---|---|
| 400 | `{"message": "Amount must be a number"}` | Non-numeric amount |
| 400 | `{"message": "Amount must be between 10 and 100"}` | Amount out of range |
| 400 | `{"message": "Invalid mobile number format. Use + followed by 6–15 digits."}` | Invalid mobile |
| 500 | `{"message": "Payment processing failed"}` | Internal Lambda error |

---

#### Step 2: Stripe Card Confirmation (client-side only)

After receiving `clientSecret`, the browser calls Stripe.js to confirm the card:

```js
const { paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
  payment_method: { card: cardElement }
});
```

This step is handled automatically by the frontend and **cannot be replicated in Postman** without a real Stripe PaymentIntent. For Postman testing, use the finalize step with a Stripe test PaymentIntent ID (see Postman Guide below).

---

#### Step 3: `POST /payments/finalize` — Finalise Payment

Confirms the payment on the backend, updates DynamoDB, and triggers SNS SMS.

**URL:** `https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod/payments/finalize`

**Headers:** `Content-Type: application/json`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `paymentId` | string | Yes | `paymentId` from Step 1 |
| `stripePaymentIntentId` | string | Yes | `paymentIntent.id` from Step 2 |
| `amount` | number | Yes | Same amount as Step 1 |
| `mobileNumber` | string | Yes | Same mobile as Step 1 |

**Example:**

```json
{
  "paymentId": "pay_a1b2c3d4e5f6",
  "stripePaymentIntentId": "pi_3abc123",
  "amount": 25.00,
  "mobileNumber": "+353871234567"
}
```

**Success Response (200):**

```json
{
  "paymentId": "pay_a1b2c3d4e5f6",
  "status": "SUCCEEDED"
}
```

**Error Responses:**

| Status | Response | Reason |
|---|---|---|
| 502 | `{"paymentId": "pay_xxx", "message": "Payment gateway rejected the request"}` | Stripe rejected |
| 500 | `{"message": "Payment processing failed"}` | Internal Lambda error |

> **Note:** On success, an SMS is automatically sent to `mobileNumber` via Amazon SNS.

---

### Invoice API (AWS Lambda via API Gateway)

#### `POST /invoice` — Generate PDF Invoice

Generates a PDF invoice for a completed payment and returns an S3 URL.

**URL:** `https://di8irmc06g.execute-api.us-east-1.amazonaws.com/invoice`

**Headers:** `Content-Type: application/json`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `paymentId` | string | Yes | Payment ID from finalize response |
| `amount` | number | Yes | Recharge amount in EUR |
| `mobileNumber` | string | Yes | Mobile number with country code |

**Example:**

```json
{
  "paymentId": "pay_a1b2c3d4e5f6",
  "amount": 25.00,
  "mobileNumber": "+353871234567"
}
```

**Success Response (200):**

```json
{
  "pdf_url": "https://s3.amazonaws.com/your-bucket/invoices/pay_a1b2c3d4e5f6.pdf"
}
```

**Error Response:**

```json
// 500
{ "error": "Invoice generation failed" }
```

> **Important:** Only call this endpoint after `status === "SUCCEEDED"` from the finalize step.

---

### CAPTCHA API (AWS Lambda via API Gateway)

#### `GET /generate-captcha`

**URL:** `https://6wy6qva0yd.execute-api.us-east-1.amazonaws.com/generate-captcha`

**Response:**

```json
{
  "captcha_token": "eyJhbGci...",
  "captcha_image_base64": "data:image/png;base64,iVBORw..."
}
```

#### `POST /validate-captcha`

**URL:** `https://6wy6qva0yd.execute-api.us-east-1.amazonaws.com/validate-captcha`

**Headers:** `Content-Type: application/x-www-form-urlencoded`

**Body:** `token=<captcha_token>&answer=ABCDE`

**Response:**

```json
// Correct
{ "success": true, "next_step": "continue" }

// Incorrect
{ "success": false, "message": "Incorrect captcha. Try again." }
```

---

## Postman Testing Guide

This guide walks through testing the complete payment flow end-to-end using Postman.

### Setup

1. Download and install [Postman](https://www.postman.com/downloads/)
2. Create a new **Collection** named `Mobile Recharge API`
3. Set a **Collection Variable**: `BASE_URL = https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod`

---

### Test 1: Check Mobile Number

| Setting | Value |
|---|---|
| Method | `GET` |
| URL | `http://localhost:5000/check-mobile?mobile=353871234567` |

**Expected Response:**
```json
{ "exists": false }
```

---

### Test 2: Create User Profile

| Setting | Value |
|---|---|
| Method | `POST` |
| URL | `http://localhost:5000/create-profile` |
| Header | `Content-Type: application/json` |

**Body (raw JSON):**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@email.com",
  "mobile": "+353871234567"
}
```

**Expected Response:**
```json
{ "status": "success" }
```

---

### Test 3: Create Payment Intent

| Setting | Value |
|---|---|
| Method | `POST` |
| URL | `{{BASE_URL}}/payments` |
| Header | `Content-Type: application/json` |

**Body (raw JSON):**
```json
{
  "mobileNumber": "+353871234567",
  "amount": 25.00
}
```

**Expected Response (200):**
```json
{
  "paymentId": "pay_07ed1e31a5",
  "clientSecret": "pi_3T8rxtPDaMhpoGKJ1jeOqmnb_secret_ROgDdBWevPX7Y21kejWgCWiBQ",
  "stripePaymentIntentId": "pi_3T8rxtPDaMhpoGKJ1jeOqmnb"
}
```

> **Important:** `paymentId` and `stripePaymentIntentId` are **unique on every call** — always copy them fresh from each response. Never reuse IDs from a previous request.

**Add a Postman Test Script** to auto-save variables (Tests tab on this request):
```js
const data = pm.response.json();
pm.collectionVariables.set("PAYMENT_ID", data.paymentId);
pm.collectionVariables.set("STRIPE_PI_ID", data.stripePaymentIntentId);
```
This means in all subsequent requests `{{PAYMENT_ID}}` and `{{STRIPE_PI_ID}}` are automatically filled — no manual copy-paste needed.

**Validation tests — expect 400:**
```json
{ "mobileNumber": "+353871234567", "amount": 5 }
```
```json
{ "mobileNumber": "12345", "amount": 25 }
```

---

### Test 3b: Confirm Card via Stripe API

This intermediate step confirms the PaymentIntent with a Stripe test card. It is required before calling `/payments/finalize` — skipping it will cause finalize to return an error because the PaymentIntent status will still be `requires_payment_method`.

| Setting | Value |
|---|---|
| Method | `POST` |
| URL | `https://api.stripe.com/v1/payment_intents/{{STRIPE_PI_ID}}/confirm` |
| Header | `Authorization: Bearer sk_test_YOUR_STRIPE_SECRET_KEY` |
| Header | `Content-Type: application/x-www-form-urlencoded` |
| Body type | `x-www-form-urlencoded` |

**Body (x-www-form-urlencoded — NOT raw JSON):**

| Key | Value |
|---|---|
| `payment_method` | `pm_card_visa` |
| `return_url` | `https://localhost` |

> **Where to find `sk_test_...`:** Stripe Dashboard → Developers → API Keys → Secret key.
> `pm_card_visa` is Stripe's built-in test Visa card — always succeeds, no real card needed.
> `return_url` is required by Stripe when `automatic_payment_methods` is enabled — any valid URL works.

**Expected Response (200):**
```json
{
  "id": "pi_3T8rxtPDaMhpoGKJ1jeOqmnb",
  "object": "payment_intent",
  "status": "succeeded",
  "amount": 1000,
  "amount_received": 1000,
  "currency": "eur"
}
```

Once `"status": "succeeded"` is returned, proceed immediately to Test 4.

**Common errors on this step:**

| Error | Cause | Fix |
|---|---|---|
| `401 Invalid API Key` | Used `pk_test_` instead of `sk_test_` | Use the **secret** key, not publishable |
| `return_url required` | Missing `return_url` in body | Add `return_url=https://localhost` |
| `PaymentIntent already confirmed` | Already called this once | Skip to Test 4 directly |

---

### Test 4: Finalise Payment

| Setting | Value |
|---|---|
| Method | `POST` |
| URL | `{{BASE_URL}}/payments/finalize` |
| Header | `Content-Type: application/json` |

**Body (raw JSON):**
```json
{
  "paymentId": "{{PAYMENT_ID}}",
  "stripePaymentIntentId": "{{STRIPE_PI_ID}}",
  "amount": 25.00,
  "mobileNumber": "+353871234567"
}
```

> `{{PAYMENT_ID}}` and `{{STRIPE_PI_ID}}` are auto-filled from the Test Script set in Test 3.

**Expected Response (200):**
```json
{
  "paymentId": "pay_07ed1e31a5",
  "status": "SUCCEEDED"
}
```

> On success, an **SMS is sent** to the mobile number via Amazon SNS automatically.

**Add a Test Script** to save payment ID for invoice:
```js
const data = pm.response.json();
pm.collectionVariables.set("FINAL_PAYMENT_ID", data.paymentId);
pm.test("Payment succeeded", () => {
  pm.expect(data.status).to.eql("SUCCEEDED");
});
```

---

### Test 5: Generate Invoice

| Setting | Value |
|---|---|
| Method | `POST` |
| URL | `https://di8irmc06g.execute-api.us-east-1.amazonaws.com/invoice` |
| Header | `Content-Type: application/json` |

**Body (raw JSON):**
```json
{
  "paymentId": "{{FINAL_PAYMENT_ID}}",
  "amount": 25.00,
  "mobileNumber": "+353871234567"
}
```

**Expected Response (200):**
```json
{
  "pdf_url": "https://s3.amazonaws.com/your-bucket/invoices/pay_07ed1e31a5.pdf"
}
```

> Copy the `pdf_url` into a browser to open the PDF invoice.

---

### Test 6: Admin Login (Salesforce)

| Setting | Value |
|---|---|
| Method | `POST` |
| URL | `http://localhost:5000/login` |
| Header | `Content-Type: application/json` |

**Body (raw JSON):**
```json
{
  "username": "admin@yourdomain.com",
  "password": "YourSalesforcePassword+SecurityToken"
}
```

**Expected Response (200):**
```json
{ "status": "success" }
```

> The session cookie `sf_access_token` is set automatically. Subsequent requests to `/admin/dashboard`, `/admin/update`, and `/admin/delete` will be authenticated.

---

### Postman Collection Variables Summary

| Variable | Set By | Value Example |
|---|---|---|
| `BASE_URL` | Manual | `https://3nsivye9u5.execute-api.us-east-1.amazonaws.com/prod` |
| `PAYMENT_ID` | Test 3 script | `pay_07ed1e31a5` |
| `STRIPE_PI_ID` | Test 3 script | `pi_3T8rxtPDaMhpoGKJ1jeOqmnb` |
| `FINAL_PAYMENT_ID` | Test 4 script | `pay_07ed1e31a5` |

> **Remember:** `PAYMENT_ID` and `STRIPE_PI_ID` are generated fresh every time you call `POST /payments`. Always run Tests 3 → 3b → 4 in sequence without reusing old IDs.

---

### Complete Payment Flow — Quick Reference

```
POST /payments          →  { paymentId, clientSecret, stripePaymentIntentId }
                                    ↓
                        [Stripe confirms card — browser only]
                                    ↓
POST /payments/finalize →  { paymentId, status: "SUCCEEDED" }
                                    ↓
                        [SNS SMS sent to mobile number]
                                    ↓
POST /invoice           →  { pdf_url: "https://s3.amazonaws.com/..." }
```

---

## Admin Panel

The admin dashboard is Salesforce-authenticated and provides full CRUD over the DynamoDB `Users` table.

| URL | Action |
|---|---|
| `/admin` | Login page (shows login form or redirects to dashboard) |
| `/admin/dashboard` | Lists all registered users |
| `/admin/update` | Edit user first name, last name, email |
| `/admin/delete` | Delete user by mobile number |
| `/logout` | Clears session, redirects to login |

**Login:** Salesforce credentials (username + password + security token appended to password).

---

## CI/CD Pipeline

Push to `main` branch triggers the full pipeline automatically:

```
git push origin main
        │
        ▼
[GitHub Actions]
  1. Checkout code
  2. Build Docker image (tagged: commit SHA + latest)
  3. Push to Docker Hub
  4. Generate docker-compose.yml for Elastic Beanstalk
  5. Zip and deploy to EB (waits for environment recovery)
        │
        ▼
[Elastic Beanstalk]
  Docker Compose pulls latest image from Docker Hub
  Runs Gunicorn on port 8080, mapped to port 80
```

**EB Configuration:**

| Setting | Value |
|---|---|
| Application | `Mobile Recharge` |
| Environment | `recharge-prod` |
| Platform | Docker on 64-bit Amazon Linux 2023 |
| Region | `us-east-1` |
| Port mapping | `80 → 8080` |

---

## Testing

**Run all tests:**

```bash
cd backend
pytest ../tests/ -v
```

**Run with coverage:**

```bash
pytest ../tests/ -v --cov=app --cov-report=xml
```

**22 tests covering:**

| Area | Tests |
|---|---|
| Page routes | `GET /`, `GET /admin` |
| Admin auth | Redirect when logged in / not logged in |
| Salesforce login | Success, wrong credentials, network error |
| Admin dashboard | Authenticated access, empty table, user list |
| Admin update (CRUD) | Auth guard, missing mobile, success |
| Admin delete (CRUD) | Auth guard, missing mobile, success |
| Check mobile | Exists, not found, invalid input |
| Create profile | Success, missing fields, missing mobile |
| Logout | Session cleared, subsequent requests redirected |

**Code quality:**

```bash
# Pylint
pylint backend/app.py --output-format=text > pylint-report.txt

# Bandit (security scan)
bandit -r backend/app.py -f json -o bandit-report.json

# SonarQube (requires SonarQube server)
sonar-scanner
```

---

## Monitoring (AWS CloudWatch)

### Dashboard

A CloudWatch Dashboard named **`MobileRecharge-Monitoring`** provides real-time visibility across all AWS services:

| Widget | Metric | Service |
|---|---|---|
| Payment API Success vs Error | `5XXError`, `4XXError`, `Count` | API Gateway |
| Invoice API Errors | `5XXError`, `4XXError` | API Gateway |
| Lambda Payment Errors | `Errors`, `Invocations`, `Duration` | Lambda |
| Lambda Invoice Errors | `Errors`, `Invocations` | Lambda |
| DynamoDB Latency | `SuccessfulRequestLatency` | DynamoDB (`Users` table) |


Navigate to: **CloudWatch → Log Insights → Select `/aws/lambda/payment-handler` → Run query**

---

## Security

| Concern | Implementation |
|---|---|
| Admin authentication | Salesforce OAuth 2.0 — no passwords stored locally |
| Session management | Flask server-side session with `FLASK_SECRET_KEY` |
| Payment security | Stripe.js — card details never touch the backend |
| CAPTCHA | Custom Lambda image CAPTCHA before card submission |
| Input validation | Regex on mobile (frontend + backend), amount range enforced |
| DynamoDB | `ConditionExpression` prevents duplicate profile creation |
| HTTPS | Enforced on all API Gateway endpoints and Elastic Beanstalk |
| Secrets | All credentials stored in GitHub Secrets + EB environment variables |
| Security scanning | Bandit static analysis in CI pipeline |