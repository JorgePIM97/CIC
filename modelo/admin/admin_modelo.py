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

FOTOS_VENDEDORES_PATH = os.getenv(
    "FOTOS_VENDEDORES",
    r"C:\Users\Administrador\Documents\ReportesCIC\FotoVendedores"
)

_JSON_DEFAULT = {
    "vendedores_force": [],
    "vendedores_exceles": [],
    "vendedores_norte_exceles": [],
    "vendedores_bajio_exceles": [],
    "vendedores_norte_force": [],
    "vendedores_bajio_force": [],
    "fotos_vendedores": {}
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

    # def _leer_json(self) -> dict:
    #     """Lee el JSON de vendedores activos; crea el archivo si no existe."""
    #     if not os.path.exists(VENDEDORES_JSON_PATH):
    #         self._escribir_json(_JSON_DEFAULT.copy())
    #     with open(VENDEDORES_JSON_PATH, "r", encoding="utf-8") as f:
    #         return json.load(f)

    def _leer_json(self) -> dict:
        """
        Lee el JSON de configuración de vendedores.

        Si el archivo no existe, lo crea.
        Si aparecen nuevas claves en _JSON_DEFAULT, las agrega
        automáticamente sin eliminar la configuración existente.
        """

        if not os.path.exists(VENDEDORES_JSON_PATH):
            self._escribir_json(_JSON_DEFAULT.copy())

        with open(VENDEDORES_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        hubo_cambios = False

        for clave, valor_default in _JSON_DEFAULT.items():

            if clave not in data:

                if isinstance(valor_default, dict):
                    data[clave] = valor_default.copy()

                elif isinstance(valor_default, list):
                    data[clave] = valor_default.copy()

                else:
                    data[clave] = valor_default

                hubo_cambios = True

        if hubo_cambios:
            self._escribir_json(data)

        return data

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


    # ------------------------------------------------------------------ #
    #  CRUD fotografías de vendedores                                   #
    # ------------------------------------------------------------------ #

    def guardar_foto_vendedor(
        self,
        vendedor: str,
        nombre_archivo: str,
        contenido: bytes
    ) -> bool:
        """
        Guarda o reemplaza la fotografía de un vendedor.

        La imagen se almacena físicamente en FOTOS_VENDEDORES_PATH
        y en vendedores_activos.json únicamente se guarda la relación:
            vendedor -> nombre_archivo
        """

        try:
            # Crear carpeta si no existe
            os.makedirs(FOTOS_VENDEDORES_PATH, exist_ok=True)

            # Validar extensión
            _, extension = os.path.splitext(nombre_archivo)
            extension = extension.lower()

            extensiones_permitidas = [".jpg", ".jpeg", ".png"]

            if extension not in extensiones_permitidas:
                st.error(
                    "Formato de imagen no permitido. "
                    "Utiliza JPG, JPEG o PNG."
                )
                return False

            # Generar nombre controlado por CIC
            nombre_seguro = (
                vendedor.strip()
                .lower()
                .replace(" ", "_")
            )

            nombre_final = f"{nombre_seguro}{extension}"

            ruta_final = os.path.join(
                FOTOS_VENDEDORES_PATH,
                nombre_final
            )

            # Obtener configuración actual
            data = self._leer_json()

            fotos = data.setdefault("fotos_vendedores", {})

            # ----------------------------------------------------------
            # Si ya tenía fotografía y cambia la extensión,
            # eliminar el archivo anterior.
            # Ejemplo:
            # cesar_valdes.jpeg -> cesar_valdes.png
            # ----------------------------------------------------------
            archivo_anterior = fotos.get(vendedor)

            if archivo_anterior and archivo_anterior != nombre_final:

                ruta_anterior = os.path.join(
                    FOTOS_VENDEDORES_PATH,
                    archivo_anterior
                )

                if os.path.exists(ruta_anterior):
                    os.remove(ruta_anterior)

            # Guardar imagen
            with open(ruta_final, "wb") as f:
                f.write(contenido)

            # Registrar relación vendedor -> fotografía
            fotos[vendedor] = nombre_final

            data["fotos_vendedores"] = fotos

            self._escribir_json(data)

            return True

        except Exception as e:
            st.error(
                f"Error al guardar fotografía de '{vendedor}': {e}"
            )
            return False


    def obtener_foto_vendedor(self, vendedor: str):
        """
        Devuelve la ruta absoluta de la fotografía del vendedor.

        Si el vendedor no tiene fotografía registrada o el archivo
        físico no existe, devuelve None.
        """

        try:
            data = self._leer_json()

            fotos = data.get("fotos_vendedores", {})

            nombre_archivo = fotos.get(vendedor)

            if not nombre_archivo:
                return None

            ruta_foto = os.path.join(
                FOTOS_VENDEDORES_PATH,
                nombre_archivo
            )

            if not os.path.exists(ruta_foto):
                return None

            return ruta_foto

        except Exception as e:
            st.error(
                f"Error al obtener fotografía de '{vendedor}': {e}"
            )
            return None


    def eliminar_foto_vendedor(self, vendedor: str) -> bool:
        """
        Elimina la fotografía física del vendedor y su referencia
        dentro de vendedores_activos.json.
        """

        try:
            data = self._leer_json()

            fotos = data.get("fotos_vendedores", {})

            nombre_archivo = fotos.get(vendedor)

            if not nombre_archivo:
                return False

            ruta_foto = os.path.join(
                FOTOS_VENDEDORES_PATH,
                nombre_archivo
            )

            # Eliminar archivo físico
            if os.path.exists(ruta_foto):
                os.remove(ruta_foto)

            # Eliminar referencia del JSON
            del fotos[vendedor]

            data["fotos_vendedores"] = fotos

            self._escribir_json(data)

            return True

        except Exception as e:
            st.error(
                f"Error al eliminar fotografía de '{vendedor}': {e}"
            )
            return False