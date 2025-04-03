import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde .env

MONGO_URL = os.getenv("MONGO_URL")  # Obtener la URL de MongoDB desde .env
