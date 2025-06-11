from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, URL

class AddCafeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    map_url = StringField("Map URL")
    has_sockets = BooleanField("Power Sockets")
    has_toilet = BooleanField("Toilet")
    has_wifi = BooleanField("Wi-Fi")
    can_take_calls = BooleanField("Can be Contacted")
    seats = StringField("Seats")
    coffee_price = StringField("Coffee Price")
    opening_hours = StringField("Opening Hours")
    closing_hours = StringField("Closeing Hours")
    contact_phone = StringField("Contact Phone")
    contact_email = StringField("Contact email")
    description = TextAreaField("Description")
    submit = SubmitField("Add Café")

class Cafe_Search(FlaskForm):
    location = StringField(validators=[DataRequired()])
    wifi = BooleanField("Wifi")
    sockets = BooleanField("Sockets")
    toilet = BooleanField("Toilet")
    calling = BooleanField("Calling")
    submit = SubmitField("Search Cafe")


class SignUp(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class Login(FlaskForm):
    email = StringField("Email address")
    password = PasswordField("Password")
    submit = SubmitField("Log in")

class Contact(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    message = TextAreaField("Message",validators=[DataRequired()])
    submit = SubmitField("Send Message")