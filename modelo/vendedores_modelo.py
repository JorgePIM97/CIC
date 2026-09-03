# modelo/vendedores_modelo.py
import pandas as pd
import streamlit as st
from .db_connection import DatabaseConnection

class VendedoresModelo:
    def __init__(self):
        self.db = DatabaseConnection()
    
    '''Consulta de datos sql para cuadrante
    '''
    # @st.cache_data
    def obtener_ventas(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene las ventas por vendedor en el periodo especificado"""
        query = """
        SELECT 
            o.SalesRepId_Value,
            SUM(CAST(o.Total AS DECIMAL(18,2))) AS TotalVendido,
            COUNT(*) AS NumVentas
        FROM 
            Opportunities o
        WHERE 
            o.SalesRepId_Value IN ({})
            AND o.StatusId_Value = '7. Vendido'
            AND o.DateCreated BETWEEN ? AND ?
        GROUP BY 
            o.SalesRepId_Value
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepId_Value', 'TotalVendido', 'NumVentas'])
                
        except Exception as e:
            st.error(f"Error obteniendo ventas: {e}")
            return pd.DataFrame(columns=['SalesRepId_Value', 'TotalVendido', 'NumVentas'])

    """
    -- Declarar variables de fecha y del vendedor
    DECLARE @FechaInicio DATE = '2025-07-01';
    DECLARE @FechaFin DATE = '2025-07-02';
    DECLARE @SalesRepNombre NVARCHAR(200) = 'JORGE MARTINEZ ALANIS'; -- aquí ingresas dinámicamente el nombre completo

    SELECT 
        dc.RepresentanteDeVentas,
        dc.Id_Vendedor_FM,
        (us.Name + ' ' + us.LastName) AS SalesRepId_Value,
        us.Id,
        SUM(dc.IngresosUSD) AS IngresosUSD
    FROM dev_Detalle_Corregida dc
    JOIN Users us ON us.Id = dc.Id_Vendedor_FM
    WHERE 
        dc.Fecha BETWEEN @FechaInicio AND @FechaFin
        AND (us.Name + ' ' + us.LastName) = @SalesRepNombre
    GROUP BY 
        dc.RepresentanteDeVentas, 
        us.Id, 
        us.Name, 
        us.LastName, 
        dc.Id_Vendedor_FM;
    """


    # @st.cache_data
    def obtener_ventas_reales_cuadrante(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene las ventas por vendedor en el periodo especificado"""
        query = """
        SELECT 
            dc.RepresentanteDeVentas,
            dc.Id_Vendedor_FM,
            (us.Name + ' ' + us.LastName) AS SalesRepId_Value,
            us.Id,
            SUM(dc.IngresosUSD) AS IngresosUSD
        FROM dev_Detalle_Corregida dc
        JOIN Users us ON us.Id = dc.Id_Vendedor_FM
        WHERE 
            dc.Fecha BETWEEN ? AND ?
            AND (us.Name + ' ' + us.LastName) IN ({})
        GROUP BY 
            dc.RepresentanteDeVentas, 
            us.Id, 
            us.Name, 
            us.LastName, 
            dc.Id_Vendedor_FM;
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            # Corregir el orden de parámetros: primero fecha_inicio, fecha_fin, luego vendedores
            cursor.execute(query, [fecha_inicio, fecha_fin] + vendedores)
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepId_Value', 'Id', 'IngresosUSD'])
                
        except Exception as e:
            st.error(f"Error obteniendo ventas: {e}")
            return pd.DataFrame(columns=['SalesRepId_Value', 'Id', 'IngresosUSD'])


    
    # @st.cache_data
    def obtener_kilometraje(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene el kilometraje acumulado por vendedor"""
        query = """
        WITH ActividadesFiltradas AS (
            SELECT 
                a.Id,
                a.SalesRepId_Value,
                a.[Date],
                a.Latitude,
                a.Longitude
            FROM 
                Activities a
            WHERE 
                a.SalesRepId_Value IN ({})
                AND a.[Date] BETWEEN ? AND ?
                AND a.Latitude IS NOT NULL AND a.Longitude IS NOT NULL
                AND a.Checkin = 1
                AND ISNUMERIC(a.Latitude) = 1 AND ISNUMERIC(a.Longitude) = 1
        ),
        ActividadesOrdenadas AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (PARTITION BY SalesRepId_Value ORDER BY [Date]) AS Orden
            FROM 
                ActividadesFiltradas
        ),
        ParesCoordenadas AS (
            SELECT 
                a1.SalesRepId_Value,
                a1.Latitude AS LatActual,
                a1.Longitude AS LonActual,
                a2.Latitude AS LatAnterior,
                a2.Longitude AS LonAnterior
            FROM 
                ActividadesOrdenadas a1
            LEFT JOIN 
                ActividadesOrdenadas a2 ON a1.SalesRepId_Value = a2.SalesRepId_Value 
                                       AND a1.Orden = a2.Orden + 1
        ),
        CalculoDistancias AS (
            SELECT 
                SalesRepId_Value,
                CASE
                    WHEN LatAnterior IS NULL THEN 0
                    ELSE 6371 * 2 * ASIN(
                        SQRT(
                            POWER(SIN((RADIANS(TRY_CAST(LatActual AS FLOAT)) - RADIANS(TRY_CAST(LatAnterior AS FLOAT)))/2), 2) +
                            COS(RADIANS(TRY_CAST(LatAnterior AS FLOAT))) * 
                            COS(RADIANS(TRY_CAST(LatActual AS FLOAT))) *
                            POWER(SIN((RADIANS(TRY_CAST(LonActual AS FLOAT)) - RADIANS(TRY_CAST(LonAnterior AS FLOAT)))/2), 2)
                        )
                    )
                END AS DistanciaKM
            FROM 
                ParesCoordenadas
        )
        SELECT 
            SalesRepId_Value,
            ROUND(SUM(DistanciaKM), 2) AS KilometrajeAcumulado,
            COUNT(*) AS NumCalculos
        FROM 
            CalculoDistancias
        GROUP BY 
            SalesRepId_Value
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepId_Value', 'KilometrajeAcumulado', 'NumCalculos'])
                
        except Exception as e:
            st.error(f"Error obteniendo kilometraje: {e}")
            return pd.DataFrame(columns=['SalesRepId_Value', 'KilometrajeAcumulado', 'NumCalculos'])
        
    # @st.cache_data
    def obtener_kilometraje_gps(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene el kilometraje acumulado por vendedor desde la tabla MovilidadRegistro"""
        query = """
            SELECT 
                Vendedor,
                SUM(CAST(Kilometros AS DECIMAL(18,2))) AS KilometrajeAcumulado,
                COUNT(*) AS NumRegistros
            FROM 
                MovilidadRegistro
            WHERE 
                Vendedor IN ({})
                AND Fecha_Movilidad BETWEEN ? AND ?
            GROUP BY 
                Vendedor
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                # Renombrar columna para que coincida con el merge
                df = df.rename(columns={'Vendedor': 'SalesRepId_Value'})
                return df
            else:
                return pd.DataFrame(columns=['SalesRepId_Value', 'KilometrajeAcumulado', 'NumRegistros'])
                
        except Exception as e:
            st.error(f"Error obteniendo kilometraje: {e}")
            return pd.DataFrame(columns=['SalesRepId_Value', 'KilometrajeAcumulado', 'NumRegistros'])
        
        
    # @st.cache_data
    def obtener_visitas(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene el total de visitas por vendedor en el periodo especificado"""
        query = """
        SELECT 
            SalesRepId_Value,
            COUNT(*) AS TotalVisitas
        FROM 
            Activities
        WHERE 
            TypeId_Value = 'Visita'
            AND SalesRepId_Value IN ({})
            AND Checkin = 1
            AND DateCreated >= ?
            AND DateCreated < DATEADD(DAY, 1, ?)
        GROUP BY 
            SalesRepId_Value
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepId_Value', 'TotalVisitas'])
                
        except Exception as e:
            st.error(f"Error obteniendo visitas ss: {e}")
            return pd.DataFrame(columns=['SalesRepId_Value', 'TotalVisitas'])
        
    # @st.cache_data
    def obtener_visitas_general(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene el total de visitas por vendedor en el periodo especificado"""
        query = """
        SELECT 
            SalesRepId_Value,
            COUNT(*) AS TotalVisitasGeneral
        FROM 
            Activities
        WHERE 
            SalesRepId_Value IN ({})
            AND Checkin = 1
            AND DateCreated >= ?
            AND DateCreated < DATEADD(DAY, 1, ?)
        GROUP BY 
            SalesRepId_Value
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepId_Value', 'TotalVisitasGeneral'])
                
        except Exception as e:
            st.error(f"Error obteniendo visitas ss: {e}")
            return pd.DataFrame(columns=['SalesRepId_Value', 'TotalVisitasGeneral'])
    
    # @st.cache_data
    def obtener_tareas(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene el total de tareas por vendedor en el periodo especificado"""
        query = """
        SELECT 
            SalesRepId_Value,
            COUNT(*) AS TotalTareas
        FROM 
            Calendars
        WHERE 
            SalesRepId_Value IN ({})
            AND DateCreated >= ?
            AND DateCreated < DATEADD(DAY, 1, ?)
        GROUP BY 
            SalesRepId_Value
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepId_Value', 'TotalTareas'])
                
        except Exception as e:
            st.error(f"Error obteniendo tareas: {e}")
            return pd.DataFrame(columns=['SalesRepId_Value', 'TotalTareas'])

    # @st.cache_data
    def obtener_actividades(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene el total de actividades por vendedor en el periodo especificado"""
        query = """
        SELECT 
            SalesRepId_Value,
            COUNT(*) AS TotalActividades
        FROM 
            Activities
        WHERE 
            SalesRepId_Value IN ({})
            AND Checkin = 1
            AND DateCreated >= ?
            AND DateCreated < DATEADD(DAY, 1, ?)
        GROUP BY 
            SalesRepId_Value
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepId_Value', 'TotalActividades'])
                
        except Exception as e:
            st.error(f"Error obteniendo actividades: {e}")
            return pd.DataFrame(columns=['SalesRepId_Value', 'TotalActividades'])
        
    # @st.cache_data
    def obtener_tiempo_visitas(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene el tiempo total en visitas presenciales por vendedor"""
        query = """
        SELECT 
            o.SalesRepName,
            SUM(ISNULL(CAST(o.EstVisitTimeHrs AS DECIMAL(18,2)), 0)) AS TotalHoras
        FROM 
            dbo.vw_Activities o
        WHERE 
            o.SalesRepName IN ({})
            AND o.TypeName = 'Visita'
            AND o.Date >= ?
            AND o.Date <= ?
            AND o.EstVisitTimeHrs IS NOT NULL
            AND o.EstVisitTimeHrs >= 0
        GROUP BY 
            o.SalesRepName
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepName', 'TotalHoras'])
                
        except Exception as e:
            st.error(f"Error obteniendo tiempo de visitas: {e}")
            return pd.DataFrame(columns=['SalesRepName', 'TotalHoras'])
        
    # @st.cache_data
    def obtener_tiempo_promedio_visitas(_self, fecha_inicio, fecha_fin, vendedores):
        """Obtiene el tiempo total en visitas presenciales por vendedor"""
        query = """
        SELECT 
            o.SalesRepName,
            AVG(ISNULL(CAST(o.EstVisitTimeHrs AS DECIMAL(18,2)), 0)) AS PromedioHoras
        FROM 
            dbo.vw_Activities o
        WHERE 
            o.SalesRepName IN ({})
            AND o.TypeName = 'Visita'
            AND o.Date >= ?
            AND o.Date <= ?
            AND o.EstVisitTimeHrs IS NOT NULL
            AND o.EstVisitTimeHrs >= 0
        GROUP BY 
            o.SalesRepName
        """.format(','.join(['?' for _ in vendedores]))
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedores + [fecha_inicio, fecha_fin])
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                return pd.DataFrame(columns=['SalesRepName', 'PromedioHoras'])
                
        except Exception as e:
            st.error(f"Error obteniendo tiempo de visitas: {e}")
            return pd.DataFrame(columns=['SalesRepName', 'PromedioHoras'])
            

    '''Obtener datos de las consultas sql
    '''
    def obtener_datos_ventasReales_gps(self, fecha_inicio_ventas, fecha_fin_ventas, fecha_inicio_kms, fecha_fin_kms, vendedores):
        """Combina datos de ventas reales y kilometraje"""
        
        # Obtener datos
        df_ventas = self.obtener_ventas_reales_cuadrante(fecha_inicio_ventas, fecha_fin_ventas, vendedores)
        df_kilometraje = self.obtener_kilometraje_gps(fecha_inicio_kms, fecha_fin_kms, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con ventas
        if not df_ventas.empty:
            df_resultado = df_base.merge(
                df_ventas[['SalesRepId_Value', 'IngresosUSD']], 
                on='SalesRepId_Value', 
                how='left'
            )
        else:
            df_resultado = df_base.copy()
            df_resultado['IngresosUSD'] = 0
        
        # Hacer merge con kilometraje
        if not df_kilometraje.empty:
            df_resultado = df_resultado.merge(
                df_kilometraje[['SalesRepId_Value', 'KilometrajeAcumulado']], 
                on='SalesRepId_Value', 
                how='left'
            )
        else:
            df_resultado['KilometrajeAcumulado'] = 0
        
        # Rellenar valores nulos y convertir a float
        df_resultado['IngresosUSD'] = pd.to_numeric(df_resultado['IngresosUSD'].fillna(0), errors='coerce')
        df_resultado['KilometrajeAcumulado'] = pd.to_numeric(df_resultado['KilometrajeAcumulado'].fillna(0), errors='coerce')
        
        # Agregar columna con el nombre del vendedor
        df_resultado['SalesRepName'] = df_resultado['SalesRepId_Value']
        
        return df_resultado

    #obtener_ventas_movilidad
    def obtener_datos_completos(self, fecha_inicio_ventas, fecha_fin_ventas, fecha_inicio_kms, fecha_fin_kms, vendedores):
        """Combina datos de ventas y kilometraje"""
        
        # Obtener datos
        df_ventas = self.obtener_ventas(fecha_inicio_ventas, fecha_fin_ventas, vendedores)
        df_kilometraje = self.obtener_kilometraje(fecha_inicio_kms, fecha_fin_kms, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con ventas
        df_resultado = df_base.merge(
            df_ventas[['SalesRepId_Value', 'TotalVendido', 'NumVentas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con kilometraje
        df_resultado = df_resultado.merge(
            df_kilometraje[['SalesRepId_Value', 'KilometrajeAcumulado']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalVendido'] = pd.to_numeric(df_resultado['TotalVendido'].fillna(0), errors='coerce')
        df_resultado['NumVentas'] = pd.to_numeric(df_resultado['NumVentas'].fillna(0), errors='coerce')
        df_resultado['KilometrajeAcumulado'] = pd.to_numeric(df_resultado['KilometrajeAcumulado'].fillna(0), errors='coerce')
        
        return df_resultado
    
    def obtener_datos_ventasForce_gps(self, fecha_inicio_ventas, fecha_fin_ventas, fecha_inicio_kms, fecha_fin_kms, vendedores):
        """Combina datos de ventas y kilometraje"""
        
        # Obtener datos
        df_ventas = self.obtener_ventas(fecha_inicio_ventas, fecha_fin_ventas, vendedores)
        df_kilometraje = self.obtener_kilometraje_gps(fecha_inicio_kms, fecha_fin_kms, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con ventas
        df_resultado = df_base.merge(
            df_ventas[['SalesRepId_Value', 'TotalVendido', 'NumVentas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con kilometraje
        df_resultado = df_resultado.merge(
            df_kilometraje[['SalesRepId_Value', 'KilometrajeAcumulado']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalVendido'] = pd.to_numeric(df_resultado['TotalVendido'].fillna(0), errors='coerce')
        df_resultado['NumVentas'] = pd.to_numeric(df_resultado['NumVentas'].fillna(0), errors='coerce')
        df_resultado['KilometrajeAcumulado'] = pd.to_numeric(df_resultado['KilometrajeAcumulado'].fillna(0), errors='coerce')
        
        # Agregar columna con el nombre del vendedor
        df_resultado['SalesRepName'] = df_resultado['SalesRepId_Value']
        
        return df_resultado
    
    def obtener_datos_reales_completos(self, fecha_inicio_ventas, fecha_fin_ventas, fecha_inicio_km, fecha_fin_km, vendedores):
        """Obtiene datos completos combinando ventas y kilometraje"""

        # Obtener datos
        df_ventas = self.obtener_ventas_reales_cuadrante(fecha_inicio_ventas, fecha_fin_ventas, vendedores) 
        df_km = self.obtener_kilometraje(fecha_inicio_km, fecha_fin_km, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})

        # Hacer merge con ventas
        df_resultado = df_base.merge(
            df_ventas[['SalesRepId_Value', 'IngresosUSD']], 
            on='SalesRepId_Value', 
            how='left'
        )

        # Hacer merge con kilometraje
        df_resultado = df_resultado.merge(
            df_km[['SalesRepId_Value', 'KilometrajeAcumulado']], 
            on='SalesRepId_Value', 
            how='left'
        )

        df_resultado['IngresosUSD'] = pd.to_numeric(df_resultado['IngresosUSD'].fillna(0), errors='coerce')
        df_resultado['KilometrajeAcumulado'] = pd.to_numeric(df_resultado['KilometrajeAcumulado'].fillna(0), errors='coerce')
        
        return df_resultado
    

    def obtener_visita_movilidad(self, fecha_inicio_visitas, fecha_fin_visitas, fecha_inicio_kms, fecha_fin_kms, vendedores):
        """Combina datos de visitas y kilometraje"""
        
        # Obtener datos
        df_visitas = self.obtener_visitas(fecha_inicio_visitas, fecha_fin_visitas, vendedores)
        df_kilometraje = self.obtener_kilometraje(fecha_inicio_kms, fecha_fin_kms, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con visitas
        df_resultado = df_base.merge(
            df_visitas[['SalesRepId_Value', 'TotalVisitas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con kilometraje
        df_resultado = df_resultado.merge(
            df_kilometraje[['SalesRepId_Value', 'KilometrajeAcumulado']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalVisitas'] = pd.to_numeric(df_resultado['TotalVisitas'].fillna(0), errors='coerce')
        df_resultado['KilometrajeAcumulado'] = pd.to_numeric(df_resultado['KilometrajeAcumulado'].fillna(0), errors='coerce')
        
        return df_resultado
    

    def obtener_visitaGeneral_movilidad(self, fecha_inicio_visitas, fecha_fin_visitas, fecha_inicio_kms, fecha_fin_kms, vendedores):
        """Combina datos de visitas y kilometraje"""
        
        # Obtener datos
        df_visitas = self.obtener_visitas_general(fecha_inicio_visitas, fecha_fin_visitas, vendedores)
        df_kilometraje = self.obtener_kilometraje(fecha_inicio_kms, fecha_fin_kms, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con visitas
        df_resultado = df_base.merge(
            df_visitas[['SalesRepId_Value', 'TotalVisitasGeneral']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con kilometraje
        df_resultado = df_resultado.merge(
            df_kilometraje[['SalesRepId_Value', 'KilometrajeAcumulado']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalVisitasGeneral'] = pd.to_numeric(df_resultado['TotalVisitasGeneral'].fillna(0), errors='coerce')
        df_resultado['KilometrajeAcumulado'] = pd.to_numeric(df_resultado['KilometrajeAcumulado'].fillna(0), errors='coerce')
        
        return df_resultado
    
    
    def obtener_visita_ventas(self, fecha_inicio_visitas, fecha_fin_visitas, fecha_inicio_ventas, fecha_fin_ventas, vendedores):
        """Combina datos de visitas y ventas"""
        
        # Obtener datos
        df_visitas = self.obtener_visitas(fecha_inicio_visitas, fecha_fin_visitas, vendedores)
        df_ventas = self.obtener_ventas(fecha_inicio_ventas, fecha_fin_ventas, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con visitas
        df_resultado = df_base.merge(
            df_visitas[['SalesRepId_Value', 'TotalVisitas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con ventas
        df_resultado = df_resultado.merge(
            df_ventas[['SalesRepId_Value', 'TotalVendido', 'NumVentas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalVisitas'] = pd.to_numeric(df_resultado['TotalVisitas'].fillna(0), errors='coerce')
        df_resultado['TotalVendido'] = pd.to_numeric(df_resultado['TotalVendido'].fillna(0), errors='coerce')
        df_resultado['NumVentas'] = pd.to_numeric(df_resultado['NumVentas'].fillna(0), errors='coerce')
        
        return df_resultado
    
    def obtener_visita_ventasReales(self, fecha_inicio_visitas, fecha_fin_visitas, fecha_inicio_ventas, fecha_fin_ventas, vendedores):
        """Combina datos de visitas y ventas reales"""
        
        # Obtener datos
        df_visitas = self.obtener_visitas(fecha_inicio_visitas, fecha_fin_visitas, vendedores)
        df_ventasReales = self.obtener_ventas_reales_cuadrante(fecha_inicio_ventas, fecha_fin_ventas, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con visitas
        df_resultado = df_base.merge(
            df_visitas[['SalesRepId_Value', 'TotalVisitas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con ventas
        df_resultado = df_resultado.merge(
            df_ventasReales[['SalesRepId_Value', 'IngresosUSD']], 
            on='SalesRepId_Value', 
            how='left'
        )
        

        # Rellenar valores nulos y convertir a float
        df_resultado['TotalVisitas'] = pd.to_numeric(df_resultado['TotalVisitas'].fillna(0), errors='coerce')
        df_resultado['IngresosUSD'] = pd.to_numeric(df_resultado['IngresosUSD'].fillna(0), errors='coerce')
        
        
        return df_resultado
    

    def obtener_tareas_actividades(self, fecha_inicio_actividades, fecha_fin_actividades, fecha_inicio_tareas, fecha_fin_tareas, vendedores):
        """Combina datos de actividades y tareas"""
    
        # Obtener datos
        df_actividades = self.obtener_actividades(fecha_inicio_actividades, fecha_fin_actividades, vendedores)
        df_tareas = self.obtener_tareas(fecha_inicio_tareas, fecha_fin_tareas, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con actividades
        df_resultado = df_base.merge(
            df_actividades[['SalesRepId_Value', 'TotalActividades']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con tareas
        df_resultado = df_resultado.merge(
            df_tareas[['SalesRepId_Value', 'TotalTareas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalActividades'] = pd.to_numeric(df_resultado['TotalActividades'].fillna(0), errors='coerce')
        df_resultado['TotalTareas'] = pd.to_numeric(df_resultado['TotalTareas'].fillna(0), errors='coerce')
        
        return df_resultado
    
    def obtener_actividades_movilidad(self, fecha_inicio_actividades, fecha_fin_actividades, fecha_inicio_kms, fecha_fin_kms, vendedores):
        """Combina datos de actividades y kilometraje"""
    
        # Obtener datos
        df_actividades = self.obtener_actividades(fecha_inicio_actividades, fecha_fin_actividades, vendedores)
        df_kilometraje = self.obtener_kilometraje(fecha_inicio_kms, fecha_fin_kms, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con actividades
        df_resultado = df_base.merge(
            df_actividades[['SalesRepId_Value', 'TotalActividades']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con kilometraje
        df_resultado = df_resultado.merge(
            df_kilometraje[['SalesRepId_Value', 'KilometrajeAcumulado']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalActividades'] = pd.to_numeric(df_resultado['TotalActividades'].fillna(0), errors='coerce')
        df_resultado['KilometrajeAcumulado'] = pd.to_numeric(df_resultado['KilometrajeAcumulado'].fillna(0), errors='coerce')
        
        return df_resultado
    
    def obtener_tiemposVisita_visitas(self, fecha_inicio_visitas, fecha_fin_visitas, fecha_inicio_tiempo, fecha_fin_tiempo, vendedores):
        """Combina datos de visitas y tiempo de visitas"""
        
        # Obtener datos
        df_visitas = self.obtener_visitas(fecha_inicio_visitas, fecha_fin_visitas, vendedores)
        df_tiempo = self.obtener_tiempo_visitas(fecha_inicio_tiempo, fecha_fin_tiempo, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con visitas
        df_resultado = df_base.merge(
            df_visitas[['SalesRepId_Value', 'TotalVisitas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con tiempo
        df_resultado = df_resultado.merge(
            df_tiempo[['SalesRepName', 'TotalHoras']], 
            left_on='SalesRepId_Value',
            right_on='SalesRepName',
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalVisitas'] = pd.to_numeric(df_resultado['TotalVisitas'].fillna(0), errors='coerce')
        df_resultado['TotalHoras'] = pd.to_numeric(df_resultado['TotalHoras'].fillna(0), errors='coerce')
        
        return df_resultado

    def obtener_tiemposVisitaPromedio_visitas(self, fecha_inicio_visitas, fecha_fin_visitas, fecha_inicio_tiempo, fecha_fin_tiempo, vendedores):
        """Combina datos de visitas y tiempo de visitas"""
        
        # Obtener datos
        df_visitas = self.obtener_visitas(fecha_inicio_visitas, fecha_fin_visitas, vendedores)
        df_tiempo = self.obtener_tiempo_promedio_visitas(fecha_inicio_tiempo, fecha_fin_tiempo, vendedores)
        
        # Crear DataFrame base con todos los vendedores
        df_base = pd.DataFrame({'SalesRepId_Value': vendedores})
        
        # Hacer merge con visitas
        df_resultado = df_base.merge(
            df_visitas[['SalesRepId_Value', 'TotalVisitas']], 
            on='SalesRepId_Value', 
            how='left'
        )
        
        # Hacer merge con tiempo
        df_resultado = df_resultado.merge(
            df_tiempo[['SalesRepName', 'PromedioHoras']], 
            left_on='SalesRepId_Value',
            right_on='SalesRepName',
            how='left'
        )
        
        # Rellenar valores nulos y convertir a float
        df_resultado['TotalVisitas'] = pd.to_numeric(df_resultado['TotalVisitas'].fillna(0), errors='coerce')
        df_resultado['PromedioHoras'] = pd.to_numeric(df_resultado['PromedioHoras'].fillna(0), errors='coerce')
        
        return df_resultado




