import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# === CONFIGURATION DE LA PAGE ===
st.set_page_config(page_title="📊 Tableau de Bord Web Analytics", layout="wide")

# === CHARGEMENT DES DONNÉES ===
@st.cache_data
def load_data():
    file_path = "owa_action_fact2.csv"  
    df = pd.read_csv(file_path, parse_dates=["timestamp"])
    
    # Nettoyer les noms de colonnes (évite les erreurs de KeyError)
    df.columns = df.columns.str.strip()
    
    return df

df = load_data()

# Vérification de l'existence de "source_name"
if "source_name" not in df.columns:
    st.error("🚨 Erreur : La colonne 'source_name' n'existe pas dans le fichier.")
    st.stop()

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
source_selected = st.sidebar.multiselect("🔗 Source", df["source_name"].dropna().unique(), default=df["source_name"].dropna().unique())

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

# SCORE ENGAGEMENT
# Charger les données (Simulé ici, remplacer par le fichier réel)
file_path = "owa_action_fact.csv"
df = pd.read_csv(file_path)

# Calculer le score d'implication en regroupant par visitor_id
df['session_duration'] = df['last_req'] - df['timestamp']

action_weights = {
    'frontend submit': 5,
    'frontend modify': 3,
    'editor publish': 7,
    'frontend create': 8,
    'view': 2  # Exemple de poids augmentés
}
df['action_score'] = df['action_name'].map(action_weights).fillna(1)
df['group_score'] = df['action_group'].apply(lambda x: 4 if x == 'publish' else 2)

# Agrégation des données par visiteur
df_grouped = df.groupby('visitor_id').agg(
    num_sessions=('session_id', 'nunique'),
    repeat_visitor=('is_repeat_visitor', 'max'),
    new_visitor=('is_new_visitor', 'max'),
    total_numeric_value=('numeric_value', 'sum'),
    avg_days_since_prior_session=('days_since_prior_session', 'mean'),
    avg_days_since_first_session=('days_since_first_session', 'mean'),
    total_session_duration=('session_duration', 'sum'),
    total_action_score=('action_score', 'sum'),
    total_group_score=('group_score', 'sum'),
    unique_actions=('action_name', 'nunique'),
    unique_groups=('action_group', 'nunique')
).reset_index()

# S'assurer que certaines valeurs restent positives
df_grouped['avg_days_since_first_session'] = df_grouped['avg_days_since_first_session'].apply(lambda x: max(x, 1))
df_grouped['total_session_duration'] = df_grouped['total_session_duration'].apply(lambda x: max(x, 1))

# Normalisation du score d'implication
df_grouped['engagement_score'] = (
    df_grouped['num_sessions'] * 5 +
    df_grouped['repeat_visitor'] * 6 - df_grouped['new_visitor'] * 2 +
    df_grouped['total_numeric_value'] * 3 +
    (30 / (df_grouped['avg_days_since_prior_session'] + 1)) +
    (50 / (df_grouped['avg_days_since_first_session'] + 1)) +
    (df_grouped['total_session_duration'] / 30) +
    df_grouped['total_action_score'] * 2 +
    df_grouped['total_group_score'] * 3 +
    df_grouped['unique_actions'] * 4 +
    df_grouped['unique_groups'] * 5
)

# Mise à l'échelle entre 0 et 100
df_grouped['engagement_score'] = (df_grouped['engagement_score'] - df_grouped['engagement_score'].min()) / (
    df_grouped['engagement_score'].max() - df_grouped['engagement_score'].min()) * 100

# Supprimer les utilisateurs avec un score d'implication de 0
df_grouped = df_grouped[df_grouped['engagement_score'] > 0]

# Filtrer pour ne conserver que les scores inférieurs ou égaux à 20
df_grouped = df_grouped[df_grouped['engagement_score'] <= 20]

# Trouver l'utilisateur avec le score le plus élevé
best_visitor = df_grouped.loc[df_grouped['engagement_score'].idxmax(), 'visitor_id']
best_score = df_grouped['engagement_score'].max()

# Streamlit App
st.title("Tableau de Bord d'Implication des Visiteurs")

# Afficher les KPIs
st.subheader("KPIs Clés")
st.metric("Nombre total de visiteurs", df_grouped['visitor_id'].nunique())
st.metric("Nombre total de sessions", df_grouped['num_sessions'].sum())
st.metric("Score moyen d'engagement", round(df_grouped['engagement_score'].mean(), 2))
st.metric("Nombre moyen d'actions uniques", round(df_grouped['unique_actions'].mean(), 2))
st.metric("Nombre moyen de groupes uniques", round(df_grouped['unique_groups'].mean(), 2))
st.metric("Meilleur visiteur", f"{best_visitor} avec un score de {round(best_score, 2)}")

# Scatter Plot avec Plotly
st.subheader("Scatter Plot : Score d'Implication des Visiteurs")
fig = px.scatter(df_grouped, x='visitor_id', y='engagement_score',
                 color='engagement_score',
                 size='engagement_score',
                 hover_data=['num_sessions', 'total_action_score', 'total_group_score'],
                 title="Engagement Score des Visiteurs",
                 color_continuous_scale=[[0, "blue"], [1, "red"]])
fig.update_layout(yaxis=dict(range=[0, 20]))
st.plotly_chart(fig)

# Afficher le tableau des données utilisées
st.subheader("Données Agrégées par Visiteur")
st.dataframe(df_grouped)


st.markdown("---")
st.markdown("🚀 **Tableau de bord développé par IA** - Optimisé pour l’analyse de performances marketing web")
