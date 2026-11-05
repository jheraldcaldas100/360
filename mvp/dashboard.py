"""Dashboard del operador (Streamlit).

Muestra el video en vivo que publica detector.py, las alertas con su
evidencia y prioridad, estadísticas de tiempos y deslizadores para ajustar
los parámetros en vivo. Ejecutar en otra terminal:

    streamlit run dashboard.py
"""

import io
import math
import os
import struct
import wave
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

from almacen import Almacen, segundos_entre

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "data"
EN_VIVO = DATOS / "en_vivo.jpg"
AJUSTES = DATOS / "ajustes.yaml"
CONFIG_ACTIVA = DATOS / "config_activa.yaml"

NOMBRES = {
    "aglomeracion": "👥 Aglomeración",
    "objeto_desatendido": "🎒 Objeto desatendido",
    "persona_en_suelo": "🚑 Persona en el suelo",
    "zona_restringida": "⛔ Zona restringida",
}
PRIORIDAD = {  # tipo -> (prioridad, color de Streamlit)
    "persona_en_suelo": ("Alta", "red"),
    "zona_restringida": ("Alta", "red"),
    "objeto_desatendido": ("Media", "orange"),
    "aglomeracion": ("Media", "orange"),
}
ESTADO_ICONO = {
    "nueva": "🔴 Nueva",
    "confirmada": "🟠 Confirmada, por atender",
    "descartada": "⚪ Descartada",
    "atendida": "✅ Atendida",
}

st.set_page_config(page_title="Tres60 SafeCampus", page_icon="🛡️", layout="wide")
st.markdown("<style>audio {display: none;}</style>", unsafe_allow_html=True)


@st.cache_resource
def almacen() -> Almacen:
    return Almacen(DATOS / "alertas.db")


@st.cache_data
def pitido() -> bytes:
    """Sonido corto de alerta generado en memoria (dos tonos)."""
    tasa, buf = 16000, io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(tasa)
        muestras = b""
        for freq in (880, 1320):
            for i in range(int(tasa * 0.18)):
                muestras += struct.pack("<h", int(12000 * math.sin(2 * math.pi * freq * i / tasa)))
        w.writeframes(muestras)
    return buf.getvalue()


def fmt_seg(valor) -> str:
    if valor is None or pd.isna(valor):
        return "—"
    return f"{valor:.1f} s" if valor < 120 else f"{valor / 60:.1f} min"


def hora(iso: str | None) -> str:
    return iso.replace("T", " ")[:19] if iso else "—"


with st.sidebar:
    st.header("🛡️ SafeCampus")
    sonido = st.toggle("Sonido en alertas nuevas", value=True)
    st.caption("Si no suena, haz clic en cualquier parte de la página: "
               "el navegador bloquea el audio hasta que interactúas.")

st.title("🛡️ Tres60 SafeCampus")
st.caption("Apoyo a la detección temprana. Cada alerta la confirma o descarta una persona.")

tab_monitoreo, tab_estadisticas, tab_config = st.tabs(
    ["📹 Monitoreo", "📊 Estadísticas", "⚙️ Configuración"]
)

# ----------------------------------------------------------------- monitoreo


@st.fragment(run_every="0.5s")
def video_en_vivo():
    if EN_VIVO.exists():
        try:
            st.image(EN_VIVO.read_bytes(), width="stretch")
        except OSError:
            pass
    else:
        st.info("Esperando video… inicia `python detector.py` en otra terminal.")


def tarjeta(db: Almacen, a):
    prioridad, color = PRIORIDAD.get(a["tipo"], ("Media", "orange"))
    with st.container(border=True):
        st.markdown(
            f"**{NOMBRES.get(a['tipo'], a['tipo'])}** :{color}-badge[Prioridad {prioridad}] · "
            f"{ESTADO_ICONO.get(a['estado'], a['estado'])}  \n"
            f"#{a['id']} · {hora(a['fecha'])} · {a['camara']}"
        )
        st.write(a["mensaje"])
        tiempos = []
        if a["duracion_s"] is not None:
            tiempos.append(f"⏱️ alerta {fmt_seg(a['duracion_s'])} después de empezar la situación")
        if a["latencia_ms"] is not None:
            tiempos.append(f"⚡ procesada en {a['latencia_ms']:.0f} ms")
        respuesta = segundos_entre(a["fecha"], a["revisada"])
        if respuesta is not None:
            tiempos.append(f"👤 revisada en {fmt_seg(respuesta)} ({a['revisado_por']})")
        atencion = segundos_entre(a["fecha"], a["atendida"])
        if atencion is not None:
            tiempos.append(f"🚓 atendida en {fmt_seg(atencion)} ({a['atendido_por']})")
        if tiempos:
            st.caption("  \n".join(tiempos))
        if a["imagen"] and Path(a["imagen"]).exists():
            with st.expander("Ver evidencia", expanded=a["estado"] == "nueva"):
                st.image(a["imagen"], width="stretch")
        if a["estado"] == "nueva":
            b1, b2 = st.columns(2)
            if b1.button("✅ Confirmar", key=f"ok{a['id']}", type="primary", width="stretch"):
                db.cambiar_estado(a["id"], "confirmada")
                st.rerun(scope="fragment")
            if b2.button("❌ Descartar", key=f"no{a['id']}", width="stretch"):
                db.cambiar_estado(a["id"], "descartada")
                st.rerun(scope="fragment")
        elif a["estado"] == "confirmada":
            if st.button("🚓 Marcar atendida", key=f"at{a['id']}", type="primary", width="stretch"):
                db.cambiar_estado(a["id"], "atendida")
                st.rerun(scope="fragment")


