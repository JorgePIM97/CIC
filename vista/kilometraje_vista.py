# vista/kkilometraje_vista.py
"""
Vista para hacer inserción de metas
"""
import streamlit as st
from modelo.metas_modelo import MetasModelo
from .seleccion_usuarios.seleccion import SeleccionUsuarios
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class KilometrajeVista:
    def __init__(self):
        self.seleccion_usuarios = SeleccionUsuarios()


    def vendedores_real_selectbox(self):
        vendedores = self.seleccion_usuarios.obtener_vendedores_force()
        
        if not vendedores:
            st.warning("No hay vendedores disponibles")
            return None
        
        # Selectbox de vendedores (selección individual)
        vendedor_seleccionado = st.selectbox(
            "Seleccionar vendedor:",
            options=vendedores,
            index=0  # Selecciona el primer vendedor por defecto
        )

        return vendedor_seleccionado


    def valor_kilometraje_input(self):
        valor_kilometraje = st.number_input(
            "Kilómetros del día:",
            min_value=0.0,
            step=1000.0,
            format="%.2f",
            value=None,  # Sin valor por defecto
            placeholder="Ingrese los kilómetros del recorrido"
        )

        # if valor_kilometraje is None or valor_kilometraje <= 0:
        #     st.warning("Debe ingresar un valor válido de kilómetros.")
    
        return valor_kilometraje

    

    def descripcion_input(self):

        descripcion = st.text_area(
            label="Descripción del recorrido (Opcional)",
            placeholder="Escribe aquí una descripción del recorrido del vendedor...",
            height=150  # puedes ajustar el alto del área de texto
        )

        return descripcion
    
    def fechaKilometraje_input(self):
        # Fecha de inicio: un mes antes del mes actual
        fecha_inicio_default = date.today()
        fecha_inicio = st.date_input("Fecha del recorrido:", fecha_inicio_default)

        return fecha_inicio