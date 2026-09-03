#C:\CIC_WebApp\modelo\cifrado\crifrar_passwords.py
"""
Ejecutar cuando se decida cifrar las contraseñas para luego ser actualizadas ya con el cifrado
"""
import bcrypt
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()  # <-- necesario para cargar el archivo .env

conn = pyodbc.connect(
    f"DRIVER={os.getenv('DRIVER')};"
    f"SERVER={os.getenv('SERVER')};"
    f"DATABASE={os.getenv('DATABASE')};"
    f"UID={os.getenv('USERNAME')};"
    f"PWD={os.getenv('PASSWORD')};"
)

cursor = conn.cursor()

# Obtener todos los usuarios con contraseñas aún sin cifrar
cursor.execute("SELECT IdUsuario, Password FROM UsuariosCIC WHERE Status = 1")
usuarios = cursor.fetchall()

actualizados = 0
omitidos = 0

for u in usuarios:
    # Si ya empieza con $2b$ significa que ya está cifrado, se omite
    if u.Password.startswith('$2b$'):
        omitidos += 1
        continue

    hashed = bcrypt.hashpw(u.Password.encode(), bcrypt.gensalt()).decode('utf-8')
    cursor.execute(
        "UPDATE UsuariosCIC SET Password = ? WHERE IdUsuario = ?",
        (hashed, u.IdUsuario)
    )
    actualizados += 1

conn.commit()
conn.close()

print(f"Actualizados: {actualizados} | Ya cifrados (omitidos): {omitidos}")