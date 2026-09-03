# controlador/rendimiento/rendimiento_controlador.py
import streamlit as st
import pandas as pd
from datetime import timedelta
from vista.base_vista import BaseVista
from vista.componentes.sidebar_ventas_real import SideBarVentaReal
from modelo.ventas_reales_modelo import VentasRealesModelo
from vista.rendimiento_vista import RendimientoVista
from vista.login.login_vista import LoginVista
from vista.componentes.info_filtros import InfoFiltros

class RendimientoControlador(BaseVista):
    def __init__(self):
        self.vista_componente = SideBarVentaReal()
        self.modelo_ventas = VentasRealesModelo()
        self.rendimiento_vista = RendimientoVista()
        self.login_vista = LoginVista()
        self.info_filtros = InfoFiltros()
        
    def ejecutar_vista_rendimiento(self):
        self.mostrar_titulo("📊 Rendimiento de los Vendedores")

        # Mostrar sidebar con filtros
        vendedores_seleccionados, fecha_inicio, fecha_fin = self.vista_componente.mostrar_sidebar_rendimiento(self.modelo_ventas)
        self.info_filtros.mostrar_info_filtro(vendedores_seleccionados, fecha_inicio, fecha_fin)

        st.markdown("---")

        # Verificar que se hayan seleccionado vendedores y fechas
        if not vendedores_seleccionados:
            st.warning("⚠️ Por favor selecciona al menos un vendedor")
            return
        
        if not fecha_inicio or not fecha_fin:
            st.warning("⚠️ Por favor selecciona el rango de fechas")
            return
        
        get_cargo = self.login_vista.get_cargo_de_sesion()

        # Determinar si es rango o mensual basado en el tipo de filtro
        tipo_filtro = st.session_state.get('tipo_filtro', 'Mensual')
        
        if tipo_filtro == "Por Rango de Fechas":
            # Usar métricas de rango
            if get_cargo == 'COORDINADOR INTELIGENCIA COMERCIAL': # ROL DE RAFA
                self.rendimiento_vista.mostrar_metricas_rendimiento_rangos_porcentajes(
                    vendedores_seleccionados, 
                    fecha_inicio, 
                    fecha_fin
                )
            else: # CUALQUIER OTRO ROL
                self.rendimiento_vista.mostrar_metricas_rendimiento_rango(
                    vendedores_seleccionados, 
                    fecha_inicio, 
                    fecha_fin
                )
        else:
            if get_cargo == 'COORDINADOR INTELIGENCIA COMERCIAL': # ROL DE RAFA
                self.rendimiento_vista.mostrar_metricas_rendimiento_porcentajes(
                    vendedores_seleccionados, 
                    fecha_inicio, 
                    fecha_fin
                )
            else: # CUALQUIER OTRO ROL
                self.rendimiento_vista.mostrar_metricas_rendimiento(
                    vendedores_seleccionados, 
                    fecha_inicio, 
                    fecha_fin
                )