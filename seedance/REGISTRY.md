# REGISTRY — librería de workflows Seedance

> **Generado desde `registry.json`.** Esa es la fuente de verdad: si editás algo, editalo ahí
> y volvé a generar este archivo. No mantengas las dos cosas a mano.

- Generado: **2026-09-04** · Fuente: comfy.org workflow library - 12 golden descargados sin modificar
- ComfyUI local: **v0.25.0** · GPU local: AMD RX 6800M 12GB (ZLUDA a medias, no confiable)
- GPU remota: Colab T4 via tunel comfy.leoblumfeld.com (CAIDO al momento de escribir esto)

> ⚠️ **NINGUNO PROBADO EN VIVO. Las fichas estan derivadas del grafo JSON, no de corridas reales. Los cost_tier son RELATIVOS entre si, no precios verificados en creditos.**

## Convención de carpetas

- `golden/` — intocable, baseline de referencia
- `experiments/` — pruebas, sufijo _testNNN
- `production/` — renders finales versionados _vNNN

## Índice

| # | id | modelo | res | dur | costo rel. | GPU | estado |
|---|----|--------|-----|-----|-----------|-----|--------|
| 1 | `seedance25_r2v` | Seedance 2.5 | 720p | 5 | BAJO | no | 🟡 sin probar |
| 2 | `seedance25_flf2v` | Seedance 2.5 | 720p | 5 | BAJO | no | 🟡 sin probar |
| 3 | `seedance25_extend` | Seedance 2.5 | 720p | 5 | MEDIO | no | 🔴 BLOQUEADO |
| 4 | `seedance25_edit` | Seedance 2.5 | 720p | 5 | MEDIO | no | 🟡 sin probar |
| 5 | `seedance20_cinematic_prompt_studio` | Seedance 2.0 Fast | 720p | 7 | BAJO-MEDIO | no | 🟡 sin probar |
| 6 | `storyboard_gptimage_seedance20` | Seedance 2.0 | 720p | 15 | ALTO | no | 🟡 sin probar |
| 7 | `product_ad_cinematic_seedance` | Seedance 2.0 | 1080p | 7 | MEDIO-ALTO | no | 🟡 sin probar |
| 8 | `seedance20_depthmotion` | Seedance 2.0 | 720p | 5 | MEDIO (+ tiempo de GPU local) | sí | 🟡 sin probar |
| 9 | `cinematic_annotate_seedance` | Seedance 2.0 | 720p | 7 | MEDIO | no | 🟡 sin probar |
| 10 | `seedance20_r2v_4k` | Seedance 2.0 | 4k | 7 | ALTO | no | 🟡 sin probar |
| 11 | `seedance20_multiframe_flf2v` | Seedance 2.0 | 1080p | 4 | ALTO | no | 🟡 sin probar |
| 12 | `product_ad_video_seedance` | MiniMax H3 (LOCAL, no Seedance) | 1344x768 | 124 frames | SIN COSTO DE API / IMPOSIBLE POR HARDWARE | sí | 🔴 BLOQUEADO |

---

## Fichas

### 1. `seedance25_r2v` — v0.1.0

**Archivo:** `golden/seedance25_r2v_v001.json`  
**Propósito:** Reference-to-Video: una imagen de referencia + prompt -> clip. BASELINE PRIMARIO de R2V.

- **Modelo:** Seedance 2.5 · **Resolución:** 720p · **Ratio:** adaptive · **Duración:** 5 · **Audio:** sí
- **Costo relativo:** BAJO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** ByteDance2ReferenceNode
- **Nodos locales:** LoadImage, SaveVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `image_1` — LoadImage (referencia)
  - `prompt` — texto
  - `seed` — int
- **Salidas:**
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - Con 1 sola referencia el modelo inventa entorno y encuadre: si importa la identidad, anclarla upstream (character sheet) en vez de arreglarla despues.
  - ratio='adaptive' deja que el modelo decida el encuadre; fijarlo si la entrega tiene formato obligatorio.

