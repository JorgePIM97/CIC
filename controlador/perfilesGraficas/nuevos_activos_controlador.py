# controlador/perfilesGraficas/nuevos_activos_controlador.py - MODIFICADO PARA MULTISELECT
"""
Controlador para clientes nuevos y activos con multiselect
"""
import streamlit as st
from datetime import datetime
from controlador.base_controlador import BaseControlador
from modelo.perfiles_modelo import PerfilesModelo
from vista.perfiles_vista import PerfilesVista

class NuevosActivosControlador(BaseControlador):
    """Controlador para el análisis de status de clientes con multiselect"""
    
    def __init__(self):
        super().__init__()
        self.modelo = PerfilesModelo()
        self.vista = PerfilesVista()
    
    def ejecutar_vista_perfiles(self):
        """Ejecuta el análisis de clientes nuevos y activos con vendedores seleccionados"""
        try:
            # Seleccionar vendedores (multiselect)
            vendedores_seleccionados = self.vista.mostrar_sidebar_perfiles()
            
            # Mostrar título
            self.vista.mostrar_titulo(f"📊 Clientes Nuevos y Activos del Año {datetime.now().year}")
            
            # Validar que hay vendedores seleccionados
            if not vendedores_seleccionados or len(vendedores_seleccionados) == 0:
                st.warning("⚠️ **No hay vendedores seleccionados**")
                st.info("👆 Por favor, selecciona al menos un vendedor en la barra lateral para ver los datos.")
                return
            
            # Obtener datos según los vendedores seleccionados
            with st.spinner(f"📊 Cargando datos de {len(vendedores_seleccionados)} vendedor(es)..."):
                df_status = self.modelo.obtener_nuevos_activos_vendedores_seleccionados(vendedores_seleccionados)
            
            # Verificar si hay datos
            if df_status is not None and not df_status.empty:
                # Verificar si realmente hay clientes (no solo estructura vacía)
                total_clientes = df_status['Total'].sum()
                
                if total_clientes > 0:
                    # Mostrar el dashboard completo
                    self.vista.mostrar_dashboard_nuevos_activos(df_status, vendedores_seleccionados)
                else:
                    st.info("📭 **No se encontraron clientes**")
                    if len(vendedores_seleccionados) == 1:
                        st.write(f"El vendedor **{vendedores_seleccionados[0]}** no tiene clientes registrados este año.")
                    else:
                        st.write(f"Los **{len(vendedores_seleccionados)}** vendedores seleccionados no tienen clientes registrados este año.")
                    
                    # Sugerencia de acción
                    st.markdown("#### 💡 Sugerencias:")
                    st.write("- Verifica que los vendedores tengan ventas completadas este año")
                    st.write("- Revisa que las oportunidades estén marcadas como '7. Vendido'")
                    st.write("- Confirma que los clientes estén asociados correctamente a los vendedores")
            else:
                st.error("❌ **Error al obtener los datos**")
                st.write("No se pudieron cargar los datos de clientes. Verifica la conexión a la base de datos.")
        
        except Exception as e:
            self.manejar_error(f"Error en análisis de clientes nuevos y activos: {str(e)}")