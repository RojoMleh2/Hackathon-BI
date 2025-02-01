import streamlit as st
import pandas as pd
import plotly.express as px

# Charger les données
def load_data():
    file_path = "owa_action_fact.csv"
    df = pd.read_csv(file_path)
    return df

df = load_data()

# Configurer le tableau de bord
st.set_page_config(page_title="Dashboard Analytics", layout="wide")

# Sidebar - Filtrage par période
df['timestamp'] = pd.to_datetime(df['id'], errors='coerce')
date_min, date_max = df['timestamp'].min(), df['timestamp'].max()
date_range = st.sidebar.date_input("Filtrer par période", [date_min, date_max])

# Filtrage des données
df_filtered = df[(df['timestamp'] >= pd.to_datetime(date_range[0])) & (df['timestamp'] <= pd.to_datetime(date_range[1]))]

# Vue Générale
st.title("📊 Tableau de Bord - Vue Générale")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_visitors = df_filtered['visitor_id'].nunique()
    st.metric("Nombre total de visiteurs uniques", total_visitors)

with col2:
    total_sessions = df_filtered['session_id'].nunique()
    st.metric("Nombre total de sessions", total_sessions)

with col3:
    conversion_rate = (df_filtered['numeric_value'].sum() / total_sessions) * 100
    st.metric("Taux de conversion", f"{conversion_rate:.2f}%")

with col4:
    bounce_rate = (df_filtered[df_filtered['action_name'] == 'bounce'].shape[0] / total_sessions) * 100
    st.metric("Taux de rebond", f"{bounce_rate:.2f}%")

# Analyse de l'Engagement Utilisateur
st.header("📊 Analyse de l'Engagement Utilisateur")
fig_actions = px.bar(df_filtered['action_name'].value_counts().head(10), title="Actions les plus réalisées")
st.plotly_chart(fig_actions)

fig_visitors = px.pie(df_filtered, names='visitor_id', title="Taux de visiteurs récurrents vs nouveaux")
st.plotly_chart(fig_visitors)

# Analyse des Clics et Interactions
st.header("📊 Analyse des Clics")
fig_clicks = px.scatter(df_filtered, x='numeric_value', y='action_name', title="Carte de chaleur des clics")
st.plotly_chart(fig_clicks)

# Analyse du Trafic et Sources d'Acquisition
st.header("📊 Analyse du Trafic")
fig_sources = px.pie(df_filtered, names='referer_id', title="Origine du trafic")
st.plotly_chart(fig_sources)

# Performance des Heures & Jours d'Activité
st.header("📊 Performance par Heure et Jour")
df_filtered['hour'] = df_filtered['timestamp'].dt.hour
fig_hours = px.histogram(df_filtered, x='hour', title="Activité par heure")
st.plotly_chart(fig_hours)

# Parcours Utilisateur
st.header("📊 Parcours Utilisateur")
st.write("Diagramme en cours de développement")

st.sidebar.markdown("Développé avec Streamlit 🚀")
