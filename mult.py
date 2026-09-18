"""
Tablas de multiplicar - App de práctica
----------------------------------------
Ejecutar con: streamlit run tablas_multiplicar_app.py

Características:
- Niveles progresivos (se desbloquea la siguiente tabla al dominar la actual)
- Patrón visual de puntos para entender la multiplicación
- Repetición espaciada: las multiplicaciones que más se fallan aparecen más seguido
- Racha de aciertos y progreso persistente entre sesiones (se guarda en un archivo JSON local)
- Repaso automático: tras 4 errores seguidos aparece la tabla completa
- Modo avanzado (opcional): multiplicación inversa, problemas con contexto y tiempo límite
"""

import streamlit as st
import json
import os
import random
import time

# ----------------------------------------------------------------------
# Configuración y persistencia
# ----------------------------------------------------------------------

DATA_FILE = "progreso_tablas.json"
TABLAS = list(range(2, 11))
UMBRAL_DOMINIO = 8          # aciertos consecutivos necesarios para dominar una tabla
LIMITE_ERRORES_SESION = 4   # errores seguidos antes de mostrar la tabla completa de repaso
LIMITE_TIEMPO_SEGUNDOS = 12  # tiempo límite por pregunta en modo avanzado

PLANTILLAS_PROBLEMA = [
    "Cada caja tiene {b} manzanas. Si hay {a} cajas, ¿cuántas manzanas hay en total?",
    "Un estante tiene {a} filas de libros, con {b} libros en cada fila. ¿Cuántos libros hay en total?",
    "En el salón hay {a} mesas, cada una con {b} sillas. ¿Cuántas sillas hay en total?",
    "Cada semana ahorras {b} monedas. ¿Cuántas monedas habrás ahorrado después de {a} semanas?",
    "Un jardín tiene {a} macetas, cada una con {b} flores. ¿Cuántas flores hay en total?",
    "En cada bolsa hay {b} caramelos. Si compras {a} bolsas, ¿cuántos caramelos tienes en total?",
]


def cargar_progreso():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Estructura inicial: solo la tabla del 2 desbloqueada
    return {
        "desbloqueadas": [2],
        "dominadas": [],
        "racha_actual": {str(t): 0 for t in TABLAS},
        "errores": {},  # "a_b": conteo_de_fallos
        "estrellas": 0,
    }


def guardar_progreso(progreso):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(progreso, f, ensure_ascii=False, indent=2)


if "progreso" not in st.session_state:
    st.session_state.progreso = cargar_progreso()

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "menu"

if "tabla_actual" not in st.session_state:
    st.session_state.tabla_actual = None

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = None

if "mostrar_resultado" not in st.session_state:
    st.session_state.mostrar_resultado = False

if "mostrar_patron" not in st.session_state:
    st.session_state.mostrar_patron = False

if "errores_sesion" not in st.session_state:
    st.session_state.errores_sesion = {t: 0 for t in TABLAS}

if "mostrar_tabla_completa" not in st.session_state:
    st.session_state.mostrar_tabla_completa = False

if "modo_avanzado" not in st.session_state:
    st.session_state.modo_avanzado = False

if "tiempo_inicio" not in st.session_state:
    st.session_state.tiempo_inicio = None

if "tiempo_agotado" not in st.session_state:
    st.session_state.tiempo_agotado = False


# ----------------------------------------------------------------------
# Estilo sobrio (CSS)
# ----------------------------------------------------------------------

st.set_page_config(page_title="Tablas de multiplicar", page_icon="×", layout="centered")

