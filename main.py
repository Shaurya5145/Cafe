from flask import Flask,render_template,redirect,url_for,session,flash,abort,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user,login_required
from forms import AddCafeForm, Cafe_Search, SignUp, Login, Contact
from functools import wraps
from datetime import date
from urllib.parse import urlparse, urljoin
from smtplib import SMTP
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI","sqlite:///london_cafes.db")
app.secret_key = os.environ.get("FLASK_KEY")

MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASS = os.environ.get("MY_PASS")


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

bookmarks = db.Table(
    "bookmarks",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("cafe_id", db.Integer, db.ForeignKey("cafes.id")),
)


class Cafes(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    img_url: Mapped[str] = mapped_column(String, unique=True)
    map_url: Mapped[str] = mapped_column(String, unique=True)
    location: Mapped[str] = mapped_column(String)
    has_sockets: Mapped[bool] = mapped_column(Boolean)
    has_toilet: Mapped[bool] = mapped_column(Boolean)
    has_wifi: Mapped[bool] = mapped_column(Boolean)
    can_take_calls: Mapped[bool] = mapped_column(Boolean)
    seats: Mapped[str] = mapped_column(String)
    coffee_price: Mapped[str] = mapped_column(String)
    opening_hours: Mapped[str] = mapped_column(String)
    closing_hours: Mapped[str] = mapped_column(String)
    contact_phone: Mapped[str] = mapped_column(String)
    contact_email: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    bookmarks = db.relationship("Cafes", secondary=bookmarks, backref="bookmarked_by")


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(user_id)


@app.context_processor
def inject_date():
    return {"current_year": date.today().year}


@app.route("/")
def home():
    form = Cafe_Search()
    all_cafes = db.session.execute(db.select(Cafes)).scalars().all()[1:6]
    return render_template("index.html", all_cafes=all_cafes, form=form)


@app.route("/search", methods=["GET", "POST"])
def search_cafe():
    form = Cafe_Search()
    if form.validate_on_submit():
        location = form.location.data.title()
        wifi = 1 if form.wifi.data == True else 0
        sockets = form.sockets.data if form.sockets.data == True else 0
        toilet = form.toilet.data if form.toilet.data == True else 0
        calling = form.calling.data if form.calling.data == True else 0

        stmt = db.select(Cafes).where(Cafes.location.ilike(f"%{location}%"))
        if wifi:
            stmt = stmt.where(Cafes.has_wifi == wifi)
        if sockets:
            stmt = stmt.where(Cafes.has_sockets == sockets)
        if toilet:
            stmt = stmt.where(Cafes.has_toilet == toilet)
        if calling:
            stmt = stmt.where(Cafes.can_take_calls == calling)

        results = db.session.execute(stmt).scalars().all()
        session["results"] = [result.id for result in results]
        return redirect(url_for("results"))
    return redirect("/#search")


@app.route("/results")
def results():
    cafe_ids = session.get("results", [])
    results = (
        db.session.execute(db.select(Cafes).where(Cafes.id.in_(cafe_ids)))
        .scalars()
        .all()
    )
    return render_template("search_result.html", results=results)


@app.route("/cafe<int:id>")
def cafe_details(id):
    cafe = db.session.execute(db.select(Cafes).where(Cafes.id == id)).scalar()
    return render_template("cafe_details.html", cafe=cafe)


def admin_required(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return func(*args, **kwargs)

    return wrapper_function


@app.route("/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafes(
            name=form.name.data,
            img_url=form.img_url.data,
            map_url=form.map_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
            opening_hours=form.opening_hours.data,
            closing_hours=form.closing_hours.data,
            contact_phone=form.contact_phone.data,
            contact_email=form.contact_email.data,
            description=form.description.data,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_cafe.html", form=form)


@app.route("/edit<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_cafe(id):
    cafe = Cafes.query.get_or_404(id)
    form = AddCafeForm(
        name=cafe.name,
        img_url=cafe.img_url,
        map_url=cafe.map_url,
        location=cafe.location,
        has_sockets=cafe.has_sockets,
        has_toilet=cafe.has_toilet,
        has_wifi=cafe.has_wifi,
        can_take_calls=cafe.can_take_calls,
        seats=cafe.seats,
        coffee_price=cafe.coffee_price,
        opening_hours=cafe.opening_hours,
        closing_hours=cafe.closing_hours,
        contact_phone=cafe.contact_phone,
        contact_email=cafe.contact_email,
        description=cafe.description,
    )
    if form.validate_on_submit():
        cafe.name = form.name.data
        cafe.img_url = form.img_url.data
        cafe.map_url = form.map_url.data
        cafe.location = form.location.data
        cafe.has_sockets = form.has_sockets.data
        cafe.has_toilet = form.has_toilet.data
        cafe.has_wifi = form.has_wifi.data
        cafe.can_take_calls = form.can_take_calls.data
        cafe.seats = form.seats.data
        cafe.coffee_price = form.coffee_price.data
        cafe.opening_hours = form.opening_hours.data
        cafe.closing_hours = form.closing_hours.data
        cafe.contact_phone = form.contact_phone.data
        cafe.contact_email = form.contact_email.data
        cafe.description = form.description.data
        db.session.commit()
        return redirect(url_for("cafe_details", id=cafe.id))
    return render_template("add_cafe.html", form=form, is_edit=True)


@app.route("/delete<int:id>")
@login_required
@admin_required
def delete(id):
    cafe = Cafes.query.get_or_404(id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/bookmarks<int:id>", methods=["GET", "POST"])
@login_required
def bookmark_cafe(id):
    cafe = Cafes.query.get_or_404(id)
    if cafe in current_user.bookmarks:
        current_user.bookmarks.remove(cafe)
    else:
        current_user.bookmarks.append(cafe)
    db.session.commit()
    return redirect(url_for("cafe_details", id=cafe.id))


@app.route("/my-bookmarks")
def show_boomarks():
    cafes = current_user.bookmarks
    return render_template("bookmarks.html", cafes=cafes)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = Contact()
    if form.validate_on_submit():
        name = form.name.data
        print(name)
        email = form.email.data
        message = form.message.data
        with SMTP(host="smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASS)
            connection.sendmail(
                msg=f"Subject:Query on your Cafe Website\n\nName: {name}\nMessage:{message}",
                from_addr=email,
                to_addrs=MY_EMAIL)
        return redirect(url_for("home"))
    return render_template("contact_us.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = SignUp()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).where(User.email == form.email.data)
        ).scalar()
        if not user:
            name = form.name.data
            email = form.email.data
            password = generate_password_hash(
                form.password.data, method="pbkdf2:sha256", salt_length=8
            )
            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        else:
            flash(message="This email already exists, login instead")
            return redirect(url_for("login"))
    return render_template("register.html", form=form)


def is_safe_host(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return ref_url.scheme == test_url.scheme and ref_url.netloc == test_url.netloc


@app.route("/login", methods=["GET", "POST"])
def login():
    form = Login()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).where(User.email == form.email.data)
        ).scalar()
        if not user:
            flash(message="No user exists with this email.")
            return redirect(url_for("login"))
        elif not check_password_hash(pwhash=user.password, password=form.password.data):
            flash(message="Wrong Password")
            return redirect(url_for("login"))
        else:
            login_user(user, remember=True)
            next_page = request.args.get("next")
            if not next_page or not is_safe_host(next_page):
                return redirect(url_for("home"))
            else:
                return redirect(next_page)
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
