# controlador/base_controlador.py
import streamlit as st
from datetime import datetime, date, timedelta

class BaseControlador:
    """Clase base para todos los controladores"""
    
    def __init__(self):
        self.modelo = None
        self.vista = None
    
    def ejecutar(self):
        """Método principal que debe ser implementado por las subclases"""
        raise NotImplementedError("El método ejecutar debe ser implementado por las subclases")
    
    def manejar_error(self, error):
        """Maneja errores de manera centralizada"""
        if self.vista:
            self.vista.mostrar_error(f"Error: {str(error)}")
        else:
            print(f"Error: {str(error)}")

