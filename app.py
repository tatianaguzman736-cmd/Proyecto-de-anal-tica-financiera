"""
ARVIX | Monitor de activos tecnológicos
Streamlit + yfinance + Plotly
"""
import base64

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="ARVIX | Monitor tecnológico", layout="wide",
                   initial_sidebar_state="expanded")

# ------------------------------------------------------------------
# Universo de activos
# ------------------------------------------------------------------
UNIVERSO = {
    "AAPL": ("Apple", "Hardware y consumo"),
    "MSFT": ("Microsoft", "Software y nube"),
    "NVDA": ("NVIDIA", "Semiconductores"),
    "GOOGL": ("Alphabet", "Internet y nube"),
    "AMZN": ("Amazon", "Internet y nube"),
    "META": ("Meta Platforms", "Internet y nube"),
    "AVGO": ("Broadcom", "Semiconductores"),
    "TSM": ("TSMC", "Semiconductores"),
    "AMD": ("AMD", "Semiconductores"),
    "ORCL": ("Oracle", "Software y nube"),
    "CRM": ("Salesforce", "Software y nube"),
    "ADBE": ("Adobe", "Software y nube"),
    "IBM": ("IBM", "Servicios TI"),
    "CSCO": ("Cisco", "Redes"),
    "PANW": ("Palo Alto Networks", "Ciberseguridad"),
    "CRWD": ("CrowdStrike", "Ciberseguridad"),
}
BENCHMARK = "QQQ"
PERIODOS = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1A": "1y", "2A": "2y", "5A": "5y"}
CAPITAL = 10_000

