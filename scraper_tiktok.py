import asyncio
import json
import os
import pandas as pd
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# ================= CONFIGURACIÓN (desde .env) =================
load_dotenv()
USUARIO_OBJETIVO = os.getenv("USUARIO_OBJETIVO", "usuario_aqui")
SESSION_ID       = os.getenv("SESSION_ID", "")
MAX_VIDEOS       = int(os.getenv("MAX_VIDEOS", 10))
# ==============================================================

async def scrapear_tiktok():
    perfil_info = {}
    videos_raw = []
    comentarios_por_video = {}
    ultimos_seguidos = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        if SESSION_ID and SESSION_ID != "TU_SESSION_ID_AQUI":
            await context.add_cookies([{
                "name": "sessionid",
                "value": SESSION_ID,
                "domain": ".tiktok.com",
                "path": "/"
            }])

        page = await context.new_page()

        async def interceptar_respuestas(response):
            url = response.url
            try:
                if "/api/post/item_list/" in url and response.status == 200:
                    data = await response.json()
                    if "itemList" in data:
                        videos_raw.extend(data["itemList"])

                elif "/api/comment/list/" in url and response.status == 200:
                    data = await response.json()
                    if "comments" in data and data["comments"]:
                        for c in data["comments"]:
                            vid_id = c.get("aweme_id")
                            texto = c.get("text")
                            autor = c.get("user", {}).get("unique_id")
                            if vid_id not in comentarios_por_video:
                                comentarios_por_video[vid_id] = []
                            comentarios_por_video[vid_id].append(f"@{autor}: {texto}")

                elif "/api/user/list/" in url and response.status == 200:
                    data = await response.json()
                    if "userList" in data:
                        for u in data["userList"]:
                            user_data = u.get("user", {})
                            ultimos_seguidos.append({
                                "usuario": user_data.get("uniqueId"),
                                "nombre": user_data.get("nickname"),
                                "biografia": user_data.get("signature", "").replace("\n", " ")
                            })
            except Exception:
                pass

        page.on("response", interceptar_respuestas)

        print(f"[*] Entrando al perfil de @{USUARIO_OBJETIVO}...")
        await page.goto(f"https://www.tiktok.com/@{USUARIO_OBJETIVO}", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        # Línea corregida sin el espacio extra:
        json_script = await page.query_selector('script#__UNIVERSAL_DATA_FOR_REHYDRATION__')
        if json_script:
            raw_json = await json_script.inner_text()
            data_hidratacion = json.loads(raw_json)
            user_detail = data_hidratacion.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {}).get("userInfo", {})
            
            user = user_detail.get("user", {})
            stats = user_detail.get("stats", {})

            perfil_info = {
                "usuario": user.get("uniqueId"),
                "nombre": user.get("nickname"),
                "biografia": user.get("signature", "").replace("\n", " "),
                "seguidores": stats.get("followerCount"),
                "seguidos": stats.get("followingCount"),
                "likes_totales": stats.get("heartCount"),
                "videos_totales": stats.get("videoCount")
            }
            print("\n=== DATOS DEL PERFIL ===")
            for k, v in perfil_info.items():
                print(f"{k.capitalize()}: {v}")

        print("\n[*] Intentando obtener los últimos seguidos...")
        try:
            boton_seguidos = await page.query_selector('[data-e2e="following-count"]')
            if boton_seguidos:
                await boton_seguidos.click()
                await page.wait_for_timeout(4000)
                await page.keyboard.press("Escape")
        except Exception as e:
            print("No se pudo abrir la lista de seguidos (puede ser privada):", e)

        await page.mouse.wheel(0, 1500)
        await page.wait_for_timeout(3000)

        videos_procesados = []
        vistos = set()
        for v in videos_raw:
            if v["id"] not in vistos and len(videos_procesados) < MAX_VIDEOS:
                vistos.add(v["id"])
                videos_procesados.append(v)

        print(f"\n[*] Analizando los últimos {len(videos_procesados)} videos y sus comentarios...")
        resultados_videos = []

        for idx, v in enumerate(videos_procesados, 1):
            vid_id = v.get("id")
            stats_v = v.get("stats", {})
            desc = v.get("desc", "")

            url_video = f"https://www.tiktok.com/@{USUARIO_OBJETIVO}/video/{vid_id}"
            print(f"  -> ({idx}/{len(videos_procesados)}) Extrayendo video {vid_id}...")
            await page.goto(url_video, wait_until="domcontentloaded")
            await page.wait_for_timeout(4000)

            lista_comentarios = comentarios_por_video.get(vid_id, [])

            resultados_videos.append({
                "id_video": vid_id,
                "url": url_video,
                "descripcion": desc,
                "vistas": stats_v.get("playCount", 0),
                "likes": stats_v.get("diggCount", 0),
                "comentarios_total": stats_v.get("commentCount", 0),
                "guardados": stats_v.get("collectCount", 0),
                "compartidos": stats_v.get("shareCount", 0),
                "muestra_comentarios": " | ".join(lista_comentarios[:15])
            })

        await browser.close()

        pd.DataFrame([perfil_info]).to_csv("1_perfil.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(ultimos_seguidos).to_csv("2_ultimos_seguidos.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(resultados_videos).to_csv("3_ultimos_10_videos.csv", index=False, encoding="utf-8-sig")
        print("\n[✓] ¡Proceso terminado! Archivos CSV generados en tu carpeta actual.")

if __name__ == "__main__":
    asyncio.run(scrapear_tiktok())