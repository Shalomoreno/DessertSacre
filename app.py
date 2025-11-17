from flask import Flask, request, render_template, redirect, session
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import requests

# ------------------------------------
# CONFIG GENERAL
# ------------------------------------
app = Flask(__name__)
app.secret_key = "clave_super_secreta"

DB_CONFIG = {
    'host': 'localhost',
    'database': 'mayron_formulario',
    'user': 'postgres',
    'password': '123456',
    'port': 5432
}

def conectar_bd():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print("Error BD:", e)
        return None

# ------------------------------------
# MAILTRAP API (FUNCIONANDO)
# ------------------------------------
MAILTRAP_TOKEN = "4fc039135cd79ca0b5441f6f09ecc2cc"

def enviar_codigo(correo_destino, codigo):
    url = "https://send.api.mailtrap.io/api/send"

    headers = {
        "Authorization": f"Bearer {MAILTRAP_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "from": {"email": "hello@demomailtrap.co", "name": "Verificación"},
        "to": [{"email": correo_destino}],
        "subject": "Código de verificación",
        "text": f"Tu código de verificación es: {codigo}",
        "category": "Registro"
    }

    try:
        r = requests.post(url, json=data, headers=headers)
        print("Mailtrap:", r.status_code, r.text)

        # Mailtrap responde 202 = OK ✔
        return r.status_code in [200, 202]

    except Exception as e:
        print("Error enviando email:", e)
        return False


# ------------------------------------
# INICIO
# ------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------
# REGISTRO
# ------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]

        conexion = conectar_bd()
        cursor = conexion.cursor()

        # GENERAR CÓDIGO
        codigo = str(random.randint(100000, 999999))

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password, codigo_verificacion, verificado)
            VALUES (%s, %s, %s, %s, FALSE)
        """, (nombre, correo, password, codigo))

        conexion.commit()
        cursor.close()
        conexion.close()

        # ENVIAR CORREO ✔
        enviar_codigo(correo, codigo)

        session["correo_temp"] = correo

        return redirect("/verify")

    return render_template("register.html")


# ------------------------------------
# VERIFICAR
# ------------------------------------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        codigo_ingresado = request.form["codigo"]
        correo = session.get("correo_temp")

        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT codigo_verificacion FROM usuarios WHERE correo=%s", (correo,))
        codigo_real = cursor.fetchone()[0]

        if codigo_ingresado == codigo_real:
            cursor.execute("UPDATE usuarios SET verificado=TRUE WHERE correo=%s", (correo,))
            conexion.commit()
            return redirect("/login")
        else:
            return "Código incorrecto"

    return render_template("verify.html")


# ------------------------------------
# LOGIN
# ------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        conexion = conectar_bd()
        cursor = conexion.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM usuarios WHERE correo=%s AND password=%s", (correo, password))
        usuario = cursor.fetchone()

        if usuario:
            if usuario["verificado"]:
                session["usuario"] = usuario["nombre"]
                return redirect("/dashboard")
            else:
                return "Debes verificar tu correo antes de iniciar sesión"
        else:
            return "Credenciales incorrectas"

    return render_template("login.html")


# ------------------------------------
# DASHBOARD
# ------------------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("usuario"):
        return redirect("/login")
    return render_template("dashboard.html", usuario=session["usuario"])


# ------------------------------------
# LOGOUT
# ------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ------------------------------------
# RUN
# ------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
