from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            flash(f"Welcome back, {user.name.split()[0]}! 🌾", "success")
            nxt = request.args.get("next")
            return redirect(nxt or url_for("main.dashboard"))
        flash("Invalid phone number or password.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip() or None
        pwd   = request.form.get("password", "")
        role  = request.form.get("role", "farmer")
        lang  = request.form.get("language", "hi")
        state = request.form.get("state", "")
        dist  = request.form.get("district", "")
        vill  = request.form.get("village", "")

        if User.query.filter_by(phone=phone).first():
            flash("Phone number already registered.", "danger")
            return render_template("auth/register.html")

        user = User(
            name=name, phone=phone, email=email,
            password_hash=generate_password_hash(pwd),
            role=role, language=lang,
            state=state, district=dist, village=vill,
            plan="free"        # ← always starts FREE, no plan forced
        )
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        flash("Account created! You're on the Free plan. Upgrade anytime. 🌱", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("main.home"))
