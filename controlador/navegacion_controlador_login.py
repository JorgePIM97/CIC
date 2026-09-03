#controlador/navegacion_controlador_login.py
import streamlit as st
from controlador.cuadrantesGartner.vendedores_controlador import VendedoresControlador
from controlador.cuadrantesGartner.visitas_movilidad_controlador import VisitaMovilidadControlador
from controlador.cuadrantesGartner.visitas_general_movilidad_controlador import VisitaGeneralMovilidadControlador
from controlador.cuadrantesGartner.visitas_ventas_controlador import VisitaVentasControlador
from controlador.cuadrantesGartner.tareas_actividades_controlador import TareaActividadControlador
from controlador.cuadrantesGartner.actividades_movilidad_controlador import ActividadMovilidadControlador
from controlador.cuadrantesGartner.tiempos_visitas_controlador import TiemposVisitasControlador
from controlador.cuadrantesGartner.tiempos_visitas_promedio_controlador import TiemposPromedioVisitasControlador
from controlador.perfilesGraficas.ventas_mensuales_controlador import VentasMensualesControlador
from controlador.perfilesGraficas.status_cliente_controlador import StatusClienteControlador
from controlador.perfilesGraficas.nuevos_activos_controlador import NuevosActivosControlador
from vista.login.login_vista import LoginVista
from vista.componentes.botones import BotonesApp
from vista.componentes.logotipos import LogosApp
from controlador.reportes.exceles_controlador import ExcelesControlador
from controlador.ventasReales.clientes_ingresos_controlador import ClientesIngresosControlador
from controlador.ventasReales.clases_ingresos_controlador import ClasesIngresosControlador
from controlador.ventasReales.clases_cantidad_controlador import ClasesCantidadControlador
from controlador.ventasReales.categoria_ingresos_controlador import CategoriaIngresosControlador
from controlador.reportes.metas_controlador import MetasControlador
from controlador.rendimiento.rendimiento_controlador import RendimientoControlador
from controlador.reportes.kilometraje_controlador import KilometrajeControlador
from controlador.reportes.planeacion_controlador import PlaneacionControlador
from controlador.reportes.resumen_movilidad_controlador import ResumenMovilidadControlador
from controlador.cuadrantesGartner.ventas_gps_controlador import VentasGpsControlador
from controlador.admin.admin_controlador import AdminControlador
from controlador.admin.configuracion_controlador import ConfiguracionControlador
# from controlador.cuadrantesGartner.ventas_reales_gps_controlador import VentasRealesGpsControlador
from vista.componentes.sidebar_ventas_real import SideBarVentaReal
from modelo.ventas_reales_modelo import VentasRealesModelo
from vista.componentes.botones import BotonesApp
from modelo.exceles_modelo import ExcelesModelo
from controlador.reportes.presupuesto_controlador import PresupuestoControlador
from modelo.cobertura_cartera_modelo import CoberturaCarteraModelo
import pandas as pd


