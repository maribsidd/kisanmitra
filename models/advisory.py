from app import db
from datetime import datetime

class Advisory(db.Model):
    __tablename__ = "advisories"

    id             = db.Column(db.Integer, primary_key=True)
    farmer_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    agent_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status         = db.Column(db.String(20), default="requested")  # requested|scheduled|completed
    scheduled_date = db.Column(db.Date)

    # Sensor readings
    soil_ph      = db.Column(db.Float)
    nitrogen     = db.Column(db.Float)
    phosphorus   = db.Column(db.Float)
    potassium    = db.Column(db.Float)
    moisture     = db.Column(db.Float)
    temperature  = db.Column(db.Float)
    crop_health  = db.Column(db.String(30))

    # Recommendations (auto-generated)
    rec_water      = db.Column(db.Text)
    rec_fertilizer = db.Column(db.Text)
    rec_next_crop  = db.Column(db.Text)
    rec_notes      = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    STATUS_COLORS = {"requested": "#F59E0B", "scheduled": "#3B82F6", "completed": "#10B981"}

    @property
    def status_color(self):
        return self.STATUS_COLORS.get(self.status, "#6b7280")
