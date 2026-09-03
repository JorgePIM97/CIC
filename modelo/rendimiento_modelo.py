# modelo/rendimiento_modelo.py
import pandas as pd
import streamlit as st
from datetime import datetime
from .db_connection import DatabaseConnection


class RendimientoModelo:
    def __init__(self):
        self.db = DatabaseConnection()

    # Columnas de monto a sumar desde PresupuestoSegmentos
    COLUMNAS_PRESUPUESTO = [
        'ConsumibleMecanizadoPlasma',
        'ConsumibleManual',
        'Refacciones',
        'ConsumibleMecanizadoLaser',
        'ConsumibleMecanizadoOxicorte',
        'SisCorteLaser',
        'SisCortePlasma',
        'SisCorteOxyWater',
        'Powermax',
    ]

    # Mapeo número -> nombre de mes (para convertir month() a texto)
    MESES_DICT = {
        1: 'Enero',    2: 'Febrero',  3: 'Marzo',
        4: 'Abril',    5: 'Mayo',     6: 'Junio',
        7: 'Julio',    8: 'Agosto',   9: 'Septiembre',
        10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }

    # Mapeo nombre de mes -> número (para filtrar rangos)
    MESES_INVERSO = {v: k for k, v in {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }.items()}

    # --------------------------------------------------------------------------
    # VENTAS
    # --------------------------------------------------------------------------

    def obtener_venta_mensual_metrica(self, vendedor, mes, año):
        """
        Obtiene el total de ventas mensuales para un vendedor específico.
        """
        try:
            conn = self.db.get_connection()
            query = """
            SELECT
                SUM(d.IngresosUSD) as Total_Venta_Mensual
            FROM dev_Detalle_Corregida d
            WHERE d.RepresentanteDeVentas = ?
            AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
            AND MONTH(d.Fecha) = ?
            AND YEAR(d.Fecha) = ?
            """
            df = pd.read_sql(query, conn, params=[vendedor, mes, año])
            conn.close()
            total_venta = df.iloc[0]['Total_Venta_Mensual'] if not df.empty else 0.0
            return float(total_venta) if total_venta is not None else 0.0
        except Exception as e:
            st.error(f"Error al obtener venta mensual: {e}")
            return 0.0

    def obtener_venta_rango_metrica(self, vendedor, fecha_inicio, fecha_fin):
        """
        Obtiene el total de ventas en un rango para un vendedor específico.
        """
        try:
            conn = self.db.get_connection()
            query = """
            SELECT
                SUM(d.IngresosUSD) as Total_Venta_Rango
            FROM dev_Detalle_Corregida d
            WHERE d.RepresentanteDeVentas = ?
            AND d.Clase != 'SERVICIOS ADMINISTRATIVOS'
            AND d.Fecha >= ?
            AND d.Fecha <= ?
            """
            df = pd.read_sql(query, conn, params=[vendedor, fecha_inicio, fecha_fin])
            conn.close()
            total_venta = df.iloc[0]['Total_Venta_Rango'] if not df.empty else 0.0
            return float(total_venta) if total_venta is not None else 0.0
        except Exception as e:
            st.error(f"Error al obtener venta rango: {e}")
            return 0.0

    # --------------------------------------------------------------------------
    # PRESUPUESTO (antes: Metas) — ahora desde PresupuestoSegmentos
    # --------------------------------------------------------------------------

    def obtener_meta_mensual_metrica(self, vendedor, mes_num, año):
        """
        Obtiene el presupuesto mensual para un vendedor desde PresupuestoSegmentos.
        Suma las columnas de segmento filtrando por NombreVendedor,
        MesPresupuesto (texto) y YearPresupuesto.

        Args:
            vendedor (str): Nombre del vendedor
            mes_num  (int): Número del mes (1-12)
            año      (int): Año

        Returns:
            float: Suma total del presupuesto del mes
        """
        try:
            mes_texto = self.MESES_DICT.get(mes_num, 'Enero')
            suma_cols = ' + '.join([
                f'ISNULL({col}, 0)' for col in self.COLUMNAS_PRESUPUESTO
            ])
            conn = self.db.get_connection()
            query = f"""
            SELECT
                SUM({suma_cols}) AS ValorPresupuesto
            FROM PresupuestoSegmentos
            WHERE NombreVendedor = ?
            AND MesPresupuesto   = ?
            AND YearPresupuesto  = ?
            """
            df = pd.read_sql(query, conn, params=[vendedor, mes_texto, año])
            conn.close()
            valor = df.iloc[0]['ValorPresupuesto'] if not df.empty else 0.0
            return float(valor) if valor is not None else 0.0
        except Exception as e:
            st.error(f"Error al obtener presupuesto mensual: {e}")
            return 0.0

    def obtener_meta_rango_metrica(self, vendedor, fecha_inicio, fecha_fin):
        """
        Obtiene el presupuesto total en un rango de fechas desde PresupuestoSegmentos.
        Suma todas las filas del vendedor cuyos MesPresupuesto/YearPresupuesto
        caen dentro del rango.

        Args:
            vendedor     (str):  Nombre del vendedor
            fecha_inicio (date): Fecha de inicio del rango
            fecha_fin    (date): Fecha de fin del rango

        Returns:
            float: Suma total del presupuesto en el rango
        """
        try:
            suma_cols = ' + '.join([
                f'ISNULL({col}, 0)' for col in self.COLUMNAS_PRESUPUESTO
            ])
            conn = self.db.get_connection()

            # Traemos todas las filas del vendedor para filtrar por rango en Python
            query = f"""
            SELECT
                MesPresupuesto,
                YearPresupuesto,
                ({suma_cols}) AS ValorPresupuesto
            FROM PresupuestoSegmentos
            WHERE NombreVendedor = ?
            """
            df = pd.read_sql(query, conn, params=[vendedor])
            conn.close()

            if df.empty:
                return 0.0

            suma_total = 0.0
            registros_incluidos = []

            for _, fila in df.iterrows():
                mes_num = self.MESES_INVERSO.get(fila['MesPresupuesto'], 0)
                año_meta = int(fila['YearPresupuesto'])

                if mes_num == 0:
                    continue

                fecha_meta = datetime(año_meta, mes_num, 1).date()

                if fecha_inicio <= fecha_meta <= fecha_fin:
                    valor = float(fila['ValorPresupuesto']) if fila['ValorPresupuesto'] else 0.0
                    suma_total += valor
                    registros_incluidos.append({
                        'mes': fila['MesPresupuesto'],
                        'valor': valor,
                        'fecha_meta': fecha_meta
                    })

            if registros_incluidos:
                print("Meses de presupuesto incluidos:")
                for reg in registros_incluidos:
                    print(f"  - {reg['mes']}: ${reg['valor']:,.2f}")

            return suma_total

        except Exception as e:
            import traceback
            traceback.print_exc()
            st.error(f"Error al obtener presupuesto rango: {e}")
            return 0.0

    # --------------------------------------------------------------------------
    # MÉTRICAS CONSOLIDADAS
    # --------------------------------------------------------------------------

    def obtener_metricas_rendimiento(self, vendedores, fecha_inicio, fecha_fin):
        """
        Calcula métricas de rendimiento mensual para los vendedores seleccionados.
        """
        mes_num  = fecha_inicio.month
        año      = fecha_inicio.year
        metricas_lista = []

        for vendedor in vendedores:
            venta_mensual = self.obtener_venta_mensual_metrica(vendedor, mes_num, año)
            meta_mensual  = self.obtener_meta_mensual_metrica(vendedor, mes_num, año)

            diferencia = venta_mensual - meta_mensual

            if meta_mensual > 0:
                diferencia2  = venta_mensual / meta_mensual
                cumplimiento = (venta_mensual / meta_mensual) * 100
            else:
                diferencia2  = 0
                cumplimiento = 0

            rendimiento = -1 - (-diferencia2)   # = diferencia2 - 1

            metricas_lista.append({
                'NombreVendedor':      vendedor,
                'Total_Venta_Mensual': venta_mensual,
                'ValorMeta':           meta_mensual,
                'Diferencia':          diferencia,
                'Rendimiento':         rendimiento,
                'Cumplimiento':        cumplimiento,
            })

        df_metricas = pd.DataFrame(metricas_lista)
        df_metricas = df_metricas.sort_values('Rendimiento', ascending=False).reset_index(drop=True)
        return df_metricas

    def obtener_metricas_rendimiento_rango(self, vendedores, fecha_inicio, fecha_fin):
        """
        Calcula métricas de rendimiento por rango de fechas para los vendedores seleccionados.
        """
        metricas_lista = []

        for vendedor in vendedores:
            venta_rango = self.obtener_venta_rango_metrica(vendedor, fecha_inicio, fecha_fin)
            meta_rango  = self.obtener_meta_rango_metrica(vendedor, fecha_inicio, fecha_fin)

            diferencia = venta_rango - meta_rango

            if meta_rango > 0:
                diferencia2  = venta_rango / meta_rango
                cumplimiento = (venta_rango / meta_rango) * 100
            else:
                diferencia2  = 0
                cumplimiento = 0

            rendimiento = diferencia2 - 1

            metricas_lista.append({
                'NombreVendedor':    vendedor,
                'Total_venta_rango': venta_rango,
                'ValorMeta':         meta_rango,
                'Diferencia':        diferencia,
                'Rendimiento':       rendimiento,
                'Cumplimiento':      cumplimiento,
            })

        df_metricas_rango = pd.DataFrame(metricas_lista)
        df_metricas_rango = df_metricas_rango.sort_values('Rendimiento', ascending=False).reset_index(drop=True)
        return df_metricas_rango