# ------------------------------------------------------------------
# Paleta
# ------------------------------------------------------------------
BG = "#0D0F14"
PANEL = "#161A22"
PANEL2 = "#1C212B"
BORDE = "#262C38"
TEXTO = "#E9ECF2"
MUTED = "#8A93A6"
LIMA = "#C6F432"
VIOLETA = "#8B5CF6"
SUBE = "#3DDC84"
BAJA = "#FF5C5C"
SERIES = [LIMA, VIOLETA, "#38BDF8", "#F59E0B", "#F472B6", "#34D399", "#A78BFA",
          "#FB7185", "#22D3EE", "#FACC15", "#60A5FA", "#E879F9", "#4ADE80",
          "#FDBA74", "#93C5FD", "#C084FC"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, [class*="css"], .stMarkdown, button, input {
  font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp {
  background: radial-gradient(1100px 520px at 85% -10%, rgba(139,92,246,.20), transparent 60%),
              radial-gradient(700px 400px at -5% 110%, rgba(198,244,50,.07), transparent 60%), __BG__;
  color: __TEXTO__; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.4rem; max-width: 1440px; }
section[data-testid="stSidebar"] { background: #10131A; border-right: 1px solid __BORDE__; }
section[data-testid="stSidebar"] label p { color: __MUTED__; font-weight: 600; }

.topbar { display:flex; justify-content:space-between; align-items:center; margin-bottom:1.2rem; }
.brand { display:flex; align-items:center; gap:.7rem; }
.brand-mark { width:38px; height:38px; border-radius:11px; background:__LIMA__; color:__BG__;
  display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.05rem; }
.brand-name { font-size:1.45rem; font-weight:800; color:__TEXTO__; line-height:1; }
.brand-sub { color:__MUTED__; font-size:.82rem; margin-top:.2rem; }
.chip { background:__PANEL__; border:1px solid __BORDE__; border-radius:999px; padding:.4rem .9rem;
  color:__MUTED__; font-size:.8rem; margin-left:.4rem; }

.card { background:__PANEL__; border:1px solid __BORDE__; border-radius:18px; padding:1.1rem 1.25rem; }
.card-title { color:__MUTED__; font-size:.85rem; font-weight:600; margin-bottom:.35rem; }
.big { font-size:2.3rem; font-weight:800; color:__TEXTO__; letter-spacing:-.02em; line-height:1.1; }
.muted { color:__MUTED__; font-size:.8rem; }
.row { display:flex; align-items:center; gap:.65rem; }
.between { display:flex; align-items:center; justify-content:space-between; gap:.5rem; }
.pill { border-radius:999px; padding:.15rem .6rem; font-weight:700; font-size:.76rem; white-space:nowrap; }
.up { background:rgba(61,220,132,.14); color:__SUBE__; }
.down { background:rgba(255,92,92,.14); color:__BAJA__; }
.logo { width:36px; height:36px; border-radius:11px; display:flex; align-items:center;
  justify-content:center; font-weight:800; font-size:.72rem; color:__BG__; flex-shrink:0; }

.tcard { background:__PANEL__; border:1px solid __BORDE__; border-radius:18px; padding:.95rem 1rem .9rem;
  margin-bottom:1rem; }
.tcard .tk { font-weight:800; color:__TEXTO__; font-size:.95rem; }
.tcard img { width:100%; height:48px; margin:.55rem 0 .45rem; display:block; }
.tcard .price { font-weight:800; color:__TEXTO__; font-size:1.15rem; }

.hero-stats { display:flex; gap:1.6rem; margin-top:.8rem; flex-wrap:wrap; }
.hero-stats div b { display:block; color:__TEXTO__; font-size:.98rem; }

.pos-row { display:flex; align-items:center; justify-content:space-between; padding:.6rem 0;
  border-top:1px solid __BORDE__; }
.pos-row:first-of-type { border-top:none; }
.pos-val { text-align:right; color:__TEXTO__; font-weight:700; font-size:.9rem; }

table.mt { width:100%; border-collapse:collapse; font-size:.86rem; }
table.mt th { color:__MUTED__; font-weight:600; text-align:right; padding:.7rem .6rem;
  border:none !important; border-bottom:1px solid __BORDE__ !important; background:transparent !important; }
table.mt th:first-child, table.mt td:first-child { text-align:left; }
table.mt td { color:__TEXTO__; text-align:right; padding:.7rem .6rem;
  border:none !important; border-bottom:1px solid __BORDE__ !important; }
table.mt tr:hover td { background:__PANEL2__; }
table.mt td.pos { color:__SUBE__; } table.mt td.neg { color:__BAJA__; }

.stTabs [data-baseweb="tab-list"], .stTabs [role="tablist"] { gap:.35rem; background:__PANEL__; padding:.35rem; border-radius:14px;
  border:1px solid __BORDE__; width:fit-content; }
.stTabs [data-baseweb="tab"], .stTabs [role="tab"] { border-radius:10px; padding:.45rem 1rem; color:__MUTED__; height:auto; }
.stTabs [aria-selected="true"] { background:__LIMA__ !important; color:__BG__ !important; }
.stTabs [aria-selected="true"] p { color:__BG__ !important; font-weight:700; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"],
.stTabs .react-aria-SelectionIndicator { display:none !important; }
.stTabs [role="tab"] p { color:__MUTED__; }

div[data-testid="stPlotlyChart"] { background:__PANEL__; border:1px solid __BORDE__; border-radius:18px;
  padding:.5rem .4rem .2rem; }
.stDownloadButton button { background:__LIMA__ !important; color:__BG__ !important; border:none !important;
  border-radius:10px !important; font-weight:700 !important; }
span[data-baseweb="tag"], .stMultiSelect [data-tag] { background:rgba(198,244,50,.14) !important;
  border:1px solid rgba(198,244,50,.35) !important; }
span[data-baseweb="tag"] *, .stMultiSelect [data-tag] * { color:__LIMA__ !important; fill:__LIMA__ !important; }
.guia { background:rgba(198,244,50,.05); border:1px solid __BORDE__; border-left:3px solid __LIMA__;
  border-radius:12px; padding:.8rem 1rem; color:#C9CFDA; font-size:.88rem; line-height:1.6; margin:.4rem 0 1.1rem; }
.guia b { color:__TEXTO__; }
.guia ul { margin:.3rem 0 0 1.1rem; padding:0; } .guia li { margin:.2rem 0; }
.sec { font-size:1.15rem; font-weight:800; color:__TEXTO__; margin:1.3rem 0 .15rem; }
.sec-sub { color:__MUTED__; font-size:.86rem; margin-bottom:.8rem; }
.intro { background:linear-gradient(120deg, rgba(139,92,246,.22), rgba(198,244,50,.06));
  border:1px solid __BORDE__; border-radius:18px; padding:1.1rem 1.3rem; margin-bottom:1rem;
  color:#D5DAE3; font-size:.92rem; line-height:1.6; }
.intro b { color:__TEXTO__; }
.nota { color:__MUTED__; font-size:.78rem; line-height:1.5; }
</style>
"""
for k, v in {"__BG__": BG, "__PANEL2__": PANEL2, "__PANEL__": PANEL, "__BORDE__": BORDE,
             "__TEXTO__": TEXTO, "__MUTED__": MUTED, "__LIMA__": LIMA, "__SUBE__": SUBE,
             "__BAJA__": BAJA}.items():
    CSS = CSS.replace(k, v)
st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------------
def html(contenido):
    st.markdown(contenido, unsafe_allow_html=True)


def estilo(fig, alto=420, titulo=None):
    fig.update_layout(
        height=alto, template="plotly_dark",
        title=dict(text=titulo, font=dict(size=15, color=TEXTO), x=0.01) if titulo else None,
        font=dict(family="Plus Jakarta Sans, sans-serif", color=MUTED, size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=55 if titulo else 15, b=10),
        legend=dict(orientation="h", yanchor="top", y=-0.08, x=0, bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=PANEL2, bordercolor=BORDE, font_color=TEXTO),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDE, zeroline=False)
    fig.update_yaxes(gridcolor="#20252F", zeroline=False, linecolor=BORDE)
    return fig


def mostrar(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def seccion(titulo, subtitulo):
    html(f'<div class="sec">{titulo}</div><div class="sec-sub">{subtitulo}</div>')


def guia(texto, titulo="Cómo leerlo"):
    html(f'<div class="guia"><b>{titulo}.</b> {texto}</div>')


def nombre(t):
    return UNIVERSO.get(t, ("Nasdaq-100 (ETF)", "Referencia"))[0]


def pill(v, sufijo=""):
    clase = "up" if v >= 0 else "down"
    flecha = "▲" if v >= 0 else "▼"
    return f'<span class="pill {clase}">{flecha} {abs(v):.2%}{sufijo}</span>'


def sparkline(s, color, w=200, h=48):
    s = s.dropna()
    if len(s) > 150:
        s = s.iloc[:: max(1, len(s) // 150)]
    y = s.values.astype(float)
    if len(y) < 2:
        return ""
    mn, mx = y.min(), y.max()
    rng = (mx - mn) or 1.0
    xs = np.linspace(0, w, len(y))
    ys = h - 3 - (y - mn) / rng * (h - 6)
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in zip(xs, ys))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="none">'
           f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0" stop-color="{color}" stop-opacity="0.35"/>'
           f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
           f'<polygon points="0,{h} {pts} {w},{h}" fill="url(#g)"/>'
           f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" '
           f'stroke-linejoin="round" stroke-linecap="round"/></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


# ------------------------------------------------------------------
# Datos
# ------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def cargar_cierres(tickers, periodo):
    data = yf.download(list(tickers), period=periodo, auto_adjust=True,
                       progress=False, threads=True)
    if data is None or data.empty:
        return pd.DataFrame()
    cierres = data["Close"]
    if isinstance(cierres, pd.Series):
        cierres = cierres.to_frame(tickers[0])
    return cierres.dropna(how="all")


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_ohlc(ticker, periodo):
    return yf.Ticker(ticker).history(period=periodo, auto_adjust=True)


def metricas(cierres):
    filas = []
    for t in cierres.columns:
        s = cierres[t].dropna()
        if len(s) < 3:
            continue
        r = s.pct_change().dropna()
        total = s.iloc[-1] / s.iloc[0] - 1
        anual = (1 + total) ** (252 / len(s)) - 1
        vol = r.std() * np.sqrt(252)
        filas.append({
            "Ticker": t, "Empresa": nombre(t),
            "Segmento": UNIVERSO.get(t, ("", "Referencia"))[1],
            "Precio (USD)": s.iloc[-1],
            "Var. día": s.iloc[-1] / s.iloc[-2] - 1,
            "Rend. periodo": total,
            "Rend. anualizado": anual,
            "Volatilidad anual": vol,
            "Caída máxima": (s / s.cummax() - 1).min(),
            "Retorno / riesgo": anual / vol if vol else np.nan,
        })
    if not filas:
        return pd.DataFrame()
    return pd.DataFrame(filas).set_index("Ticker")


# ------------------------------------------------------------------
# Barra lateral
# ------------------------------------------------------------------
with st.sidebar:
    html(f'<div class="brand" style="margin:.3rem 0 1.4rem"><div class="brand-mark">AX</div>'
         f'<div><div class="brand-name">ARVIX</div>'
         f'<div class="brand-sub">Monitor tecnológico</div></div></div>')
    seleccion = st.multiselect(
        "Empresas", options=list(UNIVERSO.keys()),
        default=["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"],
        format_func=lambda t: f"{t} · {UNIVERSO[t][0]}")
    periodo_txt = st.segmented_control("Periodo", list(PERIODOS.keys()), default="1A") \
        if hasattr(st, "segmented_control") else \
        st.radio("Periodo", list(PERIODOS.keys()), index=3, horizontal=True)
    periodo_txt = periodo_txt or "1A"
    incluir_bench = st.toggle("Comparar con Nasdaq-100 (QQQ)", value=True)
    detalle = st.selectbox("Activo en detalle", seleccion or ["AAPL"],
                           format_func=lambda t: f"{t} · {nombre(t)}")
    st.markdown("---")
    html('<p class="nota">Fuente: Yahoo Finance vía yfinance. Precios ajustados por dividendos '
         'y splits. Uso académico. No constituye recomendación de inversión. Los resultados '
         'históricos no garantizan rendimientos futuros.</p>')

periodo = PERIODOS[periodo_txt]

if not seleccion:
    st.info("Seleccione al menos una empresa en la barra lateral para iniciar el análisis.")
    st.stop()

tickers = tuple(seleccion + ([BENCHMARK] if incluir_bench else []))
with st.spinner("Descargando precios de mercado..."):
    cierres = cargar_cierres(tickers, periodo)

if cierres.empty:
    st.error("Yahoo Finance no devolvió datos. Espere un minuto y recargue la página; "
             "el servicio limita las consultas frecuentes.")
    st.stop()

tabla = metricas(cierres)
activos = [t for t in seleccion if t in tabla.index]
if not activos:
    st.error("No hay datos suficientes para las empresas seleccionadas en este periodo.")
    st.stop()

colores = {t: SERIES[i % len(SERIES)] for i, t in enumerate(seleccion)}
colores[BENCHMARK] = MUTED
ultima_fecha = cierres.index.max().strftime("%d/%m/%Y")

# ------------------------------------------------------------------
# Encabezado
# ------------------------------------------------------------------
html(f'<div class="topbar"><div><div class="brand-name" style="font-size:1.7rem">Panel de mercado</div>'
     f'<div class="brand-sub">Acciones tecnológicas · periodo {periodo_txt}</div></div>'
     f'<div><span class="chip">Último cierre {ultima_fecha}</span>'
     f'<span class="chip">{len(activos)} activos</span></div></div>')

html('<div class="intro"><b>¿Qué muestra esta plataforma?</b> Compara cómo se han comportado '
     'las acciones de grandes empresas tecnológicas en el periodo elegido. Responde tres preguntas: '
     '<b>cuál ganó más</b>, <b>cuál tuvo más riesgo</b> y <b>si se mueven juntas</b>. '
     'Use la barra lateral para cambiar las empresas, el periodo o el activo en detalle; '
     'todos los gráficos y conclusiones se recalculan automáticamente.</div>')

t_act = tabla.loc[activos]
mejor = t_act["Rend. periodo"].idxmax()
peor = t_act["Rend. periodo"].idxmin()
mas_vol = t_act["Volatilidad anual"].idxmax()
menos_vol = t_act["Volatilidad anual"].idxmin()
mejor_rr = t_act["Retorno / riesgo"].idxmax()
puntos = [
    f"<b>{nombre(mejor)} ({mejor})</b> fue la que más subió: {t_act.loc[mejor, 'Rend. periodo']:+.1%}.",
    f"<b>{nombre(peor)} ({peor})</b> tuvo el peor resultado: {t_act.loc[peor, 'Rend. periodo']:+.1%}."
    if peor != mejor else "",
    f"La más riesgosa (precio más inestable) fue <b>{mas_vol}</b>, con volatilidad de "
    f"{t_act.loc[mas_vol, 'Volatilidad anual']:.1%} al año; la más estable fue <b>{menos_vol}</b> "
    f"({t_act.loc[menos_vol, 'Volatilidad anual']:.1%}).",
    f"La mejor relación entre ganancia y riesgo la tuvo <b>{mejor_rr}</b>.",
]
if incluir_bench and BENCHMARK in tabla.index:
    q = tabla.loc[BENCHMARK, "Rend. periodo"]
    superan = [t for t in activos if t_act.loc[t, "Rend. periodo"] > q]
    puntos.append(f"El Nasdaq-100 (QQQ), que sirve de referencia del sector, rindió {q:+.1%}. "
                  f"Lo superaron {len(superan)} de {len(activos)} empresas"
                  f"{': ' + ', '.join(superan) if superan else ''}.")
html('<div class="guia"><b>Resumen del periodo.</b><ul>'
     + "".join(f"<li>{p}</li>" for p in puntos if p) + '</ul></div>')

# ------------------------------------------------------------------
# Tarjetas por activo
# ------------------------------------------------------------------
seccion("Cómo va cada empresa",
        "Precio de cierre más reciente y comportamiento durante el periodo seleccionado.")
for i in range(0, len(activos), 5):
    cols = st.columns(5)
    for col, t in zip(cols, activos[i:i + 5]):
        f = tabla.loc[t]
        color = SUBE if f["Rend. periodo"] >= 0 else BAJA
        with col:
            html(f'<div class="tcard">'
                 f'<div class="between"><div class="row">'
                 f'<div class="logo" style="background:{colores[t]}">{t[:4]}</div>'
                 f'<div><div class="tk">{t}</div><div class="muted">{f["Empresa"]}</div></div></div>'
                 f'{pill(f["Rend. periodo"])}</div>'
                 f'<img src="{sparkline(cierres[t], color)}"/>'
                 f'<div class="between"><div class="price">${f["Precio (USD)"]:,.2f}</div>'
                 f'<div class="muted">Hoy {f["Var. día"]:+.2%}</div></div></div>')

guia("La etiqueta de color indica cuánto subió (verde) o bajó (rojo) la acción en todo el periodo. "
     "La línea muestra el recorrido del precio. Abajo aparece el precio actual en dólares y la "
     "variación del último día.")

seccion("Activo en detalle y portafolio simulado",
        "A la izquierda, la historia diaria de una acción. A la derecha, qué habría pasado si "
        f"se invertían {CAPITAL:,.0f} USD repartidos entre las empresas elegidas.")

# ------------------------------------------------------------------
# Bloque principal: velas + portafolio
# ------------------------------------------------------------------
izq, der = st.columns([2.15, 1], gap="medium")

with izq:
    ohlc = cargar_ohlc(detalle, periodo)
    if detalle in tabla.index and not ohlc.empty:
        f = tabla.loc[detalle]
        html(f'<div class="card" style="margin-bottom:.8rem">'
             f'<div class="between"><div class="row">'
             f'<div class="logo" style="background:{colores.get(detalle, LIMA)}">{detalle[:4]}</div>'
             f'<div><div class="tk" style="font-weight:800">{nombre(detalle)}</div>'
             f'<div class="muted">{detalle} · NASDAQ / NYSE · USD</div></div></div>'
             f'{pill(f["Var. día"], " hoy")}</div>'
             f'<div class="big" style="margin-top:.7rem">${f["Precio (USD)"]:,.2f}</div>'
             f'<div class="hero-stats">'
             f'<div class="muted">Máximo<b>${ohlc["High"].max():,.2f}</b></div>'
             f'<div class="muted">Mínimo<b>${ohlc["Low"].min():,.2f}</b></div>'
             f'<div class="muted">Rend. periodo<b>{f["Rend. periodo"]:+.2%}</b></div>'
             f'<div class="muted">Volatilidad anual<b>{f["Volatilidad anual"]:.1%}</b></div>'
             f'<div class="muted">Caída máxima<b>{f["Caída máxima"]:.1%}</b></div>'
             f'</div></div>')

        ohlc = ohlc.copy()
        ohlc["MM50"] = ohlc["Close"].rolling(50).mean()
        ohlc["MM200"] = ohlc["Close"].rolling(200).mean()
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.78, 0.22], vertical_spacing=0.03)
        fig.add_trace(go.Candlestick(
            x=ohlc.index, open=ohlc["Open"], high=ohlc["High"], low=ohlc["Low"],
            close=ohlc["Close"], name="Precio",
            increasing=dict(line=dict(color=SUBE), fillcolor=SUBE),
            decreasing=dict(line=dict(color=BAJA), fillcolor=BAJA)), row=1, col=1)
        for mm, c in [("MM50", VIOLETA), ("MM200", "#F59E0B")]:
            if ohlc[mm].notna().any():
                fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc[mm], name=mm,
                                         line=dict(color=c, width=1.6)), row=1, col=1)
        vol_color = np.where(ohlc["Close"] >= ohlc["Open"],
                             "rgba(61,220,132,.45)", "rgba(255,92,92,.45)")
        fig.add_trace(go.Bar(x=ohlc.index, y=ohlc["Volume"], marker_color=vol_color,
                             name="Volumen", showlegend=False), row=2, col=1)
        fig.update_layout(xaxis_rangeslider_visible=False)
        mostrar(estilo(fig, 520))
        guia("Cada barra es un día. <b>Verde</b>: el precio cerró más alto de lo que abrió. "
             "<b>Rojo</b>: cerró más bajo. La línea violeta (MM50) es el promedio de los últimos "
             "50 días y la naranja (MM200), el de 200 días; muestran la tendencia sin el ruido "
             "diario. Si el precio está por encima de esas líneas, la tendencia es alcista. "
             "Las barras de abajo indican cuántas acciones se negociaron cada día (volumen).")
    else:
        st.warning("No hay precios diarios para este activo en este momento.")

with der:
    base = cierres[activos].ffill().bfill()
    norm = base / base.iloc[0]
    portafolio = norm.mean(axis=1) * CAPITAL
    rend_port = portafolio.iloc[-1] / CAPITAL - 1

    html(f'<div class="card" style="margin-bottom:.8rem; '
         f'background:linear-gradient(135deg, rgba(139,92,246,.35), {PANEL} 70%);">'
         f'<div class="card-title">Portafolio simulado</div>'
         f'<div class="big">${portafolio.iloc[-1]:,.0f}</div>'
         f'<div class="row" style="margin-top:.4rem">{pill(rend_port)}'
         f'<span class="muted">sobre ${CAPITAL:,.0f} invertidos al inicio</span></div></div>')

    fig = go.Figure(go.Scatter(
        x=portafolio.index, y=portafolio, mode="lines", fill="tozeroy",
        line=dict(color=VIOLETA, width=2.4), fillcolor="rgba(139,92,246,.18)",
        hovertemplate="$%{y:,.0f}<extra></extra>", name="Portafolio"))
    fig.update_yaxes(range=[portafolio.min() * 0.97, portafolio.max() * 1.02])
    mostrar(estilo(fig, 200))

    filas = ""
    asignacion = CAPITAL / len(activos)
    for t in activos:
        v = asignacion * norm[t].iloc[-1]
        cambio = norm[t].iloc[-1] - 1
        filas += (f'<div class="pos-row"><div class="row">'
                  f'<div class="logo" style="background:{colores[t]};width:32px;height:32px">{t[:4]}</div>'
                  f'<div><div class="tk" style="font-weight:700">{t}</div>'
                  f'<div class="muted">{nombre(t)}</div></div></div>'
                  f'<div class="pos-val">${v:,.0f}<br>{pill(cambio)}</div></div>')
    html(f'<div class="card"><div class="card-title">Posiciones</div>{filas}'
         f'<div class="nota" style="margin-top:.6rem">Simulación: ${asignacion:,.0f} por empresa '
         f'al inicio del periodo, sin rebalanceo ni comisiones.</div></div>')
    guia(f"Si al inicio del periodo se hubieran invertido {CAPITAL:,.0f} USD, "
         f"{asignacion:,.0f} en cada empresa, hoy valdrían <b>{portafolio.iloc[-1]:,.0f} USD</b> "
         f"({rend_port:+.1%}). Así se ve el efecto de no depender de una sola acción.")

st.write("")

# ------------------------------------------------------------------
# Análisis
# ------------------------------------------------------------------
seccion("Análisis comparativo",
        "Cada pestaña responde una pregunta: ¿cuál ganó más?, ¿cuál fue más riesgosa?, "
        "¿se mueven juntas? y la tabla con todas las cifras.")
tab1, tab2, tab3, tab4 = st.tabs(["Rendimiento", "Riesgo y retorno", "Correlación", "Métricas"])

with tab1:
    base100 = cierres.apply(lambda s: s / s.dropna().iloc[0] * 100)
    fig = go.Figure()
    for t in base100.columns:
        fig.add_trace(go.Scatter(
            x=base100.index, y=base100[t], name=t, mode="lines",
            line=dict(color=colores.get(t, MUTED), width=2.2,
                      dash="dot" if t == BENCHMARK else "solid"),
            hovertemplate="%{y:.1f}"))
    fig.add_hline(y=100, line_color=BORDE, line_width=1)
    mostrar(estilo(fig, 460, "Evolución de 100 USD invertidos"))
    fin_mejor = base100[mejor].dropna().iloc[-1]
    guia("Todas las acciones arrancan en 100 para poder compararlas aunque tengan precios muy "
         "distintos. Una línea por encima de 100 significa ganancia; por debajo, pérdida. "
         + ("La línea punteada gris es el Nasdaq-100: las empresas que terminan por encima de ella "
            "le ganaron al sector. " if incluir_bench else "")
         + f"Ejemplo: 100 USD invertidos en {nombre(mejor)} hoy serían <b>{fin_mejor:,.0f} USD</b>.")

    orden = tabla.sort_values("Rend. periodo")
    fig = go.Figure(go.Bar(
        x=orden["Rend. periodo"], y=orden.index, orientation="h",
        marker=dict(color=[LIMA if v >= 0 else BAJA for v in orden["Rend. periodo"]]),
        text=[f"{v:+.1%}" for v in orden["Rend. periodo"]], textposition="outside",
        textfont=dict(color=TEXTO)))
    fig.update_xaxes(tickformat=".0%")
    fig.update_layout(hovermode=False)
    mostrar(estilo(fig, 90 + 40 * len(orden), "Ranking de rendimiento del periodo"))
    guia("Ordena las acciones de mayor a menor ganancia en el periodo. Barras verdes: ganaron. "
         "Barras rojas: perdieron.")

with tab2:
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        datos = tabla.reset_index()
        fig = px.scatter(datos, x="Volatilidad anual", y="Rend. anualizado", text="Ticker",
                         color="Ticker", hover_name="Empresa",
                         color_discrete_map={t: colores.get(t, MUTED) for t in datos["Ticker"]})
        fig.update_traces(marker=dict(size=18, line=dict(width=2, color=BG)),
                          textposition="top center", textfont=dict(color=TEXTO))
        fig.update_xaxes(tickformat=".0%", title="Volatilidad anualizada")
        fig.update_yaxes(tickformat=".0%", title="Rend. anualizado")
        fig.update_layout(hovermode="closest", showlegend=False)
        fig.update_yaxes(automargin=True)
        fig = estilo(fig, 460, "Mapa de riesgo y retorno")
        fig.update_layout(margin=dict(l=85))
        mostrar(fig)
        guia(f"Eje horizontal: riesgo (qué tanto sube y baja el precio). Eje vertical: ganancia "
             f"promedio por año. Lo ideal es estar <b>arriba y a la izquierda</b>: más ganancia con "
             f"menos riesgo. En este periodo, la mejor ubicada es <b>{mejor_rr}</b>.")
    with c2:
        dd = cierres.apply(lambda s: s / s.cummax() - 1)
        fig = go.Figure()
        for t in dd.columns:
            fig.add_trace(go.Scatter(x=dd.index, y=dd[t], name=t,
                                     line=dict(color=colores.get(t, MUTED), width=1.8),
                                     hovertemplate="%{y:.1%}"))
        fig.update_yaxes(tickformat=".0%")
        mostrar(estilo(fig, 460, "Caída desde el máximo previo"))
        peor_dd = t_act["Caída máxima"].idxmin()
        guia(f"Muestra cuánto había perdido cada acción frente a su precio más alto hasta ese día. "
             f"0% significa que estaba en su máximo. La caída más fuerte la tuvo "
             f"<b>{peor_dd}</b>: {t_act.loc[peor_dd, 'Caída máxima']:.1%}. Es el peor momento "
             f"que habría vivido un inversionista.")

with tab3:
    if cierres.shape[1] < 2:
        st.info("Seleccione al menos dos activos para calcular correlaciones.")
    else:
        corr = cierres.pct_change().corr()
        fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, aspect="auto",
                        color_continuous_scale=[[0, BAJA], [0.5, PANEL2], [1, LIMA]])
        fig.update_layout(hovermode=False)
        mostrar(estilo(fig, 500, "Correlación de rendimientos diarios"))
        sub = corr.loc[activos, activos] if len(activos) > 1 else corr
        pares = sub.where(np.triu(np.ones(sub.shape, dtype=bool), k=1)).stack()
        texto = ("Mide si dos acciones suben y bajan al mismo tiempo, en una escala de −1 a 1. "
                 "<b>Cerca de 1</b>: se mueven casi igual, así que tenerlas juntas protege poco. "
                 "<b>Cerca de 0</b>: se mueven de forma independiente, lo que diversifica mejor. ")
        if len(pares):
            a, b = pares.idxmax()
            texto += (f"El par más parecido es <b>{a} y {b}</b> ({pares.max():.2f}) y la correlación "
                      f"promedio entre las empresas elegidas es {pares.mean():.2f}.")
        guia(texto)

with tab4:
    def celda(v, fmt, color=True):
        clase = ("pos" if v >= 0 else "neg") if color else ""
        return f'<td class="{clase}">{format(v, fmt)}</td>'

    cuerpo = ""
    for t, f in tabla.iterrows():
        cuerpo += (f'<tr><td><b>{t}</b> <span class="muted">{f["Empresa"]}</span></td>'
                   f'<td>${f["Precio (USD)"]:,.2f}</td>'
                   f'{celda(f["Var. día"], "+.2%")}{celda(f["Rend. periodo"], "+.2%")}'
                   f'{celda(f["Rend. anualizado"], "+.2%")}'
                   f'{celda(f["Volatilidad anual"], ".2%", False)}'
                   f'{celda(f["Caída máxima"], ".2%")}'
                   f'{celda(f["Retorno / riesgo"], ".2f", False)}</tr>')
    html(f'<div class="card"><table class="mt"><thead><tr><th>Activo</th><th>Precio</th>'
         f'<th>Var. día</th><th>Rend. periodo</th><th>Rend. anualizado</th>'
         f'<th>Volatilidad</th><th>Caída máx.</th><th>Retorno / riesgo</th></tr></thead>'
         f'<tbody>{cuerpo}</tbody></table>'
         f'<p class="nota" style="margin-top:.8rem">Retorno / riesgo = rendimiento anualizado ÷ '
         f'volatilidad anualizada. No descuenta tasa libre de riesgo.</p></div>')
    guia("Resume todas las cifras. <b>Rend. periodo</b>: ganancia total. <b>Rend. anualizado</b>: "
         "ganancia promedio por año. <b>Volatilidad</b>: riesgo. <b>Caída máx.</b>: peor pérdida desde "
         "un máximo. <b>Retorno / riesgo</b>: cuánta ganancia se obtuvo por cada unidad de riesgo; "
         "mientras más alto, mejor.")
    d1, d2, _ = st.columns([1, 1, 3])
    d1.download_button("Descargar métricas", tabla.to_csv().encode("utf-8-sig"),
                       file_name="metricas_arvix.csv", mime="text/csv")
    d2.download_button("Descargar precios", cierres.to_csv().encode("utf-8-sig"),
                       file_name="precios_arvix.csv", mime="text/csv")

st.write("")
with st.expander("Glosario de términos"):
    html("""<div class="guia" style="margin:0">
<b>Acción:</b> una parte de la propiedad de una empresa que se compra y vende en bolsa.<br>
<b>Ticker:</b> código corto que identifica una acción en la bolsa (por ejemplo, AAPL es Apple).<br>
<b>Nasdaq-100 (QQQ):</b> fondo que agrupa las 100 empresas no financieras más grandes del Nasdaq; se usa como referencia del sector tecnológico.<br>
<b>Rendimiento:</b> cuánto ganó o perdió una inversión, en porcentaje.<br>
<b>Volatilidad:</b> qué tanto sube y baja el precio. A mayor volatilidad, mayor riesgo.<br>
<b>Caída máxima (drawdown):</b> la mayor pérdida desde un precio máximo hasta un mínimo posterior.<br>
<b>Media móvil:</b> promedio del precio de los últimos días; suaviza la tendencia.<br>
<b>Correlación:</b> grado en que dos acciones se mueven en la misma dirección.<br>
<b>Diversificación:</b> repartir la inversión para no depender de un solo activo.<br>
<b>Precio ajustado:</b> precio corregido por dividendos y divisiones de acciones, para comparar en el tiempo.
</div>""")
