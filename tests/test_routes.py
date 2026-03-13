import json
from unittest.mock import patch, MagicMock

# PAGE ROUTES:
# ===========
def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Mobile Recharge" in response.data


def test_admin_shows_login_page(client):
    response = client.get("/admin")
    assert response.status_code == 200
    assert b"loginForm" in response.data


def test_admin_redirects_when_authenticated(auth_client):
    response = auth_client.get("/admin")
    assert response.status_code == 302
    assert "/admin/dashboard" in response.headers["Location"]


# LOGIN:
# =====
def test_login_missing_fields(client):
    response = client.post("/login", json={"username": "", "password": ""})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_login_missing_username(client):
    response = client.post("/login", json={"username": "", "password": "pass123"})
    assert response.status_code == 400


def test_login_salesforce_success(client):
    mock_sf_response = MagicMock()
    mock_sf_response.status_code = 200
    mock_sf_response.json.return_value = {
        "access_token": "sf_token_abc",
        "instance_url": "https://login.salesforce.com"
    }

    with patch("app.requests.post", return_value=mock_sf_response):
        response = client.post("/login", json={
            "username": "user@test.com",
            "password": "pass123token"
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"


def test_login_salesforce_failure(client):
    mock_sf_response = MagicMock()
    mock_sf_response.status_code = 400
    mock_sf_response.json.return_value = {
        "error": "invalid_grant",
        "error_description": "authentication failure"
    }

    with patch("app.requests.post", return_value=mock_sf_response):
        response = client.post("/login", json={
            "username": "bad@test.com",
            "password": "wrong"
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert "error" in data


def test_login_salesforce_network_error(client):
    import requests as req_lib
    with patch("app.requests.post", side_effect=req_lib.exceptions.ConnectionError("Connection refused")):
        response = client.post("/login", json={
            "username": "user@test.com",
            "password": "pass123"
        })
        assert response.status_code == 503


# ADMIN DASHBOARD:
# ===============
def test_dashboard_unauthorized_redirects(client):
    response = client.get("/admin/dashboard")
    assert response.status_code == 302
    assert "/admin" in response.headers["Location"]


def test_dashboard_authorized_shows_table(auth_client):
    from tests.conftest import mock_table
    mock_table.scan.return_value = {
        "Items": [
            {"mobile": 353871234567, "first_name": "John", "last_name": "Doe",
             "email": "john@test.com", "created_at": "2025-01-01T00:00:00"}
        ]
    }

    response = auth_client.get("/admin/dashboard")
    assert response.status_code == 200
    assert b"John" in response.data
    assert b"Doe" in response.data


def test_dashboard_empty_table(auth_client):
    from tests.conftest import mock_table
    mock_table.scan.return_value = {"Items": []}

    response = auth_client.get("/admin/dashboard")
    assert response.status_code == 200
    assert b"No users found" in response.data


# ADMIN (CRUD - Update):
# =====================
def test_update_unauthorized(client):
    response = client.post("/admin/update", json={"mobile": "353871234567"})
    assert response.status_code == 401


def test_update_missing_mobile(auth_client):
    response = auth_client.post("/admin/update", json={
        "first_name": "Jane", "last_name": "Doe", "email": "jane@test.com"
    })
    assert response.status_code == 400


def test_update_success(auth_client):
    from tests.conftest import mock_table
    mock_table.update_item.return_value = {}

    response = auth_client.post("/admin/update", json={
        "mobile": "353871234567",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@test.com"
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    mock_table.update_item.assert_called_once()


# ADMIN (CRUD - Delete):
# =====================
def test_delete_unauthorized(client):
    response = client.post("/admin/delete", json={"mobile": "353871234567"})
    assert response.status_code == 401


def test_delete_missing_mobile(auth_client):
    response = auth_client.post("/admin/delete", json={})
    assert response.status_code == 400


def test_delete_success(auth_client):
    from tests.conftest import mock_table
    mock_table.delete_item.return_value = {}

    response = auth_client.post("/admin/delete", json={"mobile": "353871234567"})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    mock_table.delete_item.assert_called_once()


# CHECK MOBILE:
# ============
def test_check_mobile_exists(client):
    from tests.conftest import mock_table
    mock_table.get_item.return_value = {"Item": {"mobile": 353871234567}}

    response = client.get("/check-mobile?mobile=353871234567")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["exists"] is True


def test_check_mobile_not_found(client):
    from tests.conftest import mock_table
    mock_table.get_item.return_value = {}

    response = client.get("/check-mobile?mobile=353870000000")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["exists"] is False


def test_check_mobile_invalid(client):
    response = client.get("/check-mobile?mobile=abc")
    assert response.status_code == 400


# CREATE PROFILE (CRUD - Create):
# ==============================
def test_create_profile_success(client):
    from tests.conftest import mock_table
    mock_table.put_item.return_value = {}

    response = client.post("/create-profile", json={
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@test.com",
        "mobile": "+353871234567"
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    mock_table.put_item.assert_called_once()


def test_create_profile_missing_fields(client):
    response = client.post("/create-profile", json={
        "firstName": "John",
        "lastName": "",
        "email": "john@test.com",
        "mobile": "+353871234567"
    })
    assert response.status_code == 400


def test_create_profile_missing_mobile(client):
    response = client.post("/create-profile", json={
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@test.com"
    })
    assert response.status_code == 400


# LOGOUT:
# ======
def test_logout_clears_session(auth_client):
    response = auth_client.get("/logout")
    assert response.status_code == 302
    assert "/admin" in response.headers["Location"]

    response = auth_client.get("/admin/dashboard")
    assert response.status_code == 302


# PAY ROUTE:
# =========
def test_pay_valid_request(client):
    response = client.get("/pay?mobile=%2B353871234567&amount=20&redirect=https://example.com")
    assert response.status_code == 200
    assert b"Secure Payment" in response.data


def test_pay_mobile_without_plus_prefix(client):
    response = client.get("/pay?mobile=353871234567&amount=20&redirect=https://example.com")
    assert response.status_code == 200
    assert b"Secure Payment" in response.data


def test_pay_invalid_mobile(client):
    response = client.get("/pay?mobile=abc&amount=20&redirect=https://example.com")
    assert response.status_code == 200
    assert b"Invalid mobile number provided by merchant." in response.data


def test_pay_amount_out_of_range(client):
    response = client.get("/pay?mobile=%2B353871234567&amount=5&redirect=https://example.com")
    assert response.status_code == 200
    assert b"Amount must be between 10 and 100." in response.data


def test_pay_invalid_amount_format(client):
    response = client.get("/pay?mobile=%2B353871234567&amount=abc&redirect=https://example.com")
    assert response.status_code == 200
    assert b"Invalid amount provided by merchant." in response.data


def test_pay_invalid_redirect_url(client):
    response = client.get("/pay?mobile=%2B353871234567&amount=20&redirect=ftp://example.com")
    assert response.status_code == 200
    assert b"Invalid redirect URL provided by merchant." in response.data


# EXCEPTION PATHS:
# ===============
def test_create_profile_db_error(client):
    from tests.conftest import mock_table
    mock_table.put_item.side_effect = Exception("DynamoDB error")
    response = client.post("/create-profile", json={
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@test.com",
        "mobile": "+353871234567"
    })
    mock_table.put_item.side_effect = None
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data


def test_dashboard_db_error(auth_client):
    from tests.conftest import mock_table
    mock_table.scan.side_effect = Exception("DynamoDB scan error")
    response = auth_client.get("/admin/dashboard")
    mock_table.scan.side_effect = None
    assert response.status_code == 200


def test_update_db_error(auth_client):
    from tests.conftest import mock_table
    mock_table.update_item.side_effect = Exception("DynamoDB error")
    response = auth_client.post("/admin/update", json={
        "mobile": "353871234567",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@test.com"
    })
    mock_table.update_item.side_effect = None
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data


def test_delete_db_error(auth_client):
    from tests.conftest import mock_table
    mock_table.delete_item.side_effect = Exception("DynamoDB error")
    response = auth_client.post("/admin/delete", json={"mobile": "353871234567"})
    mock_table.delete_item.side_effect = None
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data

