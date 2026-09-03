# vista/resumen_movilidad_vista.py
"""
Vista para hacer inserción de resumen de movilidad
"""
import streamlit as st
import datetime
from modelo.metas_modelo import MetasModelo
from .seleccion_usuarios.seleccion import SeleccionUsuarios

class ResumenMovilidadVista:

    def __init__(self):
        self.seleccion_usuarios = SeleccionUsuarios()
        self.meses_año = [
            'Enero',
            'Febrero',
            'Marzo',
            'Abril',
            'Mayo',
            'Junio',
            'Julio',
            'Agosto',
            'Septiembre',
            'Octubre',
            'Noviembre',
            'Diciembre'
        ]

    # 1. NombreVendedor
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

    # 2. DiasHabiles: int
    def valor_dias_habiles_input(self):
        valor = st.number_input(
            "Días Habiles:",
            min_value=0,
            step=1,
            # value=st.session_state.get("dias_habiles", 0),
            key="dias_habiles"
        )

        return int(valor)

    # 3. Mes: varchar(25)
    def meses_selectbox(self):
        # Selectbox de meses (selección individual)
        mes_seleccionado = st.selectbox(
            "Seleccionar mes:",
            options=self.meses_año,
            index=0  # Selecciona el primer mes por defecto
        ) 
        return mes_seleccionado
    
    # 4. AvgDiarioRecorrido: decimal(18,2)
    def valor_avg_recorrido_input(self):
        valor = st.number_input(
            "Valor del Promedio Diario Recorrido (Km):",
            min_value=0.0,
            step=1.0,
            # value=st.session_state.get("avg_recorrido", 0.0),
            format="%.2f",
            key="avg_recorrido"
        )

        return valor


    # 5. CantidadVisitas: int
    def valor_cantidad_visitas_input(self):
        valor = st.number_input(
            "Cantidad Visitas:",
            min_value=0,
            step=1,
            # value=st.session_state.get("cantidad_visitas", 0),
            key="cantidad_visitas"
        )

        return int(valor)

    # 6. TiempoDestinadoAtencion: decimal(18,2)
    def valor_tiempo_atencion_input(self):
        valor = st.number_input(
            "Valor del Tiempo Destinado a Atención (Hrs):",
            min_value=0.0,
            step=1.0,
            # value=st.session_state.get("tiempo_atencion", 0.0),
            format="%.2f",
            key="tiempo_atencion"
        )

        return valor

    # 7. AvgTiempoConCliente: decimal(18,2)
    def valor_tiempo_cliente_input(self):
        valor = st.number_input(
            "Valor del Tiempo Promedio con Cliente (Hrs):",
            min_value=0.0,
            # value=st.session_state.get("tiempo_cliente", 0.0),
            step=1.0,
            format="%.2f",
            key="tiempo_cliente"
        )

        return valor

    # 8. AvgVisitasPorDia: int
    def valor_avg_visitas_dia_input(self):
        valor = st.number_input(
            "Cantidad Visitas por Día:",
            min_value=0,
            step=1,
            # value=st.session_state.get("avg_visitas_dia", 0),
            key="avg_visitas_dia"
        )

        return int(valor)
    
    # 10. Año: int
    def year_resumen_movilidad(self):
        year_actual = datetime.datetime.now().year
        
        # Genera rango ±3 años
        years = list(range(year_actual - 3, year_actual + 4))
        
        year_seleccionado = st.selectbox(
            "Seleccionar año:",
            options=years,
            index=3  # El año actual queda justo en el centro
        )
        
        return year_seleccionado
