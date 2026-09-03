# vista/rendimiento_vista.py
"""
Vista para hacer graficas de rendimiento
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import calendar
from datetime import datetime, timedelta
from vista.base_vista import BaseVista
import plotly.express as px
from modelo.metas_modelo import MetasModelo
from .seleccion_usuarios.seleccion import SeleccionUsuarios
from modelo.rendimiento_modelo import RendimientoModelo


class RendimientoVista:
    def __init__(self):
        self.modelo_rendimiento = RendimientoModelo()

    ###############################################################################################
    ###-----------------------------LOS DEMAS ROLES---------------------------------------------###
    ###############################################################################################
    """
    ###############################################################################################
    """
    def mostrar_metricas_rendimiento(self, vendedores_seleccionados, fecha_inicio, fecha_fin):
        # Obtener métricas
        df_metricas = self.modelo_rendimiento.obtener_metricas_rendimiento(
            vendedores_seleccionados, 
            fecha_inicio, 
            fecha_fin
        )
        
        if df_metricas is not None and not df_metricas.empty:

            # Mostrar tabla de métricas
            st.subheader("📈 Detalle de Rendimiento")
            
            # Formatear el DataFrame para mostrar
            df_display = df_metricas.copy()
            
            # Renombrar columnas
            df_display = df_display.rename(columns={
                'NombreVendedor': 'Nombre Vendedor',
                'Total_Venta_Mensual': 'Total Venta del Mes (USD)',
                'ValorMeta': 'Valor Presupuesto del Mes (USD)',
                'Diferencia': 'Diferencia (USD)',
                'Rendimiento': 'Rendimiento',
                'Cumplimiento': 'Cumplimiento'
            })

            # Mostrar solo las columnas requeridas
            df_display = df_display[
                ['Total Venta del Mes (USD)', 'Valor Presupuesto del Mes (USD)', 'Cumplimiento']
            ]
            
            # Formatear valores numéricos
            df_display['Total Venta del Mes (USD)'] = df_display['Total Venta del Mes (USD)'].apply(lambda x: f"${x:,.2f}")
            df_display['Valor Presupuesto del Mes (USD)'] = df_display['Valor Presupuesto del Mes (USD)'].apply(lambda x: f"${x:,.2f}")
            # df_display['Diferencia (USD)'] = df_display['Diferencia (USD)'].apply(lambda x: f"${x:,.2f}")
            # df_display['Rendimiento'] = df_display['Rendimiento'].apply(lambda x: f"{x*100:.1f}%")
            df_display['Cumplimiento'] = df_display['Cumplimiento'].apply(lambda x: f"{x:.1f}%")


            # Calcular color según cumplimiento
            colores = []
            for _, fila in df_metricas.iterrows():
                venta = fila['Total_Venta_Mensual']
                meta = fila['ValorMeta']

                if venta >= meta:
                    colores.append('#A7DCA5')  # Verde (cumplió o superó la meta)
                elif venta >= meta * 0.7:
                    colores.append('#A7DCA5')  # Naranja (entre 80% y 99%)
                else:
                    colores.append('#A7DCA5')  # Rojo (por debajo del 80%)

            # Mostrar tabla
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico de barras
            st.markdown("---")
            st.subheader(f"📊 Ventas vs Presupuesto - {vendedores_seleccionados}")
            
            import plotly.graph_objects as go

            fig = go.Figure()

            # Barra de Venta Real (con color dinámico)
            fig.add_trace(go.Bar(
                name='Venta Real',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['Total_Venta_Mensual'],
                marker_color=colores,
                text=[f"${v:,.0f}" for v in df_metricas['Total_Venta_Mensual']],
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='$%{y:,.2f}<extra></extra>'
            ))

            # Barra de Meta (color fijo azul claro)
            fig.add_trace(go.Bar(
                name='Presupuesto',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['ValorMeta'],
                marker_color='#90D5FF',
                text=[f"${v:,.0f}" for v in df_metricas['ValorMeta']],
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='$%{y:,.2f}<extra></extra>'
            ))

            fig.update_layout(
                barmode='group',
                xaxis_title='Vendedor',
                yaxis_title='Monto (USD) 💰',
                height=500,
                xaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16)
                ),
                yaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16),
                    range=[0, df_metricas[['Total_Venta_Mensual', 'ValorMeta']].max().max() * 1.15]  # +15% margen
                ),
                legend=dict(
                    font=dict(size=14),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # Calcular porcentajes
            df_metricas['PorcentajeVenta'] = (df_metricas['Total_Venta_Mensual'] / df_metricas['ValorMeta']) * 100
            df_metricas['PorcentajeMeta'] = 100  # Meta fija al 100%

            # Asignar color dinámico según el rendimiento
            colores = []
            for p in df_metricas['PorcentajeVenta']:
                if p >= 100:
                    colores.append('#A7DCA5')  # Verde
                elif p >= 70:
                    colores.append('#A7DCA5')  # Naranja
                else:
                    colores.append('#A7DCA5')  # Rojo

            # st.markdown("---")
            st.subheader(f"📊 Ventas vs Presupuesto % - {vendedores_seleccionados}")

            import plotly.graph_objects as go

            fig2 = go.Figure()

            # Barra de Ventas Reales
            fig2.add_trace(go.Bar(
                name='Venta Real (%)',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['PorcentajeVenta'],
                marker_color=colores,
                text=[f"{v:.1f}%" for v in df_metricas['PorcentajeVenta']],
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='%{y:.1f}%<extra></extra>'  # Solo porcentaje
            ))

            # Barra de Meta (100%)
            fig2.add_trace(go.Bar(
                name='Presupuesto (100%)',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['PorcentajeMeta'],
                marker_color='#90D5FF',
                text=["100%"] * len(df_metricas),
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='%{y:.0f}%<extra></extra>'  # Solo porcentaje
            ))

            # Ajustar diseño
            fig2.update_layout(
                barmode='group',
                xaxis_title='Vendedor',
                yaxis_title='Cumplimiento (%)',
                height=500,
                xaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16)
                ),
                yaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16),
                    range=[0, max(110, df_metricas['PorcentajeVenta'].max() * 1.15)]
                    # range=[0, df_metricas[['Total_Venta_Mensual', 'ValorMeta']].max().max() * 1.15]  # +15% margen
                ),
                legend=dict(
                    font=dict(size=14),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )

            st.plotly_chart(fig2, use_container_width=True)            

        else:
            st.info("ℹ️ No se encontraron datos para los filtros seleccionados")

    """
    ###############################################################################################
    """
    def mostrar_metricas_rendimiento_rango(self, vendedores_seleccionados, fecha_inicio, fecha_fin):
        """
        Muestra las métricas de rendimiento para un rango de fechas
        """
        # Obtener métricas del rango
        df_metricas = self.modelo_rendimiento.obtener_metricas_rendimiento_rango(
            vendedores_seleccionados, 
            fecha_inicio, 
            fecha_fin
        )
        
        if df_metricas is not None and not df_metricas.empty:
            st.subheader("📈 Detalle de Rendimiento (Rango de Fechas)")
            
            # Formatear el DataFrame para mostrar
            df_display = df_metricas.copy()
            
            # Renombrar columnas
            df_display = df_display.rename(columns={
                'NombreVendedor': 'Nombre Vendedor',
                'Total_venta_rango': 'Total Venta (USD)',
                'ValorMeta': 'Valor Meta (USD)',
                'Diferencia': 'Diferencia (USD)',
                'Rendimiento': 'Rendimiento',
                'Cumplimiento' : 'Cumplimiento'
            })

            # Mostrar solo las columnas requeridas
            df_display = df_display[
                ['Total Venta (USD)', 'Valor Meta (USD)', 'Cumplimiento']
            ]
            
            # Formatear valores numéricos
            df_display['Total Venta (USD)'] = df_display['Total Venta (USD)'].apply(lambda x: f"${x:,.2f}")
            df_display['Valor Meta (USD)'] = df_display['Valor Meta (USD)'].apply(lambda x: f"${x:,.2f}")
            # df_display['Diferencia (USD)'] = df_display['Diferencia (USD)'].apply(lambda x: f"${x:,.2f}")
            # df_display['Rendimiento'] = df_display['Rendimiento'].apply(lambda x: f"{x*100:.1f}%")
            df_display['Cumplimiento'] = df_display['Cumplimiento'].apply(lambda x: f"{x:.1f}%")

            # Calcular color según cumplimiento
            colores = []
            for _, fila in df_metricas.iterrows():
                venta = fila['Total_venta_rango']
                meta = fila['ValorMeta']

                if venta >= meta:
                    colores.append('#A7DCA5')  # Verde
                elif venta >= meta * 0.7:
                    colores.append('#A7DCA5')  # Naranja
                else:
                    colores.append('#A7DCA5')  # Rojo

            # Mostrar tabla
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True
            )
            
            # Gráfico de barras USD
            st.markdown("---")
            st.subheader(f"📊 Ventas vs Presupuesto (USD) - {vendedores_seleccionados}")
            
            fig = go.Figure()

            # Barra de Venta Real (con color dinámico)
            fig.add_trace(go.Bar(
                name='Venta Real',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['Total_venta_rango'],
                marker_color=colores,
                text=[f"${v:,.0f}" for v in df_metricas['Total_venta_rango']],
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='$%{y:,.2f}<extra></extra>'
            ))

            # Barra de Meta (color fijo azul claro)
            fig.add_trace(go.Bar(
                name='Presupuesto',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['ValorMeta'],
                marker_color='#90D5FF',
                text=[f"${v:,.0f}" for v in df_metricas['ValorMeta']],
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='$%{y:,.2f}<extra></extra>'
            ))

            fig.update_layout(
                barmode='group',
                xaxis_title='Vendedor',
                yaxis_title='Monto (USD) 💰',
                height=500,
                xaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16)
                ),
                yaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16),
                    range=[0, df_metricas[['Total_venta_rango', 'ValorMeta']].max().max() * 1.15]
                ),
                legend=dict(
                    font=dict(size=14),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            # Gráfico de barras PORCENTAJES
            st.markdown("---")
            st.subheader(f"📊 Cumplimiento (%) - {vendedores_seleccionados}")

            # Calcular porcentajes
            df_metricas['PorcentajeVenta'] = (df_metricas['Total_venta_rango'] / df_metricas['ValorMeta']) * 100
            df_metricas['PorcentajeMeta'] = 100

            # Asignar color dinámico según el rendimiento
            colores_porcentaje = []
            for p in df_metricas['PorcentajeVenta']:
                if p >= 100:
                    colores_porcentaje.append('#A7DCA5')  # Verde
                elif p >= 70:
                    colores_porcentaje.append('#A7DCA5')  # Naranja
                else:
                    colores_porcentaje.append('#A7DCA5')  # Rojo

            fig2 = go.Figure()

            # Barra de Ventas Reales en porcentaje
            fig2.add_trace(go.Bar(
                name='Venta Real (%)',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['PorcentajeVenta'],
                marker_color=colores_porcentaje,
                text=[f"{v:.1f}%" for v in df_metricas['PorcentajeVenta']],
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='%{y:.1f}%<extra></extra>'
            ))

            # Barra de Meta (100%)
            fig2.add_trace(go.Bar(
                name='Presupuesto (100%)',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['PorcentajeMeta'],
                marker_color='#90D5FF',
                text=["100%"] * len(df_metricas),
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='%{y:.0f}%<extra></extra>'
            ))

            fig2.update_layout(
                barmode='group',
                xaxis_title='Vendedor',
                yaxis_title='Cumplimiento (%)',
                height=500,
                xaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16)
                ),
                yaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16),
                    range=[0, max(110, df_metricas['PorcentajeVenta'].max() * 1.15)]
                ),
                legend=dict(
                    font=dict(size=14),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )

            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.info("ℹ️ No se encontraron datos para el rango de fechas seleccionado")


    ###############################################################################################
    ###-------------------COORDINADOR INTELIGENCIA COMERCIAL------------------------------------###
    ###############################################################################################
    """
    ###############################################################################################
    """
    def mostrar_metricas_rendimiento_porcentajes(self, vendedores_seleccionados, fecha_inicio, fecha_fin):
        # Obtener métricas
        df_metricas = self.modelo_rendimiento.obtener_metricas_rendimiento(
            vendedores_seleccionados, 
            fecha_inicio, 
            fecha_fin
        )
        
        if df_metricas is not None and not df_metricas.empty:
            # st.subheader("📈 Detalle de Rendimiento")

            # Copiar y renombrar columnas para mostrar
            df_display = df_metricas.copy()
            df_display = df_display.rename(columns={
                'NombreVendedor': 'Nombre Vendedor',
                'Total_Venta_Mensual': 'Total Venta del Mes (USD)',
                'ValorMeta': 'Valor Presupuesto del Mes (USD)',
                'Diferencia': 'Diferencia (USD)',
                'Rendimiento': 'Rendimiento'
            })
            
            # Calcular porcentajes
            df_metricas['PorcentajeVenta'] = (df_metricas['Total_Venta_Mensual'] / df_metricas['ValorMeta']) * 100
            df_metricas['PorcentajeMeta'] = 100  # Meta fija al 100%

            # Asignar color dinámico según el rendimiento
            colores = []
            for p in df_metricas['PorcentajeVenta']:
                if p >= 100:
                    colores.append('#A7DCA5')  # Verde
                elif p >= 70:
                    colores.append('#A7DCA5')  # Naranja
                else:
                    colores.append('#A7DCA5')  # Rojo

            st.markdown("---")
            st.subheader(f"📊 Ventas vs Presupuesto % - {vendedores_seleccionados}")

            import plotly.graph_objects as go

            fig = go.Figure()

            # Barra de Ventas Reales
            fig.add_trace(go.Bar(
                name='Venta Real (%)',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['PorcentajeVenta'],
                marker_color=colores,
                text=[f"{v:.1f}%" for v in df_metricas['PorcentajeVenta']],
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='%{y:.1f}%<extra></extra>'  # Solo porcentaje
            ))

            # Barra de Meta (100%)
            fig.add_trace(go.Bar(
                name='Presupuesto (100%)',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['PorcentajeMeta'],
                marker_color='#90D5FF',
                text=["100%"] * len(df_metricas),
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='%{y:.0f}%<extra></extra>'  # Solo porcentaje
            ))

            # Ajustar diseño
            fig.update_layout(
                barmode='group',
                xaxis_title='Vendedor',
                yaxis_title='Cumplimiento (%)',
                height=500,
                xaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16)
                ),
                yaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16),
                    range=[0, max(110, df_metricas['PorcentajeVenta'].max() * 1.15)]
                ),
                legend=dict(
                    font=dict(size=14),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("ℹ️ No se encontraron datos para los filtros seleccionados")


    """
    ###############################################################################################
    """
    def mostrar_metricas_rendimiento_rangos_porcentajes(self, vendedores_seleccionados, fecha_inicio, fecha_fin):
        # Obtener métricas
        df_metricas = self.modelo_rendimiento.obtener_metricas_rendimiento_rango(
            vendedores_seleccionados, 
            fecha_inicio, 
            fecha_fin
        )
        
        if df_metricas is not None and not df_metricas.empty:
            # st.subheader("📈 Detalle de Rendimiento")

            # Copiar y renombrar columnas para mostrar
            df_display = df_metricas.copy()
            df_display = df_display.rename(columns={
                'NombreVendedor': 'Nombre Vendedor',
                'Total_venta_rango': 'Total Venta (USD)',
                'ValorMeta': 'Valor Meta (USD)',
                'Diferencia': 'Diferencia (USD)',
                'Rendimiento': 'Rendimiento'
            })
            
            # Calcular porcentajes
            df_metricas['PorcentajeVenta'] = (df_metricas['Total_venta_rango'] / df_metricas['ValorMeta']) * 100
            df_metricas['PorcentajeMeta'] = 100  # Meta fija al 100%

            # Asignar color dinámico según el rendimiento
            colores = []
            for p in df_metricas['PorcentajeVenta']:
                if p >= 100:
                    colores.append('#A7DCA5')  # Verde
                elif p >= 70:
                    colores.append('#A7DCA5')  # Naranja
                else:
                    colores.append('#A7DCA5')  # Rojo

            st.markdown("---")
            st.subheader(f"📊 Ventas vs Presupuesto % - {vendedores_seleccionados}")

            import plotly.graph_objects as go

            fig = go.Figure()

            # Barra de Ventas Reales
            fig.add_trace(go.Bar(
                name='Venta Real (%)',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['PorcentajeVenta'],
                marker_color=colores,
                text=[f"{v:.1f}%" for v in df_metricas['PorcentajeVenta']],
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='%{y:.1f}%<extra></extra>'  # Solo porcentaje
            ))

            # Barra de Meta (100%)
            fig.add_trace(go.Bar(
                name='Presupuesto (100%)',
                x=df_metricas['NombreVendedor'],
                y=df_metricas['PorcentajeMeta'],
                marker_color='#90D5FF',
                text=["100%"] * len(df_metricas),
                textposition='outside',
                textfont=dict(size=16, color='black'),
                hovertemplate='%{y:.0f}%<extra></extra>'  # Solo porcentaje
            ))

            # Ajustar diseño
            fig.update_layout(
                barmode='group',
                xaxis_title='Vendedor',
                yaxis_title='Cumplimiento (%)',
                height=500,
                xaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16)
                ),
                yaxis=dict(
                    title_font=dict(size=20),
                    tickfont=dict(size=16),
                    range=[0, max(110, df_metricas['PorcentajeVenta'].max() * 1.15)]
                ),
                legend=dict(
                    font=dict(size=14),
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='center',
                    x=0.5
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("ℹ️ No se encontraron datos para los filtros seleccionados")

