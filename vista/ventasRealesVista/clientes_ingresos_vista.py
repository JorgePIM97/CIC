# vista/ventasRealesVista/clientes_ingresos_vista.py
"""
Vista para generar gráficas y análisis de clientes_ingresos
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from vista.base_vista import BaseVista
from ..seleccion_usuarios.seleccion import SeleccionUsuarios

class ClientesIngresosVista(BaseVista):
    def __init__(self):
        self.seleccion_usuarios = SeleccionUsuarios()

    
    def preparar_datos_grafica_pastel(self, df):
        """
        Prepara los datos para la gráfica de pastel con top 10 clientes
        """
        if df.empty:
            return pd.DataFrame()
        
        # Agrupar por cliente y sumar ingresos (en caso de múltiples fechas)
        df_agrupado = df.groupby(['NombreCliente', 'NumeroDeDocumento']).agg({
            'ingresos_fact': 'sum'
        }).reset_index()
        
        # Ordenar por ingresos descendente
        df_ordenado = df_agrupado.sort_values('ingresos_fact', ascending=False)
        
        # Top 10 clientes
        top_10 = df_ordenado.head(10).copy()
        
        # Suma de otros clientes (resto)
        otros_ingresos = df_ordenado.iloc[10:]['ingresos_fact'].sum()
        
        # Si hay otros clientes, agregarlos
        if otros_ingresos > 0:
            otros_row = pd.DataFrame({
                'NombreCliente': ['Otros'],
                'NumeroDeDocumento': [''],
                'ingresos_fact': [otros_ingresos]
            })
            df_grafica = pd.concat([top_10, otros_row], ignore_index=True)
        else:
            df_grafica = top_10
        
        return df_grafica
    
    def crear_grafica_pastel(self, df_grafica, vendedor="General"):
        """
        Crea la gráfica de pastel con los datos preparados
        """
        if df_grafica.empty:
            st.warning("No hay datos para mostrar en la gráfica")
            return None
        
        # Crear colores personalizados
        colors = px.colors.qualitative.Set3[:len(df_grafica)]
        
        # Crear gráfica de pastel
        fig = go.Figure(data=[
            go.Pie(
                labels=df_grafica['NombreCliente'],
                values=df_grafica['ingresos_fact'],
                hole=0.3,  # Dona en el centro
                marker=dict(colors=colors),
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>' +
                             'Ventas: $%{value:,.2f} USD<br>' +
                             'Porcentaje: %{percent}<br>' +
                             '<extra></extra>'
            )
        ])
        
        titulo = f'Distribución de Ventas por Cliente'
        
        fig.update_layout(
            title={
                'text': titulo,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=500,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02
            )
        )
        
        return fig
    
    # def mostrar_tabla_clientes(self, df, vendedor="General"):
    #     """
    #     Muestra la tabla completa de clientes e ingresos
    #     """
    #     if df.empty:
    #         st.warning("No hay datos para mostrar en la tabla")
    #         return
        
    #     # Agrupar por cliente y sumar ingresos
    #     df_agrupado = df.groupby(['NombreCliente', 'NumeroDeDocumento']).agg({
    #         'ingresos_fact': 'sum'
    #     }).reset_index()
        
    #     # Formatear la columna de ingresos
    #     df_display = df_agrupado.copy()
    #     df_display['ingresos_fact_formatted'] = df_display['ingresos_fact'].apply(
    #         lambda x: f"${x:,.2f}"
    #     )
        
    #     # Renombrar columnas para mostrar
    #     df_display = df_display.rename(columns={
    #         'NombreCliente': 'Cliente',
    #         'NumeroDeDocumento': 'Número de Documento',
    #         'ingresos_fact_formatted': 'Ventas Totales (USD)'
    #     }).drop(columns=['ingresos_fact'])
        
    #     titulo = f"📊 Tabla de Clientes y Ventas"
    #     # # Título dinámico
    #     # if vendedor == "General":
    #     #     titulo = "📊 Tabla Completa de Clientes e Ingresos - Todos los Vendedores"
    #     # else:
    #     #     titulo = f"📊 Tabla de Clientes e Ingresos - {vendedor}"
            
    #     st.subheader(titulo)
        
    #     # Mostrar métricas resumidas
    #     col1, col2, col3 = st.columns(3)
        
    #     with col1:
    #         total_clientes = len(df_agrupado)
    #         st.metric("Total de Clientes", total_clientes)
        
    #     with col2:
    #         total_ingresos = df_agrupado['ingresos_fact'].sum()
    #         st.metric("Ventas Totales", f"${total_ingresos:,.2f} USD")
        
    #     with col3:
    #         promedio_ingresos = df_agrupado['ingresos_fact'].mean()
    #         st.metric("Promedio por Cliente", f"${promedio_ingresos:,.2f} USD")
        
    #     # Mostrar tabla con paginación y búsqueda
    #     st.dataframe(
    #         df_display,
    #         use_container_width=True,
    #         hide_index=True
    #     )

    def mostrar_tabla_clientes(self, df, vendedor="General"):
        """
        Muestra la tabla completa de clientes e ingresos
        """
        if df.empty:
            st.warning("No hay datos para mostrar en la tabla")
            return
        
        # Agrupar por cliente y sumar ingresos
        df_agrupado = df.groupby(['NombreCliente']).agg({
            'ingresos_fact': 'sum'
        }).reset_index()
        
        # Formatear la columna de ingresos
        df_display = df_agrupado.copy()
        df_display['ingresos_fact_formatted'] = df_display['ingresos_fact'].apply(
            lambda x: f"${x:,.2f}"
        )
        
        # Renombrar columnas para mostrar
        df_display = df_display.rename(columns={
            'NombreCliente': 'Cliente',
            'ingresos_fact_formatted': 'Ventas Totales (USD)'
        }).drop(columns=['ingresos_fact'])
        
        titulo = f"📊 Tabla de Clientes y Ventas"
        # # Título dinámico
        # if vendedor == "General":
        #     titulo = "📊 Tabla Completa de Clientes e Ingresos - Todos los Vendedores"
        # else:
        #     titulo = f"📊 Tabla de Clientes e Ingresos - {vendedor}"
            
        st.subheader(titulo)
        
        # Mostrar métricas resumidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_clientes = len(df_agrupado)
            st.metric("Total de Clientes", total_clientes)
        
        with col2:
            total_ingresos = df_agrupado['ingresos_fact'].sum()
            st.metric("Ventas Totales", f"${total_ingresos:,.2f} USD")
        
        with col3:
            promedio_ingresos = df_agrupado['ingresos_fact'].mean()
            st.metric("Promedio por Cliente", f"${promedio_ingresos:,.2f} USD")
        
        # Mostrar tabla con paginación y búsqueda
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )


    def generar_grafica_lineas_ingresos_mensuales(self, df_clientes, vendedor, año_seleccionado):
        """
        Genera gráfica de líneas con ingresos mensuales para el año seleccionado
        """
        try:
            # Verificar que tenemos datos y año seleccionado
            if df_clientes.empty or not año_seleccionado:
                st.warning("No hay datos disponibles para generar la gráfica")
                return
            
            # Convertir FechaReal a datetime si no lo está
            if not pd.api.types.is_datetime64_any_dtype(df_clientes['FechaReal']):
                df_clientes['FechaReal'] = pd.to_datetime(df_clientes['FechaReal'])
            
            # Extraer año y mes de la fecha
            df_clientes['Año'] = df_clientes['FechaReal'].dt.year
            df_clientes['Mes'] = df_clientes['FechaReal'].dt.month
            
            # Filtrar por el año seleccionado
            df_año = df_clientes[df_clientes['Año'] == año_seleccionado].copy()
            
            if df_año.empty:
                st.warning(f"No hay datos para el año {año_seleccionado}")
                return
            
            # Agrupar por mes y sumar ingresos
            ingresos_mensuales = df_año.groupby('Mes')['ingresos_fact'].sum().reset_index()
            
            # Crear un dataframe con todos los meses del año (1-12)
            todos_los_meses = pd.DataFrame({'Mes': range(1, 13)})
            
            # Hacer merge para asegurar que tengamos todos los meses
            ingresos_completos = todos_los_meses.merge(ingresos_mensuales, on='Mes', how='left')
            
            # Rellenar meses sin datos con 0
            ingresos_completos['ingresos_fact'] = ingresos_completos['ingresos_fact'].fillna(0)
            
            # Ordenar por mes
            ingresos_completos = ingresos_completos.sort_values('Mes')
            
            # Nombres de los meses para los labels
            nombres_meses = [
                'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
            ]
            
            # Crear la gráfica de líneas
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=nombres_meses,
                y=ingresos_completos['ingresos_fact'],
                mode='lines+markers+text',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8, color='#1f77b4'),
                text=[f'${x:,.0f} USD' for x in ingresos_completos['ingresos_fact']],
                textposition='top center',
                textfont=dict(size=10),
                hovertemplate='<b>%{x}</b><br>Ventas: $%{y:,.2f} USD<extra></extra>',
                name='Ventas Mensuales'
            ))
            
            # Personalizar el layout
            fig.update_layout(
                title=f'Ventas Mensuales - {año_seleccionado} - {vendedor}',
                xaxis_title='Mes',
                yaxis_title='💰 Ventas ($USD)',
                hovermode='x unified',
                showlegend=False,
                height=500,
                template='plotly_white',
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(12)),
                    ticktext=nombres_meses
                ),
                yaxis=dict(
                    tickformat='$,.0f',
                    gridcolor='lightgray'
                )
            )
            
            # Mostrar la gráfica
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar tabla resumen debajo de la gráfica
            st.subheader("📊 Resumen Mensual")
            
            # Crear tabla con los datos
            resumen_df = pd.DataFrame({
                'Mes': nombres_meses,
                'Ventas': ingresos_completos['ingresos_fact']
            })
            
            # Formatear ingresos para mostrar
            resumen_df['Ingresos Formateado'] = resumen_df['Ventas'].apply(lambda x: f'${x:,.2f}')
            
            # Mostrar tabla
            st.dataframe(
                resumen_df[['Mes', 'Ingresos Formateado']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Mes": st.column_config.TextColumn("Mes", width="small"),
                    "Ingresos Formateado": st.column_config.TextColumn("Ventas (USD)", width="medium")
                }
            )
            
        except Exception as e:
            st.error(f"Error al generar la gráfica: {str(e)}")