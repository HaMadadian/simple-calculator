from flask import Flask, render_template, request
from flask_restx import Api, Resource, fields

app = Flask(__name__)

# ---------- Swagger / API setup ----------
api = Api(
    app,
    version="1.0",
    title="Simple Calculator API",
    description="A simple API that adds two numbers",
    doc="/swagger",          # Swagger UI → http://127.0.0.1:5000/swagger
    prefix="/api"            # All API routes will start with /api
)

add_model = api.model("AddRequest", {
    "num1": fields.Float(required=True, description="First number", example=10),
    "num2": fields.Float(required=True, description="Second number", example=5)
})

result_model = api.model("AddResponse", {
    "result": fields.Float(description="The sum of the two numbers")
})


@api.route("/add")
class AddNumbers(Resource):
    @api.expect(add_model)
    @api.marshal_with(result_model)
    def post(self):
        """
        Add two numbers via API
        """
        data = request.get_json()
        num1 = data.get("num1")
        num2 = data.get("num2")

        if num1 is None or num2 is None:
            api.abort(400, "Both num1 and num2 are required")

        return {"result": num1 + num2}


# ---------- Original HTML form ----------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            result = num1 + num2
        except (ValueError, KeyError):
            result = "Please enter valid numbers"

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)