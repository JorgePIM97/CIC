# modelo/ventas_reales_modelo.py
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from .db_connection import DatabaseConnection

class VentasRealesModelo:
    def __init__(self):
        self.db = DatabaseConnection()
        
    """
    Consultas para obtener filtro de nombres y fechas 
    Se usa en modelo/vendedores_registrados.py
    """
    # Mantener todos los métodos existentes:
    def obtener_vendedores_ventas_reales(self):
        """
        Obtiene los representantes de ventas reales para filtro
        """
        query = """
        SELECT DISTINCT
            CASE 
                WHEN d.RepresentanteDeVentas LIKE 'Piso%' THEN 'Piso'
                ELSE d.RepresentanteDeVentas
            END AS RealRepSales
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas IS NOT NULL
        ORDER BY RealRepSales
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df['RealRepSales'].tolist()
        except Exception as e:
            st.error(f"Error al obtener vendedores: {str(e)}")
            return []
    
    def obtener_meses_años_disponibles(self, vendedor=None):
        """
        Obtiene los meses y años disponibles basado en Fecha de dev_Detalles
        Se usa en vista/componentes/sidebar_ventas_real.py
        """
        if vendedor and vendedor != "General":
            if vendedor == "Piso":
                where_clause = "WHERE d.RepresentanteDeVentas LIKE 'Piso%'"
            else:
                where_clause = f"WHERE d.RepresentanteDeVentas = '{vendedor}'"
        else:
            where_clause = ""
            
        query = f"""
        SELECT 
            YEAR(d.Fecha) AS Año,
            MONTH(d.Fecha) AS Mes
        FROM dev_Detalle_Corregida d
        {where_clause}
        GROUP BY YEAR(d.Fecha), MONTH(d.Fecha)
        ORDER BY Año DESC, Mes DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener meses y años: {str(e)}")
            return pd.DataFrame()







    """
    Consultas para obtener datos de los ingresos de las clases
    """
    def obtener_clases_ingresos_general(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene los ingresos por clase desde la base de datos (todos los vendedores)
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"WHERE d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.Clase,
            d.NumeroDeDocumento,
            SUM(d.IngresosUSD) as ingresos_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        {filtro_fecha}
        GROUP BY d.NumeroDeDocumento, d.Clase, d.Fecha
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos: {str(e)}")
            return pd.DataFrame()
        
    def obtener_clases_ingresos_vendedor(self, vendedor, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de clase para un representante de venta individual
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.Clase,
            d.NumeroDeDocumento,
            SUM(d.IngresosUSD) as ingresos_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas = '{vendedor}'
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.NumeroDeDocumento, d.Clase, d.Fecha
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos del vendedor: {str(e)}")
            return pd.DataFrame()

    def obtener_clases_ingresos_piso(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de clase cuando el representante de venta es piso
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
            
        query = f"""
        SELECT
            d.Clase,
            d.NumeroDeDocumento,
            SUM(d.IngresosUSD) as ingresos_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas LIKE 'Piso%' 
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.NumeroDeDocumento, d.Clase, d.Fecha
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos de piso: {str(e)}")
            return pd.DataFrame()
        
    
    """
    SUMATORIAS PARA TABLAS DE VENTAS CLASES***********************
    """
    def obtener_clases_ingresos_vendedor_sumatoria(self, vendedor, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de clase para un representante de venta individual
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.Clase,
            SUM(d.IngresosUSD) as ingresos_fact
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas = '{vendedor}'
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.Clase
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos del vendedor: {str(e)}")
            return pd.DataFrame()

    def obtener_clases_ingresos_piso_sumatoria(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de clase cuando el representante de venta es piso
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
            
        query = f"""
        SELECT
            d.Clase,
            SUM(d.IngresosUSD) as ingresos_fact
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas LIKE 'Piso%' 
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.Clase
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos de piso: {str(e)}")
            return pd.DataFrame()
        
    """
    *******************************************************
    """





    

    """
    Consultas para obtener datos de cantidad de las clases
    """
    def obtener_clases_cantidad_general(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene la cantidad por clase desde la base de datos (todos los vendedores)
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"WHERE d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.Clase,
            d.NumeroDeDocumento,
            SUM(d.CantidadVendida) as clases_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        GROUP BY d.NumeroDeDocumento, d.Clase, d.Fecha
        ORDER BY SUM(d.CantidadVendida) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos: {str(e)}")
            return pd.DataFrame()
        
    def obtener_clases_cantidad_vendedor(self, vendedor, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene cantidad de clase para un representante de venta individual
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.Clase,
            d.NumeroDeDocumento,
            SUM(d.CantidadVendida) as clases_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas = '{vendedor}'
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.NumeroDeDocumento, d.Clase, d.Fecha
        ORDER BY SUM(d.CantidadVendida) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos del vendedor: {str(e)}")
            return pd.DataFrame()

    def obtener_clases_cantidad_piso(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene cantidad de clase cuando el representante de venta es piso
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
            
        query = f"""
        SELECT
            d.Clase,
            d.NumeroDeDocumento,
            SUM(d.CantidadVendida) as clases_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas LIKE 'Piso%' 
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.NumeroDeDocumento, d.Clase, d.Fecha
        ORDER BY SUM(d.CantidadVendida) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos de piso: {str(e)}")
            return pd.DataFrame()
        
        
    """
    SUMATORIAS PARA TABLAS DE VENTAS CLASES CANTIDAD***********************
    """    
        
    def obtener_clases_cantidad_vendedor_sumatoria(self, vendedor, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene cantidad de clase para un representante de venta individual
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.Clase,
            SUM(d.CantidadVendida) as clases_fact
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas = '{vendedor}'
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.Clase
        ORDER BY SUM(d.CantidadVendida) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos del vendedor: {str(e)}")
            return pd.DataFrame()

    def obtener_clases_cantidad_piso_sumatoria(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene cantidad de clase cuando el representante de venta es piso
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
            
        query = f"""
        SELECT
            d.Clase,
            SUM(d.CantidadVendida) as clases_fact
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas LIKE 'Piso%' 
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.Clase
        ORDER BY SUM(d.CantidadVendida) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos de piso: {str(e)}")
            return pd.DataFrame()
    """
    *******************************************************
    """





    """
    Consultas para obtener datos de los ingresos de los clientes 
    """
    def obtener_clientes_ingresos_general(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene los ingresos por cliente desde la base de datos (todos los vendedores)
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"WHERE d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.NombreCliente,
            d.NumeroDeDocumento,
            SUM(d.IngresosUSD) as ingresos_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        {filtro_fecha}
        GROUP BY d.NumeroDeDocumento, d.NombreCliente, d.Fecha
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos: {str(e)}")
            return pd.DataFrame()
        
    def obtener_clientes_ingresos_vendedor(self, vendedor, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de cliente para un representante de venta individual
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.NombreCliente,
            d.NumeroDeDocumento,
            SUM(d.IngresosUSD) as ingresos_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas = '{vendedor}'
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.NumeroDeDocumento, d.NombreCliente, d.Fecha
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos del vendedor: {str(e)}")
            return pd.DataFrame()

    def obtener_clientes_ingresos_piso(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de cliente cuando el representante de venta es piso
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
            
        query = f"""
        SELECT
            d.NombreCliente,
            d.NumeroDeDocumento,
            SUM(d.IngresosUSD) as ingresos_fact,
            d.Fecha as FechaReal
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas LIKE 'Piso%' 
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.NumeroDeDocumento, d.NombreCliente, d.Fecha
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos de piso: {str(e)}")
            return pd.DataFrame()
        

    """
    SUMATORIAS PARA TABLAS DE VENTAS CLIENTES***********************
    """
    def obtener_clientes_ingresos_vendedor_sumatoria(self, vendedor, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de cliente para un representante de venta individual
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.NombreCliente,
            SUM(d.IngresosUSD) as ingresos_fact
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas = '{vendedor}'
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.NombreCliente
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos del vendedor: {str(e)}")
            return pd.DataFrame()

    def obtener_clientes_ingresos_piso_sumatoria(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de cliente cuando el representante de venta es piso
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
            
        query = f"""
        SELECT
            d.NombreCliente,
            SUM(d.IngresosUSD) as ingresos_fact
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas LIKE 'Piso%' 
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        {filtro_fecha}
        GROUP BY d.NombreCliente
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos de piso: {str(e)}")
            return pd.DataFrame()
        
    """
    *******************************************************
    """


    def obtener_categoria_ingresos_vendedor(self, vendedor, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene cantidad de clase para un representante de venta individual agrupado por categorías
        """
        # Aseguramos que las fechas estén en formato string correcto
        if fecha_inicio is None:
            fecha_inicio = "1900-01-01"
        if fecha_fin is None:
            fecha_fin = datetime.today().strftime("%Y-%m-%d")

        # Convertimos vendedor a string para SQL
        if isinstance(vendedor, list):
            vendedor_str = ",".join([f"'{v}'" for v in vendedor])
        else:
            vendedor_str = f"'{vendedor}'"

        query = f"""
        SELECT 
            RepresentanteDeVentas,


            CASE 
                WHEN Clase IN ('COMPONENTES DIRECTOS:BALEROS Y RODAMIENTOS',
                                'COMPONENTES DIRECTOS:ELECTRICO',
                                'HERRAMIENTA/HERRAMENTALES:HERRAMIENTA',
                                'REFACCIONES:COMPONENTES Y ACCSESORIOS'
                                ) 
                    THEN 'COMPONENTES'
                WHEN Clase IN ('CONSUMIBLES:MANUALES:PLASMA',
                                'CONSUMIBLES:MANUALES:PLASMA SYNC'
                                ) 
                    THEN 'CONSUMIBLES MANUALES'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:LASER' 
                    THEN 'CONSUMIBLES MECANIZADOS LASER'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:OXICORTE' 
                    THEN 'CONSUMIBLES MECANIZADOS OXICORTE'
                WHEN Clase IN ('CONSUMIBLES:MECANIZADOS:PLASMA', 
                                'CONSUMIBLES:MECANIZADOS:PLASMA SMART', 
                                'CONSUMIBLES:MECANIZADOS:PLASMA XPR') 
                    THEN 'CONSUMIBLES MECANIZADOS PLASMA'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:WATER'
                    THEN 'CONSUMIBLES MECANIZADOS WATER'
                WHEN Clase = 'MAQUINAS MECANIZADAS:MAQUINAS MECANIZADAS PLASMA'
                    THEN 'MAQUINAS MECANIZADAS'
                WHEN Clase IN ('CAPACITACION', 
                                'PAQUETERIAS COBRADAS AL CLIENTE', 
                                'SERVICIO TECNICO') 
                    THEN 'OTROS'
                WHEN Clase IN ('MAQUINAS MANUALES:MAQUINA MANUAL PLASMA',
                                'MAQUINAS MANUALES:MAQUINA MANUAL PLASMA SYNC')
                    THEN 'POWERMAX'
                WHEN Clase IN ('REFACCIONES:REFACCIONES LASER',
                                'REFACCIONES:REFACCIONES PLASMA',
                                'REFACCIONES:REFACCIONES PLASMA XPR',
                                'REFACCIONES:REFACCIONES PLASMA SYNC',
                                'REFACCIONES:REFACCIONES WATER',
                                'REFACCIONES:SOFTWARE') 
                    THEN 'REFACCIONES'
                WHEN Clase = 'SISTEMAS DE CORTE:SISTEMAS DE CORTE LASER'
                    THEN 'SISTEMAS DE CORTE LASER'
                WHEN Clase = 'SISTEMAS DE CORTE:SISTEMAS DE CORTE PLASMA'
                    THEN 'SISTEMAS DE CORTE PLASMA'


                ELSE 'No Categorizado'
            END AS Categoria,
            SUM(IngresosUSD) AS TotalIngresosUSD
        FROM vw_CategoriaIngresos
        WHERE FechaReal >= '{fecha_inicio}'
          AND FechaReal <= '{fecha_fin}'
          AND RepresentanteDeVentas IN ({vendedor_str})
        GROUP BY 
            RepresentanteDeVentas,


            CASE 
                WHEN Clase IN ('COMPONENTES DIRECTOS:BALEROS Y RODAMIENTOS',
                                'COMPONENTES DIRECTOS:ELECTRICO',
                                'HERRAMIENTA/HERRAMENTALES:HERRAMIENTA',
                                'REFACCIONES:COMPONENTES Y ACCSESORIOS'
                                ) 
                    THEN 'COMPONENTES'
                WHEN Clase IN ('CONSUMIBLES:MANUALES:PLASMA',
                                'CONSUMIBLES:MANUALES:PLASMA SYNC'
                                ) 
                    THEN 'CONSUMIBLES MANUALES'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:LASER' 
                    THEN 'CONSUMIBLES MECANIZADOS LASER'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:OXICORTE' 
                    THEN 'CONSUMIBLES MECANIZADOS OXICORTE'
                WHEN Clase IN ('CONSUMIBLES:MECANIZADOS:PLASMA', 
                                'CONSUMIBLES:MECANIZADOS:PLASMA SMART', 
                                'CONSUMIBLES:MECANIZADOS:PLASMA XPR') 
                    THEN 'CONSUMIBLES MECANIZADOS PLASMA'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:WATER'
                    THEN 'CONSUMIBLES MECANIZADOS WATER'
                WHEN Clase = 'MAQUINAS MECANIZADAS:MAQUINAS MECANIZADAS PLASMA'
                    THEN 'MAQUINAS MECANIZADAS'
                WHEN Clase IN ('CAPACITACION', 
                                'PAQUETERIAS COBRADAS AL CLIENTE', 
                                'SERVICIO TECNICO') 
                    THEN 'OTROS'
                WHEN Clase IN ('MAQUINAS MANUALES:MAQUINA MANUAL PLASMA',
                                'MAQUINAS MANUALES:MAQUINA MANUAL PLASMA SYNC')
                    THEN 'POWERMAX'
                WHEN Clase IN ('REFACCIONES:REFACCIONES LASER',
                                'REFACCIONES:REFACCIONES PLASMA',
                                'REFACCIONES:REFACCIONES PLASMA XPR',
                                'REFACCIONES:REFACCIONES PLASMA SYNC',
                                'REFACCIONES:REFACCIONES WATER',
                                'REFACCIONES:SOFTWARE') 
                    THEN 'REFACCIONES'
                WHEN Clase = 'SISTEMAS DE CORTE:SISTEMAS DE CORTE LASER'
                    THEN 'SISTEMAS DE CORTE LASER'
                WHEN Clase = 'SISTEMAS DE CORTE:SISTEMAS DE CORTE PLASMA'
                    THEN 'SISTEMAS DE CORTE PLASMA'


                ELSE 'No Categorizado'
            END
        ORDER BY RepresentanteDeVentas, Categoria;
        """
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos del vendedor: {str(e)}")
            return pd.DataFrame()

    def obtener_categoria_ingresos_piso(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene cantidad de clase cuando el representante de venta es piso agrupado por categorías
        """
        if fecha_inicio is None:
            fecha_inicio = "1900-01-01"
        if fecha_fin is None:
            fecha_fin = datetime.today().strftime("%Y-%m-%d")

        query = f"""
        SELECT 
            RepresentanteDeVentas,


            CASE 
                WHEN Clase IN ('COMPONENTES DIRECTOS:BALEROS Y RODAMIENTOS',
                                'COMPONENTES DIRECTOS:ELECTRICO',
                                'HERRAMIENTA/HERRAMENTALES:HERRAMIENTA',
                                'REFACCIONES:COMPONENTES Y ACCSESORIOS'
                                ) 
                    THEN 'COMPONENTES'
                WHEN Clase IN ('CONSUMIBLES:MANUALES:PLASMA',
                                'CONSUMIBLES:MANUALES:PLASMA SYNC'
                                ) 
                    THEN 'CONSUMIBLES MANUALES'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:LASER' 
                    THEN 'CONSUMIBLES MECANIZADOS LASER'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:OXICORTE' 
                    THEN 'CONSUMIBLES MECANIZADOS OXICORTE'
                WHEN Clase IN ('CONSUMIBLES:MECANIZADOS:PLASMA', 
                                'CONSUMIBLES:MECANIZADOS:PLASMA SMART', 
                                'CONSUMIBLES:MECANIZADOS:PLASMA XPR') 
                    THEN 'CONSUMIBLES MECANIZADOS PLASMA'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:WATER'
                    THEN 'CONSUMIBLES MECANIZADOS WATER'
                WHEN Clase = 'MAQUINAS MECANIZADAS:MAQUINAS MECANIZADAS PLASMA'
                    THEN 'MAQUINAS MECANIZADAS'
                WHEN Clase IN ('CAPACITACION', 
                                'PAQUETERIAS COBRADAS AL CLIENTE', 
                                'SERVICIO TECNICO') 
                    THEN 'OTROS'
                WHEN Clase IN ('MAQUINAS MANUALES:MAQUINA MANUAL PLASMA',
                                'MAQUINAS MANUALES:MAQUINA MANUAL PLASMA SYNC')
                    THEN 'POWERMAX'
                WHEN Clase IN ('REFACCIONES:REFACCIONES LASER',
                                'REFACCIONES:REFACCIONES PLASMA',
                                'REFACCIONES:REFACCIONES PLASMA XPR',
                                'REFACCIONES:REFACCIONES PLASMA SYNC',
                                'REFACCIONES:REFACCIONES WATER',
                                'REFACCIONES:SOFTWARE') 
                    THEN 'REFACCIONES'
                WHEN Clase = 'SISTEMAS DE CORTE:SISTEMAS DE CORTE LASER'
                    THEN 'SISTEMAS DE CORTE LASER'
                WHEN Clase = 'SISTEMAS DE CORTE:SISTEMAS DE CORTE PLASMA'
                    THEN 'SISTEMAS DE CORTE PLASMA'


                ELSE 'No Categorizado'
            END AS Categoria,
            SUM(IngresosUSD) AS TotalIngresosUSD
        FROM vw_CategoriaIngresos
        WHERE FechaReal >= '{fecha_inicio}'
          AND FechaReal <= '{fecha_fin}'
          AND RepresentanteDeVentas LIKE 'Piso%'
        GROUP BY 
            RepresentanteDeVentas,


            CASE 
                WHEN Clase IN ('COMPONENTES DIRECTOS:BALEROS Y RODAMIENTOS',
                                'COMPONENTES DIRECTOS:ELECTRICO',
                                'HERRAMIENTA/HERRAMENTALES:HERRAMIENTA',
                                'REFACCIONES:COMPONENTES Y ACCSESORIOS'
                                ) 
                    THEN 'COMPONENTES'
                WHEN Clase IN ('CONSUMIBLES:MANUALES:PLASMA',
                                'CONSUMIBLES:MANUALES:PLASMA SYNC'
                                ) 
                    THEN 'CONSUMIBLES MANUALES'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:LASER' 
                    THEN 'CONSUMIBLES MECANIZADOS LASER'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:OXICORTE' 
                    THEN 'CONSUMIBLES MECANIZADOS OXICORTE'
                WHEN Clase IN ('CONSUMIBLES:MECANIZADOS:PLASMA', 
                                'CONSUMIBLES:MECANIZADOS:PLASMA SMART', 
                                'CONSUMIBLES:MECANIZADOS:PLASMA XPR') 
                    THEN 'CONSUMIBLES MECANIZADOS PLASMA'
                WHEN Clase = 'CONSUMIBLES:MECANIZADOS:WATER'
                    THEN 'CONSUMIBLES MECANIZADOS WATER'
                WHEN Clase = 'MAQUINAS MECANIZADAS:MAQUINAS MECANIZADAS PLASMA'
                    THEN 'MAQUINAS MECANIZADAS'
                WHEN Clase IN ('CAPACITACION', 
                                'PAQUETERIAS COBRADAS AL CLIENTE', 
                                'SERVICIO TECNICO') 
                    THEN 'OTROS'
                WHEN Clase IN ('MAQUINAS MANUALES:MAQUINA MANUAL PLASMA',
                                'MAQUINAS MANUALES:MAQUINA MANUAL PLASMA SYNC')
                    THEN 'POWERMAX'
                WHEN Clase IN ('REFACCIONES:REFACCIONES LASER',
                                'REFACCIONES:REFACCIONES PLASMA',
                                'REFACCIONES:REFACCIONES PLASMA XPR',
                                'REFACCIONES:REFACCIONES PLASMA SYNC',
                                'REFACCIONES:REFACCIONES WATER',
                                'REFACCIONES:SOFTWARE') 
                    THEN 'REFACCIONES'
                WHEN Clase = 'SISTEMAS DE CORTE:SISTEMAS DE CORTE LASER'
                    THEN 'SISTEMAS DE CORTE LASER'
                WHEN Clase = 'SISTEMAS DE CORTE:SISTEMAS DE CORTE PLASMA'
                    THEN 'SISTEMAS DE CORTE PLASMA'


                ELSE 'No Categorizado'
            END
        ORDER BY RepresentanteDeVentas, Categoria;       
        """
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos de piso: {str(e)}")
            return pd.DataFrame()
        
    def obtener_coordinador_vendedor(self, vendedor):
        """
        Obtiene el coordinador de un vendedor específico
        """
        
        query = """
        SELECT dbo.fn_GetCoordinadorVendedorReporte(?) AS Coordinador;
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection(), params=[vendedor])
            return df
        except Exception as e:
            st.error(f"Error al obtener coordinador del vendedor: {str(e)}")
            return pd.DataFrame()
        

    # """
    # Consultas para obtener metas he ingresos anuales por vendedor
    # """
    # def obtener_ingresos_por_vendedor_reporte(self, vendedor, año):
    #     """
    #     Devuelve la suma de IngresosUSD de lo que va en el año filtrada por vendedor y año.
    #     """
    #     query = f"""
    #         SELECT SUM(IngresosUSD) AS total_ingresos
    #         FROM dev_Detalle_Corregida
    #         WHERE RepresentanteDeVentas = '{vendedor}'
    #         AND YEAR(Fecha) = {año}
    #     """
        
    #     try:
    #         df = pd.read_sql_query(query, self.db.get_connection())
    #         valor = df["total_ingresos"].iloc[0]
    #         return valor if pd.notna(valor) else 0
    #     except Exception as e:
    #         st.error(f"Error al obtener ingresos del vendedor {vendedor}: {str(e)}")
    #         return 0

    def obtener_ingresos_por_vendedor_reporte(self, vendedor, año, mes_nombre=None):
        """
        Devuelve la suma acumulada de IngresosUSD filtrada por vendedor y año.
        Si se proporciona mes_nombre, acumula desde Enero hasta ese mes inclusive.
        """
        try:
            meses_orden = {
                'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
                'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
                'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
            }

            if mes_nombre is not None:
                numero_mes = meses_orden.get(mes_nombre)
                if numero_mes is None:
                    st.error(f"Mes no válido: {mes_nombre}")
                    return 0
                mes_filtro = numero_mes
            else:
                mes_filtro = 12  # Sin filtro de mes → todo el año

            conn = self.db.get_connection()
            query = """
                SELECT SUM(IngresosUSD) AS total_ingresos
                FROM dev_Detalle_Corregida
                WHERE RepresentanteDeVentas = ?
                AND YEAR(Fecha) = ?
                AND MONTH(Fecha) <= ?
            """
            df = pd.read_sql_query(query, conn, params=[vendedor, año, mes_filtro])
            conn.close()

            valor = df["total_ingresos"].iloc[0]
            return float(valor) if pd.notna(valor) else 0

        except Exception as e:
            st.error(f"Error al obtener ingresos del vendedor {vendedor}: {str(e)}")
            return 0

    def obtener_meta_por_vendedor_reporte(self, vendedor, año):
        """
        Devuelve la suma de ValorMeta filtrada por vendedor y año.
        """
        query = f"""
            SELECT SUM(ValorMeta) AS total_meta
            FROM Metas
            WHERE NombreVendedor = '{vendedor}'
            AND YEAR(FechaRegistro) = {año}
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            valor = df["total_meta"].iloc[0]
            return valor if pd.notna(valor) else 0
        except Exception as e:
            st.error(f"Error al obtener la meta del vendedor {vendedor}: {str(e)}")
            return 0
        
    def obtener_meta_mes_por_vendedor_reporte(self, vendedor, mes, año):
        """
        Devuelve la suma de ValorMeta filtrada por vendedor y año.
        """
        query = f"""
            SELECT ValorMeta AS total_meta
            FROM Metas
            WHERE NombreVendedor = '{vendedor}'
            AND MesMeta = '{mes}'
            AND YearMeta = {año}
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            valor = df["total_meta"].iloc[0]
            return valor if pd.notna(valor) else 0
        except Exception as e:
            st.error(f"Error al obtener la meta del vendedor {vendedor}: {str(e)}")
            return 0


    """
    Consultas para obtener datos del total de ingresos de vendedores dada una fecha
    """        
    def obtener_total_ingresos_vendedor(self, vendedor, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de clase para un representante de venta individual
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        
        query = f"""
        SELECT
            d.RepresentanteDeVentas,
            SUM(d.IngresosUSD) as total_ingresos
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas = '{vendedor}'
        {filtro_fecha}
        GROUP BY d.RepresentanteDeVentas
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos del vendedor: {str(e)}")
            return pd.DataFrame()

    def obtener_total_ingresos_piso(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene ingresos de clase cuando el representante de venta es piso
        """
        # Construir filtros de fecha si se proporcionan
        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
            
        query = f"""
        SELECT
            d.RepresentanteDeVentas,
            SUM(d.IngresosUSD) as total_ingresos
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas LIKE 'Piso%' 
        {filtro_fecha}
        GROUP BY d.RepresentanteDeVentas
        ORDER BY SUM(d.IngresosUSD) DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener datos de piso: {str(e)}")
            return pd.DataFrame()
        

    # def obtener_total_meta_vendedores(
    #     self,
    #     vendedores,
    #     año,
    #     mes_inicio,
    #     mes_fin
    # ):
    #     """
    #     Obtiene la sumatoria de metas por vendedor en un rango de meses y año.
        
    #     vendedores : list[str]  -> ['Adan Garza', 'Jorge Martinez']
    #     año       : int        -> 2025
    #     mes_inicio : int        -> 6
    #     mes_fin    : int        -> 10
    #     """

    #     # Convertir lista de vendedores a formato SQL
    #     vendedores_sql = ", ".join([f"'{v}'" for v in vendedores])

    #     query = f"""
    #     SELECT
    #         NombreVendedor,
    #         ValorMeta,
    #         MesMeta
    #     FROM Metas
    #     WHERE NombreVendedor IN ({vendedores_sql})
    #     AND YEAR(FechaRegistro) = {año}
    #     AND CASE UPPER(MesMeta)
    #             WHEN 'ENERO' THEN 1
    #             WHEN 'FEBRERO' THEN 2
    #             WHEN 'MARZO' THEN 3
    #             WHEN 'ABRIL' THEN 4
    #             WHEN 'MAYO' THEN 5
    #             WHEN 'JUNIO' THEN 6
    #             WHEN 'JULIO' THEN 7
    #             WHEN 'AGOSTO' THEN 8
    #             WHEN 'SEPTIEMBRE' THEN 9
    #             WHEN 'OCTUBRE' THEN 10
    #             WHEN 'NOVIEMBRE' THEN 11
    #             WHEN 'DICIEMBRE' THEN 12
    #         END BETWEEN {mes_inicio} AND {mes_fin}
    #     """

    #     try:
    #         df = pd.read_sql_query(query, self.db.get_connection())
    #         return df
    #     except Exception as e:
    #         st.error(f"Error al obtener metas por vendedor: {str(e)}")
    #         return pd.DataFrame()
        
    def obtener_total_meta_vendedores(self, vendedores, año, mes_inicio, mes_fin):
        """
        Obtiene la sumatoria de metas por vendedor en un rango de meses y año.
        
        Args:
            vendedores : list[str]  -> ['Adan Garza', 'Jorge Martinez']
            año       : int        -> 2025
            mes_inicio : int        -> 6
            mes_fin    : int        -> 10
        
        Returns:
            DataFrame con columnas: NombreVendedor, ValorMeta, MesMeta
        """
        # Convertir lista de vendedores a formato SQL
        vendedores_sql = ", ".join([f"'{v}'" for v in vendedores])

        query = f"""
        SELECT
            NombreVendedor,
            ValorMeta,
            MesMeta
        FROM Metas
        WHERE NombreVendedor IN ({vendedores_sql})
        AND YEAR(FechaRegistro) = {año}
        AND CASE UPPER(MesMeta)
                WHEN 'ENERO' THEN 1
                WHEN 'FEBRERO' THEN 2
                WHEN 'MARZO' THEN 3
                WHEN 'ABRIL' THEN 4
                WHEN 'MAYO' THEN 5
                WHEN 'JUNIO' THEN 6
                WHEN 'JULIO' THEN 7
                WHEN 'AGOSTO' THEN 8
                WHEN 'SEPTIEMBRE' THEN 9
                WHEN 'OCTUBRE' THEN 10
                WHEN 'NOVIEMBRE' THEN 11
                WHEN 'DICIEMBRE' THEN 12
            END BETWEEN {mes_inicio} AND {mes_fin}
        """

        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener metas por vendedor: {str(e)}")
            return pd.DataFrame()

##############################

    def obtener_ingresos_mensuales_vendedor(self, vendedor, año, fecha_inicio=None, fecha_fin=None):
        """
        Devuelve ingresos agrupados por mes para un vendedor.
        Columns:
        RepresentanteDeVentas | Año | Mes | total_ingresos
        """

        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        else:
            # si no hay rango, usamos todo el año seleccionado
            filtro_fecha = f"AND YEAR(d.Fecha) = {año}"

        query = f"""
        SELECT
            d.RepresentanteDeVentas,
            YEAR(d.Fecha) as Año,
            MONTH(d.Fecha) as Mes,
            SUM(d.IngresosUSD) as total_ingresos
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas = '{vendedor}'
        {filtro_fecha}
        GROUP BY d.RepresentanteDeVentas, YEAR(d.Fecha), MONTH(d.Fecha)
        ORDER BY Año, Mes
        """

        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener ingresos mensuales del vendedor: {str(e)}")
            return pd.DataFrame()


    def obtener_ingresos_mensuales_piso(self, año, fecha_inicio=None, fecha_fin=None):
        """
        Devuelve ingresos agrupados por mes para todos los representantes Piso%.
        """

        filtro_fecha = ""
        if fecha_inicio and fecha_fin:
            filtro_fecha = f"AND d.Fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
        else:
            filtro_fecha = f"AND YEAR(d.Fecha) = {año}"

        query = f"""
        SELECT
            d.RepresentanteDeVentas,
            YEAR(d.Fecha) as Año,
            MONTH(d.Fecha) as Mes,
            SUM(d.IngresosUSD) as total_ingresos
        FROM dev_Detalle_Corregida d
        WHERE d.RepresentanteDeVentas LIKE 'Piso%'
        {filtro_fecha}
        GROUP BY d.RepresentanteDeVentas, YEAR(d.Fecha), MONTH(d.Fecha)
        ORDER BY Año, Mes
        """

        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener ingresos mensuales de piso: {str(e)}")
            return pd.DataFrame()

############################################

    def obtener_clientes_ingresos_vendedor_reporte(self, vendedor, mes_nombre, año):
        """
        Obtiene ingresos por cliente para un vendedor, mes y año específicos (para PDF)
        """
        meses = {
            'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
            'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
            'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
        }
        mes_num = meses.get(mes_nombre)
        if not mes_num:
            return pd.DataFrame()

        condicion_vendedor = (
            "d.RepresentanteDeVentas LIKE 'Piso%'"
            if vendedor == "Piso"
            else f"d.RepresentanteDeVentas = '{vendedor}'"
        )

        query = f"""
        SELECT
            d.NombreCliente,
            SUM(d.IngresosUSD) as ingresos_fact
        FROM dev_Detalle_Corregida d
        WHERE {condicion_vendedor}
        AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
        AND MONTH(d.Fecha) = {mes_num}
        AND YEAR(d.Fecha) = {año}
        GROUP BY d.NombreCliente
        ORDER BY SUM(d.IngresosUSD) DESC
        """

        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return df
        except Exception as e:
            st.error(f"Error al obtener clientes para reporte: {str(e)}")
            return pd.DataFrame()