st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .main {
        background-color: #FAFAFA;
    }
    .titulo-app {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1F2937;
        margin-bottom: 0.2rem;
    }
    .subtitulo-app {
        color: #6B7280;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .tarjeta-tabla {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        background-color: white;
    }
    .tarjeta-bloqueada {
        opacity: 0.45;
    }
    .badge-dominada {
        color: #4F46E5;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-avanzado {
        display: inline-block;
        background-color: #EEF2FF;
        color: #4F46E5;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 999px;
        margin-bottom: 1rem;
    }
    .stButton>button {
        border-radius: 6px;
        border: 1px solid #4F46E5;
        color: #4F46E5;
        background-color: white;
    }
    .stButton>button:hover {
        background-color: #4F46E5;
        color: white;
    }
    .dot {
        height: 14px;
        width: 14px;
        background-color: #4F46E5;
        border-radius: 50%;
        display: inline-block;
        margin: 3px;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Lógica de preguntas (repetición espaciada + tipos de pregunta)
# ----------------------------------------------------------------------

def elegir_multiplicador(tabla):
    """Elige un multiplicador (1-10), dando más peso a las combinaciones
    que se han fallado más veces (repetición espaciada)."""
    progreso = st.session_state.progreso
    opciones = list(range(1, 11))
    pesos = []
    for n in opciones:
        clave = f"{tabla}_{n}"
        fallos = progreso["errores"].get(clave, 0)
        pesos.append(1 + fallos * 3)
    return random.choices(opciones, weights=pesos, k=1)[0]


def generar_pregunta(tabla):
    """Genera una pregunta nueva. En modo avanzado puede ser normal,
    inversa (falta un factor) o un problema con contexto."""
    n = elegir_multiplicador(tabla)
    producto = tabla * n

    if st.session_state.modo_avanzado:
        tipo = random.choice(["inversa", "problema"])
    else:
        tipo = "normal"

    if tipo == "normal":
        texto = f"¿Cuánto es {tabla} × {n}?"
        respuesta = producto
    elif tipo == "inversa":
        texto = f"{tabla} × ___ = {producto}. ¿Qué número falta?"
        respuesta = n
    else:  # problema
        plantilla = random.choice(PLANTILLAS_PROBLEMA)
        texto = plantilla.format(a=tabla, b=n)
        respuesta = producto

    return {"tabla": tabla, "n": n, "tipo": tipo, "texto": texto, "respuesta": respuesta}


def registrar_resultado(tabla, multiplicador, correcto):
    progreso = st.session_state.progreso
    clave = f"{tabla}_{multiplicador}"

    if correcto:
        progreso["racha_actual"][str(tabla)] += 1
        progreso["estrellas"] += 1
        if clave in progreso["errores"] and progreso["errores"][clave] > 0:
            progreso["errores"][clave] -= 1
    else:
        progreso["racha_actual"][str(tabla)] = 0
        progreso["errores"][clave] = progreso["errores"].get(clave, 0) + 1

    if progreso["racha_actual"][str(tabla)] >= UMBRAL_DOMINIO and tabla not in progreso["dominadas"]:
        progreso["dominadas"].append(tabla)
        siguiente = tabla + 1
        if siguiente in TABLAS and siguiente not in progreso["desbloqueadas"]:
            progreso["desbloqueadas"].append(siguiente)

    guardar_progreso(progreso)


def dibujar_tabla_completa(tabla):
    """Muestra la tabla completa del número (1 a 10) como repaso."""
    filas_html = ""
    for n in range(1, 11):
        filas_html += (
            '<div style="display:flex; justify-content:space-between; padding:4px 12px; '
            'border-bottom:1px solid #E5E7EB; font-size:0.95rem;">'
            f'<span style="color:#6B7280;">{tabla} × {n}</span>'
            f'<span style="font-weight:600; color:#1F2937;">{tabla * n}</span>'
            '</div>'
        )
    return (
        '<div style="border:1px solid #E5E7EB; border-radius:8px; overflow:hidden; background:white;">'
        f'{filas_html}'
        '</div>'
    )


def dibujar_patron(a, b):
    """Genera un patrón visual de puntos en forma de cuadrícula a x b."""
    filas = ""
    for _ in range(a):
        fila = "".join(['<span class="dot"></span>' for _ in range(b)])
        filas += f'<div style="line-height: 1.4;">{fila}</div>'
    return filas


def iniciar_pregunta(tabla):
    """Genera una pregunta nueva y reinicia el cronómetro."""
    st.session_state.pregunta_actual = generar_pregunta(tabla)
    st.session_state.mostrar_resultado = False
    st.session_state.tiempo_inicio = time.time()
    st.session_state.tiempo_agotado = False


# ----------------------------------------------------------------------
# Pantalla: Menú principal
# ----------------------------------------------------------------------

def pantalla_menu():
    progreso = st.session_state.progreso

    st.markdown('<div class="titulo-app">Tablas de multiplicar</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-app">Elige una tabla para practicar</div>', unsafe_allow_html=True)

    total_dominadas = len(progreso["dominadas"])
    st.progress(total_dominadas / len(TABLAS))
    st.caption(f"Progreso: {total_dominadas} de {len(TABLAS)} tablas dominadas  ·  ⭐ {progreso['estrellas']} puntos")

    st.write("")
    nuevo_valor = st.toggle(
        "Modo avanzado (multiplicación inversa, problemas y tiempo límite)",
        value=st.session_state.modo_avanzado,
        key="chk_modo_avanzado",
    )
    st.session_state.modo_avanzado = nuevo_valor
    st.write("")

    cols = st.columns(3)
    for i, tabla in enumerate(TABLAS):
        col = cols[i % 3]
        desbloqueada = tabla in progreso["desbloqueadas"]
        dominada = tabla in progreso["dominadas"]

        with col:
            clase = "tarjeta-tabla" if desbloqueada else "tarjeta-tabla tarjeta-bloqueada"
            etiqueta = "✓ Dominada" if dominada else ("Disponible" if desbloqueada else "Bloqueada")

            st.markdown(f"""
            <div class="{clase}">
                <div style="font-size:1.6rem; font-weight:600;">×{tabla}</div>
                <div class="badge-dominada">{etiqueta}</div>
            </div>
            """, unsafe_allow_html=True)

            if desbloqueada:
                if st.button("Practicar", key=f"btn_{tabla}"):
                    st.session_state.tabla_actual = tabla
                    st.session_state.mostrar_patron = False
                    st.session_state.errores_sesion[tabla] = 0
                    st.session_state.mostrar_tabla_completa = False
                    iniciar_pregunta(tabla)
                    st.session_state.pantalla = "practica"
                    st.rerun()

            st.write("")


# ----------------------------------------------------------------------
# Pantalla: Práctica
# ----------------------------------------------------------------------

def pantalla_practica():
    progreso = st.session_state.progreso
    tabla = st.session_state.tabla_actual
    pregunta = st.session_state.pregunta_actual
    n = pregunta["n"]

    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("← Volver"):
            st.session_state.pantalla = "menu"
            st.rerun()

    st.markdown(f'<div class="titulo-app">Tabla del {tabla}</div>', unsafe_allow_html=True)

    if st.session_state.modo_avanzado:
        st.markdown('<span class="badge-avanzado">Modo avanzado</span>', unsafe_allow_html=True)

    racha = progreso["racha_actual"][str(tabla)]
    errores_actuales = st.session_state.errores_sesion[tabla]
    st.caption(
        f"Racha actual: {racha} de {UMBRAL_DOMINIO} para dominar esta tabla · "
        f"Errores: {errores_actuales} de {LIMITE_ERRORES_SESION}"
    )

    st.write("")
    st.markdown(f"### {pregunta['texto']}")

    if st.session_state.modo_avanzado and not st.session_state.mostrar_resultado:
        st.caption(f"⏱ Tienes {LIMITE_TIEMPO_SEGUNDOS} segundos para responder")

    # El patrón visual solo tiene sentido para la pregunta "normal"
    if pregunta["tipo"] == "normal":
        if st.checkbox("Ver patrón visual", value=st.session_state.mostrar_patron, key="chk_patron"):
            st.session_state.mostrar_patron = True
            st.markdown(dibujar_patron(tabla, n), unsafe_allow_html=True)
        else:
            st.session_state.mostrar_patron = False

    respuesta = st.number_input(
        "Tu respuesta", min_value=0, max_value=200, step=1,
        key=f"input_{tabla}_{n}_{pregunta['tipo']}"
    )

    if st.button("Comprobar"):
        elapsed = time.time() - (st.session_state.tiempo_inicio or time.time())
        tiempo_agotado = st.session_state.modo_avanzado and elapsed > LIMITE_TIEMPO_SEGUNDOS

        correcto = (not tiempo_agotado) and (respuesta == pregunta["respuesta"])

        registrar_resultado(tabla, n, correcto)
        st.session_state.progreso = cargar_progreso()  # refresca desde disco
        st.session_state.resultado_correcto = correcto
        st.session_state.tiempo_agotado = tiempo_agotado
        st.session_state.mostrar_resultado = True

        if correcto:
            st.session_state.errores_sesion[tabla] = 0
        else:
            st.session_state.errores_sesion[tabla] += 1
            if st.session_state.errores_sesion[tabla] >= LIMITE_ERRORES_SESION:
                st.session_state.mostrar_tabla_completa = True
                st.session_state.errores_sesion[tabla] = 0

    if st.session_state.mostrar_resultado:
        if st.session_state.resultado_correcto:
            st.success(f"Correcto: {tabla} × {n} = {tabla * n}")
        elif st.session_state.tiempo_agotado:
            st.error(f"¡Se acabó el tiempo! {tabla} × {n} = {tabla * n}")
        else:
            st.error(f"No es correcto. {tabla} × {n} = {tabla * n}")



        if st.session_state.mostrar_tabla_completa:
            st.warning(f"Repasemos la tabla del {tabla} completa antes de seguir:")
            st.markdown(dibujar_tabla_completa(tabla), unsafe_allow_html=True)
            if st.button("Entendido, seguir practicando"):
                st.session_state.mostrar_tabla_completa = False
                iniciar_pregunta(tabla)
                st.rerun()
        else:
            if st.button("Siguiente pregunta"):
                iniciar_pregunta(tabla)
                st.rerun()


# ----------------------------------------------------------------------
# Enrutamiento principal
# ----------------------------------------------------------------------

if st.session_state.pantalla == "menu":
    pantalla_menu()
else:
    pantalla_practica()