### 2. `seedance25_flf2v` — v0.1.0

**Archivo:** `golden/seedance25_flf2v_v001.json`  
**Propósito:** First/Last Frame: define composicion de inicio y de fin, el modelo interpola la transicion.

- **Modelo:** Seedance 2.5 · **Resolución:** 720p · **Ratio:** (sin widget en 2.5: lo deriva de los frames) · **Duración:** 5 · **Audio:** sí
- **Costo relativo:** BAJO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** ByteDance2FirstLastFrameNode
- **Nodos locales:** LoadImage x2, SaveVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `first_frame` — LoadImage
  - `last_frame` — LoadImage
  - `prompt` — texto
- **Salidas:**
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - OJO: el schema del nodo CAMBIA segun el modelo elegido. Con 'Seedance 2.5' NO hay model.ratio y aparece model.output_format; con 'Seedance 2.0' SI hay model.ratio. Cambiar el dropdown reordena los widgets.
  - Si los dos frames difieren mucho en encuadre o iluminacion, la interpolacion mete morphing.
  - El prompt del golden referencia los frames como @image1/@image2: esa sintaxis es parte del contrato, no decorativa.

### 3. `seedance25_extend` — v0.1.0

**Archivo:** `golden/seedance25_extend_v001.json`  
**Propósito:** Video extend: continua un plano existente y ademas devuelve el merge del original + la continuacion.

- **Modelo:** Seedance 2.5 · **Resolución:** 720p · **Ratio:** adaptive · **Duración:** 5 · **Audio:** sí
- **Costo relativo:** MEDIO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** > 0.25.0 (VER BLOQUEO)
- **Nodos de API:** ByteDance2ReferenceNodeV2
- **Nodos locales:** LoadVideo, Video Slice, SaveVideo x2, subgrafo 'Merge Videos' (AudioConcat, BatchImagesNode, CreateVideo, ResizeAndPadImage, GetVideoComponents, ComfySwitchNode)
- **Custom nodes:** ninguno
- **Entradas:**
  - `video_1` — LoadVideo -> Video Slice (cola del plano a continuar)
  - `prompt` — que pasa despues
  - `model.task_type` — 'extend' (clave: es lo que activa el modo)
- **Salidas:**
  - `video_continuacion` — SaveVideo
  - `video_merged` — SaveVideo (original + continuacion pegados)
- **Riesgos / modos de falla:**
  - BLOQUEADO HOY: ByteDance2ReferenceNodeV2 NO existe en el ComfyUI local v0.25.0 (comfy_api_nodes/nodes_bytedance.py solo trae ReferenceNode, FirstLastFrameNode y TextToVideoNode). Requiere git pull. Es el UNICO de los 12 que necesita actualizar ComfyUI.
  - model.task_type='extend' es el parametro que distingue este workflow de un R2V comun: si se pisa, deja de extender.
  - El subgrafo Merge Videos hace ResizeAndPadImage: si original y continuacion no comparten resolucion, aparecen barras.

### 4. `seedance25_edit` — v0.1.0

**Archivo:** `golden/seedance25_edit_v001.json`  
**Propósito:** Video edit / v2v: transforma un video existente por instruccion (ej. pasarlo a estilo clay) conservando movimiento y personajes.

- **Modelo:** Seedance 2.5 · **Resolución:** 720p · **Ratio:** adaptive · **Duración:** 5 · **Audio:** sí
- **Costo relativo:** MEDIO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** ByteDance2ReferenceNode
- **Nodos locales:** LoadVideo, Video Slice, SaveVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `video_1` — LoadVideo -> Video Slice (recorta el tramo a editar)
  - `prompt` — instruccion de edicion
