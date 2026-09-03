# vista/perfiles_vista.py - MODIFICADO
"""
Vista para análisis de perfiles de vendedores
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import calendar
from datetime import datetime, timedelta
from vista.base_vista import BaseVista
import plotly.express as px




class PerfilesVista(BaseVista):
    """Vista para mostrar perfiles de vendedores"""
    
    def __init__(self):
        super().__init__()
        self.titulo = "Perfiles de Vendedores"
        self.icono = "👤"
        
    
    def mostrar_info_seleccion_rango(self, vendedor, fecha_inicio, fecha_fin):
        """Muestra la información seleccionada con rango de fechas"""
        # Si no se pasa fecha de inicio, usar 01/01/2025 como default
        if fecha_inicio is None:
            fecha_inicio = datetime(2025, 1, 1)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Vendedor:** {vendedor}")
        with col2:
            st.info(f"**Fecha Inicio:** {fecha_inicio.strftime('%d/%m/%Y')}")
        with col3:
            st.info(f"**Fecha Fin:** {fecha_fin.strftime('%d/%m/%Y')}")
        
        st.markdown("---")

    def mostrar_info_seleccion(self, vendedor, años):
        """Muestra la información seleccionada (método original)"""
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Vendedor:** {vendedor}")
        with col2:
            st.info(f"**Años:** {', '.join(map(str, años))}")
        
        st.markdown("---")

    def mostrar_grafica_ventas_rango(self, df, vendedor, fecha_inicio, fecha_fin):
        """Muestra la gráfica de ventas mensuales para el rango de fechas"""
        fig = self._crear_grafica_ventas_mensuales_rango(df, vendedor, fecha_inicio, fecha_fin)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            self.mostrar_error("No se pudo crear la gráfica. Revisa los datos.")

    # def mostrar_grafica_cotizaciones_rango(self, df, vendedor, fecha_inicio, fecha_fin):
    #     """Muestra la gráfica de cotizaciones mensuales para el rango de fechas"""
    #     fig = self._crear_grafica_cotizaciones_mensuales_rango(df, vendedor, fecha_inicio, fecha_fin)
    #     if fig is not None:
    #         st.plotly_chart(fig, use_container_width=True)
    #     else:
    #         self.mostrar_error("No se pudo crear la gráfica. Revisa los datos.")

    def mostrar_resumen_estadistico_rango(self, df, fecha_inicio, fecha_fin):
        """Muestra el resumen estadístico para el rango de fechas"""
        st.markdown("### 📈 Total Estimado del Período")
        
        if df.empty:
            st.warning("No hay datos para mostrar en el período seleccionado.")
            return
        
        # Calcular métricas del período
        total_vendido = df['TotalVendido'].sum()
        total_ventas = df['NumVentas'].sum()
        
        # Calcular número de meses en el rango
        diff_meses = ((fecha_fin.year - fecha_inicio.year) * 12 + 
                     (fecha_fin.month - fecha_inicio.month) + 1)
        promedio_mensual = total_vendido / diff_meses if diff_meses > 0 else 0
        
        # Encontrar mejor y peor mes
        if not df.empty:
            mejor_mes = df.loc[df['TotalVendido'].idxmax()]
            peor_mes = df.loc[df['TotalVendido'].idxmin()]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total Estimado Vendido",
                value=f"${total_vendido:,.0f} USD"
            )

        with col2:
            st.metric(
                label="🗓️ Meses Analizados",
                value=f"{diff_meses}"
            )
        

        
        
        # with col2:
        #     st.metric(
        #         label="📊 Total Cantidad Estimada de Ventas",
        #         value=f"{total_ventas}"
        #     )
        
        # with col3:
        #     st.metric(
        #         label="📅 Promedio Mensual",
        #         value=f"${promedio_mensual:,.0f}"
        #     )
        
        # with col4:
        #     st.metric(
        #         label="🗓️ Meses Analizados",
        #         value=f"{diff_meses}"
        #     )
        
        # if not df.empty:
        #     col5, col6 = st.columns(2)
        #     with col5:
        #         st.success(f"🏆 Mejor mes: {mejor_mes['NombreMes']} {int(mejor_mes['Año'])}")
        #         st.caption(f"${mejor_mes['TotalVendido']:,.0f}")
            
        #     with col6:
        #         st.info(f"📉 Menor mes: {peor_mes['NombreMes']} {int(peor_mes['Año'])}")
        #         st.caption(f"${peor_mes['TotalVendido']:,.0f}")

    def mostrar_sidebar_perfiles(self):
        """Muestra la barra lateral con controles usando multiselect"""
        from .seleccion_usuarios.seleccion import SeleccionUsuarios
        seleccion_usuarios = SeleccionUsuarios()
        vendedores = seleccion_usuarios.vendedores_selector()  # Cambio aquí
        return vendedores


    def _crear_grafica_ventas_mensuales_rango(self, df, vendedor, fecha_inicio, fecha_fin):
        """Crea la gráfica de líneas para ventas mensuales en un rango de fechas con líneas separadas por año"""
        if df.empty:
            self.mostrar_warning("No hay datos para mostrar")
            return None
        
        # Obtener años únicos en los datos
        años_en_datos = sorted(df['Año'].unique())
        
        # Crear DataFrame completo con todos los meses del rango
        meses_completos = []
        for año in años_en_datos:
            # Determinar el rango de meses para este año específico
            if año == fecha_inicio.year:
                mes_inicio = fecha_inicio.month
            else:
                mes_inicio = 1
                
            if año == fecha_fin.year:
                mes_fin = fecha_fin.month
            else:
                mes_fin = 12
            
            for mes in range(mes_inicio, mes_fin + 1):
                meses_completos.append({
                    'Año': int(año),
                    'Mes': mes,
                    'NombreMes': calendar.month_name[mes],
                    'TotalVendido': 0.0,
                    'NumVentas': 0
                })
        
        df_completo = pd.DataFrame(meses_completos)
        
        # Asegurar tipos de datos correctos
        df['Año'] = df['Año'].astype(int)
        df['Mes'] = df['Mes'].astype(int)
        df['TotalVendido'] = pd.to_numeric(df['TotalVendido'], errors='coerce').fillna(0)
        
        # Combinar con datos reales usando merge
        df_merged = df_completo.merge(
            df[['Año', 'Mes', 'TotalVendido', 'NumVentas']], 
            on=['Año', 'Mes'], 
            how='left',
            suffixes=('', '_real')
        )
        
        # Usar datos reales donde existan
        df_merged['TotalVendido'] = df_merged['TotalVendido_real'].fillna(df_merged['TotalVendido'])
        df_merged['NumVentas'] = df_merged['NumVentas_real'].fillna(df_merged['NumVentas'])
        
        # Limpiar columnas auxiliares
        df_merged = df_merged.drop(columns=['TotalVendido_real', 'NumVentas_real'], errors='ignore')
        
        # Crear la gráfica
        fig = go.Figure()
        
        # Colores para cada año
        colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # Crear una línea para cada año
        for i, año in enumerate(años_en_datos):
            df_año = df_merged[df_merged['Año'] == año].sort_values('Mes')
            
            if not df_año.empty:
                # Crear etiquetas solo con el nombre del mes (sin año) ya que cada línea representa un año
                x_labels = [row['NombreMes'][:3] for _, row in df_año.iterrows()]
                
                fig.add_trace(go.Scatter(
                    name=str(año),
                    x=x_labels,
                    y=df_año['TotalVendido'],
                    mode='lines+markers',
                    line=dict(color=colores[i % len(colores)], width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x} ' + str(año) + '</b><br>' +
                                'Ventas: $%{y:,.0f}<br>' +
                                '<extra></extra>'
                ))
        
        # Si hay múltiples años, mostrar leyenda; si es un solo año, ocultarla
        mostrar_leyenda = len(años_en_datos) > 1
        
        fig.update_layout(
            title=dict(
                text=f'Ventas Estimadas Mensuales - {vendedor}',
                x=0,
                font=dict(size=24)
            ),
            xaxis_title='Mes',
            yaxis_title='💰 Total Estimado Vendido ($USD)',
            height=600,
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1
            ) if mostrar_leyenda else dict(),
            yaxis=dict(
                tickformat='$,.0f'
            ),
            showlegend=mostrar_leyenda
        )
        
        return fig

    # def _crear_grafica_cotizaciones_mensuales_rango(self, df, vendedor, fecha_inicio, fecha_fin):
    #     """Crea la gráfica de líneas para cotizaciones mensuales en un rango de fechas con líneas separadas por año"""
    #     if df.empty:
    #         self.mostrar_warning("No hay datos para mostrar")
    #         return None
        
    #     # Obtener años únicos en los datos
    #     años_en_datos = sorted(df['Año'].unique())
        
    #     # Crear DataFrame completo con todos los meses del rango
    #     meses_completos = []
    #     for año in años_en_datos:
    #         # Determinar el rango de meses para este año específico
    #         if año == fecha_inicio.year:
    #             mes_inicio = fecha_inicio.month
    #         else:
    #             mes_inicio = 1
                
    #         if año == fecha_fin.year:
    #             mes_fin = fecha_fin.month
    #         else:
    #             mes_fin = 12
            
    #         for mes in range(mes_inicio, mes_fin + 1):
    #             meses_completos.append({
    #                 'Año': int(año),
    #                 'Mes': mes,
    #                 'NombreMes': calendar.month_name[mes],
    #                 'TotalCotizado': 0.0,
    #                 'NumVentas': 0
    #             })
        
    #     df_completo = pd.DataFrame(meses_completos)
        
    #     # Asegurar tipos de datos correctos
    #     df['Año'] = df['Año'].astype(int)
    #     df['Mes'] = df['Mes'].astype(int)
    #     df['TotalCotizado'] = pd.to_numeric(df['TotalCotizado'], errors='coerce').fillna(0)
        
    #     # Combinar con datos reales usando merge
    #     df_merged = df_completo.merge(
    #         df[['Año', 'Mes', 'TotalCotizado', 'NumVentas']], 
    #         on=['Año', 'Mes'], 
    #         how='left',
    #         suffixes=('', '_real')
    #     )
        
    #     # Usar datos reales donde existan
    #     df_merged['TotalCotizado'] = df_merged['TotalCotizado_real'].fillna(df_merged['TotalCotizado'])
    #     df_merged['NumVentas'] = df_merged['NumVentas_real'].fillna(df_merged['NumVentas'])
        
    #     # Limpiar columnas auxiliares
    #     df_merged = df_merged.drop(columns=['TotalCotizado_real', 'NumVentas_real'], errors='ignore')
        
    #     # Crear la gráfica
    #     fig = go.Figure()
        
    #     # Colores para cada año (usando una paleta diferente para cotizaciones)
    #     colores = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#1f77b4']
        
    #     # Crear una línea para cada año
    #     for i, año in enumerate(años_en_datos):
    #         df_año = df_merged[df_merged['Año'] == año].sort_values('Mes')
            
    #         if not df_año.empty:
    #             # Crear etiquetas solo con el nombre del mes (sin año) ya que cada línea representa un año
    #             x_labels = [row['NombreMes'][:3] for _, row in df_año.iterrows()]
                
    #             fig.add_trace(go.Scatter(
    #                 name=str(año),
    #                 x=x_labels,
    #                 y=df_año['TotalCotizado'],
    #                 mode='lines+markers',
    #                 line=dict(color=colores[i % len(colores)], width=3),
    #                 marker=dict(size=8),
    #                 hovertemplate='<b>%{x} ' + str(año) + '</b><br>' +
    #                             'Cotizado: $%{y:,.0f}<br>' +
    #                             '<extra></extra>'
    #             ))
        
    #     # Si hay múltiples años, mostrar leyenda; si es un solo año, ocultarla
    #     mostrar_leyenda = len(años_en_datos) > 1
        
    #     fig.update_layout(
    #         title=dict(
    #             text=f'Cotizaciones Mensuales - {vendedor}',
    #             x=0.5,
    #             font=dict(size=20)
    #         ),
    #         xaxis_title='Mes',
    #         yaxis_title='Total Cotizado ($)',
    #         height=600,
    #         hovermode='x unified',
    #         legend=dict(
    #             orientation="h",
    #             yanchor="bottom",
    #             y=1.02,
    #             xanchor="right",
    #             x=1
    #         ) if mostrar_leyenda else dict(),
    #         yaxis=dict(
    #             tickformat='$,.0f'
    #         ),
    #         showlegend=mostrar_leyenda
    #     )
        
    #     return fig

    # Mantener métodos originales para compatibilidad
    def mostrar_grafica_ventas(self, df, vendedor, años_seleccionados):
        """Muestra la gráfica de ventas mensuales (método original)"""
        fig = self._crear_grafica_ventas_mensuales(df, vendedor, años_seleccionados)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            self.mostrar_error("No se pudo crear la gráfica. Revisa los datos.")

    # def mostrar_grafica_cotizaciones(self, df, vendedor, años_seleccionados):
    #     """Muestra la gráfica de cotizaciones mensuales (método original)"""
    #     fig = self._crear_grafica_cotizaciones_mensuales(df, vendedor, años_seleccionados)
    #     if fig is not None:
    #         st.plotly_chart(fig, use_container_width=True)
    #     else:
    #         self.mostrar_error("No se pudo crear la gráfica. Revisa los datos.")

    def mostrar_resumen_estadistico(self, df, años_seleccionados):
        """Muestra el resumen estadístico por año (método original)"""
        st.markdown("### 📈 Total Estimado Vendido por Año")
        resumen_cols = st.columns(len(años_seleccionados))
        
        for i, año in enumerate(años_seleccionados):
            df_año = df[df['Año'] == año]
            total_año = df_año['TotalVendido'].sum()
            ventas_año = df_año['NumVentas'].sum()
            promedio_mes = total_año / 12 if total_año > 0 else 0
            
            # with resumen_cols[i]:
            #     st.metric(
            #         label=f"📅 {año}",
            #         value=f"💰 Total Estimado Vendido: ${total_año:,.0f} USD",
            #         #delta=f"Promedio mensual: ${promedio_mes:,.0f}"
            #         delta=f"📊 Total Cantidad Estimada de Ventas: {ventas_año}"
            #     )
            #     #st.caption(f"Total de ventas: {ventas_año}")

            col1, col2, col3, col4 = st.columns(4)
        
            with col1:
                st.metric(
                    label=f"💰 Total Estimado Vendido {año}",
                    value=f"${total_año:,.0f} USD"
                )
            
            # with col2:
            #     st.metric(
            #         label="📊 Total Cantidad Estimada de Ventas",
            #         value=f"{ventas_año}"
            #     )
            

    def _crear_grafica_ventas_mensuales(self, df, vendedor, años_seleccionados):
        """Crea la gráfica de líneas para ventas mensuales (método original)"""
        if df.empty:
            self.mostrar_warning("No hay datos para mostrar")
            return None
        
        # Crear DataFrame completo con todos los meses
        meses_completos = []
        for año in años_seleccionados:
            for mes in range(1, 13):
                meses_completos.append({
                    'Año': int(año),
                    'Mes': mes,
                    'NombreMes': calendar.month_name[mes],
                    'TotalVendido': 0.0,
                    'NumVentas': 0
                })
        
        df_completo = pd.DataFrame(meses_completos)
        
        # Asegurar tipos de datos correctos
        df['Año'] = df['Año'].astype(int)
        df['Mes'] = df['Mes'].astype(int)
        df['TotalVendido'] = pd.to_numeric(df['TotalVendido'], errors='coerce').fillna(0)
        
        # Combinar con datos reales usando merge
        df_merged = df_completo.merge(
            df[['Año', 'Mes', 'TotalVendido', 'NumVentas']], 
            on=['Año', 'Mes'], 
            how='left',
            suffixes=('', '_real')
        )
        
        # Usar datos reales donde existan
        df_merged['TotalVendido'] = df_merged['TotalVendido_real'].fillna(df_merged['TotalVendido'])
        df_merged['NumVentas'] = df_merged['NumVentas_real'].fillna(df_merged['NumVentas'])
        
        # Limpiar columnas auxiliares
        df_merged = df_merged.drop(columns=['TotalVendido_real', 'NumVentas_real'], errors='ignore')
        
        # Crear la gráfica
        fig = go.Figure()
        
        # Colores para cada año
        colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        # Lista de meses en orden
        meses_orden = [calendar.month_name[i] for i in range(1, 13)]
        
        for i, año in enumerate(sorted(años_seleccionados)):
            df_año = df_merged[df_merged['Año'] == año].sort_values('Mes')
            
            # Verificar que tenemos datos
            if not df_año.empty:
                fig.add_trace(go.Scatter(
                    name=str(año),
                    x=df_año['NombreMes'],
                    y=df_año['TotalVendido'],
                    mode='lines+markers',
                    line=dict(color=colores[i % len(colores)], width=2),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>' +
                                f'Año: {año}<br>' +
                                'Ventas: $%{y:,.0f}<br>' +
                                '<extra></extra>'
                ))
        
        fig.update_layout(
            title=dict(
                text=f'Ventas Estimadas Mensuales - {vendedor}',
                x=0,
                font=dict(size=24)
            ),
            xaxis_title='Mes',
            yaxis_title='💰 Total Estimado Vendido ($USD)',
            height=600,
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=0
            ),
            xaxis=dict(
                categoryorder='array',
                categoryarray=meses_orden
            ),
            yaxis=dict(
                tickformat='$,.0f'
            ),
            showlegend=True
        )
        
        return fig


    """
        Nuevos Activos
    """
    def mostrar_dashboard_nuevos_activos(self, df, vendedores_seleccionados=None):
        """
        Muestra el dashboard de clientes nuevos vs activos
        """
        if df is not None and not df.empty:
            # Mostrar información de vendedores seleccionados
            self._mostrar_info_vendedores(vendedores_seleccionados)
            
            # Procesar datos
            clientes_activos = df[df['Tipo'] == 'Clientes Activos']['Total'].iloc[0]
            clientes_nuevos = df[df['Tipo'] == 'Clientes Nuevos']['Total'].iloc[0]
            
            # Calcular totales y porcentajes
            total_clientes = clientes_activos + clientes_nuevos
            porcentaje_activos = (clientes_activos / total_clientes) * 100 if total_clientes > 0 else 0
            porcentaje_nuevos = (clientes_nuevos / total_clientes) * 100 if total_clientes > 0 else 0
            
            # Mostrar métricas
            self._mostrar_metricas_clientes(total_clientes, clientes_activos, clientes_nuevos, 
                                          porcentaje_activos, porcentaje_nuevos)
            
            # Mostrar gráfica de pastel
            self._mostrar_grafica_pastel(clientes_activos, clientes_nuevos, 
                                       porcentaje_activos, porcentaje_nuevos, vendedores_seleccionados)
            
            # Mostrar resumen detallado
            self._mostrar_resumen_detallado(clientes_activos, clientes_nuevos, 
                                          total_clientes, porcentaje_activos, porcentaje_nuevos)
            
        else:
            st.error("No se pudieron obtener los datos. Verifica la conexión a la base de datos.")

    def _mostrar_info_vendedores(self, vendedores_seleccionados):
        """Muestra información de los vendedores seleccionados"""
        if vendedores_seleccionados:
            if len(vendedores_seleccionados) == 0:
                st.warning("⚠️ **Sin selección** - Por favor selecciona al menos un vendedor")
            elif len(vendedores_seleccionados) == 1:
                st.info(f"**Vendedor:** {vendedores_seleccionados[0]}")
            else:
                st.info(f"**🎯 {len(vendedores_seleccionados)} Vendedores Seleccionados**")
                
                # Mostrar lista en columnas para mejor visualización
                if len(vendedores_seleccionados) <= 4:
                    cols = st.columns(len(vendedores_seleccionados))
                    for i, vendedor in enumerate(vendedores_seleccionados):
                        with cols[i]:
                            st.write(f"**{i+1}.** {vendedor}")
                else:
                    # Si hay muchos vendedores, mostrar en un expander
                    with st.expander(f"📋 Ver todos los {len(vendedores_seleccionados)} vendedores"):
                        for i, vendedor in enumerate(vendedores_seleccionados, 1):
                            st.write(f"{i}. {vendedor}")
        
        st.markdown("---")

    def _mostrar_grafica_pastel(self, activos, nuevos, porc_activos, porc_nuevos, vendedores_seleccionados=None):
        """Crea y muestra la gráfica de pastel"""
        # Preparar datos para la gráfica
        datos_grafica = pd.DataFrame({
            'Categoría': ['Clientes Activos', 'Clientes Nuevos'],
            'Cantidad': [activos, nuevos],
            'Porcentaje': [porc_activos, porc_nuevos]
        })
        
        # Título dinámico basado en la selección
        if vendedores_seleccionados:
            if len(vendedores_seleccionados) == 0:
                titulo = 'Sin datos - Selecciona vendedores'
            elif len(vendedores_seleccionados) == 1:
                titulo = f'Clientes: {vendedores_seleccionados[0]}'
            else:
                titulo = f'Clientes de {len(vendedores_seleccionados)} Vendedores'
        else:
            titulo = 'Distribución de Clientes: Nuevos vs Activos'
        
        # Crear gráfica de pastel con Plotly
        fig = px.pie(
            datos_grafica, 
            values='Cantidad', 
            names='Categoría',
            title=titulo,
            color_discrete_sequence=['#66b3ff', '#99ff99'],
            hover_data=['Porcentaje']
        )
        
        # Personalizar la gráfica
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            textfont=dict(size=16, family="Arial, sans-serif", color="black"),
            hovertemplate='<b>%{label}</b><br>' +
                          'Cantidad: %{value}<br>' +
                          'Porcentaje: %{percent}<br>' +
                          '<extra></extra>'
        )
        
        fig.update_layout(
            font_size=16,
            title_font_size=20,
            title_x=0,
            title_y=0.97,
            title_xanchor="left",
            showlegend=True,
            legend=dict(
                title="Estados del cliente",
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=0,
                font=dict(size=14)
            ),
            height=600,
            margin=dict(t=100, b=100, l=50, r=50)
        )

        st.plotly_chart(fig, use_container_width=True)

    def _mostrar_metricas_clientes(self, total, activos, nuevos, porc_activos, porc_nuevos):
        """Muestra las métricas principales"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Clientes", total)
        
        with col2:
            st.metric("Clientes Activos", f"{activos} ({porc_activos:.1f}%)")
        
        with col3:
            st.metric("Clientes Nuevos", f"{nuevos} ({porc_nuevos:.1f}%)")
    
    def _mostrar_resumen_detallado(self, activos, nuevos, total, porc_activos, porc_nuevos):
        """Muestra el resumen detallado en tabla"""
        st.write("### 📋 Resumen Detallado")
        
        resumen = pd.DataFrame({
            'Categoría': ['Clientes Activos', 'Clientes Nuevos', 'Total'],
            'Cantidad': [activos, nuevos, total],
            'Porcentaje': [f"{porc_activos:.2f}%", f"{porc_nuevos:.2f}%", "100.00%"]
        })
        
        st.dataframe(resumen, use_container_width=True, hide_index=True)


    """
    Status Cliente
    """
    def mostrar_dashboard_status_clientes(self, df, vendedores_seleccionados=None):
        """
        Muestra el dashboard completo de status de clientes
        """
        if df is not None and not df.empty:
            # Mostrar información de vendedores seleccionados
            self._mostrar_info_vendedores(vendedores_seleccionados)
            
            # Mostrar métricas principales
            self._mostrar_metricas_status_principales(df)
            
            # Mostrar gráfica de pastel
            self.mostrar_grafica_status_clientes(df, vendedores_seleccionados)
            
            # Mostrar tabla detallada
            self._mostrar_tabla_status_detallada(df)
            
        else:
            st.error("No se pudieron obtener los datos de status de clientes.")

    def mostrar_grafica_status_clientes(self, df, vendedores_seleccionados=None):
        """
        Gráfica de status de clientes adaptada para multiselect
        """
        if df.empty:
            st.warning("No hay datos de status de clientes para mostrar")
            return

        # Título dinámico basado en la selección
        if vendedores_seleccionados:
            if len(vendedores_seleccionados) == 0:
                titulo = 'Sin datos - Selecciona vendedores'
            elif len(vendedores_seleccionados) == 1:
                titulo = f'Status de Clientes - {vendedores_seleccionados[0]}'
            else:
                titulo = f'Status de Clientes de {len(vendedores_seleccionados)} Vendedores'
        else:
            titulo = 'Distribución por Tipo de Cliente'

        # Texto para hover
        df['hover_text'] = df.apply(
            lambda x: f"<b>{x['TipoCliente']}</b><br>"
                    f"Cantidad: {x['Cantidad']:,}<br>"
                    f"Porcentaje: {x['Porcentaje']:.1f}%<br>"
                    f"Ventas totales: ${x['TotalVentas']:,.2f} USD",
            axis=1
        )

        df['TextoPersonalizado'] = df.apply(
            lambda x: f"{x['TipoCliente']}<br>{x['Cantidad']} clientes<br>${x['TotalVentas']:,.0f}",
            axis=1
        )

        # Crear gráfica de pastel
        fig = px.pie(
            df,
            values='Cantidad',
            names='TipoCliente',
            title=titulo,
            color_discrete_sequence=['#4A90E2', '#7ED321', '#F5A623', '#BD10E0', '#50E3C2']
        )

        # Personalizar trazas
        fig.update_traces(
            textposition='inside',
            text=df['TextoPersonalizado'],
            textfont=dict(
                size=14,
                family="Arial, sans-serif",
                color="black"
            ),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=df['hover_text']
        )

        # Ajustes de layout con leyenda arriba a la izquierda
        fig.update_layout(
            font_size=16,
            title_font_size=20,
            title_x=0,
            title_y=0.97,
            title_xanchor="left",
            showlegend=True,
            legend=dict(
                title="Tipo de Cliente",
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=0,
                font=dict(size=14)
            ),
            height=600,
            margin=dict(t=100, b=100, l=50, r=50)
        )

        st.plotly_chart(fig, use_container_width=True)

    def _mostrar_metricas_status_principales(self, df):
        """Muestra las métricas principales de status de clientes"""
        if df.empty:
            return
            
        total_general = df['TotalGeneral'].iloc[0] if not df.empty else 0
        total_ventas = df['TotalVentas'].sum() if not df.empty else 0
        
        # Calcular cliente con más ventas
        cliente_top = df.loc[df['TotalVentas'].idxmax()] if not df.empty and df['TotalVentas'].sum() > 0 else None
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Clientes", f"{total_general:,}")
        
        with col2:
            if cliente_top is not None:
                st.metric("🏆 Status con Más Ventas Estimadas", cliente_top['TipoCliente'])
            else:
                st.metric("🏆 Status con Más Ventas Estimadas", "N/A")
        # with col3:
        #     st.metric("💰 Ventas Totales", f"${total_ventas:,.0f}")
        # with col4:
        #     promedio_por_tipo = total_ventas / len(df) if len(df) > 0 else 0
        #     st.metric("📈 Promedio por Tipo", f"${promedio_por_tipo:,.0f}")

    def _mostrar_tabla_status_detallada(self, df):
        """Muestra tabla detallada con resumen por tipo de cliente"""
        st.markdown("### 📋 Resumen Detallado por Tipo de Cliente")
        
        if df.empty:
            st.warning("No hay datos para mostrar en la tabla")
            return
        
        # Preparar tabla para mostrar
        tabla_resumen = df[['TipoCliente', 'Cantidad', 'Porcentaje', 'TotalVentas']].copy()
        tabla_resumen['Porcentaje'] = tabla_resumen['Porcentaje'].apply(lambda x: f"{x:.1f}%")
        tabla_resumen['TotalVentas'] = tabla_resumen['TotalVentas'].apply(lambda x: f"${x:,.0f}")
        tabla_resumen.columns = ['Tipo de Cliente', 'Cantidad', 'Porcentaje', 'Total Ventas']
        
        # Agregar fila de total
        total_general = df['TotalGeneral'].iloc[0]
        total_ventas = df['TotalVentas'].sum()
        fila_total = {
            'Tipo de Cliente': '📊 TOTAL',
            'Cantidad': total_general,
            'Porcentaje': '100.0%',
            'Total Ventas': f"${total_ventas:,.0f}"
        }
        
        # Usar pd.concat en lugar de append
        tabla_completa = pd.concat([tabla_resumen, pd.DataFrame([fila_total])], ignore_index=True)
        
        st.dataframe(tabla_completa, use_container_width=True, hide_index=True)