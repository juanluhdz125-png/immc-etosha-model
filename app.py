import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(layout="wide", page_title="IMMC Etosha Dashboard")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Sistema de Gestión de Protección - Etosha")

# --- 1. GESTIÓN DE DATOS ---
if 'puntos' not in st.session_state:
    st.session_state['puntos'] = [
        {"name": "Gate Andersson", "x": 183, "y": -8, "r": 15, "color": "red"},
        {"name": "Camp Okaukuejo", "x": 160, "y": 5, "r": 10, "color": "orange"},
        {"name": "Hábitat Rino", "x": 100, "y": 30, "r": 20, "color": "blue"}
    ]

# --- 2. PANEL LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("⚙️ Panel de Control")
    
    # SECCIÓN PARA AÑADIR NUEVOS PUNTOS (Restaurada y mejorada)
    with st.expander("➕ Añadir Punto Nuevo", expanded=False):
        n_name = st.text_input("Nombre del punto", "Nuevo Punto")
        n_color = st.color_picker("Color del punto", "#4CAF50")
        if st.button("Añadir al Mapa"):
            st.session_state['puntos'].append({"name": n_name, "x": 150, "y": 20, "r": 15, "color": n_color})
            st.rerun()

    if st.button("🗑️ Reiniciar Todo"):
        del st.session_state['puntos']
        st.rerun()

    st.divider()
    st.subheader("📍 Editar Puntos Existentes")
    for i, p in enumerate(st.session_state['puntos']):
        with st.expander(f"Punto: {p['name']}", expanded=False):
            st.session_state['puntos'][i]['x'] = st.slider(f"X (Km)", -100, 500, p['x'], key=f"x_{i}")
            st.session_state['puntos'][i]['y'] = st.slider(f"Y (Km)", -100, 200, p['y'], key=f"y_{i}")
            st.session_state['puntos'][i]['r'] = st.slider(f"Radio (Km)", 1, 150, p['r'], key=f"r_{i}")

# --- 3. LÓGICA DE PROTECCIÓN (Cuantificación IMMC) ---
total_area = 22935 
impact_area = sum([np.pi * (p['r']**2) for p in st.session_state['puntos'] if p['color'] != 'blue'])
protection_score = max(0, 100 - (impact_area / total_area * 100))

# --- 4. VISUALIZACIÓN INTERACTIVA ---
col_map = st.container()

with col_map:
    m1, m2, m3 = st.columns(3)
  m1.metric("Puntuación de Protección", f"{protection_score:.1f}%")
    m2.metric("Efectivos Disponibles", "295") [cite: 9]
    m3.metric("Área Etosha", "22,935 km²") [cite: 6]

    fig = go.Figure()
    
    # Polígono de Etosha
    etosha_x = [10, 20, 70, 150, 280, 330, 320, 280, 160, 60, 10]
    etosha_y = [10, 45, 55, 60, 65, 50, 10, -5, -15, -5, 10]
    fig.add_trace(go.Scatter(x=etosha_x, y=etosha_y, fill="toself", fillcolor='rgba(46, 125, 50, 0.1)',
                             line=dict(color='#2E7D32', width=3), name="Límite Etosha", hoverinfo='skip'))

    # Dibujar Círculos y Puntos
    for p in st.session_state['puntos']:
        fig.add_shape(type="circle", xref="x", yref="y", x0=p['x']-p['r'], y0=p['y']-p['r'], 
                      x1=p['x']+p['r'], y1=p['y']+p['r'], line_color=p['color'], fillcolor=p['color'], opacity=0.3)
        fig.add_trace(go.Scatter(x=[p['x']], y=[p['y']], mode='markers+text', 
                                 marker=dict(size=14, color=p['color'], line=dict(width=2, color='white')),
                                 text=[f"{p['name']}<br>({p['x']}, {p['y']})"], textposition="top center", name=p['name']))

    # CONFIGURACIÓN DE INTERACCIÓN TIPO GOOGLE MAPS
    fig.update_layout(
        xaxis=dict(gridcolor='lightgray', zeroline=False),
        yaxis=dict(gridcolor='lightgray', scaleanchor="x", scaleratio=1, zeroline=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
        plot_bgcolor='white',
        dragmode='pan',  # Click izquierdo para arrastrar
        hovermode='closest'
    )

    # Habilitar Scroll Zoom y quitar botones que estorban
    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': True,        # SCROLL PARA ZOOM (Google Maps style)
        'displayModeBar': True,    # Mostrar barra para resetear zoom si te pierdes
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'displaylogo': False
    })

st.subheader("📊 Monitor de Coordenadas")
st.table(st.session_state['puntos'])
