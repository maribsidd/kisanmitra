from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    phone         = db.Column(db.String(15), unique=True, nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default="farmer")   # farmer | buyer | agent | admin
    language      = db.Column(db.String(5), default="hi")

    # Location
    state    = db.Column(db.String(80))
    district = db.Column(db.String(80))
    village  = db.Column(db.String(80))

    # Farm details
    farm_area      = db.Column(db.Float)    # acres
    soil_type      = db.Column(db.String(50))
    irrigation     = db.Column(db.String(50))

    # Subscription  ← chosen AFTER registration, default free
    plan           = db.Column(db.String(20), default="free")   # free | basic | standard | premium
    plan_activated = db.Column(db.DateTime, nullable=True)
    plan_expires   = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    crops      = db.relationship("Crop",     backref="farmer",  lazy=True, foreign_keys="Crop.farmer_id")
    buy_orders = db.relationship("Order",    backref="buyer",   lazy=True, foreign_keys="Order.buyer_id")
    sell_orders= db.relationship("Order",    backref="seller",  lazy=True, foreign_keys="Order.farmer_id")
    advisories = db.relationship("Advisory", backref="farmer",  lazy=True, foreign_keys="Advisory.farmer_id")

    # ── helpers ──────────────────────────────────────────────────
    @property
    def is_premium(self):
        return self.plan in ("basic", "standard", "premium")

    @property
    def plan_label(self):
        return {"free": "Free", "basic": "Basic", "standard": "Standard", "premium": "Premium"}.get(self.plan, "Free")

    @property
    def advisory_limit(self):
        return {"free": 0, "basic": 1, "standard": 3, "premium": 999}.get(self.plan, 0)

    @property
    def listing_limit(self):
        return {"free": 3, "basic": 10, "standard": 50, "premium": 999}.get(self.plan, 3)

    def __repr__(self):
        return f"<User {self.name} [{self.plan}]>"
