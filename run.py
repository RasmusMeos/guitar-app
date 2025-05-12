import os
from flask import Flask
from app.routes.main import main_bp
from app.routes.auth import auth_bp
import logging
from init_db import initialize_database


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)

initialize_database()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)
