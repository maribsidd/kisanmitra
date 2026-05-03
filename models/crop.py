from app import db
from datetime import datetime

class Crop(db.Model):
    __tablename__ = "crops"

    id           = db.Column(db.Integer, primary_key=True)
    farmer_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name         = db.Column(db.String(120), nullable=False)
    category     = db.Column(db.String(30), nullable=False)   # vegetable|fruit|grain|pulse|spice|other
    quantity     = db.Column(db.Float, nullable=False)         # kg
    price_per_kg = db.Column(db.Float, nullable=False)
    description  = db.Column(db.Text)
    location     = db.Column(db.String(120))
    is_organic   = db.Column(db.Boolean, default=False)
    status       = db.Column(db.String(20), default="available")  # available|sold|reserved|expired

    # Sensor data (filled after advisory visit)
    soil_ph      = db.Column(db.Float)
    nitrogen     = db.Column(db.Float)
    moisture     = db.Column(db.Float)

    harvest_date = db.Column(db.Date)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship("Order", backref="crop", lazy=True)

    @property
    def category_emoji(self):
        return {"vegetable":"🥦","fruit":"🍎","grain":"🌾","pulse":"🫘","spice":"🌶️"}.get(self.category, "🌿")

    @property
    def total_value(self):
        return round(self.quantity * self.price_per_kg, 2)
