from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models.advisory import Advisory
from datetime import date, datetime

advisory_bp = Blueprint("advisory", __name__, url_prefix="/advisory")


def _generate_recommendations(a):
    """Auto-generate simple text recommendations from sensor data."""
    a.rec_water = (
        "Irrigate immediately – soil moisture critically low." if (a.moisture or 50) < 30
        else "Irrigate within 2 days." if (a.moisture or 50) < 50
        else "Moisture adequate – skip irrigation this week."
    )
    a.rec_fertilizer = (
        "Apply Urea (46-0-0) at 50 kg/acre – nitrogen deficient." if (a.nitrogen or 30) < 20
        else "Nitrogen sufficient. Avoid over-fertilization."
    )
    ph = a.soil_ph or 7.0
    if ph < 6:
        a.rec_next_crop = "Recommended: Rice, Potato (acidic soil suits them)."
    elif ph > 7.5:
        a.rec_next_crop = "Recommended: Wheat, Barley (alkaline soil suits them)."
    else:
        a.rec_next_crop = "Recommended: Maize, Soybean, Cotton (neutral pH is ideal)."
    a.rec_notes = (
        f"Soil pH {ph} – {'apply lime to raise pH' if ph < 6.5 else 'apply sulfur to lower pH' if ph > 7.5 else 'pH is optimal'}."
    )


@advisory_bp.route("/")
@login_required
def index():
    if not current_user.is_premium:
        flash("Farm Advisory is a premium feature. Upgrade to get IoT-based soil reports. 🔒", "warning")
        return redirect(url_for("main.pricing"))

    reports = Advisory.query.filter_by(farmer_id=current_user.id).order_by(Advisory.created_at.desc()).all()
    used    = len(reports)
    limit   = current_user.advisory_limit
    return render_template("advisory/index.html", reports=reports, used=used, limit=limit, now=datetime.utcnow())


@advisory_bp.route("/request", methods=["POST"])
@login_required
def request_check():
    if not current_user.is_premium:
        flash("Upgrade to request a Farm Check. 🔒", "warning")
        return redirect(url_for("main.pricing"))

    used  = Advisory.query.filter_by(farmer_id=current_user.id).count()
    limit = current_user.advisory_limit
    if used >= limit:
        flash(f"You've used all {limit} advisory checks this month. Upgrade for more.", "warning")
        return redirect(url_for("advisory.index"))

    sched = request.form.get("scheduled_date") or None
    if sched:
        from datetime import datetime
        sched = datetime.strptime(sched, "%Y-%m-%d").date()

    adv = Advisory(farmer_id=current_user.id, scheduled_date=sched)
    db.session.add(adv)
    db.session.commit()
    flash("Farm Check requested! An agent will contact you shortly. 🌿", "success")
    return redirect(url_for("advisory.index"))


@advisory_bp.route("/demo")
@login_required
def demo_report():
    """Generate a simulated advisory so free users can preview."""
    return render_template("advisory/demo.html")
