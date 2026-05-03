from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models.crop import Crop
from models.order import Order
from models.user import User

market_bp = Blueprint("market", __name__, url_prefix="/market")

COMMISSION = 0.05


@market_bp.route("/")
def index():
    q        = request.args.get("q", "")
    category = request.args.get("category", "all")
    organic  = request.args.get("organic", "")
    max_price= request.args.get("max_price", "")

    crops = Crop.query.filter_by(status="available")
    if q:
        crops = crops.filter(Crop.name.ilike(f"%{q}%"))
    if category and category != "all":
        crops = crops.filter_by(category=category)
    if organic == "1":
        crops = crops.filter_by(is_organic=True)
    if max_price:
        try: crops = crops.filter(Crop.price_per_kg <= float(max_price))
        except: pass

    crops = crops.order_by(Crop.created_at.desc()).all()
    return render_template("market/index.html", crops=crops, q=q, category=category, organic=organic, max_price=max_price)


@market_bp.route("/<int:crop_id>")
def detail(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    return render_template("market/detail.html", crop=crop)


@market_bp.route("/<int:crop_id>/buy", methods=["POST"])
@login_required
def buy(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    if crop.status != "available":
        flash("This crop is no longer available.", "danger")
        return redirect(url_for("market.detail", crop_id=crop_id))

    qty = float(request.form.get("quantity", 1))
    if qty > crop.quantity:
        flash(f"Only {crop.quantity} kg available.", "danger")
        return redirect(url_for("market.detail", crop_id=crop_id))

    total     = round(qty * crop.price_per_kg, 2)
    commission= round(total * COMMISSION, 2)

    order = Order(
        buyer_id=current_user.id,
        farmer_id=crop.farmer_id,
        crop_id=crop.id,
        quantity=qty,
        total_amount=total,
        commission=commission,
        delivery_city=request.form.get("city", ""),
        delivery_state=request.form.get("state", ""),
        delivery_pin=request.form.get("pincode", ""),
        payment_method=request.form.get("payment", "cod"),
    )
    crop.quantity -= qty
    if crop.quantity == 0:
        crop.status = "sold"

    db.session.add(order)
    db.session.commit()
    flash("Order placed successfully! 🎉", "success")
    return redirect(url_for("account.orders"))


@market_bp.route("/list", methods=["GET", "POST"])
@login_required
def list_crop():
    # Free plan: max 3 listings
    existing = Crop.query.filter_by(farmer_id=current_user.id, status="available").count()
    if existing >= current_user.listing_limit:
        flash(f"Free plan allows {current_user.listing_limit} active listings. Upgrade to list more. 🔒", "warning")
        return redirect(url_for("main.pricing"))

    if request.method == "POST":
        crop = Crop(
            farmer_id   = current_user.id,
            name        = request.form.get("name", "").strip(),
            category    = request.form.get("category", "other"),
            quantity    = float(request.form.get("quantity", 0)),
            price_per_kg= float(request.form.get("price_per_kg", 0)),
            description = request.form.get("description", ""),
            location    = request.form.get("location", ""),
            is_organic  = bool(request.form.get("is_organic")),
        )
        db.session.add(crop)
        db.session.commit()
        flash("Crop listed on the marketplace! 🌾", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("market/list.html")


@market_bp.route("/delete/<int:crop_id>", methods=["POST"])
@login_required
def delete_crop(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    if crop.farmer_id != current_user.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("main.dashboard"))
    db.session.delete(crop)
    db.session.commit()
    flash("Listing removed.", "info")
    return redirect(url_for("main.dashboard"))
