from flask import Flask, request, render_template, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = "supersecurekey"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "passwort123"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login', methods=['POST'])
def login():
    with open("kunden.json") as f:
        kunden = json.load(f)
    with open("termine.json") as f:
        termine = json.load(f)

    plate = request.form['plate'].strip().upper()
    if plate in kunden:
        freie_termine = [t for t in termine if t not in [k['termin'] for k in kunden.values()]]
        return render_template("termine.html", plate=plate, termine=freie_termine)
    return "Kennzeichen nicht gefunden", 404

@app.route('/book', methods=['POST'])
def book():
    plate = request.form['plate']
    termin = request.form['termin']
    with open("kunden.json") as f:
        kunden = json.load(f)
    if plate in kunden and termin:
        kunden[plate]['termin'] = termin
        with open("kunden.json", "w") as f:
            json.dump(kunden, f)
        return f"<h2>Termin am {termin} für {plate} erfolgreich gebucht.</h2>"
    return "Fehler bei der Buchung", 400

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin_panel"))
        return "Login fehlgeschlagen"
    return render_template("login.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get("logged_in"):
        return redirect(url_for("admin_login"))

    with open("kunden.json") as f:
        kunden = json.load(f)
    with open("termine.json") as f:
        termine = json.load(f)

    if request.method == "POST":
        if "new_plate" in request.form:
            plate = request.form["new_plate"].strip().upper()
            if plate and plate not in kunden:
                kunden[plate] = {"termin": None}
                with open("kunden.json", "w") as f:
                    json.dump(kunden, f)
        if "new_termin" in request.form:
            termin = request.form["new_termin"].strip()
            if termin and termin not in termine:
                termine.append(termin)
                with open("termine.json", "w") as f:
                    json.dump(termine, f)

    return render_template("admin.html", kunden=kunden, termine=termine)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
