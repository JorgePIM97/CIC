# modelo/db_connection.py -> Se corre en local
import pyodbc
import streamlit as st
from dotenv import load_dotenv
import os

class DatabaseConnection:
    def __init__(self):
         
        load_dotenv()

        self.config = {
            "SERVER": os.getenv("SERVER"),
            "DATABASE": os.getenv("DATABASE"),
            "USERNAME": os.getenv("USERNAME"),
            "PASSWORD": os.getenv("PASSWORD"),
            "DRIVER": os.getenv("DRIVER")
        }
    
    '''Cadena de conexion al servidor
    '''
    #@st.cache_resource
    def get_connection(_self):
        """Establece la conexión a la base de datos"""
        conn_str = (
            f"DRIVER={{{_self.config['DRIVER']}}};"
            f"SERVER={_self.config['SERVER']};"
            f"DATABASE={_self.config['DATABASE']};"
            "Trusted_Connection=yes;"
        )
        return pyodbc.connect(conn_str)
    


# # modelo/db_connection.py
# import os
# import pyodbc

# class DatabaseConnection:
#     def __init__(self):
#         self.config = {
#             "SERVER": os.getenv("DB_SERVER", "localhost,1433"),
#             "DATABASE": os.getenv("DB_DATABASE", ""),
#             "USERNAME": os.getenv("DB_USERNAME", ""),
#             "PASSWORD": os.getenv("DB_PASSWORD", ""),
#             "DRIVER": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
#         }

#     def get_connection(self):
#         conn_str = (
#             f"DRIVER={{{self.config['DRIVER']}}};"
#             f"SERVER={self.config['SERVER']};"
#             f"DATABASE={self.config['DATABASE']};"
#             f"UID={self.config['USERNAME']};"
#             f"PWD={self.config['PASSWORD']};"
#         )
#         return pyodbc.connect(conn_str)
