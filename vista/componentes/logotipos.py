# vista/componentes/logotipos.py
import streamlit as st
import os
from typing import Optional

class LogosApp:
    
    def __init__(self):
        # Directorio base del proyecto (donde está main.py)
        self.base_path = os.path.dirname(os.path.abspath(__file__))  
        self.base_path = os.path.abspath(os.path.join(self.base_path, "..", ".."))

        # Ruta absoluta del logo
        self.LOGOTIPO_PRINCIPAL = os.path.join(self.base_path, "vista", "images", "logo_GPA.png")

    def logotipo_principal(
        self,
        image: Optional[str] = None,
        use_container_width: bool = True,
        output_format: str = "PNG"
    ):
        """
        Muestra el logotipo principal en el sidebar
        """

        # Si no se especifica imagen, usamos la ruta absoluta generada
        if image is None:
            image = self.LOGOTIPO_PRINCIPAL

        # Verificar existencia real del archivo
        if not os.path.exists(image):
            st.sidebar.error(f"⚠️ Logo no encontrado: {image}")
            return None
        
        return st.sidebar.image(
            image=image,
            use_container_width=use_container_width,
            output_format=output_format
        )
