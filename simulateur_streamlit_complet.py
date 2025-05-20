# -*- coding: utf-8 -*-


import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# === FONCTION D’OPTIMISATION ===
def optimiser_taille_planche(niveau, nb_tirs=1000, seuil_couverture=98.0):
    target_center = (0, 173)
    target_radius = 22
    ecart_type = np.interp(niveau, [0, 10], [80, 8])

    x_tirs = np.random.normal(target_center[0], ecart_type, nb_tirs)
    y_tirs = np.random.normal(target_center[1], ecart_type, nb_tirs)

    for taille in range(60, 201, 2):  # tailles testées de 60 à 200 cm
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

# === FONCTION DE SIMULATION ===
def simulate(nb_tirs, niveau_moyen, planche_largeur, planche_hauteur):
    ecart_type = np.interp(niveau_moyen, [0, 10], [80, 8])
    target_center = (0, 173)
    target_radius = 22

    planche_x_min = -planche_largeur / 2
    planche_x_max = planche_largeur / 2
    planche_y_min = target_center[1] - planche_hauteur / 2
    planche_y_max = target_center[1] + planche_hauteur / 2

    x_coords = []
    y_coords = []
    colors = []

    nb_dans_cible = 0
    nb_sur_planche = 0
    nb_rate = 0

    for _ in range(nb_tirs):
        x = np.random.normal(target_center[0], ecart_type)
        y = np.random.normal(target_center[1], ecart_type)

        if np.hypot(x - target_center[0], y - target_center[1]) <= target_radius:
            colors.append("green")
            nb_dans_cible += 1
        elif (planche_x_min <= x <= planche_x_max) and (planche_y_min <= y <= planche_y_max):
            colors.append("blue")
            nb_sur_planche += 1
        else:
            colors.append("red")
            nb_rate += 1

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

    return fig, stats_text

# === INTERFACE STREAMLIT ===
st.title("🎯 Simulateur de planche de fléchettes")

nb_tirs = st.slider("Nombre de tirs", 100, 2000, 1000, 100)
niveau_1 = st.slider("Niveau joueur 1", 0.0, 10.0, 8.0, 0.5)
niveau_2 = st.slider("Niveau joueur 2", 0.0, 10.0, 8.0, 0.5)
niveau_3 = st.slider("Niveau joueur 3", 0.0, 10.0, 8.0, 0.5)
niveau_moyen = (niveau_1 + niveau_2 + niveau_3) / 3

planche_largeur = st.slider("Largeur planche (cm)", 50, 200, 114, 2)
planche_hauteur = st.slider("Hauteur planche (cm)", 50, 200, 144, 2)



fig, stats = simulate(nb_tirs, niveau_moyen, planche_largeur, planche_hauteur)
st.pyplot(fig)
st.code(stats)

# === OPTIMISATION ===
with st.expander("🔎 Optimisation automatique de la taille de planche carrée"):
    if st.button("Calculer la taille optimale"):
        taille_opt, couverture_opt = optimiser_taille_planche(niveau_moyen, nb_tirs)
        if taille_opt:
            st.success(f"Taille optimale trouvée : {taille_opt} × {taille_opt} cm\n→ Couverture : {couverture_opt:.1f}%")
        else:
            st.error("Aucune taille trouvée pour atteindre le seuil de couverture.")



# Génération du PDF
if st.button("📄 Générer le rapport PDF"):
    pdf_path = generate_pdf(niveau_moyen, planche_largeur, planche_hauteur, nb_tirs, stats, fig)
    with open(pdf_path, "rb") as f:
        st.download_button("📥 Télécharger le rapport PDF", f, file_name="rapport_flechettes.pdf")

# === FIN DU CODE ===
