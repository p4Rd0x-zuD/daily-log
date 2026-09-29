#!/usr/bin/env python3
"""Genera una entrada TIL realista en español. Una ejecución = una entrada.
Uso: python3 farm.py [--slot N]
- Crea/actualiza daily-log/YYYY-MM-DD.md
- Appende a activity.log
- Regenera índice en README.md
Solo stdlib, sin dependencias.
"""
import argparse
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "daily-log"
ACTIVITY = ROOT / "activity.log"

# Hora Colombia (UTC-5) para que la fecha tenga sentido
TZ = timezone(timedelta(hours=-5))

TOPICOS = [
    ("Python", "Comprensiones con condición", "Hoy practiqué filtrar listas sin escribir for completo. Más legible cuando la condición es simple, pero si se anida mucho mejor volver al for normal.", "```python\npares = [x for x in range(20) if x % 2 == 0]\n# equivalente legible a un for + append\n```", "`python3 -m py_compile archivo.py` para chequeo rápido de sintaxis."),
    ("Python", "Manejo de archivos con with", "Repasé por qué siempre usar `with open(...)`. Se cierra solo aunque falle algo en el medio y evita leaks en scripts largos.", "```python\nwith open('datos.txt', encoding='utf-8') as f:\n    lineas = [l.strip() for l in f if l.strip()]\n```", "Tip: especifica siempre `encoding='utf-8'` en Windows/Linux mixto."),
    ("Python", "Diccionarios con get y setdefault", "Evité varios `if key in dict` usando `.get()` con default y `setdefault` para contadores. El código quedó más corto.", "```python\nconteo = {}\nfor w in palabras:\n    conteo[w] = conteo.get(w, 0) + 1\n```", "Para contadores grandes, `collections.Counter` es aún mejor."),
    ("Git", "Rebase vs merge en rama personal", "Practiqué `git pull --rebase` para mantener historial lineal en este repo. Solo lo uso en ramas mías, nunca en ramas compartidas.", "```bash\ngit pull --rebase origin main\ngit log --oneline -8\n```", "`git status` antes de cualquier pull, siempre."),
    ("Git", "Commits atómicos pequeños", "Me propuse commits de un solo tema con mensaje claro tipo `docs: ...`. Revisar con `git diff --cached` antes de commitear ayuda mucho.", "```bash\ngit add -p\ngit diff --cached\n```", "`git add -p` para agregar por pedazos, no todo de una."),
    ("Linux", "Permisos y chmod", "Repasé `rwx` y el modo numérico. 755 para carpetas/scripts, 644 para archivos normales. `ls -l` para verificar.", "```bash\nchmod 755 script.sh\nls -l script.sh\n```", "`chmod +x` equivale rápido para hacer ejecutable."),
    ("Linux", "Búsqueda con find y grep", "Combiné `find` para archivos y `grep -r` para contenido. Mucho más rápido que abrir todo a mano.", "```bash\nfind . -name '*.py' | head\n grep -rn 'TODO' --include='*.py' .\n```", "Con `rg` (ripgrep) es aún más rápido si está instalado."),
    ("Docker", "Capas y cache de build", "Entendí por qué el orden del Dockerfile importa: lo que cambia poco va arriba para aprovechar caché. Copiar requirements antes del código.", "```dockerfile\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\n```", "`docker build --progress=plain` para debuggear builds."),
    ("SQL", "GROUP BY + HAVING", "Practiqué agrupar y filtrar grupos con HAVING (no WHERE). Útil para duplicados y conteos.", "```sql\nSELECT email, COUNT(*) c\nFROM usuarios\nGROUP BY email\nHAVING COUNT(*) > 1;\n```", "Primero agrupa, después filtra el grupo."),
    ("SQL", "JOIN básico", "Repasé INNER JOIN para cruzar tablas por id. Dibujar las tablas en papel ayuda a no perderse.", "```sql\nSELECT u.nombre, p.total\nFROM usuarios u\nJOIN pedidos p ON p.user_id = u.id\nLIMIT 10;\n```", "Empieza con LIMIT 10 para no traer toda la tabla."),
    ("Terminal", "Historial y atajos", "Practiqué `Ctrl+R` para buscar comandos viejos y `!!` para repetir el último con sudo. Ahorra mucho tiempo.", "```bash\nsudo !!\n# repite último comando con sudo\n```", "`history | grep git` para encontrar ese comando perdido."),
    ("Backend", "Códigos HTTP que sí importan", "Memoricé los que más uso: 200 ok, 201 creado, 400 bad request, 401/403 auth, 404, 500. Devolver el correcto facilita el frontend.", "```python\nreturn {'error': 'no encontrado'}, 404\n```", "No devuelvas 200 con error adentro, rompe el contrato."),
    ("Backend", "Variables de entorno", "Moví secretos a `.env` y los leo con `os.getenv`. Nada de claves quemadas en el código.", "```python\nimport os\ntoken = os.getenv('API_TOKEN', '')\n```", "Agrega `.env` al `.gitignore` siempre."),
    ("Frontend", "Fetch con manejo de error", "Practiqué `fetch` chequeando `response.ok` antes del `.json()`. Sin eso los 404 pasan como éxito.", "```js\nconst r = await fetch(url);\nif (!r.ok) throw new Error(r.status);\nconst data = await r.json();\n```", "Envuelve en try/catch y muestra estado de carga."),
    ("Redes", "Qué muestra un ping", "Repasé que `ping` mide latencia y pérdida, no velocidad. Si hay loss alto, ni el mejor código salva la app.", "```bash\nping -c 4 8.8.8.8\n```", "`-c 4` para no dejarlo infinito."),
    ("Inglés técnico", "Vocabulario de PRs", "Anoté frases que veo en reviews: `nit:`, `LGTM`, `follow-up`, `edge case`. Entenderlas acelera leer PRs en inglés.", "```text\nnit: rename var for clarity\nLGTM after fixing edge case\n```", "Lee 1 PR en inglés al día, aunque sea corto."),
    ("Productividad", "Regla de 25 minutos", "Probé pomodoro de 25x5 para estas notas. Un bloque al día alcanza para no romper la racha.", "```text\n25 min foco -> 5 descanso -> repetir x2\n```", "Apaga notificaciones en el bloque de foco."),
    ("Markdown", "Tablas rápidas", "Practiqué tablas en README para el índice del log. Alinear con `|` cuesta al inicio pero se lee mucho mejor.", "```markdown\n| Fecha | Tema |\n|---|---|\n| 2026-09-29 | Python |\n```", "Previsualiza en GitHub antes de pushear."),
    ("Testing", "Un test mínimo útil", "Escribí un assert simple antes del código para fijar el comportamiento esperado. No TDD estricto, solo redacción clara.", "```python\nassert suma(2, 3) == 5\n```", "Un test que corre siempre > cinco perfectos que no corres."),
    ("Seguridad", "No subir secretos", "Revisé `git log -p` para verificar que nunca subí un token. `gh secret` y `.gitignore` bien puestos.", "```bash\ngit log -p --all -S 'API_TOKEN' -- activity.log\n```", "Si se filtra, rota la clave de una, no solo la borres."),
    ("VSCode", "Atajos que uso a diario", "Anoté: multi-cursor con Alt+click, renombrar con F2, ir a archivo con Ctrl+P. Pequeños pero suman.", "```text\nCtrl+P -> archivo | F2 -> renombrar | Alt+Click -> multicursor\n```", "Aprende uno nuevo por semana, no todos de golpe."),
    ("API", "Leer docs con curl", "Probé endpoints primero con `curl` antes de codear. Ver el JSON crudo evita suposiciones.", "```bash\ncurl -s https://api.github.com/users/octocat | head -c 500\n```", "`-s` para silencioso + `| jq` para pretty."),
    ("JSON", "jq para filtrar", "Usé `jq` para sacar solo campos que me importan de un JSON gigante. Indispensable con APIs.", "```bash\ncat data.json | jq '.[].login'\n```", "`jq .` solo ya formatea bonito."),
    ("Cron", "Sintaxis que siempre olvido", "Repasé cron: minuto hora día-mes mes día-semana. `*/15 * * * *` cada 15 min. GitHub Actions usa UTC.", "```bash\n# 13:30 UTC = 08:30 Bogotá\n30 13 * * *\n```", "Prueba primero con `workflow_dispatch` manual."),
    ("GitHub Actions", "Cache de pip", "Vi que cachear dependencias baja el tiempo de 2min a 30s. Pequeño cambio, gran ahorro diario.", "```yaml\n- uses: actions/setup-python@v5\n  with:\n    python-version: '3.11'\n    cache: 'pip'\n```", "El log de Actions muestra si hubo cache hit."),
]

