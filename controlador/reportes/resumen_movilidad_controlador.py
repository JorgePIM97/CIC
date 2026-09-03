import streamlit as st
from vista.base_vista import BaseVista
from vista.resumen_movilidad_vista import ResumenMovilidadVista
from modelo.resumen_movilidad_modelo import ResumenMovilidadModelo


class ResumenMovilidadControlador(BaseVista):

    def __init__(self):
        self.resumen_movilidad = ResumenMovilidadVista()
        self.modelo = ResumenMovilidadModelo()


    def ejecutar_vista_resumen(self):

        self.mostrar_titulo("📊 Ingresar Resumen de Movilidad Mensual 🚗")

        col1, col2 = st.columns([3,1])

        with col2:

            modo_operacion = st.radio(
                "Modo operación:",
                ["Insertar", "Actualizar"]
            )


        with st.form("form_resumen_movilidad"):

            vendedor = self.resumen_movilidad.vendedores_real_selectbox()

            mes = self.resumen_movilidad.meses_selectbox()

            year = self.resumen_movilidad.year_resumen_movilidad()

            dias_habiles = self.resumen_movilidad.valor_dias_habiles_input()

            avg_recorrido = self.resumen_movilidad.valor_avg_recorrido_input()

            cantidad_visitas = self.resumen_movilidad.valor_cantidad_visitas_input()

            tiempo_atencion = self.resumen_movilidad.valor_tiempo_atencion_input()

            tiempo_cliente = self.resumen_movilidad.valor_tiempo_cliente_input()

            avg_visitas_dia = self.resumen_movilidad.valor_avg_visitas_dia_input()

            submit = st.form_submit_button(
                "Guardar Resumen",
                use_container_width=True
            )


            if submit:

                if not vendedor:

                    st.error("Selecciona un vendedor")

                else:

                    try:

                        if modo_operacion == "Actualizar":

                            self.modelo.insertar_o_actualizar_resumen(
                                vendedor,
                                dias_habiles,
                                mes,
                                avg_recorrido,
                                cantidad_visitas,
                                tiempo_atencion,
                                tiempo_cliente,
                                avg_visitas_dia,
                                year
                            )
                            # self.limpiar_inputs()

                        else:

                            self.modelo.insertar_resumen(
                                vendedor,
                                dias_habiles,
                                mes,
                                avg_recorrido,
                                cantidad_visitas,
                                tiempo_atencion,
                                tiempo_cliente,
                                avg_visitas_dia,
                                year
                            )
                            # self.limpiar_inputs()

                    except Exception as e:

                        st.error(f"Error inesperado: {e}")

        # 📊 Mostrar registros existentes
        st.divider()
        st.subheader("📋 Registros de Resumen de Movilidad")

        df_resumen = self.modelo.obtener_resumenes()

        if not df_resumen.empty:

            st.dataframe(
                df_resumen,
                use_container_width=True
            )

        else:

            st.info("No hay registros de resumen de movilidad")


    # def limpiar_inputs(self):

    #     st.session_state["dias_habiles"] = 0
    #     st.session_state["avg_recorrido"] = 0.0
    #     st.session_state["cantidad_visitas"] = 0
    #     st.session_state["tiempo_atencion"] = 0.0
    #     st.session_state["tiempo_cliente"] = 0.0
    #     st.session_state["avg_visitas_dia"] = 0