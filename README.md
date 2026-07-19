# ComfyUI Colab de Leo

Repo propio para correr **ComfyUI + Z-Image Turbo** en Colab (gratis, GPU T4) y manejarlo desde **comfyweb**. Los modelos viven en tu Google Drive, así que **no se rebajan cada vez**.

## Inicio rápido (cada sesión)

1. Abrí `ComfyUI_Leo.ipynb` en Google Colab.
2. *Entorno de ejecución → Cambiar tipo de entorno → GPU (T4)*.
3. *Entorno de ejecución → Ejecutar todo*.
4. La **1ª vez** baja los modelos a tu Drive (~14 GB, una sola vez). Después arranca en ~2-3 min.
5. Al final imprime una **URL pública** (`https://xxxx.trycloudflare.com`).
6. Pegala en comfyweb → botón *Colab (Cloudflare)* → *Guardar y Conectar*. Listo.

## Modelos (se bajan solos a Drive, fuentes oficiales Apache-2.0)

| Tipo | Archivo | Fuente |
|---|---|---|
| Difusión | `z-image-turbo-fp8-e4m3fn.safetensors` | `T5B/Z-Image-Turbo-FP8` |
| Text encoder | `qwen_3_4b_fp8_mixed.safetensors` | `Comfy-Org/z_image_turbo` |
| VAE | `ae.safetensors` | `Comfy-Org/z_image_turbo` |
| ControlNet | `Z-Image-Turbo-Fun-Controlnet-Union.safetensors` | `alibaba-pai/...` |
| Upscaler | `2x-AnimeSharpV4_RCAN.safetensors` | `Kim2091/2x-AnimeSharpV4` |

**Tus LoRAs:** ponelas a mano en `Drive/MyDrive/ComfyUI-Leo/models/loras/` y van a aparecer en comfyweb.

## Alternativa free: Kaggle (`ComfyUI_Leo_Kaggle.ipynb`)

Si te quedaste sin GPU free en Colab, usá la versión Kaggle (30 h/semana de GPU, gratis).

**Una sola vez:** cuenta Kaggle con **teléfono verificado** (Settings → Phone Verification) para habilitar Internet + GPU.

**Cada sesión:** abrí `ComfyUI_Leo_Kaggle.ipynb` en Kaggle → panel derecho: *Accelerator = GPU T4 x2*, *Internet = ON* → *Run all* → copiá la URL pública → pegala en comfyweb.

**Contras vs Colab:**
- **No monta Google Drive** → por defecto rebaja los modelos cada sesión (pero la red de Kaggle es rápida, pocos minutos). Para evitarlo: guardá los modelos como **Kaggle Dataset** y adjuntalo (ver la última celda del notebook).
- Hay que **verificar el teléfono** (una vez).
- Tope de **30 h/semana** de GPU.

A favor: más horas que abrir otra cuenta Colab, y no depende del límite de tu cuenta Google.

## ¿Tengo que pagar? No.
El free de Colab alcanza. Sus límites: se desconecta si lo dejás inactivo (~90 min), la sesión tiene tope, y la GPU no está 100% garantizada. Si eso te molesta, alternativas:
- **Kaggle Notebooks** — gratis, GPU, 30 hs/semana (plan B si Colab te niega GPU).
- **RunPod / Vast.ai** — centavos/hora, sin abono, disco persistente, endpoint estable (el salto "pro" cuando quieras).

---

## Túnel FIJO con tu dominio (URL que NO cambia)

Por defecto el túnel (`pycloudflared`) da una URL nueva cada vez. Para una URL fija
`https://comfy.leoblumfeld.com` ya está **todo configurado en Cloudflare** (2026-06-28):

- Túnel **`comfy-leo`** (UUID `01c8bdfb-0647-4b3d-82bd-ece0b387178b`) creado por CLI.
- DNS **`comfy.leoblumfeld.com` → CNAME al túnel** ya ruteado.
- Credencial del túnel en la compu de Leo: `~/.cloudflared/01c8bdfb-...json` (**secreto**).
- Verificado de punta a punta el 2026-06-28 (server local → dominio → 200 OK).

