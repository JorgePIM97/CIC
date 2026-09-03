import streamlit as st
from vista.base_vista import BaseVista
from vista.kilometraje_vista import KilometrajeVista
from modelo.kilometraje_modelo import KilometrajeModelo
import pandas as pd

class KilometrajeControlador(BaseVista):
    def __init__(self):
        self.kilometraje_vista = KilometrajeVista()
        self.kilometraje_modelo = KilometrajeModelo()

    def ejecutar_vista_kilometraje(self):
        self.mostrar_titulo("🚗 Registro del Kilometraje GPS")

        # --- Inicializar variables ---
        if "kilometros_input" not in st.session_state:
            st.session_state.kilometros_input = None
        if "reset_kilometraje" not in st.session_state:
            st.session_state.reset_kilometraje = False

        # --- Reiniciar valor si se acaba de guardar ---
        if st.session_state.reset_kilometraje:
            st.session_state.kilometros_input = None
            st.session_state.reset_kilometraje = False

        # --- Entradas de usuario ---
        vendedor = self.kilometraje_vista.vendedores_real_selectbox()
        kilometros = st.number_input(
            "Kilómetros del día:",
            min_value=0.0,
            step=50.0,
            format="%.2f",
            key="kilometros_input"
        )
        descripcion = self.kilometraje_vista.descripcion_input()
        fecha_movilidad = self.kilometraje_vista.fechaKilometraje_input()

        # --- Botón habilitado solo si hay valor válido ---
        guardar_habilitado = kilometros != None
        guardar = st.button(
            "Guardar Kilometraje",
            use_container_width=True,
            disabled=not guardar_habilitado
        )

        if guardar:
            exito = self.kilometraje_modelo.insertar_kilometraje(
                vendedor=vendedor,
                kilometros=kilometros,
                descripcion=descripcion,
                fecha_movilidad=fecha_movilidad
            )
            if exito:
                st.session_state.reset_kilometraje = True
                st.success("✅ Registro guardado correctamente.")
                st.rerun()

        # --- Mostrar registros ---
        st.markdown("---")
        # st.subheader("📋 Registros de Kilometraje")

        col1, col2 = st.columns([3, 1])
        with col2:
            limite = st.selectbox(
                "Mostrar últimos:",
                options=["Todos", 10, 25, 50, 100],
                index=2
            )

        df_registros = self.kilometraje_modelo.obtener_registros_kilometraje(limite)

        if df_registros is not None and not df_registros.empty:
            df_display = df_registros.copy()
            
            # --- Formatear columnas para visualización ---
            df_display["Fecha_Movilidad"] = pd.to_datetime(df_display["Fecha_Movilidad"]).dt.date
            df_display["Fecha_Registro"] = pd.to_datetime(df_display["Fecha_Registro"]).dt.strftime("%d/%m/%Y %H:%M")
            df_display["Kilometros"] = df_display["Kilometros"].apply(lambda x: round(x, 2))
            
            # Reordenar columnas para mostrar ID primero (si existe)
            if "id_MovilidadRegistro" in df_display.columns:
                columnas = ["id_MovilidadRegistro"] + [col for col in df_display.columns if col != "id_MovilidadRegistro"]
                df_display = df_display[columnas]

            # # --- Mostrar tabla ---
            # st.dataframe(df_display, use_container_width=True, hide_index=True)

            # --- Mostrar tabla con selección múltiple ---
            st.markdown("### 📋 Registros de Kilometraje")
            
            # Configuración de selección en el dataframe
            event = st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )
            
            # Obtener las filas seleccionadas
            filas_seleccionadas = event.selection.rows
            
            if filas_seleccionadas:
                # st.info(f"📌 {len(filas_seleccionadas)} registro(s) seleccionado(s)")
                
                # Inicializar estados para confirmación
                if "mostrar_confirmacion_multi" not in st.session_state:
                    st.session_state.mostrar_confirmacion_multi = False
                if "registros_a_eliminar" not in st.session_state:
                    st.session_state.registros_a_eliminar = []

                # Botón para eliminar seleccionados
                eliminar_btn = st.button(
                    f"Eliminar {len(filas_seleccionadas)} registro(s) seleccionado(s)",
                    use_container_width=True,
                    type="primary"
                )
                
                if eliminar_btn:
                    st.session_state.mostrar_confirmacion_multi = True
                    st.session_state.registros_a_eliminar = filas_seleccionadas
                
                # Mostrar diálogo de confirmación
                if st.session_state.mostrar_confirmacion_multi:
                    st.warning("⚠️ ¿Estás seguro de que deseas eliminar estos registros?")
                    
                    # Mostrar detalles de los registros a eliminar
                    st.markdown("**Registros que serán eliminados:**")
                    registros_info = []
                    for idx in st.session_state.registros_a_eliminar:
                        row = df_display.iloc[idx]
                        if "id_MovilidadRegistro" in df_display.columns:
                            info = f"• ID: {row['id_MovilidadRegistro']} - {row['Vendedor']} - {row['Fecha_Movilidad']} - {row['Kilometros']} km"
                        else:
                            info = f"• {row['Vendedor']} - {row['Fecha_Movilidad']} - {row['Kilometros']} km"
                        registros_info.append(info)
                    
                    for info in registros_info:
                        st.markdown(info)
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        confirmar = st.button("✅ Sí, eliminar", use_container_width=True, type="primary")
                    
                    with col2:
                        cancelar = st.button("❌ Cancelar", use_container_width=True)
                    
                    # Confirmar eliminación
                    if confirmar:
                        errores = 0
                        eliminados = 0
                        
                        for idx in st.session_state.registros_a_eliminar:
                            row = df_display.iloc[idx]
                            
                            # Si existe ID, eliminar por ID
                            if "id_MovilidadRegistro" in df_display.columns:
                                id_registro = int(row['id_MovilidadRegistro'])
                                exito = self.kilometraje_modelo.eliminar_kilometraje_por_id(id_registro)
                            else:
                                # Fallback al método anterior
                                vendedor = row['Vendedor']
                                fecha_mov = row['Fecha_Movilidad']
                                kilometros_valor = float(row['Kilometros'])
                                exito = self.kilometraje_modelo.eliminar_kilometraje(
                                    vendedor, fecha_mov, kilometros_valor
                                )
                            
                            if exito:
                                eliminados += 1
                            else:
                                errores += 1
                        
                        # Mostrar resultado
                        if eliminados > 0:
                            st.success(f"✅ {eliminados} registro(s) eliminado(s) correctamente.")
                        if errores > 0:
                            st.error(f"❌ Error al eliminar {errores} registro(s).")
                        
                        # Limpiar estado y recargar
                        st.session_state.mostrar_confirmacion_multi = False
                        st.session_state.registros_a_eliminar = []
                        st.rerun()
                    
                    # Cancelar
                    if cancelar:
                        st.session_state.mostrar_confirmacion_multi = False
                        st.session_state.registros_a_eliminar = []
                        st.rerun()
            else:
                # st.info("👆 Selecciona uno o más registros de la tabla para eliminarlos")
                None
        else:
            st.info("No hay registros de kilometraje disponibles.")