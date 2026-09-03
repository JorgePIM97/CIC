#vista/componentes/botones.py
import streamlit as st

class BotonesApp:

    def boton_vendedor(self, label, type, use_container_width):
        return st.sidebar.button(
                label= label,
                type= type,
                use_container_width= use_container_width
            )
        
    def boton_deshabilitado(self, label, disabled, use_container_width, help):
        return st.sidebar.button(
            label= label, # "🔒 Comportamiento Vendedores"
            disabled= disabled, # True
            use_container_width= use_container_width, #True
            help= help # "No tienes permisos para acceder a este módulo"
        )

    def boton_generar_reporte(self, label, type, use_container_width):
        return st.button(
                label= label,
                type= type,
                use_container_width= use_container_width
            )
        