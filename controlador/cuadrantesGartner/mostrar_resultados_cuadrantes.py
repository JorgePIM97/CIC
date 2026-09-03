# controlador/mostrar_resultados_cuadrantes.py
import streamlit as st
from modelo.vendedores_modelo import VendedoresModelo
from modelo.gartner_modelo import GartnerModelo
from vista.vendedores_vista import VendedoresVista

class ResultadosCuadrantes:
    def __init__(self):
        self.vista = VendedoresVista()
        self.gartner_modelo = GartnerModelo()

    def mostrar_cuadrante_comparacion(self, df, tipo_cuadrante):
        """Muestra el cuadrante seleccionado para comparación"""
        if tipo_cuadrante == "Actividades vs Movilidad":
            self._mostrar_resultados_actividades_movilidad(df)
        elif tipo_cuadrante == "Tareas vs Actividades":
            self._mostrar_resultados_tareas_actividades(df)

    def _mostrar_resultados_actividades_movilidad(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis - versión modificada para permitir ocultar elementos"""
        # Colores por cuadrante
        colores_actividades_movilidad = {
        "Actividades Altas + Movilidad Alta": "#2ca02c",      # Verde
        "Actividades Altas + Movilidad Baja": "#1f77b4",     # Azul
        "Actividades Bajas + Movilidad Alta": "#ff7f0e",       # Naranja
        "Actividades Bajas + Movilidad Baja": "#d62728"       # Rojo
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_actividades, limite_km, limite_grafico_actividades, limite_grafico_km = \
            self.gartner_modelo.crear_cuadrante_actividades_movilidad(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_actividades, 
            limite_km, 
            limite_grafico_actividades, 
            limite_grafico_km,
            'KilometrajeAcumulado',
            'TotalActividades',
            "Movilidad (km)🚗",
            "Total de Actividades Realizadas 📌",
            colores_actividades_movilidad,
            "Actividades realizadas",
            "Movilidad (km)"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas y tabla solo si se solicita (para comparaciones no mostrar todo)
        if mostrar_metricas:
            self.vista.mostrar_metricas_actividades_movilidad(df)
        
        if mostrar_tabla:
            self.vista.mostrar_tabla_actividades_movilidad(df_clasificado)



    def _mostrar_resultados_tareas_actividades(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis - versión modificada para permitir ocultar elementos"""
        # Colores por cuadrante
        colores_tareas_actividades = {
        "Actividades Altas + Tareas Altas": "#2ca02c",      # Verde
        "Actividades Altas + Tareas Bajas": "#1f77b4",       # Azul
        "Actividades Bajas + Tareas Altas": "#ff7f0e",  # Naranja
        "Actividades Bajas + Tareas Bajas": "#d62728"       # Rojo
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_actividades, limite_tareas, limite_grafico_actividades, limite_grafico_tareas = \
            self.gartner_modelo.crear_cuadrante_tareas_actividades(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_tareas, 
            limite_actividades, 
            limite_grafico_tareas, 
            limite_grafico_actividades,
            'TotalActividades',
            'TotalTareas',
            "Total de Actividades Realizadas 📌",
            "Total de Tareas Programadas 📋",
            colores_tareas_actividades,
            "Tareas Programadas",
            "Actividades Realizadas"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas y tabla solo si se solicita
        if mostrar_metricas:
            self.vista.mostrar_metricas_tareas_actividades(df)
        
        if mostrar_tabla:
            self.vista.mostrar_tabla_tareas_actividades(df_clasificado)


    def _mostrar_resultados_tiempos_visita(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis"""
        # Colores por cuadrante
        colores_tiempo_visita = {
        "Visitas Altas + Tiempo Alto": "#2ca02c",      # Verde (ideal)
        "Visitas Altas + Tiempo Bajo": "#1f77b4",     # Azul (eficiente)
        "Visitas Bajas + Tiempo Alto": "#ff7f0e",     # Naranja (ineficiente)
        "Visitas Bajas + Tiempo Bajo": "#d62728"      # Rojo (problema)
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_visitas, limite_tiempo, limite_grafico_visitas, limite_grafico_tiempo = \
            self.gartner_modelo.crear_cuadrante_tiempos_visitas(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_visitas, 
            limite_tiempo, 
            limite_grafico_visitas, 
            limite_grafico_tiempo,
            'TotalHoras',
            'TotalVisitas',
            "Tiempo Acumulado en Visitas (Hrs) 🕒",
            "Visitas Presenciales 📍",
            colores_tiempo_visita,
            "Visitas Presenciales",
            "Tiempo Acumulado (Hrs)"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas
        if mostrar_metricas:
            self.vista.mostrar_metricas_tiempo_movilidad(df)
        
        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_tiempo_visitas(df_clasificado)

    def _mostrar_resultados_tiemposPromedio_visita(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis"""
        # Colores por cuadrante
        colores_tiempo_visita = {
        "Visitas Altas + Tiempo Alto": "#2ca02c",      # Verde (ideal)
        "Visitas Altas + Tiempo Bajo": "#1f77b4",     # Azul (eficiente)
        "Visitas Bajas + Tiempo Alto": "#ff7f0e",     # Naranja (ineficiente)
        "Visitas Bajas + Tiempo Bajo": "#d62728"      # Rojo (problema)
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_visitas, limite_tiempo, limite_grafico_visitas, limite_grafico_tiempo = \
            self.gartner_modelo.crear_cuadrante_tiemposPromedio_visitas(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_visitas, 
            limite_tiempo, 
            limite_grafico_visitas, 
            limite_grafico_tiempo,
            'PromedioHoras',
            'TotalVisitas',
            "Tiempo Promedio en Visitas (Hrs) 🕒",
            "Visitas Presenciales 📍",
            colores_tiempo_visita,
            "Visitas Presenciales",
            "Tiempo Promedio (Hrs)"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas
        if mostrar_metricas:
            self.vista.mostrar_metricas_tiempoPromedio_movilidad(df)
        
        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_tiempoPromedio_visitas(df_clasificado)

    def _mostrar_resultados_ventas_movilidad_force(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis"""
        colores_ventas_movilidad = {
            "Ventas Altas + Alta Movilidad": "#2ca02c",      
            "Ventas Altas + Baja Movilidad": "#1f77b4",     
            "Ventas Bajas + Alta Movilidad": "#ff7f0e",       
            "Ventas Bajas + Baja Movilidad": "#d62728"       
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_ventas, limite_km, limite_grafico_ventas, limite_grafico_km = \
            self.gartner_modelo.preparar_datos_cuadrante(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_ventas, 
            limite_km, 
            limite_grafico_ventas, 
            limite_grafico_km,
            'KilometrajeAcumulado',
            'TotalVendido',
            "Movilidad (km) 🚗",
            "Total Estimado Vendido (USD) 💰",
            colores_ventas_movilidad,
            "Ventas ($USD)",
            "Movilidad (km)"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas
        if mostrar_metricas:
            self.vista.mostrar_metricas_vendedores(df)
        
        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_ventas_movilidad(df_clasificado)

    def _mostrar_resultados_ventasForce_gps(self, df, mostrar_metricas=True, mostrar_tabla=True):
        # Colores por cuadrante
        colores_ventas_movilidad_gps = {
            "Ventas Altas + Alta Movilidad": "#2ca02c",      
            "Ventas Altas + Baja Movilidad": "#1f77b4",     
            "Ventas Bajas + Alta Movilidad": "#ff7f0e",       
            "Ventas Bajas + Baja Movilidad": "#d62728"       
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_ventas, limite_km, limite_grafico_ventas, limite_grafico_km = \
            self.gartner_modelo.preparar_cuadrante_ventasForce_gps(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_ventas, 
            limite_km, 
            limite_grafico_ventas, 
            limite_grafico_km,
            'KilometrajeAcumulado',
            'TotalVendido',
            "GPS (km) 🚗",
            "Total Estimado Vendido (USD) 💰",
            colores_ventas_movilidad_gps,
            "Ventas ($USD)",
            "Movilidad (km)"
        )
        self.vista.mostrar_grafico(fig)

        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_ventasForce_gps(df_clasificado)

    def _mostrar_resultados_ventasReales_gps(self, df, mostrar_metricas=True, mostrar_tabla=True):
        # Colores por cuadrante
        colores_ventasReales_movilidad_gps = {
            "Ventas Altas + Alta Movilidad": "#2ca02c",      
            "Ventas Altas + Baja Movilidad": "#1f77b4",     
            "Ventas Bajas + Alta Movilidad": "#ff7f0e",       
            "Ventas Bajas + Baja Movilidad": "#d62728"       
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_ventas, limite_km, limite_grafico_ventas, limite_grafico_km = \
            self.gartner_modelo.preparar_cuadrante_ventasReales_gps(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_ventas, 
            limite_km, 
            limite_grafico_ventas, 
            limite_grafico_km,
            'KilometrajeAcumulado',
            'IngresosUSD',
            "GPS (km) 🚗",
            "Total Vendido (USD) 💰",
            colores_ventasReales_movilidad_gps,
            "Ventas ($USD)",
            "Movilidad (km)"
        )
        self.vista.mostrar_grafico(fig)

        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_ventasReales_gps(df_clasificado)


    def _mostrar_resultados_ventas_movilidad_reales(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis"""
        colores_ventas_movilidad = {
            "Ventas Altas + Alta Movilidad": "#2ca02c",      
            "Ventas Altas + Baja Movilidad": "#1f77b4",     
            "Ventas Bajas + Alta Movilidad": "#ff7f0e",       
            "Ventas Bajas + Baja Movilidad": "#d62728"       
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_ventas, limite_km, limite_grafico_ventas, limite_grafico_km = \
            self.gartner_modelo.preparar_datos_reales_cuadrante(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_ventas, 
            limite_km, 
            limite_grafico_ventas, 
            limite_grafico_km,
            'KilometrajeAcumulado',
            'TotalVendido',
            "Movilidad (km) 🚗",
            "Total Vendido (USD) 💰",
            colores_ventas_movilidad,
            "Ventas ($USD)",
            "Movilidad (km)"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas
        if mostrar_metricas:
            self.vista.mostrar_metricas_ventas_reales(df_clasificado)
        
        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_ventas_reales_movilidad(df_clasificado)

    def _mostrar_resultados_visita_movilidad(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis"""
        # Colores por cuadrante
        colores_visita_movilidad = {
            "Visitas Altas + Alta Movilidad": "#2ca02c",      # Verde
            "Visitas Altas + Baja Movilidad": "#1f77b4",     # Azul
            "Visitas Bajas + Alta Movilidad": "#ff7f0e",       # Naranja
            "Visitas Bajas + Baja Movilidad": "#d62728"       # Rojo
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_visitas, limite_km, limite_grafico_visitas, limite_grafico_km = \
            self.gartner_modelo.preparar_cuadrante_visitas_movilidad(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_visitas, 
            limite_km, 
            limite_grafico_visitas, 
            limite_grafico_km,
            'KilometrajeAcumulado',
            'TotalVisitas',
            "Movilidad (km) 🚗",
            "Visitas Presenciales 📍",
            colores_visita_movilidad,
            "Visitas Presenciales",
            "Movilidad (km)"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas
        if mostrar_metricas:
            self.vista.mostrar_metricas_visitas_movilidad(df)
        
        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_visitas_movilidad(df_clasificado)


    def _mostrar_resultados_visitaGeneral_movilidad(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis"""
        # Colores por cuadrante
        colores_visita_movilidad = {
            "Visitas Altas + Alta Movilidad": "#2ca02c",      # Verde
            "Visitas Altas + Baja Movilidad": "#1f77b4",     # Azul
            "Visitas Bajas + Alta Movilidad": "#ff7f0e",       # Naranja
            "Visitas Bajas + Baja Movilidad": "#d62728"       # Rojo
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_visitas, limite_km, limite_grafico_visitas, limite_grafico_km = \
            self.gartner_modelo.preparar_cuadrante_visitas_generales_movilidad(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_visitas, 
            limite_km, 
            limite_grafico_visitas, 
            limite_grafico_km,
            'KilometrajeAcumulado',
            'TotalVisitasGeneral',
            "Movilidad (km) 🚗",
            "Visitas en General 📍",
            colores_visita_movilidad,
            "Visitas en General",
            "Movilidad (km)"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas
        if mostrar_metricas:
            self.vista.mostrar_metricas_visitas_general_movilidad(df)
        
        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_visitas_general_movilidad(df_clasificado)


    def _mostrar_resultados_visita_ventas(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis"""
        # Colores por cuadrante
        colores_visita_ventas = {
        "Visitas Altas + Ventas Altas": "#2ca02c",      # Verde
        "Visitas Altas + Ventas Bajas": "#ff7f0e",    # Naranja
        "Visitas Bajas + Ventas Altas": "#1f77b4",      # Azul
        "Visitas Bajas + Ventas Bajas": "#d62728"       # Rojo
        }
        # Preparar datos para el cuadrante
        df_clasificado, limite_visitas, limite_ventas, limite_grafico_visitas, limite_grafico_ventas = \
            self.gartner_modelo.preparar_cuadrante_visita_ventas(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_ventas, 
            limite_visitas, 
            limite_grafico_ventas, 
            limite_grafico_visitas,
            'TotalVisitas',
            'TotalVendido',
            "Visitas Presenciales 📍",
            "Total Estimado Vendido (USD) 💰",
            colores_visita_ventas,
            "Ventas ($USD)",
            "Visitas Presenciales"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas
        if mostrar_metricas:
            self.vista.mostrar_metricas_visitas_ventas(df)
        
        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_visitas_ventas(df_clasificado)

    def _mostrar_resultados_visita_ventasReales(self, df, mostrar_metricas=True, mostrar_tabla=True):
        """Muestra los resultados del análisis"""
        # Colores por cuadrante
        colores_visita_ventas = {
        "Visitas Altas + Ventas Altas": "#2ca02c",      # Verde
        "Visitas Altas + Ventas Bajas": "#ff7f0e",    # Naranja
        "Visitas Bajas + Ventas Altas": "#1f77b4",      # Azul
        "Visitas Bajas + Ventas Bajas": "#d62728"       # Rojo
    }
        # Preparar datos para el cuadrante
        df_clasificado, limite_visitas, limite_ventas, limite_grafico_visitas, limite_grafico_ventas = \
            self.gartner_modelo.preparar_cuadrante_visita_ventasReales(df)
        
        # Crear y mostrar el gráfico
        fig = self.vista.crear_cuadrante_gartner(
            df_clasificado, 
            limite_ventas, 
            limite_visitas, 
            limite_grafico_ventas, 
            limite_grafico_visitas,
            'TotalVisitas',
            'TotalVendido',
            "Visitas Presenciales 📍",
            "Total Vendido (USD) 💰",
            colores_visita_ventas,
            "Ventas ($USD)",
            "Visitas Presenciales"
        )
        self.vista.mostrar_grafico(fig)
        
        # Mostrar métricas
        if mostrar_metricas:
            self.vista.mostrar_metricas_visitas_ventasReales(df)
        
        # Mostrar tabla de resultados
        if mostrar_tabla:
            self.vista.mostrar_tabla_visitas_ventasReales(df_clasificado)    