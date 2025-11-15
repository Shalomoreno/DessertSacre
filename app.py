from flask import Flask, request, render_template, redirect, session, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import smtplib
import random
import os

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


# -----------------------------
# ENVIAR CODIGO AL CORREO
# -----------------------------
def enviar_codigo(correo, codigo):
    remitente = "tucorreo@gmail.com"
    contraseña = "tu_contraseña_app"

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, contraseña)
        mensaje = f"Subject: Código de verificación\n\nTu código es: {codigo}"
        servidor.sendmail(remitente, correo, mensaje)
        servidor.quit()
        print("Código enviado.")
    except:
        print("No se pudo enviar el correo.")


# -----------------------------
# PÁGINA PRINCIPAL
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------
# REGISTRO
# -----------------------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]

        conexion = conectar_bd()
        cursor = conexion.cursor()

        codigo = str(random.randint(100000, 999999))

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password, codigo_verificacion)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, password, codigo))

        conexion.commit()
        cursor.close()
        conexion.close()

        enviar_codigo(correo, codigo)

        session["correo_temp"] = correo

        return redirect("/verify")

    return render_template("register.html")


# -----------------------------
# VERIFICAR CÓDIGO
# -----------------------------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        codigo_ingresado = request.form["codigo"]
        correo = session.get("correo_temp")

        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT codigo_verificacion FROM usuarios WHERE correo=%s", (correo,))
        correcto = cursor.fetchone()[0]

        if codigo_ingresado == correcto:
            cursor.execute("UPDATE usuarios SET verificado=TRUE WHERE correo=%s", (correo,))
            conexion.commit()
            return redirect("/login")
        else:
            return "Código incorrecto"

    return render_template("verify.html")


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET","POST"])
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


# -----------------------------
# DASHBOARD (PÁGINA PROTEGIDA)
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("usuario"):
        return redirect("/login")

    return render_template("dashboard.html", usuario=session["usuario"])


# -----------------------------
# CERRAR SESIÓN
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
