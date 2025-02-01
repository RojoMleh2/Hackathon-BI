import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import zipfile
import os

# ===============================
# 📌 1. CONFIGURATION DU DASHBOARD
# ===============================
st.set_page_config(page_title="Tableau de Bord Marketing", page_icon="📊", layout="wide")

# 📌 Ajouter un en-tête et une description
st.title("📊 Tableau de Bord - Analyse des Performances Marketing")
st.markdown("Ce tableau de bord interactif vous permet d'explorer les performances des visiteurs du site web à partir des données des fichiers CSV.")

# ===============================
# 📌 2. CHARGEMENT DES DONNÉES
# ===============================
@st.cache_data
def load_data():
    # Chargement des fichiers CSV standards
    df_visitors = pd.read_csv("owa_visitor.csv")
    df_actions = pd.read_csv("owa_action_fact2.csv")
    
    # Gestion du fichier ZIP
    zip_path = "owa_click.zip"
    extract_path = "extracted_data"
    
    # Extraction du fichier ZIP s'il existe
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)  # Décompresser le fichier dans un dossier
        
        # Recherche du fichier CSV extrait
        extracted_files = os.listdir(extract_path)
        csv_file = [f for f in extracted_files if f.endswith(".csv")]
        
        if csv_file:
            df_clicks = pd.read_csv(os.path.join(extract_path, csv_file[0]))  # Chargement du fichier CSV
        else:
            st.error("Aucun fichier CSV trouvé dans l'archive ZIP.")
            df_clicks = pd.DataFrame()  # Création d'un dataframe vide en cas d'erreur
    else:
        st.error(f"Le fichier {zip_path} est introuvable.")
        df_clicks = pd.DataFrame()  # Création d'un dataframe vide en cas d'erreur
    
    return df_visitors, df_actions, df_clicks

df_visitors, df_actions, df_clicks = load_data()

# ===============================
# 📌 3. BARRE LATÉRALE AVEC FILTRES INTERACTIFS
# ===============================
st.sidebar.header("🔍 Filtres Interactifs")

# 📅 Filtrage par date
min_date = df_actions["yyyymmdd"].min()
max_date = df_actions["yyyymmdd"].max()
date_filter = st.sidebar.slider("📅 Sélectionner une période :", min_date, max_date, (min_date, max_date))

# 📍 Filtrage par type de visiteur
visitor_type = st.sidebar.radio("👥 Type de Visiteur :", ["Tous", "Nouveaux", "Récurrents"])
if visitor_type == "Nouveaux":
    df_actions = df_actions[df_actions["is_new_visitor"] == 1]
elif visitor_type == "Récurrents":
    df_actions = df_actions[df_actions["is_repeat_visitor"] == 1]

# 🌍 Filtrage par source d’acquisition
source_list = df_actions["medium"].unique().tolist()
source_filter = st.sidebar.multiselect("🌍 Source d’Acquisition :", source_list, default=source_list)

# Appliquer les filtres
df_actions = df_actions[(df_actions["yyyymmdd"] >= date_filter[0]) & (df_actions["yyyymmdd"] <= date_filter[1])]
df_actions = df_actions[df_actions["medium"].isin(source_filter)]

# ===============================
# 📌 4. INDICATEURS CLÉS DE PERFORMANCE (KPI)
# ===============================
st.subheader("📊 Indicateurs Clés de Performance")

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Visiteurs Uniques", df_visitors["id"].nunique())
col2.metric("📈 Sessions", df_actions["session_id"].nunique())

if not df_clicks.empty:
    col3.metric("💡 Taux de Clics (CTR)", f"{(df_clicks.shape[0] / df_actions.shape[0]) * 100:.2f} %")
else:
    col3.metric("💡 Taux de Clics (CTR)", "Données non disponibles")

col4.metric("🕒 Temps Moyen par Session", f"{df_actions['last_req'].mean():.2f} sec")

# ===============================
# 📌 5. ANALYSE DES VISITEURS (Graphiques)
# ===============================

st.subheader("👥 Répartition des Visiteurs")

# Graphique en camembert : Nouveaux vs Récurrents
visitor_counts = df_actions["is_new_visitor"].value_counts()
fig = px.pie(values=visitor_counts, names=["Nouveaux", "Récurrents"], title="Répartition des visiteurs")
st.plotly_chart(fig, use_container_width=True)

# Graphique en barres : Nombre de sessions par jour
df_time_series = df_actions.groupby(["year", "month"]).size().reset_index(name="Sessions")
fig = px.bar(df_time_series, x="month", y="Sessions", color="year", title="Nombre de Sessions par Mois")
st.plotly_chart(fig, use_container_width=True)

# ===============================
# 📌 6. ANALYSE DES CLICS (Carte de chaleur)
# ===============================

st.subheader("🖱️ Analyse des Clics")

if not df_clicks.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_clicks, x="click_x", y="click_y", alpha=0.3)
    plt.title("Carte de Chaleur des Clics sur la Page")
    st.pyplot(fig)
else:
    st.warning("⚠️ Données des clics non disponibles. Vérifiez si le fichier ZIP est bien chargé.")

# ===============================
# 📌 7. ANALYSE DES SOURCES DE TRAFIC
# ===============================

st.subheader("🌍 Sources de Trafic")

traffic_sources = df_actions["medium"].value_counts().reset_index()
traffic_sources.columns = ["Source", "Sessions"]
fig = px.bar(traffic_sources, x="Source", y="Sessions", title="Sessions par Source de Trafic", color="Source")
st.plotly_chart(fig, use_container_width=True)

# ===============================
# 📌 8. EXPORT DES DONNÉES
# ===============================

st.sidebar.subheader("📂 Exporter les Données")

csv = df_actions.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(label="📥 Télécharger les Données Filtrées", data=csv, file_name="filtered_data.csv", mime="text/csv")

st.sidebar.write("📊 **Créé avec amour par un expert en Data Science !** ❤️")
