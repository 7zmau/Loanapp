from loanapp import app, db
from loanapp.users.models import User
from flask_testing import TestCase
from werkzeug.security import generate_password_hash, check_password_hash
import unittest
import json
import base64


class BaseTestCase(TestCase):

    def create_app(self):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        return app

    def setUp(self):
        db.create_all()

        # Create an admin for tests.
        adminname = 'admin'
        password = 'supersecret'
        adminpass = generate_password_hash(password, method="sha256")
        user1 = User(adminname, adminpass)
        user1.admin = True
        db.session.add(user1)

        # Create a test user for tests.
        testusername = "TestUser"
        password = "testuserpass"
        testuserpass = generate_password_hash(password, method="sha256")
        testuser1 = User(testusername, testuserpass)
        db.session.add(testuser1)

        # Create testuser2
        passwd = generate_password_hash("testuserpass", method="sha256")
        testuser2 = User("TestUser2", passwd)
        testuser2.setAgent()
        db.session.add(testuser2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def get_token(self, name, password):
        response = self.client.get(
            "/users/login",
            headers={
                "Authorization": "Basic "
                + base64.b64encode(bytes(name + ":" + password, "UTF-8")).decode("UTF-8")
            },
        )
        return response.json["token"]

    def test_create_user(self):
        payload = json.dumps({"name": "Raj", "password": "passpass"})
        response = self.client.post(
            "/users", content_type="application/json", data=payload
        )
        self.assertEqual(dict(message="New user created."), response.json)

    def test_get_users_admin(self):
        response = self.client.get(
            "/users",
            headers={
                "x-access-token": self.get_token("admin", "supersecret"),
            },
        )
        self.assertIn("users", response.json)

    def test_get_users_user(self):
        response = self.client.get(
            "/users",
            headers={
                "x-access-token": self.get_token("TestUser", "testuserpass"),
            },
        )
        self.assertEqual(dict(message="Cannot perform the action."), response.json)

    def test_get_this_user(self):
        response = self.client.get(
            "/users/2",
            headers={
                "x-access-token": self.get_token("admin", "supersecret"),
            },
        )
        self.assertEqual(
            dict(user={"id": 2, "name": "TestUser", "applications": [], "loans": []}),
            response.json,
        )

    def test_promote_to_agent(self):
        response = self.client.patch(
            "users/2",
            headers={"x-access-token": self.get_token("admin", "supersecret")},
        )
        self.assertIn("is now an agent", response.json["message"])

    def test_delete_user(self):
        response = self.client.delete(
            "users/3",
            headers={"x-access-token": self.get_token("admin", "supersecret")},
        )
        self.assertEqual(dict(message="User Deleted."), response.json)

    def test_delete_user_user(self):
        response = self.client.delete(
            "users/3",
            headers={"x-access-token": self.get_token("TestUser", "testuserpass")},
        )
        self.assertEqual(dict(message="Cannot perform the action."), response.json)

    def test_get_interest_rates(self):
        payload = json.dumps({"tenure": 10})
        response = self.client.get(
            "/loans/get-interest-rates", content_type="application/json", data=payload
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dict(interest_rate=12), response.json)

    def test_get_loan_info(self):
        payload = json.dumps({"amount": 10000, "tenure": 12})
        response = self.client.get(
            "/loans/get-loan-info", content_type="application/json", data=payload
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("emi", response.json["loan_info"])

    def test_get_all_loans(self):
        response = self.client.get(
            "/users/2",
            headers={
                "x-access-token": self.get_token("admin", "supersecret"),
            },
        )
        self.assertIn(b"loans", response.data)

    def test_loan_request_user(self):
        payload = json.dumps({"amount": 10000, "tenure": 12})
        response = self.client.post(
            "/loans/apply",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser", "testuserpass")},
            data=payload,
        )
        self.assertEqual(
            "Agent will send a loan request soon.", response.json["message"]
        )

    def test_view_applications(self):
        payload = json.dumps({"amount": 10000, "tenure": 12})
        response = self.client.post(
            "/loans/apply",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser", "testuserpass")},
            data=payload,
        )
        self.assertEqual(
            "Agent will send a loan request soon.", response.json["message"]
        )
        response = self.client.get(
            "/loans/view-applications",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
        )
        self.assertIn(b"applications", response.data)

    def test_loan_request(self):
        # Apply for a loan
        payload = json.dumps({"amount": 10000, "tenure": 12})
        response = self.client.post(
            "/loans/apply",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser", "testuserpass")},
            data=payload,
        )
        self.assertEqual(
            "Agent will send a loan request soon.", response.json["message"]
        )

        # Request for loan by agent
        response = self.client.get(
            "/loans/view-applications",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
        )
        application_id = response.json["applications"][0]["application_id"]
        user_id = response.json["applications"][0]["user_id"]
        payload = json.dumps({"application_id": application_id, "user_id": user_id})
        response = self.client.post(
            "/loans/request",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
            data=payload,
        )
        self.assertEqual(dict(message="New loan requested."), response.json)

        # Test: agent cannot request same application again
        response = self.client.post(
            "/loans/request",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
            data=payload,
        )
        self.assertEqual(dict(message="Application already requested."), response.json)

        # Test: apply for loan with invalid application ID
        payload = json.dumps({"application_id": 100, "user_id": 100})
        response = self.client.post(
            "/loans/request",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
            data=payload,
        )
        self.assertEqual(dict(message="Invalid application."), response.json)

        # Test: edit a requested loan
        payload = json.dumps({"amount": 12000, "tenure": 24})
        response = self.client.put(
            "/loans/edit/1",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
            data=payload,
        )
        self.assertEqual(dict(message="Loan 1 updated."), response.json)

    def test_approve_loan(self):
        # Apply for a loan
        payload = json.dumps({"amount": 10000, "tenure": 12})
        response = self.client.post(
            "/loans/apply",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser", "testuserpass")},
            data=payload,
        )
        self.assertEqual(
            "Agent will send a loan request soon.", response.json["message"]
        )

        # Request for loan by agent
        response = self.client.get(
            "/loans/view-applications",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
        )
        application_id = response.json["applications"][0]["application_id"]
        user_id = response.json["applications"][0]["user_id"]
        payload = json.dumps({"application_id": application_id, "user_id": user_id})
        response = self.client.post(
            "/loans/request",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
            data=payload,
        )
        self.assertEqual(dict(message="New loan requested."), response.json)

        # Test: Approval of loan by admin
        payload = json.dumps({"loan_id": 1, "user_id": user_id})
        response = self.client.put(
            "/loans/approve",
            content_type="application/json",
            headers={"x-access-token": self.get_token("admin", "supersecret")},
            data=payload,
        )
        self.assertEqual(dict(message="Loan 1 approved."), response.json)

        # Test: Cannot edit loan which is already approved.
        payload = json.dumps({"amount": 12000, "tenure": 24})
        response = self.client.put(
            "/loans/edit/1",
            content_type="application/json",
            headers={"x-access-token": self.get_token("TestUser2", "testuserpass")},
            data=payload,
        )
        self.assertEqual(dict(message="Cannot edit loan."), response.json)


if __name__ == "__main__":
    unittest.main()
