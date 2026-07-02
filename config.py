class Config:
    # Clave de flask 
    SECRET_KEY = "clave_super_secreta_local"

    # Datos de la bases de datos en PostgreSQL
    DB_CONFIG = {
        "host": "localhost",
        "dbname": "Dessert_Sacre",
        "user": "postgres",
        "password": "123456",
        "port": 5432
    }

    # Info para que haya relacion al momento de enviar los correo al Gmail
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = "dessertsacre@gmail.com"
    MAIL_PASSWORD = ""

    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    # Clave para Stripe
    STRIPE_SECRET_KEY = ""