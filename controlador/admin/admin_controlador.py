# C:\CIC_WebApp\controlador\admin\admin_controlador.py
import pandas as pd
import streamlit as st
from vista.base_vista import BaseVista
from modelo.admin.admin_modelo import AdminModelo


class AdminControlador(BaseVista):
    def __init__(self):
        self.admin_modelo = AdminModelo()

    # ------------------------------------------------------------------ #
    #  Helpers reutilizables                                             #
    # ------------------------------------------------------------------ #

    def _seccion_agregar(
        self,
        vendedores_force: list[str],
        vendedores_exceles: list[str],
        key_suffix: str,
        fn_agregar_force,
        fn_agregar_excel,
    ):
        """Renderiza la sub-sección 'Agregar vendedor' para una región."""
        col_force, col_excel = st.columns(2)

        with col_force:
            st.markdown("**Force Manager**")
            sel_force = st.selectbox(
                label="Selecciona un vendedor Force",
                options=["— Selecciona —"] + vendedores_force,
                key=f"sel_force_{key_suffix}",
                help= "No aparecerán vendedores hasta que sean dados de alta en Force Manager"
            )
            if st.button("➕ Guardar vendedor Force", key=f"btn_force_{key_suffix}", use_container_width=True):
                if sel_force == "— Selecciona —":
                    st.warning("Elige un vendedor antes de guardar.")
                else:
                    if fn_agregar_force(sel_force):
                        st.success(f"✅ '{sel_force}' agregado correctamente.")
                        st.rerun()
                    else:
                        st.info(f"'{sel_force}' ya estaba registrado.")

        with col_excel:
            st.markdown("**Netsuite**")
            sel_excel = st.selectbox(
                label="Selecciona un vendedor de Netsuite",
                options=["— Selecciona —"] + vendedores_exceles,
                key=f"sel_excel_{key_suffix}",
                help= "No aparecerán vendedores hasta que sean cargados datos de Netsuite por Analista After Sales"
            )
            if st.button("➕ Guardar vendedor Excel", key=f"btn_excel_{key_suffix}", use_container_width=True):
                if sel_excel == "— Selecciona —":
                    st.warning("Elige un vendedor antes de guardar.")
                else:
                    if fn_agregar_excel(sel_excel):
                        st.success(f"✅ '{sel_excel}' agregado correctamente.")
                        st.rerun()
                    else:
                        st.info(f"'{sel_excel}' ya estaba registrado.")

    def _seccion_tabla(self, force_list: list[str], exceles_list: list[str]):
        """Renderiza la tabla + métricas de vendedores guardados."""
        max_len = max(len(force_list), len(exceles_list), 1)
        df_tabla = pd.DataFrame(
            {
                "Vendedor Force": force_list + [""] * (max_len - len(force_list)),
                "Vendedor Netsuite": exceles_list + [""] * (max_len - len(exceles_list)),
            }
        )
        df_tabla.index = df_tabla.index + 1

        st.dataframe(df_tabla, use_container_width=True, hide_index=False)

        m1, m2 = st.columns(2)
        m1.metric("Force registrados", len(force_list))
        m2.metric("Netsuite registrados", len(exceles_list))

    def _seccion_eliminar(
        self,
        force_list: list[str],
        exceles_list: list[str],
        key_suffix: str,
        fn_eliminar_force,
        fn_eliminar_excel,
    ):
        """Renderiza el expander de eliminación para una región."""
        with st.expander("⛔ Eliminar vendedor"):
            col_del_f, col_del_e = st.columns(2)

            with col_del_f:
                st.markdown("**Eliminar Force**")
                if force_list:
                    del_force = st.selectbox(
                        "Vendedor a eliminar (Force)",
                        options=force_list,
                        key=f"del_force_{key_suffix}",
                    )
                    if st.button("Eliminar Force", key=f"btn_del_force_{key_suffix}", use_container_width=True):
                        fn_eliminar_force(del_force)
                        st.success(f"'{del_force}' eliminado.")
                        st.rerun()
                else:
                    st.info("No hay vendedores Force guardados.")

            with col_del_e:
                st.markdown("**Eliminar Netsuite**")
                if exceles_list:
                    del_excel = st.selectbox(
                        "Vendedor a eliminar (Netsuite)",
                        options=exceles_list,
                        key=f"del_excel_{key_suffix}",
                    )
                    if st.button("Eliminar Netsuite", key=f"btn_del_excel_{key_suffix}", use_container_width=True):
                        fn_eliminar_excel(del_excel)
                        st.success(f"'{del_excel}' eliminado.")
                        st.rerun()
                else:
                    st.info("No hay vendedores Netsuite guardados.")

    # ------------------------------------------------------------------ #
    #  Vista principal                                                   #
    # ------------------------------------------------------------------ #

    def ejecutar_vista_admin(self):
        self.mostrar_titulo("📈 Administrar Vendedores")

        # ── Cargar catálogos de la BD (compartidos entre regiones) ─────── #
        vendedores_force   = self.admin_modelo.obtener_vendedores_force()
        vendedores_exceles = self.admin_modelo.obtener_vendedores_exceles()
        guardados          = self.admin_modelo.obtener_guardados()

        # ================================================================ #
        #  TAB por región                                                  #
        # ================================================================ #
        # tab_general, tab_norte, tab_bajio = st.tabs(["🌎 General", "🧭 Norte", "🌵 Bajío"])
        tab_general, tab_norte, tab_bajio, tab_fotos = st.tabs(
            [
                "🌎 General",
                "🧭 Norte",
                "🌵 Bajío",
                "📷 Fotografías",
            ]
        )
        # ================================================================ #
        #  TAB GENERAL                                                    #
        # ================================================================ #
        with tab_general:
            st.subheader("Sincronizar vendedor — General")
            self._seccion_agregar(
                vendedores_force=vendedores_force,
                vendedores_exceles=vendedores_exceles,
                key_suffix="general",
                fn_agregar_force=self.admin_modelo.agregar_vendedor_force,
                fn_agregar_excel=self.admin_modelo.agregar_vendedor_excel,
            )

            st.divider()
            st.subheader("Vendedores guardados — General")
            force_list   = guardados.get("vendedores_force", [])
            exceles_list = guardados.get("vendedores_exceles", [])
            self._seccion_tabla(force_list, exceles_list)

            st.divider()
            self._seccion_eliminar(
                force_list=force_list,
                exceles_list=exceles_list,
                key_suffix="general",
                fn_eliminar_force=self.admin_modelo.eliminar_vendedor_force,
                fn_eliminar_excel=self.admin_modelo.eliminar_vendedor_excel,
            )

        # ================================================================ #
        #  TAB NORTE                                                      #
        # ================================================================ #
        with tab_norte:
            st.subheader("Sincronizar vendedor — Norte")
            self._seccion_agregar(
                vendedores_force=vendedores_force,
                vendedores_exceles=vendedores_exceles,
                key_suffix="norte",
                fn_agregar_force=self.admin_modelo.agregar_vendedor_norte_force,
                fn_agregar_excel=self.admin_modelo.agregar_vendedor_norte_excel,
            )

            st.divider()
            st.subheader("Vendedores guardados — Norte")
            force_list   = guardados.get("vendedores_norte_force", [])
            exceles_list = guardados.get("vendedores_norte_exceles", [])
            self._seccion_tabla(force_list, exceles_list)

            st.divider()
            self._seccion_eliminar(
                force_list=force_list,
                exceles_list=exceles_list,
                key_suffix="norte",
                fn_eliminar_force=self.admin_modelo.eliminar_vendedor_norte_force,
                fn_eliminar_excel=self.admin_modelo.eliminar_vendedor_norte_excel,
            )

        # ================================================================ #
        #  TAB BAJÍO                                                      #
        # ================================================================ #
        with tab_bajio:
            st.subheader("Sincronizar vendedor — Bajío")
            self._seccion_agregar(
                vendedores_force=vendedores_force,
                vendedores_exceles=vendedores_exceles,
                key_suffix="bajio",
                fn_agregar_force=self.admin_modelo.agregar_vendedor_bajio_force,
                fn_agregar_excel=self.admin_modelo.agregar_vendedor_bajio_excel,
            )

            st.divider()
            st.subheader("Vendedores guardados — Bajío")
            force_list   = guardados.get("vendedores_bajio_force", [])
            exceles_list = guardados.get("vendedores_bajio_exceles", [])
            self._seccion_tabla(force_list, exceles_list)

            st.divider()
            self._seccion_eliminar(
                force_list=force_list,
                exceles_list=exceles_list,
                key_suffix="bajio",
                fn_eliminar_force=self.admin_modelo.eliminar_vendedor_bajio_force,
                fn_eliminar_excel=self.admin_modelo.eliminar_vendedor_bajio_excel,
            )

        # ================================================================ #
        #  TAB FOTOGRAFÍAS                                                 #
        # ================================================================ #

        with tab_fotos:

            st.subheader("📷 Fotografías de vendedores")

            st.caption(
                "Administra las fotografías utilizadas en los reportes PDF."
            )

            # ------------------------------------------------------------ #
            # Vendedores disponibles
            # ------------------------------------------------------------ #

            vendedores = guardados.get("vendedores_exceles", [])

            if not vendedores:
                st.info(
                    "No hay vendedores registrados. "
                    "Primero debes dar de alta vendedores en la pestaña General."
                )

            else:

                vendedor_foto = st.selectbox(
                    "Selecciona un vendedor",
                    options=["— Selecciona —"] + vendedores,
                    key="foto_vendedor"
                )

                if vendedor_foto != "— Selecciona —":

                    st.divider()

                    # ---------------------------------------------------- #
                    # Fotografía actualmente registrada
                    # ---------------------------------------------------- #

                    foto_actual = self.admin_modelo.obtener_foto_vendedor(
                        vendedor_foto
                    )

                    if foto_actual:

                        st.markdown("**Fotografía actual**")

                        st.image(
                            foto_actual,
                            width=150
                        )

                    else:

                        st.info(
                            f"'{vendedor_foto}' todavía no tiene "
                            "una fotografía registrada."
                        )

                    st.divider()

                    # ---------------------------------------------------- #
                    # Subir nueva fotografía
                    # ---------------------------------------------------- #

                    st.markdown("**Subir fotografía**")

                    archivo = st.file_uploader(
                        "Selecciona una imagen",
                        type=["jpg", "jpeg", "png"],
                        key=f"upload_foto_{vendedor_foto}"
                    )

                    if archivo is not None:

                        st.markdown("**Vista previa**")

                        st.image(
                            archivo,
                            width=150
                        )

                        if st.button(
                            "💾 Guardar fotografía",
                            key=f"guardar_foto_{vendedor_foto}",
                            use_container_width=True
                        ):

                            guardada = self.admin_modelo.guardar_foto_vendedor(
                                vendedor=vendedor_foto,
                                nombre_archivo=archivo.name,
                                contenido=archivo.getvalue()
                            )

                            if guardada:

                                st.success(
                                    f"Fotografía de '{vendedor_foto}' "
                                    "guardada correctamente."
                                )

                                st.rerun()

                    # ---------------------------------------------------- #
                    # Eliminar fotografía
                    # ---------------------------------------------------- #

                    if foto_actual:

                        st.divider()

                        with st.expander("⛔ Eliminar fotografía"):

                            st.warning(
                                "La fotografía dejará de estar disponible "
                                "para los reportes PDF."
                            )

                            if st.button(
                                "Eliminar fotografía",
                                key=f"eliminar_foto_{vendedor_foto}",
                                use_container_width=True
                            ):

                                eliminada = (
                                    self.admin_modelo.eliminar_foto_vendedor(
                                        vendedor_foto
                                    )
                                )

                                if eliminada:

                                    st.success(
                                        f"Fotografía de '{vendedor_foto}' "
                                        "eliminada correctamente."
                                    )

                                    st.rerun()