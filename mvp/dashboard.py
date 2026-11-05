"""Dashboard del operador (Streamlit).

Muestra el video en vivo que publica detector.py y la lista de alertas, y
permite confirmarlas o descartarlas. Ejecutar en otra terminal:

    streamlit run dashboard.py
"""

from pathlib import Path

import streamlit as st

from almacen import Almacen

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "data"
EN_VIVO = DATOS / "en_vivo.jpg"

NOMBRES = {
    "aglomeracion": "👥 Aglomeración",
    "objeto_desatendido": "🎒 Objeto desatendido",
    "persona_en_suelo": "🚑 Persona en el suelo",
    "zona_restringida": "⛔ Zona restringida",
}
ESTADO_ICONO = {"nueva": "🔴 Nueva", "confirmada": "✅ Confirmada", "descartada": "⚪ Descartada"}

st.set_page_config(page_title="Tres60 SafeCampus", page_icon="🛡️", layout="wide")


@st.cache_resource
def almacen() -> Almacen:
    return Almacen(DATOS / "alertas.db")


st.title("🛡️ Tres60 SafeCampus")
st.caption("Apoyo a la detección temprana. Cada alerta la confirma o descarta una persona.")

col_video, col_alertas = st.columns([3, 2], gap="large")


@st.fragment(run_every="0.5s")
def video_en_vivo():
    if EN_VIVO.exists():
        try:
            st.image(EN_VIVO.read_bytes(), width="stretch")
        except OSError:
            pass
    else:
        st.info("Esperando video… inicia `python detector.py` en otra terminal.")


@st.fragment(run_every="2s")
def panel_alertas():
    db = almacen()
    conteo = db.contar_por_estado()
    c1, c2, c3 = st.columns(3)
    c1.metric("Nuevas", conteo["nueva"])
    c2.metric("Confirmadas", conteo["confirmada"])
    c3.metric("Descartadas", conteo["descartada"])

    alertas = db.listar(30)
    # Aviso emergente cuando llega una alerta nueva.
    ultima = alertas[0]["id"] if alertas else 0
    vista = st.session_state.get("ultima_alerta_vista")
    if vista is not None and ultima > vista:
        st.toast(f"Nueva alerta: {NOMBRES.get(alertas[0]['tipo'], alertas[0]['tipo'])}", icon="🚨")
    st.session_state["ultima_alerta_vista"] = ultima

    if not alertas:
        st.write("Sin alertas por ahora.")
    for a in alertas:
        with st.container(border=True):
            st.markdown(
                f"**{NOMBRES.get(a['tipo'], a['tipo'])}** · {ESTADO_ICONO.get(a['estado'], a['estado'])}  \n"
                f"{a['fecha'].replace('T', ' ')} · {a['camara']}"
            )
            st.write(a["mensaje"])
            if a["imagen"] and Path(a["imagen"]).exists():
                with st.expander("Ver evidencia", expanded=a["estado"] == "nueva"):
                    st.image(a["imagen"], width="stretch")
            if a["estado"] == "nueva":
                b1, b2 = st.columns(2)
                if b1.button("Confirmar", key=f"ok{a['id']}", type="primary", width="stretch"):
                    db.cambiar_estado(a["id"], "confirmada")
                    st.rerun(scope="fragment")
                if b2.button("Descartar", key=f"no{a['id']}", width="stretch"):
                    db.cambiar_estado(a["id"], "descartada")
                    st.rerun(scope="fragment")


with col_video:
    st.subheader("En vivo")
    video_en_vivo()

with col_alertas:
    st.subheader("Alertas")
    panel_alertas()
