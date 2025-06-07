from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.auth import *

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_pwd = request.form['confirm_pwd']
        if not username or not password or not confirm_pwd:
            flash("Palun täida kõik väljad!", "error")
            return render_template("register.html")

        if len(username) > 32 or len(password) > 32:
            flash("Kasutajanimi või parool liiga pikk - max 32 tähemärki lubatud", "error")
            return render_template("register.html", username=username)

        if password != confirm_pwd:
            flash("Paroolid ei ühti!", "error")
            return render_template("register.html", username=username)

        if len(password) < 8:
            flash("Parool peab olema vähemalt 8 tähemärki!", "error")
            return render_template("register.html",username=username)

        if get_user_by_username(username):
            flash("Kasutajanimi juba võetud!", "error")
            return render_template("register.html")

        try:
            user_id = insert_user(username, generate_password_hash(password))
            session['user_id'] = user_id
            session['username'] = username
            flash("Kasutaja edukalt loodud!", "success")
            return redirect(url_for("main.index"))
        except sqlite3.Error:
            flash("Viga konto loomisel. Palun proovige uuesti!", "error")
            return render_template("register.html")
    return render_template("register.html")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash("Palun täida kõik väljad!", "error")
            return render_template("login.html", username=username)

        user = get_user_by_username(username)
        if user is None or not check_password_hash(user['password'], password):
            flash("Vale kasutajanimi või parool.", "error")
            return render_template("login.html", username=username)

        session['user_id'] = user['id']
        session['username'] = user['username']
        flash("Edukalt sisse logitud!", "success")
        return redirect(url_for("main.index"))


    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))