@st.fragment(run_every="2s")
def panel_alertas():
    db = almacen()
    conteo = db.contar_por_estado()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nuevas", conteo["nueva"])
    c2.metric("Por atender", conteo["confirmada"])
    c3.metric("Atendidas", conteo["atendida"])
    c4.metric("Descartadas", conteo["descartada"])

    alertas = db.listar(30)
    ultima = alertas[0]["id"] if alertas else 0
    vista = st.session_state.get("ultima_alerta_vista")
    if vista is not None and ultima > vista:
        nueva = alertas[0]
        st.toast(f"Nueva alerta: {NOMBRES.get(nueva['tipo'], nueva['tipo'])}", icon="🚨")
        if sonido:
            st.audio(pitido(), format="audio/wav", autoplay=True)
    st.session_state["ultima_alerta_vista"] = ultima

    solo_pendientes = st.toggle("Mostrar solo pendientes", key="solo_pendientes")
    if solo_pendientes:
        alertas = [a for a in alertas if a["estado"] in ("nueva", "confirmada")]
    if not alertas:
        st.write("Sin alertas por ahora.")
    for a in alertas:
        tarjeta(db, a)


with tab_monitoreo:
    col_video, col_alertas = st.columns([3, 2], gap="large")
    with col_video:
        st.subheader("En vivo")
        video_en_vivo()
    with col_alertas:
        st.subheader("Alertas")
        panel_alertas()

# -------------------------------------------------------------- estadísticas


def tabla_alertas() -> pd.DataFrame:
    filas = [dict(f) for f in almacen().listar(None)]
    df = pd.DataFrame(filas)
    if df.empty:
        return df
    df["situacion"] = df["tipo"].map(NOMBRES).fillna(df["tipo"])
    df["respuesta_s"] = [segundos_entre(f, r) for f, r in zip(df["fecha"], df["revisada"])]
    df["atencion_s"] = [segundos_entre(f, a) for f, a in zip(df["fecha"], df["atendida"])]
    df["hora"] = pd.to_datetime(df["fecha"]).dt.strftime("%H:00")
    return df


with tab_estadisticas:
    if st.button("🔄 Actualizar estadísticas"):
        st.rerun()
    df = tabla_alertas()
    if df.empty:
        st.info("Aún no hay alertas registradas.")
    else:
        revisadas = df[df["estado"] != "nueva"]
        utiles = df["estado"].isin(["confirmada", "atendida"]).sum()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Alertas totales", len(df))
        m2.metric(
            "Tasa de confirmación",
            f"{100 * utiles / len(revisadas):.0f} %" if len(revisadas) else "—",
            help="Alertas confirmadas o atendidas sobre las revisadas.",
        )
        m3.metric(
            "Tiempo de respuesta (mediana)", fmt_seg(df["respuesta_s"].median()),
            help="Desde que aparece la alerta hasta que una persona la confirma o descarta.",
        )
        m4.metric(
            "Procesamiento (mediana)",
            f"{df['latencia_ms'].median():.0f} ms" if df["latencia_ms"].notna().any() else "—",
            help="Desde que la cámara captura el fotograma hasta que se genera la alerta.",
        )

        st.subheader("Por tipo de situación")
        resumen = df.groupby("situacion").agg(
            alertas=("id", "count"),
            confirmadas=("estado", lambda s: s.isin(["confirmada", "atendida"]).sum()),
            descartadas=("estado", lambda s: (s == "descartada").sum()),
            alerta_tras_inicio_s=("duracion_s", "mean"),
            respuesta_media_s=("respuesta_s", "mean"),
            atencion_media_s=("atencion_s", "mean"),
        ).round(1)
        resumen.index.name = "Situación"
        resumen.columns = ["Alertas", "Confirmadas", "Descartadas",
                           "Alerta tras el inicio (s)", "Respuesta media (s)", "Atención media (s)"]
        st.dataframe(resumen, width="stretch")

        g1, g2 = st.columns(2)
        with g1:
            st.caption("Alertas por tipo")
            st.bar_chart(df["situacion"].value_counts())
        with g2:
            st.caption("Alertas por hora")
            st.bar_chart(df["hora"].value_counts().sort_index())

        st.subheader("Historial")
        columnas = ["id", "fecha", "camara", "situacion", "estado", "mensaje", "duracion_s",
                    "latencia_ms", "respuesta_s", "atencion_s", "revisado_por", "atendido_por"]
        st.dataframe(df[columnas], width="stretch", hide_index=True)
        st.download_button(
            "⬇️ Descargar historial (CSV)", df[columnas].to_csv(index=False).encode("utf-8"),
            "alertas_safecampus.csv", "text/csv",
        )

