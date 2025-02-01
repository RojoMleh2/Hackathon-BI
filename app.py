import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ==============================
# 📌 1. CONFIGURATION DU DASHBOARD
# ==============================
st.set_page_config(page_title="Dashboard Performance Marketing", page_icon="📊", layout="wide")

st.title("📊 Tableau de Bord - Performance Marketing")
st.markdown("Visualisation interactive des données de visiteurs, sessions et actions sur le site web.")

# ==============================
# 📌 2. CHARGEMENT & NETTOYAGE DES DONNÉES
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("merged_visitor_data.csv")
    
    # Suppression des colonnes en double (_x et _y)
    df = df.loc[:, ~df.columns.duplicated()]  # Supprime les doublons de colonnes
    df.columns = [col.replace('_x', '') for col in df.columns]  # Nettoyage des noms

    # Vérifier et supprimer les colonnes en double spécifiques
    if "yyyymmdd_x" in df.columns and "yyyymmdd_y" in df.columns:
        df = df.drop(columns=["yyyymmdd_y"])
        df = df.rename(columns={"yyyymmdd_x": "yyyymmdd"})

    if "first_session_timestamp_x" in df.columns and "first_session_timestamp_y" in df.columns:
        df = df.drop(columns=["first_session_timestamp_y"])
        df = df.rename(columns={"first_session_timestamp_x": "first_session_timestamp"})

    # ✅ Correction du format de `yyyymmdd`
    df["yyyymmdd"] = pd.to_numeric(df["yyyymmdd"], errors="coerce").fillna(0).astype(int)

    # Remplacement des valeurs manquantes
    df.fillna({"user_email": "Inconnu", "medium": "Non défini", "source_id": 0}, inplace=True)

    return df

df = load_data()

# ==============================
# 📌 3. FILTRES INTERACTIFS (Sidebar)
# ==============================
st.sidebar.header("🔍 Filtres Interactifs")

# ✅ Correction du slider avec `yyyymmdd` en entier
min_date = int(df["yyyymmdd"].min())
max_date = int(df["yyyymmdd"].max())

date_filter = st.sidebar.slider(
    "📅 Sélectionner une période :", 
    min_value=min_date, 
    max_value=max_date, 
    value=(min_date, max_date)
)

# 📍 Filtrage par type de visiteur
visitor_type = st.sidebar.radio("👥 Type de Visiteur :", ["Tous", "Nouveaux", "Récurrents"])
if visitor_type == "Nouveaux":
    df = df[df["is_new_visitor"] == 1]
elif visitor_type == "Récurrents":
    df = df[df["is_repeat_visitor"] == 1]

# 🌍 Filtrage par source d’acquisition
source_list = df["medium"].unique().tolist()
source_filter = st.sidebar.multiselect("🌍 Source d’Acquisition :", source_list, default=source_list)

# Appliquer les filtres
df = df[(df["yyyymmdd"] >= date_filter[0]) & (df["yyyymmdd"] <= date_filter[1])]
df = df[df["medium"].isin(source_filter)]

# ==============================
# 📌 4. INDICATEURS CLÉS (KPI)
# ==============================
st.subheader("📊 Indicateurs Clés de Performance")

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Visiteurs Uniques", df["visitor_id"].nunique())
col2.metric("📈 Sessions", df["session_id"].nunique())
col3.metric("💡 Taux de Clics (CTR)", f"{(df['click'].count() / df['session_id'].nunique()) * 100:.2f} %")
col4.metric("🕒 Temps Moyen par Session", f"{df['last_req'].mean():.2f} sec")

# ==============================
# 📌 5. ANALYSE DES VISITEURS (Graphiques)
# ==============================
st.subheader("👥 Répartition des Visiteurs")

# Graphique en camembert : Nouveaux vs Récurrents
visitor_counts = df["is_new_visitor"].value_counts()
fig = px.pie(values=visitor_counts, names=["Nouveaux", "Récurrents"], title="Répartition des visiteurs")
st.plotly_chart(fig, use_container_width=True)

# Graphique en barres : Nombre de sessions par jour
df_time_series = df.groupby(["year", "month"]).size().reset_index(name="Sessions")
fig = px.bar(df_time_series, x="month", y="Sessions", color="year", title="Nombre de Sessions par Mois")
st.plotly_chart(fig, use_container_width=True)

# ==============================
# 📌 6. ANALYSE DES CLICS (Carte de chaleur)
# ==============================
st.subheader("🖱️ Analyse des Clics")

# Carte de chaleur des clics sur la page
fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=df, x="click_x", y="click_y", alpha=0.3)
plt.title("Carte de Chaleur des Clics sur la Page")
st.pyplot(fig)

# ==============================
# 📌 7. ANALYSE DES SOURCES DE TRAFIC
# ==============================
st.subheader("🌍 Sources de Trafic")

# Graphique en barres des sources de trafic
traffic_sources = df["medium"].value_counts().reset_index()
traffic_sources.columns = ["Source", "Sessions"]
fig = px.bar(traffic_sources, x="Source", y="Sessions", title="Sessions par Source de Trafic", color="Source")
st.plotly_chart(fig, use_container_width=True)

# ==============================
# 📌 8. EXPORT DES DONNÉES
# ==============================
st.sidebar.subheader("📂 Exporter les Données")

# Bouton pour télécharger les données filtrées
csv = df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(label="📥 Télécharger les Données Filtrées", data=csv, file_name="filtered_data.csv", mime="text/csv")

st.sidebar.write("📊 **Créé avec amour par un expert en Data Science !** ❤️")
