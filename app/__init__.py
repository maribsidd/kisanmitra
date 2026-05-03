import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "kisanmitra-dev-secret-2024")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kisanmitra.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please login to access this page."
    login_manager.login_message_category = "info"

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth    import auth_bp
    from routes.main    import main_bp
    from routes.market  import market_bp
    from routes.advisory import advisory_bp
    from routes.account import account_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(advisory_bp)
    app.register_blueprint(account_bp)

    # Create tables + seed data
    with app.app_context():
        db.create_all()
        _seed(db)

    return app


def _seed(db):
    """Seed sample crops so the marketplace isn't empty on first run."""
    from models.user import User
    from models.crop import Crop
    from models.advisory import Advisory
    from werkzeug.security import generate_password_hash

    if User.query.first():
        return  # already seeded

    # Demo farmer
    farmer = User(
        name="Ramesh Kumar",
        phone="9876543210",
        email="ramesh@kisanmitra.in",
        password_hash=generate_password_hash("demo1234"),
        role="farmer",
        state="Maharashtra",
        district="Nashik",
        village="Niphad",
        plan="free",
    )
    db.session.add(farmer)
    db.session.flush()

    crops = [
        Crop(farmer_id=farmer.id, name="Organic Tomatoes",  category="vegetable", quantity=300, price_per_kg=22, description="Fresh desi tomatoes, no pesticides.", is_organic=True,  location="Nashik, MH"),
        Crop(farmer_id=farmer.id, name="Wheat (Grade A)",   category="grain",     quantity=800, price_per_kg=27, description="Premium wheat, recently harvested.", is_organic=False, location="Nashik, MH"),
        Crop(farmer_id=farmer.id, name="Red Onion",         category="vegetable", quantity=500, price_per_kg=18, description="Large red onions, perfect quality.", is_organic=False, location="Nashik, MH"),
        Crop(farmer_id=farmer.id, name="Alphonso Mango",    category="fruit",     quantity=150, price_per_kg=95, description="Premium Hapus from Ratnagiri.",      is_organic=True,  location="Ratnagiri, MH"),
        Crop(farmer_id=farmer.id, name="Turmeric Powder",   category="spice",     quantity=80,  price_per_kg=85, description="Pure haldi, stone-ground.",          is_organic=True,  location="Sangli, MH"),
        Crop(farmer_id=farmer.id, name="Toor Dal",          category="pulse",     quantity=200, price_per_kg=110,description="Clean & sorted toor dal.",           is_organic=False, location="Latur, MH"),
    ]
    db.session.add_all(crops)
    db.session.commit()
