"""Estrellas de multiplicar: tablas del 2 al 10 (sin x1) para niños, pensada para verse en el celular.

Ejecutar:  streamlit run estrellas_multiplicar.py
Requiere Streamlit reciente (recomendado >= 1.40).
"""
import random

import streamlit as st

# ---------------------------------------------------------------- configuración
TABLAS = list(range(2, 11))      # filas de la cuadrícula
FACTORES = list(range(2, 11))    # columnas de la cuadrícula
TOTAL = 20                       # preguntas por partida
POR_TABLA = 2                    # sorteo equilibrado: mínimo por tabla (9 x 2 = 18, más 2 extra)

FORMATOS = ["directa", "hueco_a", "hueco_b"]
PESOS = [4, 3, 3]                # con qué frecuencia sale cada formato

FELICITACIONES = ["¡Bien!", "¡Correcto!", "¡Eso es!", "¡Otra estrella!", "¡Perfecto!"]
HITOS = {
    TOTAL // 4: "¡Un cuarto del camino!",
    TOTAL // 2: "¡Ya vas por la mitad!",
    TOTAL * 3 // 4: f"¡Solo faltan {TOTAL - TOTAL * 3 // 4}!",
}

# ---------------------------------------------------------------- estilos
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap');

:root {
  --cielo: #14123A;
  --panel: #221F5C;
  --estrella: #FFD23F;
  --menta: #5EEAD4;
  --texto: #F4F2FF;
  --tenue: #8B87C9;
}
html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--cielo);
  color: var(--texto);
  font-family: 'Fredoka', 'Trebuchet MS', 'Segoe UI', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { max-width: 480px; padding: 1.2rem 1rem 3rem; }

.titulo { font-size: 2.1rem; font-weight: 700; line-height: 1.1; margin: .4rem 0; }
.sub { color: var(--tenue); font-size: 1.05rem; margin-bottom: 1rem; }

.pct { font-size: 4.2rem; font-weight: 700; color: var(--estrella); line-height: 1; }
.pct small { font-size: 1.5rem; margin-left: .1rem; }
.cuenta { color: var(--tenue); font-size: 1rem; }
.barra { height: 10px; border-radius: 99px; background: var(--panel); overflow: hidden; margin: .6rem 0 .8rem; }
.barra > i { display: block; height: 100%; background: var(--estrella); border-radius: 99px; transition: width .4s ease; }

.msg { text-align: center; min-height: 1.7rem; color: var(--menta); font-size: 1.1rem; }
.pregunta { font-size: clamp(2.4rem, 12vw, 3.4rem); font-weight: 700; text-align: center; margin: .3rem 0 .4rem; }
.hueco { display: inline-block; min-width: 1.3em; border-bottom: .1em dashed var(--menta); color: var(--menta); }
.pista { text-align: center; color: var(--tenue); font-size: 1rem; margin-bottom: .4rem; }