- **Salidas:**
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - 'Video Slice' esta antes del nodo de API por una razon: manda solo el tramo. Si se saltea, se sube y procesa video de mas.
  - La duracion del nodo (5s) y la del slice tienen que coincidir, si no se estira o se corta.
  - Deriva de identidad: la transformacion de estilo puede arrastrar los rasgos de los personajes.

### 5. `seedance20_cinematic_prompt_studio` — v0.1.0

**Archivo:** `golden/seedance20_cinematic_prompt_studio_v001.json`  
**Propósito:** Compilador de intencion creativa: Gemini traduce camara/lente/composicion/luz/ritmo a un prompt de Seedance. Es el 'director' del brief.

- **Modelo:** Seedance 2.0 Fast · **Resolución:** 720p · **Ratio:** 21:9 · **Duración:** 7 · **Audio:** sí
- **Costo relativo:** BAJO-MEDIO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** GeminiNode (gemini-3-1-pro), ByteDance2ReferenceNode
- **Nodos locales:** LoadImage, PreviewAny, SaveVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `image_1` — LoadImage (referencia visual)
  - `intent` — brief humano en texto -> Gemini
- **Salidas:**
  - `prompt` — PreviewAny (el prompt compilado, inspeccionable ANTES de gastar)
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - Doble costo por corrida: se paga Gemini Y Seedance. Iterar el prompt mirando PreviewAny antes de dejar que dispare el video.
  - Usa 'Seedance 2.0 Fast', no 2.5: es el candidato natural para previews baratos.
  - Es la pieza reusable del brief (CREATIVE BRIEF INTERFACE): conviene extraerla como modulo y reusarla en los demas.

### 6. `storyboard_gptimage_seedance20` — v0.1.0

**Archivo:** `golden/storyboard_gptimage_seedance20_v001.json`  
**Propósito:** Idea -> storyboard/keyframes con GPT Image -> secuencia animada. Es el patron 'anclar upstream' que pide el brief.

- **Modelo:** Seedance 2.0 · **Resolución:** 720p · **Ratio:** adaptive · **Duración:** 15 · **Audio:** sí
- **Costo relativo:** ALTO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** OpenAIGPTImage1, ByteDance2ReferenceNode
- **Nodos locales:** LoadImage, SaveImage, SaveVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `image_1` — LoadImage
  - `prompt` — descripcion de la secuencia (6 planos / 15s en el golden)
- **Salidas:**
  - `storyboard` — SaveImage 1536x1024
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - 15 segundos es la duracion mas larga de los 12: el mas caro por corrida. Bajar a 5s para test.
  - Requiere credenciales de OpenAI ADEMAS de las de ByteDance.
  - GPT Image en calidad 'medium' 1536x1024: subir la calidad multiplica el costo del paso de storyboard.

### 7. `product_ad_cinematic_seedance` — v0.1.0

**Archivo:** `golden/product_ad_cinematic_seedance_v001.json`  
**Propósito:** Publicidad de producto: 3 referencias + guia de marca -> Gemini 3.1 Pro planifica los planos -> Seedance 1080p.

- **Modelo:** Seedance 2.0 · **Resolución:** 1080p · **Ratio:** adaptive · **Duración:** 7 · **Audio:** sí
- **Costo relativo:** MEDIO-ALTO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** GeminiNodeV2 (Gemini 3.1 Pro), ByteDance2ReferenceNode
- **Nodos locales:** LoadImage x3, PrimitiveStringMultiline x3, PreviewAny, SaveVideo, subgrafo 'Create Prompt' (RegexReplace, SomethingToString), subgrafo 'Selected Prompt' (ComfySwitchNode, StringCompare)
- **Custom nodes:** ninguno
- **Entradas:**
  - `image_1..3` — LoadImage x3 (producto / hero / detalle)
  - `brand_guidance` — PrimitiveStringMultiline x3
