# vista/ventasRealesVista/clases_ingresos_vista.py
"""
Vista para generar gráficas y análisis de clases_ingresos
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from vista.base_vista import BaseVista
from modelo.ventas_reales_modelo import VentasRealesModelo
from ..seleccion_usuarios.seleccion import SeleccionUsuarios

class ClasesIngresosVista(BaseVista):
    def __init__(self):
        self.seleccion_usuarios = SeleccionUsuarios()
        self.ventas_reales_modelo = VentasRealesModelo()

    def preparar_datos_grafica_pastel(self, df):
        """
        Prepara los datos para la gráfica de pastel con top 10 clases
        """
        if df.empty:
            return pd.DataFrame()
        
        # Agrupar por clase y sumar ingresos (en caso de múltiples fechas)
        df_agrupado = df.groupby(['Clase', 'NumeroDeDocumento']).agg({
            'ingresos_fact': 'sum'
        }).reset_index()
        
        # Ordenar por ingresos descendente
        df_ordenado = df_agrupado.sort_values('ingresos_fact', ascending=False)
        
        # Top 10 clases
        top_10 = df_ordenado.head(10).copy()
        
        # Suma de otras clases (resto)
        otros_ingresos = df_ordenado.iloc[10:]['ingresos_fact'].sum()
        
        # Si hay otras clases, agregarlas
        if otros_ingresos > 0:
            otros_row = pd.DataFrame({
                'Clase': ['Otros'],
                'NumeroDeDocumento': [''],
                'ingresos_fact': [otros_ingresos]
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
        
        # Título dinámico según los vendedores
        if len(vendedores_lista) == 1:
            #titulo = f'Distribución de Ingresos por Clase - {vendedores_lista[0]} (Top 10)'
            titulo = f'Distribución de Ventas por Clase'
        elif len(vendedores_lista) <= 3:
            vendedores_str = ", ".join(vendedores_lista)
            # titulo = f'Distribución de Ingresos por Clase - {vendedores_str} (Top 10)'
            titulo = f'Distribución de Ventas por Clase'
        else:
            # titulo = f'Distribución de Ingresos por Clase - {len(vendedores_lista)} Vendedores (Top 10)'
            titulo = f'Distribución de Ventas por Clase'
        
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
    
    # def mostrar_tabla_clases(self, df, vendedores_lista):
    #     """
    #     Muestra la tabla completa de clases e ingresos (ahora acepta lista de vendedores)
    #     """
    #     if df.empty:
    #         st.warning("No hay datos para mostrar en la tabla")
    #         return
        
    #     # Agrupar por cliente y sumar ingresos
    #     df_agrupado = df.groupby(['Clase', 'NumeroDeDocumento']).agg({
    #         'ingresos_fact': 'sum'
    #     }).reset_index()
        
    #     # Formatear la columna de ingresos
    #     df_display = df_agrupado.copy()
    #     df_display['ingresos_fact_formatted'] = df_display['ingresos_fact'].apply(
    #         lambda x: f"${x:,.2f}"
    #     )
        
    #     # Renombrar columnas para mostrar
    #     df_display = df_display.rename(columns={
    #         'Clase': 'Clase',
    #         'NumeroDeDocumento': 'Número de Documento',
    #         'ingresos_fact_formatted': 'Ventas Totales (USD)'
    #     }).drop(columns=['ingresos_fact'])
        
    #     titulo = f"📊 Tabla de Clases y Ventas"
    #     # # Título dinámico según los vendedores
    #     # if len(vendedores_lista) == 1:
    #     #     titulo = f"📊 Tabla de Clases e Ingresos - {vendedores_lista[0]}"
    #     # elif len(vendedores_lista) <= 3:
    #     #     vendedores_str = ", ".join(vendedores_lista)
    #     #     titulo = f"📊 Tabla de Clases e Ingresos - {vendedores_str}"
    #     # else:
    #     #     titulo = f"📊 Tabla de Clases e Ingresos - {len(vendedores_lista)} Vendedores"
            
    #     st.subheader(titulo)
        
    #     # Mostrar métricas resumidas
    #     col1, col2, col3 = st.columns(3)
        
    #     with col1:
    #         total_clases = len(df_agrupado)
    #         st.metric("Total de Clases", total_clases)
        
    #     with col2:
    #         total_ingresos = df_agrupado['ingresos_fact'].sum()
    #         st.metric("Ventas Totales", f"${total_ingresos:,.2f} USD")
        
    #     with col3:
    #         promedio_ingresos = df_agrupado['ingresos_fact'].mean()
    #         st.metric("Promedio por Clase", f"${promedio_ingresos:,.2f} USD")
        
    #     # Mostrar tabla con paginación y búsqueda
    #     st.dataframe(
    #         df_display,
    #         use_container_width=True,
    #         hide_index=True
    #     )

    def mostrar_tabla_clases(self, df, vendedores_lista):
        """
        Muestra la tabla completa de clases e ingresos (ahora acepta lista de vendedores)
        """
        if df.empty:
            st.warning("No hay datos para mostrar en la tabla")
            return
        
        # Agrupar por cliente y sumar ingresos
        df_agrupado = df.groupby(['Clase']).agg({
            'ingresos_fact': 'sum'
        }).reset_index()
        
        # Formatear la columna de ingresos
        df_display = df_agrupado.copy()
        df_display['ingresos_fact_formatted'] = df_display['ingresos_fact'].apply(
            lambda x: f"${x:,.2f}"
        )
        
        # Renombrar columnas para mostrar
        df_display = df_display.rename(columns={
            'Clase': 'Clase',
            'ingresos_fact_formatted': 'Ventas Totales (USD)'
        }).drop(columns=['ingresos_fact'])
        
        titulo = f"📊 Tabla de Clases y Ventas"
        # # Título dinámico según los vendedores
        # if len(vendedores_lista) == 1:
        #     titulo = f"📊 Tabla de Clases e Ingresos - {vendedores_lista[0]}"
        # elif len(vendedores_lista) <= 3:
        #     vendedores_str = ", ".join(vendedores_lista)
        #     titulo = f"📊 Tabla de Clases e Ingresos - {vendedores_str}"
        # else:
        #     titulo = f"📊 Tabla de Clases e Ingresos - {len(vendedores_lista)} Vendedores"
            
        st.subheader(titulo)
        
        # Mostrar métricas resumidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_clases = len(df_agrupado)
            st.metric("Total de Clases", total_clases)
        
        with col2:
            total_ingresos = df_agrupado['ingresos_fact'].sum()
            st.metric("Ventas Totales", f"${total_ingresos:,.2f} USD")
        
        with col3:
            promedio_ingresos = df_agrupado['ingresos_fact'].mean()
            st.metric("Promedio por Clase", f"${promedio_ingresos:,.2f} USD")
        
        # Mostrar tabla con paginación y búsqueda
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )

    # def generar_grafica_lineas_ingresos_mensuales(self, df_clases, vendedores_lista, año_seleccionado):
    #     """
    #     Genera gráfica de líneas con ingresos mensuales para el año seleccionado (ahora acepta lista de vendedores)
    #     """
    #     try:
    #         # Consulta para saber meta anual de vendedor
    #         # total_meta_anual = self.ventas_reales_modelo.obtener_meta_por_vendedor_reporte(vendedor, año)

    #         # Verificar que tenemos datos y año seleccionado
    #         if df_clases.empty or not año_seleccionado:
    #             st.warning("No hay datos disponibles para generar la gráfica")
    #             return
            
    #         # Convertir FechaReal a datetime si no lo está
    #         if not pd.api.types.is_datetime64_any_dtype(df_clases['FechaReal']):
    #             df_clases['FechaReal'] = pd.to_datetime(df_clases['FechaReal'])
            
    #         # Extraer año y mes de la fecha
    #         df_clases['Año'] = df_clases['FechaReal'].dt.year
    #         df_clases['Mes'] = df_clases['FechaReal'].dt.month
            
    #         # Filtrar por el año seleccionado
    #         df_año = df_clases[df_clases['Año'] == año_seleccionado].copy()
            
    #         if df_año.empty:
    #             st.warning(f"No hay datos para el año {año_seleccionado}")
    #             return
            
    #         # Agrupar por mes y sumar ingresos
    #         ingresos_mensuales = df_año.groupby('Mes')['ingresos_fact'].sum().reset_index()
            
    #         # Crear un dataframe con todos los meses del año (1-12)
    #         todos_los_meses = pd.DataFrame({'Mes': range(1, 13)})
            
    #         # Hacer merge para asegurar que tengamos todos los meses
    #         ingresos_completos = todos_los_meses.merge(ingresos_mensuales, on='Mes', how='left')
            
    #         # Rellenar meses sin datos con 0
    #         ingresos_completos['ingresos_fact'] = ingresos_completos['ingresos_fact'].fillna(0)
            
    #         # Ordenar por mes
    #         ingresos_completos = ingresos_completos.sort_values('Mes')
            
    #         # Nombres de los meses para los labels
    #         nombres_meses = [
    #             'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
    #             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
    #         ]
            
    #         # Crear la gráfica de líneas
    #         fig = go.Figure()
            
    #         fig.add_trace(go.Scatter(
    #             x=nombres_meses,
    #             y=ingresos_completos['ingresos_fact'],
    #             mode='lines+markers+text',
    #             line=dict(color='#1f77b4', width=3),
    #             marker=dict(size=8, color='#1f77b4'),
    #             text=[f'${x:,.0f} USD' for x in ingresos_completos['ingresos_fact']],
    #             textposition='top center',
    #             textfont=dict(size=10),
    #             hovertemplate='<b>%{x}</b><br>Ventas: $%{y:,.2f} USD<extra></extra>',
    #             name='Ventas Mensuales'
    #         ))
            
    #         # Título dinámico según los vendedores
    #         if len(vendedores_lista) == 1:
    #             titulo_vendedores = vendedores_lista[0]
    #         elif len(vendedores_lista) <= 3:
    #             titulo_vendedores = ", ".join(vendedores_lista)
    #         else:
    #             titulo_vendedores = f"{len(vendedores_lista)} Vendedores"
            
    #         # Personalizar el layout
    #         fig.update_layout(
    #             title=f'Ventas Mensuales - {año_seleccionado} - {vendedores_lista}',
    #             xaxis_title='Mes',
    #             yaxis_title='💰 Ventas ($USD)',
    #             hovermode='x unified',
    #             showlegend=False,
    #             height=500,
    #             template='plotly_white',
    #             xaxis=dict(
    #                 tickmode='array',
    #                 tickvals=list(range(12)),
    #                 ticktext=nombres_meses
    #             ),
    #             yaxis=dict(
    #                 tickformat='$,.0f',
    #                 gridcolor='lightgray'
    #             )
    #         )
            
    #         # Mostrar la gráfica
    #         st.plotly_chart(fig, use_container_width=True)
            
    #         # Mostrar tabla resumen debajo de la gráfica
    #         st.subheader("📊 Resumen Mensual")
            
    #         # Crear tabla con los datos
    #         resumen_df = pd.DataFrame({
    #             'Mes': nombres_meses,
    #             'Ventas': ingresos_completos['ingresos_fact']
    #         })
            
    #         # Formatear ingresos para mostrar
    #         resumen_df['Ingresos Formateado'] = resumen_df['Ventas'].apply(lambda x: f'${x:,.2f}')
            
    #         # Mostrar tabla
    #         st.dataframe(
    #             resumen_df[['Mes', 'Ingresos Formateado']],
    #             hide_index=True,
    #             use_container_width=True,
    #             column_config={
    #                 "Mes": st.column_config.TextColumn("Mes", width="small"),
    #                 "Ingresos Formateado": st.column_config.TextColumn("Ventas (USD)", width="medium")
    #             }
    #         )
            
    #     except Exception as e:
    #         st.error(f"Error al generar la gráfica: {str(e)}")

    # def generar_grafica_lineas_ingresos_mensuales(self, df_clases, vendedores_lista, año_seleccionado, df_metas=None):
    #     """
    #     Genera gráfica de líneas con ingresos mensuales y metas para el año seleccionado
        
    #     Args:
    #         df_clases: DataFrame con las ventas reales
    #         vendedores_lista: Lista de vendedores seleccionados
    #         año_seleccionado: Año a graficar
    #         df_metas: DataFrame con las metas (opcional)
    #     """
    #     try:
    #         # Verificar que tenemos datos y año seleccionado
    #         if df_clases.empty or not año_seleccionado:
    #             st.warning("No hay datos disponibles para generar la gráfica")
    #             return
            
    #         # Convertir FechaReal a datetime si no lo está
    #         if not pd.api.types.is_datetime64_any_dtype(df_clases['FechaReal']):
    #             df_clases['FechaReal'] = pd.to_datetime(df_clases['FechaReal'])
            
    #         # Extraer año y mes de la fecha
    #         df_clases['Año'] = df_clases['FechaReal'].dt.year
    #         df_clases['Mes'] = df_clases['FechaReal'].dt.month
            
    #         # Filtrar por el año seleccionado
    #         df_año = df_clases[df_clases['Año'] == año_seleccionado].copy()
            
    #         if df_año.empty:
    #             st.warning(f"No hay datos para el año {año_seleccionado}")
    #             return
            
    #         # Agrupar por mes y sumar ingresos
    #         ingresos_mensuales = df_año.groupby('Mes')['ingresos_fact'].sum().reset_index()
            
    #         # Crear un dataframe con todos los meses del año (1-12)
    #         todos_los_meses = pd.DataFrame({'Mes': range(1, 13)})
            
    #         # Hacer merge para asegurar que tengamos todos los meses
    #         ingresos_completos = todos_los_meses.merge(ingresos_mensuales, on='Mes', how='left')
            
    #         # Rellenar meses sin datos con 0
    #         ingresos_completos['ingresos_fact'] = ingresos_completos['ingresos_fact'].fillna(0)
            
    #         # ========== PROCESAMIENTO DE METAS ==========
    #         metas_mensuales = None
    #         if df_metas is not None and not df_metas.empty:
    #             # Mapeo de nombres de meses a números
    #             meses_map = {
    #                 'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4,
    #                 'MAYO': 5, 'JUNIO': 6, 'JULIO': 7, 'AGOSTO': 8,
    #                 'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12
    #             }
                
    #             # Convertir MesMeta a número
    #             df_metas['MesNumero'] = df_metas['MesMeta'].str.upper().map(meses_map)
                
    #             # Agrupar metas por mes y sumar
    #             metas_por_mes = df_metas.groupby('MesNumero')['ValorMeta'].sum().reset_index()
    #             metas_por_mes.columns = ['Mes', 'Meta']
                
    #             # Merge con todos los meses
    #             metas_mensuales = todos_los_meses.merge(metas_por_mes, on='Mes', how='left')
    #             metas_mensuales['Meta'] = metas_mensuales['Meta'].fillna(0)
            
    #         # Ordenar por mes
    #         ingresos_completos = ingresos_completos.sort_values('Mes')
            
    #         # Nombres de los meses para los labels
    #         nombres_meses = [
    #             'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
    #             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
    #         ]
            
    #         # ========== CREAR LA GRÁFICA ==========
    #         fig = go.Figure()
            

    #         # Barra de ventas reales
    #         fig.add_trace(go.Bar(
    #             x=nombres_meses,
    #             y=ingresos_completos['ingresos_fact'],
    #             text=[f'${x:,.0f}' for x in ingresos_completos['ingresos_fact']],
    #             textposition='outside',  # mejor para barras
    #             textfont=dict(size=10),
    #             marker=dict(
    #                 color='#1f77b4',
    #                 line=dict(width=0.5)
    #                 ),
    #             hovertemplate='<b>%{x}</b><br>Ventas: $%{y:,.2f} USD<extra></extra>',
    #             name='Ventas'
    #         ))

    #         # Línea de metas (si existen)
    #         if metas_mensuales is not None:
    #             fig.add_trace(go.Scatter(
    #                 x=nombres_meses,
    #                 y=metas_mensuales['Meta'],
    #                 mode='lines+markers+text',
    #                 line=dict(color='#ff7f0e', width=3, dash='dash'),
    #                 marker=dict(size=8, color='#ff7f0e', symbol='diamond'),
    #                 text=[f'${x:,.0f}' for x in metas_mensuales['Meta']],
    #                 textposition='bottom center',
    #                 textfont=dict(size=10, color='#ff7f0e'),
    #                 hovertemplate='<b>%{x}</b><br>Meta: $%{y:,.2f} USD<extra></extra>',
    #                 name='Meta Mensual'
    #             ))
            
    #         # Título dinámico según los vendedores
    #         if len(vendedores_lista) == 1:
    #             titulo_vendedores = vendedores_lista[0]
    #         elif len(vendedores_lista) <= 3:
    #             titulo_vendedores = ", ".join(vendedores_lista)
    #         else:
    #             titulo_vendedores = f"{len(vendedores_lista)} Vendedores"
            
    #         # Personalizar el layout
    #         fig.update_layout(
    #             title=f'Ventas vs Metas - {año_seleccionado} - {titulo_vendedores}',
    #             xaxis_title='Mes',
    #             yaxis_title='💰 Venta ($USD)',
    #             hovermode='x unified',
    #             showlegend=True,
    #             legend=dict(
    #                 orientation="h",
    #                 yanchor="bottom",
    #                 y=1.02,
    #                 xanchor="right",
    #                 x=1
    #             ),
    #             height=500,
    #             template='plotly_white',
    #             xaxis=dict(
    #                 tickmode='array',
    #                 tickvals=list(range(12)),
    #                 ticktext=nombres_meses
    #             ),
    #             yaxis=dict(
    #                 tickformat='$,.0f',
    #                 gridcolor='lightgray'
    #             )
    #         )
            
    #         # Mostrar la gráfica
    #         st.plotly_chart(fig, use_container_width=True)
            
    #         # ========== TABLA RESUMEN ==========
    #         st.subheader("📊 Resumen Mensual")
            
    #         # Crear tabla con los datos
    #         resumen_data = {
    #             'Mes': nombres_meses,
    #             'Ventas': ingresos_completos['ingresos_fact']
    #         }
            
    #         if metas_mensuales is not None:
    #             resumen_data['Meta'] = metas_mensuales['Meta']
    #             resumen_data['Diferencia'] = ingresos_completos['ingresos_fact'] - metas_mensuales['Meta']
    #             resumen_data['% Cumplimiento'] = (
    #                 (ingresos_completos['ingresos_fact'] / metas_mensuales['Meta'] * 100)
    #                 .fillna(0)
    #                 .replace([float('inf'), -float('inf')], 0)
    #             )
            
    #         resumen_df = pd.DataFrame(resumen_data)
            
    #         # Formatear columnas
    #         resumen_df['Ventas Formateado'] = resumen_df['Ventas'].apply(lambda x: f'${x:,.2f}')
            
    #         columnas_mostrar = ['Mes', 'Ventas Formateado']
    #         config_columnas = {
    #             "Mes": st.column_config.TextColumn("Mes", width="small"),
    #             "Ventas Formateado": st.column_config.TextColumn("Ventas (USD)", width="medium")
    #         }
            
    #         if metas_mensuales is not None:
    #             resumen_df['Meta Formateado'] = resumen_df['Meta'].apply(lambda x: f'${x:,.2f}')
    #             resumen_df['Diferencia Formateado'] = resumen_df['Diferencia'].apply(lambda x: f'${x:,.2f}')
    #             resumen_df['Cumplimiento Formateado'] = resumen_df['% Cumplimiento'].apply(lambda x: f'{x:.1f}%')
                
    #             columnas_mostrar = ['Mes', 'Ventas Formateado', 'Meta Formateado', 'Diferencia Formateado', 'Cumplimiento Formateado']
    #             config_columnas.update({
    #                 "Meta Formateado": st.column_config.TextColumn("Meta (USD)", width="medium"),
    #                 "Diferencia Formateado": st.column_config.TextColumn("Diferencia (USD)", width="medium"),
    #                 "Cumplimiento Formateado": st.column_config.TextColumn("% Cumplimiento", width="small")
    #             })
            
    #         # Mostrar tabla
    #         st.dataframe(
    #             resumen_df[columnas_mostrar],
    #             hide_index=True,
    #             use_container_width=True,
    #             column_config=config_columnas
    #         )
            
    #     except Exception as e:
    #         st.error(f"Error al generar la gráfica: {str(e)}")
    #         import traceback
    #         st.error(traceback.format_exc())

