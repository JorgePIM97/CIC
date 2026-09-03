# modelo/vendedores_registrados.py
from controlador.perfilesGraficas.status_cliente_controlador import StatusClienteControlador as VendedoresRegistrados
from modelo.ventas_reales_modelo import VentasRealesModelo

class VendedoresRegistrados:
    def __init__(self):
        self.ventas_reales = VentasRealesModelo()

    """Nombres de SalesRepId1_Value de tabla Accounts"""
    def obtener_vendedores_completos(self):
        """Obtiene la lista de vendedores por defecto"""
        return [
            'JORGE MARTINEZ ALANIS', # Monterrey
            'ALFONSO GASCA OROZCO', # Guadalajara
            'ADAN GARZA MARTINEZ', # Monclova
            'CESAR VALDES ZUÑIGA', # Leon
            'Javier Ibarrola'
        
        ]
    
    
    def obtener_vendedores_monclova(self):
        """Obtiene la lista de vendedores de zona Monclova"""
        return [
            'ADAN GARZA MARTINEZ' # Monclova
        ]
    
    def obtener_vendedores_monterrey(self):
        """Obtiene la lista de vendedores de zona monterrey"""
        return [
            'JORGE MARTINEZ ALANIS' # Monterrey
        ]
    
    def obtener_vendedores_guadalajara(self):
        """Obtiene la lista de vendedores de zona guadalajara"""
        return [
            'ALFONSO GASCA OROZCO' # Guadalajara
        ]
    
    def obtener_vendedores_leon(self):
        """Obtiene la lista de vendedores de zona Leon"""
        return [
            'CESAR VALDES ZUÑIGA' # Leon
        ]
    
    def obtener_vendedores_norte(self):
        """Obtiene la lista de vendedores de zona norte"""
        return [
            'JORGE MARTINEZ ALANIS', # Monterrey
            'ADAN GARZA MARTINEZ' # Monclova
        ]
    
    def obtener_vendedores_bajio(self):
        """Obtiene la lista de vendedores de zona bajio"""
        return [
            'ALFONSO GASCA OROZCO', # Guadalajara
            'CESAR VALDES ZUÑIGA', # Leon
            'Javier Ibarrola'
        ]
    

    # """Obtiene vendedores de dev_Detalle_Corregida (Informacion de Excel)"""
    # def obtener_vendedoresReales_completos(self):
    #     """Obtiene la lista de vendedores reales completos"""
    #     vendedores_reales = self.ventas_reales.obtener_vendedores_ventas_reales()

    #     return vendedores_reales
    
    def obtener_vendedoresReales_completos(self):
        """Obtiene la lista de vendedores reales completos"""
        vendedores_reales = ['Adan Garza', 
                             'Alfonso Gasca', 
                             'Jorge Martinez', 
                             'Cesar Valdes',
                             'Javier Ibarrola',
                             'Piso']

        return vendedores_reales
    

    def obtener_vendedoresReales_leon(self):
        """Obtiene la lista de vendedores reales de zona Leon (solo Cesar Valdes)"""
        vendedores_reales = self.ventas_reales.obtener_vendedores_ventas_reales()
        
        # Filtrar solo a "Cesar Valdes"
        vendedores_reales_leon = [v for v in vendedores_reales if v == "Cesar Valdes"]

        return vendedores_reales_leon
    
    def obtener_vendedoresReales_guadalajara(self):
        """Obtiene la lista de vendedores reales de zona Guadalajara (solo Alfonso Gasca)"""
        vendedores_reales = self.ventas_reales.obtener_vendedores_ventas_reales()
        
        # Filtrar solo a "Alfonso Gasca"
        vendedores_reales_guadalajara = [v for v in vendedores_reales if v == "Alfonso Gasca"]

        return vendedores_reales_guadalajara
    
    def obtener_vendedoresReales_monclova(self):
        """Obtiene la lista de vendedores reales de zona Monclova (solo Adan Garza)"""
        vendedores_reales = self.ventas_reales.obtener_vendedores_ventas_reales()
        
        # Filtrar solo a "Adan Garza"
        vendedores_reales_monclova = [v for v in vendedores_reales if v == "Adan Garza"]

        return vendedores_reales_monclova
    
    def obtener_vendedoresReales_monterrey(self):
        """Obtiene la lista de vendedores reales de zona Monterrey (solo Jorge Martinez)"""
        vendedores_reales = self.ventas_reales.obtener_vendedores_ventas_reales()
        
        # Filtrar solo a "Jorge Martinez"
        vendedores_reales_monterrey = [v for v in vendedores_reales if v == "Jorge Martinez"]

        return vendedores_reales_monterrey
    

    def obtener_vendedoresReales_norte(self):
        """Obtiene la lista de vendedores reales de zona Norte (Jorge Martinez y Adan Garza)"""
        vendedores_reales = self.ventas_reales.obtener_vendedores_ventas_reales()
        
        # Lista de vendedores permitidos en zona Norte
        vendedores_norte = ["Jorge Martinez", "Adan Garza"]

        # Filtrar solo a "Jorge Martinez" y "Adan Garza"
        vendedores_reales_norte = [v for v in vendedores_reales if v in vendedores_norte]

        return vendedores_reales_norte
    
    def obtener_vendedoresReales_bajio(self):
        """Obtiene la lista de vendedores reales de zona Bajio (Cesar Valdes y Alfonso Gasca)"""
        vendedores_reales = self.ventas_reales.obtener_vendedores_ventas_reales()
        
        # Lista de vendedores permitidos en zona Bajio
        vendedores_bajio = ["Cesar Valdes", "Alfonso Gasca"]

        # Filtrar solo a "Cesar Valdes" y "Alfonso Gasca"
        vendedores_reales_bajio = [v for v in vendedores_reales if v in vendedores_bajio]

        return vendedores_reales_bajio
    

    