- **Salidas:**
  - `prompt` — PreviewAny
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - El subgrafo 'Selected Prompt' usa ComfySwitchNode: hay una rama activa y otras muertas. Verificar cual esta seleccionada antes de disparar, o se paga un video con el prompt equivocado.
  - Consistencia de producto: es el riesgo central de este caso. Las 3 referencias tienen que mostrar el MISMO producto desde angulos distintos, no 3 productos.
  - Gemini 3.1 Pro es el modelo de texto mas caro de los usados en los 12.

### 8. `seedance20_depthmotion` — v0.1.0

**Archivo:** `golden/seedance20_depthmotion_v001.json`  
**Propósito:** Transferencia de movimiento: extrae profundidad/motion de un video fuente y le aplica otra identidad visual.

- **Modelo:** Seedance 2.0 · **Resolución:** 720p · **Ratio:** adaptive · **Duración:** 5 · **Audio:** sí
- **Costo relativo:** MEDIO (+ tiempo de GPU local)
- **Corre en:** Necesita GPU (o CPU lenta): DepthAnythingV2Preprocessor es modelo LOCAL.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** ByteDance2ReferenceNode (dentro del subgrafo 'Seedance 2.0 Depth Dancer')
- **Nodos locales:** LoadImage, VHS_LoadVideo, SaveVideo, DepthAnythingV2Preprocessor, VHS_VideoCombine, VHS_VideoInfo, GetVideoComponents, CreateVideo
- **Custom nodes:** ComfyUI-VideoHelperSuite (INSTALADO), comfyui_controlnet_aux (INSTALADO)
- **Entradas:**
  - `video` — VHS_LoadVideo (fuente de movimiento)
  - `image_1` — LoadImage (identidad visual destino)
- **Salidas:**
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - UNICO de los 12 que mezcla local + API: si el Colab esta apagado hay que correr Depth Anything V2 en CPU (lento, pero funciona).
  - El checkpoint de Depth Anything V2 hay que BAJARLO: los custom nodes estan instalados pero el peso NO se verifico en disco (models/ no existe localmente).
  - Deriva geometrica: la profundidad del video fuente puede pelearse con la identidad destino si las siluetas no coinciden.

### 9. `cinematic_annotate_seedance` — v0.1.0

**Archivo:** `golden/cinematic_annotate_seedance_v001.json`  
**Propósito:** Anotacion cinematografica: se marca una imagen a mano (flechas, cajas, etiquetas) y Gemini lee esas marcas como direccion de camara y movimiento.

- **Modelo:** Seedance 2.0 · **Resolución:** 720p · **Ratio:** 21:9 · **Duración:** 7 · **Audio:** sí
- **Costo relativo:** MEDIO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** GeminiNode (gemini-3-1-flash-lite), GeminiImage2Node (Nano Banana 2 / Gemini 3.1 Flash Image), ByteDance2ReferenceNode
- **Nodos locales:** LoadImage, PreviewImage, PreviewAny, SaveVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `image_1` — LoadImage (frame limpio con marcas encima)
- **Salidas:**
  - `prompt` — PreviewAny
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - Triple costo por corrida: 2 llamadas a Gemini + Seedance.
  - El system_prompt le ordena explicitamente que las marcas NO aparezcan en el video. Si se toca ese texto, las flechas pueden terminar renderizadas.
  - Depende de que las anotaciones sean legibles: marcas ambiguas producen direccion de camara ambigua.

### 10. `seedance20_r2v_4k` — v0.1.0

**Archivo:** `golden/seedance20_r2v_4k_v001.json`  
**Propósito:** R2V de alta calidad con hasta 4 imagenes de referencia. Baseline de calidad, no de iteracion.

- **Modelo:** Seedance 2.0 · **Resolución:** 4k · **Ratio:** 1:1 · **Duración:** 7 · **Audio:** sí
- **Costo relativo:** ALTO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** ByteDance2ReferenceNode
- **Nodos locales:** LoadImage x4, SaveVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `image_1..image_4` — LoadImage x4 (referencias multiples)
  - `prompt` — texto
