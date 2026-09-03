# controlador/reportes/metas_controlador.py
import streamlit as st
from vista.base_vista import BaseVista
from modelo.metas_modelo import MetasModelo
from vista.metas_vista import MetasVista

class MetasControlador(BaseVista):
    def __init__(self):
        self.metas_modelo = MetasModelo()
        self.vista_metas = MetasVista()


    def ejecutar_vista_metas(self):


        self.mostrar_titulo("📊 Ingresar Presupuesto de Vendedores")

        # Opción para manejar duplicados
        col1, col2 = st.columns([3, 1])
        
        with col2:
            modo_operacion = st.radio(
                "Elija modo de operación:",
                ["Insertar", "Actualizar"]
                # help="'Solo insertar': No permite duplicados\n'Actualizar': Reemplaza la meta existente"
            )

        with st.form("Ingrese Presupuesto"):
            # vendedores reales selectbox 
            vendedor_seleccionado = self.vista_metas.vendedores_real_selectbox()

            year_seleccionado = self.vista_metas.year_meta()

            mes_seleccionado = self.vista_metas.meses_selectbox()

            valor_meta = self.vista_metas.valor_meta_input()

            submit_button = st.form_submit_button("Guardar Presupuesto", use_container_width=True)

            if submit_button:
                # Validaciones básicas
                if not vendedor_seleccionado:
                    st.error("Por favor selecciona un vendedor")
                elif valor_meta <= 0:
                    st.error("El valor de la meta debe ser mayor a 0")
                else:
                    try:
                        if modo_operacion == "Actualizar":
                            # Usar el método que inserta o actualiza
                            self.metas_modelo.insertar_o_actualizar_meta(
                                nombre_vendedor=vendedor_seleccionado,
                                valor_meta=valor_meta,
                                mes_meta=mes_seleccionado,
                                year_meta=year_seleccionado
                            )
                        else:
                            # Solo insertar (no permite duplicados)
                            self.metas_modelo.insertar_meta(
                                nombre_vendedor=vendedor_seleccionado,
                                valor_meta=valor_meta,
                                mes_meta=mes_seleccionado,
                                year_meta=year_seleccionado
                            )
                            
                    except Exception as e:
                        st.error(f"Error inesperado al procesar el presupuesto: {e}")

        # Mostrar metas existentes (opcional)
        self.vista_metas.mostrar_metas_existentes()

