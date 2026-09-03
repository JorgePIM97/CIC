# vista/vendedores_vista.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from dateutil.relativedelta import relativedelta
from modelo.vendedores_registrados import VendedoresRegistrados
from .login.login_vista import LoginVista

class VendedoresVista:
    def __init__(self):
        self.vendedores = VendedoresRegistrados()
        self.login_vista = LoginVista()

        self.opciones_cuadrantes = [
            "Ninguno",
            "Ventas vs GPS",
            "Ventas Estimadas vs Movilidad",
            "Visitas vs Ventas",
            "Visitas Generales vs Movilidad",
            "Visitas vs Movilidad",
            "Tareas vs Actividades",
            "Actividades vs Movilidad",
            "Tiempos vs Visitas",
            "Tiempos Promedio vs Visitas"           
        ]

        self.opciones_cuadrantes_master = [
            "Ninguno",
            "Ventas vs GPS",
            "Ventas Estimadas vs Movilidad",
            "Ventas Reales vs Movilidad",
            "Visitas vs Ventas Estimadas",
            "Visitas vs Ventas Reales",
            "Visitas Generales vs Movilidad",
            "Visitas vs Movilidad",
            "Tareas vs Actividades",
            "Actividades vs Movilidad",
            "Tiempos vs Visitas",
            "Tiempos Promedio vs Visitas"           
        ]

    

    def configurar_pagina(self):
        """Configura la página de Streamlit"""
        st.set_page_config(
            page_title="Análisis de Vendedores - Cuadrante de Gartner",
            page_icon="📊",
            layout="wide"
        )
    
    def mostrar_titulo(self, titulo_vista: str):
        """Muestra el título principal"""
        st.title(titulo_vista)
        st.markdown("---")
    


    def mostrar_opciones_comparacion(self):
        get_cargo = self.login_vista.get_cargo_de_sesion()
        if get_cargo == 'CEO':

            cuadrante_comparacion = st.sidebar.selectbox(
                "Seleccionar cuadrante para comparar:",
                self.opciones_cuadrantes_master,
                key="cuadrante_comparacion"
            )
        elif get_cargo == 'DIRECTOR DE PRODUCCION':

            cuadrante_comparacion = st.sidebar.selectbox(
                "Seleccionar cuadrante para comparar:",
                self.opciones_cuadrantes_master,
                key="cuadrante_comparacion"
            )
        elif get_cargo == 'DIRECTOR COMERCIAL':

            cuadrante_comparacion = st.sidebar.selectbox(
                "Seleccionar cuadrante para comparar:",
                self.opciones_cuadrantes_master,
                key="cuadrante_comparacion"
            )
        else:
            cuadrante_comparacion = st.sidebar.selectbox(
                "Seleccionar cuadrante para comparar:",
                self.opciones_cuadrantes,
                key="cuadrante_comparacion"
            )            
            
        return cuadrante_comparacion


    """---------------------------------------------------------------
        Muestra la barra lateral con selector de vendedores y fechas
       ---------------------------------------------------------------
    """
    def mostrar_sidebar_cuadrantes(self):
        """Muestra la barra lateral con controles"""
        
        st.sidebar.header("📅 Rango de fechas")
        
        # Fechas
        col1, col2 = st.sidebar.columns(2)
        with col1:
            # Fecha de inicio: un mes antes del mes actual
            fecha_inicio_default = date.today().replace(day=1) - relativedelta(months=1)
            fecha_inicio = st.date_input("Inicio", fecha_inicio_default)
        
        with col2:
            # Fecha de fin: fecha actual
            fecha_fin = st.date_input("Fin", date.today())

        from .seleccion_usuarios.seleccion import SeleccionUsuarios
        seleccion_usuarios = SeleccionUsuarios()
        vendedores = seleccion_usuarios.vendedores_selector()

        # AGREGAR SELECTOR DE CUADRANTE PARA COMPARAR
        st.sidebar.header("📌 Comparación de Cuadrantes")

        cuadrante_comparacion = self.mostrar_opciones_comparacion()

        return fecha_inicio, fecha_fin, vendedores, cuadrante_comparacion
    
    def crear_cuadrante_gartner(
            self, 
            df, 
            limite_y, 
            limite_x, 
            limite_grafico_y=None, 
            limite_grafico_x=None,
            x_df_cuadrante=None,
            y_df_cuadrante=None,
            x_title="Eje X",
            y_title="Eje Y",
            colores=None,
            y_leyend="Eje Y",
            x_leyend="Eje X"
        ):
        """Crea el cuadrante de Gartner con Plotly ajustando automáticamente los límites del gráfico."""

        # --- Validar y limpiar datos ---
        df = df[(df[x_df_cuadrante] >= 0) & (df[y_df_cuadrante] >= 0)]

        if df.empty:
            st.warning("No hay datos positivos para mostrar en el cuadrante.")
            return go.Figure()

        # --- Calcular límites dinámicos ---
        max_x = df[x_df_cuadrante].max()
        max_y = df[y_df_cuadrante].max()

        # Si no se pasan límites manuales, ajustarlos automáticamente con un margen
        limite_grafico_x = limite_grafico_x or (max_x * 1.1 if max_x > 0 else 10)
        limite_grafico_y = limite_grafico_y or (max_y * 1.1 if max_y > 0 else 10)

        # --- Crear figura ---
        fig = go.Figure()

        # --- Trazar puntos por cuadrante ---
        for cuadrante in df['Cuadrante'].unique():
            df_cuadrante = df[df['Cuadrante'] == cuadrante]

            fig.add_trace(go.Scatter(
                x=df_cuadrante[x_df_cuadrante],
                y=df_cuadrante[y_df_cuadrante],
                mode='markers+text',
                marker=dict(
                    size=30,
                    color=(colores or {}).get(cuadrante, '#666666'),
                    opacity=0.8,
                    line=dict(width=2, color='white')
                ),
                text=df_cuadrante['SalesRepId_Value'].str.split().str[0],
                textposition="top center",
                textfont=dict(size=18, color='black'),
                name=cuadrante,
                hovertemplate=(
                    f"<b>%{{text}}</b><br>" +
                    f"{y_leyend}: %{{y:,.0f}}<br>" +
                    f"{x_leyend}: %{{x:,.1f}}<br>" +
                    "<extra></extra>"
                )
            ))

        # --- Líneas de referencia ---
        fig.add_hline(y=limite_y, line_dash="dash", line_color="gray", opacity=0.7)
        fig.add_vline(x=limite_x, line_dash="dash", line_color="gray", opacity=0.7)

        # --- Configuración del layout ---
        fig.update_layout(
            xaxis_title=x_title,
            yaxis_title=y_title,
            width=800,
            height=650,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            xaxis=dict(
                range=[0, limite_grafico_x],
                title_font=dict(size=22),
                zeroline=True,
                zerolinecolor='gray',
                constrain='domain'
            ),
            yaxis=dict(
                range=[0, limite_grafico_y],
                title_font=dict(size=22),
                zeroline=True,
                zerolinecolor='gray',
                constrain='domain'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        return fig


    
    def crear_grafica_pastel(self):
        pass
    
    def mostrar_grafico(self, fig):
        """Muestra el gráfico de Plotly"""
        st.plotly_chart(fig, use_container_width=True)
    
    def mostrar_metricas_vendedores(self, df):
        """Muestra las métricas principales"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Vendedores", len(df))
        
        with col2:
            st.metric("Total Estimado Ventas", f"${df['TotalVendido'].sum():,.0f} USD")


    def mostrar_metricas_ventas_reales(self, df):
        """Muestra las métricas principales"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Vendedores", len(df))
        
        with col2:
            st.metric("Total Ventas", f"${df['TotalVendido'].sum():,.0f} USD")


    def mostrar_metricas_visitas_movilidad(self, df):
        """Muestra las métricas principales"""
        col1, col2, col3, col4 = st.columns(4)
            
        with col1:
            st.metric("Total Vendedores", len(df))
            
        with col2:
            st.metric("Total Visitas", f"{df['TotalVisitas'].sum():,.0f}")

    def mostrar_metricas_visitas_general_movilidad(self, df):
        """Muestra las métricas principales"""
        col1, col2, col3, col4 = st.columns(4)
            
        with col1:
            st.metric("Total Vendedores", len(df))
            
        with col2:
            st.metric("Total Visitas Generales", f"{df['TotalVisitasGeneral'].sum():,.0f}")
            
    def mostrar_metricas_visitas_ventas(self, df):
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
            
        with col1:
            st.metric("Total Vendedores", len(df))
            
        with col2:
            st.metric("Total Visitas", f"{df['TotalVisitas'].sum():,.0f}")
            
        with col3:
            st.metric("Total Estimado Ventas", self.formatear_moneda(df['TotalVendido'].sum()))

    def mostrar_metricas_visitas_ventasReales(self, df):
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
            
        with col1:
            st.metric("Total Vendedores", len(df))
            
        with col2:
            st.metric("Total Visitas", f"{df['TotalVisitas'].sum():,.0f}")
            
        with col3:
            st.metric("Total Ventas", self.formatear_moneda(df['TotalVendido'].sum()))
            
    def mostrar_metricas_tareas_actividades(self, df):
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Vendedores", len(df))
        
        with col2:
            st.metric("Total Actividades", f"{df['TotalActividades'].sum():,.0f}")
        
        with col3:
            st.metric("Total Tareas", f"{df['TotalTareas'].sum():,.0f}")
        
        with col4:
            ratio_promedio = df['TotalActividades'].sum() / max(df['TotalTareas'].sum(), 1)
            st.metric("Ratio Actividades/Tareas", f"{ratio_promedio:.2f}")

    def mostrar_metricas_actividades_movilidad(self, df):
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Vendedores", len(df))
        
        with col2:
            st.metric("Total Actividades", f"{df['TotalActividades'].sum():,.0f}")
        
        with col3:
            st.metric("Km Total", f"{df['KilometrajeAcumulado'].sum():,.1f}")
        
        with col4:
            promedio_actividades = df['TotalActividades'].mean()
            st.metric("Promedio Actividades", f"{promedio_actividades:,.0f}")

    def mostrar_metricas_tiempo_movilidad(self, df):
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Vendedores", len(df))
        
        with col2:
            st.metric("Total Visitas", f"{df['TotalVisitas'].sum():,.0f}")
        
        with col3:
            st.metric("Total Horas", f"{df['TotalHoras'].sum():,.1f}")
        
        with col4:
            promedio_horas = df['TotalHoras'].sum() / df['TotalVisitas'].sum() if df['TotalVisitas'].sum() > 0 else 0
            st.metric("Promedio hrs/visita", f"{promedio_horas:.1f}")

    def mostrar_metricas_tiempoPromedio_movilidad(self, df):
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Vendedores", len(df))
        
        with col2:
            st.metric("Total Visitas", f"{df['TotalVisitas'].sum():,.0f}")
        
        with col3:
            st.metric("Total Promedio", f"{df['PromedioHoras'].sum():,.1f}")
        
        # with col4:
        #     promedio_horas = df['PromedioHoras'].sum() / df['TotalVisitas'].sum() if df['TotalVisitas'].sum() > 0 else 0
        #     st.metric("Promedio hrs/visita", f"{promedio_horas:.1f}")

    def formatear_moneda(self, valor):
        """Formatea valores monetarios en pesos mexicanos"""
        return f"${valor:,.2f}"


    def mostrar_tabla_ventas_movilidad(self, df_clasificado):
        """Muestra la tabla de resultados"""
        st.markdown("### 📋 Detalle Estimado")
        
        # Ordenar por cuadrante y ventas
        df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVendido'], ascending=[True, False])
        
        # Formatear tabla
        df_display = df_tabla.copy()
        df_display['Total Vendido'] = df_display['TotalVendido'].apply(lambda x: f"${x:,.0f}")
        df_display['Kilometraje'] = df_display['KilometrajeAcumulado'].apply(lambda x: f"{x:,.1f} km")
        
        st.dataframe(
            df_display[['SalesRepId_Value', 'Total Vendido', 'Kilometraje']],
            column_config={
                'SalesRepId_Value': 'Vendedor',
                'Total Vendido': 'Total Estimado Vendido (USD)',
                'Kilometraje': 'Km Recorridos'
            },
            hide_index=True,
            use_container_width=True
        )

    def mostrar_tabla_ventas_reales_movilidad(self, df_clasificado):
        """Muestra la tabla de resultados"""
        st.markdown("### 📋 Detalle Real")
        
        # Ordenar por cuadrante y ventas
        df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVendido'], ascending=[True, False])
        
        # Formatear tabla
        df_display = df_tabla.copy()
        df_display['Total Vendido'] = df_display['TotalVendido'].apply(lambda x: f"${x:,.0f}")
        df_display['Kilometraje'] = df_display['KilometrajeAcumulado'].apply(lambda x: f"{x:,.1f} km")
        
        st.dataframe(
            df_display[['SalesRepId_Value', 'Total Vendido', 'Kilometraje']],
            column_config={
                'SalesRepId_Value': 'Vendedor',
                'Total Vendido': 'Total Vendido (USD)',
                'Kilometraje': 'Km Recorridos'
            },
            hide_index=True,
            use_container_width=True
        )    

    def mostrar_tabla_ventasForce_gps(self, df_clasificado):
        # Tabla de resultados
        st.markdown("### 📋 Detalle por Vendedor")
        
        # Ordenar por cuadrante y ventas
        df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVendido'], ascending=[True, False])
        
        # Formatear tabla
        df_display = df_tabla.copy()
        df_display['Total Vendido'] = df_display['TotalVendido'].apply(lambda x: f"${x:,.0f}")
        df_display['Kilometraje'] = df_display['KilometrajeAcumulado'].apply(lambda x: f"{x:,.1f} km")
        df_display['Eficiencia'] = df_display.apply(
            lambda row: f"${row['TotalVendido']/row['KilometrajeAcumulado']:,.0f}/km" 
            if row['KilometrajeAcumulado'] > 0 else "N/A", axis=1
        )
        
        st.dataframe(
            df_display[['SalesRepName', 'Total Vendido', 'Kilometraje']],
            column_config={
                'SalesRepName': 'Vendedor',
                'Total Vendido': 'Ventas',
                'Kilometraje': 'Km Recorridos',
                # 'Eficiencia': 'Eficiencia',
                # 'Cuadrante': 'Clasificación'
            },
            hide_index=True,
            use_container_width=True
        )   

    def mostrar_tabla_ventasReales_gps(self, df_clasificado):
        # Tabla de resultados
        st.markdown("### 📋 Detalle por Vendedor")
        
        # Ordenar por cuadrante y ventas
        df_tabla = df_clasificado.sort_values(['Cuadrante', 'IngresosUSD'], ascending=[True, False])
        
        # Formatear tabla
        df_display = df_tabla.copy()
        df_display['Ventas Reales'] = df_display['IngresosUSD'].apply(lambda x: f"${x:,.0f}")
        df_display['Kilometraje'] = df_display['KilometrajeAcumulado'].apply(lambda x: f"{x:,.1f} km")
        df_display['Eficiencia'] = df_display.apply(
            lambda row: f"${row['IngresosUSD']/row['KilometrajeAcumulado']:,.0f}/km" 
            if row['KilometrajeAcumulado'] > 0 else "N/A", axis=1
        )
        
        st.dataframe(
            df_display[['SalesRepName', 'Ventas Reales', 'Kilometraje']],
            column_config={
                'SalesRepName': 'Vendedor',
                'Ventas Reales': 'Ventas (USD)',
                'Kilometraje': 'Km Recorridos',
                # 'Eficiencia': 'Eficiencia',
                # 'Cuadrante': 'Clasificación'
            },
            hide_index=True,
            use_container_width=True
        )

    def mostrar_tabla_visitas_movilidad(self, df_clasificado):
        # Tabla de resultados
            st.markdown("### 📋 Detalle por Vendedor")
            
            # Ordenar por cuadrante y visitas
            df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVisitas'], ascending=[True, False])
            
            # Formatear tabla
            df_display = df_tabla.copy()
            df_display['Visitas'] = df_display['TotalVisitas'].apply(lambda x: f"{x:,.0f}")
            df_display['Kilometraje'] = df_display['KilometrajeAcumulado'].apply(lambda x: f"{x:,.1f} km")
            
            st.dataframe(
                df_display[['SalesRepId_Value', 'Visitas', 'Kilometraje', 'Descripcion']],
                column_config={
                    'SalesRepId_Value': 'Vendedor',
                    # 'Cuadrante': 'Clasificación',
                    'Visitas': 'Total Visitas',
                    'Kilometraje': 'Km Recorridos',
                    'Descripcion': 'Descripción'
                },
                hide_index=True,
                use_container_width=True
            )


    def mostrar_tabla_visitas_general_movilidad(self, df_clasificado):
        # Tabla de resultados
            st.markdown("### 📋 Detalle por Vendedor")
            
            # Ordenar por cuadrante y visitas
            df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVisitasGeneral'], ascending=[True, False])
            
            # Formatear tabla
            df_display = df_tabla.copy()
            df_display['Visitas'] = df_display['TotalVisitasGeneral'].apply(lambda x: f"{x:,.0f}")
            df_display['Kilometraje'] = df_display['KilometrajeAcumulado'].apply(lambda x: f"{x:,.1f} km")
            
            st.dataframe(
                df_display[['SalesRepId_Value', 'Visitas', 'Kilometraje', 'Descripcion']],
                column_config={
                    'SalesRepId_Value': 'Vendedor',
                    # 'Cuadrante': 'Clasificación',
                    'Visitas': 'Total Visitas Generales',
                    'Kilometraje': 'Km Recorridos',
                    'Descripcion': 'Descripción'
                },
                hide_index=True,
                use_container_width=True
            )


    def mostrar_tabla_visitas_ventas(self, df_clasificado):
        # Tabla de resultados
        st.markdown("### 📋 Detalle Estimado")
        
        # Ordenar por cuadrante y ventas
        df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVendido'], ascending=[True, False])
        
        # Formatear tabla
        df_display = df_tabla.copy()
        df_display['Visitas'] = df_display['TotalVisitas'].apply(lambda x: f"{x:,.0f}")
        df_display['Ventas'] = df_display['TotalVendido'].apply(lambda x: self.formatear_moneda(x))
        df_display['Num_Ventas'] = df_display['NumVentas'].apply(lambda x: f"{x:,.0f}")
        
        # Calcular efectividad por vendedor
        df_display['Efectividad'] = df_display.apply(
            lambda row: f"{(row['NumVentas'] / row['TotalVisitas'] * 100):.1f}%" if row['TotalVisitas'] > 0 else "0%", 
            axis=1
        )
        
        st.dataframe(
            df_display[['SalesRepId_Value', 'Visitas', 'Num_Ventas', 'Ventas']],
            column_config={
                'SalesRepId_Value': 'Vendedor',
                #'Cuadrante': 'Clasificación',
                'Visitas': 'Total Visitas',
                'Num_Ventas': 'Núm. Ventas',
                'Ventas': 'Total Estimado Vendido (USD)'
                # 'Efectividad': 'Efectividad',
                # 'Descripcion': 'Descripción'
            },
            hide_index=True,
            use_container_width=True
        )

    def mostrar_tabla_tareas_actividades(self, df_clasificado):
         # Tabla de resultados
        st.markdown("### 📋 Detalle por Vendedor")
        
        # Calcular ratio para cada vendedor
        df_clasificado['Ratio'] = df_clasificado['TotalActividades'] / df_clasificado['TotalTareas'].replace(0, 1)
        
        # Ordenar por cuadrante y actividades
        df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalActividades'], ascending=[True, False])
        
        # Formatear tabla
        df_display = df_tabla.copy()
        df_display['Actividades'] = df_display['TotalActividades'].apply(lambda x: f"{x:,.0f}")
        df_display['Tareas'] = df_display['TotalTareas'].apply(lambda x: f"{x:,.0f}")
        df_display['Ratio_Formatted'] = df_display['Ratio'].apply(lambda x: f"{x:.2f}")
        
        st.dataframe(
            df_display[['SalesRepId_Value', 'Actividades', 'Tareas', 'Ratio_Formatted', 'Descripcion']],
            column_config={
                'SalesRepId_Value': 'Vendedor',
                #'Cuadrante': 'Clasificación',
                'Actividades': 'Total Actividades',
                'Tareas': 'Total Tareas',
                'Ratio_Formatted': 'Ratio Act/Tar',
                'Descripcion': 'Descripción'
            },
            hide_index=True,
            use_container_width=True
        )

    def mostrar_tabla_actividades_movilidad(self, df_clasificado):
        # Tabla de resultados
        st.markdown("### 📋 Detalle por Vendedor")
        
        # Ordenar por cuadrante y actividades
        df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalActividades'], ascending=[True, False])
        
        # Formatear tabla
        df_display = df_tabla.copy()
        df_display['Actividades'] = df_display['TotalActividades'].apply(lambda x: f"{x:,.0f}")
        df_display['Kilometraje'] = df_display['KilometrajeAcumulado'].apply(lambda x: f"{x:,.1f} km")
        
        st.dataframe(
            df_display[['SalesRepId_Value', 'Actividades', 'Kilometraje', 'Descripcion']],
            column_config={
                'SalesRepId_Value': 'Vendedor',
                # 'Cuadrante': 'Clasificación',
                'Actividades': 'Total Actividades',
                'Kilometraje': 'Km Recorridos',
                'Descripcion': 'Descripción'
            },
            hide_index=True,
            use_container_width=True
        )
    
    def mostrar_tabla_tiempo_visitas(self, df_clasificado):
        # Tabla de resultados
            st.markdown("### 📋 Detalle por Vendedor")
            
            # Ordenar por cuadrante y visitas
            df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVisitas'], ascending=[True, False])
            
            # Calcular eficiencia (horas por visita)
            df_tabla['EficienciaHrsVisita'] = df_tabla.apply(
                lambda row: row['TotalHoras'] / row['TotalVisitas'] if row['TotalVisitas'] > 0 else 0, 
                axis=1
            )
            
            # Formatear tabla
            df_display = df_tabla.copy()
            df_display['Visitas'] = df_display['TotalVisitas'].apply(lambda x: f"{x:,.0f}")
            df_display['Horas'] = df_display['TotalHoras'].apply(lambda x: f"{x:,.1f}")
            df_display['Eficiencia'] = df_display['EficienciaHrsVisita'].apply(lambda x: f"{x:.1f} hrs/visita")
            
            st.dataframe(
                df_display[['SalesRepId_Value', 'Visitas', 'Horas']],
                column_config={
                    'SalesRepId_Value': 'Vendedor',
                    # 'Cuadrante': 'Clasificación',
                    'Visitas': 'Total Visitas',
                    'Horas': 'Total Horas'
                    # 'Eficiencia': 'Eficiencia',
                    # 'Descripcion': 'Descripción'
                },
                hide_index=True,
                use_container_width=True
            )

    def mostrar_tabla_tiempoPromedio_visitas(self, df_clasificado):
        # Tabla de resultados
            st.markdown("### 📋 Detalle por Vendedor")
            
            # Ordenar por cuadrante y visitas
            df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVisitas'], ascending=[True, False])
            
            # # Calcular eficiencia (horas por visita)
            # df_tabla['EficienciaHrsVisita'] = df_tabla.apply(
            #     lambda row: row['TotalHoras'] / row['TotalVisitas'] if row['TotalVisitas'] > 0 else 0, 
            #     axis=1
            # )
            
            # Formatear tabla
            df_display = df_tabla.copy()
            df_display['Visitas'] = df_display['TotalVisitas'].apply(lambda x: f"{x:,.0f}")
            df_display['HorasPromedio'] = df_display['PromedioHoras'].apply(lambda x: f"{x:,.1f}")
            # df_display['Eficiencia'] = df_display['EficienciaHrsVisita'].apply(lambda x: f"{x:.1f} hrs/visita")
            
            st.dataframe(
                df_display[['SalesRepId_Value', 'Visitas', 'HorasPromedio']],
                column_config={
                    'SalesRepId_Value': 'Vendedor',
                    # 'Cuadrante': 'Clasificación',
                    'Visitas': 'Total Visitas',
                    'HorasPromedio': 'Total Horas en Promedio'
                    # 'Eficiencia': 'Eficiencia',
                    # 'Descripcion': 'Descripción'
                },
                hide_index=True,
                use_container_width=True
            )

    def mostrar_tabla_visitas_ventasReales(self, df_clasificado):
        # Tabla de resultados
        st.markdown("### 📋 Detalle Real")
        
        # Ordenar por cuadrante y ventas
        df_tabla = df_clasificado.sort_values(['Cuadrante', 'TotalVendido'], ascending=[True, False])
        
        # Formatear tabla
        df_display = df_tabla.copy()
        df_display['Visitas'] = df_display['TotalVisitas'].apply(lambda x: f"{x:,.0f}")
        df_display['Total Vendido'] = df_display['TotalVendido'].apply(lambda x: f"${x:,.0f}")
        
        # # Calcular efectividad por vendedor
        # df_display['Efectividad'] = df_display.apply(
        #     lambda row: f"{(row['NumVentas'] / row['TotalVisitas'] * 100):.1f}%" if row['TotalVisitas'] > 0 else "0%", 
        #     axis=1
        # )
        
        st.dataframe(
            df_display[['SalesRepId_Value', 'Visitas', 'Total Vendido']],
            column_config={
                'SalesRepId_Value': 'Vendedor',
                'Visitas': 'Total Visitas',
                'Total Vendido': 'Total Vendido (USD)'
            },
            hide_index=True,
            use_container_width=True
        )            
    
    def mostrar_mensaje_error(self, mensaje):
        """Muestra un mensaje de error"""
        st.error(mensaje)
    
    def mostrar_mensaje_warning(self, mensaje):
        """Muestra un mensaje de advertencia"""
        st.warning(mensaje)
    
    def mostrar_mensaje_info(self, mensaje):
        """Muestra un mensaje informativo"""
        st.info(mensaje)
    
    def mostrar_spinner(self, mensaje):
        """Muestra un spinner con mensaje"""
        return st.spinner(mensaje)
    
    def limpiar_cache(self):
        """Limpia el cache de Streamlit"""
        st.cache_data.clear()
        st.cache_resource.clear()