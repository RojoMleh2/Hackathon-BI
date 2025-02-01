import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# === CONFIGURATION DE LA PAGE ===
st.set_page_config(page_title="📊 Tableau de Bord Web Analytics", layout="wide")

# === CHARGEMENT DES DONNÉES ===
@st.cache_data
def load_data():
    file_path = "owa_action_fact2.csv"  # Assure-toi que ton fichier est dans le même dossier
    df = pd.read_csv(file_path, parse_dates=["timestamp"])
    return df

df = load_data()

# === SIDEBAR (FILTRES DYNAMIQUES) ===
st.sidebar.header("🔍 Filtres")

# 🗓 Sélection d’une période avec un calendrier
min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()
start_date, end_date = st.sidebar.date_input("📆 Sélectionner une période :", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filtrer les données en fonction des dates sélectionnées
filtered_df = df[(df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)]

# 🔗 Sélection des canaux d’acquisition
medium_selected = st.sidebar.multiselect("🛒 Canal d'acquisition", df["medium"].unique(), default=df["medium"].unique())

# 🔗 Sélection des sources (affichage des noms des sources)
source_selected = st.sidebar.multiselect("🔗 Source", df["source_name"].unique(), default=df["source_name"].unique())

# 👥 Type de visiteur
visitor_type = st.sidebar.radio("👥 Type de visiteur", ["Tous", "Nouveau", "Récurrent"])

# Appliquer les autres filtres
filtered_df = filtered_df[
    (filtered_df["medium"].isin(medium_selected)) &
    (filtered_df["source_name"].isin(source_selected))
]

if visitor_type == "Nouveau":
    filtered_df = filtered_df[filtered_df["is_new_visitor"] == 1]
elif visitor_type == "Récurrent":
    filtered_df = filtered_df[filtered_df["is_repeat_visitor"] == 1]

# === SECTION 1 : SYNTHÈSE GLOBALE ===
st.markdown("## 📊 Synthèse Globale")

col1, col2, col3 = st.columns(3)
col1.metric("👥 Sessions Totales", f"{filtered_df['session_id'].nunique():,}")
col2.metric("🧑‍💻 Visiteurs Uniques", f"{filtered_df['visitor_id'].nunique():,}")
col3.metric("🔁 Taux de Retour", f"{filtered_df['is_repeat_visitor'].mean()*100:.2f} %")

# 📌 Répartition Nouveaux vs. Récurrents
visitor_dist = filtered_df["is_new_visitor"].value_counts(normalize=True) * 100
fig_pie = px.pie(
    names=["Nouveaux Visiteurs", "Visiteurs Récurrents"], 
    values=[visitor_dist.get(1, 0), visitor_dist.get(0, 0)],
    title="📌 Répartition Nouveaux vs. Récurrents"
)
st.plotly_chart(fig_pie, use_container_width=True)

# 📊 Canaux d'acquisition
fig_medium = px.bar(filtered_df["medium"].value_counts(), title="📊 Canaux d'Acquisition")
st.plotly_chart(fig_medium, use_container_width=True)

# 📈 Évolution du trafic
fig_traffic = px.line(filtered_df.groupby("timestamp")["session_id"].nunique(), title="📈 Évolution du Trafic")
st.plotly_chart(fig_traffic, use_container_width=True)

# === SECTION 2 : ENGAGEMENT UTILISATEUR ===
st.markdown("## 🎭 Engagement Utilisateur")

col4, col5 = st.columns(2)
col4.metric("⚡ Nombre total d'actions", f"{filtered_df['action_name'].count():,}")
col5.metric("📌 Actions moyennes par session", f"{filtered_df['action_name'].count()/filtered_df['session_id'].nunique():.2f}")

# 📊 Top actions les plus réalisées
fig_actions = px.bar(filtered_df["action_name"].value_counts().head(5), title="🔝 Top 5 Actions les Plus Réalisées")
st.plotly_chart(fig_actions, use_container_width=True)

# 📅 Meilleures heures d'engagement
filtered_df["hour"] = filtered_df["timestamp"].dt.hour
fig_heatmap = px.density_heatmap(filtered_df, x="hour", y="dayofweek", title="⏰ Meilleures Heures d'Engagement")
st.plotly_chart(fig_heatmap, use_container_width=True)

# === SECTION 3 : CONVERSION ===
st.markdown("## 🎯 Conversion")

fig_conversion = px.bar(
    filtered_df.groupby("action_name")["session_id"].count().sort_values(ascending=False).head(5),
    title="🎯 Actions Clés les Plus Convertissantes"
)
st.plotly_chart(fig_conversion, use_container_width=True)

# === SECTION 4 : FIDÉLISATION ===
st.markdown("## 🔄 Fidélisation & Rétention")

col6, col7 = st.columns(2)
col6.metric("🔁 Taux de Retour", f"{filtered_df['is_repeat_visitor'].mean()*100:.2f} %")
col7.metric("📆 Durée moyenne entre les visites", f"{filtered_df['days_since_prior_session'].mean():.1f} jours")

# 📊 Répartition des visiteurs par fréquence
fig_freq = px.histogram(filtered_df["num_prior_sessions"], title="📊 Fréquence des Visites")
st.plotly_chart(fig_freq, use_container_width=True)

# === SECTION 5 : ANALYSE TEMPORELLE ===
st.markdown("## 🕒 Analyse Temporelle")

fig_sessions_time = px.line(
    filtered_df.groupby("timestamp")["session_id"].count(),
    title="📅 Sessions par Jour"
)
st.plotly_chart(fig_sessions_time, use_container_width=True)

# 📊 Meilleurs jours pour l’engagement
fig_dayofweek = px.bar(filtered_df.groupby("dayofweek")["session_id"].count(), title="📊 Meilleurs Jours pour l'Engagement")
st.plotly_chart(fig_dayofweek, use_container_width=True)

st.markdown("---")
st.markdown("🚀 **Tableau de bord développé par IA** - Optimisé pour l’analyse de performances marketing web")
