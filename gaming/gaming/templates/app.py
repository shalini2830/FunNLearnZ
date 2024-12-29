import urllib.parse
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)

# URL-encode the password (and username if needed)
password = "Sujatha@2004"
encoded_password = urllib.parse.quote_plus(password)

# Configure the MongoDB connection
app.config["MONGO_URI"] = f"mongodb+srv://sujathagd394:{encoded_password}@cluster0.jlpyj.mongodb.net/game_app?retryWrites=true&w=majority&appName=Cluster0"

app.secret_key = "your_secret_key"  # For flashing messages
mongo = PyMongo(app)


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = mongo.db.users.find_one({"email": email})

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_user = mongo.db.users.find_one({"email": email})

        if existing_user:
            flash("Email already registered", "danger")
            return redirect(url_for("signup"))

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        mongo.db.users.insert_one({"email": email, "password": hashed_password})

        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    games = [
        {"name": "Game 1", "icon": url_for("static", filename="icons/game1.png")},
        {"name": "Game 2", "icon": url_for("static", filename="icons/game2.png")},
        {"name": "Game 3", "icon": url_for("static", filename="icons/game3.png")},
        {"name": "Game 4", "icon": url_for("static", filename="icons/game4.png")},
    ]
    return render_template("dashboard.html", games=games)


@app.route('/game<int:game_id>')
def game_page(game_id):
    try:
        return render_template(f'game{game_id}.html')
    except:
        return "Game content not found.", 404


if __name__ == "__main__":
    app.run(debug=True)
