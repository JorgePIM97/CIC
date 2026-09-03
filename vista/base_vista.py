# vista/base_vista.py
import streamlit as st

class BaseVista:
    """Clase base para todas las vistas"""
    
    def __init__(self):
        self.titulo = ""
        self.icono = ""
    
    def configurar_pagina(self, titulo, icono="📊", layout="wide"):
        """Configuración básica de la página"""
        st.set_page_config(
            page_title=titulo,
            page_icon=icono,
            layout=layout
        )
    
    def mostrar_titulo(self, titulo):
        """Muestra el título de la página"""
        st.title(titulo)
        st.markdown("---")
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        st.error(mensaje)
    
    def mostrar_exito(self, mensaje):
        """Muestra un mensaje de éxito"""
        st.success(mensaje)
    
    def mostrar_info(self, mensaje):
        """Muestra un mensaje informativo"""
        st.info(mensaje)
    
    def mostrar_warning(self, mensaje):
        """Muestra un mensaje de advertencia"""
        st.warning(mensaje)