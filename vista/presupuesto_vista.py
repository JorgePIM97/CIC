"""
Vista para hacer inserción de metas
"""
import streamlit as st
import datetime
from .componentes.sidebar_ventas_real import SideBarVentaReal
from .seleccion_usuarios.seleccion import SeleccionUsuarios

class PresupuestoVista:

    def __init__(self):
        self.seleccion_vendedores = SideBarVentaReal()
        self.seleccion_usuarios = SeleccionUsuarios()
        self.meses_año = [
            'Enero', 'Febrero', 'Marzo', 'Abril',
            'Mayo', 'Junio', 'Julio', 'Agosto',
            'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
        ]

    def vendedores_real_selectbox(self):
        lista_vendedores = self.seleccion_usuarios.obtener_vendedores_excel()
        if not lista_vendedores:
            st.warning("No hay vendedores disponibles")
            return None
        return st.selectbox("Seleccionar vendedor:", options=lista_vendedores, index=0)

    def year_presupuesto(self):
        year_actual = datetime.datetime.now().year
        years = list(range(year_actual - 3, year_actual + 4))
        return st.selectbox("Seleccionar año:", options=years, index=3)

    # def meses_selectbox(self):
    #     return st.selectbox("Seleccionar mes:", options=self.meses_año, index=0)

    def meses_selectbox(self):
        opciones = ['Todos los meses'] + self.meses_año
        return st.selectbox("Seleccionar mes:", options=opciones, index=0)
    # ------------------------------------------------------------------
    # HELPER INTERNO
    # ------------------------------------------------------------------
    def _number_input(self, label, caption_label):
        valor = st.number_input(
            f"{label} (USD):",
            min_value=0.0,
            value=None,
            placeholder="Ingresa un valor...",
            step=1000.0,
            format="%.2f"
        )
        if valor and valor > 0:
            st.caption(f"💰 {caption_label}: ${valor:,.2f}")
        return valor if valor is not None else 0.0

    # ------------------------------------------------------------------
    # CONSUMIBLES (existentes)
    # ------------------------------------------------------------------
    def valor_consumible_mecanizado_plasma(self):
        return self._number_input("Valor de Consumible Mecanizado Plasma", "Consumible Mecanizado Plasma")

    def valor_consumible_manual(self):
        return self._number_input("Valor de Consumible Manual", "Consumible Manual")

    def valor_refacciones(self):
        return self._number_input("Valor de Refacciones", "Refacciones")

    def valor_consumible_mecanizado_laser(self):
        return self._number_input("Valor de Consumible Mecanizado Laser", "Consumible Mecanizado Laser")

    def valor_consumible_mecanizado_oxicorte(self):
        return self._number_input("Valor de Consumible Mecanizado Oxicorte", "Consumible Mecanizado Oxicorte")

    # ------------------------------------------------------------------
    # SISTEMAS (nuevos)
    # ------------------------------------------------------------------
    def valor_sis_corte_laser(self):
        return self._number_input("Valor de Sistema de Corte Laser", "Sistema de Corte Laser")

    def valor_sis_corte_plasma(self):
        return self._number_input("Valor de Sistema de Corte Plasma", "Sistema de Corte Plasma")

    def valor_sis_corte_oxy_water(self):
        return self._number_input("Valor de Sistema de Corte OxyWater", "Sistema de Corte OxyWater")

    def valor_powermax(self):
        return self._number_input("Valor de Powermax", "Powermax")

    def valor_robotica(self):
        return self._number_input("Valor de Robótica", "Robótica")