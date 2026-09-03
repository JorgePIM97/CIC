# controlador/visitas_ventas_controlador.py
import streamlit as st
import pandas as pd 
from modelo.vendedores_modelo import VendedoresModelo
from modelo.gartner_modelo import GartnerModelo
from vista.vendedores_vista import VendedoresVista
from vista.login.login_vista import LoginVista
from .mostrar_resultados_cuadrantes import ResultadosCuadrantes

class VisitaVentasControlador:
    def __init__(self):
        self.modelo = VendedoresModelo()
        self.vista = VendedoresVista()
        self.gartner_modelo = GartnerModelo()
        self.login_vista = LoginVista()
        self.mostrar_resultados = ResultadosCuadrantes()
    
    def ejecutar_vista_cuadrante(self):
        """Método principal que ejecuta la aplicación"""
        # Configurar la página
        self.vista.configurar_pagina()
        
        # Mostrar título
        self.vista.mostrar_titulo("📊 Visitas Presenciales vs Total Vendido")

        # fecha_inicio, fecha_fin, vendedores = self.vista.mostrar_sidebar_cuadrantes()
        fecha_inicio, fecha_fin, vendedores, cuadrante_comparacion = self.vista.mostrar_sidebar_cuadrantes()
        
        # Procesar datos si hay vendedores seleccionados
        if vendedores:
            self._procesar_datos(fecha_inicio, fecha_fin, vendedores, cuadrante_comparacion)
        else:
            self.vista.mostrar_mensaje_info("Selecciona al menos un vendedor para generar el análisis.")
    
    def _procesar_datos(self, fecha_inicio, fecha_fin, vendedores, cuadrante_comparacion):
        """Procesa los datos y muestra los resultados"""
        with self.vista.mostrar_spinner("Obteniendo datos..."):
            # Obtener datos del modelo usando la función correcta para visitas y movilidad
            df = self.modelo.obtener_visita_ventas(
                fecha_inicio.strftime('%Y%m%d'),
                fecha_fin.strftime('%Y%m%d'),
                fecha_inicio.strftime('%Y%m%d'),
                fecha_fin.strftime('%Y%m%d'),
                vendedores
            )

        with self.vista.mostrar_spinner("Obteniendo datos..."):
            # Obtener datos del modelo usando la función correcta para visitas y movilidad
            df_real = self.modelo.obtener_visita_ventasReales(
                fecha_inicio.strftime('%Y%m%d'),
                fecha_fin.strftime('%Y%m%d'),
                fecha_inicio.strftime('%Y%m%d'),
                fecha_fin.strftime('%Y%m%d'),
                vendedores
            )
        
        if not df.empty and not df_real.empty:

            get_cargo = self.login_vista.get_cargo_de_sesion()

            if get_cargo == 'CEO':

                if cuadrante_comparacion == "Ninguno":
                    st.subheader("✅ Visitas vs Ventas Reales")
                    self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)

                elif cuadrante_comparacion == "Visitas vs Ventas Reales":
                    st.subheader("✅ Visitas vs Ventas Reales")
                    self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)

                else:
                    # Mostrar comparación lado a lado
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Visitas vs Ventas Reales")
                        self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)
                    
                    with col2:
                        self.comparacion_privilegios_completos(cuadrante_comparacion, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, vendedores)

            elif get_cargo == 'DIRECTOR DE PRODUCCION':

                if cuadrante_comparacion == "Ninguno":
                    # Mostrar solo el cuadrante principal
                    st.subheader("✅ Visitas vs Ventas Reales")
                    self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)

                elif cuadrante_comparacion == "Visitas vs Ventas Reales":
                    # Mostrar solo el cuadrante principal
                    st.subheader("✅ Visitas vs Ventas Reales")
                    self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)

                else:
                    # Mostrar comparación lado a lado
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Visitas vs Ventas Reales")
                        self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)
                    
                    with col2:
                        self.comparacion_privilegios_completos(cuadrante_comparacion, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, vendedores)

            elif get_cargo == 'DIRECTOR COMERCIAL':

                if cuadrante_comparacion == "Ninguno":
                    # Mostrar solo el cuadrante principal
                    # self.mostrar_resultados._mostrar_resultados_ventas_movilidad_force(df, mostrar_metricas=False, mostrar_tabla=True)
                    st.subheader("✅ Visitas vs Ventas Reales")
                    self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)

                elif cuadrante_comparacion == "Visitas vs Ventas Reales":
                    # Mostrar solo el cuadrante principal
                    # self.mostrar_resultados._mostrar_resultados_ventas_movilidad_force(df, mostrar_metricas=False, mostrar_tabla=True)
                    st.subheader("✅ Visitas vs Ventas Reales")
                    self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)

                else:
                    # Mostrar comparación lado a lado
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Visitas vs Ventas Reales")
                        # self.mostrar_resultados._mostrar_resultados_ventas_movilidad_force(df, mostrar_metricas=False, mostrar_tabla=True)
                        self.mostrar_resultados._mostrar_resultados_visita_ventasReales(df_real, mostrar_metricas=False, mostrar_tabla=True)
                    
                    with col2:
                        self.comparacion_privilegios_completos(cuadrante_comparacion, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, vendedores)

            elif get_cargo == 'COORDINADOR INTELIGENCIA COMERCIAL': 

                if cuadrante_comparacion == "Ninguno":
                    # Mostrar solo el cuadrante principal
                    self.mostrar_resultados._mostrar_resultados_visita_ventas(df, mostrar_metricas=False, mostrar_tabla=True)

                elif cuadrante_comparacion == "Visitas vs Ventas":
                    # Mostrar solo el cuadrante principal
                    self.mostrar_resultados._mostrar_resultados_visita_ventas(df, mostrar_metricas=False, mostrar_tabla=True)

                else:
                    # Mostrar comparación lado a lado
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Visitas vs Ventas")
                        self.mostrar_resultados._mostrar_resultados_visita_ventas(df, mostrar_metricas=False, mostrar_tabla=True)
                    
                    with col2:
                        self.comparacion_privilegios_acotados(cuadrante_comparacion, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, vendedores)

            elif get_cargo == 'COORDINADOR DE VENTAS':   

                if cuadrante_comparacion == "Ninguno":
                    # Mostrar solo el cuadrante principal
                    self.mostrar_resultados._mostrar_resultados_visita_ventas(df, mostrar_metricas=False, mostrar_tabla=True)

                elif cuadrante_comparacion == "Visitas vs Ventas":
                    # Mostrar solo el cuadrante principal
                    self.mostrar_resultados._mostrar_resultados_visita_ventas(df, mostrar_metricas=False, mostrar_tabla=True)

                else:
                    # Mostrar comparación lado a lado
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Visitas vs Ventas")
                        self.mostrar_resultados._mostrar_resultados_visita_ventas(df, mostrar_metricas=False, mostrar_tabla=True)
                    
                    with col2:
                        self.comparacion_privilegios_acotados(cuadrante_comparacion, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, vendedores)

        else:
            self.vista.mostrar_mensaje_warning("No se encontraron datos para las fechas seleccionadas.")

    def _obtener_datos_cuadrante_comparacion(self, fecha_inicio_actividades, fecha_fin_actividades,fecha_inicio_tareas, fecha_fin_tareas, vendedores, df_datos: VendedoresModelo):
        """Obtiene datos para el cuadrante de tareas vs actividades"""
        # Aquí necesitarás implementar la lógica para obtener datos de tareas
        # Ejemplo (ajusta según tu modelo):
        try:
            df_tareas = df_datos(
                fecha_inicio_actividades.strftime('%Y%m%d'),
                fecha_fin_actividades.strftime('%Y%m%d'),
                fecha_inicio_tareas.strftime('%Y%m%d'),
                fecha_fin_tareas.strftime('%Y%m%d'),
                vendedores
            )
            return df_tareas
        except Exception as e:
            st.error(f"Error al obtener datos de tareas: {str(e)}")
            return pd.DataFrame()
        
    def comparacion_privilegios_completos(self, cuadrante_comparacion, fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores):
        st.subheader(f"📌 {cuadrante_comparacion}")

        if cuadrante_comparacion == "Visitas vs Ventas Estimadas":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_datos_completos)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_ventas_movilidad_force(df_tareas, mostrar_metricas=False, mostrar_tabla=True)
        
        elif cuadrante_comparacion == "Ventas vs GPS":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_2, fecha_inicio_1, fecha_fin_2, vendedores, self.modelo.obtener_datos_ventasReales_gps)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_ventasReales_gps(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Tareas vs Actividades":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_tareas_actividades)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_tareas_actividades(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Tiempos vs Visitas":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_tiemposVisita_visitas)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_tiempos_visita(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Tiempos Promedio vs Visitas":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_tiemposVisitaPromedio_visitas)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_tiemposPromedio_visita(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Visitas vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_visita_movilidad)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_visita_movilidad(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Visitas Generales vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_visitaGeneral_movilidad)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_visitaGeneral_movilidad(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Actividades vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_actividades_movilidad)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_actividades_movilidad(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Ventas Estimadas vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_datos_completos)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_ventas_movilidad_force(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Ventas Reales vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_datos_reales_completos)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_ventas_movilidad_reales(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

    def comparacion_privilegios_acotados(self, cuadrante_comparacion, fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores):
        st.subheader(f"📌 {cuadrante_comparacion}")
        
        if cuadrante_comparacion == "Tareas vs Actividades":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_tareas_actividades)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_tareas_actividades(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Ventas vs GPS":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_2, fecha_inicio_1, fecha_fin_2, vendedores, self.modelo.obtener_datos_ventasForce_gps)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_ventasForce_gps(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Tiempos vs Visitas":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_tiemposVisita_visitas)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_tiempos_visita(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Tiempos Promedio vs Visitas":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_tiemposVisitaPromedio_visitas)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_tiemposPromedio_visita(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Visitas vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_visita_movilidad)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_visita_movilidad(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Visitas Generales vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_visitaGeneral_movilidad)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_visitaGeneral_movilidad(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Actividades vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_actividades_movilidad)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_actividades_movilidad(df_tareas, mostrar_metricas=False, mostrar_tabla=True)

        elif cuadrante_comparacion == "Ventas vs Movilidad":
            df_tareas = self._obtener_datos_cuadrante_comparacion(fecha_inicio_1, fecha_fin_1, fecha_inicio_2, fecha_fin_2, vendedores, self.modelo.obtener_datos_completos)
            if not df_tareas.empty:
                self.mostrar_resultados._mostrar_resultados_ventas_movilidad_force(df_tareas, mostrar_metricas=False, mostrar_tabla=True)
