from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "orders"

    id             = db.Column(db.Integer, primary_key=True)
    buyer_id       = db.Column(db.Integer, db.ForeignKey("users.id"),  nullable=False)
    farmer_id      = db.Column(db.Integer, db.ForeignKey("users.id"),  nullable=False)
    crop_id        = db.Column(db.Integer, db.ForeignKey("crops.id"),  nullable=False)
    quantity       = db.Column(db.Float,   nullable=False)
    total_amount   = db.Column(db.Float,   nullable=False)
    commission     = db.Column(db.Float,   default=0)
    status         = db.Column(db.String(20), default="pending")  # pending|confirmed|dispatched|delivered|cancelled
    payment_method = db.Column(db.String(20), default="cod")
    delivery_city  = db.Column(db.String(80))
    delivery_state = db.Column(db.String(80))
    delivery_pin   = db.Column(db.String(10))
    notes          = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUS_COLORS = {
        "pending": "#F59E0B", "confirmed": "#3B82F6",
        "dispatched": "#8B5CF6", "delivered": "#10B981", "cancelled": "#EF4444"
    }

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, "#6b7280")
