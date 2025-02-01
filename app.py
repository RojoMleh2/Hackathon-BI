import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# === CONFIGURATION DE LA PAGE ===
st.set_page_config(page_title="📊 Tableau de Bord Web Analytics", layout="wide")

# === CHARGEMENT DES DONNÉES ===
@st.cache_data
def load_data():
    file_path = "owa_action_fact2.csv"  # Chemin vers ton fichier CSV
    df = pd.read_csv(file_path, parse_dates=["timestamp"])
    return df

df = load_data()

# === SIDEBAR (FILTRES DYNAMIQUES) ===
st.sidebar.header("🔍 Filtres")
year_selected = st.sidebar.multiselect("📅 Année", df["year"].unique(), default=df["year"].unique())
month_selected = st.sidebar.multiselect("📆 Mois", df["month"].unique(), default=df["month"].unique())
week_selected = st.sidebar.multiselect("📊 Semaine de l'année", df["weekofyear"].unique(), default=df["weekofyear"].unique())
medium_selected = st.sidebar.multiselect("🛒 Canal d'acquisition", df["medium"].unique(), default=df["medium"].unique())
source_selected = st.sidebar.multiselect("🔗 Source", df["source_id"].unique(), default=df["source_id"].unique())
campaign_selected = st.sidebar.multiselect("📢 Campagne", df["campaign_id"].unique(), default=df["campaign_id"].unique())
visitor_type = st.sidebar.radio("👥 Type de visiteur", ["Tous", "Nouveau", "Récurrent"])

# Filtrage des données en fonction des choix utilisateurs
filtered_df = df[
    (df["year"].isin(year_selected)) & 
    (df["month"].isin(month_selected)) & 
    (df["weekofyear"].isin(week_selected)) &
    (df["medium"].isin(medium_selected)) &
    (df["source_id"].isin(source_selected)) &
    (df["campaign_id"].isin(campaign_selected))
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
fig_traffic = px.line(filtered_df.groupby("yyyymmdd")["session_id"].nunique(), title="📈 Évolution du Trafic")
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

# 📢 Performances des campagnes
fig_campaign = px.bar(
    filtered_df.groupby("campaign_id")["session_id"].count().sort_values(ascending=False).head(10),
    title="📢 Performance des Campagnes Marketing"
)
st.plotly_chart(fig_campaign, use_container_width=True)

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
    filtered_df.groupby("yyyymmdd")["session_id"].count(),
    title="📅 Sessions par Jour"
)
st.plotly_chart(fig_sessions_time, use_container_width=True)

# 📊 Meilleurs jours pour l’engagement
fig_dayofweek = px.bar(filtered_df.groupby("dayofweek")["session_id"].count(), title="📊 Meilleurs Jours pour l'Engagement")
st.plotly_chart(fig_dayofweek, use_container_width=True)

st.markdown("---")
st.markdown("🚀 **Tableau de bord développé par IA** - Optimisé pour l’analyse de performances marketing web")

