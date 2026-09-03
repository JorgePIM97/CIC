# vista/componentes/sidebar_ventas_real.py
"""
Sidebar principal de ventas reales
"""
import streamlit as st
from datetime import date
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from vista.base_vista import BaseVista
from ..seleccion_usuarios.seleccion import SeleccionUsuarios

class SideBarVentaReal(BaseVista):
    def __init__(self):
        self.seleccion_usuarios = SeleccionUsuarios()


    def vendedores_multiselect(self):
        vendedores = self.seleccion_usuarios.seleccion_privilegiosReal_zona()
        
        # Multiselect de vendedores (sin opción "General")
        vendedores_seleccionados = st.multiselect(
            "Seleccionar vendedores:",
            options=vendedores,
            default=vendedores[:1] if vendedores else [],  # Por defecto selecciona el primer vendedor
            help="Selecciona uno o varios vendedores para comparar sus datos"
        )

        return vendedores_seleccionados

    # Vendedores Excel sin piso
    def vendedores_sidebar_multiselect(self):
        vendedores = self.seleccion_usuarios.obtener_vendedores_excel()
        
        # Multiselect de vendedores (sin opción "General")
        vendedores_seleccionados = st.sidebar.multiselect(
            "Seleccionar vendedores:",
            options=vendedores,
            default=vendedores[:1] if vendedores else [],  # Por defecto selecciona el primer vendedor
            help="Selecciona uno o varios vendedores para comparar sus datos"
        )

        return vendedores_seleccionados
    
    # Vendedores Excel con piso
    def vendedores_sidebar_multiselect_piso(self):
        vendedores = self.seleccion_usuarios.obtener_vendedores_excel()
        
        # Multiselect de vendedores (sin opción "General")
        vendedores_seleccionados = st.sidebar.multiselect(
            "Seleccionar vendedores:",
            options=vendedores+["Piso"],
            default=vendedores[:1] if vendedores else [],  # Por defecto selecciona el primer vendedor
            help="Selecciona uno o varios vendedores para comparar sus datos"
        )

        return vendedores_seleccionados
    

    def mostrar_sidebar_rendimiento(self, modelo):
        """
        Sidebar principal para los filtros del controlador
        """
        st.sidebar.header("Vendedores")

        vendedores_seleccionados = self.vendedores_sidebar_multiselect()
        
        # Filtros de fecha - Solo disponibles si hay vendedores seleccionados
        fecha_inicio = None
        fecha_fin = None

        # Selector de tipo de filtro
        usar_rango = st.sidebar.radio(
            "Selecciona el tipo de filtro:",
            ["Mensual", "Por Rango de Fechas"],
            key="tipo_filtro_radio"
        ) == "Por Rango de Fechas"

        if usar_rango:
            # ==================== MODO: POR RANGO DE FECHAS ====================
            st.sidebar.markdown("### 📅 Rango de Fechas")
            
            if vendedores_seleccionados:
                col1, col2 = st.sidebar.columns(2)
                
                with col1:
                    # Fecha de inicio: un mes antes del mes actual
                    fecha_inicio_default = date.today().replace(day=1) - relativedelta(months=1)
                    fecha_inicio = st.date_input(
                        "Fecha Inicio",
                        fecha_inicio_default,
                        key="fecha_inicio_range"
                    )
                
                with col2:
                    # Fecha de fin: fecha actual
                    fecha_fin_default = date.today()
                    fecha_fin = st.date_input(
                        "Fecha Fin",
                        fecha_fin_default,
                        key="fecha_fin_range"
                    )
                
                # Validar que fecha_inicio sea menor que fecha_fin
                if fecha_inicio and fecha_fin:
                    if fecha_inicio > fecha_fin:
                        st.sidebar.error("❌ La fecha de inicio no puede ser mayor que la fecha de fin")
                        fecha_inicio = None
                        fecha_fin = None
                    else:
                        st.sidebar.info(f"✅ Período: {fecha_inicio} a {fecha_fin}")
            else:
                st.sidebar.warning("⚠️ Selecciona al menos un vendedor para ver los filtros de fecha")

        else:
            # ==================== MODO: MENSUAL ====================
            if vendedores_seleccionados:
                st.sidebar.header("📅 Mensual")
                
                # Obtener meses y años disponibles para los vendedores seleccionados
                meses_años_df = self.obtener_meses_años_para_vendedores(modelo, vendedores_seleccionados)
                
                if not meses_años_df.empty:
                    # Obtener años únicos disponibles
                    años_disponibles = sorted(meses_años_df['Año'].unique(), reverse=True)
                    
                    # Determinar el año actual como default
                    año_actual = datetime.now().year
                    
                    # Encontrar el índice del año actual, si no existe usar el primer año disponible
                    if año_actual in años_disponibles:
                        año_default_index = años_disponibles.index(año_actual)
                    else:
                        año_default_index = 0  # Primer año disponible
                    
                    # Selector de año con año actual como default
                    años_opciones = [str(año) for año in años_disponibles]
                    
                    año_seleccionado_str = st.sidebar.selectbox(
                        "Seleccionar Año:",
                        options=años_opciones,
                        index=año_default_index,
                        key="año_select"
                    )
                    
                    año_seleccionado = int(año_seleccionado_str)
                    
                    # Filtrar meses disponibles para el año seleccionado
                    meses_del_año_df = meses_años_df[meses_años_df['Año'] == año_seleccionado]
                    
                    if not meses_del_año_df.empty:
                        meses_del_año = sorted(meses_del_año_df['Mes'].unique(), reverse=True)

                        # Crear nombres de meses
                        nombres_meses = {
                            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                        }
                        
                        meses_opciones = [f"{nombres_meses[mes]}" for mes in meses_del_año]
                        
                        # Selector de mes
                        mes_seleccionado_str = st.sidebar.selectbox(
                            "Seleccionar Mes:",
                            options=meses_opciones,
                            index=0,
                            key="mes_select"
                        )
                        
                        # Obtener el número del mes seleccionado
                        mes_seleccionado = None
                        for num, nombre in nombres_meses.items():
                            if nombre == mes_seleccionado_str:
                                mes_seleccionado = num
                                break
                        
                        if mes_seleccionado:
                            # Establecer rango de fechas para el mes específico
                            fecha_inicio = datetime(año_seleccionado, mes_seleccionado, 1).date()
                            
                            # Último día del mes
                            if mes_seleccionado == 12:
                                fecha_fin = datetime(año_seleccionado + 1, 1, 1).date() - timedelta(days=1)
                            else:
                                fecha_fin = datetime(año_seleccionado, mes_seleccionado + 1, 1).date() - timedelta(days=1)
                            
                            # Mostrar información del filtro aplicado
                            st.sidebar.info(f"✅ Período: {mes_seleccionado_str} {año_seleccionado}")
                    
                    else:
                        st.sidebar.warning(f"⚠️ No hay datos disponibles para el año {año_seleccionado}")
                        fecha_inicio = None
                        fecha_fin = None
                
                else:
                    st.sidebar.warning("⚠️ No hay datos de fechas disponibles para los vendedores seleccionados")
                    fecha_inicio = None
                    fecha_fin = None
            
            else:
                st.sidebar.warning("⚠️ Selecciona al menos un vendedor para ver las opciones de fecha")
                fecha_inicio = None
                fecha_fin = None
        
        # Guardar el tipo de filtro en session_state para el controlador
        st.session_state.tipo_filtro = "Por Rango de Fechas" if usar_rango else "Mensual"
        
        return vendedores_seleccionados, fecha_inicio, fecha_fin


    def mostrar_sidebar_ventasReales(self, modelo):
        """
        Sidebar principal para los filtros del controlador
        """
        st.sidebar.header("Vendedores")
        
        vendedores_seleccionados = self.vendedores_sidebar_multiselect_piso()
        
        # Filtros de fecha - Solo disponibles si hay vendedores seleccionados
        fecha_inicio = None
        fecha_fin = None
        año_seleccionado = None
        mes_seleccionado = None

        # Selector de tipo de filtro
        usar_rango = st.sidebar.radio(
            "Selecciona el tipo de filtro:",
            ["Mensual", "Por Rango de Fechas"],
            key="tipo_filtro"
        ) == "Por Rango de Fechas"
        
  
        if usar_rango:
            st.sidebar.markdown("### 📅 Rango de Fechas")
            
            if vendedores_seleccionados:
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    # Fecha de inicio: un mes antes del mes actual
                    fecha_inicio_default = date.today().replace(day=1) - relativedelta(months=1)
                    fecha_inicio = st.date_input("Inicio", fecha_inicio_default)
                
                with col2:
                    # Fecha de fin: fecha actual
                    fecha_fin = st.date_input("Fin", date.today())
        else:
            if vendedores_seleccionados:
                st.sidebar.header("📅 Mensual")
                
                # Obtener meses y años disponibles para los vendedores seleccionados
                # Usaremos "General" para obtener todos los datos y luego filtrar
                meses_años_df = self.obtener_meses_años_para_vendedores(modelo, vendedores_seleccionados)
                
                if not meses_años_df.empty:
                    # Obtener años únicos disponibles
                    años_disponibles = sorted(meses_años_df['Año'].unique(), reverse=True)
                    
                    # Determinar el año actual como default
                    año_actual = datetime.now().year
                    
                    # Encontrar el índice del año actual, si no existe usar el primer año disponible
                    if año_actual in años_disponibles:
                        año_default_index = años_disponibles.index(año_actual) + 1  # +1 porque "Todos los años" está en índice 0
                    else:
                        año_default_index = 1  # Primer año disponible
                    
                    años_opciones = ["Todos los años"] + [str(año) for año in años_disponibles]
                    
                    # Selector de año con año actual como default
                    año_seleccionado_str = st.sidebar.selectbox(
                        "Seleccionar Año:",
                        options=años_opciones,
                        index=año_default_index
                    )
                    
                    # Si se selecciona un año específico
                    if año_seleccionado_str != "Todos los años":
                        año_seleccionado = int(año_seleccionado_str)
                        
                        # Filtrar meses disponibles para el año seleccionado
                        meses_del_año_df = meses_años_df[meses_años_df['Año'] == año_seleccionado]
                        
                        if not meses_del_año_df.empty:
                            meses_del_año = sorted(meses_del_año_df['Mes'].unique(), reverse=True)

                            # Crear nombres de meses
                            nombres_meses = {
                                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                            }
                            
                            meses_opciones = ["Todos los meses"] + [f"{nombres_meses[mes]} ({mes})" for mes in meses_del_año]
                            
                            # Selector de mes
                            mes_seleccionado_str = st.sidebar.selectbox(
                                "Seleccionar Mes:",
                                options=meses_opciones,
                                index=0
                            )
                            
                            # Si se selecciona un mes específico
                            if mes_seleccionado_str != "Todos los meses":
                                # Extraer el número del mes del string
                                mes_seleccionado = int(mes_seleccionado_str.split('(')[1].split(')')[0])
                                
                                # Establecer rango de fechas para el mes específico
                                fecha_inicio = datetime(año_seleccionado, mes_seleccionado, 1).date()
                                
                                # Último día del mes
                                if mes_seleccionado == 12:
                                    fecha_fin = datetime(año_seleccionado + 1, 1, 1).date() - timedelta(days=1)
                                else:
                                    fecha_fin = datetime(año_seleccionado, mes_seleccionado + 1, 1).date() - timedelta(days=1)
                            
                            elif año_seleccionado:
                                # Si solo se selecciona el año, establecer rango para todo el año
                                fecha_inicio = datetime(año_seleccionado, 1, 1).date()
                                fecha_fin = datetime(año_seleccionado, 12, 31).date()
                        else:
                            st.sidebar.warning(f"No hay datos disponibles para el año {año_seleccionado}")
                            # Aún así, establecer las fechas del año
                            fecha_inicio = datetime(año_seleccionado, 1, 1).date()
                            fecha_fin = datetime(año_seleccionado, 12, 31).date()
                    
                    # Mostrar información del filtro aplicado
                    if fecha_inicio and fecha_fin:
                        nombres_meses = {
                            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                        }
                        
                        if mes_seleccionado:
                            st.sidebar.info(f"Filtrando: {nombres_meses[mes_seleccionado]} {año_seleccionado}")
                        elif año_seleccionado:
                            st.sidebar.info(f"Filtrando: Todo {año_seleccionado}")
                    else:
                        st.sidebar.info("Mostrando todos los períodos disponibles")
                else:
                    st.sidebar.warning("No hay datos de fechas disponibles para los vendedores seleccionados")
            else:
                st.sidebar.warning("Selecciona al menos un vendedor para ver las opciones de fecha")
        
        return vendedores_seleccionados, fecha_inicio, fecha_fin
    
    def obtener_meses_años_para_vendedores(self, modelo, vendedores_seleccionados):
        """
        Obtiene los meses y años disponibles para una lista de vendedores
        """
        df_total = pd.DataFrame()
        
        for vendedor in vendedores_seleccionados:
            df_temp = modelo.obtener_meses_años_disponibles(vendedor)
            if not df_temp.empty:
                df_total = pd.concat([df_total, df_temp], ignore_index=True)
        
        # Eliminar duplicados y mantener solo combinaciones únicas de año/mes
        if not df_total.empty:
            df_total = df_total.drop_duplicates().reset_index(drop=True)
        
        return df_total
    

    def obtener_lista_vendedores(self):
        """
        Retorna la lista de vendedores disponibles según privilegios y zona.
        """
        return self.seleccion_usuarios.seleccion_privilegiosReal_zona()

    # def obtener_vendedoresReales_completos_pdf(self):
    #     """Obtiene la lista de vendedores reales completos"""
    #     # vendedores_reales = self.ventas_reales.obtener_vendedores_ventas_reales()
    #     vendedores_reales = ['Adan Garza', 'Alfonso Gasca', 'Jorge Martinez', 'Cesar Valdes']

    #     return vendedores_reales
    
    # def obtener_vendedoresReales_completos_pdf(self):
    #     """Obtiene la lista de vendedores reales completos"""
    #     exceles_list = self.seleccion_usuarios.obtener_vendedoresReales_completos_pdf()

    #     return exceles_list

    def mostrar_filtros_ventas(self, modelo):
        """
        Filtros centrados en página principal.
        Sin sidebar, sin rango de fechas, solo vendedor + año/mes.
        """
        fecha_inicio = None
        fecha_fin = None
        mes_seleccionado = None
        año_seleccionado = None

        col1, col2, col3 = st.columns(3)

        with col1:
            vendedores_seleccionados = st.multiselect(
                "Vendedores",
                # options=self.obtener_lista_vendedores(),
                options = self.seleccion_usuarios.obtener_vendedores_excel(),
                placeholder="Selecciona vendedores..."
            )

        if vendedores_seleccionados:
            meses_años_df = self.obtener_meses_años_para_vendedores(modelo, vendedores_seleccionados)

            if not meses_años_df.empty:
                años_disponibles = sorted(meses_años_df['Año'].unique(), reverse=True)
                año_actual = datetime.now().year
                años_opciones = ["Todos los años"] + [str(a) for a in años_disponibles]

                año_default_index = (
                    años_opciones.index(str(año_actual))
                    if str(año_actual) in años_opciones else 1
                )

                with col2:
                    año_seleccionado_str = st.selectbox(
                        "Año",
                        options=años_opciones,
                        index=año_default_index
                    )

                if año_seleccionado_str != "Todos los años":
                    año_seleccionado = int(año_seleccionado_str)
                    meses_del_año = sorted(
                        meses_años_df[meses_años_df['Año'] == año_seleccionado]['Mes'].unique(),
                        reverse=True
                    )

                    nombres_meses = {
                        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                    }

                    meses_opciones = ["Todos los meses"] + [
                        f"{nombres_meses[m]} ({m})" for m in meses_del_año
                    ]

                    with col3:
                        mes_seleccionado_str = st.selectbox(
                            "Mes",
                            options=meses_opciones,
                            index=0
                        )

                    # Calcular fechas
                    if mes_seleccionado_str != "Todos los meses":
                        mes_seleccionado = int(mes_seleccionado_str.split('(')[1].split(')')[0])
                        fecha_inicio = datetime(año_seleccionado, mes_seleccionado, 1).date()
                        fecha_fin = (
                            datetime(año_seleccionado + 1, 1, 1).date() - timedelta(days=1)
                            if mes_seleccionado == 12
                            else datetime(año_seleccionado, mes_seleccionado + 1, 1).date() - timedelta(days=1)
                        )
                    else:
                        fecha_inicio = datetime(año_seleccionado, 1, 1).date()
                        fecha_fin = datetime(año_seleccionado, 12, 31).date()

            else:
                st.warning("No hay datos de fechas disponibles para los vendedores seleccionados.")
        else:
            # st.info("Selecciona al menos un vendedor para ver las opciones de fecha.")
            None
        return vendedores_seleccionados, fecha_inicio, fecha_fin