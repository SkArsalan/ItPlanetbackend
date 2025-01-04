from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_cors import CORS
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Enable CORS with credentials
    CORS(app, supports_credentials=True, origins=["*"], methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"], allow_headers=["Content-Type"])

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."

    from app.models import User
    
    @app.route('/')
    def home():
        return '<h1>Hello world</h2>'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))

    # Register blueprints
    from app.auth import auth
    app.register_blueprint(auth)

    from app.inventory import inventory
    app.register_blueprint(inventory)
    
    from app.sales import sales
    app.register_blueprint(sales)
    
    from app.quotation import quotation
    app.register_blueprint(quotation)

    return app