- **Salidas:**
  - `video` — SaveVideo mp4
- **Riesgos / modos de falla:**
  - 4k x 7s = el tier mas caro de los R2V. NUNCA iterar aca: probar en seedance25_r2v a 720p y recien despues subir.
  - ratio 1:1 es un default del golden, no una restriccion del modelo.
  - Las 4 referencias solo suman si son coherentes entre si; referencias contradictorias degradan el resultado.

### 11. `seedance20_multiframe_flf2v` — v0.1.0

**Archivo:** `golden/seedance20_multiframe_flf2v_v001.json`  
**Propósito:** Stitch multiframe: 5 nodos FLF2V encadenados con 6 imagenes -> 5 clips + concatenacion. Secuencia larga con control de composicion en cada corte.

- **Modelo:** Seedance 2.0 · **Resolución:** 1080p · **Ratio:** 16:9 · **Duración:** 4 · **Audio:** no
- **Costo relativo:** ALTO
- **Corre en:** CPU (cualquiera). Nodos de API.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** ByteDance2FirstLastFrameNode x5
- **Nodos locales:** LoadImage x6, SaveVideo x6, ImageBatch x4, GetVideoComponents x5, CreateVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `image_1..image_6` — LoadImage x6 (los 6 puntos de anclaje de la secuencia)
- **Salidas:**
  - `clips` — SaveVideo x5
  - `secuencia` — SaveVideo (concatenado)
- **Riesgos / modos de falla:**
  - 5 llamadas a la API por corrida: el mayor costo por click de los 12. Un fallo en el clip 5 igual te cobro los 5.
  - Probar UN solo tramo (bypasseando los otros 4) antes de correr la cadena entera.
  - audio=False en los 5: la secuencia sale muda por diseno, el audio se pega despues.

### 12. `product_ad_video_seedance` — v0.1.0

**Archivo:** `golden/product_ad_video_seedance_v001.json`  
**Propósito:** Publicidad de producto con hero/environment + producto/detalle + guia de marca. OJO: en el golden el motor de video NO es Seedance sino MiniMax H3 LOCAL.

- **Modelo:** MiniMax H3 (LOCAL, no Seedance) · **Resolución:** 1344x768 · **Ratio:** - · **Duración:** 124 frames · **Audio:** sí
- **Costo relativo:** SIN COSTO DE API / IMPOSIBLE POR HARDWARE
- **Corre en:** BLOQUEADO en este hardware. Difusion de video local a 1344x768 x124 frames.
- **ComfyUI mínimo:** 0.25.0
- **Nodos de API:** GeminiNodeV2 (Gemini 3.1 Pro)
- **Nodos locales:** LoadImage x3, PrimitiveStringMultiline x3, SaveVideo, subgrafo 'Reference to Video (Minimax H3)': UNETLoader, CLIPLoader, VAELoader, SamplerCustomAdvanced, MiniMaxH3ReferenceToVideo, BasicGuider, BasicScheduler, KSamplerSelect, RandomNoise, VAEDecode, VAEDecodeAudio, ResolutionSelector, CreateVideo
- **Custom nodes:** ninguno
- **Entradas:**
  - `image_1..3` — LoadImage x3
  - `brand_guidance` — PrimitiveStringMultiline x3
- **Salidas:**
  - `video` — SaveVideo
- **Riesgos / modos de falla:**
  - NO CORRE HOY. El subgrafo es difusion de video local completa: pide UNET + CLIP + VAE de MiniMax H3 a 1344x768 x124 frames. No entra en la T4 del Colab ni en la RX 6800M.
  - Para usarlo hay que AMPUTAR el subgrafo MiniMax y reemplazarlo por un ByteDance2ReferenceNode: ahi queda equivalente a product_ad_cinematic_seedance.
  - Ninguno de los pesos de MiniMax H3 esta en disco.
