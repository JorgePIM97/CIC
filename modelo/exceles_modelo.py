#modelo/exceles_modelo.py
import pandas as pd
import requests
import streamlit as st
from .db_connection import DatabaseConnection
import smtplib
from email.message import EmailMessage
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import calendar
from .rendimiento_modelo import RendimientoModelo
from .ventas_reales_modelo import VentasRealesModelo
from PIL import Image as PILImage
from dotenv import load_dotenv
import os
import zipfile
from reportlab.lib.pagesizes import letter, landscape
from .reporte_pdf.servicio_cliente_modelo import ServicioClienteModelo
from .reporte_pdf.distribucion_clientes import DistribucionClienteModelo
from .reporte_pdf.tipo_clientes import TipoClientesModelo
from .resumen_movilidad_modelo import ResumenMovilidadModelo
from .kilometraje_modelo import KilometrajeModelo
from .presupuesto_modelo import PresupuestoModelo
import tempfile
import shutil

load_dotenv()

BANXICO_TOKEN = os.getenv("BANXICO")
SERIE = os.getenv("SERIE_BANXICO")  # Tipo de cambio FIX (Banxico)

def obtener_tipo_cambio(fecha: str, cache: dict) -> float:
    """
    Consulta el tipo de cambio FIX de Banxico para una fecha dada (YYYY-MM-DD).
    Usa un diccionario cache para no repetir consultas.
    """
    if fecha in cache:
        return cache[fecha]

    url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{SERIE}/datos/{fecha}/{fecha}?token={BANXICO_TOKEN}"
    try:
        resp = requests.get(url).json()
        valor = float(resp["bmx"]["series"][0]["datos"][0]["dato"])
        cache[fecha] = valor
        return valor
    except Exception as e:
        print(f"Error obteniendo tipo de cambio para {fecha}: {e}")
        cache[fecha] = None
        return None

