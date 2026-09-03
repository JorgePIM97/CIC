# vista/exceles_vista.py
"""
Vista para generar reportes de exceles
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import calendar
from datetime import datetime, timedelta
from vista.base_vista import BaseVista
import plotly.express as px

class ExcelesVista:

    def __init__(self):
        pass


    def arrastrar_archivo_excel(self, uploader_key, df_key):
        uploaded_file = st.file_uploader(
            "Arrastra y suelta un archivo Excel formato XLSX aquí",
            type=['xlsx'],
            accept_multiple_files=False,
            key=uploader_key
        )

        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)

                # Guardar en session_state en un key distinto al del uploader
                st.session_state[df_key] = df

                st.success("Archivo cargado correctamente!")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
                    
                with col2:
                    value=f"{uploaded_file.size / 1024:.1f} KB"
                    st.write(f"Tamaño: {value}")
                
                st.subheader("Vista previa de los datos")
                st.dataframe(df, use_container_width=True) 

            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")


    def arrastrar_archivo_pdf(self):
        archivo_pdf = st.file_uploader(
            "Cargar archivo PDF", 
            type=["pdf"]
            )
        
        return archivo_pdf


