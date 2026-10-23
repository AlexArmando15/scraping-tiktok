import os
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

# 1. Cargar las variables desde el archivo .env (forzando actualización con override=True)
load_dotenv(override=True)

# 2. Obtener y limpiar la API Key (quita espacios o comillas accidentales)
api_key_limpia = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")

if not api_key_limpia or not api_key_limpia.startswith("gsk_"):
    raise ValueError(
        "ERROR: No se encontró una GROQ_API_KEY válida en tu archivo .env. "
        "Verifica que en tu .env exista la línea: GROQ_API_KEY=gsk_..."
    )

# 3. Leer el CSV de comentarios generado por el scraper
archivo_csv = "4_comentarios_detallados.csv"
df = pd.read_csv(archivo_csv)

# 4. Limpiar datos: eliminar filas donde el comentario esté vacío (NaN)
df = df.dropna(subset=["comentario"])

# 5. Formatear los comentarios con su autor y likes para darle contexto a la IA
lista_comentarios = []
for idx, fila in df.iterrows():
    linea = f"- @{fila['autor']} (Likes: {fila['likes_comentario']}): {fila['comentario']}"
    lista_comentarios.append(linea)

texto_comentarios = "\n".join(lista_comentarios)

# 6. Construir el Prompt 
prompt_analisis = f"""
Actúa como un analista de datos y psicólogo experto en psicometría digital y el modelo de personalidad Big Five (OCEAN).
A continuación te entrego los comentarios extraídos de los últimos 10 videos de la cuenta de TikTok @alexarmando15:

COMENTARIOS EXTRAÍDOS:
{texto_comentarios}

Realiza un análisis completo estructurado en las siguientes secciones:

1. DISTRIBUCIÓN BIG FIVE (DEBE SUMAR EXACTAMENTE 100%):
   Calcula el peso porcentual relativo de cada uno de los 5 rasgos en la audiencia de modo que LA SUMA TOTAL DE LOS 5 PORCENTAJES SEA EXACTAMENTE 100%. 
   Muestra los resultados en una tabla Markdown clara con estas columnas: | Rasgo (Big Five) | Porcentaje (%) | Nivel Cualitativo |
   - Apertura a la experiencia (Openness)
   - Responsabilidad (Conscientiousness)
   - Extraversión (Extraversion)
   - Amabilidad (Agreeableness)
   - Neuroticismo / Sensibilidad emocional (Neuroticism)
    Incluye al final de la tabla una fila de **TOTAL** que muestre **100%**. (Verifica matemáticamente antes de responder que la suma de los 5 valores sea exactamente 100%).

2. JUSTIFICACIÓN CON EVIDENCIA:
   Explica por qué asignaste cada porcentaje citando ejemplos textuales de los comentarios (desahogos emocionales, letras de canciones, empatía o emojis).

3. CONCLUSIÓN PSICOLÓGICA DE LA AUDIENCIA:
   Redacta una conclusión ejecutiva sobre qué tipo de comunidad interactúa con esta cuenta y qué emociones predominan.
"""

# 7. Inicializar el cliente de Groq pasándole directamente la clave limpia
client = Groq(api_key=api_key_limpia)

print("[*] Enviando comentarios a Groq (openai/gpt-oss-120b) para análisis Big Five...\n")

# 8. Llamar a la API
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": prompt_analisis
        }
    ],
    temperature=0.7,
    max_completion_tokens=2048,
    top_p=1,
    reasoning_effort="medium",
    stream=True,
    stop=None
)

# 9. Imprimir la respuesta en tiempo real (streaming) y guardarla
reporte_completo = ""
for chunk in completion:
    fragmento = chunk.choices[0].delta.content or ""
    print(fragmento, end="")
    reporte_completo += fragmento

# 10. Guardar el informe final en un archivo Markdown para tu deber
with open("5_reporte_bigfive.md", "w", encoding="utf-8") as f:
    f.write(reporte_completo)

print("\n\n[✓] ¡Análisis guardado exitosamente en '5_reporte_bigfive.md'!")