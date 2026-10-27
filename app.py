
import os
from flask import Flask, redirect, render_template_string, session, url_for
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "bitte-spaeter-aendern")

oauth = OAuth(app)

oauth.register(
    name="discord",
    client_id=os.environ.get("DISCORD_CLIENT_ID"),
    client_secret=os.environ.get("DISCORD_CLIENT_SECRET"),
    access_token_url="https://discord.com/api/oauth2/token",
    authorize_url="https://discord.com/oauth2/authorize",
    api_base_url="https://discord.com/api/",
    client_kwargs={"scope": "identify"},
)

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Schubert Logistik | Bot-Dashboard</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0; background: #101214; color: #f4f4f4;
    font-family: Arial, sans-serif;
}
header {
    padding: 24px; background: #191c20;
    border-bottom: 1px solid #353a40;
}
header h1 { margin: 0; font-size: 23px; }
header p { color: #aeb4bc; margin-bottom: 0; }
main { max-width: 1000px; margin: auto; padding: 24px; }
.card {
    background: #1b1f24; border: 1px solid #343a40;
    border-radius: 14px; padding: 22px; margin-bottom: 16px;
}
button, .button {
    display: inline-block; border: 0; border-radius: 8px;
    background: #e9edf1; color: #111; padding: 12px 18px;
    font-weight: bold; text-decoration: none; cursor: pointer;
}
.muted { color: #aeb4bc; }
.grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 14px; }
</style>
</head>
<body>
<header>
    <h1>SCHUBERT LOGISTIK</h1>
    <p>Bot-Dashboard · Zentrale Verwaltung</p>
</header>
<main>
    {% if user %}
    <section class="card">
        <h2>Willkommen, {{ user.username }}!</h2>
        <p class="muted">Du bist mit Discord angemeldet.</p>
        <a class="button" href="{{ url_for('logout') }}">Abmelden</a>
    </section>
    <h2>Verwaltung</h2>
    <div class="grid">
        <section class="card"><h3>👋 Willkommen</h3><p class="muted">Willkommensnachrichten und Kanäle konfigurieren.</p></section>
        <section class="card"><h3>👥 Personal</h3><p class="muted">Einstellungen, Rollen und Personalakten.</p></section>
        <section class="card"><h3>🪪 Fahrerkarten</h3><p class="muted">Fahrerkarten und Dienstnummern verwalten.</p></section>
        <section class="card"><h3>🚛 Fuhrpark</h3><p class="muted">Fahrzeuge und Kilometerstände.</p></section>
        <section class="card"><h3>📒 Fahrtenbuch</h3><p class="muted">Fahrten und Ranglisten.</p></section>
        <section class="card"><h3>⏱️ Schichtsystem</h3><p class="muted">Schichten und Arbeitszeiten.</p></section>
    </div>
    {% else %}
    <section class="card">
        <h2>Deine zentrale Bot-Verwaltung</h2>
        <p class="muted">Melde dich mit Discord an, um das Dashboard zu öffnen.</p>
        <a class="button" href="{{ url_for('login') }}">Mit Discord anmelden</a>
    </section>
    {% endif %}
    <p class="muted">Schubert Logistik GmbH & Co. KG</p>
</main>
</body>
</html>
"""


@app.route("/")
def index():
    user = session.get("user")
    return render_template_string(HTML, user=user)


@app.route("/login")
def login():
    if not os.environ.get("DISCORD_CLIENT_ID") or not os.environ.get("DISCORD_CLIENT_SECRET"):
        return "Discord-Login ist noch nicht eingerichtet. Bitte Umgebungsvariablen in Render setzen.", 503

    redirect_uri = url_for("callback", _external=True)
    return oauth.discord.authorize_redirect(redirect_uri)


@app.route("/callback")
def callback():
    token = oauth.discord.authorize_access_token()
    response = oauth.discord.get("users/@me", token=token)
    session["user"] = response.json()
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
