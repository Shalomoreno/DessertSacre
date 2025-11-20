from flask import Flask, request, render_template, redirect, session
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import smtplib
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash

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
EMAIL_USER = "dessertsacre@gmail.com"
EMAIL_PASS = "utrehsexsumaxznm"   # Contraseña de aplicación Gmail


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
# INDEX
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

        # Validar correo existente
        cursor.execute("SELECT id FROM usuarios WHERE correo=%s", (correo,))
        if cursor.fetchone():
            return "El correo ya está registrado"

        # Encriptar contraseña
        password_hash = generate_password_hash(password)

        # Generar código
        codigo = str(random.randint(100000, 999999))

        cursor.execute("""
            INSERT INTO usuarios (nombre, correo, password, codigo_verificacion, verificado)
            VALUES (%s, %s, %s, %s, FALSE)
        """, (nombre, correo, password_hash, codigo))

        conexion.commit()

        # ENVIAR CÓDIGO
        enviar_codigo(correo, codigo)

        # GUARDAR CORREO TEMPORAL EN SESIÓN
        session["correo_temp"] = correo

        cursor.close()
        conexion.close()

        return redirect("/verify")

    return render_template("register.html")


# ------------------------------------
# VERIFICACIÓN
# ------------------------------------
@app.route("/verify", methods=["GET", "POST"])
def verify():
    correo = session.get("correo_temp")

    if not correo:
        return redirect("/register")

    if request.method == "POST":
        codigo_ingresado = request.form["codigo"]

        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT codigo_verificacion FROM usuarios WHERE correo=%s", (correo,))
        result = cursor.fetchone()

        if not result:
            return "Error interno."

        codigo_real = result[0]

        if codigo_ingresado == codigo_real:
            cursor.execute("""
                UPDATE usuarios SET verificado=TRUE WHERE correo=%s
            """, (correo,))
            conexion.commit()

            cursor.close()
            conexion.close()

            return redirect("/login")
        else:
            return "Código incorrecto ❌"

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

        cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (correo,))
        usuario = cursor.fetchone()

        if not usuario:
            return "Correo o contraseña incorrectos"

        # Comparar contraseña encriptada
        if not check_password_hash(usuario["password"], password):
            return "Correo o contraseña incorrectos"

        if not usuario["verificado"]:
            return "Debes verificar tu correo antes de iniciar sesión"

        session["usuario"] = usuario["nombre"]
        return redirect("/dashboard")

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
# NAVBAR
# ------------------------------------

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/historia')
def historia():
    return render_template('historia.html')

@app.route('/equipo')
def equipo():
    return render_template('equipo.html')

@app.route('/redes')
def redes():
    return render_template('redes.html')

@app.route('/ubicacion')
def ubicacion():
    return render_template('ubicacion.html')

# rutas de cuenta
@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    # lógica de logout
    return "Sesión cerrada", 200


# ------------------------------------
# RUN
# ------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
