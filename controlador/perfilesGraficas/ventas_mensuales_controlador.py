# controlador/ventas_mensuales_controlador.py - MODIFICADO
"""
Controlador para ventas mensuales
"""
import streamlit as st
from datetime import datetime, date, timedelta
from controlador.base_controlador import BaseControlador
from modelo.perfiles_modelo import PerfilesModelo
from vista.perfiles_vista import PerfilesVista
from modelo.vendedores_registrados import VendedoresRegistrados
from vista.seleccion_usuarios.seleccion import SeleccionUsuarios

class VentasMensualesControlador(BaseControlador):
    """Controlador para el análisis de ventas mensuales"""
    
    def __init__(self):
        super().__init__()
        self.modelo = PerfilesModelo()
        self.vista = PerfilesVista()
        self.vendedores = VendedoresRegistrados()
        self.seleccion_usuarios = SeleccionUsuarios()

    
    def ejecutar_vista_perfiles(self):
        """Ejecuta el análisis de ventas mensuales"""
        try:
            # Obtener datos para los filtros
            vendedores = self.seleccion_usuarios.seleccion_privilegios_zona()
            
            if not vendedores:
                self.vista.mostrar_error("No se pudieron cargar los vendedores.")
                return
            
            # Obtener rango de fechas disponibles
            fecha_min, fecha_max = self.modelo.obtener_rango_fechas_disponibles()
            
            # Mostrar filtros en el sidebar
            vendedor_seleccionado, usar_rango, años_seleccionados, fecha_inicio, fecha_fin = self._mostrar_filtros_sidebar(
                vendedores, fecha_min, fecha_max
            )
            
            # Validar selección
            if usar_rango:
                if fecha_inicio > fecha_fin:
                    self.vista.mostrar_error("La fecha de inicio debe ser menor o igual a la fecha de fin.")
                    return
                self._mostrar_vista_ventas_rango(vendedor_seleccionado, fecha_inicio, fecha_fin)
            else:
                if not años_seleccionados:
                    self.vista.mostrar_warning("Por favor selecciona al menos un año para mostrar los datos.")
                    return
                self._mostrar_vista_ventasMensuales(vendedor_seleccionado, años_seleccionados)
            
        except Exception as e:
            self.manejar_error(e)
    
    def _mostrar_filtros_sidebar(self, vendedores, fecha_min, fecha_max):
        """Muestra los filtros en el sidebar"""
        #st.sidebar.markdown("### 👤 Selección de Vendedor")
        
        st.sidebar.header("Vendedor")
        # Filtro de vendedor
        vendedor_seleccionado = st.sidebar.selectbox(
            "Seleccione vendedor:",
            vendedores,
            index=0,
            key="perfiles_vendedor"
        )
        
        st.sidebar.markdown("### Tipo de Filtro")
        
        # Selector de tipo de filtro
        usar_rango = st.sidebar.radio(
            "Selecciona el tipo de filtro:",
            ["Por Años", "Por Rango de Fechas"],
            key="tipo_filtro"
        ) == "Por Rango de Fechas"
        
        años_seleccionados = []
        fecha_inicio = fecha_min
        fecha_fin = fecha_max
        
        if usar_rango:
            st.sidebar.markdown("### 📆 Rango de Fechas")
            
            # Fecha mínima fija: 1 de enero de 2020
            fecha_min_fija = datetime(datetime.now().year, 1, 1)
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                # Filtros de fecha
                fecha_inicio = st.date_input(
                    "Fecha de inicio:",
                    value=fecha_min_fija,
                    min_value=fecha_min_fija,
                    max_value=fecha_max,
                    key="fecha_inicio"
                )
            
            with col2:
                fecha_fin = st.date_input(
                    "Fecha de fin:",
                    value=fecha_max,
                    min_value=fecha_min_fija,
                    max_value=fecha_max,
                    key="fecha_fin"
                )
        
        else:
            st.sidebar.markdown("### 📅 Selección de Años")
            años_disponibles = self.modelo.obtener_años_disponibles()
            
            if not años_disponibles:
                self.vista.mostrar_error("No se pudieron cargar los años disponibles.")
                return vendedor_seleccionado, usar_rango, [], fecha_inicio, fecha_fin
            
            # Filtro de años
            años_seleccionados = st.sidebar.multiselect(
                "Años a comparar:",
                años_disponibles,
                default=años_disponibles[:2] if len(años_disponibles) >= 2 else años_disponibles,
                key="perfiles_años"
            )
        
        # # Botón para actualizar
        # if st.sidebar.button("🔄 Actualizar Datos", key="perfiles_actualizar"):
        #     st.cache_data.clear()
        
        return vendedor_seleccionado, usar_rango, años_seleccionados, fecha_inicio, fecha_fin
    
    def _mostrar_vista_ventas_rango(self, vendedor_seleccionado, fecha_inicio, fecha_fin):
        """Muestra la vista principal con datos de rango de fechas - Solo Ventas"""
        # Mostrar título
        self.vista.mostrar_titulo("📊 Estimacion de Ventas Mensuales")
        
        # Mostrar información seleccionada
        #self.vista.mostrar_info_seleccion_rango(vendedor_seleccionado, fecha_inicio, fecha_fin)
        
        # Obtener datos de ventas directamente (sin tabs)
        with st.spinner("Cargando datos de ventas..."):
            df_ventas = self.modelo.obtener_ventas_mensuales_por_rango(
                vendedor_seleccionado, fecha_inicio, fecha_fin
            )
        
        if df_ventas.empty:
            self.vista.mostrar_warning(
                f"No se encontraron ventas para {vendedor_seleccionado} en el período seleccionado."
            )
        else:
            # Mostrar gráfica de ventas
            self.vista.mostrar_grafica_ventas_rango(
                df_ventas, vendedor_seleccionado, fecha_inicio, fecha_fin
            )
            
            # Mostrar resumen estadístico
            self.vista.mostrar_resumen_estadistico_rango(df_ventas, fecha_inicio, fecha_fin)
    
    def _mostrar_vista_ventasMensuales(self, vendedor_seleccionado, años_seleccionados):
        """Muestra la vista principal con los datos (método original)"""
        # Mostrar título
        self.vista.mostrar_titulo("📊 Estimación de Ventas Mensuales")
        
        # Mostrar información seleccionada
        #self.vista.mostrar_info_seleccion(vendedor_seleccionado, años_seleccionados)
        
        # Obtener datos
        with st.spinner("Cargando datos de ventas..."):
            df_ventas = self.modelo.obtener_ventas_mensuales(vendedor_seleccionado, años_seleccionados)
        
        if df_ventas.empty:
            self.vista.mostrar_warning(
                f"No se encontraron ventas para {vendedor_seleccionado} en los años seleccionados."
            )
            return
        
        # Mostrar gráfica
        self.vista.mostrar_grafica_ventas(df_ventas, vendedor_seleccionado, años_seleccionados)
        
        # Mostrar resumen estadístico
        self.vista.mostrar_resumen_estadistico(df_ventas, años_seleccionados)