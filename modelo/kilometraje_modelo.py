# modelo/kilometraje_modelo.py
import pandas as pd
import streamlit as st
import calendar
from datetime import datetime
from .db_connection import DatabaseConnection

class KilometrajeModelo:
    def __init__(self):
        self.db = DatabaseConnection()


    def obtener_total_kilometraje_mes(self, vendedor, mes, año):
        """
        Obtiene el total de kilometraje recorrido por un vendedor en un mes y año específico.
        """

        try:
            conn = self.db.get_connection()

            # Convertir mes a número
            meses = {
                "enero": 1,
                "febrero": 2,
                "marzo": 3,
                "abril": 4,
                "mayo": 5,
                "junio": 6,
                "julio": 7,
                "agosto": 8,
                "septiembre": 9,
                "octubre": 10,
                "noviembre": 11,
                "diciembre": 12
            }

            numero_mes = meses.get(mes.lower())

            if numero_mes is None:
                st.error("Mes inválido.")
                return pd.DataFrame()

            # Query SQL
            query = """
            DECLARE @FechaInicio DATE = DATEFROMPARTS(?, ?, 1)
            DECLARE @FechaFin DATE = DATEADD(MONTH, 1, @FechaInicio)

            SELECT 
                Vendedor,
                SUM(Kilometros) AS TotalKilometros
            FROM MovilidadRegistro
            WHERE Vendedor LIKE ? + '%'
            AND Fecha_Movilidad >= @FechaInicio
            AND Fecha_Movilidad < @FechaFin
            GROUP BY Vendedor
            """

            params = (año, numero_mes, vendedor)

            df = pd.read_sql(query, conn, params=params)

            conn.close()

            return df

        except Exception as e:
            st.error(f"Error al obtener el kilometraje: {e}")
            return pd.DataFrame()

    def insertar_kilometraje(self, vendedor, kilometros, descripcion, fecha_movilidad):
        """
        Inserta un nuevo registro de kilometraje en la tabla MovilidadRegistro.
        """

        # Validar que haya valores
        if not vendedor:
            st.error("Debe seleccionar un vendedor.")
            return False
        if kilometros <= 0 or kilometros == None:
            st.error("Debe ingresar un valor válido de kilómetros.")
            return False

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Fecha actual como fecha de registro
            fecha_registro = datetime.now()

            # Query SQL para insertar datos
            query = """
                INSERT INTO [ForceSyncDB_Worker].[dbo].[MovilidadRegistro]
                    ([Vendedor], [Kilometros], [Descripcion], [Fecha_Movilidad], [Fecha_Registro])
                VALUES (?, ?, ?, ?, ?)
            """

            # Parámetros
            params = (vendedor, kilometros, descripcion, fecha_movilidad, fecha_registro)

            cursor.execute(query, params)
            conn.commit()
            
            cursor.close()
            conn.close()

            st.success("✅ Kilometraje registrado correctamente.")
            return True

        except Exception as e:
            st.error(f"Error al insertar el registro: {e}")
            return False
        

    def obtener_registros_kilometraje(self, limite):
        """
        Obtiene los registros de kilometraje de la tabla MovilidadRegistro.
        
        Args:
            limite (int | str): Número máximo de registros a mostrar o 'Todos'
            
        Returns:
            DataFrame: DataFrame con los registros o None si hay error
        """
        try:
            conn = self.db.get_connection()

            if limite == "Todos":
                # Sin límite, trae todos los registros
                query = """
                    SELECT
                        [id_MovilidadRegistro],
                        [Vendedor],
                        [Kilometros],
                        [Descripcion],
                        [Fecha_Movilidad],
                        [Fecha_Registro]
                    FROM [ForceSyncDB_Worker].[dbo].[MovilidadRegistro]
                    ORDER BY [Fecha_Registro] DESC
                """
                df = pd.read_sql(query, conn)
            else:
                # Con límite
                query = """
                    SELECT TOP (?)
                        [id_MovilidadRegistro],
                        [Vendedor],
                        [Kilometros],
                        [Descripcion],
                        [Fecha_Movilidad],
                        [Fecha_Registro]
                    FROM [ForceSyncDB_Worker].[dbo].[MovilidadRegistro]
                    ORDER BY [Fecha_Registro] DESC
                """
                df = pd.read_sql(query, conn, params=[limite])

            conn.close()
            return df

        except Exception as e:
            st.error(f"Error al obtener los registros: {e}")
            return None

    def eliminar_kilometraje(self, vendedor, fecha_movilidad, kilometros):
        """
        Elimina un registro de kilometraje según el vendedor, fecha y kilómetros.
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                DELETE FROM [ForceSyncDB_Worker].[dbo].[MovilidadRegistro]
                WHERE [Vendedor] = ? AND [Fecha_Movilidad] = ? AND [Kilometros] = ?
            """

            cursor.execute(query, (vendedor, fecha_movilidad, kilometros))
            conn.commit()
            cursor.close()
            conn.close()

            st.success("🗑️ Registro eliminado correctamente.")
            return True

        except Exception as e:
            st.error(f"Error al eliminar el registro: {e}")
            return False


    def eliminar_kilometraje_por_id(self, id_registro):
        """
        Elimina un registro de kilometraje por su ID (más confiable).
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                DELETE FROM [ForceSyncDB_Worker].[dbo].[MovilidadRegistro]
                WHERE [id_MovilidadRegistro] = ?
            """

            cursor.execute(query, (id_registro,))
            conn.commit()
            cursor.close()
            conn.close()

            return True

        except Exception as e:
            st.error(f"Error al eliminar el registro: {e}")
            return False