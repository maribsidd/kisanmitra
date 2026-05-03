from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.crop import Crop
from models.order import Order
from models.advisory import Advisory

main_bp = Blueprint("main", __name__)

PRICE_TRENDS = {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
    "wheat":  [22, 24, 21, 26, 28],
    "rice":   [35, 34, 37, 38, 36],
    "tomato": [18, 15, 22, 30, 25],
    "onion":  [20, 18, 16, 22, 24],
}

PLATFORM_STATS = {
    "farmers":  "1,240+",
    "listings": "3,870+",
    "orders":   "8,920+",
    "savings":  "28%",
}


@main_bp.route("/")
def home():
    featured = Crop.query.filter_by(status="available").order_by(Crop.created_at.desc()).limit(6).all()
    return render_template("home.html", crops=featured, stats=PLATFORM_STATS)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    my_listings = Crop.query.filter_by(farmer_id=current_user.id).order_by(Crop.created_at.desc()).all()
    my_orders   = Order.query.filter_by(buyer_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    my_sales    = Order.query.filter_by(farmer_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    my_reports  = Advisory.query.filter_by(farmer_id=current_user.id).order_by(Advisory.created_at.desc()).all()

    total_revenue = sum(o.total_amount for o in Order.query.filter_by(farmer_id=current_user.id, status="delivered").all())

    return render_template("dashboard.html",
        listings=my_listings,
        orders=my_orders,
        sales=my_sales,
        reports=my_reports,
        total_revenue=total_revenue,
        price_trends=PRICE_TRENDS,
    )


@main_bp.route("/pricing")
def pricing():
    return render_template("pricing.html")