# clases_ingresos_vista.py

    # def generar_grafica_lineas_ingresos_mensuales(
    #     self, df_clases, vendedores_lista, año_seleccionado,
    #     df_metas=None,
    #     df_clases_anterior=None,   # ← nuevo
    #     df_metas_anterior=None     # ← nuevo
    # ):
    #     try:
    #         if df_clases.empty or not año_seleccionado:
    #             st.warning("No hay datos disponibles para generar la gráfica")
    #             return

    #         if not pd.api.types.is_datetime64_any_dtype(df_clases['FechaReal']):
    #             df_clases['FechaReal'] = pd.to_datetime(df_clases['FechaReal'])

    #         df_clases['Año'] = df_clases['FechaReal'].dt.year
    #         df_clases['Mes'] = df_clases['FechaReal'].dt.month

    #         todos_los_meses = pd.DataFrame({'Mes': range(1, 13)})
    #         nombres_meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    #         año_anterior = año_seleccionado - 1

    #         meses_map = {
    #             'ENERO':1,'FEBRERO':2,'MARZO':3,'ABRIL':4,'MAYO':5,'JUNIO':6,
    #             'JULIO':7,'AGOSTO':8,'SEPTIEMBRE':9,'OCTUBRE':10,'NOVIEMBRE':11,'DICIEMBRE':12
    #         }

    #         def agrupar_ingresos(df):
    #             """Agrupa un df de clases por mes y hace merge con todos los meses."""
    #             if df is None or df.empty:
    #                 return todos_los_meses.assign(ingresos_fact=0)
    #             if not pd.api.types.is_datetime64_any_dtype(df['FechaReal']):
    #                 df = df.copy()
    #                 df['FechaReal'] = pd.to_datetime(df['FechaReal'])
    #             df = df.copy()
    #             df['Mes'] = df['FechaReal'].dt.month
    #             agrupado = df.groupby('Mes')['ingresos_fact'].sum().reset_index()
    #             return todos_los_meses.merge(agrupado, on='Mes', how='left').fillna({'ingresos_fact': 0})

    #         def agrupar_metas(df_m):
    #             """Convierte df_metas a columnas Mes/Meta."""
    #             if df_m is None or df_m.empty:
    #                 return None
    #             df_m = df_m.copy()
    #             df_m['MesNumero'] = df_m['MesMeta'].str.upper().map(meses_map)
    #             metas_mes = df_m.groupby('MesNumero')['ValorMeta'].sum().reset_index()
    #             metas_mes.columns = ['Mes', 'Meta']
    #             return todos_los_meses.merge(metas_mes, on='Mes', how='left').fillna({'Meta': 0})

    #         # ── Datos año actual ──────────────────────────────────────────
    #         df_año = df_clases[df_clases['Año'] == año_seleccionado].copy()
    #         if df_año.empty:
    #             st.warning(f"No hay datos para el año {año_seleccionado}")
    #             return

    #         ingresos_actual   = agrupar_ingresos(df_año)
    #         ingresos_anterior = agrupar_ingresos(df_clases_anterior)
    #         metas_actual      = agrupar_metas(df_metas)
    #         metas_ant         = agrupar_metas(df_metas_anterior)

    #         hay_anterior = df_clases_anterior is not None and not df_clases_anterior.empty

    #         # ── Gráfica ───────────────────────────────────────────────────
    #         fig = go.Figure()

    #         # Barra año anterior
    #         if hay_anterior:
    #             fig.add_trace(go.Bar(
    #                 x=nombres_meses,
    #                 y=ingresos_anterior['ingresos_fact'],
    #                 name=f'Ventas {año_anterior}',
    #                 marker=dict(color="#fab361"),
    #                 text=[f'${x:,.0f}' for x in ingresos_anterior['ingresos_fact']],
    #                 textposition='outside',
    #                 textfont=dict(size=9),
    #                 hovertemplate=f'<b>%{{x}}</b><br>Ventas {año_anterior}: $%{{y:,.2f}} USD<extra></extra>'
    #             ))

    #         # Barra año actual
    #         fig.add_trace(go.Bar(
    #             x=nombres_meses,
    #             y=ingresos_actual['ingresos_fact'],
    #             name=f'Ventas {año_seleccionado}',
    #             marker=dict(color="#55a2da"),
    #             text=[f'${x:,.0f}' for x in ingresos_actual['ingresos_fact']],
    #             textposition='outside',
    #             textfont=dict(size=9),
    #             hovertemplate=f'<b>%{{x}}</b><br>Ventas {año_seleccionado}: $%{{y:,.2f}} USD<extra></extra>'
    #         ))

    #         # Línea meta año anterior
    #         if metas_ant is not None:
    #             fig.add_trace(go.Scatter(
    #                 x=nombres_meses,
    #                 y=metas_ant['Meta'],
    #                 mode='lines+markers',
    #                 line=dict(color='#ff7f0e', width=3, dash='dash'),
    #                 marker=dict(size=6, color='#ff7f0e', symbol='diamond'),
    #                 name=f'Meta {año_anterior}',
    #                 hovertemplate=f'<b>%{{x}}</b><br>Meta {año_anterior}: $%{{y:,.2f}} USD<extra></extra>'
    #             ))

    #         # Línea meta año actual
    #         if metas_actual is not None:
    #             fig.add_trace(go.Scatter(
    #                 x=nombres_meses,
    #                 y=metas_actual['Meta'],
    #                 mode='lines+markers+text',
    #                 line=dict(color="#196cb1", width=3, dash='dash'),
    #                 marker=dict(size=8, color='#196cb1', symbol='diamond'),
    #                 text=[f'${x:,.0f}' for x in metas_actual['Meta']],
    #                 textposition='bottom center',
    #                 textfont=dict(size=10, color='#196cb1'),
    #                 name=f'Meta {año_seleccionado}',
    #                 hovertemplate=f'<b>%{{x}}</b><br>Meta {año_seleccionado}: $%{{y:,.2f}} USD<extra></extra>'
    #             ))

    #         # Título
    #         if len(vendedores_lista) == 1:
    #             titulo_vendedores = vendedores_lista[0]
    #         elif len(vendedores_lista) <= 3:
    #             titulo_vendedores = ", ".join(vendedores_lista)
    #         else:
    #             titulo_vendedores = f"{len(vendedores_lista)} Vendedores"

    #         fig.update_layout(
    #             title=f'Ventas vs Metas — {año_anterior} vs {año_seleccionado} — {titulo_vendedores}',
    #             xaxis_title='Mes',
    #             yaxis_title='💰 Venta ($USD)',
    #             barmode='group',
    #             hovermode='x unified',
    #             showlegend=True,
    #             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    #             height=520,
    #             template='plotly_white',
    #             xaxis=dict(tickmode='array', tickvals=list(range(12)), ticktext=nombres_meses),
    #             yaxis=dict(tickformat='$,.0f', gridcolor='lightgray')
    #         )

    #         st.plotly_chart(fig, use_container_width=True)

    #         # ── Tabla resumen ─────────────────────────────────────────────
    #         st.subheader("📊 Resumen Mensual")

    #         resumen_data = {'Mes': nombres_meses}

    #         if hay_anterior:
    #             resumen_data[f'Ventas {año_anterior}'] = ingresos_anterior['ingresos_fact'].values

    #         resumen_data[f'Ventas {año_seleccionado}'] = ingresos_actual['ingresos_fact'].values

    #         if hay_anterior:
    #             ant_vals = ingresos_anterior['ingresos_fact'].values
    #             act_vals = ingresos_actual['ingresos_fact'].values
    #             with pd.option_context('mode.use_inf_as_na', True):
    #                 yoy = pd.Series(
    #                     [(a - b) / b * 100 if b != 0 else 0 for a, b in zip(act_vals, ant_vals)]
    #                 )
    #             resumen_data['Var. YoY'] = yoy

    #         if metas_actual is not None:
    #             resumen_data[f'Meta {año_seleccionado}'] = metas_actual['Meta'].values
    #             resumen_data['Diferencia'] = ingresos_actual['ingresos_fact'].values - metas_actual['Meta'].values
    #             resumen_data['% Cumplimiento'] = [
    #                 a / m * 100 if m != 0 else 0
    #                 for a, m in zip(ingresos_actual['ingresos_fact'].values, metas_actual['Meta'].values)
    #             ]

    #         resumen_df = pd.DataFrame(resumen_data)

    #         col_config = {"Mes": st.column_config.TextColumn("Mes", width="small")}
    #         cols_mostrar = ['Mes']

    #         def fmt_money(col, label):
    #             resumen_df[col + '_f'] = resumen_df[col].apply(lambda x: f'${x:,.2f}')
    #             col_config[col + '_f'] = st.column_config.TextColumn(label, width="medium")
    #             cols_mostrar.append(col + '_f')

    #         if hay_anterior:
    #             fmt_money(f'Ventas {año_anterior}', f'Ventas {año_anterior} (USD)')

    #         fmt_money(f'Ventas {año_seleccionado}', f'Ventas {año_seleccionado} (USD)')

    #         if hay_anterior:
    #             resumen_df['yoy_f'] = resumen_df['Var. YoY'].apply(lambda x: f'{x:+.1f}%')
    #             col_config['yoy_f'] = st.column_config.TextColumn("Var. YoY", width="small")
    #             cols_mostrar.append('yoy_f')

    #         if metas_actual is not None:
    #             fmt_money(f'Meta {año_seleccionado}', f'Meta {año_seleccionado} (USD)')
    #             fmt_money('Diferencia', 'Diferencia (USD)')
    #             resumen_df['cum_f'] = resumen_df['% Cumplimiento'].apply(lambda x: f'{x:.1f}%')
    #             col_config['cum_f'] = st.column_config.TextColumn("% Cumplimiento", width="small")
    #             cols_mostrar.append('cum_f')

    #         st.dataframe(resumen_df[cols_mostrar], hide_index=True, use_container_width=True, column_config=col_config)

    #     except Exception as e:
    #         st.error(f"Error al generar la gráfica: {str(e)}")
    #         import traceback
    #         st.error(traceback.format_exc())

    def generar_grafica_lineas_ingresos_mensuales(
        self, df_clases, vendedores_lista, año_seleccionado,
        df_metas=None,
        df_clases_anterior=None,
    ):
        try:
            if df_clases.empty or not año_seleccionado:
                st.warning("No hay datos disponibles para generar la gráfica")
                return

            if not pd.api.types.is_datetime64_any_dtype(df_clases['FechaReal']):
                df_clases['FechaReal'] = pd.to_datetime(df_clases['FechaReal'])

            df_clases['Año'] = df_clases['FechaReal'].dt.year
            df_clases['Mes'] = df_clases['FechaReal'].dt.month

            todos_los_meses = pd.DataFrame({'Mes': range(1, 13)})
            nombres_meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
            año_anterior = año_seleccionado - 1

            meses_map = {
                'ENERO':1,'FEBRERO':2,'MARZO':3,'ABRIL':4,'MAYO':5,'JUNIO':6,
                'JULIO':7,'AGOSTO':8,'SEPTIEMBRE':9,'OCTUBRE':10,'NOVIEMBRE':11,'DICIEMBRE':12
            }

            def agrupar_ingresos(df):
                if df is None or df.empty:
                    return todos_los_meses.assign(ingresos_fact=0)
                if not pd.api.types.is_datetime64_any_dtype(df['FechaReal']):
                    df = df.copy()
                    df['FechaReal'] = pd.to_datetime(df['FechaReal'])
                df = df.copy()
                df['Mes'] = df['FechaReal'].dt.month
                agrupado = df.groupby('Mes')['ingresos_fact'].sum().reset_index()
                return todos_los_meses.merge(agrupado, on='Mes', how='left').fillna({'ingresos_fact': 0})

            def agrupar_presupuesto(df_m):
                if df_m is None or df_m.empty:
                    return None
                df_m = df_m.copy()
                col_mes   = 'MesMeta'   if 'MesMeta'   in df_m.columns else 'MesPresupuesto'
                col_valor = 'ValorMeta' if 'ValorMeta'  in df_m.columns else 'TotalPresupuesto'
                df_m['MesNumero'] = df_m[col_mes].str.upper().map(meses_map)
                presupuesto_mes = df_m.groupby('MesNumero')[col_valor].sum().reset_index()
                presupuesto_mes.columns = ['Mes', 'Presupuesto']
                return todos_los_meses.merge(presupuesto_mes, on='Mes', how='left').fillna({'Presupuesto': 0})

            # ── Datos ─────────────────────────────────────────────────────────
            df_año = df_clases[df_clases['Año'] == año_seleccionado].copy()
            if df_año.empty:
                st.warning(f"No hay datos para el año {año_seleccionado}")
                return

            ingresos_actual   = agrupar_ingresos(df_año)
            ingresos_anterior = agrupar_ingresos(df_clases_anterior)
            presupuesto_actual = agrupar_presupuesto(df_metas)

            hay_anterior = df_clases_anterior is not None and not df_clases_anterior.empty

            # ── Gráfica ───────────────────────────────────────────────────────
            fig = go.Figure()

            # Barra año anterior
            if hay_anterior:
                fig.add_trace(go.Bar(
                    x=nombres_meses,
                    y=ingresos_anterior['ingresos_fact'],
                    name=f'Ventas {año_anterior}',
                    marker=dict(color="#bababa"),
                    text=[f'${x:,.0f}' for x in ingresos_anterior['ingresos_fact']],
                    textposition='outside',
                    textfont=dict(size=9),
                    hovertemplate=f'<b>%{{x}}</b><br>Ventas {año_anterior}: $%{{y:,.2f}} USD<extra></extra>'
                ))

            # Barra año actual
            fig.add_trace(go.Bar(
                x=nombres_meses,
                y=ingresos_actual['ingresos_fact'],
                name=f'Ventas {año_seleccionado}',
                marker=dict(color="#55a2da"),
                text=[f'${x:,.0f}' for x in ingresos_actual['ingresos_fact']],
                textposition='outside',
                textfont=dict(size=9),
                hovertemplate=f'<b>%{{x}}</b><br>Ventas {año_seleccionado}: $%{{y:,.2f}} USD<extra></extra>'
            ))

            # Línea presupuesto año actual
            if presupuesto_actual is not None:
                fig.add_trace(go.Scatter(
                    x=nombres_meses,
                    y=presupuesto_actual['Presupuesto'],
                    mode='lines+markers+text',
                    line=dict(color="#196cb1", width=3, dash='dash'),
                    marker=dict(size=8, color='#196cb1', symbol='diamond'),
                    text=[f'${x:,.0f}' for x in presupuesto_actual['Presupuesto']],
                    textposition='bottom center',
                    textfont=dict(size=10, color='#196cb1'),
                    name=f'Presupuesto {año_seleccionado}',
                    hovertemplate=f'<b>%{{x}}</b><br>Presupuesto {año_seleccionado}: $%{{y:,.2f}} USD<extra></extra>'
                ))

            # ── Título ────────────────────────────────────────────────────────
            if len(vendedores_lista) == 1:
                titulo_vendedores = vendedores_lista[0]
            elif len(vendedores_lista) <= 3:
                titulo_vendedores = ", ".join(vendedores_lista)
            else:
                titulo_vendedores = f"{len(vendedores_lista)} Vendedores"

            titulo = (
                f'Ventas vs Presupuesto — {año_anterior} vs {año_seleccionado} — {titulo_vendedores}'
                if hay_anterior else
                f'Ventas vs Presupuesto — {año_seleccionado} — {titulo_vendedores}'
            )

            fig.update_layout(
                title=titulo,
                xaxis_title='Mes',
                yaxis_title='💰 Venta ($USD)',
                barmode='group',
                hovermode='x unified',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=520,
                template='plotly_white',
                xaxis=dict(tickmode='array', tickvals=list(range(12)), ticktext=nombres_meses),
                yaxis=dict(tickformat='$,.0f', gridcolor='lightgray')
            )

            st.plotly_chart(fig, use_container_width=True)

            # ── Tabla resumen ─────────────────────────────────────────────────
            st.subheader("📊 Resumen Mensual")

            resumen_data = {'Mes': nombres_meses}

            if hay_anterior:
                resumen_data[f'Ventas {año_anterior}'] = ingresos_anterior['ingresos_fact'].values

            resumen_data[f'Ventas {año_seleccionado}'] = ingresos_actual['ingresos_fact'].values

            if presupuesto_actual is not None:
                resumen_data[f'Presupuesto {año_seleccionado}'] = presupuesto_actual['Presupuesto'].values
                resumen_data['Diferencia'] = (
                    ingresos_actual['ingresos_fact'].values - presupuesto_actual['Presupuesto'].values
                )
                resumen_data['% Cumplimiento'] = [
                    a / p * 100 if p != 0 else 0
                    for a, p in zip(ingresos_actual['ingresos_fact'].values, presupuesto_actual['Presupuesto'].values)
                ]

            resumen_df = pd.DataFrame(resumen_data)

            col_config = {"Mes": st.column_config.TextColumn("Mes", width="small")}
            cols_mostrar = ['Mes']

            def fmt_money(col, label):
                resumen_df[col + '_f'] = resumen_df[col].apply(lambda x: f'${x:,.2f}')
                col_config[col + '_f'] = st.column_config.TextColumn(label, width="medium")
                cols_mostrar.append(col + '_f')

            if hay_anterior:
                fmt_money(f'Ventas {año_anterior}', f'Ventas {año_anterior} (USD)')

            fmt_money(f'Ventas {año_seleccionado}', f'Ventas {año_seleccionado} (USD)')

            if presupuesto_actual is not None:
                fmt_money(f'Presupuesto {año_seleccionado}', f'Presupuesto {año_seleccionado} (USD)')
                fmt_money('Diferencia', 'Diferencia (USD)')
                resumen_df['cum_f'] = resumen_df['% Cumplimiento'].apply(lambda x: f'{x:.1f}%')
                col_config['cum_f'] = st.column_config.TextColumn("% Cumplimiento", width="small")
                cols_mostrar.append('cum_f')

            st.dataframe(
                resumen_df[cols_mostrar],
                hide_index=True,
                use_container_width=True,
                column_config=col_config
            )

        except Exception as e:
            st.error(f"Error al generar la gráfica: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

    ############################################
    # 
    ############################################


    def generar_grafica_lineas_por_vendedor(self, df):
        """
        Genera gráfica de líneas con una línea por vendedor.
        df debe contener:
        RepresentanteDeVentas | Año | Mes | total_ingresos
        """

        if df is None or df.empty:
            st.warning("No hay datos para mostrar la gráfica mensual por vendedor.")
            return

        columnas_requeridas = ["RepresentanteDeVentas", "Mes", "total_ingresos"]
        for col in columnas_requeridas:
            if col not in df.columns:
                st.error(f"Falta la columna requerida: {col}")
                st.write("Columnas disponibles:", df.columns.tolist())
                return

        df_plot = df.copy()
        df_plot["Mes"] = pd.to_numeric(df_plot["Mes"], errors="coerce").fillna(0).astype(int)
        df_plot["total_ingresos"] = pd.to_numeric(df_plot["total_ingresos"], errors="coerce").fillna(0)

        # 🔥 Nombres de meses bonitos
        nombres_meses = {
            1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
            5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
            9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
        }
        df_plot["MesNombre"] = df_plot["Mes"].map(nombres_meses)

        # Orden correcto de meses
        orden_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        df_plot["MesNombre"] = pd.Categorical(df_plot["MesNombre"], categories=orden_meses, ordered=True)

        # Agrupar por si vienen duplicados
        df_plot = df_plot.groupby(["RepresentanteDeVentas", "MesNombre"], as_index=False)["total_ingresos"].sum()

        fig = px.line(
            df_plot,
            x="MesNombre",
            y="total_ingresos",
            color="RepresentanteDeVentas",
            markers=True
        )
        

        fig.update_layout(
            xaxis_title="Mes",
            yaxis_title="Venta ($USD)",
            hovermode="x unified",
            legend_title="Vendedores"
        )
        
        st.plotly_chart(fig, use_container_width=True)


