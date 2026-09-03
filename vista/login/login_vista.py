# vista/login/login_vista.py
import streamlit as st
from modelo.usuarios_modelo import UsuariosModelo

class LoginVista:
    def __init__(self):
        self.modelo = UsuariosModelo()
        # Mapa de permisos por cargo
        self.permisos_por_cargo = {
            'CEO': {
                'comportamiento_vendedores': True,
                'vendedores': False,
                'exceles': False,
                'ventas_reales': True,
                'metas': False,
                'rendimiento': True,
                'kilometraje': False,               
                'planeacion': False,
                'resumen_movilidad': False,
                'presupuesto': False,
                'admin': False,
                'config': True
            },
            'DIRECTOR DE PRODUCCION': {
                'comportamiento_vendedores': True,
                'vendedores': False,
                'exceles': False,
                'ventas_reales': True,
                'metas': False,
                'rendimiento': True,
                'kilometraje': False,               
                'planeacion': False,
                'resumen_movilidad': False,
                'presupuesto': False,
                'admin': False,
                'config': True
            },
            'DIRECTOR COMERCIAL': {
                'comportamiento_vendedores': True,
                'vendedores': False,
                'exceles': False,
                'ventas_reales': True,
                'metas': False,
                'rendimiento': True,
                'kilometraje': False,               
                'planeacion': False,
                'resumen_movilidad': False,
                'presupuesto': False,
                'admin': False,
                'config': True
            },
            'ANALISTA AFTER SALES': {
                'comportamiento_vendedores': False,
                'vendedores': False,
                'exceles': True,
                'ventas_reales': True,
                'metas': False,
                'rendimiento': True,
                'kilometraje': False,               
                'planeacion': False,
                'resumen_movilidad': False,
                'presupuesto': True,
                'admin': False,
                'config': True
            },
            'COORDINADOR DE VENTAS': {
                'comportamiento_vendedores': True,
                'vendedores': False,
                'exceles': False,
                'ventas_reales': True,
                'metas': False,
                'rendimiento': True,
                'kilometraje': False,               
                'planeacion': False,
                'resumen_movilidad': False,
                'presupuesto': False,
                'admin': False,
                'config': True
            },
            'COORDINADOR INTELIGENCIA COMERCIAL': {
                'comportamiento_vendedores': True,
                'vendedores': False,
                'exceles': False,
                'ventas_reales': False,
                'metas': False,
                'rendimiento': True,
                'kilometraje': True,               
                'planeacion': True,
                'resumen_movilidad': True,
                'presupuesto': False,
                'admin': False,
                'config': True
            },
            'ADMINISTRADOR': {
                'comportamiento_vendedores': False,
                'vendedores': False,
                'exceles': False,
                'ventas_reales': False,
                'metas': False,
                'rendimiento': False,
                'kilometraje': False,               
                'planeacion': False,
                'resumen_movilidad': False,
                'presupuesto': False,
                'admin': True,
                'config': True
            }
        }        

        # Inicializar estados de sesión
        if 'usuario_autenticado' not in st.session_state:
            st.session_state.usuario_autenticado = False
        
        if 'usuario_actual' not in st.session_state:
            st.session_state.usuario_actual = None

        if 'cargo_actual' not in st.session_state:
            st.session_state.cargo_actual = None    

        if 'zona_actual' not in st.session_state:
            st.session_state.zona_actual = None    
            
        if 'permisos_usuario' not in st.session_state:
            st.session_state.permisos_usuario = {}

    def login_form(self):
        """Formulario de login"""
        st.markdown("### 🔐 Iniciar Sesión")
        # CSS para centrar el formulario
        st.markdown("""
            <style>
            /* Contenedor principal del formulario */
            div[data-testid="stForm"] {
                max-width: 315px;
                margin: 0 auto !important;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            /* Estilo para las etiquetas - Tamaño 18px y semibold */
            label p {
                font-weight: 600 !important;
                font-size: 18px !important;  /* Tamaño aumentado a 18px */
                margin-bottom: 8px !important;
            }
            
            /* Estilo para los inputs */
            .stTextInput input {
                width: 100% !important;
                margin-bottom: 15px !important;
                font-size: 16px !important;  /* Tamaño opcional para el texto dentro del input */
            }
            
            /* Estilo para el botón */
            .stButton button {
                width: 100% !important;
                margin-top: 10px !important;
                font-size: 16px !important;  /* Tamaño opcional para el botón */
            }
        </style>
        """, unsafe_allow_html=True)

        #st.markdown("<h3 style='text-align: center;'>🔐 Iniciar Sesión</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        # with st.form("login_form"):
        #     usuario = st.text_input("Usuario", placeholder="Ingrese su usuario")
        #     password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
        #     submit_button = st.form_submit_button("Entrar", use_container_width=True)

        with st.form("login_form"):
            correo = st.text_input("Correo", placeholder="Ingrese su correo")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            submit_button = st.form_submit_button("Entrar", use_container_width=True)

            if submit_button:
                st.session_state.permisos_usuario = {
                'comportamiento_vendedores': False,
                'vendedores': False,
                'exceles': False,
                'ventas_reales': False,
                'metas': False,
                'rendimiento': False,
                'kilometraje': False,               
                'planeacion': False,
                'resumen_movilidad': False,
                'presupuesto': False
                }
                # self._validar_credenciales(usuario, password)
                self._validar_credenciales(correo, password)
                
                # from controlador.navegacion_controlador_login import NavegacionControladorLogin
                # NavegacionControladorLogin._mostrar_pantalla_inicio_autenticado()
                
    # def _validar_credenciales(self, correo, password):
    #     """Valida contra la base de datos"""
    #     user = self.modelo.validar_usuario(correo, password)

    #     if user:
    #         st.session_state.usuario_autenticado = True
    #         st.session_state.usuario_actual = f"{user.Nombre}"
    #         st.session_state.cargo_actual = f"{user.Cargo}"
    #         st.session_state.zona_actual = f"{user.Zona}"

    #         # Permisos según el cargo
    #         cargo = user.Cargo.strip().upper()
    #         st.session_state.permisos_usuario = self.permisos_por_cargo.get(cargo, {
    #             'comportamiento_vendedores': False,
    #             'vendedores': False,
    #             'exceles': False,
    #             'ventas_reales': False,
    #             'metas': False,
    #             'rendimiento': False,
    #             'kilometraje': False,               
    #             'planeacion': False,
    #             'resumen_movilidad': False,
    #             'presupuesto': False
    #         })

    #         st.success(f"¡Bienvenido {user.Nombre}!")
    #         st.rerun()
    #     else:
    #         st.error("❌ Correo o contraseña incorrectos, o usuario inactivo.")

    # def login_form(self):
    #     """Formulario de login"""

    #     # Inicializar estado
    #     if 'mostrar_cambio_password' not in st.session_state:
    #         st.session_state.mostrar_cambio_password = False

    #     st.markdown("""
    #         <style>
    #         div[data-testid="stForm"] {
    #             max-width: 315px;
    #             margin: 0 auto !important;
    #             padding: 20px;
    #             border-radius: 10px;
    #             box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    #         }
    #         label p {
    #             font-weight: 600 !important;
    #             font-size: 18px !important;
    #             margin-bottom: 8px !important;
    #         }
    #         .stTextInput input {
    #             width: 100% !important;
    #             margin-bottom: 15px !important;
    #             font-size: 16px !important;
    #         }
    #         .stButton button {
    #             width: 100% !important;
    #             margin-top: 10px !important;
    #             font-size: 16px !important;
    #         }
    #         /* Botón que parece enlace azul */
    #         .stButton button[kind="secondary"] {
    #             background: none !important;
    #             border: none !important;
    #             color: #1a73e8 !important;
    #             font-size: 14px !important;
    #             box-shadow: none !important;
    #             margin-top: 4px !important;
    #             text-align: right !important;      /* <-- alineado a la derecha */
    #             padding-right: 0 !important;
    #         }
    #         .stButton button[kind="secondary"]:hover {
    #             text-decoration: underline !important;
    #             background: none !important;
    #             color: #1558b0 !important;
    #         }

    #         </style>
    #     """, unsafe_allow_html=True)

    #     # ── FORMULARIO DE LOGIN ──
    #     st.markdown("### 🔐 Iniciar Sesión")

    #     st.markdown("---")

    #     with st.form("login_form"):
    #         correo = st.text_input("Correo", placeholder="Ingrese su correo")
    #         password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
    #         submit_button = st.form_submit_button("Entrar", use_container_width=True)

    #         if submit_button:
    #             st.session_state.permisos_usuario = {
    #                 'comportamiento_vendedores': False,
    #                 'vendedores': False,
    #                 'exceles': False,
    #                 'ventas_reales': False,
    #                 'metas': False,
    #                 'rendimiento': False,
    #                 'kilometraje': False,
    #                 'planeacion': False,
    #                 'resumen_movilidad': False,
    #                 'presupuesto': False,
    #                 'admin': False,
    #                 'config': False
    #             }
    #             self._validar_credenciales(correo, password)
    #     if not st.session_state.mostrar_cambio_password:
    #         # ── FORMULARIO DE LOGIN ──
    #         st.markdown("### 🔐 Iniciar Sesión")
    #         with st.form("login_form"):
    #             correo = st.text_input("Correo", placeholder="Ingrese su correo")
    #             password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
    #             submit_button = st.form_submit_button("Entrar", use_container_width=True)

    #             if submit_button:
    #                 st.session_state.permisos_usuario = {
    #                     'comportamiento_vendedores': False,
    #                     'vendedores': False,
    #                     'exceles': False,
    #                     'ventas_reales': False,
    #                     'metas': False,
    #                     'rendimiento': False,
    #                     'kilometraje': False,
    #                     'planeacion': False,
    #                     'resumen_movilidad': False,
    #                     'presupuesto': False,
    #                     'admin': False,
    #                     'config': False
    #                 }
    #                 self._validar_credenciales(correo, password)

    #         # Enlace debajo del form de login
    #         # st.markdown('<div class="link-btn-wrapper">', unsafe_allow_html=True)
    #         _, col_center, _ = st.columns([0.94, 2.5, 0.5])
    #         with col_center:
    #             if st.button("cambiar contraseña", key="ir_a_cambio_pwd", use_container_width=True):
    #                 st.session_state.mostrar_cambio_password = True
    #                 st.rerun()

    #     else:
    #         # ── FORMULARIO DE CAMBIO DE CONTRASEÑA ──
    #         self._formulario_cambio_password()


    def formulario_cambio_password(self, correo_usuario):
        """Formulario para cambiar la contraseña"""
        st.markdown("### 🔑 Cambiar Contraseña")
        with st.form("form_cambio_password"):
            # correo = st.text_input("Correo", value = correo_usuario, disabled=True)
            st.markdown("""
                <style>
                    input[disabled] {
                        -webkit-text-fill-color: #262730 !important;
                        opacity: 1 !important;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.text_input("Correo", value=correo_usuario, disabled=True)
            password_actual = st.text_input("Contraseña actual", type="password", placeholder="Ingrese su contraseña actual")
            nueva_password = st.text_input("Nueva contraseña", type="password", placeholder="Nueva contraseña")
            confirmar_password = st.text_input("Confirmar contraseña", type="password", placeholder="Repita la nueva contraseña")
            submit = st.form_submit_button("Guardar cambio", use_container_width=True)

            if submit:
                if not correo_usuario or not password_actual or not nueva_password or not confirmar_password:
                    st.error("❌ Todos los campos son obligatorios.")
                elif nueva_password != confirmar_password:
                    st.error("❌ Las contraseñas nuevas no coinciden.")
                elif nueva_password == password_actual:
                    st.error("❌ La nueva contraseña debe ser diferente a la actual.")
                else:
                    usuario_valido = self.modelo.validar_usuario(correo_usuario, password_actual)
                    if not usuario_valido:
                        st.error("❌ El correo o la contraseña actual son incorrectos.")
                    else:
                        exito = self.modelo.actualizar_password(correo_usuario, nueva_password)
                        if exito:
                            st.success("✅ Contraseña actualizada correctamente.")
                            st.session_state.mostrar_cambio_password = False
                            st.rerun()
                        else:
                            st.error("❌ Ocurrió un error al actualizar la contraseña.")

        # # Enlace para volver al login
        # # Reemplaza el bloque del enlace de volver por:
        # _, col_center, _ = st.columns([1.03, 2.5, 0.5])
        # with col_center:
        #     if st.button("← volver al login", key="volver_login", use_container_width=True):
        #         st.session_state.mostrar_cambio_password = False
        #         st.rerun()
                
    def _validar_credenciales(self, correo, password):
        """Valida contra la base de datos"""
        user = self.modelo.validar_usuario(correo, password)

        if user:
            st.session_state.usuario_autenticado = True
            st.session_state.usuario_actual = f"{user.Nombre}"
            st.session_state.cargo_actual = f"{user.Cargo}"
            st.session_state.zona_actual = f"{user.Zona}"

            # Permisos según el cargo
            cargo = user.Cargo.strip().upper()
            st.session_state.permisos_usuario = self.permisos_por_cargo.get(cargo, {
                'comportamiento_vendedores': False,
                'vendedores': False,
                'exceles': False,
                'ventas_reales': False,
                'metas': False,
                'rendimiento': False,
                'kilometraje': False,               
                'planeacion': False,
                'resumen_movilidad': False,
                'presupuesto': False,
                'admin': False,
                'config': False
            })

            st.success(f"¡Bienvenido {user.Nombre}!")
            st.rerun()
        else:
            st.error("❌ Correo o contraseña incorrectos, o usuario inactivo.")
            
    def logout(self):
        """Función para cerrar sesión"""
        st.session_state.usuario_autenticado = False
        st.session_state.usuario_actual = None
        st.session_state.cargo_actual = None
        st.session_state.zona_actual = None
        st.session_state.permisos_usuario = {
            'comportamiento_vendedores': False,
            'vendedores': False,
            'exceles': False,
            'ventas_reales': False,
            'metas': False,
            'rendimiento': False,
            'kilometraje': False,               
            'planeacion': False,
            'resumen_movilidad': False,
            'presupuesto': False,
            'admin': False,
            'config': False
        }
        # También resetear estados de navegación
        st.session_state.mostrar_comportamientos = False
        st.session_state.mostrar_perfiles = False
        st.session_state.mostrar_exceles = False
        st.session_state.mostrar_ventas_reales = False
        st.session_state.mostrar_metas = False
        st.session_state.mostrar_kilometraje = False
        st.session_state.mostrar_planeacion = False
        st.session_state.mostrar_presupuesto = False

        st.rerun()

    def mostrar_info_usuario(self):
        """Muestra información del usuario logueado en el sidebar"""
        if st.session_state.usuario_autenticado:
            st.sidebar.markdown("---")
            # st.sidebar.markdown(f"**Cargo:** {st.session_state.cargo_actual}")
            st.sidebar.markdown(f"**Usuario:** {st.session_state.usuario_actual}")
            
            if st.sidebar.button("Cerrar Sesión", use_container_width=True):
                self.logout()

    def get_zona_de_sesion(self):
        try:
            get_zona = st.session_state.zona_actual
        except Exception as e:
            print(f"Error al obtener cargo actual: {e}")
        return get_zona

    def get_cargo_de_sesion(self):
        try:
            get_cargo = st.session_state.cargo_actual
        except Exception as e:
            print(f"Error al obtener cargo actual: {e}")
        return get_cargo

    def get_usuario_de_sesion(self):
        try:
            get_usuario = st.session_state.usuario_actual
        except Exception as e:
            print(f"Error al obtener usuario actual: {e}")
        return get_usuario