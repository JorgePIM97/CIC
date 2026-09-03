# C:\CIC_WebApp\controlador\admin\configuracion_controlador.py
import streamlit as st
from vista.base_vista import BaseVista
from modelo.admin.admin_modelo import AdminModelo
from modelo.usuarios_modelo import UsuariosModelo
from vista.login.login_vista import LoginVista


class ConfiguracionControlador(BaseVista):
    def __init__(self):
        self.admin_modelo = AdminModelo()
        self.login_vista = LoginVista()
        self.usuario_modelo = UsuariosModelo()

    def _resetear_modulos(self):
        """Desactiva todos los módulos de navegación"""
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
        st.session_state.mostrar_config = False

    def ejecutar_vista_configuracion(self):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title("⚙️ Configuración de Perfil")
        with col2:
            st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
            if st.button("← Volver", use_container_width=False):
                self._resetear_modulos()
                st.rerun()

        st.markdown("---")
        # --- Aquí tu contenido de configuración ---
        usuario_cargo = st.session_state.get('cargo_actual', 'Cargo')
        correo_usuario = self.usuario_modelo.obtener_correo(usuario_cargo)
        self.login_vista.formulario_cambio_password(str(correo_usuario))
        st.markdown("---")
