# 🎵 TikTok Scraper

Scraper de perfiles TikTok usando Playwright. Extrae datos del perfil, últimos seguidos y los últimos N videos con sus comentarios, y los exporta en archivos CSV.

---

## 📁 Archivos generados

| Archivo | Contenido |
|---|---|
| `1_perfil.csv` | Info del perfil (seguidores, likes, bio, etc.) |
| `2_ultimos_seguidos.csv` | Lista de usuarios seguidos |
| `3_ultimos_10_videos.csv` | Últimos videos con estadísticas y comentarios |

---

## ⚙️ Configuración previa

### 1. Crear el archivo `.env`

Copia el archivo `.env.example` y renómbralo a `.env`, luego rellena tus datos:

```
SESSION_ID=pega_aqui_tu_sessionid_de_tiktok
USUARIO_OBJETIVO=nombre_usuario_sin_arroba
MAX_VIDEOS=10
```

> ⚠️ **El `.env` está en `.gitignore` y NUNCA se sube a GitHub.**

#### ¿Cómo obtener el `SESSION_ID`?
1. Abre [tiktok.com](https://www.tiktok.com) en Chrome e inicia sesión.
2. Pulsa `F12` → pestaña **Application** → **Cookies** → `https://www.tiktok.com`.
3. Busca la cookie llamada `sessionid` y copia su valor.

---

## 🛠️ Instalación

### Paso 1 — Instalar dependencias Python

```powershell
C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe -m pip install playwright pandas python-dotenv
```

### Paso 2 — Instalar el navegador Chromium para Playwright

```powershell
C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe -m playwright install --force chromium
```

> 💡 Si aparece un cartel naranja de **360 Total Security**, haz clic en **Allow**.

---

## ▶️ Ejecución

### Paso 3 — Ejecutar el scraper

```powershell
C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe scraper_tiktok.py
```

El navegador se abrirá automáticamente, navegará por el perfil y al terminar encontrarás los 3 archivos CSV en la misma carpeta.

---

## 📦 Dependencias

| Librería | Uso |
|---|---|
| `playwright` | Automatización del navegador |
| `pandas` | Generación de archivos CSV |
| `python-dotenv` | Lectura del archivo `.env` |