REFLEXIONES = [
    "Mañana quiero profundizar con un ejemplo más grande.",
    "Lo anoto para no olvidarlo en el próximo proyecto.",
    "Pequeño avance pero constante, que es lo que importa.",
    "Me quedó una duda, la dejo para revisar mañana con calma.",
    "Esto me va a servir directo en lo que estoy armando.",
]

def pick_topic(rng):
    return rng.choice(TOPICOS)

def build_entry(rng, slot=1):
    ahora = datetime.now(TZ)
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M")
    cat, titulo, cuerpo, snippet, tip = pick_topic(rng)
    reflex = rng.choice(REFLEXIONES)
    entry = f"""## {hora} — {titulo} ({cat})

{cuerpo}

{snippet}

> {tip}

*{reflex}*

"""
    return fecha, entry, f"{cat}: {titulo}"

def regenerate_readme():
    archivos = sorted(LOG_DIR.glob("*.md"), reverse=True) if LOG_DIR.exists() else []
    lineas = ["# daily-log", "", "Bitácora diaria de aprendizaje. Notas cortas en español: qué aprendí, snippet y tip.", ""]
    lineas.append(f"Última actualización: {datetime.now(TZ).strftime('%Y-%m-%d %H:%M')} (Bogotá)")
    lineas.append("")
    lineas.append("| Fecha | Archivo |")
    lineas.append("|---|---|")
    if not archivos:
        lineas.append("| — | Sin entradas aún |")
    else:
        for p in archivos[:14]:
            lineas.append(f"| {p.stem} | [daily-log/{p.name}](daily-log/{p.name}) |")
    lineas.append("")
    lineas.append("## Cómo funciona")
    lineas.append("")
    lineas.append("- Cada día se agrega 1-5 entradas automáticas vía GitHub Actions (cron).")
    lineas.append("- Cada entrada es una nota corta real de estudio/trabajo.")
    lineas.append("- `activity.log` guarda el historial lineal de topics.")
    lineas.append("")
    (ROOT / "README.md").write_text("\n".join(lineas), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", type=int, default=1)
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    rng = random.Random(args.seed if args.seed is not None else random.randint(1, 999999) + args.slot * 1000)
    LOG_DIR.mkdir(exist_ok=True)
    fecha, entry, resumen = build_entry(rng, args.slot)
    target = LOG_DIR / f"{fecha}.md"
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    if target.exists():
        prev = target.read_text(encoding="utf-8")
        # evita duplicar mismo título el mismo día
        if resumen in prev and args.slot > 1:
            cat2, tit2, cuerpo2, snip2, tip2 = pick_topic(rng)
            resumen = f"{cat2}: {tit2}"
            entry = f"""## {datetime.now(TZ).strftime('%H:%M')} — {tit2} ({cat2})\n\n{cuerpo2}\n\n{snip2}\n\n> {tip2}\n\n*{rng.choice(REFLEXIONES)}*\n\n"""
        target.write_text(prev + "\n" + entry, encoding="utf-8")
    else:
        header = f"# {fecha}\n\nNotas del día. Cada bloque es una micro-sesión de estudio.\n\n"
        target.write_text(header + entry, encoding="utf-8")
    with open(ACTIVITY, "a", encoding="utf-8") as f:
        f.write(f"{now} | {resumen} (slot {args.slot})\n")
    regenerate_readme()
    print(f"OK {target.name} :: {resumen}")

if __name__ == "__main__":
    main()
