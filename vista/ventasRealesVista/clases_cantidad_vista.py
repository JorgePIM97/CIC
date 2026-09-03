# vista/ventasRealesVista/clases_cantidad_vista.py
"""
Vista para generar gráficas y análisis de clases_cantidad
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from vista.base_vista import BaseVista
from ..seleccion_usuarios.seleccion import SeleccionUsuarios

class ClasesCantidadVista(BaseVista):
    def __init__(self):
        self.seleccion_usuarios = SeleccionUsuarios()

    def preparar_datos_grafica_pastel(self, df):
        """
        Prepara los datos para la gráfica de pastel con top 10 clases
        """
        if df.empty:
            return pd.DataFrame()
        
        # Agrupar por clase y sumar cantidades (en caso de múltiples fechas)
        df_agrupado = df.groupby(['Clase']).agg({
            'clases_fact': 'sum'
        }).reset_index()
        
        # Ordenar por cantidad descendente
        df_ordenado = df_agrupado.sort_values('clases_fact', ascending=False)
        
        # Top 10 clases
        top_10 = df_ordenado.head(10).copy()
        
        # Suma de otras clases (resto)
        otros_cantidad = df_ordenado.iloc[10:]['clases_fact'].sum()
        
        # Si hay otras clases, agregarlas
        if otros_cantidad > 0:
            otros_row = pd.DataFrame({
                'Clase': ['Otros'],
                'clases_fact': [otros_cantidad]
            })
            df_grafica = pd.concat([top_10, otros_row], ignore_index=True)
        else:
            df_grafica = top_10
        
        return df_grafica
    
    def crear_grafica_pastel(self, df_grafica, vendedores_lista):
        """
        Crea la gráfica de pastel con los datos preparados (ahora acepta lista de vendedores)
        """
        if df_grafica.empty:
            st.warning("No hay datos para mostrar en la gráfica")
            return None
        
        # Crear colores personalizados
        colors = px.colors.qualitative.Set3[:len(df_grafica)]
        
        # Crear gráfica de pastel
        fig = go.Figure(data=[
            go.Pie(
                labels=df_grafica['Clase'],
                values=df_grafica['clases_fact'],
                hole=0.3,  # Dona en el centro
                marker=dict(colors=colors),
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>' +
                             'Cantidad: %{value}<br>' +
                             'Porcentaje: %{percent}<br>' +
                             '<extra></extra>'
            )
        ])
        
        titulo = f'Distribución de Catidades por Clase Vendidas'
        
        
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
    
    def mostrar_tabla_clases(self, df, vendedores_lista):
        """
        Muestra la tabla completa de clases y cantidades (ahora acepta lista de vendedores)
        """
        if df.empty:
            st.warning("No hay datos para mostrar en la tabla")
            return
        
        # Agrupar por clase y sumar cantidades
        df_agrupado = df.groupby(['Clase']).agg({
            'clases_fact': 'sum'
        }).reset_index()
        
        # Formatear la columna de cantidades
        df_display = df_agrupado.copy()
        df_display['clases_fact_formatted'] = df_display['clases_fact'].apply(
            lambda x: f"{int(x)}"
        )
        
        # Renombrar columnas para mostrar
        df_display = df_display.rename(columns={
            'Clase': 'Clase',
            'clases_fact_formatted': 'Cantidad Total'
        }).drop(columns=['clases_fact'])

        titulo = f"📊 Cantidad de Clases Vendidas"
        # # Título dinámico según los vendedores
        # if len(vendedores_lista) == 1:
        #     titulo = f"📊 Cantidad de Clases Vendidas - {vendedores_lista[0]}"
        # elif len(vendedores_lista) <= 3:
        #     vendedores_str = ", ".join(vendedores_lista)
        #     titulo = f"📊 Cantidad de Clases Vendidas - {vendedores_str}"
        # else:
        #     titulo = f"📊 Cantidad de Clases Vendidas - {len(vendedores_lista)} Vendedores"
            
        st.subheader(titulo)
        
        # Mostrar métricas resumidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_clases = len(df_agrupado)
            st.metric("Total de Clases", total_clases)
        
        with col2:
            total_cantidad = df_agrupado['clases_fact'].sum()
            st.metric("Cantidad Total Vendida", f"{int(total_cantidad)}")
        
        with col3:
            promedio_cantidad = df_agrupado['clases_fact'].mean()
            st.metric("Promedio por Clase", f"{promedio_cantidad:,.0f}")
        
        # Mostrar tabla con paginación y búsqueda
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

    def generar_grafica_lineas_cantidad_mensuales(self, df_clases, vendedores_lista, año_seleccionado):
        """
        Genera gráfica de líneas con cantidades mensuales para el año seleccionado (ahora acepta lista de vendedores)
        """
        try:
            # Verificar que tenemos datos y año seleccionado
            if df_clases.empty or not año_seleccionado:
                st.warning("No hay datos disponibles para generar la gráfica")
                return
            
            # Convertir FechaReal a datetime si no lo está
            if not pd.api.types.is_datetime64_any_dtype(df_clases['FechaReal']):
                df_clases['FechaReal'] = pd.to_datetime(df_clases['FechaReal'])
            
            # Extraer año y mes de la fecha
            df_clases['Año'] = df_clases['FechaReal'].dt.year
            df_clases['Mes'] = df_clases['FechaReal'].dt.month
            
            # Filtrar por el año seleccionado
            df_año = df_clases[df_clases['Año'] == año_seleccionado].copy()
            
            if df_año.empty:
                st.warning(f"No hay datos para el año {año_seleccionado}")
                return
            
            # Agrupar por mes y sumar cantidades
            cantidad_mensuales = df_año.groupby('Mes')['clases_fact'].sum().reset_index()
            
            # Crear un dataframe con todos los meses del año (1-12)
            todos_los_meses = pd.DataFrame({'Mes': range(1, 13)})
            
            # Hacer merge para asegurar que tengamos todos los meses
            cantidad_completos = todos_los_meses.merge(cantidad_mensuales, on='Mes', how='left')
            
            # Rellenar meses sin datos con 0
            cantidad_completos['clases_fact'] = cantidad_completos['clases_fact'].fillna(0)
            
            # Ordenar por mes
            cantidad_completos = cantidad_completos.sort_values('Mes')
            
            # Nombres de los meses para los labels
            nombres_meses = [
                'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
            ]
            
            # Crear la gráfica de líneas
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=nombres_meses,
                y=cantidad_completos['clases_fact'],
                mode='lines+markers+text',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8, color='#1f77b4'),
                text=[f'{x:,.0f}' for x in cantidad_completos['clases_fact']],
                textposition='top center',
                textfont=dict(size=10),
                hovertemplate='<b>%{x}</b><br>Cantidad: %{y}<extra></extra>',
                name='Cantidad de Clases Vendidas Mensuales'
            ))
            
            # Título dinámico según los vendedores
            if len(vendedores_lista) == 1:
                titulo_vendedores = vendedores_lista[0]
            elif len(vendedores_lista) <= 3:
                titulo_vendedores = ", ".join(vendedores_lista)
            else:
                titulo_vendedores = f"{len(vendedores_lista)} Vendedores"
            
            # Personalizar el layout
            fig.update_layout(
                title=f'Cantidad de Clases Vendidas Mensuales - {año_seleccionado} - {vendedores_lista}',
                xaxis_title='Mes',
                yaxis_title='Cantidad',
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
                'Cantidad': cantidad_completos['clases_fact']
            })
            
            # Formatear cantidades para mostrar
            resumen_df['Cantidad Formateado'] = resumen_df['Cantidad'].apply(lambda x: f'{int(x)}')
            
            # Mostrar tabla
            st.dataframe(
                resumen_df[['Mes', 'Cantidad Formateado']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Mes": st.column_config.TextColumn("Mes", width="small"),
                    "Cantidad Formateado": st.column_config.TextColumn("Cantidad Total", width="medium")
                }
            )
            
        except Exception as e:
            st.error(f"Error al generar la gráfica: {str(e)}")