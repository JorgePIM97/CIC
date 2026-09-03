# vista/ventasRealesVista/categoria_ingresos_vista.py
"""
Vista para generar gráficas y análisis de categorías de ingresos
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from vista.base_vista import BaseVista
from ..seleccion_usuarios.seleccion import SeleccionUsuarios

class CategoriaIngresosVista(BaseVista):
    def __init__(self):
        self.seleccion_usuarios = SeleccionUsuarios()

    def preparar_datos_grafica_pastel(self, df):
        """
        Prepara los datos para la gráfica de pastel con top 10 categorías
        """
        if df.empty:
            return pd.DataFrame()
        
        # Agrupar por categoría y sumar ingresos
        df_agrupado = df.groupby(['Categoria']).agg({
            'TotalIngresosUSD': 'sum'
        }).reset_index()
        
        # Ordenar por ingresos descendente
        df_ordenado = df_agrupado.sort_values('TotalIngresosUSD', ascending=False)
        
        # Top 10 categorías
        top_10 = df_ordenado.head(10).copy()
        
        # Suma de otras categorías (resto)
        otros_ingresos = df_ordenado.iloc[10:]['TotalIngresosUSD'].sum()
        
        # Si hay otras categorías, agregarlas
        if otros_ingresos > 0:
            otros_row = pd.DataFrame({
                'Categoria': ['Otros'],
                'TotalIngresosUSD': [otros_ingresos]
            })
            df_grafica = pd.concat([top_10, otros_row], ignore_index=True)
        else:
            df_grafica = top_10
        
        return df_grafica
    
    def crear_grafica_pastel(self, df_grafica, vendedores_lista):
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
                labels=df_grafica['Categoria'],
                values=df_grafica['TotalIngresosUSD'],
                hole=0.3,  # Dona en el centro
                marker=dict(colors=colors),
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>' +
                             'Ingresos: $%{value:,.2f} USD<br>' +
                             'Porcentaje: %{percent}<br>' +
                             '<extra></extra>'
            )
        ])
        
        # Título dinámico según los vendedores
        titulo = 'Distribución de Ventas por Proyecto'
        
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
    
    # def crear_grafica_pastel(self, df_grafica, vendedores_lista):
    #     """
    #     Crea la gráfica de pastel con los datos preparados
    #     """
    #     if df_grafica.empty:
    #         st.warning("No hay datos para mostrar en la gráfica")
    #         return None
        
    #     # Crear colores personalizados
    #     colors = px.colors.qualitative.Set3[:len(df_grafica)]
        
    #     # Crear gráfica de pastel
    #     fig = go.Figure(data=[
    #         go.Pie(
    #             labels=df_grafica['Categoria'],
    #             values=df_grafica['TotalIngresosUSD'],
    #             hole=0.3,
    #             marker=dict(colors=colors),
    #             textinfo='label+percent',
    #             textposition='auto',
    #             hovertemplate='<b>%{label}</b><br>' +
    #                         'Ingresos: $%{value:,.2f} USD<br>' +
    #                         'Porcentaje: %{percent}<br>' +
    #                         '<extra></extra>',
    #             domain=dict(x=[0.05, 0.75])  # ← El pastel ocupa solo el 70% del ancho, dejando espacio a ambos lados
    #         )
    #     ])
        
    #     titulo = 'Distribución de Ventas por Proyecto'
        
    #     fig.update_layout(
    #         title={
    #             'text': titulo,
    #             'x': 0.5,
    #             'xanchor': 'center',
    #             'font': {'size': 18}
    #         },
    #         height=600,
    #         showlegend=True,
    #         legend=dict(
    #             orientation="v",
    #             yanchor="middle",
    #             y=0.5,
    #             xanchor="left",
    #             x=0.78  # ← La leyenda empieza justo después del pastel
    #         ),
    #         margin=dict(l=40, r=150, t=60, b=120)
    #     )
        
    #     return fig

    def mostrar_tabla_categorias(self, df):
        """
        Muestra la tabla completa de categorías y totales
        """
        if df.empty:
            st.warning("No hay datos para mostrar en la tabla")
            return
        
        # Agrupar por categoría y sumar ingresos
        df_agrupado = df.groupby(['Categoria']).agg({
            'TotalIngresosUSD': 'sum'
        }).reset_index()
        
        # Ordenar por ingresos descendente
        df_agrupado = df_agrupado.sort_values('TotalIngresosUSD', ascending=False)
        
        # Formatear la columna de ingresos
        df_display = df_agrupado.copy()
        df_display['Ingresos Formateados'] = df_display['TotalIngresosUSD'].apply(
            lambda x: f"${x:,.2f}"
        )
        
        # Renombrar columnas para mostrar
        df_display = df_display.rename(columns={
            'Categoria': 'Categoría',
            'Ingresos Formateados': 'Ventas Totales (USD)'
        })
        
        titulo = "📊 Tabla de Categorías y Ventas"
        st.subheader(titulo)
        
        # Mostrar métricas resumidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_categorias = len(df_agrupado)
            st.metric("Total de Categorías", total_categorias)
        
        with col2:
            total_ingresos = df_agrupado['TotalIngresosUSD'].sum()
            st.metric("Ventas Totales", f"${total_ingresos:,.2f} USD")
        
        with col3:
            promedio_ingresos = df_agrupado['TotalIngresosUSD'].mean()
            st.metric("Promedio por Categoría", f"${promedio_ingresos:,.2f} USD")
        
        # Mostrar tabla con paginación y búsqueda
        st.dataframe(
            df_display[['Categoría', 'Ventas Totales (USD)']],
            use_container_width=True,
            hide_index=True
        )

    def generar_grafica_lineas_categoria_mensuales(self, df_categorias, vendedores_lista, año_seleccionado):
        """
        Genera gráfica de líneas con ingresos mensuales para el año seleccionado
        """
        try:
            # Verificar que tenemos datos y año seleccionado
            if df_categorias.empty or not año_seleccionado:
                st.warning("No hay datos disponibles para generar la gráfica")
                return
            
            # Asegurar que tenemos la columna FechaReal
            if 'FechaReal' not in df_categorias.columns:
                st.error("No se encontró la columna 'FechaReal' en los datos")
                return
            
            # Convertir FechaReal a datetime si no lo está
            if not pd.api.types.is_datetime64_any_dtype(df_categorias['FechaReal']):
                df_categorias['FechaReal'] = pd.to_datetime(df_categorias['FechaReal'])
            
            # Extraer año y mes de la fecha
            df_categorias['Año'] = df_categorias['FechaReal'].dt.year
            df_categorias['Mes'] = df_categorias['FechaReal'].dt.month
            
            # Filtrar por el año seleccionado
            df_año = df_categorias[df_categorias['Año'] == año_seleccionado].copy()
            
            if df_año.empty:
                st.warning(f"No hay datos para el año {año_seleccionado}")
                return
            
            # Agrupar por mes y sumar ingresos
            ingresos_mensuales = df_año.groupby('Mes')['TotalIngresosUSD'].sum().reset_index()
            
            # Crear un dataframe con todos los meses del año (1-12)
            todos_los_meses = pd.DataFrame({'Mes': range(1, 13)})
            
            # Hacer merge para asegurar que tengamos todos los meses
            ingresos_completos = todos_los_meses.merge(ingresos_mensuales, on='Mes', how='left')
            
            # Rellenar meses sin datos con 0
            ingresos_completos['TotalIngresosUSD'] = ingresos_completos['TotalIngresosUSD'].fillna(0)
            
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
                y=ingresos_completos['TotalIngresosUSD'],
                mode='lines+markers+text',
                line=dict(color='#1f77b4', width=3),
                marker=dict(size=8, color='#1f77b4'),
                text=[f'${x:,.0f}' for x in ingresos_completos['TotalIngresosUSD']],
                textposition='top center',
                textfont=dict(size=10),
                hovertemplate='<b>%{x}</b><br>Ingresos: $%{y:,.2f}<extra></extra>',
                name='Ingresos por Categorías Mensuales'
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
                title=f'Ingresos por Categorías Mensuales - {año_seleccionado} - {titulo_vendedores}',
                xaxis_title='Mes',
                yaxis_title='💰 Ingresos ($USD)',
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
                'Ingresos': ingresos_completos['TotalIngresosUSD']
            })
            
            # Formatear ingresos para mostrar
            resumen_df['Ingresos Formateados'] = resumen_df['Ingresos'].apply(lambda x: f'${x:,.2f}')
            
            # Mostrar tabla
            st.dataframe(
                resumen_df[['Mes', 'Ingresos Formateados']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Mes": st.column_config.TextColumn("Mes", width="small"),
                    "Ingresos Formateados": st.column_config.TextColumn("Ventas Totales", width="medium")
                }
            )
            
        except Exception as e:
            st.error(f"Error al generar la gráfica: {str(e)}")
            st.write("Datos disponibles:")
            st.write(df_categorias.columns.tolist())

    def mostrar_top_categorias(self, df, numero_top=9):
        """
        Muestra el top de categorías en la barra lateral
        """
        if df.empty:
            st.warning("No hay datos para mostrar")
            return
        
        st.subheader(f"🏆 Top {numero_top} Categorías")
        
        # Agrupar por categoría en caso de múltiples fechas
        df_top = df.groupby(['Categoria']).agg({
            'TotalIngresosUSD': 'sum'
        }).reset_index().sort_values('TotalIngresosUSD', ascending=False)
        
        top_categorias = df_top.head(numero_top)
        
        for idx, row in top_categorias.iterrows():
            st.write(f"**{row['Categoria']}**")
            st.write(f"${row['TotalIngresosUSD']:,.2f} USD")
            st.write("---")