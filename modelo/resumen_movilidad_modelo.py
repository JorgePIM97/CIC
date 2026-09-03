#modelo/resumen_movilidad_modelo.py
import pandas as pd
import streamlit as st
from .db_connection import DatabaseConnection

class ResumenMovilidadModelo:
    def __init__(self):
        self.db = DatabaseConnection()


    def verificar_resumen_existente(self, nombre_vendedor, mes, year):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT COUNT(*)
            FROM ResumenMovilidad
            WHERE NombreVendedor = ?
            AND Mes = ?
            AND Año = ?
            """

            cursor.execute(query, (nombre_vendedor, mes, year))
            count = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            return count > 0

        except Exception as e:
            st.error(f"Error al verificar resumen existente: {e}")
            return False


    def insertar_resumen(
        self,
        nombre_vendedor,
        dias_habiles,
        mes,
        avg_diario_recorrido,
        cantidad_visitas,
        tiempo_destinado_atencion,
        avg_tiempo_cliente,
        avg_visitas_dia,
        year
    ):

        try:

            if self.verificar_resumen_existente(nombre_vendedor, mes, year):
                st.warning(f"Ya existe un resumen para {nombre_vendedor} - {mes} {year}")
                return False

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO ResumenMovilidad
            (
                DiasHabiles,
                Mes,
                AvgDiarioRecorrido,
                CantidadVisitas,
                TiempoDestinadoAtencion,
                AvgTiempoConCliente,
                AvgVisitasPorDia,
                NombreVendedor,
                Año
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, (
                dias_habiles,
                mes,
                avg_diario_recorrido,
                cantidad_visitas,
                tiempo_destinado_atencion,
                avg_tiempo_cliente,
                avg_visitas_dia,
                nombre_vendedor,
                year
            ))

            conn.commit()

            cursor.close()
            conn.close()

            st.success(f"Resumen insertado correctamente para {nombre_vendedor} - {mes} {year}")

            return True

        except Exception as e:
            st.error(f"Error al insertar resumen: {e}")
            return False


    def actualizar_resumen(
        self,
        nombre_vendedor,
        dias_habiles,
        mes,
        avg_diario_recorrido,
        cantidad_visitas,
        tiempo_destinado_atencion,
        avg_tiempo_cliente,
        avg_visitas_dia,
        year
    ):

        try:

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            UPDATE ResumenMovilidad
            SET
                DiasHabiles = ?,
                AvgDiarioRecorrido = ?,
                CantidadVisitas = ?,
                TiempoDestinadoAtencion = ?,
                AvgTiempoConCliente = ?,
                AvgVisitasPorDia = ?,
                FechaRegistro = GETDATE()
            WHERE
                NombreVendedor = ?
                AND Mes = ?
                AND Año = ?
            """

            cursor.execute(query, (
                dias_habiles,
                avg_diario_recorrido,
                cantidad_visitas,
                tiempo_destinado_atencion,
                avg_tiempo_cliente,
                avg_visitas_dia,
                nombre_vendedor,
                mes,
                year
            ))

            if cursor.rowcount > 0:
                conn.commit()
                st.success(f"Resumen actualizado correctamente para {nombre_vendedor} - {mes} {year}")
                result = True
            else:
                st.warning("No se encontró el resumen para actualizar")
                result = False

            cursor.close()
            conn.close()

            return result

        except Exception as e:
            st.error(f"Error al actualizar resumen: {e}")
            return False


    def insertar_o_actualizar_resumen(
        self,
        nombre_vendedor,
        dias_habiles,
        mes,
        avg_diario_recorrido,
        cantidad_visitas,
        tiempo_destinado_atencion,
        avg_tiempo_cliente,
        avg_visitas_dia,
        year
    ):

        if self.verificar_resumen_existente(nombre_vendedor, mes, year):

            return self.actualizar_resumen(
                nombre_vendedor,
                dias_habiles,
                mes,
                avg_diario_recorrido,
                cantidad_visitas,
                tiempo_destinado_atencion,
                avg_tiempo_cliente,
                avg_visitas_dia,
                year
            )

        else:

            return self.insertar_resumen(
                nombre_vendedor,
                dias_habiles,
                mes,
                avg_diario_recorrido,
                cantidad_visitas,
                tiempo_destinado_atencion,
                avg_tiempo_cliente,
                avg_visitas_dia,
                year
            )
        
    def obtener_resumenes(self):
        """
        Obtiene todos los registros de resumen de movilidad
        """

        try:
            conn = self.db.get_connection()

            query = """
            SELECT
                idResumenMovilidad,
                NombreVendedor,
                DiasHabiles,
                Mes,
                Año,
                AvgDiarioRecorrido,
                CantidadVisitas,
                TiempoDestinadoAtencion,
                AvgTiempoConCliente,
                AvgVisitasPorDia,
                FechaRegistro
            FROM ResumenMovilidad
            ORDER BY
                Año DESC,
                CASE Mes
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

            if not df.empty:
                df['FechaRegistro'] = pd.to_datetime(df['FechaRegistro']).dt.strftime('%d/%m/%Y %H:%M')

            return df

        except Exception as e:
            st.error(f"Error al obtener los resúmenes: {e}")
            return pd.DataFrame()

    def obtener_resumenes_reporte_pdf(self, nombre_vendedor, mes, año):
        """
        Obtiene el resumen de movilidad filtrado por NombreVendedor, Mes y Año
        """

        try:
            conn = self.db.get_connection()

            query = """
            SELECT
                idResumenMovilidad,
                NombreVendedor,
                DiasHabiles,
                Mes,
                Año,
                AvgDiarioRecorrido,
                CantidadVisitas,
                TiempoDestinadoAtencion,
                AvgTiempoConCliente,
                AvgVisitasPorDia,
                FechaRegistro
            FROM ResumenMovilidad
            WHERE NombreVendedor LIKE ? + '%'
            AND Mes = ?
            AND Año = ?
            ORDER BY
                CASE Mes
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

            df = pd.read_sql(query, conn, params=[nombre_vendedor, mes, año])

            conn.close()

            if not df.empty:
                df['FechaRegistro'] = pd.to_datetime(df['FechaRegistro']).dt.strftime('%d/%m/%Y %H:%M')

            return df

        except Exception as e:
            st.error(f"Error al obtener los resúmenes: {e}")
            return pd.DataFrame()
        
    def obtener_cantidad_visitas_pdf(self, nombre_vendedor, mes, año):
        """
        Obtiene la cantidad de visitas filtrado por NombreVendedor, Mes y Año
        """
        try:
            conn = self.db.get_connection()

            query = """
            SELECT
                CantidadVisitas
            FROM ResumenMovilidad
            WHERE NombreVendedor LIKE ? + '%'
            AND Mes = ?
            AND Año = ?
            """

            df = pd.read_sql(query, conn, params=[nombre_vendedor, mes, año])
            conn.close()

            if not df.empty:
                return df['CantidadVisitas'].iloc[0]
            
            return 0

        except Exception as e:
            st.error(f"Error al obtener la cantidad de visitas: {e}")
            return 0