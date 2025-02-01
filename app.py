import streamlit as st
import pandas as pd
import numpy as np

# ==============================
# 📌 1. CHARGEMENT & NETTOYAGE DES DONNÉES
# ==============================
@st.cache_data
def load_data():
    df = pd.read_csv("merged_data.csv")

    # Suppression des colonnes en double (_x et _y)
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = [col.replace('_x', '') for col in df.columns]

    # Vérifier si "yyyymmdd_x" et "yyyymmdd_y" existent et les corriger
    if "yyyymmdd_x" in df.columns and "yyyymmdd_y" in df.columns:
        df = df.drop(columns=["yyyymmdd_y"])
        df = df.rename(columns={"yyyymmdd_x": "yyyymmdd"})

    # ✅ Vérification si "yyyymmdd" existe dans le DataFrame
    if "yyyymmdd" in df.columns:
        st.write("✅ La colonne 'yyyymmdd' existe, voici un aperçu des premières valeurs uniques :")
        st.write(df["yyyymmdd"].unique()[:10])  # Afficher un échantillon des valeurs uniques

        try:
            df["yyyymmdd"] = df["yyyymmdd"].astype(str)  # S'assurer que c'est une chaîne
            df["yyyymmdd"] = pd.to_numeric(df["yyyymmdd"], errors="coerce").fillna(0).astype(int)
        except Exception as e:
            st.error(f"⚠️ Erreur lors de la conversion de 'yyyymmdd' : {e}")
    else:
        st.error("❌ La colonne 'yyyymmdd' est absente du fichier. Vérifiez votre fichier CSV.")

    return df

df = load_data()

# ==============================
# 📌 2. AFFICHER LES COLONNES POUR DEBUG
# ==============================
st.write("📌 Colonnes disponibles dans le DataFrame :")
st.write(df.columns.tolist())
