# controlador/ventasReales/clientes_ingresos_controlador.py
from datetime import timedelta
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from vista.base_vista import BaseVista
from modelo.ventas_reales_modelo import VentasRealesModelo
from vista.ventasRealesVista.clases_ingresos_vista import ClasesIngresosVista
from .clases_ingresos_controlador import ClasesIngresosControlador
from vista.ventasRealesVista.clientes_ingresos_vista import ClientesIngresosVista
from vista.componentes.sidebar_ventas_real import SideBarVentaReal
from vista.componentes.info_filtros import InfoFiltros
from modelo.presupuesto_modelo import PresupuestoModelo


class ClientesIngresosControlador(BaseVista):
    def __init__(self):
        self.modelo = VentasRealesModelo()
        self.vista = ClientesIngresosVista()
        self.vista_componente = SideBarVentaReal()
        self.info_filtros = InfoFiltros()
        self.vista_clases = ClasesIngresosVista()
        self.controlador_clases = ClasesIngresosControlador()
        self.presupuesto_modelo = PresupuestoModelo()
        
    def ejecutar_vista_ventas(self):
        """
        Ejecuta la vista completa de clientes e ingresos con filtros
        """
        # Mostrar título
        self.mostrar_titulo("📈 Ventas por Cliente")
        
        # Mostrar sidebar con filtros
        vendedores_seleccionados, fecha_inicio, fecha_fin = self.vista_componente.mostrar_sidebar_ventasReales(self.modelo)
        
        # Extraer año seleccionado de las fechas
        año_seleccionado = fecha_inicio.year if fecha_inicio else None

        # Verificar que se haya seleccionado al menos un vendedor
        if not vendedores_seleccionados:
            st.warning("Por favor, selecciona al menos un vendedor para mostrar los datos.")
            return

        # Obtener datos según los filtros seleccionados
        with st.spinner("Cargando datos de clientes..."):
            df_clientes = self.obtener_datos_filtrados(vendedores_seleccionados, fecha_inicio, fecha_fin)
            df_clientes_sumatoria = self.obtener_datos_filtrados_sumatoria(vendedores_seleccionados, fecha_inicio, fecha_fin)
            df_clases = self.controlador_clases.obtener_datos_filtrados(vendedores_seleccionados, fecha_inicio, fecha_fin)

            año_anterior = (año_seleccionado - 1) if año_seleccionado else None
            if año_anterior and fecha_inicio and fecha_fin:
                from datetime import date
                fecha_inicio_ant = date(año_anterior, fecha_inicio.month, fecha_inicio.day)
                fecha_fin_ant    = date(año_anterior, fecha_fin.month,   fecha_fin.day)
                df_clases_anterior = self.controlador_clases.obtener_datos_filtrados(vendedores_seleccionados, fecha_inicio_ant, fecha_fin_ant)
            else:
                df_clases_anterior = None

        if not df_clientes.empty:
            # Mostrar información del filtro aplicado
            self.info_filtros.mostrar_info_filtro(vendedores_seleccionados, fecha_inicio, fecha_fin)
            
            # Dividir la pantalla en dos columnas
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Preparar datos para gráfica de pastel
                df_grafica = self.vista.preparar_datos_grafica_pastel(df_clientes)
                
                # Crear y mostrar gráfica de pastel
                fig = self.vista.crear_grafica_pastel(df_grafica, vendedores_seleccionados)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Mostrar top 5 clientes como resumen
                st.subheader("🏆 Top 5 Clientes")
                
                # Agrupar por cliente en caso de múltiples fechas
                df_top = df_clientes.groupby(['NombreCliente']).agg({
                    'ingresos_fact': 'sum'
                }).reset_index().sort_values('ingresos_fact', ascending=False)
                
                top_5 = df_top.head(5)
                for idx, row in top_5.iterrows():
                    st.write(f"**{row['NombreCliente']}**")
                    st.write(f"${row['ingresos_fact']:,.2f} USD")
                    st.write("---")
            
            st.markdown("---")
            # Gráfica de líneas mensuales
            if año_seleccionado:
                st.subheader("📈 Ventas Mensuales General")
                
                # Obtener metas mensuales para los vendedores seleccionados
                # Determinar rango de meses según el filtro
                if fecha_inicio and fecha_fin:
                    mes_inicio = fecha_inicio.month
                    mes_fin = fecha_fin.month
                else:
                    mes_inicio = 1
                    mes_fin = 12
                
                # Obtener las metas
                df_presupuesto_actual = self.presupuesto_modelo.obtener_presupuesto_anual_vendedores(
                    vendedores_seleccionados, año_seleccionado, mes_inicio, mes_fin
                )
                self.vista_clases.generar_grafica_lineas_ingresos_mensuales(
                    df_clases,
                    vendedores_seleccionados,
                    año_seleccionado,
                    df_metas=df_presupuesto_actual,
                    df_clases_anterior=df_clases_anterior,
                )

                # ✅ Nueva gráfica: ingresos mensuales por vendedor
                df_ingresos_mensuales_vendedores = self.obtener_ingresos_mensuales_filtrados(
                    vendedores_seleccionados,
                    año_seleccionado,
                    fecha_inicio,
                    fecha_fin
                )

                st.subheader("📈 Ventas Mensuales por Vendedor")
                self.vista_clases.generar_grafica_lineas_por_vendedor(df_ingresos_mensuales_vendedores)

            st.markdown("---")
            
            # Mostrar tabla completa
            self.vista.mostrar_tabla_clientes(df_clientes_sumatoria, vendedores_seleccionados)
            
            # Botón para descargar datos
            # self.agregar_boton_descarga(df_clientes, vendedores_seleccionados)
        
        else:
            st.error("No se pudieron cargar los datos de clientes para los filtros seleccionados")
    
    def obtener_datos_filtrados(self, vendedores_lista, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene los datos según los filtros aplicados (ahora acepta una lista de vendedores)
        """
        # Combinar datos de todos los vendedores seleccionados
        df_total = pd.DataFrame()
        
        for vendedor in vendedores_lista:
            if vendedor == "Piso":
                df_temp = self.modelo.obtener_clientes_ingresos_piso(fecha_inicio, fecha_fin)
            else:
                df_temp = self.modelo.obtener_clientes_ingresos_vendedor(vendedor, fecha_inicio, fecha_fin)
            
            # Agregar columna con el nombre del vendedor para identificación
            if not df_temp.empty:
                df_temp['Vendedor'] = vendedor
                df_total = pd.concat([df_total, df_temp], ignore_index=True)
        
        return df_total
    
    def obtener_datos_filtrados_sumatoria(self, vendedores_lista, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene los datos según los filtros aplicados (ahora acepta una lista de vendedores)
        """
        # Combinar datos de todos los vendedores seleccionados
        df_total_sumatoria = pd.DataFrame()
        
        for vendedor in vendedores_lista:
            if vendedor == "Piso":
                df_temp = self.modelo.obtener_clientes_ingresos_piso_sumatoria(fecha_inicio, fecha_fin)
            else:
                df_temp = self.modelo.obtener_clientes_ingresos_vendedor_sumatoria(vendedor, fecha_inicio, fecha_fin)
            
            # Agregar columna con el nombre del vendedor para identificación
            if not df_temp.empty:
                df_temp['Vendedor'] = vendedor
                df_total_sumatoria = pd.concat([df_total_sumatoria, df_temp], ignore_index=True)
        
        return df_total_sumatoria
    
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