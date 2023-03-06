from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/docs"
API_URL = "http://localhost:5000/spec"

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
)
