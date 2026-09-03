# modelo/gartner_modelo.py
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

class GartnerModelo:
    '''Clasificaciones del vendedor en el cuadrante
    '''
    @staticmethod
    def clasificar_vendedor(ventas, km, limite_ventas, limite_km):
        """Clasifica al vendedor en ventas vs movilidad según el cuadrante"""
        if ventas >= limite_ventas and km >= limite_km:
            return "Ventas Altas + Alta Movilidad", "Alta Performance + Alta Movilidad"
        elif ventas >= limite_ventas and km < limite_km:
            return "Ventas Altas + Baja Movilidad", "Alta Performance + Baja Movilidad"
        elif ventas <= limite_ventas and km >= limite_km:
            return "Ventas Bajas + Alta Movilidad", "Baja Performance + Alta Movilidad"
        else:
            return "Ventas Bajas + Baja Movilidad", "Baja Performance + Baja Movilidad"
        
    @staticmethod
    def clasificar_vendedorReal(ventas, km, limite_ventas, limite_km):
        """Clasifica al vendedor en ventas vs movilidad según el cuadrante"""
        if ventas >= limite_ventas and km >= limite_km:
            return "Ventas Altas + Alta Movilidad", "Alta Performance + Alta Movilidad"
        elif ventas >= limite_ventas and km < limite_km:
            return "Ventas Altas + Baja Movilidad", "Alta Performance + Baja Movilidad"
        elif ventas < limite_ventas and km >= limite_km:
            return "Ventas Bajas + Alta Movilidad", "Baja Performance + Alta Movilidad"
        else:
            return "Ventas Bajas + Baja Movilidad", "Baja Performance + Baja Movilidad"
        
    
    @staticmethod
    def clasificar_visita_movilidad(visitas, km, limite_visitas, limite_km):
        """Clasifica el vendedor en visita vs movilidad según el cuadrante"""
        if visitas >= limite_visitas and km >= limite_km:
            return "Visitas Altas + Alta Movilidad", "Altas Visitas + Alta Movilidad"
        elif visitas >= limite_visitas and km < limite_km:
            return "Visitas Altas + Baja Movilidad", "Altas Visitas + Baja Movilidad"
        elif visitas < limite_visitas and km >= limite_km:
            return "Visitas Bajas + Alta Movilidad", "Bajas Visitas + Alta Movilidad"
        else:
            return "Visitas Bajas + Baja Movilidad", "Bajas Visitas + Baja Movilidad"
        
    @staticmethod
    def clasificar_visita_ventas(visitas, ventas, limite_visitas, limite_ventas):
        """Clasifica al vendedor según el cuadrante"""
        if visitas >= limite_visitas and ventas >= limite_ventas:
            return "Visitas Altas + Ventas Altas", "Visitas Altas + Ventas Altas"
        elif visitas >= limite_visitas and ventas < limite_ventas:
            return "Visitas Altas + Ventas Bajas", "Visitas Altas + Ventas Bajas"
        elif visitas < limite_visitas and ventas >= limite_ventas:
            return "Visitas Bajas + Ventas Altas", "Visitas Bajas + Ventas Altas"
        else:
            return "Visitas Bajas + Ventas Bajas", "Visitas Bajas + Ventas Bajas"
        
    @staticmethod
    def clasificar_tareas_actividades(actividades, tareas, limite_actividades, limite_tareas):
        """Clasifica al vendedor según el cuadrante"""
        if actividades >= limite_actividades and tareas >= limite_tareas:
            return "Actividades Altas + Tareas Altas", "Actividades Altas + Tareas Altas"
        elif actividades >= limite_actividades and tareas < limite_tareas:
            return "Actividades Altas + Tareas Bajas", "Actividades Altas + Tareas Bajas"
        elif actividades < limite_actividades and tareas >= limite_tareas:
            return "Actividades Bajas + Tareas Altas", "Actividades Bajas + Tareas Altas"
        else:
            return "Actividades Bajas + Tareas Bajas", "Actividades Bajas + Tareas Bajas"
        
    @staticmethod
    def clasificar_actividades_movilidad(actividades, km, limite_actividades, limite_km):
        """Clasifica al vendedor según el cuadrante"""
        if actividades >= limite_actividades and km >= limite_km:
            return "Actividades Altas + Movilidad Alta", "Actividades Altas + Movilidad Alta"
        elif actividades >= limite_actividades and km < limite_km:
            return "Actividades Altas + Movilidad Baja", "Actividades Altas + Movilidad Baja"
        elif actividades < limite_actividades and km >= limite_km:
            return "Actividades Bajas + Movilidad Alta", "Actividades Bajas + Movilidad Alta"
        else:
            return "Actividades Bajas + Movilidad Baja", "Actividades Bajas + Movilidad Baja"

    @staticmethod
    def clasificar_tiempo_visitas(visitas, horas, limite_visitas, limite_horas):
        """Clasifica al vendedor según el cuadrante"""
        if visitas >= limite_visitas and horas >= limite_horas:
            return "Visitas Altas + Tiempo Alto", "Visitas Altas + Tiempo Alto"
        elif visitas >= limite_visitas and horas < limite_horas:
            return "Visitas Altas + Tiempo Bajo", "Visitas Altas + Tiempo Bajo"
        elif visitas < limite_visitas and horas >= limite_horas:
            return "Visitas Bajas + Tiempo Alto", "Visitas Bajas + Tiempo Alto"
        else:
            return "Visitas Bajas + Tiempo Bajo", "Visitas Bajas + Tiempo Bajo"

    @staticmethod
    def clasificar_ventasForce_gps(ventas, km, limite_ventas, limite_km):
        """Clasifica al vendedor según el cuadrante"""
        if ventas >= limite_ventas and km >= limite_km:
            return "Ventas Altas + Alta Movilidad", "Alta Performance + Alta Movilidad"
        elif ventas >= limite_ventas and km < limite_km:
            return "Ventas Altas + Baja Movilidad", "Alta Performance + Baja Movilidad"
        elif ventas < limite_ventas and km >= limite_km:
            return "Ventas Bajas + Alta Movilidad", "Baja Performance + Alta Movilidad"
        else:
            return "Ventas Bajas + Baja Movilidad", "Baja Performance + Baja Movilidad"

    @staticmethod
    def clasificar_ventasReales_gps(ventas, km, limite_ventas, limite_km):
        """Clasifica al vendedor según el cuadrante"""
        if ventas >= limite_ventas and km >= limite_km:
            return "Ventas Altas + Alta Movilidad", "Alta Performance + Alta Movilidad"
        elif ventas >= limite_ventas and km < limite_km:
            return "Ventas Altas + Baja Movilidad", "Alta Performance + Baja Movilidad"
        elif ventas < limite_ventas and km >= limite_km:
            return "Ventas Bajas + Alta Movilidad", "Baja Performance + Alta Movilidad"
        else:
            return "Ventas Bajas + Baja Movilidad", "Baja Performance + Baja Movilidad"
        
    '''Preparacion de limite de datos en el cuadrante
    '''
    @staticmethod
    def preparar_cuadrante_ventasReales_gps(df):
        """Prepara los datos para el cuadrante de Gartner"""
        # Convertir a float para evitar problemas con Decimal
        df['IngresosUSD'] = pd.to_numeric(df['IngresosUSD'], errors='coerce')
        df['KilometrajeAcumulado'] = pd.to_numeric(df['KilometrajeAcumulado'], errors='coerce')
        
        # Calcular límites dinámicos
        max_ventas = float(df['IngresosUSD'].max())
        max_km = float(df['KilometrajeAcumulado'].max())
        
        # Evitar división por cero
        if max_ventas == 0:
            max_ventas = 1
        if max_km == 0:
            max_km = 1
        
        limite_ventas = max_ventas / 2  # Punto medio como límite
        limite_km = max_km / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen del 10%)
        limite_grafico_ventas = max_ventas * 1.1
        limite_grafico_km = max_km * 1.1
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_ventasReales_gps(row['IngresosUSD'], row['KilometrajeAcumulado'], 
                                        limite_ventas, limite_km), axis=1
        ))

        return df, limite_ventas, limite_km, limite_grafico_ventas, limite_grafico_km

    @staticmethod
    def preparar_cuadrante_ventasForce_gps(df):
        """Prepara los datos para el cuadrante de Gartner"""
        # Convertir a float para evitar problemas con Decimal
        df['TotalVendido'] = pd.to_numeric(df['TotalVendido'], errors='coerce')
        df['KilometrajeAcumulado'] = pd.to_numeric(df['KilometrajeAcumulado'], errors='coerce')
        
        # Calcular límites dinámicos
        max_ventas = float(df['TotalVendido'].max())
        max_km = float(df['KilometrajeAcumulado'].max())
        
        limite_ventas = max_ventas / 2  # Punto medio como límite
        limite_km = max_km / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen del 10%)
        limite_grafico_ventas = max_ventas * 1.1
        limite_grafico_km = max_km * 1.1
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_ventasForce_gps(row['TotalVendido'], row['KilometrajeAcumulado'], 
                                        limite_ventas, limite_km), axis=1
        ))

        return df, limite_ventas, limite_km, limite_grafico_ventas, limite_grafico_km

    @staticmethod
    def preparar_datos_cuadrante(df):
        """Prepara los datos para el cuadrante de Gartner"""
        # Convertir a float para evitar problemas con Decimal
        df['TotalVendido'] = pd.to_numeric(df['TotalVendido'], errors='coerce')
        df['KilometrajeAcumulado'] = pd.to_numeric(df['KilometrajeAcumulado'], errors='coerce')
        
        # Calcular límites dinámicos
        max_ventas = float(df['TotalVendido'].max())
        max_km = float(df['KilometrajeAcumulado'].max())
        
        limite_ventas = max_ventas / 2  # Punto medio como límite
        limite_km = max_km / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_ventas = max_ventas + 100000
        limite_grafico_km = max_km + 100
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_vendedor(
                row['TotalVendido'], 
                row['KilometrajeAcumulado'], 
                limite_ventas, 
                limite_km
            ), axis=1
        ))
        
        return df, limite_ventas, limite_km, limite_grafico_ventas, limite_grafico_km
    
    @staticmethod
    def preparar_datos_reales_cuadrante(df):
        """Prepara los datos para el cuadrante de Gartner"""
        # Verificar que las columnas existen
        if 'IngresosUSD' not in df.columns:
            st.error("La columna 'IngresosUSD' no existe en los datos")
            return pd.DataFrame(), 0, 0, 0, 0
        
        if 'KilometrajeAcumulado' not in df.columns:
            st.error("La columna 'KilometrajeAcumulado' no existe en los datos")  
            return pd.DataFrame(), 0, 0, 0, 0
        
        # Convertir a float para evitar problemas con Decimal
        df['IngresosUSD'] = pd.to_numeric(df['IngresosUSD'], errors='coerce').fillna(0)
        df['KilometrajeAcumulado'] = pd.to_numeric(df['KilometrajeAcumulado'], errors='coerce').fillna(0)
        
        # Calcular límites dinámicos
        max_ventas = float(df['IngresosUSD'].max())
        max_km = float(df['KilometrajeAcumulado'].max())
        
        limite_ventas = max_ventas / 2  # Punto medio como límite
        limite_km = max_km / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_ventas = max_ventas + 100000
        limite_grafico_km = max_km + 100
        
        # Clasificar vendedores (usar el método correcto)
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_vendedorReal(  # Cambiado aquí
                row['IngresosUSD'], 
                row['KilometrajeAcumulado'], 
                limite_ventas, 
                limite_km
            ), axis=1
        ))
        
        # Renombrar la columna para consistencia con la vista
        df['TotalVendido'] = df['IngresosUSD']
        
        return df, limite_ventas, limite_km, limite_grafico_ventas, limite_grafico_km
    
    @staticmethod
    def preparar_cuadrante_visitas_movilidad(df):
        """Crea el cuadrante de Gartner con Plotly para visitas vs movilidad"""
        
        # Convertir a float para evitar problemas con Decimal
        df['TotalVisitas'] = pd.to_numeric(df['TotalVisitas'], errors='coerce')
        df['KilometrajeAcumulado'] = pd.to_numeric(df['KilometrajeAcumulado'], errors='coerce')
        
        # Calcular límites dinámicos
        max_visitas = float(df['TotalVisitas'].max())
        max_km = float(df['KilometrajeAcumulado'].max())
        
        limite_visitas = max_visitas / 2  # Punto medio como límite
        limite_km = max_km / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_visitas = max_visitas + (max_visitas * 0.1)  # 10% margen
        limite_grafico_km = max_km + (max_km * 0.1)  # 10% margen
        
        # Clasificar vendedores usando la función correcta
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_visita_movilidad(
                row['TotalVisitas'], 
                row['KilometrajeAcumulado'], 
                limite_visitas, 
                limite_km), 
                axis=1
        ))

        return df, limite_visitas, limite_km, limite_grafico_visitas, limite_grafico_km
    

    @staticmethod
    def preparar_cuadrante_visitas_generales_movilidad(df):
        """Crea el cuadrante de Gartner con Plotly para visitas vs movilidad"""
        
        # Convertir a float para evitar problemas con Decimal
        df['TotalVisitasGeneral'] = pd.to_numeric(df['TotalVisitasGeneral'], errors='coerce')
        df['KilometrajeAcumulado'] = pd.to_numeric(df['KilometrajeAcumulado'], errors='coerce')
        
        # Calcular límites dinámicos
        max_visitas = float(df['TotalVisitasGeneral'].max())
        max_km = float(df['KilometrajeAcumulado'].max())
        
        limite_visitas = max_visitas / 2  # Punto medio como límite
        limite_km = max_km / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_visitas = max_visitas + (max_visitas * 0.1)  # 10% margen
        limite_grafico_km = max_km + (max_km * 0.1)  # 10% margen
        
        # Clasificar vendedores usando la función correcta
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_visita_movilidad(
                row['TotalVisitasGeneral'], 
                row['KilometrajeAcumulado'], 
                limite_visitas, 
                limite_km), 
                axis=1
        ))

        return df, limite_visitas, limite_km, limite_grafico_visitas, limite_grafico_km
    
    
    @staticmethod
    def preparar_cuadrante_visita_ventas(df):
        """Crea el cuadrante de Gartner con Plotly"""
        
        # Convertir a float para evitar problemas con Decimal
        df['TotalVisitas'] = pd.to_numeric(df['TotalVisitas'], errors='coerce')
        df['TotalVendido'] = pd.to_numeric(df['TotalVendido'], errors='coerce')
        
        # Calcular límites dinámicos
        max_visitas = float(df['TotalVisitas'].max())
        max_ventas = float(df['TotalVendido'].max())
        
        limite_visitas = max_visitas / 2  # Punto medio como límite
        limite_ventas = max_ventas / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_visitas = max_visitas + (max_visitas * 0.1)  # 10% margen
        limite_grafico_ventas = max_ventas + (max_ventas * 0.1)  # 10% margen
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_visita_ventas(
                row['TotalVisitas'], 
                row['TotalVendido'], 
                limite_visitas, 
                limite_ventas), 
                axis=1
        ))

        return df, limite_visitas, limite_ventas, limite_grafico_visitas, limite_grafico_ventas
    
    @staticmethod
    def preparar_cuadrante_visita_ventasReales(df): #PENDIENTE
        """Crea el cuadrante de Gartner con Plotly"""
        
        # Convertir a float para evitar problemas con Decimal
        df['TotalVisitas'] = pd.to_numeric(df['TotalVisitas'], errors='coerce').fillna(0)
        df['IngresosUSD'] = pd.to_numeric(df['IngresosUSD'], errors='coerce').fillna(0)
        
        # Calcular límites dinámicos
        max_visitas = float(df['TotalVisitas'].max())
        max_ventas = float(df['IngresosUSD'].max())
        
        limite_visitas = max_visitas / 2  # Punto medio como límite
        limite_ventas = max_ventas / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_visitas = max_visitas + (max_visitas * 0.1)  # 10% margen
        limite_grafico_ventas = max_ventas + (max_ventas * 0.1)  # 10% margen
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_visita_ventas(
                row['TotalVisitas'], 
                row['IngresosUSD'], 
                limite_visitas, 
                limite_ventas), 
                axis=1
        ))

        # Renombrar la columna para consistencia con la vista
        df['TotalVendido'] = df['IngresosUSD']

        return df, limite_visitas, limite_ventas, limite_grafico_visitas, limite_grafico_ventas
    


    @staticmethod
    def crear_cuadrante_tareas_actividades(df):
        """Crea el cuadrante de Gartner con Plotly"""
        
        # Convertir a float para evitar problemas con Decimal
        df['TotalActividades'] = pd.to_numeric(df['TotalActividades'], errors='coerce')
        df['TotalTareas'] = pd.to_numeric(df['TotalTareas'], errors='coerce')
        
        # Calcular límites dinámicos
        max_actividades = float(df['TotalActividades'].max())
        max_tareas = float(df['TotalTareas'].max())
        
        limite_actividades = max_actividades / 2  # Punto medio como límite
        limite_tareas = max_tareas / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_actividades = max_actividades + (max_actividades * 0.1)  # 10% margen
        limite_grafico_tareas = max_tareas + (max_tareas * 0.1)  # 10% margen
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_tareas_actividades(
                row['TotalActividades'], 
                row['TotalTareas'], 
                limite_actividades, 
                limite_tareas), 
                axis=1
        ))

        return df, limite_actividades, limite_tareas, limite_grafico_actividades, limite_grafico_tareas
    
    @staticmethod
    def crear_cuadrante_actividades_movilidad(df):
        """Crea el cuadrante de Gartner con Plotly"""
        # Convertir a float para evitar problemas con Decimal
        df['TotalActividades'] = pd.to_numeric(df['TotalActividades'], errors='coerce')
        df['KilometrajeAcumulado'] = pd.to_numeric(df['KilometrajeAcumulado'], errors='coerce')
        
        # Calcular límites dinámicos
        max_actividades = float(df['TotalActividades'].max())
        max_km = float(df['KilometrajeAcumulado'].max())
        
        limite_actividades = max_actividades / 2  # Punto medio como límite
        limite_km = max_km / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_actividades = max_actividades + (max_actividades * 0.1)  # 10% margen
        limite_grafico_km = max_km + (max_km * 0.1)  # 10% margen
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_actividades_movilidad(
                row['TotalActividades'], 
                row['KilometrajeAcumulado'], 
                limite_actividades, 
                limite_km), 
                axis=1
        ))

        return df, limite_actividades, limite_km, limite_grafico_actividades, limite_grafico_km

    @staticmethod
    def crear_cuadrante_tiempos_visitas(df):
        """Crea el cuadrante de Gartner con Plotly"""

        # Convertir a float para evitar problemas con Decimal
        df['TotalVisitas'] = pd.to_numeric(df['TotalVisitas'], errors='coerce')
        df['TotalHoras'] = pd.to_numeric(df['TotalHoras'], errors='coerce')
        
        # Calcular límites dinámicos
        max_visitas = float(df['TotalVisitas'].max())
        max_horas = float(df['TotalHoras'].max())
        
        limite_visitas = max_visitas / 2  # Punto medio como límite
        limite_horas = max_horas / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_visitas = max_visitas + (max_visitas * 0.1)  # 10% margen
        limite_grafico_horas = max_horas + (max_horas * 0.1)  # 10% margen
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_tiempo_visitas(
                row['TotalVisitas'], 
                row['TotalHoras'], 
                limite_visitas, 
                limite_horas), 
                axis=1
        ))

        return df, limite_visitas, limite_horas, limite_grafico_visitas, limite_grafico_horas

    @staticmethod
    def crear_cuadrante_tiemposPromedio_visitas(df):
        """Crea el cuadrante de Gartner con Plotly"""

        # Convertir a float para evitar problemas con Decimal
        df['TotalVisitas'] = pd.to_numeric(df['TotalVisitas'], errors='coerce')
        df['PromedioHoras'] = pd.to_numeric(df['PromedioHoras'], errors='coerce')
        
        # Calcular límites dinámicos
        max_visitas = float(df['TotalVisitas'].max())
        max_horas = float(df['PromedioHoras'].max())
        
        limite_visitas = max_visitas / 2  # Punto medio como límite
        limite_horas = max_horas / 2  # Punto medio como límite
        
        # Límites del gráfico (con margen)
        limite_grafico_visitas = max_visitas + (max_visitas * 0.1)  # 10% margen
        limite_grafico_horas = max_horas + (max_horas * 0.1)  # 10% margen
        
        # Clasificar vendedores
        df['Cuadrante'], df['Descripcion'] = zip(*df.apply(
            lambda row: GartnerModelo.clasificar_tiempo_visitas(
                row['TotalVisitas'], 
                row['PromedioHoras'], 
                limite_visitas, 
                limite_horas), 
                axis=1
        ))

        return df, limite_visitas, limite_horas, limite_grafico_visitas, limite_grafico_horas