### Lo único que falta: el secreto en Colab (una vez)
1. En Colab, panel izquierdo → 🔑 **Secretos** → **+ Agregar secreto nuevo**.
2. Nombre: `CF_TUNNEL_CRED`.
3. Valor: el **contenido del JSON** de credencial (`~/.cloudflared/01c8bdfb-...json`).
   ⚠️ Es secreto: va sólo en Colab Secrets, **nunca al repo**.
4. Activá el toggle de *Acceso del notebook*.

La celda 4 del notebook ya detecta `CF_TUNNEL_CRED`: si está, levanta el túnel fijo
(`cloudflared ... run --credentials-file comfy-leo`) y la URL es siempre
`https://comfy.leoblumfeld.com`. Si NO está, cae al túnel random de respaldo (`pycloudflared`).

> Nota: el túnel `comfy-leo` es **distinto** del túnel `vera` (que rutea `n8n.leoblumfeld.com`).
> No se pisan: cada uno corre en su lado (vera local, comfy-leo en Colab).
>
> Pendiente menor: el túnel fijo todavía **no se probó desde el Colab real** (falta cargar el
> secreto y *Ejecutar todo*). La cadena Cloudflare+DNS sí quedó validada.

---

## Troubleshooting: `FileNotFoundError: extra_model_paths.yaml`

Si la celda 4 tira ese error, la causa real casi siempre es que **la celda 2 no terminó** (se
colgó o se cortó a mitad de camino), así que `/content/ComfyUI` todavía no existe. Pasó el
2026-07-11: un custom node (`ComfyUI_Simple_Qwen3-VL-gguf`) pedía `llama-cpp-python>=0.3.17` sin
wheel precompilado, y el `pip install -r requirements.txt` genérico lo compilaba desde cero
(C++/CUDA) colgando la sesión de Colab.

**Fix aplicado (commit `8a8bfa9`):**
- `llama-cpp-python` se filtra del install genérico de requirements de custom nodes; un
  instalador dedicado busca wheel precompilado (CUDA cu128/cp312/linux) y si no lo encuentra,
  **saltea el nodo Qwen-VL** en vez de compilar y colgar.
- La celda 4 ahora chequea `os.path.isfile('/content/ComfyUI/main.py')` antes de escribir el
  yaml; si falta, tira un `RuntimeError` claro ("volvé a correr la celda 2") en vez del error
  críptico.

**Si vuelve a pasar con un custom node nuevo:** revisar si trae una dependencia pesada sin wheel
(CUDA/C++) y filtrarla igual que se hizo con `llama-cpp-python`, no dejarla pasar por el pip
genérico.

---

## Troubleshooting: `AssertionError: Torch not compiled with CUDA enabled`

Si la celda 4 (o el arranque de `main.py`) tira ese traceback al importar
`comfy.model_management` — pasó el 2026-07-19 — la causa **no es un bug del notebook**: es que
el *entorno de ejecución* de Colab de esa sesión es CPU, no GPU T4. El notebook no fuerza ninguna
build de torch (el `requirements.txt` de ComfyUI pide `torch` sin pin de versión, así que nunca
reinstala el que Colab ya trae preinstalado); si ese torch preinstalado es la build CPU-only, es
porque la VM conectada es CPU.

**Fix (a mano en la UI de Colab, no hay nada para pushear del lado del código):**
1. *Entorno de ejecución → Cambiar tipo de entorno de ejecución → GPU (T4) → Guardar.*
2. *Entorno de ejecución → Ejecutar todo* de nuevo.
3. Si ya tenías T4 elegido y sigue fallando: probablemente se agotó la cuota gratis de GPU de tu
   cuenta por hoy (se resetea con el tiempo). Alternativa sin esperar: `ComfyUI_Leo_Kaggle.ipynb`
   (mismo repo, otra cuota de GPU T4 gratis).

**Mitigación agregada al notebook (2026-07-19):** nueva celda 0 (`Chequeo de GPU`), primera
celda ejecutable del notebook, corre `nvidia-smi` y si falla tira un `RuntimeError` con estas
mismas instrucciones — así el error aparece en segundos en vez de varios minutos después (clonado
+ pip installs) con un traceback críptico.
