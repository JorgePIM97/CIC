# C:\CIC_WebApp\modelo\admin\admin_modelo.py
import json
import os
import pandas as pd
import streamlit as st
from ..db_connection import DatabaseConnection

# Ruta del archivo JSON donde se guardan los vendedores activos
VENDEDORES_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "vendedores_activos.json"
)

_JSON_DEFAULT = {
    "vendedores_force": [],
    "vendedores_exceles": [],
    "vendedores_norte_exceles": [],
    "vendedores_bajio_exceles": [],
    "vendedores_norte_force": [],
    "vendedores_bajio_force": []
}


class AdminModelo:
    def __init__(self):
        self.db = DatabaseConnection()

    # ------------------------------------------------------------------ #
    #  Consultas BD                                                        #
    # ------------------------------------------------------------------ #

    def obtener_vendedores_exceles(self) -> list[str]:
        """Devuelve los nombres únicos de RepresentanteDeVentas (exceles)."""
        query = """
        SELECT DISTINCT
            CASE
                WHEN RepresentanteDeVentas LIKE 'Piso%' THEN 'Piso'
                ELSE RepresentanteDeVentas
            END AS vendedores_excel
        FROM dev_Detalle_Corregida;
        """
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return sorted(df["vendedores_excel"].dropna().tolist())
        except Exception as e:
            st.error(f"Error al obtener vendedores (exceles): {e}")
            return []

    def obtener_vendedores_force(self) -> list[str]:
        """Devuelve los SalesRepId_Value únicos de usuarios en Force Manager."""
        query = """
        SELECT DISTINCT
            a.SalesRepId_Value AS force_vendedores
        FROM [ForceSyncDB_Worker].[dbo].[Activities] a
        INNER JOIN [ForceSyncDB_Worker].[dbo].[Users] u
            ON u.Id = a.SalesRepId_Id;
        """
        try:
            df = pd.read_sql_query(query, self.db.get_connection())
            return sorted(df["force_vendedores"].dropna().tolist())
        except Exception as e:
            st.error(f"Error al obtener vendedores (Force): {e}")
            return []

    # ------------------------------------------------------------------ #
    #  JSON helpers                                                        #
    # ------------------------------------------------------------------ #

    def _leer_json(self) -> dict:
        """Lee el JSON de vendedores activos; crea el archivo si no existe."""
        if not os.path.exists(VENDEDORES_JSON_PATH):
            self._escribir_json(_JSON_DEFAULT.copy())
        with open(VENDEDORES_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _escribir_json(self, data: dict) -> None:
        """Sobreescribe el JSON de vendedores activos."""
        os.makedirs(os.path.dirname(VENDEDORES_JSON_PATH), exist_ok=True)
        with open(VENDEDORES_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------ #
    #  CRUD vendedores guardados general                                 #
    # ------------------------------------------------------------------ #

    def obtener_guardados(self) -> dict:
        """Devuelve el dict completo con las dos listas guardadas."""
        return self._leer_json()

    def agregar_vendedor_force(self, nombre: str) -> bool:
        """
        Agrega un vendedor Force al JSON si no existe ya.
        Devuelve True si se agregó, False si ya estaba.
        """
        data = self._leer_json()
        if nombre not in data["vendedores_force"]:
            data["vendedores_force"].append(nombre)
            data["vendedores_force"].sort()
            self._escribir_json(data)
            return True
        return False

    def agregar_vendedor_excel(self, nombre: str) -> bool:
        """
        Agrega un vendedor Excel al JSON si no existe ya.
        Devuelve True si se agregó, False si ya estaba.
        """
        data = self._leer_json()
        if nombre not in data["vendedores_exceles"]:
            data["vendedores_exceles"].append(nombre)
            data["vendedores_exceles"].sort()
            self._escribir_json(data)
            return True
        return False

    def eliminar_vendedor_force(self, nombre: str) -> None:
        """Elimina un vendedor Force del JSON."""
        data = self._leer_json()
        data["vendedores_force"] = [v for v in data["vendedores_force"] if v != nombre]
        self._escribir_json(data)

    def eliminar_vendedor_excel(self, nombre: str) -> None:
        """Elimina un vendedor Excel del JSON."""
        data = self._leer_json()
        data["vendedores_exceles"] = [v for v in data["vendedores_exceles"] if v != nombre]
        self._escribir_json(data)

    # ------------------------------------------------------------------ #
    #  CRUD vendedores guardados norte                                   #
    # ------------------------------------------------------------------ #

    def agregar_vendedor_norte_force(self, nombre: str) -> bool:
        """
        Agrega un vendedor Force al JSON si no existe ya.
        Devuelve True si se agregó, False si ya estaba.
        """
        data = self._leer_json()
        if nombre not in data["vendedores_norte_force"]:
            data["vendedores_norte_force"].append(nombre)
            data["vendedores_norte_force"].sort()
            self._escribir_json(data)
            return True
        return False

    def agregar_vendedor_norte_excel(self, nombre: str) -> bool:
        """
        Agrega un vendedor Excel al JSON si no existe ya.
        Devuelve True si se agregó, False si ya estaba.
        """
        data = self._leer_json()
        if nombre not in data["vendedores_norte_exceles"]:
            data["vendedores_norte_exceles"].append(nombre)
            data["vendedores_norte_exceles"].sort()
            self._escribir_json(data)
            return True
        return False

    def eliminar_vendedor_norte_force(self, nombre: str) -> None:
        """Elimina un vendedor Force del JSON."""
        data = self._leer_json()
        data["vendedores_norte_force"] = [v for v in data["vendedores_norte_force"] if v != nombre]
        self._escribir_json(data)

    def eliminar_vendedor_norte_excel(self, nombre: str) -> None:
        """Elimina un vendedor Excel del JSON."""
        data = self._leer_json()
        data["vendedores_norte_exceles"] = [v for v in data["vendedores_norte_exceles"] if v != nombre]
        self._escribir_json(data)

    # ------------------------------------------------------------------ #
    #  CRUD vendedores guardados bajio                                   #
    # ------------------------------------------------------------------ #

    def agregar_vendedor_bajio_force(self, nombre: str) -> bool:
        """
        Agrega un vendedor Force al JSON si no existe ya.
        Devuelve True si se agregó, False si ya estaba.
        """
        data = self._leer_json()
        if nombre not in data["vendedores_bajio_force"]:
            data["vendedores_bajio_force"].append(nombre)
            data["vendedores_bajio_force"].sort()
            self._escribir_json(data)
            return True
        return False

    def agregar_vendedor_bajio_excel(self, nombre: str) -> bool:
        """
        Agrega un vendedor Excel al JSON si no existe ya.
        Devuelve True si se agregó, False si ya estaba.
        """
        data = self._leer_json()
        if nombre not in data["vendedores_bajio_exceles"]:
            data["vendedores_bajio_exceles"].append(nombre)
            data["vendedores_bajio_exceles"].sort()
            self._escribir_json(data)
            return True
        return False

    def eliminar_vendedor_bajio_force(self, nombre: str) -> None:
        """Elimina un vendedor Force del JSON."""
        data = self._leer_json()
        data["vendedores_bajio_force"] = [v for v in data["vendedores_bajio_force"] if v != nombre]
        self._escribir_json(data)

    def eliminar_vendedor_bajio_excel(self, nombre: str) -> None:
        """Elimina un vendedor Excel del JSON."""
        data = self._leer_json()
        data["vendedores_bajio_exceles"] = [v for v in data["vendedores_bajio_exceles"] if v != nombre]
        self._escribir_json(data)