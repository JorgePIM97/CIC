# vista/metas_vista.py
"""
Vista para hacer inserción de metas
"""
import streamlit as st
import datetime
from modelo.metas_modelo import MetasModelo
from .seleccion_usuarios.seleccion import SeleccionUsuarios

class MetasVista:

    def __init__(self):
        self.seleccion_usuarios = SeleccionUsuarios()
        self.metas_modelo = MetasModelo()
        self.meses_año = [
            'Enero',
            'Febrero',
            'Marzo',
            'Abril',
            'Mayo',
            'Junio',
            'Julio',
            'Agosto',
            'Septiembre',
            'Octubre',
            'Noviembre',
            'Diciembre',
        ]


    def mostrar_metas_existentes(self):
        """Muestra las metas existentes para referencia"""
        st.markdown("---")
        st.subheader("📋 Presupuestos Registrados")
        
        try:
            df_metas = self.metas_modelo.obtener_todas_las_metas()
            
            if df_metas.empty:
                st.info("No hay metas registradas todavía.")
            else:
                # Selección de columnas a mostrar
                columnas_mostrar = ["NombreVendedor", "MesMeta", "ValorMeta_Formateado", "FechaRegistro", "YearMeta"]
                df_vista = df_metas[columnas_mostrar].rename(columns={
                    "NombreVendedor": "Vendedor",
                    "MesMeta": "Mes",
                    "ValorMeta_Formateado": "Presupuesto",
                    "FechaRegistro": "Fecha de Registro",
                    "YearMeta": "Año"
                })

                st.dataframe(
                    df_vista,
                    use_container_width=True,
                    hide_index=True
                )
                
        except Exception as e:
            st.warning(f"No se pudieron cargar los presupuestos existentes: {e}")


    def vendedores_real_selectbox(self):
        vendedores = self.seleccion_usuarios.seleccion_privilegiosReal_zona()
        
        if not vendedores:
            st.warning("No hay vendedores disponibles")
            return None
        
        # Selectbox de vendedores (selección individual)
        vendedor_seleccionado = st.selectbox(
            "Seleccionar vendedor:",
            options=vendedores,
            index=0  # Selecciona el primer vendedor por defecto
        )

        return vendedor_seleccionado

    def year_meta(self):
        year_actual = datetime.datetime.now().year
        
        # Genera rango ±3 años
        years = list(range(year_actual - 3, year_actual + 4))
        
        year_meta_seleccionado = st.selectbox(
            "Seleccionar año:",
            options=years,
            index=3  # El año actual queda justo en el centro
        )
        
        return year_meta_seleccionado


    def meses_selectbox(self):
        # Selectbox de meses (selección individual)
        mes_seleccionado = st.selectbox(
            "Seleccionar mes:",
            options=self.meses_año,
            index=0  # Selecciona el primer mes por defecto
        )

        return mes_seleccionado
    
    def valor_meta_input(self):
        valor_meta = st.number_input(
            "Valor del Presupuesto (USD):",
            min_value=0.0,
            value=0.0,  # Valor por defecto
            step=1000.0,  # Incremento de 1000 en 1000
            format="%.2f"  # Formato con 2 decimales
        )

        # Mostrar el valor formateado para mejor legibilidad
        if valor_meta > 0:
            st.caption(f"💰 Meta: ${valor_meta:,.2f}")

        return valor_meta