class ExcelesModelo:
    def __init__(self):
        self.db = DatabaseConnection()
        self.rendimiento_modelo = RendimientoModelo()
        self.ventas_reales_modelo = VentasRealesModelo()
        self.servicio_cliente = ServicioClienteModelo()
        self.distribucion_cliente = DistribucionClienteModelo()
        self.tipo_clientes = TipoClientesModelo()
        self.resumen_movilidad = ResumenMovilidadModelo()
        self.kilometraje_modelo = KilometrajeModelo()
        self.presupuesto_modelo = PresupuestoModelo()
        
        # Mapeo de columnas Excel a columnas de base de datos
        self.mapeo_columnas = {
            "Cliente/Trabajo: Nombre (agrupado)": "NombreCliente",
            "Clase: Nombre (agrupado)": "Clase",
            "Descripción": "Descripcion",
            "Artículo": "Articulo",
            "Tipo": "Tipo",
            "Número de documento": "NumeroDeDocumento",
            "Fecha": "Fecha",
            "Cant. vendida": "CantidadVendida",
            "Precio de venta": "PrecioDeVenta",
            "Ingresos": "Ingresos",
            "Números de serie": "NumerosDeSerie",
            "Representante de ventas principal: Nombre": "RepresentanteDeVentas",
            "Cliente/proyecto: ID_Cliente_FM": "Id_Cliente_FM",
            "Cliente/proyecto: RFC": "Cliente_RFC",
            "Moneda: Símbolo de moneda": "Moneda",
            "Importe (moneda extranjera)": "Importe",
            "Tipo de cambio": "TipoDeCambio",
            "Precio unitario de cambio": "PrecioUnitario",
            "Representante de ventas principal: ID_Vendedor_FM": "Id_Vendedor_FM",
            "Estado de la transacción: Descripción": "EstadoTransaccion"
        }

    def mapear_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mapea las columnas del Excel a los nombres de columnas de la base de datos
        """
        try:
            df_mapeado = df.copy()
            df_mapeado.rename(columns=self.mapeo_columnas, inplace=True)
            
            columnas_encontradas = [col_bd for col_excel, col_bd in self.mapeo_columnas.items() 
                                   if col_excel in df.columns]
            
            columnas_faltantes = [col_bd for col_excel, col_bd in self.mapeo_columnas.items() 
                                 if col_excel not in df.columns]
            
            if columnas_faltantes:
                st.info(f"ℹ️ Columnas no encontradas en el Excel: {', '.join(columnas_faltantes)}")
            
            # if columnas_encontradas:
            #     st.success(f"✅ Columnas mapeadas correctamente: {len(columnas_encontradas)}")
            
            return df_mapeado
            
        except Exception as e:
            st.error(f"Error al mapear columnas: {e}")
            return df

    def obtener_meses_años_existentes(self):
        """Obtiene los meses y años que ya existen en la base de datos"""
        query = """
        SELECT DISTINCT 
            YEAR(Fecha) AS Año, 
            MONTH(Fecha) AS Mes
        FROM dev_Detalle_Corregida
        WHERE Fecha IS NOT NULL
        ORDER BY Año DESC, Mes DESC
        """
        try:
            conn = self.db.get_connection()
            df_existentes = pd.read_sql_query(query, conn)
            conn.close()
            
            if df_existentes.empty:
                return pd.DataFrame(columns=['Año', 'Mes'])
            
            df_existentes['Año'] = df_existentes['Año'].astype(int)
            df_existentes['Mes'] = df_existentes['Mes'].astype(int)
            
            return df_existentes
            
        except Exception as e:
            st.error(f"Error al consultar fechas existentes: {e}")
            return pd.DataFrame(columns=['Año', 'Mes'])

    def validar_fechas_duplicadas(self, df_excel):
        """
        Valida si las fechas del Excel ya existen en la base de datos (por mes y año)
        """
        try:
            if df_excel.empty:
                st.error("El archivo Excel está vacío")
                return True, pd.DataFrame(), pd.DataFrame()
            
            if 'Fecha' not in df_excel.columns:
                st.error("El archivo Excel no contiene la columna 'Fecha'")
                return True, pd.DataFrame(), pd.DataFrame()
            
            df_trabajo = df_excel.copy()
            df_trabajo['Fecha'] = pd.to_datetime(df_trabajo['Fecha'], errors='coerce')
            
            fechas_invalidas = df_trabajo['Fecha'].isnull().sum()
            if fechas_invalidas > 0:
                st.warning(f"Se encontraron {fechas_invalidas} fechas inválidas que serán ignoradas")
            
            df_trabajo = df_trabajo[df_trabajo['Fecha'].notna()]
            
            if df_trabajo.empty:
                st.error("No se encontraron fechas válidas en el archivo")
                return True, pd.DataFrame(), pd.DataFrame()
            
            df_trabajo['Año'] = df_trabajo['Fecha'].dt.year
            df_trabajo['Mes'] = df_trabajo['Fecha'].dt.month
            
            meses_años_excel = df_trabajo[['Año', 'Mes']].drop_duplicates()
            meses_años_excel['Año'] = meses_años_excel['Año'].astype(int)
            meses_años_excel['Mes'] = meses_años_excel['Mes'].astype(int)
            
            meses_años_existentes = self.obtener_meses_años_existentes()
            
            if meses_años_existentes.empty:
                return False, pd.DataFrame(), meses_años_excel
            
            duplicados = pd.merge(
                meses_años_excel, 
                meses_años_existentes, 
                on=['Año', 'Mes'], 
                how='inner'
            )
            
            hay_duplicados = not duplicados.empty
            
            return hay_duplicados, duplicados, meses_años_excel
            
        except Exception as e:
            st.error(f"Error al validar fechas duplicadas: {e}")
            import traceback
            st.error(f"Detalle del error: {traceback.format_exc()}")
            return True, pd.DataFrame(), pd.DataFrame()

    def insertar_detalles(self, df: pd.DataFrame, archivo_pdf):
        """Inserta los valores del DataFrame en la tabla dev_Detalle_Corregida"""
        
        try:
            if df.empty:
                st.error("❌ El archivo está vacío")
                return
            
            # st.info("🔄 Mapeando columnas del Excel...")
            df_mapeado = self.mapear_columnas(df)
            
            columnas_requeridas = ['Fecha', 'NombreCliente', 'RepresentanteDeVentas']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df_mapeado.columns]
            if columnas_faltantes:
                st.error(f"❌ Faltan columnas requeridas: {', '.join(columnas_faltantes)}")
                return
            
            # Construir meses_años_excel directamente desde el DataFrame sin validar duplicados
            df_mapeado["Fecha"] = pd.to_datetime(df_mapeado["Fecha"], errors='coerce')
            meses_años_excel = (
                df_mapeado[df_mapeado["Fecha"].notna()]
                .assign(
                    Mes=lambda x: x["Fecha"].dt.month,
                    Año=lambda x: x["Fecha"].dt.year
                )
                [["Mes", "Año"]]
                .drop_duplicates()
                .reset_index(drop=True)
            )
            

            # Construir meses_años_excel directamente desde el DataFrame sin validar duplicados
            df_mapeado["Fecha"] = pd.to_datetime(df_mapeado["Fecha"], errors='coerce')
            meses_años_excel = (
                df_mapeado[df_mapeado["Fecha"].notna()]
                .assign(
                    Mes=lambda x: x["Fecha"].dt.month,
                    Año=lambda x: x["Fecha"].dt.year
                )
                [["Mes", "Año"]]
                .drop_duplicates()
                .reset_index(drop=True)
            )
            
            # st.success("✅ **Validación exitosa:** No se detectaron fechas duplicadas. Procediendo con la carga...")
            
            if not meses_años_excel.empty:
                meses_años_display = meses_años_excel.copy()
                meses_años_display['Mes_Nombre'] = meses_años_display['Mes'].map({
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                })
                
                st.info("📅 **Períodos que se cargarán:**")
                meses_ordenados = meses_años_display.sort_values(['Año', 'Mes'])
                st.dataframe(
                    meses_ordenados[['Mes_Nombre', 'Año']],
                    column_config={
                        'Mes_Nombre': 'Mes',
                        'Año': 'Año'
                    },
                    hide_index=True
                )
            
            df_trabajo = df_mapeado.copy()
            
            # st.info("🔧 Procesando columnas numéricas...")
            
            columnas_numericas = {
                "CantidadVendida": 0,
                "PrecioDeVenta": 0,
                "Ingresos": 0,
                "Importe": 0,
                "Id_Cliente_FM": 0,
                "TipoDeCambio": 1,
                "PrecioUnitario": 0,
                "Id_Vendedor_FM": 0
            }
            
            for columna, valor_defecto in columnas_numericas.items():
                if columna in df_trabajo.columns:
                    df_trabajo[columna] = pd.to_numeric(df_trabajo[columna], errors="coerce").fillna(valor_defecto)
                else:
                    df_trabajo[columna] = valor_defecto
            
            # st.info("📅 Procesando fechas...")
            df_trabajo["Fecha"] = pd.to_datetime(df_trabajo["Fecha"], errors='coerce')
            df_trabajo = df_trabajo[df_trabajo["Fecha"].notna()]
            df_trabajo["Fecha"] = df_trabajo["Fecha"].dt.strftime("%Y-%m-%d")
            
            df_trabajo["TipoDeCambioUSD"] = None
            df_trabajo["IngresosUSD"] = None

            cache_tc = {}
            total_rows = len(df_trabajo)
            
            if total_rows == 0:
                st.error("❌ No hay registros válidos para procesar")
                return

            # st.info(f"💱 Procesando tipos de cambio para {total_rows:,} registros...")
            
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            for i, row in df_trabajo.iterrows():
                if i % 100 == 0 or i == total_rows - 1:
                    progress = (i + 1) / total_rows
                    progress_bar.progress(progress)
                    progress_text.text(f"Procesando tipos de cambio... {i+1:,}/{total_rows:,}")
                
                if pd.isna(row.get("Moneda")):
                    continue
                    
                if str(row["Moneda"]).upper() == "MXN":
                    tc = obtener_tipo_cambio(row["Fecha"], cache_tc)
                    if tc:
                        df_trabajo.at[i, "TipoDeCambioUSD"] = tc
                        if pd.notna(row["Ingresos"]) and row["Ingresos"] != 0:
                            df_trabajo.at[i, "IngresosUSD"] = row["Ingresos"] / tc
                elif str(row["Moneda"]).upper() == "USD":
                    df_trabajo.at[i, "IngresosUSD"] = row.get("Importe", 0)

            progress_bar.empty()
            progress_text.empty()
            # st.success("✅ Tipos de cambio procesados correctamente")

            # st.info("💾 Insertando registros en la base de datos...")

            conn = self.db.get_connection()
            cursor = conn.cursor()

            progress_bar_insert = st.progress(0)
            progress_text_insert = st.empty()
            registros_insertados = 0

            for idx, row in df_trabajo.iterrows():
                try:
                    if idx % 50 == 0 or idx == len(df_trabajo) - 1:
                        progress = (idx + 1) / total_rows
                        progress_bar_insert.progress(progress)
                        progress_text_insert.text(f"Insertando registros... {idx+1:,}/{total_rows:,}")
                    
                    row_clean = row.where(pd.notnull(row), None)

                    cursor.execute("""
                        INSERT INTO dev_Detalle_Corregida (
                            NombreCliente, Clase, Descripcion, Articulo, Tipo,
                            NumeroDeDocumento, Fecha, CantidadVendida,
                            PrecioDeVenta, Ingresos, NumerosDeSerie, RepresentanteDeVentas,
                            Id_Cliente_FM, Cliente_RFC, Moneda, Importe, TipoDeCambio, PrecioUnitario,
                            Id_Vendedor_FM, TipoDeCambioUSD, IngresosUSD, EstadoTransaccion
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row_clean.get("NombreCliente"),
                        row_clean.get("Clase"),
                        row_clean.get("Descripcion"),
                        row_clean.get("Articulo"),
                        row_clean.get("Tipo"),
                        row_clean.get("NumeroDeDocumento"),
                        row_clean.get("Fecha"),
                        float(row_clean["CantidadVendida"]) if row_clean["CantidadVendida"] is not None else None,
                        float(row_clean["PrecioDeVenta"]) if row_clean["PrecioDeVenta"] is not None else None,
                        float(row_clean["Ingresos"]) if row_clean["Ingresos"] is not None else None,
                        row_clean.get("NumerosDeSerie"),
                        row_clean.get("RepresentanteDeVentas"),
                        float(row_clean["Id_Cliente_FM"]) if row_clean["Id_Cliente_FM"] is not None else None,
                        row_clean.get("Cliente_RFC"),
                        row_clean.get("Moneda"),
                        float(row_clean["Importe"]) if row_clean["Importe"] is not None else None,
                        float(row_clean["TipoDeCambio"]) if row_clean["TipoDeCambio"] is not None else None,
                        float(row_clean["PrecioUnitario"]) if row_clean["PrecioUnitario"] is not None else None,
                        float(row_clean["Id_Vendedor_FM"]) if row_clean["Id_Vendedor_FM"] is not None else None,
                        float(row_clean["TipoDeCambioUSD"]) if row_clean["TipoDeCambioUSD"] is not None else None,
                        float(row_clean["IngresosUSD"]) if row_clean["IngresosUSD"] is not None else None,
                        row_clean.get("EstadoTransaccion")
                    ))
                    registros_insertados += 1
                    
                except Exception as e:
                    st.warning(f"Error al insertar registro {idx}: {e}")
                    continue

            progress_bar_insert.empty()
            progress_text_insert.empty()

            conn.commit()
            conn.close()
            
            # st.success(f"✅ **¡Proceso completado exitosamente!**")
            # st.success(f"✅ **Registros insertados:** {registros_insertados:,} de {total_rows:,}")
            
            if registros_insertados < total_rows:
                st.warning(f"⚠️ Se omitieron {total_rows - registros_insertados:,} registros debido a errores")

            # Construir información de períodos para reportes
            periodos_info = []
            if not meses_ordenados.empty:
                for _, row in meses_ordenados.iterrows():
                    periodos_info.append({
                        'mes': row['Mes'],
                        'año': row['Año'],
                        'mes_nombre': row['Mes_Nombre']
                    })
                
                # Texto para correo general
                periodos_texto = []
                for año, grupo in meses_ordenados.groupby('Año'):
                    meses_lista = grupo['Mes_Nombre'].tolist()
                    if len(meses_lista) > 1:
                        meses_texto = ', '.join(meses_lista[:-1]) + f" y {meses_lista[-1]}"
                    else:
                        meses_texto = meses_lista[0]
                    periodo_texto = f"{meses_texto} del año {año}"
                    periodos_texto.append(periodo_texto)
                periodo_final = ' y '.join(periodos_texto)
            else:
                periodo_final = "sin periodo definido"

            self.enviar_correos(archivo_pdf, periodo_final)

            # Generar reportes PDF
            self.enviar_correo_reportes_pdf(periodos_info)

        except Exception as e:
            st.error(f"❌ Error general en el proceso: {e}")
            import traceback
            st.error(f"Detalle del error: {traceback.format_exc()}")

    def obtener_vendedores_validos(self):
        """Obtiene vendedores con Id_Vendedor_FM válido que existe en Users"""
        query = """
        SELECT DISTINCT 
            d.RepresentanteDeVentas,
            d.Id_Vendedor_FM
        FROM dev_Detalle_Corregida d
        INNER JOIN Users u ON d.Id_Vendedor_FM = u.Id
        WHERE d.Id_Vendedor_FM IS NOT NULL
        AND d.RepresentanteDeVentas IS NOT NULL
        ORDER BY d.RepresentanteDeVentas
        """
        try:
            conn = self.db.get_connection()
            df_vendedores = pd.read_sql_query(query, conn)
            conn.close()
            return df_vendedores
        except Exception as e:
            st.error(f"Error al obtener vendedores: {e}")
            return pd.DataFrame()

    def obtener_datos_vendedor_periodo(self, vendedor, mes, año):
        """Obtiene datos de ventas de un vendedor para un período específico"""
        query = """
        SELECT 
            NombreCliente,
            Clase,
            Descripcion,
            Fecha,
            IngresosUSD,
            Moneda
        FROM dev_Detalle_Corregida
        WHERE RepresentanteDeVentas = ?
        AND MONTH(Fecha) = ?
        AND YEAR(Fecha) = ?
        AND IngresosUSD IS NOT NULL
        """
        try:
            conn = self.db.get_connection()
            df_datos = pd.read_sql_query(query, conn, params=(vendedor, mes, año))
            conn.close()
            return df_datos
        except Exception as e:
            print(f"Error al obtener datos del vendedor: {e}")
            return pd.DataFrame()
        
    def obtener_todos_los_detalles(self):
        """Obtiene todos los registros de dev_Detalle_Corregida para visualización"""
        query = """
        SELECT
            RepresentanteDeVentas,
            YEAR(Fecha)  AS Año,
            MONTH(Fecha) AS Mes,
            NombreCliente,
            Clase,
            Descripcion,
            Articulo,
            Fecha,
            CantidadVendida,
            PrecioDeVenta,
            Ingresos,
            IngresosUSD,
            Moneda
        FROM dev_Detalle_Corregida
        ORDER BY Fecha DESC
        """
        try:
            conn = self.db.get_connection()
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error al obtener detalles: {e}")
            return pd.DataFrame()

    def obtener_meta_vendedor(self, vendedor, mes_nombre, año):
        """
        Obtiene la meta mensual para un vendedor específico
        
        Args:
            vendedor (str): Nombre del vendedor
            mes (str): Nombre del mes (ej: 'Julio')
            año (int): Año
        
        Returns:
            float: Valor de la meta mensual
        """
        try:
            conn = self.db.get_connection()
            
            query = """
            SELECT ValorMeta 
            FROM Metas
            WHERE NombreVendedor = ?
            AND MesMeta = ? 
            AND YEAR(FechaRegistro) = ?
            """
            
            df = pd.read_sql(query, conn, params=[vendedor, mes_nombre, año])
            conn.close()
            
            valor_meta = df.iloc[0]['ValorMeta'] if not df.empty else 0.0
            return float(valor_meta) if valor_meta is not None else 0.0
            
        except Exception as e:
            st.error(f"Error al obtener meta mensual: {e}")
            return 0.0


    def generar_grafica_lineas_mensual(self, vendedor, año):
        """Genera gráfica de líneas de ventas mensuales del año"""
        query = """
        SELECT 
            MONTH(Fecha) as Mes,
            SUM(IngresosUSD) as TotalVentas
        FROM dev_Detalle_Corregida
        WHERE RepresentanteDeVentas = ?
        AND YEAR(Fecha) = ?
        AND IngresosUSD IS NOT NULL
        GROUP BY MONTH(Fecha)
        ORDER BY MONTH(Fecha)
        """
        try:
            conn = self.db.get_connection()
            df_mensual = pd.read_sql_query(query, conn, params=(vendedor, año))
            conn.close()
            
            total_meta_anual = self.ventas_reales_modelo.obtener_meta_por_vendedor_reporte(vendedor, año)

            if df_mensual.empty:
                return None
            
            # Completar todos los meses
            todos_meses = pd.DataFrame({'Mes': range(1, 13)})
            df_completo = todos_meses.merge(df_mensual, on='Mes', how='left')
            df_completo['TotalVentas'] = df_completo['TotalVentas'].fillna(0)
            
            nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            
            fig = go.Figure()
            
            # Línea de ventas mensuales
            fig.add_trace(go.Scatter(
                x=nombres_meses,
                y=df_completo['TotalVentas'],
                mode='lines+markers',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8, color='#1f77b4'),
                name='Ventas Mensuales'
            ))
            
            # Línea de meta anual (horizontal)
            if total_meta_anual and total_meta_anual > 0:
                meta_mensual = total_meta_anual / 12
                fig.add_trace(go.Scatter(
                    x=nombres_meses,
                    y=[meta_mensual] * 12,
                    mode='lines',
                    line=dict(color='#911218', width=2, dash='dash'),
                    name=f'Meta Mensual (${meta_mensual:,.0f})'
                ))
            
            fig.update_layout(
                title=dict(
                    text=f'Ventas Mensuales - {año}',
                    font=dict(size=18, color='#000000')
                ),
                xaxis_title=dict(
                    text='Mes',
                    font=dict(color='#000000', size=12)
                ),
                yaxis_title=dict(
                    text='Ventas ($USD)',
                    font=dict(color='#000000', size=12)
                ),
                height=450,
                template='plotly_white',
                margin=dict(l=90, r=40, t=80, b=70),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(color='#000000', size=11)
                ),
                xaxis=dict(
                    tickfont=dict(color='#000000', size=11),
                    gridcolor='#E5E5E5'
                ),
                yaxis=dict(
                    tickfont=dict(color='#000000', size=11),
                    gridcolor='#E5E5E5',
                    tickformat='$,.0f'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error al generar gráfica de líneas: {e}")
            return None

    def generar_grafica_barras_meta(self, vendedor, mes, año, total_ventas, meta):
        """Genera gráfica de barras comparando ventas vs meta"""
        fig = go.Figure()
        
        # Color según cumplimiento
        if total_ventas >= meta:
            color_venta = '#A7DCA5'  # Verde
        elif total_ventas >= meta * 0.7:
            color_venta = '#A7DCA5'  # Naranja
        else:
            color_venta = '#A7DCA5'  # Rojo
        
        fig.add_trace(go.Bar(
            name='Venta Real',
            x=[vendedor],
            y=[total_ventas],
            marker_color=color_venta,
            text=[f'${total_ventas:,.0f}'],
            textposition='inside',
            textfont=dict(
                size=12  # Texto más pequeño en las barras
            
            )
        ))
        
        fig.add_trace(go.Bar(
            name='Meta',
            x=[vendedor],
            y=[meta],
            marker_color='#90D5FF',
            text=[f'${meta:,.0f}'],
            textposition='inside',
            textfont=dict(
                size=12  # Texto más pequeño en las barras
                
            )
        ))
        
        fig.update_layout(
            # title=dict(
            #     text='Ventas vs Meta',
            #     font=dict(size=12)  # Título más pequeño y legible
            # ),
            xaxis=dict(
                title=dict(
                    text='Vendedor',
                    font=dict(size=12)  # Etiqueta eje X más pequeña
                ),
                tickfont=dict(size=12)  # Texto de ticks del eje X más pequeño
            ),
            yaxis=dict(
                title=dict(
                    text='Monto (USD)',
                    font=dict(size=12)  # Etiqueta eje Y más pequeña
                ),
                tickfont=dict(size=12)  # Texto de ticks del eje Y más pequeño
            ),
            barmode='group',
            height=400,
            font=dict(size=12),  # Tamaño de fuente general más pequeño
            legend=dict(
                font=dict(size=12),  # Leyenda más pequeña
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=50, r=50, t=60, b=50)  # Márgenes ajustados para mejor legibilidad
        )
        
        return fig

    def generar_grafica_lineas_ingresos_mensuales_fig(
        self, df_clases, vendedores_lista, año_seleccionado, mes_nombre,
        df_metas=None, df_clases_anterior=None, df_metas_anterior=None
    ):
        try:
            año_anterior = año_seleccionado - 1
            print(f"[DEBUG] vendedores_lista: {vendedores_lista}")
            print(f"[DEBUG] año_seleccionado: {año_seleccionado}, año_anterior: {año_anterior}")

            placeholders = ','.join(['?'] * len(vendedores_lista))
            query_ingresos = f"""
                SELECT Fecha, IngresosUSD
                FROM dev_Detalle_Corregida
                WHERE RepresentanteDeVentas IN ({placeholders})
                AND YEAR(Fecha) IN (?, ?)
                AND IngresosUSD IS NOT NULL
            """
            conn = self.db.get_connection()
            df_raw = pd.read_sql_query(
                query_ingresos, conn,
                params=(*vendedores_lista, año_seleccionado, año_anterior)
            )
            conn.close()
            print(f"[DEBUG] df_raw shape: {df_raw.shape}")
            print(f"[DEBUG] df_raw head:\n{df_raw.head()}")

            if df_raw.empty:
                print("[DEBUG] df_raw está vacío, retornando None")
                return None

            df_raw['Fecha'] = pd.to_datetime(df_raw['Fecha'])
            df_clases          = df_raw[df_raw['Fecha'].dt.year == año_seleccionado].copy()
            df_clases_anterior = df_raw[df_raw['Fecha'].dt.year == año_anterior].copy()

            # ── Consulta presupuesto por segmentos ──
            query_metas = f"""
                SELECT [ConsumibleMecanizadoPlasma]
                    ,[ConsumibleManual]
                    ,[Refacciones]
                    ,[ConsumibleMecanizadoLaser]
                    ,[ConsumibleMecanizadoOxicorte]
                    ,[MesPresupuesto]
                    ,[YearPresupuesto]
                    ,[SisCorteLaser]
                    ,[SisCortePlasma]
                    ,[SisCorteOxyWater]
                    ,[Powermax]
                    ,[Robotica]
                FROM PresupuestoSegmentos
                WHERE NombreVendedor IN ({placeholders})
                AND YearPresupuesto IN (?, ?)
            """
            conn = self.db.get_connection()
            df_metas_raw = pd.read_sql_query(
                query_metas, conn,
                params=(*vendedores_lista, año_seleccionado, año_anterior)
            )
            conn.close()

            # Calcular total del presupuesto sumando todas las columnas de segmentos
            cols_segmentos = [
                'ConsumibleMecanizadoPlasma', 
                'ConsumibleManual', 
                'Refacciones',
                'ConsumibleMecanizadoLaser', 
                'ConsumibleMecanizadoOxicorte',
                'SisCorteLaser',
                'SisCortePlasma',
                'SisCorteOxyWater',
                'Powermax',
                'Robotica'
            ]

            if not df_metas_raw.empty:
                df_metas_raw[cols_segmentos] = df_metas_raw[cols_segmentos].fillna(0)
                df_metas_raw['ValorMeta'] = df_metas_raw[cols_segmentos].sum(axis=1)
                # Renombrar columna de mes para compatibilidad con agrupar_metas
                df_metas_raw = df_metas_raw.rename(columns={
                    'MesPresupuesto': 'MesMeta',
                    'YearPresupuesto': 'YearMeta'
                })
                df_metas          = df_metas_raw[df_metas_raw['YearMeta'] == año_seleccionado].copy()
                df_metas_anterior = df_metas_raw[df_metas_raw['YearMeta'] == año_anterior].copy()

            # ── Helpers ──
            todos_los_meses = pd.DataFrame({'Mes': range(1, 13)})
            nombres_meses   = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
            meses_map = {
                'ENERO':1,'FEBRERO':2,'MARZO':3,'ABRIL':4,'MAYO':5,'JUNIO':6,
                'JULIO':7,'AGOSTO':8,'SEPTIEMBRE':9,'OCTUBRE':10,'NOVIEMBRE':11,'DICIEMBRE':12
            }

            def agrupar_ingresos(df):
                if df is None or df.empty:
                    return todos_los_meses.assign(IngresosUSD=0)
                if not pd.api.types.is_datetime64_any_dtype(df['Fecha']):
                    df = df.copy()
                    df['Fecha'] = pd.to_datetime(df['Fecha'])
                df = df.copy()
                df['Mes'] = df['Fecha'].dt.month
                agrupado = df.groupby('Mes')['IngresosUSD'].sum().reset_index()
                return todos_los_meses.merge(agrupado, on='Mes', how='left').fillna({'IngresosUSD': 0})
            
            def agrupar_metas(df_m):
                if df_m is None or df_m.empty:
                    return None
                df_m = df_m.copy()
                df_m['MesNumero'] = df_m['MesMeta'].str.upper().map(meses_map)
                metas_mes = df_m.groupby('MesNumero')['ValorMeta'].sum().reset_index()
                metas_mes.columns = ['Mes', 'Meta']
                return todos_los_meses.merge(metas_mes, on='Mes', how='left').fillna({'Meta': 0})

            ingresos_actual   = agrupar_ingresos(df_clases)
            ingresos_anterior = agrupar_ingresos(df_clases_anterior)
            metas_actual      = agrupar_metas(df_metas)
            metas_ant         = agrupar_metas(df_metas_anterior)
            hay_anterior      = df_clases_anterior is not None and not df_clases_anterior.empty

            # ── Figura ──
            fig = go.Figure()

            if hay_anterior:
                # fig.add_trace(go.Bar(
                #     x=nombres_meses, y=ingresos_anterior['IngresosUSD'],
                #     name=f'Ventas {año_anterior}', marker=dict(color="#E89898"),
                #     text=[f'${x:,.0f}' for x in ingresos_anterior['IngresosUSD']],
                #     textposition='outside', textfont=dict(size=10, color='black')
                # ))
                fig.add_trace(go.Bar(
                    x=nombres_meses, y=ingresos_anterior['IngresosUSD'],
                    name=f'Ventas {año_anterior}', marker=dict(color="#bababa"),
                    text=[f'${x:,.0f}' for x in ingresos_anterior['IngresosUSD']],
                    textposition='inside',
                    textangle=-90,
                    textfont=dict(size=11, color='white', family='Arial Black'),
                    insidetextanchor='middle',
                ))

            fig.add_trace(go.Bar(
                x=nombres_meses, y=ingresos_actual['IngresosUSD'],
                name=f'Ventas {año_seleccionado}', marker=dict(color="#16a0e6"),
                text=[f'${x:,.0f}' for x in ingresos_actual['IngresosUSD']],
                textposition='inside',
                textangle=-90,
                textfont=dict(size=11, color='white', family='Arial Black'),
                insidetextanchor='middle',
            ))

            if metas_actual is not None:
                fig.add_trace(go.Scatter(
                    x=nombres_meses, y=metas_actual['Meta'],
                    mode='lines+markers', line=dict(color="#196cb1", width=3, dash='dash'),
                    marker=dict(size=8, color='#196cb1', symbol='diamond'),
                    text=[f'${x:,.0f}' for x in metas_actual['Meta']],
                    textposition='bottom center', textfont=dict(size=10, color='#196cb1'),
                    name=f'Presupuesto {año_seleccionado}'
                ))

            if len(vendedores_lista) == 1:
                titulo_vendedores = vendedores_lista[0]
            elif len(vendedores_lista) <= 3:
                titulo_vendedores = ", ".join(vendedores_lista)
            else:
                titulo_vendedores = f"{len(vendedores_lista)} Vendedores"

            fig.update_layout(
                title=dict(
                    text=f'Comprativo de Ventas Mensuales — {titulo_vendedores} {mes_nombre} {año_seleccionado}',
                    font=dict(size=20, color='black', family="Arial Black"),
                    y=0.98,
                    yanchor='top'
                ),
                xaxis_title=dict(text='Mes',
                                font=dict(size=18, color='black', family="Arial Black")),
                yaxis_title=dict(text='Venta ($USD)',
                                font=dict(size=18, color='black', family="Arial Black")),
                barmode='group',
                showlegend=True,
                legend=dict(orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1,
                            font=dict(size=16)),
                height=450, template='plotly_white',
                xaxis=dict(tickmode='array',
                        tickvals=list(range(12)),
                        ticktext=nombres_meses,
                        tickfont=dict(size=16, color='black')
                        ),
                yaxis=dict(tickformat='$,.0f',
                        gridcolor='lightgray',
                        tickfont=dict(size=16, color='black')
                        ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=90, r=40, t=95, b=95)
            )

            return fig

        except Exception as e:
            print(f"Error al generar gráfica de líneas para PDF: {e}")
            return None

    # ── helper reutilizable ──────────────────────────────────────────────────────
    def _calcular_margenes_pastel(self, n_elementos: int) -> dict:
        """
        Devuelve márgenes proporcionales al número de slices.
        - Pocos datos  → margen pequeño  → gráfico grande
        - Muchos datos → margen grande   → etiquetas no se empalman
        """
        margen_base   = 40          # mínimo siempre presente
        extra_por_item = 6         # píxeles extra por cada elemento
        margen_vertical = min(margen_base + n_elementos * extra_por_item, 180)
        return dict(l=50, r=50, t=margen_vertical, b=margen_vertical)

    def _calcular_rotacion_pastel(self, valores: list) -> float:
        """
        - Si hay un slice > 50%: se centra en la parte superior del pastel.
        - Si no:  el slice mayor se centra a la izquierda (180°) para que
                los slices pequeños queden agrupados a la derecha.
        """
        total = sum(valores)
        if total == 0:
            return 0

        porcentajes = [v / total for v in valores]
        idx_mayor = porcentajes.index(max(porcentajes))
        angulo_acumulado = sum(p * 360 for p in porcentajes[:idx_mayor])
        angulo_slice_mayor = porcentajes[idx_mayor] * 360

        if porcentajes[idx_mayor] > 0.50:
            # Centrar el slice dominante en la parte superior (90° en Plotly = arriba)
            rotacion = 90 - angulo_acumulado - (angulo_slice_mayor / 2)
        else:
            # Slices pequeños a la derecha: slice mayor centrado a la izquierda
            rotacion = 180 - angulo_acumulado - (angulo_slice_mayor / 2)

        return rotacion % 360

    def generar_grafica_pastel_categoria(self, df_datos, mes_nombre, año):
        if df_datos.empty:
            return None
        
        # Si no existe TotalIngresosUSD, lo calculamos agrupando
        if "TotalIngresosUSD" not in df_datos.columns:
            if "Clase" not in df_datos.columns or "IngresosUSD" not in df_datos.columns:
                print("Error: faltan columnas necesarias para agrupar por categoría")
                return None

            df_datos = (
                df_datos.groupby("Clase", as_index=False)
                .agg(TotalIngresosUSD=("IngresosUSD", "sum"))
                .rename(columns={"Clase": "Categoria"})
            )

        df_grafica = df_datos.copy()
        df_grafica = df_grafica.sort_values("TotalIngresosUSD", ascending=False)

        # Top 30 + Otros
        if len(df_grafica) > 30:
            top_30 = df_grafica.head(30)
            otros = pd.DataFrame({
                "Categoria": ["Otros"],
                "TotalIngresosUSD": [df_grafica.iloc[30:]["TotalIngresosUSD"].sum()]
            })
            df_final = pd.concat([top_30, otros], ignore_index=True)
        else:
            df_final = df_grafica

        # ← Inserta <br> si el label supera 30 caracteres, respetando espacios
        def wrap_label(label, max_chars=25):
            if len(label) <= max_chars:
                return label
            corte = label.rfind(' ', 0, max_chars)
            if corte == -1:
                corte = max_chars
            return label[:corte] + '<br>' + label[corte:].strip()

        df_final = df_final.copy()
        df_final["Categoria"] = df_final["Categoria"].apply(wrap_label)

        colors_pastel = [
            "#A8C8E8",  # azul cielo pastel
            "#E89898",  # rojo pastel
            "#F83939",  # guinda pastel
            "#70A4DB",  # azul marino pastel
            "#333333",  # gris oscuro
            "#BBBBBB",  # gris claro
        ]
        colors_palette = colors_pastel[:len(df_final)]

        valores = df_final["TotalIngresosUSD"].tolist()
        rotacion = self._calcular_rotacion_pastel(valores)

        fig = go.Figure(data=[
            go.Pie(
                labels=df_final["Categoria"],
                values=valores,
                hole=0.3,
                marker=dict(colors=colors_palette),
                # ← Incluye label + porcentaje + valor en cada slice
                textinfo="label+percent+value",
                texttemplate="<b>%{label}</b><br>%{percent}<br>$%{value:,.0f}",
                textposition="outside",
                textfont=dict(size=14, color="black", family="Arial Black"),
                rotation=rotacion
            )
        ])

        fig.update_layout(
            title=dict(
                text=f'Participación de Ventas Mensual - {mes_nombre} {año}',
                font=dict(size=18, weight='bold', color='black'),
                y=0.98,
                yanchor='top'
            ),
            # ← Leyenda desactivada: la info ya está en cada rebanada
            showlegend=False,
            height=500,
            width=600,
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            # ← Márgenes amplios para que las etiquetas externas no se corten
            margin=dict(l=120, r=120, t=100, b=100),
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        return fig

    def generar_grafica_pastel_top_clientes(self, vendedor, mes_nombre, año):
            """
            Genera gráfica de pastel con top 5 clientes + 'Otros' para el PDF
            """
            try:
                df = self.ventas_reales_modelo.obtener_clientes_ingresos_vendedor_reporte(vendedor, mes_nombre, año)
                if df is None or df.empty:
                    return None

                df_agrupado = df.groupby('NombreCliente').agg({'ingresos_fact': 'sum'}).reset_index()
                df_ordenado = df_agrupado.sort_values('ingresos_fact', ascending=False)

                top_5 = df_ordenado.head(5).copy()
                otros_ingresos = df_ordenado.iloc[5:]['ingresos_fact'].sum()

                if otros_ingresos > 0:
                    otros_row = pd.DataFrame({'NombreCliente': ['Otros'], 'ingresos_fact': [otros_ingresos]})
                    df_grafica = pd.concat([top_5, otros_row], ignore_index=True)
                else:
                    df_grafica = top_5

                # ← Omite los primeros 9 caracteres del nombre; "Otros" se deja intacto
                df_grafica['LabelCorto'] = df_grafica['NombreCliente'].apply(
                    lambda x: x[9:] if len(x) > 9 else x
                )

                # ← Inserta <br> si el label supera 35 caracteres, respetando espacios
                def wrap_label(label, max_chars=25):
                    if len(label) <= max_chars:
                        return label
                    corte = label.rfind(' ', 0, max_chars)
                    if corte == -1:
                        corte = max_chars
                    return label[:corte] + '<br>' + label[corte:].strip()

                df_grafica['LabelCorto'] = df_grafica['LabelCorto'].apply(wrap_label)

                colores_paleta = [
                    "#A8C8E8",  # azul cielo pastel
                    "#E89898",  # rojo pastel
                    "#F83939",  # guinda pastel
                    "#70A4DB",  # azul marino pastel
                    "#333333",  # gris oscuro
                    "#BBBBBB",  # gris claro
                ]
                colores = colores_paleta[:len(df_grafica)]

                valores = df_grafica['ingresos_fact'].tolist()
                rotacion = self._calcular_rotacion_pastel(valores)

                fig = go.Figure(data=[
                    go.Pie(
                        labels=df_grafica['LabelCorto'],
                        values=valores,
                        hole=0.3,
                        marker=dict(colors=colores),
                        textinfo="label+percent+value",
                        texttemplate="<b>%{label}</b><br>%{percent}<br>$%{value:,.0f}",
                        textposition='outside',
                        textfont=dict(size=14, color="black", family="Arial Black"),
                        rotation=rotacion
                    )
                ])

                fig.update_layout(
                    title=dict(
                        text=f'Participación Ventas por Cliente - {mes_nombre} {año}',
                        font=dict(size=18, weight='bold', color='black'),
                        y=0.98,
                        yanchor='top'
                    ),
                    showlegend=False,
                    height=600,
                    width=700,
                    uniformtext_minsize=10,
                    uniformtext_mode='hide',
                    margin=dict(l=120, r=120, t=100, b=100),
                    paper_bgcolor="white",
                    plot_bgcolor="white"
                )

                return fig
            except Exception as e:
                print(f"Error al generar gráfica pastel clientes: {e}")
                return None
        
    def generar_grafica_pastel_distribucion_clientes(self, vendedor, mes_nombre, año):
        """
        Genera gráfica de pastel con Activos y Nuevos clientes para el PDF
        """
        try:
            df = self.distribucion_cliente.get_distribucion_clientes(vendedor, mes_nombre, año)
            if df is None or df.empty:
                return None

            categorias = ['Atendidos', 'Fuera de Cobertura']
            valores    = [df['Atendidos'].iloc[0], df['Fuera de Cobertura'].iloc[0]]

            colores_paleta = [
            "#A8C8E8",  # azul cielo pastel
            "#E89898",  # rojo pastel
            "#F83939",  # guinda pastel
            
            "#70A4DB",  # azul marino pastel
            "#333333",  # gris claro pastel
            "#BBBBBB",  # rojo pastel
            ]
            # colores    = px.colors.qualitative.Set3[:2]
            colores = colores_paleta[:2]

            fig = go.Figure(data=[
                go.Pie(
                    labels=categorias,
                    values=valores,
                    hole=0.3,
                    marker=dict(colors=colores),
                    textinfo='percent+value',
                    textposition='outside',
                    textfont=dict(size=14, color='black', family='Arial Black')
                )
            ])

            fig.update_layout(
                title=dict(
                    text=f'Cobertura de la Cartera - {mes_nombre} {año}',
                    font=dict(size=18, weight='bold', color='black'),
                    y=0.96,
                    yanchor='top'
                ),
                showlegend=True,
                height=530,           # ← más alto para respirar
                width=550,
                legend=dict(
                    orientation='h',
                    yanchor='top',
                    y=-0.40,
                    xanchor='center',
                    x=0.5,
                    font=dict(size=16)
                ),
                uniformtext_minsize=12,
                uniformtext_mode='show',
                margin=dict(l=50, r=50, t=100, b=80),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            return fig

        except Exception as e:
            print(f"Error al generar gráfica pastel distribución clientes: {e}")
            return None
        
    def generar_grafica_pastel_actividad_tipo_cliente(self, vendedor, año, mes_nombre):
        """
        Genera gráfica de pastel con actividad por tipo de cliente para el PDF
        """
        try:
            df = self.tipo_clientes.get_actividad_tipo_cliente(vendedor, año)
            if df is None or df.empty:
                return None

            colores_paleta = [
            "#A8C8E8",  # azul cielo pastel
            "#E89898",  # rojo pastel
            "#F83939",  # guinda pastel
            
            "#70A4DB",  # azul marino pastel
            "#333333",  # gris claro pastel
            "#BBBBBB",  # rojo pastel
            ]
            # colores = px.colors.qualitative.Set3[:len(df)]
            colores = colores_paleta[:len(df)]

            fig = go.Figure(data=[
                go.Pie(
                    labels=df['TipoAgrupado'],
                    values=df['Cantidad'],
                    hole=0.3,
                    marker=dict(colors=colores),
                    textinfo='percent',
                    textposition='outside',
                    textfont=dict(size=14, color='black', family='Arial Black')
                )
            ])

            fig.update_layout(
                title=dict(
                    text=f'Distribución de Actividad por Tipo de Cliente <br>{mes_nombre} {año}',
                    font=dict(size=18, weight='bold', color='black'),
                    y=0.96,
                    yanchor='top'
                ),
                showlegend=True,
                height=480,
                width=500,
                legend=dict(
                    orientation='h',
                    yanchor='top',
                    y=-0.40,
                    xanchor='center',
                    x=0.5,
                    font=dict(size=16)
                ),
                uniformtext_minsize=12,
                uniformtext_mode='show',
                margin=dict(l=50, r=50, t=100, b=80),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            return fig

        except Exception as e:
            print(f"Error al generar gráfica pastel actividad tipo cliente: {e}")
            return None


    def generar_pdf_reporte(
        self, vendedor, mes_nombre, año, df_datos, meta,
        df_clases=None, df_metas=None,
        df_clases_anterior=None, df_metas_anterior=None
    ):
        buffer = BytesIO()
        
        PAGE = landscape(letter)
        ANCHO = PAGE[0]
        ALTO  = PAGE[1]
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=PAGE,
            topMargin=0.3*inch,
            bottomMargin=0.3*inch,
            leftMargin=0.4*inch,
            rightMargin=0.4*inch
        )
        story = []
        styles = getSampleStyleSheet()

        # --------------------------------------------------
        # 1. Título
        # --------------------------------------------------
        titulo_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'],
            fontSize=11, textColor=colors.HexColor('#000000'),
            spaceAfter=6, alignment=TA_CENTER
        )
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")

        story.append(Paragraph(
            f"Reporte de Ventas: &nbsp; {vendedor} - {mes_nombre} {año} &nbsp;&nbsp; Reporte generado el día: {fecha_hoy}",
            titulo_style
        ))

        # --------------------------------------------------
        # 2. Resumen — tabla con filas Mensual / Acumulado
        # --------------------------------------------------
        df_categoria   = self.obtener_categoria_ingresos_reporte(vendedor, mes_nombre, año)
        # total_venta_anual = self.ventas_reales_modelo.obtener_ingresos_por_vendedor_reporte(vendedor, año)
        total_venta_anual = self.ventas_reales_modelo.obtener_ingresos_por_vendedor_reporte(vendedor, año, mes_nombre)
        # total_meta_anual  = self.ventas_reales_modelo.obtener_meta_por_vendedor_reporte(vendedor, año)
        # total_meta        = self.ventas_reales_modelo.obtener_meta_mes_por_vendedor_reporte(vendedor, mes_nombre, año)
        
        total_presupuesto_mes    = self.presupuesto_modelo.obtener_total_presupuesto_mensual(vendedor, año, mes_nombre)
        total_presupuesto_acumulado = self.presupuesto_modelo.obtener_total_presupuesto_acumulado(vendedor, año, mes_nombre)

        total_ventas_valor = df_datos['IngresosUSD'].sum()
        cumplimiento_mes   = (total_ventas_valor / total_presupuesto_mes) * 100 if total_presupuesto_mes else 0
        cumplimiento_acumulado = (total_venta_anual / total_presupuesto_acumulado) * 100 if total_presupuesto_acumulado else 0

        diferencia_mes   = total_ventas_valor - total_presupuesto_mes
        diferencia_anual = total_venta_anual  - total_presupuesto_acumulado

        header_style = ParagraphStyle('HeaderStyle', fontSize=8,  textColor=colors.white,               fontName='Helvetica-Bold', alignment=1)
        label_style  = ParagraphStyle('LabelStyle',  fontSize=8,  textColor=colors.HexColor('#333333'), fontName='Helvetica-Bold', alignment=1)
        value_style  = ParagraphStyle('ValueStyle',  fontSize=9,  textColor=colors.HexColor('#000000'), fontName='Helvetica-Bold', alignment=1)

        COL_LABEL = 1.0 * inch
        COL_DATA  = (ANCHO - 4.8*inch - COL_LABEL) / 4

        tabla_resumen = Table(
            [
                [Paragraph("",             header_style),
                Paragraph("Ventas",       header_style),
                Paragraph("Presupuesto",  header_style),
                Paragraph("Diferencia",   header_style),
                Paragraph("Cumplimiento", header_style)],
                [Paragraph("Mensual",                          label_style),
                Paragraph(f"${total_ventas_valor:,.2f} USD",  value_style),
                Paragraph(f"${total_presupuesto_mes:,.2f} USD", value_style),
                Paragraph(f"${diferencia_mes:,.2f} USD",      value_style),
                Paragraph(f"{cumplimiento_mes:,.2f}%",        value_style)],
                [Paragraph("Acumulado",                        label_style),
                Paragraph(f"${total_venta_anual:,.2f} USD",   value_style),
                Paragraph(f"${total_presupuesto_acumulado:,.2f} USD", value_style),
                Paragraph(f"${diferencia_anual:,.2f} USD",    value_style),
                Paragraph(f"{cumplimiento_acumulado:,.2f}%",      value_style)],
            ],
            colWidths=[COL_LABEL, COL_DATA, COL_DATA, COL_DATA, COL_DATA]
        )

        tabla_resumen.setStyle(TableStyle([
            ('BACKGROUND',   (0,0), (-1,0), colors.HexColor('#911218')),
            ('BACKGROUND',   (0,1), (-1,1), colors.HexColor('#F5F5F5')),
            ('BACKGROUND',   (0,2), (-1,2), colors.white),
            ('BACKGROUND',   (0,1), (0,2),  colors.HexColor('#E8E8E8')),
            ('BOX',          (0,0), (-1,-1), 1.5, colors.HexColor('#911218')),
            ('LINEBELOW',    (0,0), (-1,0),  0.5, colors.grey),
            ('INNERGRID',    (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',       (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING',  (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING',   (0,0), (-1,-1), 4),
            ('BOTTOMPADDING',(0,0), (-1,-1), 4),
        ]))

        story.append(tabla_resumen)
        story.append(Spacer(0, 20))

        # --------------------------------------------------
        # 3. HOJA 1 — Fila 2: Comparativo ventas (50%) | Ventas por Segmento (50%)
        # --------------------------------------------------
        ANCHO_UTIL = ANCHO - 0.8*inch

        ANCHO_LINEAS   = ANCHO_UTIL * 0.50
        ANCHO_SEGMENTO = ANCHO_UTIL * 0.50

        # ---------- Gráfica comparativo ----------
        fig_lineas = self.generar_grafica_lineas_ingresos_mensuales_fig(
            df_clases=df_clases,
            vendedores_lista=[vendedor],
            año_seleccionado=año,
            mes_nombre=mes_nombre,
            df_metas=df_metas,
            df_clases_anterior=df_clases_anterior,
            df_metas_anterior=df_metas_anterior
        )

        img_lineas = None
        if fig_lineas:
            buffer_lineas = BytesIO()
            fig_lineas.write_image(buffer_lineas, format='png', width=1000, height=450)
            buffer_lineas.seek(0)
            img_lineas = Image(buffer_lineas, width=ANCHO_LINEAS - 10, height=(ANCHO_LINEAS - 10) * (450/1000))

        if not img_lineas:
            img_lineas = Paragraph("No hay datos gráfica de líneas", styles['Normal'])


        # ---------- Tabla Ventas por Segmento ----------
        # df_categoria_anual = self.obtener_categoria_ingresos_anual_reporte(vendedor, año)


        MESES_ES = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
            "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
            "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }
        mes_num = MESES_ES[mes_nombre]

        df_categoria_anual = self.obtener_categoria_ingresos_anual_reporte(vendedor, año, mes_num)

        TODOS_LOS_SEGMENTOS = [
            "COMPONENTES",
            "CONSUMIBLES MANUALES",
            "CONSUMIBLES MECANIZADOS LASER",
            "CONSUMIBLES MECANIZADOS OXICORTE",
            "CONSUMIBLES MECANIZADOS PLASMA",
            "CONSUMIBLES MECANIZADOS WATER",
            "MAQUINAS MECANIZADAS",
            "OTROS",
            "POWERMAX",
            "REFACCIONES",
            "SISTEMAS DE CORTE LASER",
            "SISTEMAS DE CORTE PLASMA",
        ]

        header_cat_style = ParagraphStyle('HeaderCat', fontSize=6,   fontName='Helvetica-Bold', textColor=colors.white,              alignment=TA_CENTER)
        header_sub_style = ParagraphStyle('HeaderSub', fontSize=5.5, fontName='Helvetica-Bold', textColor=colors.white,              alignment=TA_CENTER)
        cat_label_style  = ParagraphStyle('CatLabel',  fontSize=5,   fontName='Helvetica',      textColor=colors.HexColor('#333333'), alignment=TA_LEFT)
        cat_value_style  = ParagraphStyle('CatValue',  fontSize=5.5, fontName='Helvetica-Bold', textColor=colors.HexColor('#000000'), alignment=TA_CENTER)

        W       = ANCHO_SEGMENTO - 12
        COL_SEG = W * 0.36
        COL_IMP = W * 0.18
        COL_PCT = W * 0.10

        # --- Normalizar df_categoria (mes) ---
        if df_categoria is not None and not df_categoria.empty:
            df_cat = df_categoria.copy()
            if "TotalIngresosUSD" not in df_cat.columns:
                df_cat = (
                    df_cat.groupby("Clase", as_index=False)
                    .agg(TotalIngresosUSD=("IngresosUSD", "sum"))
                    .rename(columns={"Clase": "Categoria"})
                )
        else:
            df_cat = pd.DataFrame({"Categoria": [], "TotalIngresosUSD": []})

        # --- Normalizar df_categoria_anual ---
        if df_categoria_anual is not None and not df_categoria_anual.empty:
            df_cat_anual = df_categoria_anual.copy()
            if "TotalIngresosUSD" not in df_cat_anual.columns:
                df_cat_anual = (
                    df_cat_anual.groupby("Clase", as_index=False)
                    .agg(TotalIngresosUSD=("IngresosUSD", "sum"))
                    .rename(columns={"Clase": "Categoria"})
                )
        else:
            df_cat_anual = pd.DataFrame({"Categoria": [], "TotalIngresosUSD": []})

        # --- Merge contra catálogo completo ---
        df_base = pd.DataFrame({"Categoria": TODOS_LOS_SEGMENTOS})

        df_merged = (
            df_base
            .merge(df_cat.rename(columns={"TotalIngresosUSD": "TotalMesUSD"}),   on="Categoria", how="left")
            .merge(df_cat_anual.rename(columns={"TotalIngresosUSD": "TotalAnualUSD"}), on="Categoria", how="left")
            .fillna(0)
            .sort_values(["TotalMesUSD", "TotalAnualUSD"], ascending=[False, False])
            .reset_index(drop=True)
        )

        total_mes   = df_merged["TotalMesUSD"].sum()
        total_anual = df_merged["TotalAnualUSD"].sum()

        # --- Construir filas de la tabla ---
        datos_cat = [
            [Paragraph("Ventas por Segmento", header_cat_style),
             Paragraph(f"Mes-{mes_nombre}",   header_cat_style),
             Paragraph("",                    header_cat_style),
             Paragraph(f"Año-{año}",          header_cat_style),
             Paragraph("",                    header_cat_style)],
            [Paragraph("",        header_sub_style),
             Paragraph("Importe", header_sub_style),
             Paragraph("Cump.",   header_sub_style),
             Paragraph("Importe", header_sub_style),
             Paragraph("Cump.",   header_sub_style)],
        ]

        for _, row in df_merged.iterrows():
            pct_mes   = (row["TotalMesUSD"]   / total_mes   * 100) if total_mes   else 0
            pct_anual = (row["TotalAnualUSD"] / total_anual * 100) if total_anual else 0
            datos_cat.append([
                Paragraph(str(row["Categoria"]),            cat_label_style),
                Paragraph(f"${row['TotalMesUSD']:,.0f}",    cat_value_style),
                Paragraph(f"{pct_mes:.1f}%",                cat_value_style),
                Paragraph(f"${row['TotalAnualUSD']:,.0f}",  cat_value_style),
                Paragraph(f"{pct_anual:.1f}%",              cat_value_style),
            ])

        # --- Crear tabla DESPUÉS del for ---
        tabla_categorias = Table(
            datos_cat,
            colWidths=[COL_SEG, COL_IMP, COL_PCT, COL_IMP, COL_PCT],
            rowHeights=[12] * len(datos_cat)       
        )

        cat_style_cmds = [
            ('BACKGROUND',    (0, 0), (-1, 1), colors.HexColor('#911218')),
            ('SPAN',          (0, 0), (0, 0)),
            ('SPAN',          (1, 0), (2, 0)),
            ('SPAN',          (3, 0), (4, 0)),
            ('LINEBELOW',     (0, 0), (-1, 0), 0.5, colors.HexColor('#C0C0C0')),
            ('LINEBEFORE',    (3, 0), (3, -1), 0.8, colors.HexColor('#C0C0C0')),
            ('BOX',           (0, 0), (-1, -1), 1.2, colors.HexColor('#911218')),
            ('INNERGRID',     (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ('ALIGN',         (0, 0), (-1,  1), 'CENTER'),
            ('ALIGN',         (0, 2), (0,  -1), 'LEFT'),
            ('ALIGN',         (1, 2), (-1, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 2),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 2),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]
        for idx in range(2, len(datos_cat)):
            bg = colors.HexColor('#F5F5F5') if idx % 2 == 0 else colors.white
            cat_style_cmds.append(('BACKGROUND', (0, idx), (-1, idx), bg))

        tabla_categorias.setStyle(TableStyle(cat_style_cmds))

        # ---------- Tabla fila 2: gráfica + segmento ----------
        tabla_fila2 = Table(
            [[img_lineas, tabla_categorias]],
            colWidths=[ANCHO_LINEAS, ANCHO_SEGMENTO]
        )
        tabla_fila2.setStyle(TableStyle([
            ('VALIGN',       (0,0), (-1,-1), 'TOP'),
            ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING',  (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(tabla_fila2)
        story.append(Spacer(0, 10))

        # --------------------------------------------------
        # 4. HOJA 1 — Fila 3: fig_pastel_1 (50%) | fig_pastel_2 (50%)
        # --------------------------------------------------
        ANCHO_PASTEL = ANCHO_UTIL * 0.50

        fig_pastel_1 = self.generar_grafica_pastel_categoria(df_categoria, mes_nombre, año)
        fig_pastel_2 = self.generar_grafica_pastel_top_clientes(vendedor, mes_nombre, año)

        img_pastel_1 = None
        img_pastel_2 = None

        RENDER_W = 1050   # ← más ancho para que las etiquetas laterales no se corten
        RENDER_H = 600   # ← altura sin cambios, pastel sigue siendo redondo

        if fig_pastel_1:
            buffer_pastel_1 = BytesIO()
            fig_pastel_1.write_image(buffer_pastel_1, format='png', width=RENDER_W, height=RENDER_H)
            buffer_pastel_1.seek(0)
            DISPLAY_W_PASTEL = ANCHO_UTIL * 0.50 - 10
            # El aspect ratio usa RENDER_W/RENDER_H para que la imagen no se estire
            img_pastel_1 = Image(buffer_pastel_1, width=DISPLAY_W_PASTEL, height=DISPLAY_W_PASTEL * (RENDER_H / RENDER_W))

        if fig_pastel_2:
            buffer_pastel_2 = BytesIO()
            fig_pastel_2.write_image(buffer_pastel_2, format='png', width=RENDER_W, height=RENDER_H)
            buffer_pastel_2.seek(0)
            DISPLAY_W_PASTEL = ANCHO_UTIL * 0.50 - 10
            img_pastel_2 = Image(buffer_pastel_2, width=DISPLAY_W_PASTEL, height=DISPLAY_W_PASTEL * (RENDER_H / RENDER_W))

        if not img_pastel_1:
            img_pastel_1 = Paragraph("Sin datos gráfica pastel", styles['Normal'])
        if not img_pastel_2:
            img_pastel_2 = Paragraph("Sin datos gráfica barras", styles['Normal'])

        tabla_fila3 = Table(
            [[img_pastel_1, img_pastel_2]],
            colWidths=[ANCHO_PASTEL, ANCHO_PASTEL]
        )
        tabla_fila3.setStyle(TableStyle([
            ('VALIGN',       (0,0), (-1,-1), 'TOP'),
            ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING',  (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(tabla_fila3)

        # --------------------------------------------------
        # Salto de página — inicia Hoja 2
        # --------------------------------------------------
        story.append(PageBreak())

        # --------------------------------------------------
        # 5. HOJA 2 — Tabla Resumen de Movilidad
        # --------------------------------------------------
        df_movilidad = self.resumen_movilidad.obtener_resumenes_reporte_pdf(vendedor, mes_nombre, año)
        df_km        = self.kilometraje_modelo.obtener_total_kilometraje_mes(vendedor, mes_nombre, año)
        total_km     = f"{df_km['TotalKilometros'].iloc[0]:,.1f}" if df_km is not None and not df_km.empty else "—"

        titulo_movilidad_style = ParagraphStyle(
            'TituloMovilidad', parent=styles['Heading1'],
            fontSize=12, textColor=colors.HexColor("#000000"),
            spaceAfter=6, alignment=TA_LEFT
        )
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(
            f"Resumen de Actividades: &nbsp; {vendedor} - {mes_nombre} {año} &nbsp;&nbsp; Resumen generado el día: {fecha_hoy}",
            titulo_movilidad_style
        ))
        story.append(Spacer(0, 6))

        if df_movilidad is not None and not df_movilidad.empty:
            header_mov_style = ParagraphStyle('HeaderMov', fontSize=8, fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
            cell_mov_style   = ParagraphStyle('CellMov',   fontSize=9, fontName='Helvetica-Bold', textColor=colors.HexColor('#222222'), alignment=TA_CENTER)

            columnas_movilidad = [
                ("Días Hábiles",                       "DiasHabiles"),
                ("Total Kilometraje",                   "__km__"),
                ("Promedio Diario Recorrido (Km)",      "AvgDiarioRecorrido"),
                ("Cantidad Visitas",                    "CantidadVisitas"),
                ("Tiempo Atención (Hrs)",               "TiempoDestinadoAtencion"),
                ("Promedio Tiempo con Cliente (Hrs)",   "AvgTiempoConCliente"),
                ("Promedio Visitas por Día",            "AvgVisitasPorDia"),
            ]

            encabezados = [Paragraph(col[0], header_mov_style) for col in columnas_movilidad]
            datos_mov   = [encabezados]

            for _, row in df_movilidad.iterrows():
                fila = []
                for col in columnas_movilidad:
                    if col[1] == "__km__":
                        fila.append(Paragraph(total_km, cell_mov_style))
                    else:
                        fila.append(Paragraph(str(row[col[1]]) if pd.notna(row[col[1]]) else "—", cell_mov_style))
                datos_mov.append(fila)

            n_cols    = len(columnas_movilidad)
            col_ancho = (ANCHO - 0.8*inch) / n_cols

            tabla_movilidad = Table(datos_mov, colWidths=[col_ancho] * n_cols)

            mov_style_cmds = [
                ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#911218')),
                ('BOX',           (0,0), (-1,-1), 1.2, colors.HexColor('#911218')),
                ('INNERGRID',     (0,0), (-1,-1), 0.4, colors.lightgrey),
                ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
                ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
                ('LEFTPADDING',   (0,0), (-1,-1), 4),
                ('RIGHTPADDING',  (0,0), (-1,-1), 4),
                ('TOPPADDING',    (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]
            for idx in range(1, len(datos_mov)):
                bg = colors.HexColor('#F5F5F5') if idx % 2 != 0 else colors.white
                mov_style_cmds.append(('BACKGROUND', (0, idx), (-1, idx), bg))

            tabla_movilidad.setStyle(TableStyle(mov_style_cmds))
            story.append(tabla_movilidad)
        else:
            story.append(Paragraph("Sin datos de movilidad para este período.", styles['Normal']))

        story.append(Spacer(0, 20))

        # --------------------------------------------------
        # 6. HOJA 2 — Fila 2: Servicio Cliente | Dist. Clientes | Tipo Cliente
        # --------------------------------------------------
        asistencia_porc     = self.servicio_cliente.get_porcentaje_asistencia_vs_planeacion(vendedor, mes_nombre, año)
        cobertura_porc      = self.servicio_cliente.get_porcentaje_cobertura_cartera(vendedor, mes_nombre, año)
        visitas_porc        = self.servicio_cliente.get_porcentaje_visitas_comerciales(vendedor, mes_nombre, año)
        demostraciones_porc = self.servicio_cliente.get_porcentaje_demostraciones_pmx(vendedor, mes_nombre, año)
        clientes_porc     = self.servicio_cliente.get_porcentaje_nuevos_clientes(vendedor, mes_nombre, año)
        prospectos_porc     = self.servicio_cliente.get_porcentaje_nuevos_prospectos(vendedor, mes_nombre, año)
        oportunidades_porc  = self.servicio_cliente.get_porcentaje_oportunidades(vendedor, mes_nombre, año)

        asistencia_cant     = self.servicio_cliente.get_cantidad_asistencia(vendedor, mes_nombre, año)
        cobertura_cant      = self.servicio_cliente.get_cantidad_cobertura_cartera(vendedor, mes_nombre, año)
        # visitas_cant        = self.servicio_cliente.get_cantidad_visitas_comerciales(vendedor, mes_nombre, año)
        visitas_cant        = self.resumen_movilidad.obtener_cantidad_visitas_pdf(vendedor, mes_nombre, año)
        demostraciones_cant = self.servicio_cliente.get_cantidad_demostraciones_pmx(vendedor, mes_nombre, año)
        clientes_cant     = self.servicio_cliente.get_cantidad_nuevos_clientes(vendedor, mes_nombre, año)
        prospectos_cant     = self.servicio_cliente.get_cantidad_nuevos_prospectos(vendedor, mes_nombre, año)
        oportunidades_cant  = self.servicio_cliente.get_cantidad_oportunidades(vendedor, mes_nombre, año)

        header_sc_style = ParagraphStyle('HeaderSC',  fontSize=8,   fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
        header_sc_style2= ParagraphStyle('HeaderSC2', fontSize=6,   fontName='Helvetica-Bold', textColor=colors.white, alignment=TA_CENTER)
        cell_label_style= ParagraphStyle('CellLabel', fontSize=5.5, fontName='Helvetica',      textColor=colors.HexColor('#333333'), alignment=TA_LEFT)
        cell_value_style= ParagraphStyle('CellValue', fontSize=6,   fontName='Helvetica-Bold', textColor=colors.HexColor('#000000'), alignment=TA_CENTER)

        def wrap(text, style):
            return Paragraph(text.replace(" ", "<br/>"), style)

        datos_sc = [
            [Paragraph("Servicio Cliente", header_sc_style2),
             Paragraph("Cantidad",            header_sc_style2),
             Paragraph("Porcentaje",                header_sc_style2)],
            [wrap("Asistencia vs\nPlaneación",  cell_label_style), Paragraph(str(asistencia_cant),     cell_value_style), Paragraph(f"{round(asistencia_porc*100,0):.0f}%",     cell_value_style)],
            [wrap("Cobertura\nde Cartera",       cell_label_style), Paragraph(str(cobertura_cant),      cell_value_style), Paragraph(f"{round(cobertura_porc*100,0):.0f}%",      cell_value_style)],
            # [wrap("Visitas\nComerciales",         cell_label_style), Paragraph(str(visitas_cant),        cell_value_style), Paragraph(f"{round(visitas_porc*100,0):.0f}%",        cell_value_style)],
            [wrap("Demostraciones\nPMX",          cell_label_style), Paragraph(str(demostraciones_cant), cell_value_style), Paragraph(f"{round(demostraciones_porc*100,0):.0f}%", cell_value_style)],
            [wrap("Nuevos Clientes",  cell_label_style), Paragraph(str(clientes_cant),     cell_value_style), Paragraph(f"{round(clientes_porc*100,0):.0f}%",     cell_value_style)],
            [wrap("Nuevos Prospectos",  cell_label_style), Paragraph(str(prospectos_cant),     cell_value_style), Paragraph(f"{round(prospectos_porc*100,0):.0f}%",     cell_value_style)],
            [wrap("Oportunidades",                cell_label_style), Paragraph(str(oportunidades_cant),  cell_value_style), Paragraph("",  cell_value_style)], # Porcentaje pendiente
        ]

        COL3         = ANCHO_UTIL / 3
        COL_SC_LABEL = (COL3 - 12) * 0.52
        COL_SC_CANT  = (COL3 - 12) * 0.20
        COL_SC_PCT   = (COL3 - 12) * 0.28

        tabla_sc = Table(
            datos_sc,
            colWidths=[COL_SC_CANT, COL_SC_LABEL, COL_SC_PCT]
        )
        tabla_sc.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), colors.HexColor('#911218')),
            ('BACKGROUND',    (0,1), (-1,1), colors.HexColor('#F5F5F5')),
            ('BACKGROUND',    (0,2), (-1,2), colors.white),
            ('BACKGROUND',    (0,3), (-1,3), colors.HexColor('#F5F5F5')),
            ('BACKGROUND',    (0,4), (-1,4), colors.white),
            ('BACKGROUND',    (0,5), (-1,5), colors.HexColor('#F5F5F5')),
            ('BACKGROUND',    (0,6), (-1,6), colors.white),
            ('BOX',           (0,0), (-1,-1), 1.2, colors.HexColor('#911218')),
            ('INNERGRID',     (0,0), (-1,-1), 0.4, colors.lightgrey),
            ('ALIGN',         (0,0), (-1, 0), 'CENTER'),
            ('ALIGN',         (0,1), (0, -1), 'LEFT'),    # col 0 → etiquetas, alineadas izquierda
            ('ALIGN',         (1,1), (1, -1), 'CENTER'),  # col 1 → cantidades, centradas
            ('ALIGN',         (2,1), (2, -1), 'CENTER'),  # col 2 → porcentajes, centrados
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING',   (0,0), (-1,-1), 3),
            ('RIGHTPADDING',  (0,0), (-1,-1), 3),
            ('TOPPADDING',    (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))

        # ---------- Gráficas distribución y tipo cliente ----------
        fig_dist_clientes = self.generar_grafica_pastel_distribucion_clientes(vendedor, mes_nombre, año)
        fig_tipo_cliente  = self.generar_grafica_pastel_actividad_tipo_cliente(vendedor, año, mes_nombre)

        img_dist_clientes = None
        img_tipo_cliente  = None

        if fig_dist_clientes:
            buffer_dist = BytesIO()
            fig_dist_clientes.write_image(buffer_dist, format='png', width=600, height=580)
            buffer_dist.seek(0)
            DISPLAY_W_PASTEL = ANCHO_UTIL * 0.32 - 10
            img_dist_clientes = Image(buffer_dist, width=DISPLAY_W_PASTEL, height=DISPLAY_W_PASTEL * (580/600))

        if fig_tipo_cliente:
            buffer_tipo = BytesIO()
            fig_tipo_cliente.write_image(buffer_tipo, format='png', width=600, height=580)
            buffer_tipo.seek(0)
            DISPLAY_W_PASTEL = ANCHO_UTIL * 0.32 - 10
            img_tipo_cliente = Image(buffer_tipo, width=DISPLAY_W_PASTEL, height=DISPLAY_W_PASTEL * (580/600))

        if not img_dist_clientes:
            img_dist_clientes = Paragraph("Sin datos distribución clientes", styles['Normal'])
        if not img_tipo_cliente:
            img_tipo_cliente  = Paragraph("Sin datos actividad tipo cliente", styles['Normal'])

        tabla_fila_h2 = Table(
            [[tabla_sc, img_dist_clientes, img_tipo_cliente]],
            colWidths=[COL3, COL3, COL3]
        )
        tabla_fila_h2.setStyle(TableStyle([
            ('VALIGN',       (0,0), (-1,-1), 'TOP'),
            ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
            ('LEFTPADDING',  (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(tabla_fila_h2)

        story.append(Spacer(0, 60))

        # --------------------------------------------------
        # 7. Firmas
        # --------------------------------------------------
        df_coordinador     = self.ventas_reales_modelo.obtener_coordinador_vendedor(vendedor)
        coordinador_nombre = "Coordinador"
        if not df_coordinador.empty and 'Coordinador' in df_coordinador.columns:
            coordinador_nombre = df_coordinador['Coordinador'].iloc[0]
            if pd.isna(coordinador_nombre) or coordinador_nombre == "":
                coordinador_nombre = "Coordinador"

        firma_style  = ParagraphStyle('Firmas', fontSize=9, alignment=TA_CENTER)
        linea_firma  = "______________________________"

        tabla_firmas_superior = Table(
            [
                [Paragraph(linea_firma, firma_style),        Paragraph(linea_firma, firma_style)],
                [Paragraph(vendedor.upper(), firma_style),   Paragraph(coordinador_nombre.upper(), firma_style)],
                [Paragraph("VENDEDOR", firma_style),          Paragraph("COORDINADOR DE VENTAS", firma_style)]
            ],
            colWidths=[3*inch, 3*inch]
        )
        tabla_firmas_superior.setStyle(TableStyle([
            ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(tabla_firmas_superior)
        story.append(Spacer(1, 0.4*inch))

        tabla_firma_centrada = Table(
            [
                [Paragraph(linea_firma, firma_style)],
                [Paragraph("MIRYAM MEZA SANDOVAL", firma_style)],
                [Paragraph("ANALISTA AFTER SALES",  firma_style)]
            ],
            colWidths=[3*inch]
        )
        tabla_firma_centrada.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(tabla_firma_centrada)

        # --------------------------------------------------
        # Borde, logotipo y marca de agua
        # --------------------------------------------------
        def agregar_borde(canvas, doc):
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#911218"))
            canvas.setLineWidth(3)
            canvas.rect(0.15*inch, 0.15*inch, PAGE[0] - 0.3*inch, PAGE[1] - 0.3*inch)

            # logo_path = r"C:\CIC_WebApp\vista\images\logo_GPA.png"
            logo_path = os.getenv("LOGO_PDF")

            if canvas.getPageNumber() == 1:
                try:
                    canvas.drawImage(logo_path, 0.5*inch, PAGE[1] - 1.8*inch,
                                    width=120, height=95, preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    print("Error al insertar logotipo:", e)

            try:
                canvas.setFillAlpha(0.15)
                canvas.drawImage(logo_path, PAGE[0] - 1.6*inch, PAGE[1] - 1.4*inch,
                                width=100, height=80, preserveAspectRatio=True, mask='auto')
                canvas.setFillAlpha(1)
            except Exception as e:
                print("Error al insertar marca de agua:", e)

            canvas.restoreState()

        doc.build(story, onFirstPage=agregar_borde, onLaterPages=agregar_borde)
        buffer.seek(0)
        return buffer


    #----------------------------------------------------------------------------
    #
    #----------------------------------------------------------------------------
    def enviar_correo_reportes_pdf(self, periodos_info):
        """Genera y envía reportes PDF por vendedor y período"""

        lista_vendedores = [
            'Adan Garza',
            'Alfonso Gasca',
            'Jorge Martinez',
            'Cesar Valdes'
        ]

        if not lista_vendedores or not periodos_info:
            st.warning("⚠️ No hay vendedores o períodos definidos para generar reportes.")
            return

        remitente      = os.getenv("CORREO_EMISOR")
        contraseña_app = os.getenv("APP_PASSWORD")
        destinatarios  = [os.getenv("CORREO_REPORTES_1"),
                          os.getenv("CORREO_REPORTES_2")]

        total_reportes     = len(lista_vendedores) * len(periodos_info)
        reportes_exitosos  = 0
        progress_bar       = st.progress(0)
        progress_text      = st.empty()

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(remitente, contraseña_app)

                for idx_reporte, (vendedor, periodo) in enumerate(
                    [(v, p) for p in periodos_info for v in lista_vendedores], start=1
                ):
                    mes        = periodo['mes']
                    año        = periodo['año']
                    mes_nombre = periodo['mes_nombre']

                    progress_bar.progress(idx_reporte / total_reportes)
                    progress_text.text(
                        f"Generando reporte {idx_reporte}/{total_reportes}: "
                        f"{vendedor} - {mes_nombre} {año}"
                    )

                    # Verificar que haya datos para este vendedor y período
                    df_datos = self.obtener_datos_vendedor_periodo(vendedor, mes, año)
                    if df_datos is None or df_datos.empty:
                        st.warning(f"⚠️ Sin datos para {vendedor} - {mes_nombre} {año}. Se omite.")
                        continue
                    


                    meta = self.obtener_meta_vendedor(vendedor, mes_nombre, año)
                    # presupuesto = self.presupuesto_modelo.obtener_total_presupuesto_acumulado(vendedor, año, mes_nombre)
                    fecha_hoy = datetime.now().strftime("%d/%m/%Y")

                    try:
                        # Generar PDF — df_clases/df_metas son None porque
                        # generar_grafica_lineas_ingresos_mensuales_fig
                        # hace sus propias queries con vendedores_lista y año
                        pdf_buffer = self.generar_pdf_reporte(
                            vendedor           = vendedor,
                            mes_nombre         = mes_nombre,
                            año                = año,
                            df_datos           = df_datos,
                            meta               = meta,
                            df_clases          = None,
                            df_metas           = None,
                            df_clases_anterior = None,
                            df_metas_anterior  = None,
                        )

                        nombre_archivo = (
                            f"Reporte_{vendedor.replace(' ', '_')}"
                            f"_{mes_nombre}_{año}.pdf"
                        )

                        # --- Armar y enviar correo ---
                        total_ventas     = df_datos['IngresosUSD'].sum()
                        cumplimiento_str = (
                            f"{(total_ventas / meta * 100):.1f}% "
                            f"{'✅' if total_ventas >= meta else '⚠️'}"
                            if meta and meta > 0
                            else "Sin meta definida"
                        )

                        # total_venta_anual = self.ventas_reales_modelo.obtener_ingresos_por_vendedor_reporte(vendedor, año, mes_nombre)
                        total_presupuesto = self.presupuesto_modelo.obtener_total_presupuesto_mensual(vendedor, año, mes_nombre)
                        cumplimiento = (total_ventas / total_presupuesto) * 100 if total_presupuesto else 0


                        email = EmailMessage()
                        email["From"]    = remitente
                        email["To"]      = ", ".join(destinatarios)
                        email["Subject"] = (
                            f"Reporte de Ventas - {vendedor} - {mes_nombre} {año}"
                        )
                        email.set_content(
                            f"Estimado usuario,\n\n"
                            f"Se adjunta el reporte de ventas de {vendedor} "
                            f"correspondiente al período {mes_nombre} {año}  Reporte generado en día {fecha_hoy}.\n\n"
                            f"Resumen:\n"
                            f"  - Total Ventas : ${total_ventas:,.2f} USD\n"
                            f"  - Presupuesto  : ${total_presupuesto:,.2f} USD\n"
                            f"  - Cumplimiento : {cumplimiento:,.2f}%\n\n"
                            f"Saludos cordiales."
                        )

                        pdf_buffer.seek(0)
                        email.add_attachment(
                            pdf_buffer.read(),
                            maintype='application',
                            subtype='pdf',
                            filename=nombre_archivo
                        )

                        smtp.send_message(email)
                        reportes_exitosos += 1

                    except Exception as e:
                        st.warning(
                            f"❌ Error al generar/enviar reporte para "
                            f"{vendedor} - {mes_nombre} {año}: {e}"
                        )
                        import traceback
                        st.warning(traceback.format_exc())
                        continue

        except smtplib.SMTPAuthenticationError:
            st.error(
                "❌ Error de autenticación SMTP. "
                "Verifica las variables CORREO_EMISOR y APP_PASSWORD."
            )
        except Exception as e:
            st.error(f"❌ Error general al enviar reportes: {e}")
            import traceback
            st.error(traceback.format_exc())
        finally:
            progress_bar.empty()
            progress_text.empty()

        omitidos = total_reportes - reportes_exitosos
        if reportes_exitosos == total_reportes:
            st.success(f"✅ Todos los reportes generados y enviados: {reportes_exitosos}/{total_reportes}")
        elif reportes_exitosos > 0:
            st.success(f"✅ Reportes enviados: {reportes_exitosos}/{total_reportes}")
            st.warning(f"⚠️ Omitidos o con error: {omitidos}")
        else:
            st.error(f"❌ No se pudo enviar ningún reporte. Revisa los errores anteriores.")

    def enviar_correos(self, archivo_pdf, periodo):
        """Envío de correos de notificación general"""
        st.spinner("📧 Enviando notificación a usuarios...")

        correos_validos = self.obtener_correos_validos()

        if correos_validos.empty:
            st.warning("⚠️ No se encontraron correos válidos en la base de datos.")
            return

        remitente = os.getenv("CORREO_EMISOR")
        contraseña_app = os.getenv("APP_PASSWORD")

        # carpeta_destino = r"C:\Users\Administrador\Documents\ReportesCIC\Reportes"
        carpeta_destino = os.getenv("CARPETA_DESTINO")
        os.makedirs(carpeta_destino, exist_ok=True)

        adjunto = None
        nombre_pdf = None
        if archivo_pdf is not None:
            nombre_pdf = archivo_pdf.name
            ruta_pdf = os.path.join(carpeta_destino, nombre_pdf)
            with open(ruta_pdf, "wb") as f:
                f.write(archivo_pdf.getbuffer())
            adjunto = archivo_pdf.getvalue()

        asunto = "CIC Ventas Actualizadas"
        mensaje = f"Estimado usuario,\n\nSe ha cargado reporte en CIC de las ventas del periodo {periodo}.\n\nSaludos."

        enviados = 0
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(remitente, contraseña_app) 

            for correo in correos_validos["Correo"].dropna():
                if "@" not in correo:
                    continue

                email = EmailMessage()
                email["From"] = remitente
                email["To"] = correo
                email["Subject"] = asunto
                email.set_content(mensaje)

                if adjunto:
                    email.add_attachment(
                        adjunto,
                        maintype="application",
                        subtype="pdf",
                        filename=nombre_pdf
                    )

                smtp.send_message(email)
                enviados += 1

        st.success(f"✅ Datos registrados y correos enviados a {enviados} destinatarios.")
        if archivo_pdf:
            st.info(f"📄 PDF guardado en {carpeta_destino}")

    def obtener_correos_validos(self):
        """Obtiene los correos válidos de usuarios activos"""
        query = """
        SELECT Correo FROM dbo.UsuariosCIC WHERE Correo IS NOT NULL AND Status = 1
        """
        try:
            conn = self.db.get_connection()
            df_existentes = pd.read_sql_query(query, conn)
            conn.close()
            return df_existentes
        except Exception as e:
            st.error(f"Error al obtener correos válidos: {e}")
            return pd.DataFrame()
        


    def obtener_categoria_ingresos_reporte(self, vendedor, mes_nombre, año):
        """
        Obtiene cantidad de clase para un representante de venta individual agrupado por categorías.
        Convierte el nombre del mes a número antes de ejecutar la consulta.
        """

        # ==========================
        # MAPEO DE NOMBRE → NÚMERO
        # ==========================
        meses = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }

        # Convertir a número
        mes_numero = meses.get(mes_nombre.lower().strip())

        if mes_numero is None:
            print(f"Mes inválido recibido: {mes_nombre}")
            return pd.DataFrame()

        # ==========================
        # CONSULTA SQL CORREGIDA
        # ==========================
        query = f"""
            WITH CategorizacionVentas AS (
                SELECT 
                    RepresentanteDeVentas,
                    CASE 
                        WHEN Clase IN ('COMPONENTES DIRECTOS:BALEROS Y RODAMIENTOS',
                                        'COMPONENTES DIRECTOS:ELECTRICO',
                                        'HERRAMIENTA/HERRAMENTALES:HERRAMIENTA',
                                        'REFACCIONES:COMPONENTES Y ACCSESORIOS') 
                            THEN 'COMPONENTES'
                        WHEN Clase IN ('CONSUMIBLES:MANUALES:PLASMA',
                                        'CONSUMIBLES:MANUALES:PLASMA SYNC') 
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
                    IngresosUSD
                FROM vw_CategoriaIngresos
                WHERE YEAR(FechaReal) = {año} 
                AND MONTH(FechaReal) = {mes_numero}
                AND RepresentanteDeVentas = '{vendedor}'
            )
            SELECT 
                RepresentanteDeVentas,
                Categoria,
                SUM(IngresosUSD) AS TotalIngresosUSD
            FROM CategorizacionVentas
            GROUP BY RepresentanteDeVentas, Categoria
            ORDER BY Categoria;
            """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error al obtener datos de categorías: {str(e)}")
            return pd.DataFrame()
        

    def obtener_categoria_ingresos_anual_reporte(self, vendedor, año, mes):
        """
        Obtiene ingresos por categoría acumulados desde enero hasta el mes indicado.
        """
        query = f"""
            WITH CategorizacionVentas AS (
                SELECT 
                    RepresentanteDeVentas,
                    CASE 
                        WHEN Clase IN ('COMPONENTES DIRECTOS:BALEROS Y RODAMIENTOS',
                                        'COMPONENTES DIRECTOS:ELECTRICO',
                                        'HERRAMIENTA/HERRAMENTALES:HERRAMIENTA',
                                        'REFACCIONES:COMPONENTES Y ACCSESORIOS') 
                            THEN 'COMPONENTES'
                        WHEN Clase IN ('CONSUMIBLES:MANUALES:PLASMA',
                                        'CONSUMIBLES:MANUALES:PLASMA SYNC') 
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
                    IngresosUSD
                FROM vw_CategoriaIngresos
                WHERE YEAR(FechaReal) = {año}
                AND MONTH(FechaReal) <= {mes}        -- ← único cambio en la query
                AND RepresentanteDeVentas = '{vendedor}'
            )
            SELECT 
                RepresentanteDeVentas,
                Categoria,
                SUM(IngresosUSD) AS TotalIngresosUSD
            FROM CategorizacionVentas
            GROUP BY RepresentanteDeVentas, Categoria
            ORDER BY Categoria;
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error al obtener datos de categorías anuales: {str(e)}")
            return pd.DataFrame()
        
    def obtener_meses_años_existentes_por_vendedor(
        self, vendedor, fecha_inicio, fecha_fin
    ):
        """
        Obtiene meses y años existentes para un vendedor en un rango
        """

        query = """
            SELECT DISTINCT 
                YEAR(Fecha) AS Año,
                MONTH(Fecha) AS Mes
            FROM dev_Detalle_Corregida
            WHERE Fecha IS NOT NULL
            AND RepresentanteDeVentas = ?
            AND Fecha BETWEEN ? AND ?
            ORDER BY Año, Mes
        """

        try:
            conn = self.db.get_connection()

            df = pd.read_sql_query(
                query,
                conn,
                params=[vendedor, fecha_inicio, fecha_fin]
            )

            conn.close()

            if df.empty:
                return []

            return [
                (int(row["Mes"]), int(row["Año"]))
                for _, row in df.iterrows()
            ]

        except Exception as e:
            st.warning(f"Error consultando meses para {vendedor}: {e}")
            return []

    def generar_pdf_reporte_boton(
        self, vendedores_seleccionados, fecha_inicio, fecha_fin,
        df_clases=None, df_metas=None,
        df_clases_anterior=None, df_metas_anterior=None
    ):
        """
        Genera reportes PDF para múltiples vendedores y períodos.
        Si hay múltiples reportes, los empaqueta en un archivo ZIP.
        """
        
        with st.spinner("📊 Generando reportes PDF..."):
            
            MESES_ES = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            
            reportes_generados = []
            
            for vendedor in vendedores_seleccionados:
                
                meses_con_datos = self.obtener_meses_años_existentes_por_vendedor(
                    vendedor, fecha_inicio, fecha_fin
                )
                
                if not meses_con_datos:
                    continue
                
                for mes_numero, año in meses_con_datos:
                    
                    mes_nombre = MESES_ES.get(mes_numero)
                    if not mes_nombre:
                        continue
                    
                    df_datos = self.obtener_datos_vendedor_periodo(
                        vendedor, mes_numero, año
                    )
                    
                    if df_datos.empty:
                        continue
                    
                    meta = self.obtener_meta_vendedor(vendedor, mes_nombre, año)
                    
                    try:
                        pdf_buffer = self.generar_pdf_reporte(
                            vendedor, mes_nombre, año, df_datos, meta,
                            df_clases=df_clases,
                            df_metas=df_metas,
                            df_clases_anterior=df_clases_anterior,
                            df_metas_anterior=df_metas_anterior
                        )
                        
                        nombre_archivo = (
                            f"Reporte_{vendedor.replace(' ', '_')}_"
                            f"{mes_nombre}_{año}.pdf"
                        )
                        
                        reportes_generados.append({
                            'buffer': pdf_buffer.getvalue(),
                            'nombre': nombre_archivo,
                            'vendedor': vendedor,
                            'periodo': f"{mes_nombre} {año}"
                        })
                        
                    except Exception as e:
                        st.warning(f"⚠️ Error en {vendedor} - {mes_nombre} {año}: {e}")
            
            # Procesar resultados
            if reportes_generados:
                st.success(f"✅ {len(reportes_generados)} reporte(s) generado(s) correctamente")
                
                # Si solo hay un reporte, descarga PDF directa
                if len(reportes_generados) == 1:
                    reporte = reportes_generados[0]
                    
                    st.download_button(
                        label=f"📥 Descargar {reporte['nombre']}",
                        data=reporte['buffer'],
                        file_name=reporte['nombre'],
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.info(f"📄 Reporte: **{reporte['vendedor']}** - {reporte['periodo']}")
                
                # Si hay múltiples reportes, crear y descargar ZIP
                else:
                    # Crear archivo ZIP en memoria
                    zip_buffer = BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for reporte in reportes_generados:
                            # Agregar cada PDF al ZIP
                            zip_file.writestr(reporte['nombre'], reporte['buffer'])
                    
                    # Preparar el buffer para descarga
                    zip_buffer.seek(0)
                    
                    # Nombre del archivo ZIP con fecha y hora
                    fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_zip = f"Reportes_CIC_{fecha_str}.zip"
                    
                    # Botón de descarga del ZIP
                    st.download_button(
                        label=f"📦 Descargar todos los reportes ({len(reportes_generados)} archivos)",
                        data=zip_buffer.getvalue(),
                        file_name=nombre_zip,
                        mime="application/zip",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Mostrar resumen de reportes incluidos
                    st.info(f"📦 El archivo ZIP contiene {len(reportes_generados)} reportes")
                    
                    # Expandible con la lista completa de reportes
                    with st.expander("📋 Ver lista completa de reportes incluidos"):
                        for i, reporte in enumerate(reportes_generados, 1):
                            st.write(f"{i}. **{reporte['vendedor']}** - {reporte['periodo']}")
                            st.caption(f"   └─ {reporte['nombre']}")
            
            else:
                st.warning("⚠️ No se generaron reportes con los filtros actuales")
                st.info("Verifica que:")
                st.write("- Los vendedores seleccionados tengan datos en el período")
                st.write("- El rango de fechas sea correcto")

