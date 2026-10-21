import asyncio
import json
import os
import pandas as pd
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# ================= CONFIGURACIÓN (desde .env) =================
load_dotenv()
USUARIO_OBJETIVO = os.getenv("USUARIO_OBJETIVO", "alexarmando15")
SESSION_ID       = os.getenv("SESSION_ID", "")
MAX_VIDEOS       = int(os.getenv("MAX_VIDEOS", 10))
# ==============================================================

async def scrapear_tiktok():
    perfil_info = {}
    videos_raw = []
    comentarios_por_video = {}
    ultimos_seguidos = []

    async with async_playwright() as p:
        # Args adicionales para ocultar que el navegador es controlado por automatización
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        if SESSION_ID and SESSION_ID != "TU_SESSION_ID_AQUI":
            await context.add_cookies([
                {
                    "name": "sessionid",
                    "value": SESSION_ID,
                    "domain": ".tiktok.com",
                    "path": "/"
                },
                {
                    "name": "sessionid_ss",
                    "value": SESSION_ID,
                    "domain": ".tiktok.com",
                    "path": "/"
                }
            ])

        page = await context.new_page()

        # Interceptor de respuestas de la API interna de TikTok
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
                            vid_id = str(c.get("aweme_id", ""))
                            texto = c.get("text", "").strip()
                            autor = c.get("user", {}).get("unique_id") or c.get("user", {}).get("nickname", "usuario")
                            likes_com = c.get("digg_count", 0)
                            if vid_id:
                                if vid_id not in comentarios_por_video:
                                    comentarios_por_video[vid_id] = []
                                entrada = {"autor": autor, "comentario": texto, "likes": likes_com}
                                if entrada not in comentarios_por_video[vid_id]:
                                    comentarios_por_video[vid_id].append(entrada)

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
                await page.wait_for_timeout(1000)
        except Exception as e:
            print("No se pudo abrir la lista de seguidos (puede ser privada):", e)

        # Hacer scroll ligero para asegurar que carguen los primeros 10 videos en la cuadrícula
        await page.mouse.wheel(0, 1200)
        await page.wait_for_timeout(3000)
        await page.mouse.wheel(0, -1200)
        await page.wait_for_timeout(1500)

        videos_procesados = []
        vistos = set()
        for v in videos_raw:
            if v["id"] not in vistos and len(videos_procesados) < MAX_VIDEOS:
                vistos.add(v["id"])
                videos_procesados.append(v)

        print(f"\n[*] Analizando los últimos {len(videos_procesados)} videos y abriendo el visor para extraer comentarios...")

        # En lugar de usar page.goto() 10 veces (que da error HTTP), hacemos clic en el primer video de la cuadrícula
        # y navegamos hacia abajo con la tecla ArrowDown como un usuario real
        try:
            primer_item = await page.query_selector('[data-e2e="user-post-item"] a')
            if primer_item:
                await primer_item.click()
                await page.wait_for_timeout(3500)

                for idx in range(len(videos_procesados)):
                    v = videos_procesados[idx]
                    vid_id = str(v.get("id"))
                    total_com = v.get("stats", {}).get("commentCount", 0)
                    print(f"  -> ({idx+1}/{len(videos_procesados)}) Revisando publicación {vid_id} ({total_com} comentarios reportados)...")

                    if total_com > 0:
                        # Esperar a que la API suelte los comentarios de la vista lateral
                        await page.wait_for_timeout(2500)

                        # Respaldo DOM: Si la API no los capturó aún, leemos los elementos de comentario en pantalla
                        if not comentarios_por_video.get(vid_id):
                            elementos_com = await page.query_selector_all('[data-e2e="comment-level-1"]')
                            for el in elementos_com:
                                texto_dom = (await el.inner_text()).strip().replace("\n", " ")
                                if texto_dom:
                                    if vid_id not in comentarios_por_video:
                                        comentarios_por_video[vid_id] = []
                                    comentarios_por_video[vid_id].append({
                                        "autor": "usuario_tiktok",
                                        "comentario": texto_dom,
                                        "likes": 0
                                    })

                    extraidos = len(comentarios_por_video.get(vid_id, []))
                    print(f"     [+] Comentarios capturados: {extraidos}")

                    # Pasar al siguiente video presionando la flecha hacia abajo
                    if idx < len(videos_procesados) - 1:
                        await page.keyboard.press("ArrowDown")
                        await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"[!] Aviso al navegar por el visor de videos: {e}")

        # Construir las tablas finales con los datos que ya están seguros en memoria
        resultados_videos = []
        todos_los_comentarios_csv = []

        for v in videos_procesados:
            vid_id = str(v.get("id"))
            stats_v = v.get("stats", {})
            desc = v.get("desc", "")
            total_com = stats_v.get("commentCount", 0)
            url_video = f"https://www.tiktok.com/@{USUARIO_OBJETIVO}/video/{vid_id}"

            lista_coms = comentarios_por_video.get(vid_id, [])

            for c in lista_coms:
                todos_los_comentarios_csv.append({
                    "id_video": vid_id,
                    "autor": c["autor"],
                    "comentario": c["comentario"],
                    "likes_comentario": c["likes"]
                })

            resumen_texto = " | ".join([f"@{c['autor']}: {c['comentario']}" for c in lista_coms[:15]])

            resultados_videos.append({
                "id_video": vid_id,
                "url": url_video,
                "descripcion": desc,
                "vistas": stats_v.get("playCount", 0),
                "likes": stats_v.get("diggCount", 0),
                "comentarios_total": total_com,
                "comentarios_extraidos": len(lista_coms),
                "guardados": stats_v.get("collectCount", 0),
                "compartidos": stats_v.get("shareCount", 0),
                "muestra_comentarios": resumen_texto
            })

        await browser.close()

        pd.DataFrame([perfil_info]).to_csv("1_perfil.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(ultimos_seguidos).to_csv("2_ultimos_seguidos.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(resultados_videos).to_csv("3_ultimos_10_videos.csv", index=False, encoding="utf-8-sig")
        pd.DataFrame(todos_los_comentarios_csv).to_csv("4_comentarios_detallados.csv", index=False, encoding="utf-8-sig")
        print("\n[✓] ¡Proceso terminado sin errores! Archivos CSV generados en tu carpeta actual.")

if __name__ == "__main__":
    asyncio.run(scrapear_tiktok())