MOBILE RECHARGE APPLICATION
============================
MSc Cloud Computing - Scalable Cloud Programming
National College of Ireland
Student: Mithilesh Kumar Singh

================================================================
OVERVIEW
================================================================
A cloud-native mobile top-up application that allows users to
recharge mobile numbers using Stripe payment processing, with CAPTCHA
verification, automated PDF invoice generation, SMS confirmation via
Amazon SNS, and a Salesforce-authenticated admin dashboard.

================================================================
PREREQUISITES
================================================================
- Python 3.11 or higher
- pip (Python package manager)
- Docker (optional, for containerised run)
- AWS account with DynamoDB table named "Users"
- Salesforce connected app (for admin login)
- Stripe account (test or live keys)

================================================================
ENVIRONMENT VARIABLES
================================================================
Create the file: backend/templates/.env
Add the following variables:

  AWS_REGION=us-east-1
  FLASK_SECRET_KEY=your-secret-key-here
  SALESFORCE_CLIENT_ID=your-salesforce-client-id
  SALESFORCE_CLIENT_SECRET=your-salesforce-client-secret
  SALESFORCE_AUTH_URL=https://login.salesforce.com/services/oauth2/token
  STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key

================================================================
INSTALLATION AND RUN (LOCAL)
================================================================
Step 1 - Clone the repository:
  git clone https://github.com/mithileshkrsinghniitians/Mobile-Recharge.git
  cd mobile-recharge

Step 2 - Create a virtual environment:
  python3 -m venv venv
  source venv/bin/activate        (Mac/Linux)
  venv\Scripts\activate           (Windows)

Step 3 - Install dependencies:
  pip install -r backend/requirements.txt

Step 4 - Create .env file (see Environment Variables section above)

Step 5 - Run the application:
  cd backend
  python app.py

Application runs at: http://localhost:5000

================================================================
INSTALLATION AND RUN (DOCKER)
================================================================
Step 1 - Build the Docker image:
  docker build -t mobile-recharge-app .

Step 2 - Run the container:
  docker run -p 8080:8080 \
    --env-file backend/templates/.env \
    mobile-recharge-app

Application runs at: http://localhost:8080

================================================================
RUNNING TESTS
================================================================
  cd backend
  pytest ../tests/ -v

To run with coverage report:
  pytest ../tests/ -v --cov=app --cov-report=term-missing

Expected: 22 tests, all passing.

================================================================
PROJECT STRUCTURE
================================================================
  backend/
    app.py              - Flask application (all routes)
    requirements.txt    - Python dependencies
    templates/
      index.html        - Main recharge UI
      pay.html          - Hosted payment page
      login.html        - Admin login
      admin.html        - Admin dashboard
  static/
    css/style.css       - Shared styles
    js/app.js           - Recharge form logic
    js/profile.js       - Profile modal logic
    js/login.js         - Admin login logic
  tests/
    conftest.py         - Test fixtures
    test_routes.py      - 22 unit tests
  Dockerfile            - Docker build config
  README.md             - Full project documentation
  payment-api-swagger.yaml - API documentation

================================================================
API DOCUMENTATION
================================================================
Full API reference is available in README.md and on SwaggerHub:
https://app.swaggerhub.com/apis/cloudsfdc/Payment-API/2.0.0#/default/createPaymentIntent

================================================================
DEPLOYMENT
================================================================
The application is deployed automatically via GitHub Actions.
Push to the 'main' branch triggers:
  1. Docker image build
  2. Push to Docker Hub
  3. Deploy to AWS Elastic Beanstalk (recharge-prod environment)

For full CI/CD details see .github/workflows/deploy.yml