.cuadricula { display: grid; grid-template-columns: repeat(9, 1fr); gap: 5px; margin: 1.3rem 0; }
.c { aspect-ratio: 1; border-radius: 28%; background: #1B1852; }
.c.obj { background: #2A2670; box-shadow: inset 0 0 0 2px #4B47A8; }
.c.gem { box-shadow: inset 0 0 0 2px rgba(94, 234, 212, .8), 0 0 8px rgba(94, 234, 212, .35); }
.c.ok {
  background: var(--estrella); box-shadow: 0 0 10px rgba(255, 210, 63, .55);
  display: flex; align-items: center; justify-content: center;
  color: #14123A; font-size: clamp(.7rem, 3.6vw, 1rem);
}
.c.ok::after { content: "★"; }
.c.nueva { animation: pop .45s ease-out; }
@keyframes pop { 0% { transform: scale(.4); } 60% { transform: scale(1.25); } 100% { transform: scale(1); } }
@media (prefers-reduced-motion: reduce) {
  .c.nueva { animation: none; }
  .barra > i { transition: none; }
}

.insignia {
  display: inline-block; padding: .35rem 1rem; border-radius: 99px; margin-bottom: 1rem;
  border: 2px solid var(--menta); color: var(--menta); font-weight: 600;
}

/* botones */
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
  width: 100%; min-height: 3.4rem; border: 0; border-radius: 1rem;
  background: var(--estrella); font-family: inherit;
}
div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { background: #FFE066; }
div.stButton > button:focus-visible, div[data-testid="stFormSubmitButton"] > button:focus-visible {
  outline: 3px solid var(--menta); outline-offset: 2px;
}
.stButton button p, div[data-testid="stFormSubmitButton"] button p {
  color: #14123A; font-weight: 600; font-size: 1.2rem; margin: 0;
}
[data-testid="stExpander"] { border: 1px solid #2E2A7A; border-radius: 1rem; background: transparent; }
[data-testid="stExpander"] summary { color: var(--tenue); }
[data-testid="stExpander"] div.stButton > button { background: transparent; border: 2px solid #4B47A8; }
[data-testid="stExpander"] .stButton button p { color: var(--texto); }

/* campo de respuesta: píldora clara con números oscuros (siempre legible) */
[data-testid="stForm"] { border: 0; padding: 0; }
div[data-testid="stNumberInput"] div[data-baseweb="input"] {
  background: #F4F2FF !important;
  border: 3px solid transparent !important;
  border-radius: 999px !important;
  overflow: hidden;
}
div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {
  border-color: var(--estrella) !important;
  box-shadow: 0 0 0 4px rgba(255, 210, 63, .35) !important;
}
div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
  background: transparent !important; border: 0 !important;
}
div[data-testid="stNumberInput"] input {
  background: transparent !important;
  color: #14123A !important;
  -webkit-text-fill-color: #14123A !important;
  caret-color: #14123A;
  font-family: inherit; font-size: 2.4rem; font-weight: 700;
  text-align: center; height: 3.8rem; padding: 0 1rem;
}
div[data-testid="stNumberInput"] button { display: none !important; }
[data-testid="InputInstructions"] { display: none; }
"""


# ---------------------------------------------------------------- lógica
def nuevo_formato():
    return random.choices(FORMATOS, weights=PESOS)[0]


def sortear():
    """Elige TOTAL casillas: POR_TABLA de cada fila y el resto al azar."""
    todas = [(a, b) for a in TABLAS for b in FACTORES]
    elegidas = []
    for a in TABLAS:
        elegidas += random.sample([p for p in todas if p[0] == a], POR_TABLA)
    resto = [p for p in todas if p not in elegidas]
    elegidas += random.sample(resto, TOTAL - len(elegidas))
    return elegidas


def barajar(pares):
    """Mezcla evitando, si se puede, dos preguntas seguidas de la misma tabla."""
    pares = list(pares)
    for _ in range(300):
        random.shuffle(pares)
        if all(pares[i][0] != pares[i + 1][0] for i in range(len(pares) - 1)):
            break
    return pares


def esperado(q):
    if q["f"] == "hueco_a":
        return q["a"]
    if q["f"] == "hueco_b":
        return q["b"]
    return q["a"] * q["b"]


def texto_pregunta(q):
    a, b, p = q["a"], q["b"], q["a"] * q["b"]
    hueco = '<span class="hueco">?</span>'
    if q["f"] == "hueco_a":
        return f"{hueco} × {b} = {p}"
    if q["f"] == "hueco_b":
        return f"{a} × {hueco} = {p}"
    return f"{a} × {b} = {hueco}"


def pista(q):
    """Cuenta de n en n sin llegar al resultado, para que el niño complete el último paso."""
    base, veces = (q["b"], q["a"]) if q["f"] == "hueco_a" else (q["a"], q["b"])
    return ", ".join(str(base * i) for i in range(1, veces)) + ", …"


def cuadricula_html(objetivo, hechas, ultima):
    obj = set(objetivo)
    # La casilla "gemela" de una acertada (5x9 tras acertar 9x5) brilla tenue si toca en esta partida.
    gemelas = {(b, a) for (a, b) in hechas if a != b and (b, a) not in hechas and (b, a) in obj}
    celdas = []
    for a in TABLAS:
        for b in FACTORES:
            p = (a, b)
            if p in hechas:
                cls = "c ok nueva" if p == ultima else "c ok"
            elif p in gemelas:
                cls = "c gem"
            elif p in obj:
                cls = "c obj"
            else:
                cls = "c"
            celdas.append(f'<div class="{cls}"></div>')
    etiqueta = f"Progreso: {len(hechas)} de {TOTAL} estrellas encendidas"
    return f'<div class="cuadricula" role="img" aria-label="{etiqueta}">{"".join(celdas)}</div>'


def progreso_html(n):
    pct = n * 100 // TOTAL
    return (
        f'<div class="pct">{pct}<small>%</small></div>'
        f'<div class="cuenta">{n} de {TOTAL} estrellas</div>'
        f'<div class="barra"><i style="width:{pct}%"></i></div>'
    )


# ---------------------------------------------------------------- estado y callbacks
def init_estado():
    s = st.session_state
    if "pantalla" not in s:
        s.pantalla = "inicio"
        s.objetivo = []
        s.cola = []
        s.hechas = set()
        s.ultima = None
        s.msg = None
        s.hito = None
        s.celebrar = False
        s.confirmar = False


def iniciar_partida():
    s = st.session_state
    s.objetivo = sortear()
    s.cola = [{"a": a, "b": b, "f": nuevo_formato(), "int": 0} for a, b in barajar(s.objetivo)]
    s.hechas = set()
    s.ultima = None
    s.msg = None
    s.hito = None
    s.celebrar = False
    s.confirmar = False
    s.pantalla = "juego"


def ir_inicio():
    st.session_state.confirmar = False
    st.session_state.pantalla = "inicio"


def pedir_confirmacion():
    st.session_state.confirmar = True


def cancelar_reset():
    st.session_state.confirmar = False


def responder():
    s = st.session_state
    r = s.get("respuesta")
    if r is None or not s.cola:
        s.msg = "Escribe un número y toca Listo."
        return
    q = s.cola[0]
    if int(r) == esperado(q):
        s.cola.pop(0)
        s.hechas.add((q["a"], q["b"]))
        s.ultima = (q["a"], q["b"])
        s.msg = random.choice(FELICITACIONES)
        if not s.cola:
            s.pantalla = "final"
            s.celebrar = True
        elif len(s.hechas) in HITOS:
            s.hito = HITOS[len(s.hechas)]
    else:
        # Sin marcas de error: la pregunta pasa al final y vuelve con otro formato.
        q["int"] += 1
        q["f"] = nuevo_formato()
        if len(s.cola) > 1:
            s.cola.append(s.cola.pop(0))
            s.msg = "¡Casi! Esta vuelve a salir al final."
        else:
            s.msg = "¡Casi! Inténtalo otra vez."


# ---------------------------------------------------------------- pantallas
def pantalla_inicio():
    st.markdown('<div class="titulo">Estrellas de multiplicar</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub">Responde {TOTAL} multiplicaciones y enciende tu constelación.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(cuadricula_html([], set(), None), unsafe_allow_html=True)
    st.button("Jugar", type="primary", on_click=iniciar_partida)


def pantalla_juego():
    s = st.session_state
    if s.hito:
        st.toast(s.hito, icon="⭐")
        s.hito = None

    q = s.cola[0]
    st.markdown(progreso_html(len(s.hechas)), unsafe_allow_html=True)
    st.markdown(f'<div class="msg">{s.msg or ""}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pregunta">{texto_pregunta(q)}</div>', unsafe_allow_html=True)
    if q["int"] >= 1:
        st.markdown(f'<div class="pista">Pista: {pista(q)}</div>', unsafe_allow_html=True)

    with st.form("form_respuesta", clear_on_submit=True):
        st.number_input(
            "Tu respuesta", min_value=0, max_value=100, value=None, step=1,
            format="%d", key="respuesta", label_visibility="collapsed",
        )
        st.form_submit_button("Listo", type="primary", on_click=responder)

    st.markdown(cuadricula_html(s.objetivo, s.hechas, s.ultima), unsafe_allow_html=True)

    with st.expander("Opciones", expanded=s.confirmar):
        if not s.confirmar:
            st.button("Empezar de nuevo", key="btn_reset", on_click=pedir_confirmacion)
        else:
            st.markdown('<div class="sub">¿Empezar de nuevo? Perderás lo que llevas.</div>', unsafe_allow_html=True)
            st.button("Sí, empezar de nuevo", key="btn_si", on_click=ir_inicio)
            st.button("No, seguir jugando", key="btn_no", on_click=cancelar_reset)


def pantalla_final():
    s = st.session_state
    if s.celebrar:
        st.balloons()
        s.celebrar = False
    st.markdown(progreso_html(TOTAL), unsafe_allow_html=True)
    st.markdown('<div class="titulo">¡Lo lograste!</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub">Encendiste las {TOTAL} estrellas. Esta es tu constelación de hoy.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(cuadricula_html(s.objetivo, set(s.objetivo), None), unsafe_allow_html=True)
    st.markdown('<div class="insignia">Constelación completa</div>', unsafe_allow_html=True)
    st.button("Jugar otra vez", type="primary", on_click=iniciar_partida)


# ---------------------------------------------------------------- app
st.set_page_config(
    page_title="Estrellas de multiplicar", page_icon="⭐",
    layout="centered", initial_sidebar_state="collapsed",
)
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
init_estado()

{"inicio": pantalla_inicio, "juego": pantalla_juego, "final": pantalla_final}[st.session_state.pantalla]()
