# modelo/usuarios_modelo.py
import pandas as pd
import streamlit as st
from .db_connection import DatabaseConnection
import bcrypt

class UsuariosModelo:
    def __init__(self):
        self.db = DatabaseConnection()
    
    # def validar_usuario(self, correo, password):
    #     """Valida si existe un usuario con ese correo y password"""
    #     # Solo buscar por correo, el password se valida con bcrypt después
    #     query = """
    #         SELECT IdUsuario, Nombre, Apellido, Cargo, Zona, Status, Password
    #         FROM UsuariosCIC
    #         WHERE Correo = ? AND Status = 1
    #     """
    #     conn = self.db.get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute(query, (correo,))
    #     row = cursor.fetchone()
    #     conn.close()

    #     if row is None:
    #         return None  # Correo no existe

    #     try:
    #         if bcrypt.checkpw(password.encode(), row.Password.encode()):
    #             return row
    #     except Exception:
    #         return None  # Hash inválido o contraseña incorrecta

    #     return None

    # def actualizar_password(self, correo: str, nueva_password: str) -> bool:
    #     hashed = bcrypt.hashpw(nueva_password.encode(), bcrypt.gensalt()).decode('utf-8')  # <-- .decode()
    #     query = """
    #         UPDATE UsuariosCIC
    #         SET Password = ?
    #         WHERE Correo = ? AND Status = 1
    #     """
    #     conn = self.db.get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute(query, (hashed, correo))
    #     filas_afectadas = cursor.rowcount
    #     conn.commit()
    #     conn.close()
    #     return filas_afectadas > 0
        
    def validar_usuario(self, correo, password):
        """Valida si existe un usuario con ese correo y password"""
        query = """
            SELECT IdUsuario, Nombre, Apellido, Cargo, Zona, Status
            FROM UsuariosCIC
            WHERE Correo = ? AND Password = ? AND Status = 1
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (correo, password))
        row = cursor.fetchone()
        conn.close()
        return row  # None si no existe

    def actualizar_password(self, correo: str, nueva_password: str) -> bool:
        """Actualiza la contraseña del usuario dado su correo. Retorna True si se actualizó."""
        query = """
            UPDATE UsuariosCIC
            SET Password = ?
            WHERE Correo = ? AND Status = 1
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (nueva_password, correo))
        filas_afectadas = cursor.rowcount
        conn.commit()
        conn.close()
        return filas_afectadas > 0
    

    def obtener_correo(self, cargo):
        """Valida si existe un usuario con ese correo y password"""
        query = """
            SELECT Correo
            FROM UsuariosCIC
            WHERE Cargo = ? 
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (cargo))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None  # None si no existe
