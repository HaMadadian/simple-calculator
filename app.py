import os
from flask import Flask, render_template, request
from flask_restx import Api, Resource, fields
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

# ---------- Version ----------
APP_VERSION = "1.2"

# ---------- Username & Password from environment variables ----------
USERNAME = os.environ.get("BASIC_AUTH_USERNAME", "admin")
PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD", "password123")

users = {
    USERNAME: generate_password_hash(PASSWORD)
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None


# ---------- Force authentication on ALL routes ----------
@app.before_request
def require_authentication():
    # This forces the browser to ask for username/password on every request
    return auth.login_required(lambda: None)()


# ---------- Swagger / API setup ----------
api = Api(
    app,
    version=APP_VERSION,
    title="Simple Calculator API",
    description="A simple API that can add or multiply two numbers (Protected)",
    doc="/swagger",
    prefix="/api"
)

numbers_model = api.model("Numbers", {
    "num1": fields.Float(required=True, description="First number", example=10),
    "num2": fields.Float(required=True, description="Second number", example=5)
})

result_model = api.model("Result", {
    "result": fields.Float(description="The calculated result")
})


@api.route("/add")
class AddNumbers(Resource):
    @api.expect(numbers_model)
    @api.marshal_with(result_model)
    def post(self):
        """Add two numbers"""
        data = request.get_json()
        return {"result": data["num1"] + data["num2"]}


@api.route("/multiply")
class MultiplyNumbers(Resource):
    @api.expect(numbers_model)
    @api.marshal_with(result_model)
    def post(self):
        """Multiply two numbers"""
        data = request.get_json()
        return {"result": data["num1"] * data["num2"]}


# ---------- HTML Form ----------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    operation = "add"

    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operation = request.form.get("operation", "add")

            if operation == "add":
                result = num1 + num2
            elif operation == "multiply":
                result = num1 * num2
        except (ValueError, KeyError):
            result = "Please enter valid numbers"

    return render_template(
        "index.html",
        result=result,
        operation=operation,
        version=APP_VERSION
    )


if __name__ == "__main__":
    app.run(debug=True)