# ------------------------------------------------------------- configuración

with tab_config:
    st.subheader("Parámetros de detección")
    if not CONFIG_ACTIVA.exists():
        st.info("Inicia `python detector.py` para ver y ajustar sus parámetros.")
    else:
        cfg = yaml.safe_load(CONFIG_ACTIVA.read_text(encoding="utf-8"))
        reglas = cfg.get("reglas", {})
        ag = reglas.get("aglomeracion", {})
        ob = reglas.get("objeto_desatendido", {})
        su = reglas.get("persona_en_suelo", {})
        zo = reglas.get("zona_restringida", {})
        st.caption("Los cambios se aplican en vivo, en un segundo, sin reiniciar el detector. "
                   "Al reiniciarlo vuelve a usar los valores de config.yaml.")
        with st.form("parametros"):
            confianza = st.slider("Confianza mínima de detección", 0.1, 0.9,
                                  float(cfg.get("confianza", 0.4)), 0.05)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**👥 Aglomeración**")
                ag_on = st.checkbox("Activa", ag.get("activa", True), key="ag_on")
                ag_n = st.slider("Personas mínimas", 1, 50, int(ag.get("personas_min", 3)))
                ag_s = st.slider("Segundos sostenidos", 1, 300, int(ag.get("segundos", 5)), key="ag_s")

                st.markdown("**🚑 Persona en el suelo**")
                su_on = st.checkbox("Activa", su.get("activa", True), key="su_on")
                su_s = st.slider("Segundos en el suelo", 1, 120, int(su.get("segundos", 5)), key="su_s")
                su_p = st.slider("Proporción ancho/alto para considerar 'acostada'", 1.0, 3.0,
                                 float(su.get("proporcion", 1.3)), 0.1)
            with c2:
                st.markdown("**🎒 Objeto desatendido**")
                ob_on = st.checkbox("Activa", ob.get("activa", True), key="ob_on")
                ob_s = st.slider("Segundos sin nadie cerca (hipótesis real: 600)", 5, 1200,
                                 int(ob.get("segundos", 20)), key="ob_s")
                ob_m = st.slider("Tamaño del 'lugar' alrededor del objeto", 0.2, 3.0,
                                 float(ob.get("margen", 1.0)), 0.1)
                ob_r = st.slider("Segundos junto al objeto para reiniciar el conteo", 1, 30,
                                 int(ob.get("segundos_para_reiniciar", 3)))

                st.markdown("**⛔ Zona restringida**")
                zo_on = st.checkbox("Activa", zo.get("activa", False), key="zo_on")
                zona = zo.get("zona", [0.6, 0.0, 1.0, 1.0])
                zx = st.slider("Zona: horizontal (proporción del ancho)", 0.0, 1.0,
                               (float(zona[0]), float(zona[2])), 0.05)
                zy = st.slider("Zona: vertical (proporción del alto)", 0.0, 1.0,
                               (float(zona[1]), float(zona[3])), 0.05)
                zo_s = st.slider("Segundos dentro de la zona", 0, 30, int(zo.get("segundos", 2)), key="zo_s")

            if st.form_submit_button("Aplicar cambios", type="primary"):
                ajustes = {
                    "confianza": confianza,
                    "reglas": {
                        "aglomeracion": {"activa": ag_on, "personas_min": ag_n, "segundos": ag_s},
                        "objeto_desatendido": {"activa": ob_on, "segundos": ob_s, "margen": ob_m,
                                               "segundos_para_reiniciar": ob_r},
                        "persona_en_suelo": {"activa": su_on, "segundos": su_s, "proporcion": su_p},
                        "zona_restringida": {"activa": zo_on, "segundos": zo_s,
                                             "zona": [zx[0], zy[0], zx[1], zy[1]]},
                    },
                }
                tmp = AJUSTES.with_suffix(".tmp")
                tmp.write_text(yaml.safe_dump(ajustes, allow_unicode=True), encoding="utf-8")
                os.replace(tmp, AJUSTES)
                st.success("Cambios enviados al detector. Se aplican en un segundo.")