class NavegacionControladorLogin:
    def __init__(self):
        self.botonVendedor = BotonesApp()
        self.logotipos = LogosApp()
        self.reportes_excel = ExcelesControlador()
        self.reportes_metas = MetasControlador()
        self.rendimiento = RendimientoControlador()
        self.kilometraje = KilometrajeControlador()
        self.planeacion = PlaneacionControlador()
        self.resumen_movilidad = ResumenMovilidadControlador()
        self.venta_real = SideBarVentaReal()
        self.modelo = VentasRealesModelo()
        self.presupuesto = PresupuestoControlador()
        self.admin = AdminControlador()
        self.config = ConfiguracionControlador()

        self.controlador_clases = ClasesIngresosControlador()
        self.botones = BotonesApp()
        self.exceles_modelo = ExcelesModelo()


        self.comportamientos_dic = {
            "Ventas vs GPS": VentasGpsControlador(),
            "Ventas vs Movilidad": VendedoresControlador(),
            "Visitas vs Ventas": VisitaVentasControlador(),
            "Visitas Generales vs Movilidad": VisitaGeneralMovilidadControlador(),
            "Visitas vs Movilidad": VisitaMovilidadControlador(),
            "Tareas vs Actividades": TareaActividadControlador(),
            "Actividades vs Movilidad": ActividadMovilidadControlador(),
            "Tiempos vs Visitas": TiemposVisitasControlador(),
            "Tiempos Promedio vs Visitas": TiemposPromedioVisitasControlador(),
        }

        self.estimaciones_dic = {
            "Ventas Mensuales": VentasMensualesControlador(),
            "Status Clientes": StatusClienteControlador(),
            "Clientes Nuevos y Activos": NuevosActivosControlador(),
        }

        self.ventas_dic = {
            "Ventas por Proyecto": CategoriaIngresosControlador(),
            "Ventas por Cliente": ClientesIngresosControlador(),
            "Ventas por Clases": ClasesIngresosControlador(),
            "Cantidad Clases Vendida": ClasesCantidadControlador(),
        }
        
        # Inicializar la vista de login
        self.login_vista = LoginVista()
        
        # Estados para controlar la navegación
        if 'mostrar_comportamientos' not in st.session_state:
            st.session_state.mostrar_comportamientos = False
        
        if 'mostrar_perfiles' not in st.session_state:
            st.session_state.mostrar_perfiles = False

        if 'mostrar_exceles' not in st.session_state:
            st.session_state.mostrar_exceles = False
        
        if 'mostrar_metas' not in st.session_state:
            st.session_state.mostrar_metas = False

        if 'mostrar_presupuesto' not in st.session_state:
            st.session_state.mostrar_presupuesto = False

        if 'mostrar_admin' not in st.session_state:
            st.session_state.mostrar_admin = False

        if 'mostrar_config' not in st.session_state:
            st.session_state.mostrar_config = False

        if 'mostrar_rendimiento' not in st.session_state:
            st.session_state.mostrar_rendimiento = False

        if 'mostrar_kilometraje' not in st.session_state:
            st.session_state.mostrar_kilometraje = False

        if 'mostrar_planeacion' not in st.session_state:
            st.session_state.mostrar_planeacion = False

        if 'mostrar_resumen_movilidad' not in st.session_state:
            st.session_state.mostrar_resumen_movilidad = False

        if 'mostrar_ventas_reales' not in st.session_state:
            st.session_state.mostrar_ventas_reales = False

        if 'pagina_seleccionada' not in st.session_state:
            st.session_state.pagina_seleccionada = "Ventas vs GPS"
        
        if 'perfil_seleccionado' not in st.session_state:
            st.session_state.perfil_seleccionado = "Ventas Mensuales"

        if 'venta_seleccionada' not in st.session_state:
            st.session_state.venta_seleccionada = "Ventas por Proyecto"

    def ejecutar_barra_principal(self):
        """Controla la navegación entre páginas"""
        # Ocultar botón de descarga CSV en todos los dataframes
        st.markdown("""
            <style>
            button[data-testid="stElementToolbarButton"][title="Download as CSV"] {
                display: none;
            }
            </style>
        """, unsafe_allow_html=True)
        self.logotipos.logotipo_principal()
        st.sidebar.title("Centro Inteligencia Comercial")
        st.sidebar.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

        # Verificar si el usuario está autenticado
        if not st.session_state.get('usuario_autenticado', False):
            # Si no está autenticado, mostrar solo la pantalla de login
            self._mostrar_pantalla_login()
            return

        # Si está autenticado, mostrar información del usuario
        self.login_vista.mostrar_info_usuario()
        # self._mostrar_pantalla_inicio_autenticado()

        # Mostrar botones según permisos del usuario
        self._mostrar_botones_navegacion()


        # Lógica de visualización según el estado
        if st.session_state.mostrar_comportamientos:
            self._mostrar_cuadrantes()
        elif st.session_state.mostrar_ventas_reales:
            self._mostrar_ventas_reales()
        elif st.session_state.mostrar_perfiles:
            self._mostrar_perfiles()
        elif st.session_state.mostrar_exceles:
            self._mostrar_exceles()
        elif st.session_state.mostrar_metas:
            self._mostrar_metas()
        elif st.session_state.mostrar_presupuesto:
            self._mostrar_presupuesto()
        elif st.session_state.mostrar_admin:
            self._mostrar_admin()
        elif st.session_state.mostrar_config:
            self._mostrar_config()
        elif st.session_state.mostrar_rendimiento:
            self._mostrar_rendimiento()
        elif st.session_state.mostrar_kilometraje:
            self._mostrar_kilometraje()
        elif st.session_state.mostrar_planeacion:
            self._mostrar_planeacion()
        elif st.session_state.mostrar_resumen_movilidad:
            self._mostrar_resumen_movilidad()
        else:
            self._mostrar_pantalla_inicio_autenticado()

    # Reemplaza el método actual (retorna None, nunca funciona)
    def _mostrar_boton_configuracion_perfil(self):
        st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
        return st.sidebar.button("⚙️ Configuración Perfil", use_container_width=True)
    
    def  _mostrar_botones_navegacion(self):
        """Muestra los botones de navegación según los permisos del usuario"""
        permisos = st.session_state.get('permisos_usuario', {})
        
        # Botón "Comportamiento Vendedores" - Solo si tiene permisos
        if permisos.get('comportamiento_vendedores', False):
            if self.botonVendedor.boton_vendedor(
                "Comportamiento Vendedores",
                "primary" if st.session_state.mostrar_comportamientos else "primary",
                True
            ):    
                st.session_state.mostrar_comportamientos = not st.session_state.mostrar_comportamientos
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_comportamientos:
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_metas = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None

        # # Botón "Admin" - Solo si tiene permisos
        # if permisos.get('admin', False):
        #     if self.botonVendedor.boton_vendedor(
        #         "Administrar Vendedores",
        #         "primary" if st.session_state.mostrar_exceles else "primary", 
        #         True
        #     ):
        #         st.session_state.mostrar_admin = not st.session_state.mostrar_admin
        #         # Desactivar el otro modo si se activa este
        #         if st.session_state.mostrar_admin:
        #             st.session_state.mostrar_comportamientos = False
        #             st.session_state.mostrar_perfiles = False
        #             st.session_state.mostrar_ventas_reales = False
        #             st.session_state.mostrar_exceles = False
        #             st.session_state.mostrar_rendimiento = False
        #             st.session_state.mostrar_kilometraje = False
        #             st.session_state.mostrar_planeacion = False
        #             st.session_state.mostrar_resumen_movilidad = False
        #             st.session_state.mostrar_presupuesto = False
        #             st.session_state.mostrar_metas = False
        # else:
        #     None

        # # Botón "Configuración Perfil" — disponible para TODOS los usuarios autenticados
        # st.sidebar.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        # st.sidebar.markdown("---")
        # if st.sidebar.button("⚙️ Configuración Perfil", use_container_width=True):
        #     # Desactivar todos los demás módulos
        #     st.session_state.mostrar_comportamientos = False
        #     st.session_state.mostrar_perfiles = False
        #     st.session_state.mostrar_exceles = False
        #     st.session_state.mostrar_ventas_reales = False
        #     st.session_state.mostrar_metas = False
        #     st.session_state.mostrar_rendimiento = False
        #     st.session_state.mostrar_kilometraje = False
        #     st.session_state.mostrar_planeacion = False
        #     st.session_state.mostrar_resumen_movilidad = False
        #     st.session_state.mostrar_presupuesto = False
        #     st.session_state.mostrar_admin = False
        #     st.session_state.mostrar_config = True
        #     st.rerun()

        # Boton Ventas Reales
        if permisos.get('ventas_reales', False):
            if self.botonVendedor.boton_vendedor(
                "Ventas",
                "primary" if st.session_state.mostrar_ventas_reales else "primary",
                True
            ):    
                st.session_state.mostrar_ventas_reales = not st.session_state.mostrar_ventas_reales
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_ventas_reales:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_metas = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None

        # Botón "Vendedores" - Solo si tiene permisos
        if permisos.get('vendedores', False):
            if self.botonVendedor.boton_vendedor(
                "Ventas Estimadas",
                "primary" if st.session_state.mostrar_perfiles else "primary", 
                True
            ):
                st.session_state.mostrar_perfiles = not st.session_state.mostrar_perfiles
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_perfiles:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_metas = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None

        # Botón "Excel" - Solo si tiene permisos
        if permisos.get('exceles', False):
            if self.botonVendedor.boton_vendedor(
                "Cargar Ultimo Mes",
                "primary" if st.session_state.mostrar_exceles else "primary", 
                True
            ):
                st.session_state.mostrar_exceles = not st.session_state.mostrar_exceles
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_exceles:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_metas = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None

        # Botón "Metas" - Solo si tiene permisos
        if permisos.get('metas', False):
            if self.botonVendedor.boton_vendedor(
                "Cargar Presupuestos",
                "primary" if st.session_state.mostrar_exceles else "primary", 
                True
            ):
                st.session_state.mostrar_metas = not st.session_state.mostrar_metas
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_metas:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None

        # Botón "Presupuesto" - Solo si tiene permisos
        if permisos.get('presupuesto', False):
            if self.botonVendedor.boton_vendedor(
                "Presupuesto Segmentos",
                "primary" if st.session_state.mostrar_presupuesto else "primary", 
                True
            ):
                st.session_state.mostrar_presupuesto = not st.session_state.mostrar_presupuesto
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_presupuesto:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_metas = False
        else:
            None

        # Botón "Rendimiento" - Solo si tiene permisos
        if permisos.get('rendimiento', False):
            if self.botonVendedor.boton_vendedor(
                "Rendimiento de Vendedores",
                "primary" if st.session_state.mostrar_rendimiento else "primary", 
                True
            ):
                st.session_state.mostrar_rendimiento = not st.session_state.mostrar_rendimiento
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_rendimiento:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_metas = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None

        # Botón "Kilometraje" - Solo si tiene permisos
        if permisos.get('kilometraje', False):
            if self.botonVendedor.boton_vendedor(
                "Registrar Kilometraje",
                "primary" if st.session_state.mostrar_kilometraje else "primary", 
                True
            ):
                st.session_state.mostrar_kilometraje = not st.session_state.mostrar_kilometraje
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_kilometraje:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_metas = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None

        # Botón "planeacion" - Solo si tiene permisos
        if permisos.get('planeacion', False):
            if self.botonVendedor.boton_vendedor(
                "Monitoreo de Planeacion",
                "primary" if st.session_state.mostrar_planeacion else "primary", 
                True
            ):
                st.session_state.mostrar_planeacion = not st.session_state.mostrar_planeacion
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_planeacion:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_metas = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_resumen_movilidad = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None

        # Botón "resumen movilidad" - Solo si tiene permisos
        if permisos.get('resumen_movilidad', False):
            if self.botonVendedor.boton_vendedor(
                "Resumen Mensual de Movilidad",
                "primary" if st.session_state.mostrar_resumen_movilidad else "primary", 
                True
            ):
                st.session_state.mostrar_resumen_movilidad = not st.session_state.mostrar_resumen_movilidad
                # Desactivar el otro modo si se activa este
                if st.session_state.mostrar_resumen_movilidad:
                    st.session_state.mostrar_comportamientos = False
                    st.session_state.mostrar_perfiles = False
                    st.session_state.mostrar_ventas_reales = False
                    st.session_state.mostrar_exceles = False
                    st.session_state.mostrar_metas = False
                    st.session_state.mostrar_rendimiento = False
                    st.session_state.mostrar_kilometraje = False
                    st.session_state.mostrar_planeacion = False
                    st.session_state.mostrar_presupuesto = False
        else:
            None


    def _mostrar_cuadrantes(self):
        """Muestra los controladores de comportamiento de vendedores"""
        if not st.session_state.get('permisos_usuario', {}).get('comportamiento_vendedores', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
            
        st.sidebar.subheader("📊 Tipo de Análisis")     
        pagina = st.sidebar.selectbox(
            "Seleccione tipo de análisis:",
            list(self.comportamientos_dic.keys()),
            key="pagina_selectbox"
        )
        st.session_state.pagina_seleccionada = pagina
        self.comportamientos_dic[st.session_state.pagina_seleccionada].ejecutar_vista_cuadrante()

    def _mostrar_perfiles(self):
        """Muestra los controladores de perfiles"""
        if not st.session_state.get('permisos_usuario', {}).get('vendedores', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        st.sidebar.subheader("Tipo de Análisis")    
        perfil = st.sidebar.selectbox(
            "Seleccione tipo de análisis:",
            list(self.estimaciones_dic.keys()),
            key="perfil_selectbox"
        )
        st.session_state.perfil_seleccionado = perfil
        self.estimaciones_dic[st.session_state.perfil_seleccionado].ejecutar_vista_perfiles()

    def _mostrar_exceles(self):
        """Muestra los controladores de exceles"""
        if not st.session_state.get('permisos_usuario', {}).get('exceles', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.reportes_excel.ejecutar_vista_exceles()

    def _mostrar_metas(self):
        """Muestra los controladores de metas"""
        if not st.session_state.get('permisos_usuario', {}).get('metas', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.reportes_metas.ejecutar_vista_metas()

    def _mostrar_presupuesto(self):
        """Muestra los controladores de presupuesto"""
        if not st.session_state.get('permisos_usuario', {}).get('presupuesto', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.presupuesto.ejecutar_vista_presupuesto()

    def _mostrar_admin(self):
        """Muestra los controladores de admin"""
        if not st.session_state.get('permisos_usuario', {}).get('admin', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.admin.ejecutar_vista_admin()

    def _mostrar_config(self):
        """Muestra los controladores de config"""
        if not st.session_state.get('permisos_usuario', {}).get('config', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.config.ejecutar_vista_configuracion()

    def _mostrar_kilometraje(self):
        """Muestra los controladores del registro del kilometraje"""
        if not st.session_state.get('permisos_usuario', {}).get('kilometraje', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.kilometraje.ejecutar_vista_kilometraje()
        
    def _mostrar_planeacion(self):
        """Muestra los controladores para el monitoreo de planeacion"""
        if not st.session_state.get('permisos_usuario', {}).get('planeacion', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.planeacion.ejecutar_vista_planeacion()

    def _mostrar_resumen_movilidad(self):
        """Muestra los controladores para resumen de movilidad"""
        if not st.session_state.get('permisos_usuario', {}).get('resumen_movilidad', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.resumen_movilidad.ejecutar_vista_resumen()

    def _mostrar_rendimiento(self):
        """Muestra los controladores de rendimiento"""
        if not st.session_state.get('permisos_usuario', {}).get('rendimiento', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        self.rendimiento.ejecutar_vista_rendimiento()

    def _mostrar_ventas_reales(self):
        """Muestra los controladores de las ventas reales"""
        if not st.session_state.get('permisos_usuario', {}).get('ventas_reales', False):
            st.error("❌ No tienes permisos para acceder a este módulo")
            return
        
        """SelectBox para seleccionar tipo de analisis de ventas reales
        """
        st.sidebar.subheader("Tipo de Análisis") 
        ventas = st.sidebar.selectbox(
            "Seleccione tipo de análisis:",
            list(self.ventas_dic.keys()),
            key="venta_selectbox"
        )
        st.session_state.venta_seleccionada = ventas
        self.ventas_dic[st.session_state.venta_seleccionada].ejecutar_vista_ventas()


    def _mostrar_pantalla_login(self):
        """Muestra la pantalla de login cuando no está autenticado"""
        st.title(" Centro de Inteligencia Comercial")
        st.markdown("---")
    
        # Mostrar el formulario de login
        self.login_vista.login_form()

    def _mostrar_pantalla_inicio_autenticado(self):
        """Muestra la pantalla de inicio cuando está autenticado pero no ha seleccionado ningún módulo"""
        # usuario_actual = st.session_state.get('usuario_actual', 'Usuario')
        usuario_cargo = st.session_state.get('cargo_actual', 'Cargo')
        usuario_zona = st.session_state.get('zona_actual', 'Zona')

        if usuario_cargo == 'CEO':
            self.descripcion_privilegios_completos("Ernesto")

        if usuario_cargo == 'ADMINISTRADOR':
            self.descripcion_admin()

        elif usuario_cargo == 'DIRECTOR DE PRODUCCION':
            self.descripcion_privilegios_completos("Omar")

        elif usuario_cargo == 'DIRECTOR COMERCIAL':
            self.descripcion_privilegios_completos("Silvino")
            
        elif usuario_cargo == 'ANALISTA AFTER SALES':
            self.descripcion_analista_aftersales("Miryam")
            
        elif usuario_cargo == 'COORDINADOR INTELIGENCIA COMERCIAL':
            self.descripcion_coordinador_inteligencia_comercial("Rafael")

        elif usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'LEON':
            self.descripcion_coordinador_ventas("León")

        elif usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'MONCLOVA':
            self.descripcion_coordinador_ventas("Monclova") 

        elif usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'GUADALAJARA':
            self.descripcion_coordinador_ventas("Guadalajara")

        elif usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'MONTERREY':
            self.descripcion_coordinador_ventas("Monterrey")

        elif usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'NORTE':
            self.descripcion_coordinador_ventas("Norte")

        elif usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'BAJIO':
            self.descripcion_coordinador_ventas("Bajio")

    def descripcion_admin(self):
        self._mostrar_admin()

    def _mostrar_configuracion(self):
        st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
        if st.button("⚙️ Configuración Perfil", use_container_width=True):
            st.session_state.mostrar_comportamientos = False
            st.session_state.mostrar_perfiles = False
            st.session_state.mostrar_exceles = False
            st.session_state.mostrar_ventas_reales = False
            st.session_state.mostrar_metas = False
            st.session_state.mostrar_rendimiento = False
            st.session_state.mostrar_kilometraje = False
            st.session_state.mostrar_planeacion = False
            st.session_state.mostrar_resumen_movilidad = False
            st.session_state.mostrar_presupuesto = False
            st.session_state.mostrar_admin = False
            st.session_state.mostrar_config = True
            st.rerun()

    def descripcion_coordinador_ventas(self, zona):
        st.title(f"Bienvenido a Zona de {zona}")
        st.markdown("---") 
        st.markdown("### 🎯 Selecciona un módulo para comenzar")
        st.markdown("---") 
        st.markdown("#### Acceso completo a todos los módulos")
        st.markdown("""
        - **Comportamiento Vendedores**: Módulo para analizar movimientos de los vendedores en un rango de fechas. 
        """)
        st.markdown("---") 
        st.markdown("""
        - **Ventas**: Gráficas para análizar ventas totales de cada mes por vendedor o general.
                    
        **Tipos de Análisis**   
        - **Ventas por Proyecto**: Categorias principales de las clases vendidas.   
        - **Ventas por Cliente**: Clientes que más compran.  
        - **Ventas por Clases**: Productos que más ingresos generan.  
        - **Cantidad de Clases Vendidas**: Productos que más se venden en cantidad.  
        """) 
        st.markdown("---") 
        st.markdown("""
        - **Rendimiento de vendedores**: Modulo para observar comparacion de porcentaje de Ventas vs Presupuesto de un vendedor en un rango de fechas.
        """) 

    # def descripcion_coordinador_inteligencia_comercial(self, nombre):
    #     st.title(f"Bienvenido {nombre}")
    #     st.markdown("---") 
    #     st.markdown("### 🎯 Selecciona un módulo para comenzar")
    #     st.markdown("---") 
    #     st.markdown("#### Modulos disponibles para visualización y registro de movilidad")
    #     st.markdown("---") 
    #     st.markdown("""
    #     - **Conmportamiento de Vendedores**:  Sirve para observar la movilidad, ventas y actividades que los vendedores registran en el Force Manager por medio de diagramas de Gartner. 
    #     """)
    #     st.markdown("""
    #     - **Rendimiento de Vendedores**:  Modulo para observar el porcentaje de Ventas vs Presupuesto de un vendedor en un rango de fechas. 
    #     """)
    #     st.markdown("""
    #     - **Registrar Kilometraje**:  Formulario para registrar el kilometraje diario marcado por el GPS del carro de un vendedor. 
    #     """)
    #     st.markdown("""
    #     - **Monitoreo de Planeación**:  Sirve para observar si los vendedores han registrado actividades en la utima semana, de esta manera determinar si han logrado conceguir targets. 
    #     """)
    #     # st.markdown("---") 
    #     st.markdown("""
    #     - **Resumen Mensual de Movilidad**: Formulario para registrar los resumenes mensuales mensuales de un vendedor en el CIC.
    #     """) 

    #     #Implementar filtros y tabla aqui

    def descripcion_coordinador_inteligencia_comercial(self, nombre):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(f"Bienvenida {nombre}")
        with col2:
            self._mostrar_configuracion()
        st.markdown("---")
        st.markdown("### 🎯 Selecciona un módulo para comenzar")
        st.markdown("---")
        st.markdown("#### Módulos disponibles para visualización y registro de movilidad")
        st.markdown("---")
        st.markdown("""
        - **Comportamiento de Vendedores**: Sirve para observar la movilidad, ventas y actividades
          que los vendedores registran en el Force Manager por medio de diagramas de Gartner.
        """)
        st.markdown("""
        - **Rendimiento de Vendedores**: Módulo para observar el porcentaje de Ventas vs Presupuesto
          de un vendedor en un rango de fechas.
        """)
        st.markdown("""
        - **Registrar Kilometraje**: Formulario para registrar el kilometraje diario marcado por el
          GPS del carro de un vendedor.
        """)
        st.markdown("""
        - **Monitoreo de Planeación**: Sirve para observar si los vendedores han registrado
          actividades en la última semana, de esta manera determinar si han logrado conseguir targets.
        """)
        st.markdown("""
        - **Resumen Mensual de Movilidad**: Formulario para registrar los resúmenes mensuales de un
          vendedor en el CIC.
        """)
 
        # ================================================================
        # KPI: COBERTURA DE CARTERA COMERCIAL
        # ================================================================
        st.markdown("---")
        st.markdown("## 📊 KPI: Cobertura de Cartera Comercial")
        st.markdown(
            "Mide qué porcentaje de la cartera activa de clientes ha sido visitada "
            "por cada representante de ventas en el periodo seleccionado."
        )
        st.markdown("---")
 
        # ── Obtener lista de vendedores disponibles para este cargo ──────
        # from modelo.vendedores_registrados import VendedoresRegistrados
        from modelo.cobertura_cartera_modelo import CoberturaCarteraModelo
        import pandas as pd
        from datetime import date
 
        # vendedores_disponibles = VendedoresRegistrados().obtener_vendedores_completos()
 
        vendedores_disponibles = [
            'JORGE MARTINEZ ALANIS', # Monterrey
            'ALFONSO GASCA OROZCO', # Guadalajara
            'ADAN GARZA MARTINEZ', # Monclova
            'CESAR VALDES ZUÑIGA', # Leon
            'Javier Ibarrola'
        
        ]

        # ── FILTROS ──────────────────────────────────────────────────────
        col1, col2, col3 = st.columns([2, 1, 1])
 
        with col1:
            vendedores_sel = st.multiselect(
                "Representantes de ventas:",
                options=vendedores_disponibles,
                default=vendedores_disponibles,
                key="kpi_cob_vendedores",
                help="Selecciona uno o más representantes de ventas",
            )
 
        with col2:
            fecha_inicio = st.date_input(
                "📅 Fecha inicio:",
                value=date(date.today().year, 1, 1),
                key="kpi_cob_fecha_inicio",
            )
 
        with col3:
            fecha_fin = st.date_input(
                "📅 Fecha fin:",
                value=date.today(),
                key="kpi_cob_fecha_fin",
            )
 
        # Desplegable para @DiasActividad
        PERIODOS_ACTIVIDAD = {
            "Mensual (30 días)":     30,
            "Trimestral (90 días)":  90,
            "Semestral (182 días)": 182,
            "Anual (365 días)":     365,
        }
 
        periodo_sel = st.selectbox(
            "⏱️ Ventana de actividad del cliente (define cartera activa):",
            options=list(PERIODOS_ACTIVIDAD.keys()),
            index=1,          # Trimestral como valor por defecto
            key="kpi_cob_periodo",
            help=(
                "Determina cuántos días hacia atrás desde la fecha fin se considera "
                "que un cliente está activo en la cartera."
            ),
        )
        dias_actividad = PERIODOS_ACTIVIDAD[periodo_sel]
 
        # ── BOTÓN DE CONSULTA ────────────────────────────────────────────
        ejecutar = st.button(
            "🔍 Consultar KPI",
            key="kpi_cob_ejecutar",
            type="primary",
            use_container_width=False,
        )
 
        # ── VALIDACIONES Y EJECUCIÓN ─────────────────────────────────────
        if ejecutar:
            if not vendedores_sel:
                st.warning("⚠️ Selecciona al menos un representante de ventas.")
                return
 
            if fecha_inicio > fecha_fin:
                st.error("❌ La fecha de inicio no puede ser mayor que la fecha fin.")
                return
 
            with st.spinner("Consultando base de datos..."):
                try:
                    modelo_kpi = CoberturaCarteraModelo()
                    df = modelo_kpi.obtener_cobertura(
                        fecha_inicio=str(fecha_inicio),
                        fecha_fin=str(fecha_fin),
                        dias_actividad=dias_actividad,
                        vendedores=vendedores_sel,
                    )
                except Exception as e:
                    st.error(f"❌ Error al consultar la base de datos: {e}")
                    return
 
            if df is None or df.empty:
                st.info("ℹ️ No se encontraron resultados para los filtros seleccionados.")
                return
 
            # ── MÉTRICAS RESUMEN ─────────────────────────────────────────
            st.markdown("### Resumen del periodo")
 
            total_visitados  = df["Clientes Visitados en el mes"].sum()
            total_activos    = df["Clientes activos"].max()   # ya es por vendedor; usa suma si son distintos
            cobertura_global = (
                df["Clientes Visitados en el mes"].sum()
                / df["Clientes activos"].sum()
                * 100
            ) if df["Clientes activos"].sum() > 0 else 0
 
            m1, m2, m3 = st.columns(3)
            m1.metric("Total visitas únicas acumuladas", f"{total_visitados:,}")
            m2.metric(
                "Cartera activa total",
                f"{df['Clientes activos'].sum():,}",
                help=f"Clientes con actividad en los últimos {dias_actividad} días",
            )
            m3.metric(
                "Cobertura global del periodo",
                f"{cobertura_global:.1f}%",
            )
 
            # ── TABLA DE RESULTADOS ──────────────────────────────────────
            st.markdown("### Detalle por representante y mes")
 
            # Formato visual para la columna de cobertura
            df_display = df.copy()
            df_display["Cobertura de cartera (%)"] = df_display["Cobertura de cartera (%)"].apply(
                lambda x: f"{x:.1f}%"
            )
 
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Cobertura de cartera (%)": st.column_config.TextColumn(
                        "Cobertura (%)",
                        help="% de clientes activos visitados en el mes",
                    ),
                    "Clientes Visitados en el mes": st.column_config.NumberColumn(
                        "Visitados",
                        format="%d",
                    ),
                    "Clientes activos": st.column_config.NumberColumn(
                        "Cartera activa",
                        format="%d",
                        help=f"Clientes con actividad en los últimos {dias_actividad} días",
                    ),
                },
            )
 
            # ── DESCARGA CSV ─────────────────────────────────────────────
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="⬇️ Descargar resultados (.csv)",
                data=csv,
                file_name=f"cobertura_cartera_{fecha_inicio}_{fecha_fin}.csv",
                mime="text/csv",
                key="kpi_cob_download",
            )

    def descripcion_analista_aftersales(self, nombre):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(f"Bienvenida {nombre}")
        with col2:
            self._mostrar_configuracion()

        # st.markdown("---") 
        st.markdown("### 🎯 Selecciona un módulo para comenzar")
        st.markdown("---") 

        st.markdown("#### Acceso a todos los modulos para analizar y registrar ventas")

        st.markdown("""
        - **Ventas**:  Modulo para analizar y obsevar ventas de un rango de fechas mediante graficas. 
        """)
        st.markdown("""
        - **Cargar Ultimo Mes**:  Modulo para cargar excel formato (.xlsx) de ventas mensual ya sea arrastrando o seleccionando archivo. 
        """)
        st.markdown("""
        - **Presupuesto Segmentos**:  Formulario para ingresar presupuestos de vendedores en sus respectivas fechas. 
        """)
        st.markdown("""
        - **Rendimiento de Vendedores**:  Modulo para observar comparacion de porcentaje de Ventas vs Presupuesto de un vendedor en un rango de fechas.
        """)
        st.markdown("---") 

        st.markdown("### 📊 Generar Reporte Mensual")
        

        vendedores_seleccionados, fecha_inicio, fecha_fin = self.venta_real.mostrar_filtros_ventas(self.modelo)
        df_clases = self.controlador_clases.obtener_datos_filtrados(vendedores_seleccionados, fecha_inicio, fecha_fin)
        año_seleccionado = fecha_inicio.year if fecha_inicio else None

        if not vendedores_seleccionados:
            st.info("Selecciona uno o varios vendedores.")
            return

        # ── Calcular mes_inicio y mes_fin ANTES del spinner ──────────────
        if fecha_inicio and fecha_fin:
            mes_inicio = fecha_inicio.month
            mes_fin = fecha_fin.month
        else:
            mes_inicio = 1
            mes_fin = 12

        año_anterior = (año_seleccionado - 1) if año_seleccionado else None

        with st.spinner("Cargando datos de categorías..."):
            # df_categorias = self.obtener_datos_filtrados(vendedores_seleccionados, fecha_inicio, fecha_fin)
            df_clases = self.controlador_clases.obtener_datos_filtrados(vendedores_seleccionados, fecha_inicio, fecha_fin)

            # Datos del año anterior
            if año_anterior:
                from datetime import date
                fecha_inicio_ant = date(año_anterior, fecha_inicio.month, fecha_inicio.day) if fecha_inicio else None
                fecha_fin_ant    = date(año_anterior, fecha_fin.month,   fecha_fin.day)     if fecha_fin   else None
                df_clases_anterior = self.controlador_clases.obtener_datos_filtrados(
                    vendedores_seleccionados, fecha_inicio_ant, fecha_fin_ant
                )
                df_metas_anterior = self.modelo.obtener_total_meta_vendedores(
                    vendedores_seleccionados, año_anterior, mes_inicio, mes_fin
                )
            else:
                df_clases_anterior = None
                df_metas_anterior = None
                
        df_metas = self.modelo.obtener_total_meta_vendedores(
                            vendedores_seleccionados, año_seleccionado, mes_inicio, mes_fin
                        )

        get_cargo = self.login_vista.get_cargo_de_sesion()
        if get_cargo == 'ANALISTA AFTER SALES':
            generar_reporte_btn = self.botones.boton_generar_reporte("Generar Reporte", type='primary', use_container_width=True)
            if generar_reporte_btn:
                if not fecha_inicio or not fecha_fin:
                    st.warning("Selecciona un período válido para generar el reporte")
                else:
                    # Obtener metas del año actual (si no las tienes aún fuera del spinner)
                    df_metas = self.modelo.obtener_total_meta_vendedores(
                        vendedores_seleccionados, año_seleccionado, mes_inicio, mes_fin
                    )
                    self.exceles_modelo.generar_pdf_reporte_boton(
                        vendedores_seleccionados, fecha_inicio, fecha_fin,
                        df_clases=df_clases,
                        df_metas=df_metas,
                        df_clases_anterior=df_clases_anterior,
                        df_metas_anterior=df_metas_anterior
                    )

    def descripcion_privilegios_completos(self, nombre):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title(f"Bienvenida {nombre}")
        with col2:
            self._mostrar_configuracion()
        st.markdown("---") 
        st.markdown("### 🎯 Selecciona un módulo para comenzar")
        st.markdown("---") 
        st.markdown("#### Acceso completo a módulos de venta y movilidad")
        st.markdown("""
        - **Comportamiento Vendedores**: Sirve para observar la movilidad, ventas y actividades que los vendedores registran en el Force Manager por medio de diagramas de Gartner. 
        """)
        st.markdown("---") 
        st.markdown("""
        - **Ventas**: Gráficas para análizar ventas totales de cada mes por vendedor o general.
                    
        **Tipos de Análisis**   
        - **Ventas por Proyecto**: Categorias principales de las clases vendidas.   
        - **Ventas por Cliente**: Clientes que más compran.  
        - **Ventas por Clases**: Productos que más ingresos generan.  
        - **Cantidad de Clases Vendidas**: Productos que más se venden en cantidad.  
        """) 

        st.markdown("---") 
        st.markdown("""
        - **Rendimiento de vendedores**: Modulo para observar comparacion de porcentaje de Ventas vs Presupuesto de un vendedor en un rango de fechas.
        """) 