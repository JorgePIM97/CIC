# controlador/ventasReales/categoria_ingresos_controlador.py
from datetime import timedelta
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from vista.base_vista import BaseVista
from modelo.ventas_reales_modelo import VentasRealesModelo
from vista.ventasRealesVista.categoria_ingresos_vista import CategoriaIngresosVista
from vista.ventasRealesVista.clases_ingresos_vista import ClasesIngresosVista
from vista.componentes.sidebar_ventas_real import SideBarVentaReal
from .clases_ingresos_controlador import ClasesIngresosControlador
from vista.componentes.info_filtros import InfoFiltros
from vista.componentes.botones import BotonesApp
from modelo.exceles_modelo import ExcelesModelo
from vista.login.login_vista import LoginVista
from modelo.presupuesto_modelo import PresupuestoModelo

class CategoriaIngresosControlador(BaseVista):
    def __init__(self):
        self.modelo = VentasRealesModelo()
        self.vista_componente = SideBarVentaReal()
        self.vista = CategoriaIngresosVista()
        self.vista_clases = ClasesIngresosVista()
        self.controlador_clases = ClasesIngresosControlador()
        self.info_filtros = InfoFiltros()
        self.botones = BotonesApp()
        self.exceles_modelo = ExcelesModelo()
        self.login_vista = LoginVista()
        self.presupuesto_modelo = PresupuestoModelo()

    def ejecutar_vista_ventas(self):
        self.mostrar_titulo("📈 Ventas por Proyecto")
        
        vendedores_seleccionados, fecha_inicio, fecha_fin = self.vista_componente.mostrar_sidebar_ventasReales(self.modelo)

        año_seleccionado = fecha_inicio.year if fecha_inicio else None

        if not vendedores_seleccionados:
            st.warning("Por favor, selecciona al menos un vendedor para mostrar los datos.")
            return

        # ── Calcular mes_inicio y mes_fin ANTES del spinner ──────────────
        if fecha_inicio and fecha_fin:
            mes_inicio = fecha_inicio.month
            mes_fin = fecha_fin.month
        else:
            mes_inicio = 1
            mes_fin = 12

        año_anterior = (año_seleccionado - 1) if año_seleccionado else None

        with st.spinner("Cargando datos de categorías..."):
            df_categorias = self.obtener_datos_filtrados(vendedores_seleccionados, fecha_inicio, fecha_fin)
            df_clases = self.controlador_clases.obtener_datos_filtrados(vendedores_seleccionados, fecha_inicio, fecha_fin)

            if año_anterior:
                from datetime import date
                fecha_inicio_ant = date(año_anterior, fecha_inicio.month, fecha_inicio.day) if fecha_inicio else None
                fecha_fin_ant    = date(año_anterior, fecha_fin.month,   fecha_fin.day)     if fecha_fin   else None
                df_clases_anterior = self.controlador_clases.obtener_datos_filtrados(
                    vendedores_seleccionados, fecha_inicio_ant, fecha_fin_ant
                )
            else:
                df_clases_anterior = None

        if not df_categorias.empty:
            self.info_filtros.mostrar_info_filtro(vendedores_seleccionados, fecha_inicio, fecha_fin)

            col1, col2 = st.columns([2, 1])
            with col1:
                df_grafica = self.vista.preparar_datos_grafica_pastel(df_categorias)
                if not df_grafica.empty:
                    fig = self.vista.crear_grafica_pastel(df_grafica, vendedores_seleccionados)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No hay datos suficientes para generar la gráfica de pastel")
            with col2:
                self.vista.mostrar_top_categorias(df_categorias, 9)

            st.markdown("---")

            if año_seleccionado:
                st.subheader("📈 Ventas Mensuales General")

                df_presupuesto_actual = self.presupuesto_modelo.obtener_presupuesto_anual_vendedores(
                    vendedores_seleccionados, año_seleccionado, mes_inicio, mes_fin
                )

                self.vista_clases.generar_grafica_lineas_ingresos_mensuales(
                    df_clases,
                    vendedores_seleccionados,
                    año_seleccionado,
                    df_metas=df_presupuesto_actual,
                    df_clases_anterior=df_clases_anterior,
                    # df_metas_anterior=...   ← eliminar esta línea completamente
                )

                df_ingresos_mensuales_vendedores = self.obtener_ingresos_mensuales_filtrados(
                    vendedores_seleccionados, año_seleccionado, fecha_inicio, fecha_fin
                )
                st.subheader("📈 Ventas Mensuales por Vendedor")
                self.vista_clases.generar_grafica_lineas_por_vendedor(df_ingresos_mensuales_vendedores)

                st.markdown("---")

            self.vista.mostrar_tabla_categorias(df_categorias)


        else:
            st.error("No se pudieron cargar los datos de categorías para los filtros seleccionados")
            st.info("Verifica que:")
            st.write("- Los vendedores seleccionados tengan datos en el período")
            st.write("- El rango de fechas contenga información")
            st.write("- La conexión a la base de datos esté funcionando")

    def obtener_datos_filtrados(self, vendedores_lista, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene los datos según los filtros aplicados para múltiples vendedores
        """
        df_total = pd.DataFrame()
        
        try:
            for vendedor in vendedores_lista:
                if vendedor == "Piso":
                    df_temp = self.modelo.obtener_categoria_ingresos_piso(fecha_inicio, fecha_fin)
                else:
                    df_temp = self.modelo.obtener_categoria_ingresos_vendedor(vendedor, fecha_inicio, fecha_fin)
                
                # Agregar columna con el nombre del vendedor para identificación
                if not df_temp.empty:
                    df_temp['Vendedor'] = vendedor
                    df_total = pd.concat([df_total, df_temp], ignore_index=True)
                else:
                    st.info(f"No se encontraron datos para {vendedor} en el período seleccionado")
            
            # Verificar si tenemos datos agregados
            if df_total.empty:
                st.warning("No se encontraron datos para ninguno de los vendedores seleccionados")
                return pd.DataFrame()
            
            # Validar estructura de datos
            columnas_requeridas = ['Categoria', 'TotalIngresosUSD']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df_total.columns]
            
            if columnas_faltantes:
                st.error(f"Faltan columnas requeridas en los datos: {columnas_faltantes}")
                st.write("Columnas disponibles:", df_total.columns.tolist())
                return pd.DataFrame()
            
            return df_total
            
        except Exception as e:
            st.error(f"Error al obtener datos filtrados: {str(e)}")
            return pd.DataFrame()
        

    def validar_datos(self, df):
        """
        Valida que los datos tienen la estructura correcta
        """
        if df.empty:
            return False, "DataFrame vacío"
        
        columnas_requeridas = ['Categoria', 'TotalIngresosUSD']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        
        if columnas_faltantes:
            return False, f"Faltan columnas: {columnas_faltantes}"
        
        # Verificar que TotalIngresosUSD es numérico
        if not pd.api.types.is_numeric_dtype(df['TotalIngresosUSD']):
            return False, "La columna TotalIngresosUSD debe ser numérica"
        
        return True, "Datos válidos"
    
    """
    def obtener_datos_totales_filtrados(self, vendedores_lista, fecha_inicio=None, fecha_fin=None):

        # Combinar datos de todos los vendedores seleccionados
        df_total = pd.DataFrame()
        
        for vendedor in vendedores_lista:
            if vendedor == "Piso":
                df_temp = self.modelo.obtener_total_ingresos_piso(fecha_inicio, fecha_fin)
            else:
                df_temp = self.modelo.obtener_total_ingresos_vendedor(vendedor, fecha_inicio, fecha_fin)
            
            # Agregar columna con el nombre del vendedor para identificación
            if not df_temp.empty:
                df_temp['Vendedor'] = vendedor
                df_total = pd.concat([df_total, df_temp], ignore_index=True)
        
        return df_total
    """

    

    def obtener_ingresos_mensuales_filtrados(self, vendedores_lista, año, fecha_inicio=None, fecha_fin=None):
        """
        Regresa un DataFrame con ingresos mensuales combinados para todos los vendedores seleccionados.
        Columns: RepresentanteDeVentas | Año | Mes | total_ingresos
        """
        df_total = pd.DataFrame()

        for vendedor in vendedores_lista:
            if vendedor == "Piso":
                df_temp = self.modelo.obtener_ingresos_mensuales_piso(año, fecha_inicio, fecha_fin)
            else:
                df_temp = self.modelo.obtener_ingresos_mensuales_vendedor(vendedor, año, fecha_inicio, fecha_fin)

            if not df_temp.empty:
                df_total = pd.concat([df_total, df_temp], ignore_index=True)

        return df_total


