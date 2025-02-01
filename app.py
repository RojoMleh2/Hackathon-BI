import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# === CONFIGURATION DE LA PAGE ===
st.set_page_config(page_title="📊 Tableau de Bord SEO & Web Analytics", layout="wide")

# === CHARGEMENT DES DONNÉES ===
@st.cache_data
def load_data():
    file_path = "owa_action_fact2.csv"
    df = pd.read_csv(file_path, parse_dates=["timestamp"])
    df.columns = df.columns.str.strip()  # Nettoyer les noms de colonnes
    return df

df = load_data()

# === VERIFICATIONS ===
if "source_name" not in df.columns:
    st.error("🚨 Erreur : La colonne 'source_name' est absente.")
    st.stop()

# === SIDEBAR (FILTRES DYNAMIQUES) ===
st.sidebar.header("🔍 Filtres")

# 🗓 Sélection de la période
min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()
start_date, end_date = st.sidebar.date_input("📆 Période :", [min_date, max_date], min_value=min_date, max_value=max_date)

# 🎯 Filtrage des données par date
filtered_df = df[(df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)]

# 🔗 Canaux d'acquisition
medium_selected = st.sidebar.multiselect("🛒 Canal d'acquisition", df["medium"].unique(), default=df["medium"].unique())

# 🔗 Sources
source_selected = st.sidebar.multiselect("🔗 Source", df["source_name"].dropna().unique(), default=df["source_name"].dropna().unique())

# 👥 Type de visiteur
visitor_type = st.sidebar.radio("👥 Type de visiteur", ["Tous", "Nouveau", "Récurrent"])

# Appliquer les filtres
filtered_df = filtered_df[
    (filtered_df["medium"].isin(medium_selected)) & 
    (filtered_df["source_name"].isin(source_selected))
]

if visitor_type == "Nouveau":
    filtered_df = filtered_df[filtered_df["is_new_visitor"] == 1]
elif visitor_type == "Récurrent":
    filtered_df = filtered_df[filtered_df["is_repeat_visitor"] == 1]

# === CREATION DES ONGLETS ===
tabs = st.tabs(["🏠 Accueil", "📥 Acquisition", "🎭 Engagement", "🎯 Conversion & Rétention", "📊 Score d'Engagement", "🕒 Analyse Temporelle"])

# === 🏠 ACCUEIL (KPI GLOBAUX) ===
with tabs[0]:
    st.markdown("## 🏠 Vue Globale des Performances SEO")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Sessions Totales", f"{filtered_df['session_id'].nunique():,}")
    col2.metric("🧑‍💻 Visiteurs Uniques", f"{filtered_df['visitor_id'].nunique():,}")
    col3.metric("🔁 Taux de Retour", f"{filtered_df['is_repeat_visitor'].mean()*100:.2f} %")
    
    col4, col5 = st.columns(2)
    col4.metric("📆 Durée Moyenne Entre Visites", f"{filtered_df['days_since_prior_session'].mean():.1f} jours")
    col5.metric("🔥 Score d’Engagement Moyen", f"{filtered_df['engagement_score'].mean():.2f}")

# === 📥 ACQUISITION ===
with tabs[1]:
    st.markdown("## 📥 Analyse du Trafic & Acquisition")

    # 📊 Canaux d'acquisition
    fig_medium = px.bar(filtered_df["medium"].value_counts().reset_index(), x="index", y="medium", title="📊 Canaux d'Acquisition")
    st.plotly_chart(fig_medium, use_container_width=True)

    # 📈 Évolution du trafic
    fig_traffic = px.line(filtered_df.groupby("timestamp")["session_id"].nunique().reset_index(), x="timestamp", y="session_id", title="📈 Évolution du Trafic")
    st.plotly_chart(fig_traffic, use_container_width=True)

# === 🎭 ENGAGEMENT UTILISATEUR ===
with tabs[2]:
    st.markdown("## 🎭 Engagement Utilisateur")

    col1, col2 = st.columns(2)
    col1.metric("⚡ Nombre total d'actions", f"{filtered_df['action_name'].count():,}")
    col2.metric("📌 Actions moyennes par session", f"{filtered_df['action_name'].count()/filtered_df['session_id'].nunique():.2f}")

    # 📊 Top actions réalisées
    fig_actions = px.bar(filtered_df["action_name"].value_counts().reset_index().head(5), x="index", y="action_name", title="🔝 Top 5 Actions les Plus Réalisées")
    st.plotly_chart(fig_actions, use_container_width=True)

# === 🎯 CONVERSION & RÉTENTION ===
with tabs[3]:
    st.markdown("## 🎯 Conversion & Rétention")

    # 📊 Actions clés
    fig_conversion = px.bar(filtered_df.groupby("action_name")["session_id"].count().reset_index().sort_values(by="session_id", ascending=False).head(5), x="action_name", y="session_id", title="🎯 Actions Clés les Plus Convertissantes")
    st.plotly_chart(fig_conversion, use_container_width=True)

# === 📊 SCORE D’ENGAGEMENT (ISOLÉ) ===
with tabs[4]:
    st.markdown("## 📊 Score d’Engagement des Visiteurs")

    # 📊 Scatter Plot Engagement Score
    fig_engagement = px.scatter(filtered_df, x='visitor_id', y='engagement_score',
                                color='engagement_score', size='engagement_score',
                                title="Engagement Score des Visiteurs",
                                color_continuous_scale=[[0, "blue"], [1, "red"]])
    st.plotly_chart(fig_engagement, use_container_width=True)

# === 🕒 ANALYSE TEMPORELLE ===
with tabs[5]:
    st.markdown("## 🕒 Analyse Temporelle")

    # 📈 Sessions par jour
    fig_sessions_time = px.line(filtered_df.groupby("timestamp")["session_id"].count().reset_index(), x="timestamp", y="session_id", title="📅 Sessions par Jour")
    st.plotly_chart(fig_sessions_time, use_container_width=True)

