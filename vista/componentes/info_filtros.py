import streamlit as st
from datetime import timedelta

class InfoFiltros:
    def __init__(self):
         pass
    
    def mostrar_info_filtro(self, vendedores_lista, fecha_inicio, fecha_fin):
        """
        Muestra información sobre los filtros aplicados
        """
        # Construir string de vendedores
        if len(vendedores_lista) == 1:
            vendedores_str = vendedores_lista[0]
        elif len(vendedores_lista) <= 5:
            vendedores_str = ", ".join(vendedores_lista)
        else:
            vendedores_str = f"{', '.join(vendedores_lista[:2])} y {len(vendedores_lista)-2} más"
        
        if fecha_inicio and fecha_fin:
            # Determinar si es un mes específico o un año completo
            es_mes_completo = (fecha_inicio.day == 1 and 
                             (fecha_fin.day == 31 or 
                              (fecha_fin + timedelta(days=1)).day == 1))
            
            if es_mes_completo and fecha_inicio.month == fecha_fin.month:
                # Filtro por mes específico
                nombres_meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }
                mes_nombre = nombres_meses[fecha_inicio.month]
                st.info(f"🎯 **Vendedores:** {vendedores_str} | 📅 **{mes_nombre} {fecha_inicio.year}**")
                
            elif fecha_inicio.month == 1 and fecha_inicio.day == 1 and fecha_fin.month == 12 and fecha_fin.day == 31:
                # Filtro por año completo
                st.info(f"🎯 **Vendedores:** {vendedores_str} | 📅 **Año {fecha_inicio.year}**")
            else:
                # Rango de fechas personalizado
                st.info(f"🎯 **Vendedores:** {vendedores_str} | 📅 **Período:** {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
        else:
            st.info(f"🎯 **Vendedores:** {vendedores_str} | 📅 **Todos los períodos**")