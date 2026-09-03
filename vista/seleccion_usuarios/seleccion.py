# vista/seleccion_usuarios/seleccion.py
import streamlit as st
from ..login.login_vista import LoginVista
from modelo.vendedores_registrados import VendedoresRegistrados
from modelo.admin.admin_modelo import AdminModelo

class SeleccionUsuarios:
    def __init__(self):
        self.login_vista = LoginVista()
        self.vendedores = VendedoresRegistrados()
        self.admin = AdminModelo()

    def seleccion_privilegios_zona(self):

        # get_usuario = self.login_vista.get_usuario_de_sesion()
        get_cargo = self.login_vista.get_cargo_de_sesion()
        get_zona = self.login_vista.get_zona_de_sesion()

        if get_cargo == 'CEO':
            vendedores_default = self.vendedores.obtener_vendedores_completos()
        elif get_cargo == 'DIRECTOR DE PRODUCCION':
            vendedores_default = self.vendedores.obtener_vendedores_completos()
        elif get_cargo == 'DIRECTOR COMERCIAL':
            vendedores_default = self.vendedores.obtener_vendedores_completos()
        elif get_cargo == 'ANALISTA AFTER SALES':
            vendedores_default = self.vendedores.obtener_vendedores_completos()
        elif get_cargo == 'COORDINADOR INTELIGENCIA COMERCIAL':
            vendedores_default = self.vendedores.obtener_vendedores_completos()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'LEON':
            vendedores_default = self.vendedores.obtener_vendedores_leon()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'MONCLOVA':
            vendedores_default = self.vendedores.obtener_vendedores_monclova()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'GUADALAJARA':
            vendedores_default = self.vendedores.obtener_vendedores_guadalajara()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'MONTERREY':
            vendedores_default = self.vendedores.obtener_vendedores_monterrey()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'NORTE':
            vendedores_default = self.vendedores.obtener_vendedores_norte()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'BAJIO':
            vendedores_default = self.vendedores.obtener_vendedores_bajio()
        else:
            vendedores_default = []

        return vendedores_default
    

    def seleccion_privilegiosReal_zona(self):

        get_cargo = self.login_vista.get_cargo_de_sesion()
        get_zona = self.login_vista.get_zona_de_sesion()

        if get_cargo == 'CEO':
            vendedores_default = self.vendedores.obtener_vendedoresReales_completos()
        elif get_cargo == 'DIRECTOR DE PRODUCCION':
            vendedores_default = self.vendedores.obtener_vendedoresReales_completos()
        elif get_cargo == 'DIRECTOR COMERCIAL':
            vendedores_default = self.vendedores.obtener_vendedoresReales_completos()
        elif get_cargo == 'ANALISTA AFTER SALES':
            vendedores_default = self.vendedores.obtener_vendedoresReales_completos()
        elif get_cargo == 'COORDINADOR INTELIGENCIA COMERCIAL':
            vendedores_default = self.vendedores.obtener_vendedoresReales_completos()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'LEON':
            vendedores_default = self.vendedores.obtener_vendedoresReales_leon()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'MONCLOVA':
            vendedores_default = self.vendedores.obtener_vendedoresReales_monclova()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'MONTERREY':
            vendedores_default = self.vendedores.obtener_vendedoresReales_monterrey()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'GUADALAJARA':
            vendedores_default = self.vendedores.obtener_vendedoresReales_guadalajara()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'NORTE':
            vendedores_default = self.vendedores.obtener_vendedoresReales_norte()
        elif get_cargo == 'COORDINADOR DE VENTAS' and get_zona == 'BAJIO':
            vendedores_default = self.vendedores.obtener_vendedoresReales_bajio()
        else:
            None

        return vendedores_default
    
    def vendedores_selector(self):
        """
        Multiselect de vendedores con todos seleccionados por defecto
        """
        vendedores_default = self.obtener_vendedores_force()

        vendedores = st.sidebar.multiselect(
            "Seleccionar Vendedores:",
            vendedores_default,
            default=vendedores_default,
            key="vendedores_perfil_multiselect",
            help="Selecciona uno o más vendedores para analizar sus clientes"
        )

        return vendedores

    def vendedores_desplegable(self):
        """
        DEPRECATED: Usar vendedores_selector() en su lugar
        Mantenido para compatibilidad hacia atrás
        """
        return self.vendedores_selector()


    #Funcion para obtener lista de vendedores del excel json
    def obtener_vendedores_excel(self):
            """Obtiene la lista de vendedores completos de los exceles"""
            usuario_cargo = st.session_state.get('cargo_actual', 'Cargo')
            usuario_zona = st.session_state.get('zona_actual', 'Zona')

            guardados = self.admin.obtener_guardados()

            if usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'NORTE':
                exceles_list = guardados.get("vendedores_norte_exceles", [])

            elif usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'BAJIO':
                exceles_list = guardados.get("vendedores_bajio_exceles", [])

            else:
                exceles_list = guardados.get("vendedores_exceles", [])

            return exceles_list
    
    #Funcion para obtener lista de vendedores del force json
    def obtener_vendedores_force(self):
            """Obtiene la lista de vendedores completos del force"""
            usuario_cargo = st.session_state.get('cargo_actual', 'Cargo')
            usuario_zona = st.session_state.get('zona_actual', 'Zona')

            guardados = self.admin.obtener_guardados()

            if usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'NORTE':
                force_list = guardados.get("vendedores_norte_force", [])

            elif usuario_cargo == 'COORDINADOR DE VENTAS' and usuario_zona == 'BAJIO':
                force_list = guardados.get("vendedores_bajio_force", [])

            else:
                force_list = guardados.get("vendedores_force", [])
            
            return force_list
    
