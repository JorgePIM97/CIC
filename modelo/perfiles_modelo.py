# modelo/perfiles_modelo.py - MODIFICADO
import pandas as pd
import streamlit as st
import calendar
from datetime import datetime
from .db_connection import DatabaseConnection

class PerfilesModelo:
    def __init__(self):
        self.db = DatabaseConnection()
    
    @st.cache_data
    def obtener_ventas_mensuales_por_rango(_self, vendedor, fecha_inicio, fecha_fin):
        """Obtiene las ventas mensuales por vendedor para el rango de fechas especificado"""
        query = """
        SELECT 
            YEAR(o.DateCreated) AS Año,
            MONTH(o.DateCreated) AS Mes,
            SUM(CAST(o.Total AS DECIMAL(18,2))) AS TotalVendido,
            COUNT(*) AS NumVentas
        FROM 
            Opportunities o
        WHERE 
            o.SalesRepId_Value = ?
            AND o.StatusId_Value = '7. Vendido'
            AND o.DateCreated >= ?
            AND o.DateCreated <= ?
        GROUP BY 
            YEAR(o.DateCreated), MONTH(o.DateCreated)
        ORDER BY 
            Año, Mes
        """
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            # Convertir fechas a string formato SQL
            fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
            fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
            params = [vendedor, fecha_inicio_str, fecha_fin_str]
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                # Agregar nombre del mes
                df['NombreMes'] = df['Mes'].apply(lambda x: calendar.month_name[x])
                return df
            else:
                return pd.DataFrame(columns=['Año', 'Mes', 'TotalVendido', 'NumVentas', 'NombreMes'])
                
        except Exception as e:
            st.error(f"Error obteniendo ventas mensuales: {e}")
            return pd.DataFrame(columns=['Año', 'Mes', 'TotalVendido', 'NumVentas', 'NombreMes'])

    @st.cache_data
    def obtener_cotizaciones_mensuales_por_rango(_self, vendedor, fecha_inicio, fecha_fin):
        """Obtiene las cotizaciones mensuales por vendedor para el rango de fechas especificado"""
        query = """
        SELECT 
            YEAR(o.DateCreated) AS Año,
            MONTH(o.DateCreated) AS Mes,
            SUM(CAST(o.Total AS DECIMAL(18,2))) AS TotalCotizado,
            COUNT(*) AS NumVentas
        FROM 
            Opportunities o
        WHERE 
            o.SalesRepId_Value = ?
            AND o.StatusId_Value = '4. Cotización Presentada'
            AND o.DateCreated >= ?
            AND o.DateCreated <= ?
        GROUP BY 
            YEAR(o.DateCreated), MONTH(o.DateCreated)
        ORDER BY 
            Año, Mes
        """
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
            fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
            params = [vendedor, fecha_inicio_str, fecha_fin_str]
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                df['NombreMes'] = df['Mes'].apply(lambda x: calendar.month_name[x])
                return df
            else:
                return pd.DataFrame(columns=['Año', 'Mes', 'TotalCotizado', 'NumVentas', 'NombreMes'])
                
        except Exception as e:
            st.error(f"Error obteniendo cotizaciones mensuales: {e}")
            return pd.DataFrame(columns=['Año', 'Mes', 'TotalCotizado', 'NumVentas', 'NombreMes'])

    @st.cache_data
    def obtener_rango_fechas_disponibles(_self):
        """Obtiene el rango de fechas disponibles en la base de datos"""
        query = """
        SELECT 
            MIN(DateCreated) as FechaMinima,
            MAX(DateCreated) as FechaMaxima
        FROM Opportunities
        WHERE StatusId_Value IN ('7. Vendido', '4. Cotización Presentada')
        """
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            if row and row[0] and row[1]:
                return row[0].date(), row[1].date()
            else:
                # Si no hay datos, devolver un rango por defecto
                from datetime import date
                return date(2020, 1, 1), date.today()
        except Exception as e:
            st.error(f"Error obteniendo rango de fechas: {e}")
            from datetime import date
            return date(2020, 1, 1), date.today()

    # Mantener métodos originales para compatibilidad
    @st.cache_data
    def obtener_ventas_mensuales(_self, vendedor, años):
        """Obtiene las ventas mensuales por vendedor para los años especificados (método original)"""
        años_str = ','.join(['?' for _ in años])
        query = f"""
        SELECT 
            YEAR(o.DateCreated) AS Año,
            MONTH(o.DateCreated) AS Mes,
            SUM(CAST(o.Total AS DECIMAL(18,2))) AS TotalVendido,
            COUNT(*) AS NumVentas
        FROM 
            Opportunities o
        WHERE 
            o.SalesRepId_Value = ?
            AND o.StatusId_Value = '7. Vendido'
            AND YEAR(o.DateCreated) IN ({años_str})
        GROUP BY 
            YEAR(o.DateCreated), MONTH(o.DateCreated)
        ORDER BY 
            Año, Mes
        """
        
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            params = [vendedor] + años
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                df['NombreMes'] = df['Mes'].apply(lambda x: calendar.month_name[x])
                return df
            else:
                return pd.DataFrame(columns=['Año', 'Mes', 'TotalVendido', 'NumVentas', 'NombreMes'])
                
        except Exception as e:
            st.error(f"Error obteniendo ventas mensuales: {e}")
            return pd.DataFrame(columns=['Año', 'Mes', 'TotalVendido', 'NumVentas', 'NombreMes'])

    @st.cache_data
    def obtener_años_disponibles(_self):
        """Obtiene los años disponibles en la base de datos"""
        query = """
        SELECT DISTINCT YEAR(DateCreated) AS Año
        FROM Opportunities
        WHERE StatusId_Value = '7. Vendido'
        ORDER BY Año DESC
        """
        try:
            conn = _self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            st.error(f"Error obteniendo años: {e}")
            return []
        
    
        
 
    #@st.cache_data
    def obtener_nuevos_activos_general(self):
        """
        Función para obtener los datos de los clientes nuevos y activos GENERALES
        """
        query = """
        WITH ClientesActivos AS (
            -- Clientes que han comprado en el año actual y son de tipo 'Cliente'
            SELECT DISTINCT a.Name, a.DateCreated
            FROM [ForceSyncDB_Worker].[dbo].[Accounts] a
            INNER JOIN [ForceSyncDB_Worker].[dbo].[Opportunities] o 
                ON a.Name = o.AccountId1_Value
            WHERE a.TypeId_Value = 'Cliente'
                AND a.Deleted = 0
                AND o.StatusId_Value = '7. Vendido'
                AND YEAR(o.ClosedDate) = YEAR(GETDATE())
        ),
        ClientesNuevos AS (
            -- Clientes activos que además fueron creados en el año actual
            SELECT Name, DateCreated
            FROM ClientesActivos
            WHERE YEAR(DateCreated) = YEAR(GETDATE())
        )
        SELECT 
            'Clientes Activos' as Tipo,
            COUNT(*) as Total
        FROM ClientesActivos
        UNION ALL
        SELECT 
            'Clientes Nuevos' as Tipo,
            COUNT(*) as Total
        FROM ClientesNuevos;
        """
        
        return self._ejecutar_query_clientes(query)

    def obtener_nuevos_activos_vendedores_seleccionados(self, vendedores_lista):
        """
        Función para obtener los datos de los clientes nuevos y activos de VENDEDORES SELECCIONADOS
        """
        if not vendedores_lista or len(vendedores_lista) == 0:
            # Si no hay vendedores seleccionados, retornar datos vacíos
            return pd.DataFrame({
                'Tipo': ['Clientes Activos', 'Clientes Nuevos'], 
                'Total': [0, 0]
            })
        
        # Crear placeholders para la query IN (?, ?, ?, ...)
        placeholders = ', '.join(['?' for _ in vendedores_lista])
        
        query = f"""
        WITH ClientesActivos AS (
            -- Clientes que han comprado en el año actual y son de tipo 'Cliente'
            SELECT DISTINCT a.Name, a.DateCreated, a.SalesRepId1_Value
            FROM [ForceSyncDB_Worker].[dbo].[Accounts] a
            INNER JOIN [ForceSyncDB_Worker].[dbo].[Opportunities] o 
                ON a.Name = o.AccountId1_Value
            WHERE a.TypeId_Value = 'Cliente'
                AND a.Deleted = 0
                AND o.StatusId_Value = '7. Vendido'
                AND YEAR(o.ClosedDate) = YEAR(GETDATE())
                AND a.SalesRepId1_Value IN ({placeholders})
                AND o.SalesRepId_Value IN ({placeholders})
        ),
        ClientesNuevos AS (
            -- Clientes activos que además fueron creados en el año actual
            SELECT Name, DateCreated, SalesRepId1_Value
            FROM ClientesActivos
            WHERE YEAR(DateCreated) = YEAR(GETDATE())
        )
        SELECT 
            'Clientes Activos' as Tipo,
            COUNT(*) as Total
        FROM ClientesActivos
        UNION ALL
        SELECT 
            'Clientes Nuevos' as Tipo,
            COUNT(*) as Total
        FROM ClientesNuevos;
        """
        
        # Duplicar la lista de vendedores para ambos placeholders en la query
        params = vendedores_lista + vendedores_lista
        return self._ejecutar_query_clientes(query, params)

    def obtener_nuevos_activos_vendedor(self, vendedor):
        """
        Función para obtener los datos de los clientes nuevos y activos de UN VENDEDOR ESPECÍFICO
        (Mantenida para compatibilidad, pero ahora usa la función de múltiples vendedores)
        """
        return self.obtener_nuevos_activos_vendedores_seleccionados([vendedor])

    def _ejecutar_query_clientes(self, query, params=None):
        """
        Método auxiliar para ejecutar las queries de clientes
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                
                # Validar que tenemos los datos esperados
                if not df.empty and 'Tipo' in df.columns and 'Total' in df.columns:
                    # Asegurar que tenemos ambos tipos de clientes, aunque alguno sea 0
                    tipos_esperados = ['Clientes Activos', 'Clientes Nuevos']
                    for tipo in tipos_esperados:
                        if tipo not in df['Tipo'].values:
                            # Agregar fila con 0 si no existe el tipo
                            nueva_fila = pd.DataFrame({'Tipo': [tipo], 'Total': [0]})
                            df = pd.concat([df, nueva_fila], ignore_index=True)
                    
                    return df
                else:
                    st.warning("Los datos obtenidos no tienen el formato esperado")
                    return pd.DataFrame(columns=['Tipo', 'Total'])
            else:
                # Retornar DataFrame vacío con estructura correcta si no hay datos
                return pd.DataFrame({
                    'Tipo': ['Clientes Activos', 'Clientes Nuevos'], 
                    'Total': [0, 0]
                })
                
        except Exception as e:
            st.error(f"Error obteniendo datos de clientes: {e}")
            # Retornar DataFrame vacío con estructura correcta en caso de error
            return pd.DataFrame({
                'Tipo': ['Clientes Activos', 'Clientes Nuevos'], 
                'Total': [0, 0]
            })
        finally:
            # Asegurar que la conexión se cierre
            try:
                if conn:
                    conn.close()
            except:
                pass



    """
    Status Cliente
    """
    def obtener_status_cliente_general(self):
        """
        Función para obtener los datos de tipos de clientes GENERALES
        """
        query = """
        WITH TotalClientes AS (
            SELECT COUNT(*) AS Total
            FROM [ForceSyncDB_Worker].[dbo].[Accounts]
            WHERE TypeId_Value IN ('Cliente', 'Prospecto', 'Antiguo cliente') 
                AND Deleted = 0
        ),
        ConteoPorTipo AS (
            SELECT 
                TypeId_Value AS TipoCliente,
                COUNT(*) AS Cantidad
            FROM [ForceSyncDB_Worker].[dbo].[Accounts]
            WHERE TypeId_Value IN ('Cliente', 'Prospecto', 'Antiguo cliente') 
                AND Deleted = 0
            GROUP BY TypeId_Value
        ),
        VentasPorTipo AS (
            SELECT 
                a.TypeId_Value AS TipoCliente,
                SUM(ISNULL(op.Total, 0)) AS TotalVentas
            FROM [ForceSyncDB_Worker].[dbo].[Opportunities] op
            INNER JOIN [ForceSyncDB_Worker].[dbo].[Accounts] a ON a.Id = op.AccountId1_Id
            WHERE a.TypeId_Value IN ('Cliente', 'Prospecto', 'Antiguo cliente')
                AND a.Deleted = 0
                AND op.StatusId_Value = '7. Vendido'
            GROUP BY a.TypeId_Value
        )
        SELECT 
            c.TipoCliente,
            c.Cantidad,
            t.Total AS TotalGeneral,
            ROUND((c.Cantidad * 100.0 / t.Total), 2) AS Porcentaje,
            COALESCE(v.TotalVentas, 0) AS TotalVentas
        FROM ConteoPorTipo c
        CROSS JOIN TotalClientes t
        LEFT JOIN VentasPorTipo v ON c.TipoCliente = v.TipoCliente
        ORDER BY c.Cantidad DESC;
        """
        
        return self._ejecutar_query_status(query)

    def obtener_status_cliente_vendedores_seleccionados(self, vendedores_lista):
        """
        Función para obtener los datos de tipos de clientes de VENDEDORES SELECCIONADOS
        """
        if not vendedores_lista or len(vendedores_lista) == 0:
            # Si no hay vendedores seleccionados, retornar datos vacíos
            return pd.DataFrame(columns=['TipoCliente', 'Cantidad', 'TotalGeneral', 'Porcentaje', 'TotalVentas'])
        
        # Crear placeholders para la query IN (?, ?, ?, ...)
        placeholders = ', '.join(['?' for _ in vendedores_lista])
        
        query = f"""
        WITH TotalClientes AS (
            SELECT COUNT(*) AS Total
            FROM [ForceSyncDB_Worker].[dbo].[Accounts]
            WHERE TypeId_Value IN ('Cliente', 'Prospecto', 'Antiguo cliente') 
                AND Deleted = 0
                AND SalesRepId1_Value IN ({placeholders})
        ),
        ConteoPorTipo AS (
            SELECT 
                TypeId_Value AS TipoCliente,
                COUNT(*) AS Cantidad
            FROM [ForceSyncDB_Worker].[dbo].[Accounts]
            WHERE TypeId_Value IN ('Cliente', 'Prospecto', 'Antiguo cliente') 
                AND Deleted = 0
                AND SalesRepId1_Value IN ({placeholders})
            GROUP BY TypeId_Value
        ),
        VentasPorTipo AS (
            SELECT 
                a.TypeId_Value AS TipoCliente,
                SUM(ISNULL(op.Total, 0)) AS TotalVentas
            FROM [ForceSyncDB_Worker].[dbo].[Opportunities] op
            INNER JOIN [ForceSyncDB_Worker].[dbo].[Accounts] a ON a.Id = op.AccountId1_Id
            WHERE a.TypeId_Value IN ('Cliente', 'Prospecto', 'Antiguo cliente')
                AND a.Deleted = 0
                AND op.StatusId_Value = '7. Vendido'
                AND a.SalesRepId1_Value IN ({placeholders})
                AND op.SalesRepId_Value IN ({placeholders})
            GROUP BY a.TypeId_Value
        )
        SELECT 
            c.TipoCliente,
            c.Cantidad,
            t.Total AS TotalGeneral,
            ROUND((c.Cantidad * 100.0 / NULLIF(t.Total, 0)), 2) AS Porcentaje,
            COALESCE(v.TotalVentas, 0) AS TotalVentas
        FROM ConteoPorTipo c
        CROSS JOIN TotalClientes t
        LEFT JOIN VentasPorTipo v ON c.TipoCliente = v.TipoCliente
        ORDER BY c.Cantidad DESC;
        """
        
        # Cuadruplicar la lista de vendedores para todos los placeholders en la query
        params = vendedores_lista * 4  # Para los 4 diferentes IN clauses
        return self._ejecutar_query_status(query, params)

    @st.cache_data
    def obtener_status_cliente(_self, vendedor):
        """
        DEPRECATED: Función para un solo vendedor - mantenida para compatibilidad
        """
        return _self.obtener_status_cliente_vendedores_seleccionados([vendedor])

    def _ejecutar_query_status(self, query, params=None):
        """
        Método auxiliar para ejecutar las queries de status de clientes
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            
            if rows:
                columns = [column[0] for column in cursor.description]
                df = pd.DataFrame.from_records(rows, columns=columns)
                return df
            else:
                # Retornar DataFrame vacío con estructura correcta si no hay datos
                return pd.DataFrame(columns=['TipoCliente', 'Cantidad', 'TotalGeneral', 'Porcentaje', 'TotalVentas'])
                
        except Exception as e:
            st.error(f"Error obteniendo datos de status de clientes: {e}")
            return pd.DataFrame(columns=['TipoCliente', 'Cantidad', 'TotalGeneral', 'Porcentaje', 'TotalVentas'])
        finally:
            try:
                if conn:
                    conn.close()
            except:
                pass
