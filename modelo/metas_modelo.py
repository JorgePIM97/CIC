# modelo/metas_modelo.py
import pandas as pd
import streamlit as st
from .db_connection import DatabaseConnection

class MetasModelo:
    def __init__(self):
        self.db = DatabaseConnection()

    def insertar_meta(self, nombre_vendedor, valor_meta, mes_meta, year_meta):
        """
        Inserta una nueva meta en la tabla Metas después de verificar que no exista
        
        Args:
            nombre_vendedor (str): Nombre del vendedor
            valor_meta (float): Valor de la meta
            mes_meta (str): Mes al que corresponde la meta (ej: 'Julio')
        
        Returns:
            bool: True si la inserción fue exitosa, False si hubo error
        """
        try:
            # Primero verificamos si ya existe una meta para ese vendedor y mes
            if self.verificar_meta_existente(nombre_vendedor, mes_meta, year_meta):
                st.warning(f"Ya existe una meta para {nombre_vendedor} en el mes de {mes_meta} del año {year_meta}")
                return False
            
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO Metas (NombreVendedor, ValorMeta, MesMeta, YearMeta)
            VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(query, (nombre_vendedor, valor_meta, mes_meta, year_meta))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            st.success(f"Meta insertada correctamente para {nombre_vendedor} - {mes_meta} del {year_meta}: ${valor_meta:,.2f}")
            return True
            
        except Exception as e:
            st.error(f"Error al insertar meta: {e}")
            return False
        
    def verificar_meta_existente(self, nombre_vendedor, mes_meta, year_meta):
        """
        Verifica si ya existe una meta para el vendedor y mes especificado
        
        Args:
            nombre_vendedor (str): Nombre del vendedor
            mes_meta (str): Mes de la meta
        
        Returns:
            bool: True si existe, False si no existe
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT COUNT(*) FROM Metas 
            WHERE NombreVendedor = ? AND MesMeta = ? AND YearMeta = ?
            """
            
            cursor.execute(query, (nombre_vendedor, mes_meta, year_meta))
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return count > 0
            
        except Exception as e:
            st.error(f"Error al verificar meta existente: {e}")
            return False

    def obtener_todas_las_metas(self):
        """
        Obtiene todas las metas registradas en la base de datos
        
        Returns:
            pd.DataFrame: DataFrame con todas las metas o DataFrame vacío si hay error
        """
        try:
            conn = self.db.get_connection()
            
            query = """
            SELECT 
                idMeta,
                NombreVendedor,
                ValorMeta,
                MesMeta,
                FechaRegistro,
                YearMeta
            FROM Metas
            ORDER BY 
                CASE MesMeta
                    WHEN 'Enero' THEN 1
                    WHEN 'Febrero' THEN 2
                    WHEN 'Marzo' THEN 3
                    WHEN 'Abril' THEN 4
                    WHEN 'Mayo' THEN 5
                    WHEN 'Junio' THEN 6
                    WHEN 'Julio' THEN 7
                    WHEN 'Agosto' THEN 8
                    WHEN 'Septiembre' THEN 9
                    WHEN 'Octubre' THEN 10
                    WHEN 'Noviembre' THEN 11
                    WHEN 'Diciembre' THEN 12
                END, 
                NombreVendedor
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            # Formatear la columna de valor para mejor visualización
            if not df.empty:
                df['ValorMeta_Formateado'] = df['ValorMeta'].apply(lambda x: f"${x:,.2f}")
                df['FechaRegistro'] = pd.to_datetime(df['FechaRegistro']).dt.strftime('%d/%m/%Y %H:%M')
            
            return df
            
        except Exception as e:
            st.error(f"Error al obtener las metas: {e}")
            return pd.DataFrame()  # Retorna DataFrame vacío en caso de error

    def obtener_metas_por_vendedor(self, nombre_vendedor):
        """
        Obtiene las metas de un vendedor específico
        
        Args:
            nombre_vendedor (str): Nombre del vendedor
        
        Returns:
            pd.DataFrame: DataFrame con las metas del vendedor
        """
        try:
            conn = self.db.get_connection()
            
            query = """
            SELECT 
                idMeta,
                NombreVendedor,
                ValorMeta,
                MesMeta,
                FechaRegistro,
                YearMeta
            FROM Metas
            WHERE NombreVendedor = ?
            ORDER BY 
                CASE MesMeta
                    WHEN 'Enero' THEN 1
                    WHEN 'Febrero' THEN 2
                    WHEN 'Marzo' THEN 3
                    WHEN 'Abril' THEN 4
                    WHEN 'Mayo' THEN 5
                    WHEN 'Junio' THEN 6
                    WHEN 'Julio' THEN 7
                    WHEN 'Agosto' THEN 8
                    WHEN 'Septiembre' THEN 9
                    WHEN 'Octubre' THEN 10
                    WHEN 'Noviembre' THEN 11
                    WHEN 'Diciembre' THEN 12
                END
            """
            
            df = pd.read_sql(query, conn, params=[nombre_vendedor])
            conn.close()
            
            # Formatear la columna de valor para mejor visualización
            if not df.empty:
                df['ValorMeta_Formateado'] = df['ValorMeta'].apply(lambda x: f"${x:,.2f}")
                df['FechaRegistro'] = pd.to_datetime(df['FechaRegistro']).dt.strftime('%d/%m/%Y %H:%M')
            
            return df
            
        except Exception as e:
            st.error(f"Error al obtener las metas del vendedor: {e}")
            return pd.DataFrame()


    def actualizar_meta(self, nombre_vendedor, valor_meta, mes_meta, year_meta):
        """
        Actualiza una meta existente
        
        Args:
            nombre_vendedor (str): Nombre del vendedor
            valor_meta (float): Nuevo valor de la meta
            mes_meta (str): Mes al que corresponde la meta
        
        Returns:
            bool: True si la actualización fue exitosa, False si hubo error
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
            UPDATE Metas 
            SET ValorMeta = ?, FechaRegistro = GETDATE()
            WHERE NombreVendedor = ? AND MesMeta = ? AND YearMeta = ?
            """
            
            cursor.execute(query, (valor_meta, nombre_vendedor, mes_meta, year_meta))
            
            if cursor.rowcount > 0:
                conn.commit()
                st.success(f"Meta actualizada correctamente para {nombre_vendedor} - {mes_meta}: ${valor_meta:,.2f}")
                result = True
            else:
                st.warning("No se encontró la meta para actualizar")
                result = False
            
            cursor.close()
            conn.close()
            
            return result
            
        except Exception as e:
            st.error(f"Error al actualizar meta: {e}")
            return False

    def insertar_o_actualizar_meta(self, nombre_vendedor, valor_meta, mes_meta, year_meta):
        """
        Inserta una nueva meta o actualiza una existente
        
        Args:
            nombre_vendedor (str): Nombre del vendedor
            valor_meta (float): Valor de la meta
            mes_meta (str): Mes al que corresponde la meta
        
        Returns:
            bool: True si la operación fue exitosa, False si hubo error
        """
        if self.verificar_meta_existente(nombre_vendedor, mes_meta, year_meta):
            return self.actualizar_meta(nombre_vendedor, valor_meta, mes_meta, year_meta)
        else:
            return self.insertar_meta(nombre_vendedor, valor_meta, mes_meta, year_meta)