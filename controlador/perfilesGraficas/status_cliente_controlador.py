# controlador/perfilesGraficas/status_cliente_controlador.py - MODIFICADO PARA MULTISELECT
"""
Controlador para status de clientes con multiselect
"""
import streamlit as st
from controlador.base_controlador import BaseControlador
from modelo.perfiles_modelo import PerfilesModelo
from vista.perfiles_vista import PerfilesVista

class StatusClienteControlador(BaseControlador):
    """Controlador para el análisis de status de clientes con multiselect"""
    
    def __init__(self):
        super().__init__()
        self.modelo = PerfilesModelo()
        self.vista = PerfilesVista()

    def ejecutar_vista_perfiles(self):
        """Ejecuta el análisis de status de clientes con vendedores seleccionados"""
        try:
            # Mostrar título
            self.vista.mostrar_titulo("📊 Status de Clientes")

            # Seleccionar vendedores (multiselect)
            vendedores_seleccionados = self.vista.mostrar_sidebar_perfiles()
            
            # Validar que hay vendedores seleccionados
            if not vendedores_seleccionados or len(vendedores_seleccionados) == 0:
                st.warning("⚠️ **No hay vendedores seleccionados**")
                st.info("👆 Por favor, selecciona al menos un vendedor en la barra lateral para ver los datos.")
                return
            
            # Obtener datos según los vendedores seleccionados
            with st.spinner(f"📊 Cargando datos de status de {len(vendedores_seleccionados)} vendedor(es)..."):
                df_status = self.modelo.obtener_status_cliente_vendedores_seleccionados(vendedores_seleccionados)
            
            # Verificar si hay datos
            if df_status is not None and not df_status.empty:
                # Verificar si realmente hay clientes (no solo estructura vacía)
                total_clientes = df_status['Cantidad'].sum() if 'Cantidad' in df_status.columns else 0
                
                if total_clientes > 0:
                    # Mostrar el dashboard completo
                    self.vista.mostrar_dashboard_status_clientes(df_status, vendedores_seleccionados)
                else:
                    st.info("📭 **No se encontraron clientes**")
                    if len(vendedores_seleccionados) == 1:
                        st.write(f"El vendedor **{vendedores_seleccionados[0]}** no tiene clientes registrados.")
                    else:
                        st.write(f"Los **{len(vendedores_seleccionados)}** vendedores seleccionados no tienen clientes registrados.")
                    
                    # Sugerencia de acción
                    st.markdown("#### 💡 Sugerencias:")
                    st.write("- Verifica que los vendedores tengan clientes asignados")
                    st.write("- Revisa que los clientes estén marcados correctamente como 'Cliente', 'Prospecto' o 'Antiguo cliente'")
                    st.write("- Confirma que los clientes no estén marcados como eliminados")
            else:
                st.error("❌ **Error al obtener los datos**")
                st.write("No se pudieron cargar los datos de status de clientes. Verifica la conexión a la base de datos.")
                
        except Exception as e:
            self.manejar_error(f"Error en análisis de status de clientes: {str(e)}")