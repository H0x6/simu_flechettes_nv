# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import io

def optimiser_taille_planche(niveau, nb_tirs=1000, seuil_couverture=98.0):
    target_center = (0, 173)
    target_radius = 22
    ecart_type = np.interp(niveau, [0, 10], [80, 8])
    x_tirs = np.random.normal(target_center[0], ecart_type, nb_tirs)
    y_tirs = np.random.normal(target_center[1], ecart_type, nb_tirs)
    for taille in range(60, 201, 2):
        planche_x_min = -taille / 2
        planche_x_max = taille / 2
        planche_y_min = target_center[1] - taille / 2
        planche_y_max = target_center[1] + taille / 2
        dans_cible = 0
        sur_planche = 0
        for x, y in zip(x_tirs, y_tirs):
            if np.hypot(x - target_center[0], y - target_center[1]) <= target_radius:
                dans_cible += 1
            elif (planche_x_min <= x <= planche_x_max) and (planche_y_min <= y <= planche_y_max):
                sur_planche += 1
        couverture = (dans_cible + sur_planche) / nb_tirs * 100
        if couverture >= seuil_couverture:
            return taille, couverture
    return None, None

def generate_pdf(niveau_moyen, largeur, hauteur, nb_tirs, stats_text, fig):
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png')
    img_buf.seek(0)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Rapport de simulation - Planche de fléchettes", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Paramètres de simulation :", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, f"- Niveau moyen des joueurs : {niveau_moyen:.1f}/10\n"
                         f"- Taille de la planche : {largeur} x {hauteur} cm\n"
                         f"- Nombre de tirs simulés : {nb_tirs}")
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Résultats :", ln=True)
    pdf.set_font("Arial", '', 11)
    for line in stats_text.split('\n'):
        pdf.cell(0, 8, line, ln=True)
    img_path = "/tmp/simulation_result.png"
    with open(img_path, "wb") as f:
        f.write(img_buf.read())
    pdf.image(img_path, x=30, w=150)
    pdf_path = "/tmp/rapport_flechettes.pdf"
    pdf.output(pdf_path)
    return pdf_path

def simulate(nb_tirs, niveau_moyen, planche_largeur, planche_hauteur):
    ecart_type = np.interp(niveau_moyen, [0, 10], [80, 8])
    target_center = (0, 173)
    target_radius = 22
    planche_x_min = -planche_largeur / 2
    planche_x_max = planche_largeur / 2
    planche_y_min = target_center[1] - planche_hauteur / 2
    planche_y_max = target_center[1] + planche_hauteur / 2
    x_coords, y_coords, colors = [], [], []
    nb_dans_cible = nb_sur_planche = nb_rate = 0
    for _ in range(nb_tirs):
        x = np.random.normal(target_center[0], ecart_type)
        y = np.random.normal(target_center[1], ecart_type)
        if np.hypot(x - target_center[0], y - target_center[1]) <= target_radius:
            colors.append("green"); nb_dans_cible += 1
        elif (planche_x_min <= x <= planche_x_max) and (planche_y_min <= y <= planche_y_max):
            colors.append("blue"); nb_sur_planche += 1
        else:
            colors.append("red"); nb_rate += 1
        x_coords.append(x)
        y_coords.append(y)
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.add_patch(plt.Rectangle((planche_x_min, planche_y_min), planche_largeur, planche_hauteur,
                               edgecolor='black', facecolor='lightyellow', lw=2))
    ax.add_patch(plt.Circle(target_center, target_radius, color='black', fill=False, lw=2))
    ax.scatter(x_coords, y_coords, c=colors, alpha=0.7)
    ax.set_xlim(-150, 150)
    ax.set_ylim(planche_y_min - 50, planche_y_max + 50)
    ax.set_aspect('equal')
    ax.set_title(f"Simulation de {nb_tirs} tirs", fontsize=12, pad=30)
    ax.set_xlabel("Largeur (cm)")
    ax.set_ylabel("Hauteur (cm)")
    plt.grid(True)
    stats_text = (
        f"Niveau moyen : {niveau_moyen:.2f}/10\n"
        f"Taille planche : {planche_largeur} x {planche_hauteur} cm\n"
        f"Résultats sur {nb_tirs} tirs :\n"
        f"- Dans la cible : {nb_dans_cible}\n"
        f"- Sur la planche : {nb_sur_planche}\n"
        f"- Ratées : {nb_rate} ({nb_rate / nb_tirs * 100:.1f}%)"
    )
    return fig, stats_text, x_coords, y_coords, colors

# === INTERFACE STREAMLIT ===
st.title("🎯 Simulateur de planche de fléchettes (avancé)")

nb_tirs = st.slider("Nombre de tirs", 100, 2000, 1000, 100)
niveau_1 = st.slider("Niveau joueur 1", 0.0, 10.0, 8.0, 0.5)
niveau_2 = st.slider("Niveau joueur 2", 0.0, 10.0, 8.0, 0.5)
niveau_3 = st.slider("Niveau joueur 3", 0.0, 10.0, 8.0, 0.5)
niveau_moyen = (niveau_1 + niveau_2 + niveau_3) / 3

planche_largeur = st.slider("Largeur planche (cm)", 50, 200, 114, 2)
planche_hauteur = st.slider("Hauteur planche (cm)", 50, 200, 144, 2)

# OPTIMISATION
if st.button("🔍 Calculer la taille carrée optimale"):
    taille_opt, couverture_opt = optimiser_taille_planche(niveau_moyen, nb_tirs)
    if taille_opt:
        st.success(f"Taille optimale : {taille_opt} × {taille_opt} cm (couverture {couverture_opt:.1f}%)")
    else:
        st.error("Aucune taille ne satisfait le seuil demandé.")

# Simulation
fig, stats, x_coords, y_coords, colors = simulate(nb_tirs, niveau_moyen, planche_largeur, planche_hauteur)
st.pyplot(fig)
st.code(stats)

# Export PDF
if st.button("📄 Générer le rapport PDF"):
    pdf_path = generate_pdf(niveau_moyen, planche_largeur, planche_hauteur, nb_tirs, stats, fig)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Télécharger le rapport PDF", f, file_name="rapport_flechettes.pdf")

# Vue Plotly 3D
if st.checkbox("🧊 Voir la vue 3D des tirs simulés"):
    z_coords = np.random.uniform(300, 400, nb_tirs)
    fig3d = go.Figure()
    for x, y, z, c in zip(x_coords, y_coords, z_coords, colors):
        fig3d.add_trace(go.Scatter3d(x=[x, x], y=[y, y], z=[z, 0],
                                     mode='lines+markers',
                                     line=dict(color=c, width=2),
                                     marker=dict(size=3, color=c),
                                     showlegend=False))
    planche_x = [-planche_largeur/2, planche_largeur/2, planche_largeur/2, -planche_largeur/2, -planche_largeur/2]
    planche_y = [173 - planche_hauteur/2]*2 + [173 + planche_hauteur/2]*2 + [173 - planche_hauteur/2]
    planche_z = [0]*5
    fig3d.add_trace(go.Scatter3d(x=planche_x, y=planche_y, z=planche_z,
                                 mode='lines', line=dict(color='black', width=4)))
    fig3d.update_layout(
        title="🧊 Vue 3D des trajectoires de fléchettes",
        scene=dict(
            xaxis_title='Largeur (cm)',
            yaxis_title='Hauteur (cm)',
            zaxis_title='Profondeur (cm)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1)),
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )
    st.plotly_chart(fig3d)
