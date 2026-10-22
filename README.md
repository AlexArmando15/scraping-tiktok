# 🎵 TikTok Scraper + Análisis Big Five con IA

Scraper de perfiles TikTok usando Playwright. Extrae datos del perfil, últimos seguidos y los últimos N videos con sus comentarios, los exporta en archivos CSV y luego realiza un **análisis de personalidad Big Five (OCEAN)** de la audiencia usando la API de Groq (IA).

---

## 📁 Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `scraper_tiktok.py` | Script principal: extrae datos del perfil y comentarios |
| `analisis_bigfive.py` | Script de IA: analiza los comentarios con el modelo Big Five |

## 📄 Archivos generados

| Archivo | Contenido |
|---|---|
| `1_perfil.csv` | Info del perfil (seguidores, likes, bio, etc.) |
| `2_ultimos_seguidos.csv` | Lista de usuarios seguidos recientemente |
| `3_ultimos_10_videos.csv` | Últimos videos con estadísticas |
| `4_comentarios_detallados.csv` | Comentarios extraídos de cada video |
| `5_reporte_bigfive.md` | Reporte final del análisis Big Five generado por IA |

---

## ⚙️ Configuración previa

### 1. Crear el archivo `.env`

Copia el archivo `.env.example` y renómbralo a `.env`, luego rellena todos tus datos:

```env
SESSION_ID=pega_aqui_tu_sessionid_de_tiktok
USUARIO_OBJETIVO=nombre_usuario_sin_arroba
MAX_VIDEOS=10
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ **El `.env` está en `.gitignore` y NUNCA se sube a GitHub.**

#### ¿Cómo obtener el `SESSION_ID`?
1. Abre [tiktok.com](https://www.tiktok.com) en Chrome e inicia sesión.
2. Pulsa `F12` → pestaña **Application** → **Cookies** → `https://www.tiktok.com`.
3. Busca la cookie llamada `sessionid` y copia su valor.

#### ¿Cómo obtener la `GROQ_API_KEY`?
1. Crea una cuenta gratuita en [console.groq.com](https://console.groq.com).
2. Ve a **API Keys** → **Create API Key**.
3. Copia la clave (empieza por `gsk_...`) y pégala en tu `.env`.

---

## 🛠️ Instalación

### Paso 1 — Instalar dependencias Python

Instala todas las librerías necesarias para ambos scripts de una sola vez:

```powershell
C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe -m pip install playwright pandas python-dotenv groq
```

### Paso 2 — Instalar el navegador Chromium para Playwright

```powershell
C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe -m playwright install --force chromium
```

> 💡 Si aparece un cartel naranja de **360 Total Security**, haz clic en **Allow**.

---

## ▶️ Ejecución

Sigue los pasos en orden. El segundo script depende de los CSV generados por el primero.

### Paso 3 — Ejecutar el scraper (extrae datos de TikTok)

```powershell
C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe scraper_tiktok.py
```

El navegador se abrirá automáticamente, navegará por el perfil y al terminar encontrarás los archivos CSV (`1_perfil.csv`, `2_ultimos_seguidos.csv`, `3_ultimos_10_videos.csv`, `4_comentarios_detallados.csv`) en la misma carpeta.

### Paso 4 — Ejecutar el análisis Big Five con IA

> ⚠️ **Requisito:** el `Paso 3` debe haberse ejecutado primero para que exista el archivo `4_comentarios_detallados.csv`.

```powershell
C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe analisis_bigfive.py
```

El script leerá los comentarios del CSV, los enviará a la API de Groq y mostrará el análisis en tiempo real (streaming). Al finalizar, guardará el reporte completo en `5_reporte_bigfive.md`.

---

## 📦 Dependencias

| Librería | Uso |
|---|---|
| `playwright` | Automatización del navegador para el scraper |
| `pandas` | Lectura y generación de archivos CSV |
| `python-dotenv` | Lectura del archivo `.env` |
| `groq` | Cliente oficial de la API de Groq para el análisis con IA |

---

## ▶️ Video de ejecución 


https://github.com/user-attachments/assets/7f24db35-a5c3-4f9e-9860-37816f1675c0



