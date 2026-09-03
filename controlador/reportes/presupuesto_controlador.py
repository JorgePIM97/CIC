#\controlador\reportes\presupuesto_controlador.py
import streamlit as st
from vista.base_vista import BaseVista
from vista.presupuesto_vista import PresupuestoVista
from modelo.presupuesto_modelo import PresupuestoModelo
import pandas as pd

class PresupuestoControlador(BaseVista):
    def __init__(self):
        self.presupuesto_vista = PresupuestoVista()
        self.presupuesto_modelo = PresupuestoModelo()

    def ejecutar_vista_presupuesto(self):
        self.mostrar_titulo("📊 Ingresar Presupuesto por Segmento")

        col1, col2 = st.columns([3, 1])
        with col2:
            modo_operacion = st.radio(
                "Elija modo de operación:",
                ["Insertar", "Actualizar"]
            )

        with st.form("Ingrese Presupuesto"):
            vendedor_seleccionado          = self.presupuesto_vista.vendedores_real_selectbox()
            year_seleccionado              = self.presupuesto_vista.year_presupuesto()
            mes_seleccionado               = self.presupuesto_vista.meses_selectbox()

            st.divider()
            st.subheader("Consumibles")
            consumible_mecanizado_plasma   = self.presupuesto_vista.valor_consumible_mecanizado_plasma()
            consumible_manual              = self.presupuesto_vista.valor_consumible_manual()
            refacciones                    = self.presupuesto_vista.valor_refacciones()
            consumible_mecanizado_laser    = self.presupuesto_vista.valor_consumible_mecanizado_laser()
            consumible_mecanizado_oxicorte = self.presupuesto_vista.valor_consumible_mecanizado_oxicorte()

            st.divider()
            st.subheader("Sistemas")
            sis_corte_laser                = self.presupuesto_vista.valor_sis_corte_laser()
            sis_corte_plasma               = self.presupuesto_vista.valor_sis_corte_plasma()
            sis_corte_oxy_water            = self.presupuesto_vista.valor_sis_corte_oxy_water()
            powermax                       = self.presupuesto_vista.valor_powermax()
            robotica                       = self.presupuesto_vista.valor_robotica()

            submit_button = st.form_submit_button("Guardar Presupuesto", use_container_width=True)

            if submit_button:
                if not vendedor_seleccionado:
                    st.error("Por favor selecciona un vendedor")
                else:
                    try:
                        kwargs_base = dict(
                            nombre_vendedor                = vendedor_seleccionado,
                            year_presupuesto               = year_seleccionado,
                            consumible_mecanizado_plasma   = consumible_mecanizado_plasma,
                            consumible_manual              = consumible_manual,
                            refacciones                    = refacciones,
                            consumible_mecanizado_laser    = consumible_mecanizado_laser,
                            consumible_mecanizado_oxicorte = consumible_mecanizado_oxicorte,
                            sis_corte_laser                = sis_corte_laser,
                            sis_corte_plasma               = sis_corte_plasma,
                            sis_corte_oxy_water            = sis_corte_oxy_water,
                            powermax                       = powermax,
                            robotica                       = robotica,
                        )

                        if mes_seleccionado == 'Todos los meses':
                            # Siempre usa insertar_o_actualizar para cada mes
                            self.presupuesto_modelo.insertar_o_actualizar_todos_los_meses(**kwargs_base)

                        else:
                            kwargs = {**kwargs_base, 'mes_presupuesto': mes_seleccionado}
                            if modo_operacion == "Actualizar":
                                self.presupuesto_modelo.insertar_o_actualizar_presupuesto(**kwargs)
                            else:
                                self.presupuesto_modelo.insertar_presupuesto(**kwargs)

                    except Exception as e:
                        st.error(f"Error inesperado al procesar el presupuesto: {e}")
        # ──────────────────────────────────────────────────────────────────────
        # TABLA DE PRESUPUESTOS GUARDADOS
        # ──────────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("📋 Presupuestos Registrados")

        MESES_ORDEN = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]

        # Cargar todos los registros
        df_todos = self.presupuesto_modelo.obtener_todas_los_presupuestos()

        if df_todos.empty:
            st.info("ℹ️ No hay presupuestos registrados aún.")
        else:
            # ── Filtros ────────────────────────────────────────────────────────
            with st.expander("🔍 Filtros", expanded=True):
                col_v, col_m, col_a = st.columns(3)

                with col_v:
                    vendedores_disponibles = sorted(df_todos['NombreVendedor'].dropna().unique().tolist())
                    vendedor_filtro = st.selectbox(
                        "Vendedor",
                        options=["Todos"] + vendedores_disponibles,
                        key="filtro_tabla_vendedor"
                    )

                with col_m:
                    meses_disponibles = [
                        m for m in MESES_ORDEN
                        if m in df_todos['MesPresupuesto'].unique()
                    ]
                    mes_filtro = st.selectbox(
                        "Mes",
                        options=["Todos"] + meses_disponibles,
                        key="filtro_tabla_mes"
                    )

                with col_a:
                    años_disponibles = sorted(df_todos['YearPresupuesto'].dropna().unique().tolist(), reverse=True)
                    año_filtro = st.selectbox(
                        "Año",
                        options=["Todos"] + [str(a) for a in años_disponibles],
                        key="filtro_tabla_año"
                    )

            # ── Aplicar filtros ────────────────────────────────────────────────
            df_filtrado = df_todos.copy()

            if vendedor_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado['NombreVendedor'] == vendedor_filtro]

            if mes_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado['MesPresupuesto'] == mes_filtro]

            if año_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado['YearPresupuesto'] == int(año_filtro)]

            # ── Mostrar conteo y tabla ─────────────────────────────────────────
            st.caption(f"Mostrando **{len(df_filtrado)}** registro(s) de **{len(df_todos)}** en total")

            if df_filtrado.empty:
                st.warning("⚠️ No se encontraron registros con los filtros seleccionados.")
            else:
                # Columnas a mostrar y sus etiquetas
                columnas_display = {
                    'NombreVendedor':              'Vendedor',
                    'MesPresupuesto':              'Mes',
                    'YearPresupuesto':             'Año',
                    'ConsumibleMecanizadoPlasma':  'C. Mec. Plasma',
                    'ConsumibleManual':            'C. Manual',
                    'Refacciones':                 'Refacciones',
                    'ConsumibleMecanizadoLaser':   'C. Mec. Láser',
                    'ConsumibleMecanizadoOxicorte':'C. Mec. Oxicorte',
                    'SisCorteLaser':               'Sis. Corte Láser',
                    'SisCortePlasma':              'Sis. Corte Plasma',
                    'SisCorteOxyWater':            'Sis. Oxy/Water',
                    'Powermax':                    'Powermax',
                    'Robotica':                    'Robótica',
                    'FechaRegistro':               'Fecha Registro',
                }

                df_display = df_filtrado[list(columnas_display.keys())].rename(columns=columnas_display)

                # Formatear columnas numéricas como moneda
                cols_moneda = [
                    'C. Mec. Plasma', 'C. Manual', 'Refacciones',
                    'C. Mec. Láser', 'C. Mec. Oxicorte', 'Sis. Corte Láser',
                    'Sis. Corte Plasma', 'Sis. Oxy/Water', 'Powermax', 'Robótica'
                ]
                for col in cols_moneda:
                    if col in df_display.columns:
                        df_display[col] = df_display[col].apply(
                            lambda x: f"${x:,.2f}" if pd.notna(x) else "$0.00"
                        )

                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                )