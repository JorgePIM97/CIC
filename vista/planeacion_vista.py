# # vista/planeacion_vista.py
# """
# Vista donde se definen botones y tablas para motitorear planeaciones
# """
# import streamlit as st
# from modelo.planeacion_modelo import PlaneacionModelo
# from .seleccion_usuarios.seleccion import SeleccionUsuarios

# class MetasVista:

#     def __init__(self):
#         self.seleccion_usuarios = SeleccionUsuarios()


#     def get_vendedores(self):
#         vendedores = self.seleccion_usuarios.seleccion_privilegios_zona()

#         return vendedores