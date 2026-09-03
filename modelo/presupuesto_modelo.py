# modelo/presupuesto_modelo.py
import pandas as pd
import streamlit as st
from .db_connection import DatabaseConnection

class PresupuestoModelo:
    def __init__(self):
        self.db = DatabaseConnection()

    def insertar_presupuesto(self, 
                             nombre_vendedor, 
                             year_presupuesto, 
                             mes_presupuesto,
                             consumible_mecanizado_plasma,
                             consumible_manual,
                             refacciones,
                             consumible_mecanizado_laser,
                             consumible_mecanizado_oxicorte,
                             sis_corte_laser,
                             sis_corte_plasma,
                             sis_corte_oxy_water,
                             powermax,
                             robotica):
        try:
            if self.verificar_presupuesto_existente(nombre_vendedor, mes_presupuesto, year_presupuesto):
                st.warning(f"Ya existe un presupuesto para {nombre_vendedor} en {mes_presupuesto} del {year_presupuesto}")
                return False

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO PresupuestoSegmentos (
                NombreVendedor,
                ConsumibleMecanizadoPlasma,
                ConsumibleManual,
                Refacciones,
                ConsumibleMecanizadoLaser,
                ConsumibleMecanizadoOxicorte,
                SisCorteLaser,
                SisCortePlasma,
                SisCorteOxyWater,
                Powermax,
                Robotica,
                MesPresupuesto,
                YearPresupuesto,
                FechaRegistro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """

            cursor.execute(query, (
                nombre_vendedor,
                consumible_mecanizado_plasma,
                consumible_manual,
                refacciones,
                consumible_mecanizado_laser,
                consumible_mecanizado_oxicorte,
                sis_corte_laser,
                sis_corte_plasma,
                sis_corte_oxy_water,
                powermax,
                robotica,
                mes_presupuesto,
                year_presupuesto
            ))
            conn.commit()
            cursor.close()
            conn.close()

            st.success(f"Presupuesto insertado correctamente para {nombre_vendedor} - {mes_presupuesto} {year_presupuesto}")
            return True

        except Exception as e:
            st.error(f"Error al insertar presupuesto: {e}")
            return False

    def verificar_presupuesto_existente(self, nombre_vendedor, mes_presupuesto, year_presupuesto):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT COUNT(*) FROM PresupuestoSegmentos
            WHERE NombreVendedor = ? AND MesPresupuesto = ? AND YearPresupuesto = ?
            """

            cursor.execute(query, (nombre_vendedor, mes_presupuesto, year_presupuesto))
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            return count > 0

        except Exception as e:
            st.error(f"Error al verificar presupuesto existente: {e}")
            return False

    def obtener_todas_los_presupuestos(self):
        try:
            conn = self.db.get_connection()

            query = """
            SELECT
                idPresupuestoSegmento,
                NombreVendedor,
                ConsumibleMecanizadoPlasma,
                ConsumibleManual,
                Refacciones,
                ConsumibleMecanizadoLaser,
                ConsumibleMecanizadoOxicorte,
                SisCorteLaser,
                SisCortePlasma,
                SisCorteOxyWater,
                Powermax,
                Robotica,
                MesPresupuesto,
                YearPresupuesto,
                FechaRegistro
            FROM PresupuestoSegmentos
            ORDER BY
                YearPresupuesto,
                CASE MesPresupuesto
                    WHEN 'Enero'      THEN 1
                    WHEN 'Febrero'    THEN 2
                    WHEN 'Marzo'      THEN 3
                    WHEN 'Abril'      THEN 4
                    WHEN 'Mayo'       THEN 5
                    WHEN 'Junio'      THEN 6
                    WHEN 'Julio'      THEN 7
                    WHEN 'Agosto'     THEN 8
                    WHEN 'Septiembre' THEN 9
                    WHEN 'Octubre'    THEN 10
                    WHEN 'Noviembre'  THEN 11
                    WHEN 'Diciembre'  THEN 12
                END,
                NombreVendedor
            """

            df = pd.read_sql(query, conn)
            conn.close()

            if not df.empty:
                df['FechaRegistro'] = pd.to_datetime(df['FechaRegistro']).dt.strftime('%d/%m/%Y %H:%M')

            return df

        except Exception as e:
            st.error(f"Error al obtener los presupuestos: {e}")
            return pd.DataFrame()

    def obtener_presupuesto_por_vendedor(self, nombre_vendedor):
        try:
            conn = self.db.get_connection()

            query = """
            SELECT
                idPresupuestoSegmento,
                NombreVendedor,
                ConsumibleMecanizadoPlasma,
                ConsumibleManual,
                Refacciones,
                ConsumibleMecanizadoLaser,
                ConsumibleMecanizadoOxicorte,
                SisCorteLaser,
                SisCortePlasma,
                SisCorteOxyWater,
                Powermax,
                Robotica,
                MesPresupuesto,
                YearPresupuesto,
                FechaRegistro
            FROM PresupuestoSegmentos
            WHERE NombreVendedor = ?
            ORDER BY
                YearPresupuesto,
                CASE MesPresupuesto
                    WHEN 'Enero'      THEN 1
                    WHEN 'Febrero'    THEN 2
                    WHEN 'Marzo'      THEN 3
                    WHEN 'Abril'      THEN 4
                    WHEN 'Mayo'       THEN 5
                    WHEN 'Junio'      THEN 6
                    WHEN 'Julio'      THEN 7
                    WHEN 'Agosto'     THEN 8
                    WHEN 'Septiembre' THEN 9
                    WHEN 'Octubre'    THEN 10
                    WHEN 'Noviembre'  THEN 11
                    WHEN 'Diciembre'  THEN 12
                END
            """

            df = pd.read_sql(query, conn, params=[nombre_vendedor])
            conn.close()

            if not df.empty:
                df['FechaRegistro'] = pd.to_datetime(df['FechaRegistro']).dt.strftime('%d/%m/%Y %H:%M')

            return df

        except Exception as e:
            st.error(f"Error al obtener presupuesto del vendedor: {e}")
            return pd.DataFrame()

    def actualizar_presupuesto(self, 
                             nombre_vendedor, 
                             year_presupuesto, 
                             mes_presupuesto,
                             consumible_mecanizado_plasma,
                             consumible_manual,
                             refacciones,
                             consumible_mecanizado_laser,
                             consumible_mecanizado_oxicorte,
                             sis_corte_laser,
                             sis_corte_plasma,
                             sis_corte_oxy_water,
                             powermax,
                             robotica):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            UPDATE PresupuestoSegmentos
            SET
                ConsumibleMecanizadoPlasma   = ?,
                ConsumibleManual             = ?,
                Refacciones                  = ?,
                ConsumibleMecanizadoLaser    = ?,
                ConsumibleMecanizadoOxicorte = ?,
                SisCorteLaser                = ?,
                SisCortePlasma               = ?,
                SisCorteOxyWater             = ?,
                Powermax                     = ?,
                Robotica                     = ?,
                FechaRegistro                = GETDATE()
            WHERE NombreVendedor = ? AND MesPresupuesto = ? AND YearPresupuesto = ?
            """

            cursor.execute(query, (
                consumible_mecanizado_plasma,
                consumible_manual,
                refacciones,
                consumible_mecanizado_laser,
                consumible_mecanizado_oxicorte,
                sis_corte_laser,
                sis_corte_plasma,
                sis_corte_oxy_water,
                powermax,
                robotica,
                nombre_vendedor,
                mes_presupuesto,
                year_presupuesto
            ))

            if cursor.rowcount > 0:
                conn.commit()
                st.success(f"Presupuesto actualizado correctamente para {nombre_vendedor} - {mes_presupuesto} {year_presupuesto}")
                result = True
            else:
                st.warning("No se encontró el presupuesto para actualizar")
                result = False

            cursor.close()
            conn.close()
            return result

        except Exception as e:
            st.error(f"Error al actualizar presupuesto: {e}")
            return False

    def insertar_o_actualizar_presupuesto(self, 
                             nombre_vendedor, 
                             year_presupuesto, 
                             mes_presupuesto,
                             consumible_mecanizado_plasma,
                             consumible_manual,
                             refacciones,
                             consumible_mecanizado_laser,
                             consumible_mecanizado_oxicorte,
                             sis_corte_laser,
                             sis_corte_plasma,
                             sis_corte_oxy_water,
                             powermax,
                             robotica):

        args = (
            nombre_vendedor, year_presupuesto, mes_presupuesto,
            consumible_mecanizado_plasma, consumible_manual, refacciones,
            consumible_mecanizado_laser, consumible_mecanizado_oxicorte,
            sis_corte_laser, sis_corte_plasma, sis_corte_oxy_water,
            powermax, robotica
        )

        if self.verificar_presupuesto_existente(nombre_vendedor, mes_presupuesto, year_presupuesto):
            return self.actualizar_presupuesto(*args)
        else:
            return self.insertar_presupuesto(*args)

    def obtener_total_presupuesto_anual(self, nombre_vendedor, year_presupuesto):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT 
                SUM(
                    ConsumibleMecanizadoPlasma +
                    ConsumibleManual +
                    Refacciones +
                    ConsumibleMecanizadoLaser +
                    ConsumibleMecanizadoOxicorte +
                    SisCorteLaser +
                    SisCortePlasma +
                    SisCorteOxyWater +
                    Powermax +
                    Robotica
                ) AS TotalPresupuestoAnual
            FROM PresupuestoSegmentos
            WHERE NombreVendedor = ?
              AND YearPresupuesto = ?
            """

            cursor.execute(query, (nombre_vendedor, year_presupuesto))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return float(result[0]) if result and result[0] is not None else 0

        except Exception as e:
            st.error(f"Error al obtener TotalPresupuestoAnual: {e}")
            return 0

    def obtener_total_presupuesto_mensual(self, nombre_vendedor, year_presupuesto, mes_presupuesto):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT 
                SUM(
                    ConsumibleMecanizadoPlasma +
                    ConsumibleManual +
                    Refacciones +
                    ConsumibleMecanizadoLaser +
                    ConsumibleMecanizadoOxicorte +
                    SisCorteLaser +
                    SisCortePlasma +
                    SisCorteOxyWater +
                    Powermax +
                    Robotica
                ) AS TotalPresupuestoMensual
            FROM PresupuestoSegmentos
            WHERE NombreVendedor = ?
              AND YearPresupuesto = ?
              AND MesPresupuesto = ?
            """

            cursor.execute(query, (nombre_vendedor, year_presupuesto, mes_presupuesto))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return float(result[0]) if result and result[0] is not None else 0

        except Exception as e:
            st.error(f"Error al obtener TotalPresupuestoMensual: {e}")
            return 0

    def obtener_total_presupuesto_acumulado(self, nombre_vendedor, year_presupuesto, mes_presupuesto):
        try:
            meses_orden = {
                'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
                'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
                'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
            }

            numero_mes = meses_orden.get(mes_presupuesto)
            if numero_mes is None:
                st.error(f"Mes no válido: {mes_presupuesto}")
                return 0

            meses_validos = [mes for mes, num in meses_orden.items() if num <= numero_mes]
            placeholders = ','.join(['?' for _ in meses_validos])

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = f"""
            SELECT 
                SUM(
                    ConsumibleMecanizadoPlasma +
                    ConsumibleManual +
                    Refacciones +
                    ConsumibleMecanizadoLaser +
                    ConsumibleMecanizadoOxicorte +
                    SisCorteLaser +
                    SisCortePlasma +
                    SisCorteOxyWater +
                    Powermax +
                    Robotica
                ) AS TotalPresupuestoAcumulado
            FROM PresupuestoSegmentos
            WHERE NombreVendedor = ?
              AND YearPresupuesto = ?
              AND MesPresupuesto IN ({placeholders})
            """

            params = [nombre_vendedor, year_presupuesto] + meses_validos
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            return float(result[0]) if result and result[0] is not None else 0

        except Exception as e:
            st.error(f"Error al obtener TotalPresupuestoAcumulado: {e}")
            return 0
        
    def obtener_presupuesto_anual_vendedores(self, vendedores_lista, year_presupuesto, mes_inicio=1, mes_fin=12):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            placeholders = ','.join(['?' for _ in vendedores_lista])

            query = f"""
            SELECT
                MesPresupuesto,
                SUM(
                    ConsumibleMecanizadoPlasma +
                    ConsumibleManual +
                    Refacciones +
                    ConsumibleMecanizadoLaser +
                    ConsumibleMecanizadoOxicorte +
                    SisCorteLaser +
                    SisCortePlasma +
                    SisCorteOxyWater +
                    Powermax +
                    Robotica
                ) AS TotalPresupuesto
            FROM PresupuestoSegmentos
            WHERE NombreVendedor IN ({placeholders})
            AND YearPresupuesto = ?
            GROUP BY MesPresupuesto
            """

            params = vendedores_lista + [year_presupuesto]
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if not rows:
                return pd.DataFrame(columns=['MesPresupuesto', 'TotalPresupuesto'])

            # Construir el DataFrame fila por fila para evitar problemas con el driver ODBC
            data = [{'MesPresupuesto': row[0], 'TotalPresupuesto': float(row[1]) if row[1] is not None else 0.0} for row in rows]
            df = pd.DataFrame(data)

            meses_map = {
                'ENERO':1,'FEBRERO':2,'MARZO':3,'ABRIL':4,'MAYO':5,'JUNIO':6,
                'JULIO':7,'AGOSTO':8,'SEPTIEMBRE':9,'OCTUBRE':10,'NOVIEMBRE':11,'DICIEMBRE':12
            }
            df['MesNumero'] = df['MesPresupuesto'].str.upper().map(meses_map)
            df = df[df['MesNumero'].between(mes_inicio, mes_fin)].drop(columns='MesNumero')

            return df

        except Exception as e:
            st.error(f"Error al obtener presupuesto anual: {e}")
            return pd.DataFrame(columns=['MesPresupuesto', 'TotalPresupuesto'])
        
    def insertar_o_actualizar_todos_los_meses(self,
                                            nombre_vendedor,
                                            year_presupuesto,
                                            consumible_mecanizado_plasma,
                                            consumible_manual,
                                            refacciones,
                                            consumible_mecanizado_laser,
                                            consumible_mecanizado_oxicorte,
                                            sis_corte_laser,
                                            sis_corte_plasma,
                                            sis_corte_oxy_water,
                                            powermax,
                                            robotica):
        meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril',
            'Mayo', 'Junio', 'Julio', 'Agosto',
            'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]

        exitosos = 0
        fallidos  = 0

        for mes in meses:
            try:
                args = (
                    nombre_vendedor, year_presupuesto, mes,
                    consumible_mecanizado_plasma, consumible_manual, refacciones,
                    consumible_mecanizado_laser, consumible_mecanizado_oxicorte,
                    sis_corte_laser, sis_corte_plasma, sis_corte_oxy_water,
                    powermax, robotica
                )
                resultado = self.insertar_o_actualizar_presupuesto(*args)
                if resultado:
                    exitosos += 1
                else:
                    fallidos += 1
            except Exception as e:
                st.error(f"Error en {mes}: {e}")
                fallidos += 1

        if exitosos > 0:
            st.success(f"✅ {exitosos}/12 meses procesados correctamente para {nombre_vendedor} - {year_presupuesto}")
        if fallidos > 0:
            st.warning(f"⚠️ {fallidos} mes(es) no pudieron procesarse")