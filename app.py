from flask import Flask, request, render_template, redirect, session
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import smtplib
from email.mime.text import MIMEText

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
# CONFIG SMTP GMAIL
# ------------------------------------
EMAIL_USER = "dessertsacre@gmail.com"       # <-- TU CORREO
EMAIL_PASS = "utrehsexsumaxznm"          # <-- TU CONTRASEÑA DE APLICACIÓN


def enviar_codigo(correo_destino, codigo):
    msg = MIMEText(f"Tu código de verificación es: {codigo}")
    msg["Subject"] = "Código de verificación"
    msg["From"] = EMAIL_USER
    msg["To"] = correo_destino

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
            print("Correo enviado ✔")
            return True

    except Exception as e:
        print("Error enviando correo:", e)
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

            cursor.close()
            conexion.close()

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
