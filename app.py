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

# === SCORE D'ENGAGEMENT ===
# 🛠 Correction : Assurer que "last_req" et "timestamp" sont bien en datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

if df["last_req"].dtype != 'datetime64[ns]':
    df["last_req"] = pd.to_numeric(df["last_req"], errors="coerce")  # Convertir en nombre si nécessaire
    df["last_req"] = pd.to_datetime(df["last_req"], unit="s", errors="coerce")  # Convertir en datetime

# Vérifier si les conversions ont bien fonctionné
if df["last_req"].isna().sum() > 0:
    st.warning("⚠ Certaines valeurs de 'last_req' n'ont pas pu être converties en datetime.")

# Vérifier les types de données avant conversion
st.write("Avant conversion :")
st.write(df.dtypes)

# ✅ Correction : Assurer que "timestamp" est bien en datetime
if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# ✅ Correction : Assurer que "last_req" est bien en datetime
if not pd.api.types.is_datetime64_any_dtype(df["last_req"]):
    df["last_req"] = pd.to_numeric(df["last_req"], errors="coerce")  # Convertir en nombre si nécessaire
    df["last_req"] = pd.to_datetime(df["last_req"], unit="s", errors="coerce")  # Convertir en datetime

# 🔍 Vérifier s'il y a encore des NaN après conversion
st.write("Après conversion :")
st.write(df.dtypes)

# Vérifier les valeurs incorrectes avant la soustraction
if df["last_req"].isna().sum() > 0 or df["timestamp"].isna().sum() > 0:
    st.warning("⚠ Certaines valeurs n'ont pas pu être converties en datetime !")
    st.write(df[df["last_req"].isna() | df["timestamp"].isna()])

# ✅ Correction de la soustraction
df["session_duration"] = (df["last_req"] - df["timestamp"]).dt.total_seconds()
df["session_duration"] = df["session_duration"].fillna(0)  # Remplacer NaN par 0

# ✅ Correction appliquée aussi au `filtered_df`
filtered_df["session_duration"] = (filtered_df["last_req"] - filtered_df["timestamp"]).dt.total_seconds()
filtered_df["session_duration"] = filtered_df["session_duration"].fillna(0)

# Calcul de la durée de session en secondes
df["session_duration"] = (df["last_req"] - df["timestamp"]).dt.total_seconds().fillna(0)

# Appliquer la correction au dataframe filtré
filtered_df["session_duration"] = (filtered_df["last_req"] - filtered_df["timestamp"]).dt.total_seconds().fillna(0)

action_weights = {
    'frontend submit': 5,
    'frontend modify': 3,
    'editor publish': 7,
    'frontend create': 8,
    'view': 2  # Exemple de poids augmentés
}
filtered_df['action_score'] = filtered_df['action_name'].map(action_weights).fillna(1)
filtered_df['group_score'] = filtered_df['action_group'].apply(lambda x: 4 if x == 'publish' else 2)

# Agrégation des données par visiteur
df_grouped = filtered_df.groupby('visitor_id').agg(
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

# Streamlit App
st.title("Tableau de Bord d'Implication des Visiteurs")

st.subheader("Scatter Plot : Score d'Implication des Visiteurs")

# ✅ Correction : Convertir visitor_id en chaîne de caractères pour une meilleure lisibilité
df_grouped['visitor_id'] = df_grouped['visitor_id'].astype(str)

# ✅ Correction : Ajustement dynamique de l'axe Y
fig = px.scatter(df_grouped, x='visitor_id', y='engagement_score',
                 color='engagement_score',
                 size='engagement_score',
                 hover_data=['num_sessions', 'total_action_score', 'total_group_score'],
                 title="Engagement Score des Visiteurs",
                 color_continuous_scale="Blues")

fig.update_layout(yaxis=dict(range=[df_grouped['engagement_score'].min(), df_grouped['engagement_score'].max()]))

st.plotly_chart(fig)

st.subheader("Données Agrégées par Visiteur")
st.dataframe(df_grouped)

st.markdown("---")
st.markdown("🚀 **Tableau de bord optimisé pour l’analyse de performances marketing web**")
