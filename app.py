from flask import Flask, request
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="Simple Calculator API",
    description="A simple API that adds two numbers",
    doc="/swagger"          # Swagger UI will be available at /swagger
)

# Define the expected input
add_model = api.model("AddRequest", {
    "num1": fields.Float(required=True, description="First number", example=10),
    "num2": fields.Float(required=True, description="Second number", example=5)
})

# Define the response
result_model = api.model("AddResponse", {
    "result": fields.Float(description="The sum of the two numbers")
})


@api.route("/api/add")
class AddNumbers(Resource):
    @api.expect(add_model)
    @api.marshal_with(result_model)
    def post(self):
        """
        Add two numbers
        """
        data = request.get_json()
        num1 = data.get("num1")
        num2 = data.get("num2")

        if num1 is None or num2 is None:
            api.abort(400, "Both num1 and num2 are required")

        result = num1 + num2
        return {"result": result}


if __name__ == "__main__":
    app.run(debug=True)