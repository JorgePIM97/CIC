#modelo/reporte_pdf/servicio_cliente_modelo.py
import streamlit as st
import calendar
from ..db_connection import DatabaseConnection


class ServicioClienteModelo:
    def __init__(self):
        self.db = DatabaseConnection()

    # --------------------------------------------------
    # UTILIDAD INTERNA
    # --------------------------------------------------
    def _get_id_vendedor(self, vendedor):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT TOP 1 Id_Vendedor_FM
                FROM ForceSyncDB_Worker.dbo.dev_Detalle_Corregida
                WHERE RepresentanteDeVentas = ?
            """

            cursor.execute(query, (vendedor,))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row else None

        except Exception as e:
            st.error(f"Error obteniendo Id_Vendedor_FM: {e}")
            return None

    def _get_fecha_ref(self, mes_nombre, año):
        """
        Retorna (fecha_inicio_mes, fecha_fin_mes, fecha_inicio_año) como strings 'YYYY-MM-DD'
        """
        meses = {
            'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
            'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
            'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
        }
        mes_num    = meses.get(mes_nombre, 1)
        ultimo_dia = calendar.monthrange(año, mes_num)[1]

        fecha_inicio_mes  = f"{año}-{mes_num:02d}-01"
        fecha_fin_mes     = f"{año}-{mes_num:02d}-{ultimo_dia}"
        fecha_inicio_año  = f"{año}-01-01"

        return fecha_inicio_mes, fecha_fin_mes, fecha_inicio_año

    # --------------------------------------------------
    # ---------------- PORCENTAJES ----------------------
    # --------------------------------------------------

    # --------------------------------------------------
    # 1. ASISTENCIA VS PLANEACION (PORCENTAJE)
    # --------------------------------------------------
    def get_porcentaje_asistencia_vs_planeacion(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT CAST(
                CEILING(
                    (
                        (
                            SELECT COUNT(*) * 1.0 FROM Activities
                            WHERE SalesRepId_Id = ?
                              AND Checkin = 1
                              AND CheckoutDate >= CAST(? AS DATE)
                              AND CheckoutDate <= CAST(? AS DATE)
                        )
                        /
                        NULLIF(
                            (
                                SELECT COUNT(*) FROM Calendars
                                WHERE SalesRepId_Id = ?
                                  AND DateCreated >= CAST(? AS DATE)
                                  AND DateCreated <= CAST(? AS DATE)
                            ), 0
                        )
                    ) * 100
                ) / 100.0
            AS DECIMAL(10,2))
            """

            cursor.execute(query, (
                id_vendedor, fecha_inicio_mes, fecha_fin_mes,
                id_vendedor, fecha_inicio_mes, fecha_fin_mes
            ))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error en asistencia vs planeación: {e}")
            return 0

    # --------------------------------------------------
    # 2. COBERTURA CARTERA (PORCENTAJE)
    # --------------------------------------------------
    def get_porcentaje_cobertura_cartera(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, fecha_inicio_año = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT CAST(
                CEILING(
                    (
                        (SELECT COUNT(DISTINCT act.AccountId_Value) * 1.0
                         FROM Activities act
                         INNER JOIN Accounts acc ON acc.Id = act.AccountId_Id
                         WHERE act.SalesRepId_Id = ?
                           AND act.Checkin = 1
                           AND act.CheckoutDate >= CAST(? AS DATE)
                           AND act.CheckoutDate <= CAST(? AS DATE)
                           AND acc.TypeId_Value NOT IN ('Lead'))
                        /
                        NULLIF(
                            (SELECT COUNT(DISTINCT Name)
                             FROM Accounts
                             WHERE DateCreated >= CAST(? AS DATE)
                               AND DateCreated <= CAST(? AS DATE)
                               AND TypeId_Value NOT IN ('Lead')), 0
                        )
                    ) * 100
                ) / 100.0
            AS DECIMAL(10,2))
            """

            cursor.execute(query, (
                id_vendedor, fecha_inicio_mes, fecha_fin_mes,
                fecha_inicio_año, fecha_fin_mes
            ))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error en cobertura cartera: {e}")
            return 0

    # --------------------------------------------------
    # 3. VISITAS COMERCIALES (PORCENTAJE)
    # --------------------------------------------------
    def get_porcentaje_visitas_comerciales(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT CAST(
                CEILING(
                    (
                        (SELECT COUNT(id) * 1.0 FROM Activities
                         WHERE CheckoutDate >= CAST(? AS DATE)
                           AND CheckoutDate <= CAST(? AS DATE)
                           AND SalesRepId_Id = ?
                           AND TypeId_Value = 'Visita')
                        /
                        NULLIF(
                            (SELECT COUNT(id) FROM Activities
                             WHERE CheckoutDate >= CAST(? AS DATE)
                               AND CheckoutDate <= CAST(? AS DATE)
                               AND SalesRepId_Id = ?), 0
                        )
                    ) * 100
                ) / 100.0
            AS DECIMAL(10,2))
            """

            cursor.execute(query, (
                fecha_inicio_mes, fecha_fin_mes, id_vendedor,
                fecha_inicio_mes, fecha_fin_mes, id_vendedor
            ))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error en visitas comerciales: {e}")
            return 0

    # --------------------------------------------------
    # 4. DEMOSTRACIONES PMX (PORCENTAJE)
    # --------------------------------------------------
    def get_porcentaje_demostraciones_pmx(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT CAST(
                CEILING(
                    (
                        (SELECT COUNT(id) * 1.0 FROM Activities
                         WHERE CheckoutDate >= CAST(? AS DATE)
                           AND CheckoutDate <= CAST(? AS DATE)
                           AND SalesRepId_Id = ?
                           AND TypeId_Value IN ('Demostración PMX', 'Presentación de Propuesta'))
                        /
                        NULLIF(
                            (SELECT COUNT(id) FROM Activities
                             WHERE CheckoutDate >= CAST(? AS DATE)
                               AND CheckoutDate <= CAST(? AS DATE)
                               AND SalesRepId_Id = ?), 0
                        )
                    ) * 100
                ) / 100.0
            AS DECIMAL(10,2))
            """

            cursor.execute(query, (
                fecha_inicio_mes, fecha_fin_mes, id_vendedor,
                fecha_inicio_mes, fecha_fin_mes, id_vendedor
            ))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error en demostraciones PMX: {e}")
            return 0

    # --------------------------------------------------
    # 5. NUEVOS CLIENTES (PORCENTAJE)
    # --------------------------------------------------
    def get_porcentaje_nuevos_clientes(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, fecha_inicio_año = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT CAST(
                CEILING(
                    (
                        (SELECT COUNT(*) * 1.0 FROM Accounts
                        WHERE SalesRepId1_Id = ?
                        AND DateCreated >= CAST(? AS DATE)
                        AND DateCreated <= CAST(? AS DATE)
                        AND TypeId_Value IN ('Cliente'))
                        /
                        NULLIF(
                            (SELECT COUNT(*) FROM Accounts
                            WHERE SalesRepId1_Id = ?
                            AND DateCreated >= CAST(? AS DATE)
                            AND DateCreated <= CAST(? AS DATE))
                        , 0)
                    ) * 100
                ) / 100.0
            AS DECIMAL(10,2))
            """

            cursor.execute(query, (
                id_vendedor, fecha_inicio_mes, fecha_fin_mes,
                id_vendedor, fecha_inicio_año, fecha_fin_mes
            ))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error en nuevos clientes: {e}")
            return 0

    # --------------------------------------------------
    # 6. NUEVOS PROSPECTOS (PORCENTAJE)
    # --------------------------------------------------
    def get_porcentaje_nuevos_prospectos(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, fecha_inicio_año = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT CAST(
                CEILING(
                    (
                        (SELECT COUNT(*) * 1.0 FROM Accounts
                        WHERE SalesRepId1_Id = ?
                        AND DateCreated >= CAST(? AS DATE)
                        AND DateCreated <= CAST(? AS DATE)
                        AND TypeId_Value IN ('Prospecto'))
                        /
                        NULLIF(
                            (SELECT COUNT(*) FROM Accounts
                            WHERE SalesRepId1_Id = ?
                            AND DateCreated >= CAST(? AS DATE)
                            AND DateCreated <= CAST(? AS DATE))
                        , 0)
                    ) * 100
                ) / 100.0
            AS DECIMAL(10,2))
            """

            cursor.execute(query, (
                id_vendedor, fecha_inicio_mes, fecha_fin_mes,
                id_vendedor, fecha_inicio_año, fecha_fin_mes
            ))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error en nuevos prospectos: {e}")
            return 0

    # --------------------------------------------------
    # 7. OPORTUNIDADES (PORCENTAJE)
    # --------------------------------------------------
    def get_porcentaje_oportunidades(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT CAST(
                    CEILING(
                        (
                            CAST(
                                (SELECT COUNT(*)
                                    FROM Opportunities
                                    WHERE DateCreated >= CAST(? AS DATE)
                                    AND DateCreated <= CAST(? AS DATE)
                                    AND SalesRepId_Id = ?)
                            AS DECIMAL(10,2))
                            /
                            NULLIF(
                                (SELECT COUNT(*)
                                    FROM Activities
                                    WHERE DateCreated >= CAST(? AS DATE)
                                    AND DateCreated <= CAST(? AS DATE)
                                    AND SalesRepId_Id = ?)
                            , 0)
                        ) * 100
                    )
                AS DECIMAL(10,2))
            """

            cursor.execute(query, (
                fecha_inicio_mes, fecha_fin_mes, id_vendedor,
                fecha_inicio_mes, fecha_fin_mes, id_vendedor
            ))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error en oportunidades: {e}")
            return 0
        

    # --------------------------------------------------
    # ---------------- CANTIDADES ----------------------
    # --------------------------------------------------

    # --------------------------------------------------
    # 1. CANTIDAD DE ASISTENCIAS
    # --------------------------------------------------
    def get_cantidad_asistencia(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT COUNT(*)
                FROM Activities
                WHERE SalesRepId_Id = ?
                  AND Checkin = 1
                  AND CheckoutDate >= CAST(? AS DATE)
                  AND CheckoutDate <= CAST(? AS DATE)
            """

            cursor.execute(query, (
                id_vendedor,
                fecha_inicio_mes,
                fecha_fin_mes
            ))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error obteniendo cantidad de actividades: {e}")
            return 0
        
    # --------------------------------------------------
    # 2. COBERTURA CARTERA (CANTIDAD)
    # --------------------------------------------------
    def get_cantidad_cobertura_cartera(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT COUNT(DISTINCT act.AccountId_Value)
                FROM Activities act
                INNER JOIN Accounts acc ON acc.Id = act.AccountId_Id
                WHERE act.SalesRepId_Id = ?
                AND act.Checkin = 1
                AND act.CheckoutDate >= CAST(? AS DATE)
                AND act.CheckoutDate <= CAST(? AS DATE)
                AND acc.TypeId_Value NOT IN ('Lead')
            """

            cursor.execute(query, (
                id_vendedor,
                fecha_inicio_mes,
                fecha_fin_mes
            ))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error obteniendo cantidad cobertura cartera: {e}")
            return 0
        
    # --------------------------------------------------
    # 3. VISITAS COMERCIALES (CANTIDAD)
    # --------------------------------------------------
    def get_cantidad_visitas_comerciales(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT COUNT(id)
                FROM Activities
                WHERE CheckoutDate >= CAST(? AS DATE)
                AND CheckoutDate <= CAST(? AS DATE)
                AND SalesRepId_Id = ?
                AND TypeId_Value = 'Visita'
            """

            cursor.execute(query, (
                fecha_inicio_mes,
                fecha_fin_mes,
                id_vendedor
            ))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error obteniendo cantidad de visitas comerciales: {e}")
            return 0
        
    # --------------------------------------------------
    # 4. DEMOSTRACIONES PMX (CANTIDAD)
    # --------------------------------------------------
    def get_cantidad_demostraciones_pmx(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT COUNT(id)
                FROM Activities
                WHERE CheckoutDate >= CAST(? AS DATE)
                AND CheckoutDate <= CAST(? AS DATE)
                AND SalesRepId_Id = ?
                AND TypeId_Value IN ('Demostración PMX', 'Presentación de Propuesta')
            """

            cursor.execute(query, (
                fecha_inicio_mes,
                fecha_fin_mes,
                id_vendedor
            ))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error obteniendo cantidad de demostraciones PMX: {e}")
            return 0
        
    # --------------------------------------------------
    # 5. NUEVOS CLIENTES (CANTIDAD)
    # --------------------------------------------------
    def get_cantidad_nuevos_clientes(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT COUNT(*)
                FROM Accounts
                WHERE SalesRepId1_Id = ?
                AND DateCreated >= CAST(? AS DATE)
                AND DateCreated <= CAST(? AS DATE)
                AND TypeId_Value = 'Cliente'
            """

            cursor.execute(query, (
                id_vendedor,
                fecha_inicio_mes,
                fecha_fin_mes
            ))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error obteniendo nuevos clientes: {e}")
            return 0
        
    # --------------------------------------------------
    # 6. NUEVOS PROSPECTOS (CANTIDAD)
    # --------------------------------------------------
    def get_cantidad_nuevos_prospectos(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT COUNT(*)
                FROM Accounts
                WHERE SalesRepId1_Id = ?
                AND DateCreated >= CAST(? AS DATE)
                AND DateCreated <= CAST(? AS DATE)
                AND TypeId_Value = 'Prospecto'
            """

            cursor.execute(query, (
                id_vendedor,
                fecha_inicio_mes,
                fecha_fin_mes
            ))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error obteniendo nuevos prospectos: {e}")
            return 0

    # --------------------------------------------------
    # 7. OPORTUNIDADES (CANTIDAD)
    # --------------------------------------------------
    def get_cantidad_oportunidades(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return 0

            fecha_inicio_mes, fecha_fin_mes, _ = self._get_fecha_ref(mes_nombre, año)

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT COUNT(*)
                FROM Opportunities
                WHERE DateCreated >= CAST(? AS DATE)
                AND DateCreated <= CAST(? AS DATE)
                AND SalesRepId_Id = ?                                                     
            """

            cursor.execute(query, (
                fecha_inicio_mes,
                fecha_fin_mes,
                id_vendedor
            ))

            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row and row[0] else 0

        except Exception as e:
            st.error(f"Error obteniendo cantidad de oportunidades: {e}")
            return 0