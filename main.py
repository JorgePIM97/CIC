# main.py
import sys
import os
import streamlit as st

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controlador.navegacion_controlador_login import NavegacionControladorLogin

def main():
    """Función principal de la aplicación"""
    try:
        # Configurar la página principal
        st.set_page_config(
            page_title="Centro Inteligencia Comercial",
            page_icon="🏢",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Crear el controlador de navegación
        navegacion = NavegacionControladorLogin()

        # Ejecutar la aplicación
        navegacion.ejecutar_barra_principal()

    except Exception as e:
        st.error(f"Error al iniciar la aplicación: {str(e)}")
        st.error("Por favor, verifica que todos los archivos estén en su lugar correcto.")
        # Mostrar detalles del error en modo debug
        if st.checkbox("Mostrar detalles del error"):
            st.exception(e)

if __name__ == "__main__":
    main()