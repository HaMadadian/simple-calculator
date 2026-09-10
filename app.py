import os
import time
from datetime import datetime
from flask import Flask, render_template, request
from flask_restx import Api, Resource, fields
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

# ---------- Version ----------
APP_VERSION = "1.3"

# ---------- Database setup ----------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///calculator.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ---------- Database Model ----------
class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    num1 = db.Column(db.Float, nullable=False)
    num2 = db.Column(db.Float, nullable=False)
    operation = db.Column(db.String(20), nullable=False)
    result = db.Column(db.Float, nullable=False)
    unix_timestamp = db.Column(db.Integer, nullable=False)
    local_time = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<{self.operation}: {self.num1} and {self.num2} = {self.result}>"


# ---------- Username & Password ----------
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


# ---------- Protect everything ----------
@app.before_request
def require_authentication():
    return auth.login_required(lambda: None)()


# ---------- Helper function to save calculation ----------
def save_calculation(num1, num2, operation, result):
    now = datetime.now()
    calculation = Calculation(
        num1=num1,
        num2=num2,
        operation=operation,
        result=result,
        unix_timestamp=int(time.time()),
        local_time=now.strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(calculation)
    db.session.commit()


# ---------- Swagger / API setup ----------
api = Api(
    app,
    version=APP_VERSION,
    title="Simple Calculator API",
    description="A simple API that can add or multiply two numbers (Protected + Database)",
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
        num1 = data["num1"]
        num2 = data["num2"]
        result = num1 + num2

        save_calculation(num1, num2, "add", result)
        return {"result": result}


@api.route("/multiply")
class MultiplyNumbers(Resource):
    @api.expect(numbers_model)
    @api.marshal_with(result_model)
    def post(self):
        """Multiply two numbers"""
        data = request.get_json()
        num1 = data["num1"]
        num2 = data["num2"]
        result = num1 * num2

        save_calculation(num1, num2, "multiply", result)
        return {"result": result}


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

            # Save to database
            save_calculation(num1, num2, operation, result)

        except (ValueError, KeyError):
            result = "Please enter valid numbers"

    return render_template(
        "index.html",
        result=result,
        operation=operation,
        version=APP_VERSION
    )


# ---------- Create the database tables ----------
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)