%%writefile app.py
import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuración estética
st.set_page_config(layout="wide", page_title="IMMC Etosha Dashboard")

# CSS personalizado para que se vea más limpio
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Sistema de Gestión de Protección - Etosha")

if 'puntos' not in st.session_state:
    st.session_state['puntos'] = [
        {"name": "Gate Andersson", "x": 183, "y": -8, "r": 15, "color": "red"},
        {"name": "Camp Okaukuejo", "x": 160, "y": 5, "r": 10, "color": "orange"},
        {"name": "Hábitat Rino", "x": 100, "y": 30, "r": 20, "color": "blue"}
    ]

# Layout de dos columnas: Controles a la izquierda, Mapa a la derecha
col_ctrl, col_map = st.columns([1, 2.5])

with col_ctrl:
    st.subheader("⚙️ Parámetros de Campo")
    
    for i, p in enumerate(st.session_state['puntos']):
        with st.expander(f"📍 {p['name']}", expanded=(i==0)):
            # Usamos sliders con 'on_change' para mejorar la respuesta si fuera local
            st.session_state['puntos'][i]['x'] = st.slider(f"X (Km)", -50, 400, p['x'], key=f"x_{i}")
            st.session_state['puntos'][i]['y'] = st.slider(f"Y (Km)", -50, 100, p['y'], key=f"y_{i}")
            st.session_state['puntos'][i]['r'] = st.slider(f"Radio (Km)", 1, 100, p['r'], key=f"r_{i}")

# Lógica de Protección (Cuantificación aproximada)
total_area = 22935 # km2 [cite: 6]
# Simulamos una métrica de "Área Bajo Influencia Humana"
impact_area = sum([np.pi * (p['r']**2) for p in st.session_state['puntos'] if p['color'] != 'blue'])
protection_score = max(0, 100 - (impact_area / total_area * 100))

with col_map:
    # Métricas rápidas arriba del mapa
    m1, m2, m3 = st.columns(3)
    m1.metric("Puntuación de Protección", f"{protection_score:.1f}%")
    m2.metric("Efectivos Disponibles", "295")
    m3.metric("Área Etosha", "22,935 km²")

    # Mapa interactivo Plotly
    fig = go.Figure()
    etosha_x = [10, 20, 70, 150, 280, 330, 320, 280, 160, 60, 10]
    etosha_y = [10, 45, 55, 60, 65, 50, 10, -5, -15, -5, 10]
    
    fig.add_trace(go.Scatter(x=etosha_x, y=etosha_y, fill="toself", fillcolor='rgba(46, 125, 50, 0.1)',
                             line=dict(color='#2E7D32', width=3), name="Límite Etosha"))

    for p in st.session_state['puntos']:
        fig.add_shape(type="circle", xref="x", yref="y", x0=p['x']-p['r'], y0=p['y']-p['r'], 
                      x1=p['x']+p['r'], y1=p['y']+p['r'], line_color=p['color'], fillcolor=p['color'], opacity=0.25)
        fig.add_trace(go.Scatter(x=[p['x']], y=[p['y']], mode='markers+text', 
                                 marker=dict(size=14, color=p['color'], line=dict(width=2, color='white')),
                                 text=[p['name']], textposition="top center"))

    fig.update_layout(xaxis=dict(range=[-60, 420]), yaxis=dict(range=[-50, 110], scaleanchor="x"),
                      margin=dict(l=0, r=0, t=0, b=0), height=600, plot_bgcolor='white')
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
