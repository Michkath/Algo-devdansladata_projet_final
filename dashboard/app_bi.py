"""
TourismeData — Dashboard BI Premium
=====================================
Auteur  : Ben Youssef Sajed Rôle : BI / Data Analyst
Projet  : Pipeline Data Engineering & BI sur les hébergements touristiques français
"""

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# ==============================================================================
# 0. CONFIGURATION DE LA PAGE & DESIGN
# ==============================================================================
st.set_page_config(
    page_title="TourismeData — BI",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Allégé - Laisse Streamlit gérer le Mode Sombre / Mode Clair automatiquement
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=DM+Sans:wght@400;500&display=swap');
    .main-header { font-family: 'Cormorant Garamond', serif; font-size: 2.8rem; font-weight: 700; }
    .main-header span { color: #D4AF37; }
    /* Cartes KPI transparentes pour s'adapter au thème clair/sombre */
    .kpi-card { border-radius: 10px; padding: 1.5rem; border-top: 4px solid #D4AF37; background-color: rgba(128, 128, 128, 0.1); }
    .kpi-label { font-size: 0.8rem; text-transform: uppercase; font-weight: 500; opacity: 0.7; }
    .kpi-value { font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; font-weight: 700; }
    .gold-divider { height: 2px; background: linear-gradient(to right, #D4AF37, transparent); border: none; margin: 1.5rem 0; }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-header">Tourisme<span>Data</span> 📊</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div style="opacity: 0.7; font-size: 1.1rem; margin-bottom: 20px;">Business Intelligence · Dashboard décisionnel des Hébergements Classés</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)


# ==============================================================================
# 1. ACQUISITION DES DONNÉES
# ==============================================================================
@st.cache_data(ttl=300, show_spinner=False)
def load_all_data() -> pd.DataFrame:
    try:
        # Un seul appel vers l'endpoint d'export (tous les enregistrements d'un coup)
        response = requests.get("http://127.0.0.1:5000/hebergements/export", timeout=30)
        response.raise_for_status()

        raw = response.json()
        items = raw.get("hebergements", [])

        if not items:
            return pd.DataFrame()

        df = pd.DataFrame(items)

        # Nettoyage des colonnes critiques
        if "classement" in df.columns:
            df["etoiles"] = (
                df["classement"].astype(str).str.extract(r"(\d+)").astype(float)
            )
        for col in ("capacite_accueil", "nombre_chambres"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Création du code département pour la carte
        if "code_postal" in df.columns:
            df["code_postal"] = df["code_postal"].astype(str).str.zfill(5)
            df["dept_code"] = df["code_postal"].str[:2]
            # Gestion de la Corse
            df.loc[df["code_postal"].str.startswith("20"), "dept_code"] = (
                df.loc[df["code_postal"].str.startswith("20"), "code_postal"]
                .str[:3]
                .map(lambda x: "2A" if x <= "201" else "2B")
            )

        return df
    except Exception as exc:
        st.error(f"🔌 Erreur API. Vérifiez que Flask tourne sur le port 5000. ({exc})")
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def load_geojson():
    url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
    try:
        return requests.get(url, timeout=10).json()
    except:
        return {}


with st.spinner("⏳ Récupération des données depuis l'API..."):
    df_brut = load_all_data()

if df_brut.empty:
    st.warning("Aucune donnée disponible. Démarrez l'API Flask.")
    st.stop()

# ==============================================================================
# 2. FILTRES DYNAMIQUES (SIDEBAR)
# ==============================================================================
st.sidebar.title("🎛️ Filtres d'Analyse")
df_filtered = df_brut.copy()

if "type_hebergement" in df_filtered.columns:
    types_dispos = sorted(df_filtered["type_hebergement"].dropna().unique())
    selected_types = st.sidebar.multiselect(
        "🏩 Type d'hébergement", types_dispos, default=types_dispos
    )
    if selected_types:
        df_filtered = df_filtered[df_filtered["type_hebergement"].isin(selected_types)]

if "ville" in df_filtered.columns:
    villes_dispos = sorted(df_filtered["ville"].dropna().unique())
    selected_villes = st.sidebar.multiselect(
        "🏙️ Communes", villes_dispos, placeholder="Toutes les communes…"
    )
    if selected_villes:
        df_filtered = df_filtered[df_filtered["ville"].isin(selected_villes)]

if "etoiles" in df_filtered.columns and df_filtered["etoiles"].notna().any():
    min_star, max_star = int(df_filtered["etoiles"].min()), int(
        df_filtered["etoiles"].max()
    )
    if min_star < max_star:
        selected_stars = st.sidebar.slider(
            "⭐ Classement", min_star, max_star, (min_star, max_star)
        )
        df_filtered = df_filtered[
            df_filtered["etoiles"].between(selected_stars[0], selected_stars[1])
        ]

st.sidebar.markdown(f"**{len(df_filtered):,}** résultats".replace(",", " "))

if df_filtered.empty:
    st.error(
        "⚠️ Aucun hébergement ne correspond à ces critères. Veuillez modifier vos filtres."
    )
    st.stop()

# ==============================================================================
# 3. ONGLETS ET GRAPHIQUES
# ==============================================================================
tab1, tab2, tab3 = st.tabs(["🌍 Vue Globale", "🗺️ Cartographie", "📊 Analyse Croisée"])

# ----------------- ONGLET 1 : VUE GLOBALE -----------------
with tab1:
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Établissements</div><div class="kpi-value">{len(df_filtered):,}</div></div>'.replace(
            ",", " "
        ),
        unsafe_allow_html=True,
    )
    k2.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Lits disponibles</div><div class="kpi-value">{df_filtered.get("capacite_accueil", pd.Series()).sum():,.0f}</div></div>'.replace(
            ",", " "
        ),
        unsafe_allow_html=True,
    )
    k3.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Moyenne Étoiles</div><div class="kpi-value">{df_filtered.get("etoiles", pd.Series()).mean():.1f} ⭐</div></div>',
        unsafe_allow_html=True,
    )
    k4.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Communes Couvertes</div><div class="kpi-value">{df_filtered.get("ville", pd.Series()).nunique():,}</div></div>'.replace(
            ",", " "
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        if "type_hebergement" in df_filtered.columns:
            fig_pie = px.pie(
                df_filtered, names="type_hebergement", hole=0.4, title="Répartition par Type"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        if "ville" in df_filtered.columns:
            top_villes = df_filtered["ville"].value_counts().head(10).reset_index()
            fig_bar = px.bar(
                top_villes,
                y="ville",
                x="count",
                orientation="h",
                title="Top 10 Communes (En volume)",
            )
            fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_bar, use_container_width=True)

    # Bouton d'export
    st.markdown("---")
    csv = df_filtered.to_csv(index=False, sep=";").encode("utf-8-sig")
    st.download_button(
        label="📥 Exporter la sélection en CSV",
        data=csv,
        file_name="tourisme_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ----------------- ONGLET 2 : CARTOGRAPHIE -----------------
with tab2:
    if "dept_code" in df_filtered.columns:
        dept_df = df_filtered.groupby("dept_code").size().reset_index(name="count")
        geojson = load_geojson()

        if geojson:
            fig_map = px.choropleth(
                dept_df,
                geojson=geojson,
                locations="dept_code",
                featureidkey="properties.code",
                color="count",
                color_continuous_scale="Oryel",
                labels={"count": "Nb d'établissements"},
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            fig_map.update_layout(
                title="Densité des hébergements par département",
                height=600,
                margin=dict(t=40, b=0, l=0, r=0),
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Fond de carte indisponible (Vérifiez la connexion).")

# ----------------- ONGLET 3 : ANALYSE CROISÉE (SIMPLIFIÉE) -----------------
with tab3:
    st.markdown("### 🔍 Insights Métiers")
    st.markdown(
        "Cette section permet de comprendre la relation entre le type d'établissement, son classement et sa capacité d'accueil."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Graphique 1 : Capacité moyenne par Type
        if (
            "type_hebergement" in df_filtered.columns
            and "capacite_accueil" in df_filtered.columns
        ):
            cap_moy = (
                df_filtered.groupby("type_hebergement")["capacite_accueil"].mean().reset_index()
            )
            fig_cap = px.bar(
                cap_moy,
                x="type_hebergement",
                y="capacite_accueil",
                title="Capacité Moyenne par Type",
                text_auto=".0f",
                color="type_hebergement",
            )
            fig_cap.update_layout(
                showlegend=False, xaxis_title="", yaxis_title="Capacité Moyenne (Lits)"
            )
            st.plotly_chart(fig_cap, use_container_width=True)

    with col_b:
        # Graphique 2 : Relation Étoiles vs Capacité
        if (
            "etoiles" in df_filtered.columns
            and "capacite_accueil" in df_filtered.columns
        ):
            # On retire les valeurs nulles pour éviter les bugs
            df_scatter = df_filtered.dropna(subset=["etoiles", "capacite_accueil"])
            fig_scatter = px.box(
                df_scatter,
                x="etoiles",
                y="capacite_accueil",
                title="Distribution de la Capacité par Étoiles",
                points="all",
            )
            fig_scatter.update_layout(
                xaxis_title="Nombre d'Étoiles", yaxis_title="Capacité (Lits)"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
