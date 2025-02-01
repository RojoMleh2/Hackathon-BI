import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ===============================
# 📌 1. CONFIGURATION DU DASHBOARD
# ===============================
st.set_page_config(page_title="Tableau de Bord - Analyse de performance Marketing", page_icon="📊", layout="wide")

# 📌 Ajouter un en-tête et une description
st.title("📊 Tableau de Bord - Analyse des Performances Marketing")
st.markdown("Ce tableau de bord interactif vous permet d'explorer les performances des visiteurs du site web à partir des données des fichiers CSV.")

# ===============================
# 📌 2. CHARGEMENT DES DONNÉES
# ===============================
@st.cache_data
def load_data():
<<<<<<< HEAD
    df_merge = pd.read_csv("merged_visitor_data.csv")
    return df_merge
=======
    df_visitors = pd.read_csv("owa_visitor.csv")
    df_actions = pd.read_csv("owa_action_fact2.csv")
    df_clicks = pd.read_csv("owa_click.csv")
    return df_visitors, df_actions, df_clicks
>>>>>>> 536696d4e9f20be5e7ef8fb7859767fcac640b67

df_merge = load_data()

# ===============================
# 📌 3. BARRE LATÉRALE AVEC FILTRES INTERACTIFS
# ===============================
st.sidebar.header("🔍 Filtres Interactifs")

# 📅 Filtrage par date
min_date = df_merge["yyyymmdd"].min()
max_date = df_merge["yyyymmdd"].max()
date_filter = st.sidebar.slider("📅 Sélectionner une période :", min_date, max_date, (min_date, max_date))

# 📍 Filtrage par type de visiteur
visitor_type = st.sidebar.radio("👥 Type de Visiteur :", ["Tous", "Nouveaux", "Récurrents"])
if visitor_type == "Nouveaux":
    df_actions = df_merge[df_merge["is_new_visitor"] == 1]
elif visitor_type == "Récurrents":
    df_actions = df_merge[df_merge["is_repeat_visitor"] == 1]

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
col1.metric("👥 Visiteurs Uniques", df_merge["id"].nunique())
col2.metric("📈 Sessions", df_actions["session_id"].nunique())
col3.metric("💡 Taux de Clics (CTR)", f"{(df_merge.shape[0] / df_actions.shape[0]) * 100:.2f} %")
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

# Carte de chaleur des clics sur la page
fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=df_merge, x="click_x", y="click_y", alpha=0.3)
plt.title("Carte de Chaleur des Clics sur la Page")
st.pyplot(fig)

# ===============================
# 📌 7. ANALYSE DES SOURCES DE TRAFIC
# ===============================

st.subheader("🌍 Sources de Trafic")

# Graphique en barres des sources de trafic
traffic_sources = df_actions["medium"].value_counts().reset_index()
traffic_sources.columns = ["Source", "Sessions"]
fig = px.bar(traffic_sources, x="Source", y="Sessions", title="Sessions par Source de Trafic", color="Source")
st.plotly_chart(fig, use_container_width=True)

# ===============================
# 📌 8. EXPORT DES DONNÉES
# ===============================

st.sidebar.subheader("📂 Exporter les Données")

# Bouton pour télécharger les données filtrées
csv = df_actions.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(label="📥 Télécharger les Données Filtrées", data=csv, file_name="filtered_data.csv", mime="text/csv")

st.sidebar.write("📊 **Créé avec amour par un expert en Data Science !** ❤️")
