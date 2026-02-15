# Import Libraries:
import os
from datetime import datetime, timezone
import boto3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
from dotenv import load_dotenv

# Load environment variables from .env:
load_dotenv(os.path.join(os.path.dirname(__file__), 'templates', '.env'))

# DynamoDB Resources:
region = os.environ.get('AWS_REGION', 'us-east-1')
dynamodb = boto3.resource('dynamodb', region_name=region)
users_table = dynamodb.Table('Users')

# Initialize Flask App:
app = Flask(__name__, template_folder='templates', static_folder='../static', static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_dev_key')

# Configuration:
REQUEST_TIMEOUT = 10  # seconds

# Salesforce OAuth settings:
SF_CLIENT_ID = os.environ.get('SALESFORCE_CLIENT_ID')
SF_CLIENT_SECRET = os.environ.get('SALESFORCE_CLIENT_SECRET')
SF_AUTH_URL = os.environ.get('SALESFORCE_AUTH_URL', 'https://login.salesforce.com/services/oauth2/token')


# Index route:
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# Check Mobile Route Validates Mobile Number In DB:
@app.route("/check-mobile", methods=["GET"])
def check_mobile():
    mobile = request.args.get("mobile")

    try:
        mobile_number = int(mobile)

        response = users_table.get_item(
            Key={"mobile": mobile_number}
        )

        if "Item" in response:
            return jsonify({"exists": True})
        else:
            return jsonify({"exists": False})

    except ValueError:
        return jsonify({"error": "Invalid mobile number"}), 400


# Create Profile Route Validates Input And Create Record In DB:
@app.route("/create-profile", methods=["POST"])
def create_profile():
    try:
        data = request.get_json(force=True)

        first_name = data.get("firstName")
        last_name = data.get("lastName")
        email = data.get("email")
        mobile_raw = data.get("mobile")

        if not all([first_name, last_name, email, mobile_raw]):
            return jsonify({"error": "Missing required fields"}), 400

        mobile_number = int(str(mobile_raw).replace("+", ""))

        users_table.put_item(
            Item={
                "mobile": mobile_number,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            ConditionExpression="attribute_not_exists(mobile)"
        )

        return jsonify({"status": "success"})

    except Exception as e:
        print("Create profile error:", str(e))
        return jsonify({"error": "Unable to create profile"}), 500


# Authenticate via Salesforce OAuth 2.0 Username-Password flow:
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    payload = {
        "grant_type": "password",
        "client_id": SF_CLIENT_ID,
        "client_secret": SF_CLIENT_SECRET,
        "username": username,
        "password": password
    }

    try:
        response = requests.post(SF_AUTH_URL, data=payload, timeout=REQUEST_TIMEOUT)
        result = response.json()

        if response.status_code == 200 and "access_token" in result:
            session['sf_access_token'] = result['access_token']
            session['sf_instance_url'] = result.get('instance_url', '')
            return jsonify({"status": "success"})
        else:
            error_msg = result.get("error_description", "Authentication failed")
            return jsonify({"error": error_msg}), 401

    except requests.exceptions.RequestException:
        return jsonify({"error": "Unable to reach Salesforce. Please try again."}), 503


# Admin Route show login page, or redirect to dashboard if already authenticated:
@app.route("/admin", methods=["GET"])
def admin_login_page():
    if session.get('sf_access_token'):
        return redirect(url_for('admin_dashboard'))
    return render_template("login.html")


# Admin Dashboard protect admin dashboard & shows all Users from DynamoDB:
@app.route("/admin/dashboard", methods=["GET"])
def admin_dashboard():
    if not session.get('sf_access_token'):
        return redirect(url_for('admin_login_page'))

    try:
        response = users_table.scan()
        users = response.get('Items', [])

        for user in users:
            if 'mobile' in user:
                user['mobile'] = int(user['mobile'])
    except Exception as e:
        print("DynamoDB scan error:", str(e))
        users = []

    return render_template("admin.html", users=users)


# Admin Update Route update a user record in DynamoDB (first_name, last_name, email):
@app.route("/admin/update", methods=["POST"])
def admin_update():
    if not session.get('sf_access_token'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    mobile = data.get("mobile")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")

    if not mobile:
        return jsonify({"error": "Mobile number is required"}), 400

    try:
        mobile_number = int(mobile)
        users_table.update_item(
            Key={"mobile": mobile_number},
            UpdateExpression="SET first_name = :fn, last_name = :ln, email = :em",
            ExpressionAttributeValues={
                ":fn": first_name,
                ":ln": last_name,
                ":em": email
            }
        )
        return jsonify({"status": "success"})
    except Exception as e:
        print("Update error:", str(e))
        return jsonify({"error": "Failed to update user"}), 500


# Admin Delete Route delete a user record from DynamoDB:
@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    if not session.get('sf_access_token'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    mobile = data.get("mobile")

    if not mobile:
        return jsonify({"error": "Mobile number is required"}), 400

    try:
        mobile_number = int(mobile)
        users_table.delete_item(Key={"mobile": mobile_number})
        return jsonify({"status": "success"})
    except Exception as e:
        print("Delete error:", str(e))
        return jsonify({"error": "Failed to delete user"}), 500


# Logout Route clear session and redirect to admin login:
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('admin_login_page'))


# App Entry Point:
if __name__ == "__main__":
    app.run(debug=os.environ.get('FLASK_DEBUG', 'true').lower() == 'true')
