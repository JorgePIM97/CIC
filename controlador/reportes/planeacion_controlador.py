# controlador/reportes/planeacion_controlador.py
import streamlit as st
import pandas as pd
from datetime import datetime
from modelo.planeacion_modelo import PlaneacionModelo
from vista.base_vista import BaseVista

class PlaneacionControlador(BaseVista):

    def __init__(self):
        self.modelo = PlaneacionModelo()
        

    def ejecutar_vista_planeacion(self):
        self.mostrar_titulo("🔍 Monitoreo de Planeación 🖥️")

        actividades = self.modelo.obtener_actividades_vendedores()

        vendedores_completos = self.modelo.obtener_vendedores_completos()
        vendedores_df = pd.DataFrame(vendedores_completos, columns=["Vendedor"])

        df_actividades = vendedores_df.merge(
            actividades,
            on="Vendedor",
            how="left"
        ).fillna({"TotalActividades": 0})

        # APLICAR ALIAS A LA TABLA "Planeaciones por vendedor"
        df_actividades_renombrado = df_actividades.rename(columns={
            "Vendedor": "Vendedor",
            "TotalActividades": "Total de Actividades"
        })

        df_notificaciones = self.modelo.obtener_notificaciones()
        df_strikes = self.modelo.obtener_strikes()
        df_detalle = self.modelo.obtener_detalle_planeacion()

        # APLICAR ALIAS A LA TABLA "Detalle de planeacion"
        df_detalle_renombrado = df_detalle.rename(columns={
            "Id": "Id Actividad",
            "Subject": "Descripcion",
            "SalesRepId_Value": "Vendedor",
            "DateCreated": "Fecha Creada",
            "TypeId_Value": "Asunto",
            "Cuenta": "Cuenta",
            "StatusProspecto": "Status"
        })

        st.subheader("📌 Planeaciones por vendedor")
        st.dataframe(df_actividades_renombrado)

        st.subheader("📋 Detalle de Planeación")
        st.dataframe(df_detalle_renombrado)

        # Lunes (0) o Viernes (4)
        hoy = datetime.now().weekday()
        boton_habilitado = hoy in (0, 4)

        st.markdown("""
        <style>
        .card {
            background-color: #ffffff10;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 12px;
            border: 1px solid #cccccc50;
        }
        .card-title {
            font-size: 32px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        for index, row in df_actividades.iterrows():

            vendedor = row["Vendedor"]
            total_actividades = int(row["TotalActividades"])

            if total_actividades < 15:

                total_notif = df_notificaciones.loc[
                    df_notificaciones["VendedorId"] == vendedor, "TotalNotificaciones"
                ].sum()

                total_strikes = df_strikes.loc[
                    df_strikes["VendedorId"] == vendedor, "TotalStrikes"
                ].sum()

                usada_hoy = self.modelo.notificacion_existente_hoy(vendedor) > 0

                # 👉 CADA 2 elementos se crea una NUEVA FILA
                if index % 2 == 0:
                    cols = st.columns(2)

                # 👉 Selección de columna
                col = cols[0] if index % 2 == 0 else cols[1]

                with col:
                    st.markdown(f"""
                    <div class='card'>
                        <div class='card-title'>
                            <strong>{vendedor.upper()} - ⚠️ {total_actividades} actividades</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    mcol1, mcol2 = st.columns(2)

                    with mcol1:
                        st.markdown(f"""
                        <div style="text-align:center; padding:10px; background:#e7f1ff; border-radius:6px;">
                            <div>🔔</div>
                            <div style="font-size:24px; font-weight:bold;">{total_notif}</div>
                            <div style="font-size:13px;">NOTIFICACIONES</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with mcol2:
                        st.markdown(f"""
                        <div style="text-align:center; padding:10px; background:#f8d7da; border-radius:6px;">
                            <div>💥</div>
                            <div style="font-size:24px; font-weight:bold;">{total_strikes}</div>
                            <div style="font-size:13px;">STRIKES</div>
                        </div>
                        """, unsafe_allow_html=True)

                    key_confirm = f"notif_confirm_{vendedor}"
                    boton_deshabilitado = not boton_habilitado or usada_hoy

                    if st.button(
                        f"Agregar notificación",
                        key=f"notif_{vendedor}",
                        disabled=boton_deshabilitado,
                        use_container_width=True,
                        type="primary"
                    ):
                        st.session_state[key_confirm] = True
