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
    
    # Vérifier si les colonnes nécessaires sont présentes
    required_columns = [
        'session_id', 'visitor_id', 'is_repeat_visitor', 'is_new_visitor',
        'numeric_value', 'days_since_prior_session', 'days_since_first_session',
        'action_name', 'action_group'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if not missing_columns:
        # Définir les poids des actions
        action_weights = {
            'frontend submit': 5,
            'frontend modify': 3,
            'editor publish': 7,
            'frontend create': 8,
            'view': 2
        }

        # Ajouter une colonne de score en fonction des actions
        df['action_score'] = df['action_name'].map(action_weights).fillna(1)
        df['group_score'] = df['action_group'].apply(lambda x: 4 if x == 'publish' else 2)

        # Agréger les scores par visiteur
        df_grouped = df.groupby('visitor_id').agg(
            num_sessions=('session_id', 'nunique'),
            repeat_visitor=('is_repeat_visitor', 'max'),
            new_visitor=('is_new_visitor', 'max'),
            total_numeric_value=('numeric_value', 'sum'),
            avg_days_since_prior_session=('days_since_prior_session', 'mean'),
            avg_days_since_first_session=('days_since_first_session', 'mean'),
            total_action_score=('action_score', 'sum'),
            total_group_score=('group_score', 'sum'),
            unique_actions=('action_name', 'nunique'),
            unique_groups=('action_group', 'nunique')
        ).reset_index()

        # S'assurer que certaines valeurs restent positives
        df_grouped['avg_days_since_first_session'] = df_grouped['avg_days_since_first_session'].apply(lambda x: max(x, 1))

        # Calcul du score d'engagement
        df_grouped['engagement_score'] = (
            df_grouped['num_sessions'] * 5 +
            df_grouped['repeat_visitor'] * 6 - df_grouped['new_visitor'] * 2 +
            df_grouped['total_numeric_value'] * 3 +
            (30 / (df_grouped['avg_days_since_prior_session'] + 1)) +
            (50 / (df_grouped['avg_days_since_first_session'] + 1)) +
            df_grouped['total_action_score'] * 2 +
            df_grouped['total_group_score'] * 3 +
            df_grouped['unique_actions'] * 4 +
            df_grouped['unique_groups'] * 5
        )

        # Normalisation entre 0 et 100
        df_grouped['engagement_score'] = (df_grouped['engagement_score'] - df_grouped['engagement_score'].min()) / (
            df_grouped['engagement_score'].max() - df_grouped['engagement_score'].min()) * 100

        # Fusionner avec le dataset principal
        df = df.merge(df_grouped[['visitor_id', 'engagement_score']], on='visitor_id', how='left')

    return df

df = load_data()

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
tabs = st.tabs(["🏠 Accueil", "📊 Score d'Engagement"])

# === 🏠 ACCUEIL (KPI GLOBAUX) ===
with tabs[0]:
    st.markdown("## 🏠 Vue Globale des Performances SEO")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Sessions Totales", f"{filtered_df['session_id'].nunique():,}")
    col2.metric("🧑‍💻 Visiteurs Uniques", f"{filtered_df['visitor_id'].nunique():,}")
    col3.metric("🔁 Taux de Retour", f"{filtered_df['is_repeat_visitor'].mean()*100:.2f} %")

    if 'engagement_score' in filtered_df.columns:
        col4, col5 = st.columns(2)
        col4.metric("🔥 Score d’Engagement Moyen", f"{filtered_df['engagement_score'].mean():.2f}")
    else:
        st.warning("Le score d'engagement n'a pas pu être calculé.")

# === 📊 SCORE D’ENGAGEMENT (ISOLÉ) ===
with tabs[1]:
    st.markdown("## 📊 Score d’Engagement des Visiteurs")

    if 'engagement_score' in filtered_df.columns:
        fig_engagement = px.scatter(filtered_df, x='visitor_id', y='engagement_score',
                                    color='engagement_score', size='engagement_score',
                                    title="Engagement Score des Visiteurs",
                                    color_continuous_scale=[[0, "blue"], [1, "red"]])
        st.plotly_chart(fig_engagement, use_container_width=True)
    else:
        st.warning("Impossible d'afficher le score d'engagement.")

