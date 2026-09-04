# -*- coding: utf-8 -*-
"""
leo_api_key_inject — inyecta la API key de comfy.org en cada prompt.

POR QUE EXISTE
--------------
Los nodos de API de comfy.org (ByteDance/Seedance, Gemini, OpenAI) NO leen la key
de ninguna variable de entorno ni flag de CLI: la reciben SOLO por el campo
`extra_data.api_key_comfy_org` de cada request a `/prompt` (ver `execution.py`,
donde `get_input_data()` hace `extra_data.get("api_key_comfy_org", None)`).

En la interfaz web eso lo hace el frontend solo, con la sesion del navegador. Pero
cualquier cliente que encole por API (curl, un script, un agente) no tiene esa
sesion, y el nodo falla con:

    Unauthorized: Please login first to use this node.

Este parche resuelve exactamente eso: si la variable de entorno COMFY_ORG_API_KEY
esta presente, la inyecta en `extra_data` de cada ejecucion que no traiga una
propia. Los requests que SI traen su key (los del navegador) no se tocan.

SEGURIDAD
---------
- La key se lee del entorno del proceso, que en el Colab viene de Colab Secrets.
- NUNCA se imprime, ni se loguea, ni se guarda en disco, ni entra al grafo.
- Si la variable no esta, el parche no hace nada y todo sigue funcionando igual
  desde el navegador.

Es un custom node solo por el vehiculo de carga (ComfyUI importa `custom_nodes/`
al arrancar); no registra ningun nodo.
"""

import os
import logging

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

_TAG = "[leo_api_key_inject]"


def _install():
    key = os.environ.get("COMFY_ORG_API_KEY", "").strip()
    if not key:
        logging.info(
            f"{_TAG} Sin COMFY_ORG_API_KEY en el entorno: no se inyecta nada. "
            f"La interfaz web sigue funcionando normal; los requests por API van a "
            f"fallar con 'Unauthorized' hasta que cargues el secreto."
        )
        return

    try:
        import execution
    except Exception as e:
        logging.warning(f"{_TAG} No se pudo importar 'execution': {e}")
        return

    PE = getattr(execution, "PromptExecutor", None)
    if PE is None:
        logging.warning(f"{_TAG} No se encontro execution.PromptExecutor; ComfyUI cambio de estructura.")
        return

    if getattr(PE, "_leo_api_key_patched", False):
        return

    original = getattr(PE, "execute_async", None)
    if original is None:
        logging.warning(f"{_TAG} No se encontro PromptExecutor.execute_async; no se parchea.")
        return

    async def patched_execute_async(self, prompt, prompt_id, extra_data=None, execute_outputs=[]):
        if extra_data is None:
            extra_data = {}
        # Solo completar si el cliente no mando la suya (el navegador manda la propia).
        if not extra_data.get("api_key_comfy_org") and not extra_data.get("auth_token_comfy_org"):
            extra_data["api_key_comfy_org"] = key
        return await original(self, prompt, prompt_id, extra_data, execute_outputs)

    PE.execute_async = patched_execute_async
    PE._leo_api_key_patched = True
    # Se confirma que quedo activo, sin revelar el valor ni su longitud exacta.
    logging.info(f"{_TAG} Activo: los prompts sin key propia se autentican con COMFY_ORG_API_KEY.")


_install()
