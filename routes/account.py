from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from app import db
from models.order import Order
from models.user import User

account_bp = Blueprint("account", __name__, url_prefix="/account")

PLAN_PRICES = {"basic": 500, "standard": 1000, "premium": 1500}
PLAN_DURATION_DAYS = 30


@account_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.name     = request.form.get("name", current_user.name).strip()
        current_user.email    = request.form.get("email", "").strip() or None
        current_user.language = request.form.get("language", current_user.language)
        current_user.state    = request.form.get("state", "")
        current_user.district = request.form.get("district", "")
        current_user.village  = request.form.get("village", "")
        farm_area = request.form.get("farm_area", "")
        current_user.farm_area = float(farm_area) if farm_area else None
        current_user.soil_type  = request.form.get("soil_type", "")
        current_user.irrigation = request.form.get("irrigation", "")

        new_pwd = request.form.get("new_password", "").strip()
        if new_pwd:
            current_user.password_hash = generate_password_hash(new_pwd)

        db.session.commit()
        flash("Profile updated! ✅", "success")
        return redirect(url_for("account.profile"))

    return render_template("account/profile.html")


@account_bp.route("/orders")
@login_required
def orders():
    bought = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).all()
    sold   = Order.query.filter_by(farmer_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("account/orders.html", bought=bought, sold=sold)


@account_bp.route("/subscribe/<plan>", methods=["POST"])
@login_required
def subscribe(plan):
    if plan not in PLAN_PRICES:
        flash("Invalid plan.", "danger")
        return redirect(url_for("main.pricing"))

    # In production, integrate Razorpay/Stripe here.
    # For demo, we activate immediately.
    current_user.plan          = plan
    current_user.plan_activated= datetime.utcnow()
    current_user.plan_expires  = datetime.utcnow() + timedelta(days=PLAN_DURATION_DAYS)
    db.session.commit()
    flash(f"🎉 Subscribed to {plan.capitalize()} plan! Premium features are now unlocked.", "success")
    return redirect(url_for("main.dashboard"))


@account_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    if order.farmer_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("account.orders"))
    order.status = request.form.get("status", order.status)
    order.updated_at = datetime.utcnow()
    db.session.commit()
    flash("Order status updated.", "success")
    return redirect(url_for("account.orders"))


@account_bp.route("/cancel-plan", methods=["POST"])
@login_required
def cancel_plan():
    current_user.plan          = "free"
    current_user.plan_activated= None
    current_user.plan_expires  = None
    db.session.commit()
    flash("Subscription cancelled. You're now on the Free plan.", "info")
    return redirect(url_for("account.profile"))
