from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/docs"
API_URL = "https://bigger-yoshi.herokuapp.com/spec"

# Call factory function to create our blueprint
swaggerui_bp = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
)
