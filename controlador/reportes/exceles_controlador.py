#controlador/reportes/exceles_controlador.py
import streamlit as st
import pandas as pd
from vista.base_vista import BaseVista
from vista.exceles_vista import ExcelesVista
from vista.componentes.sidebar_ventas_real import SideBarVentaReal
from modelo.exceles_modelo import ExcelesModelo

class ExcelesControlador(BaseVista):
    def __init__(self):
        self.excel_vista = ExcelesVista()
        self.excel_modelo = ExcelesModelo()
        self.vendedores_pdf = SideBarVentaReal()
        
    def ejecutar_vista_exceles(self):
        self.mostrar_titulo("📊 Carga de Reportes Mensuales")

        st.markdown("---")

        # Mostrar información sobre períodos existentes
        with st.expander("📅 Ver períodos ya cargados en la base de datos"):
            try:
                meses_existentes = self.excel_modelo.obtener_meses_años_existentes()
                if not meses_existentes.empty:
                    meses_display = meses_existentes.copy()

                    if 'Mes' in meses_display.columns:
                        meses_display['Mes_Nombre'] = meses_display['Mes'].map({
                            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                        })

                        st.dataframe(
                            meses_display[['Mes_Nombre', 'Año']],
                            column_config={
                                'Mes_Nombre': 'Mes',
                                'Año': 'Año'
                            },
                            hide_index=True,
                            use_container_width=True
                        )
                    else:
                        st.error("Error: No se pudo obtener la información de meses")
                else:
                    st.info("No hay datos cargados en la base de datos.")
            except Exception as e:
                st.error(f"Error al obtener períodos existentes: {e}")

        # --- DETALLES ---
        st.markdown("### 📂 Inserte archivo Excel - Consulta de NetSuite")

        self.excel_vista.arrastrar_archivo_excel(
            uploader_key="uploader_detalles",
            df_key="df_detalles"
        )

        archivo_pdf = None

        col1, col2, col3 = st.columns(3)
        with col2:
            if "df_detalles" in st.session_state:
                if st.button("⬆️ Guardar en Base de Datos y Notificar", use_container_width=True):
                    df = st.session_state["df_detalles"]
                    try:
                        with st.spinner("Validando y procesando datos..."):
                            self.excel_modelo.insertar_detalles(df, archivo_pdf)
                    except Exception as e:
                        st.error(f"❌ Error en el proceso: {e}")
                        import traceback
                        st.error(traceback.format_exc())

        # ──────────────────────────────────────────────────────────────────────────
        # TABLA DE REGISTROS — dev_Detalle_Corregida
        # ──────────────────────────────────────────────────────────────────────────
        st.divider()
        

        MESES_NOMBRE = {
            1: 'Enero',    2: 'Febrero',  3: 'Marzo',
            4: 'Abril',    5: 'Mayo',     6: 'Junio',
            7: 'Julio',    8: 'Agosto',   9: 'Septiembre',
            10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        MESES_ORDEN = list(MESES_NOMBRE.values())

        # Botón para cargar/recargar datos (evita consulta automática en cada rerun)
        # col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        # with col_btn1:
        #     st.subheader("📋 Registros Cargados en Base de Datos")
        # with col_btn2:
        #     cargar_datos = st.button("📋 Ver Registros", use_container_width=True)

        cargar_datos = st.button("📋 Ver Registros", use_container_width=True)

        if cargar_datos:
            with st.spinner("Consultando base de datos..."):
                df_raw = self.excel_modelo.obtener_todos_los_detalles()
            if df_raw.empty:
                st.info("ℹ️ No hay registros en la base de datos.")
                st.session_state["df_detalles_bd"] = pd.DataFrame()
            else:
                st.session_state["df_detalles_bd"] = df_raw

        df_raw = st.session_state.get("df_detalles_bd", pd.DataFrame())

        if not df_raw.empty:

            # ── Filtros ────────────────────────────────────────────────────────────
            with st.expander("🔍 Filtros", expanded=True):
                col_v, col_a, col_m, col_c, col_cl = st.columns(5)

                with col_v:
                    vendedores = sorted(df_raw['RepresentanteDeVentas'].dropna().unique().tolist())
                    filtro_vendedor = st.selectbox(
                        "Vendedor",
                        options=["Todos"] + vendedores,
                        key="det_filtro_vendedor"
                    )

                with col_a:
                    años = sorted(df_raw['Año'].dropna().unique().tolist(), reverse=True)
                    filtro_año = st.selectbox(
                        "Año",
                        options=["Todos"] + [str(a) for a in años],
                        key="det_filtro_año"
                    )

                with col_m:
                    # Mostrar meses disponibles en orden calendario
                    nums_disponibles = sorted(df_raw['Mes'].dropna().unique().tolist())
                    meses_disponibles = [MESES_NOMBRE[n] for n in nums_disponibles if n in MESES_NOMBRE]
                    filtro_mes = st.selectbox(
                        "Mes",
                        options=["Todos"] + meses_disponibles,
                        key="det_filtro_mes"
                    )

                with col_c:
                    clientes = sorted(df_raw['NombreCliente'].dropna().unique().tolist())
                    filtro_cliente = st.selectbox(
                        "Cliente",
                        options=["Todos"] + clientes,
                        key="det_filtro_cliente"
                    )

                with col_cl:
                    clases = sorted(df_raw['Clase'].dropna().unique().tolist())
                    filtro_clase = st.selectbox(
                        "Clase",
                        options=["Todos"] + clases,
                        key="det_filtro_clase"
                    )

            # ── Aplicar filtros ────────────────────────────────────────────────────
            MESES_INVERSO = {v: k for k, v in MESES_NOMBRE.items()}
            df_filtrado = df_raw.copy()

            if filtro_vendedor != "Todos":
                df_filtrado = df_filtrado[df_filtrado['RepresentanteDeVentas'] == filtro_vendedor]

            if filtro_año != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Año'] == int(filtro_año)]

            if filtro_mes != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Mes'] == MESES_INVERSO[filtro_mes]]

            if filtro_cliente != "Todos":
                df_filtrado = df_filtrado[df_filtrado['NombreCliente'] == filtro_cliente]

            if filtro_clase != "Todos":
                df_filtrado = df_filtrado[df_filtrado['Clase'] == filtro_clase]

            # ── Conteo y tabla ─────────────────────────────────────────────────────
            st.caption(f"Mostrando **{len(df_filtrado):,}** registro(s) de **{len(df_raw):,}** en total")

            if df_filtrado.empty:
                st.warning("⚠️ No se encontraron registros con los filtros seleccionados.")
            else:
                # Preparar columnas para mostrar
                df_display = df_filtrado.drop(columns=['Año', 'Mes'], errors='ignore').copy()

                # Renombrar columnas
                df_display = df_display.rename(columns={
                    'RepresentanteDeVentas': 'Vendedor',
                    'NombreCliente':         'Cliente',
                    'Clase':                 'Clase',
                    'Descripcion':           'Descripción',
                    'Articulo':              'Artículo',
                    'Fecha':                 'Fecha',
                    'CantidadVendida':       'Cant. Vendida',
                    'PrecioDeVenta':         'Precio Venta',
                    'Ingresos':              'Ingresos',
                    'IngresosUSD':           'Ingresos USD',
                    'Moneda':                'Moneda',
                })

                # Formatear columnas numéricas
                for col in ['Ingresos', 'Ingresos USD', 'Precio Venta']:
                    if col in df_display.columns:
                        df_display[col] = df_display[col].apply(
                            lambda x: f"${x:,.2f}" if pd.notna(x) else ""
                        )

                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                )