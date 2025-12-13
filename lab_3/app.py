import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static

sns.set_theme(style="whitegrid")

# ------------------------------------------------------------
# ÎNCĂRCAREA DATELOR
# ------------------------------------------------------------

@st.cache_data
def load_data(csv_path: str = "cams_data.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df.dropna(inplace=True)
    return df

df = load_data()

# ------------------------------------------------------------
# INTERFAȚA STREAMLIT
# ------------------------------------------------------------

st.title("Explorator Calitate Aer - CAMS")

st.sidebar.header("Filtre")

# Filtru dată
date_min = df['date'].min().date()
date_max = df['date'].max().date()
date_range = st.sidebar.date_input("Selectează interval dată", [date_min, date_max])
df_filtered = df[(df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])]

# Filtru PM2.5
pm25_range = st.sidebar.slider("Interval PM2.5", float(df['pm25'].min()), float(df['pm25'].max()), (float(df['pm25'].min()), float(df['pm25'].max())))
df_filtered = df_filtered[(df_filtered['pm25'] >= pm25_range[0]) & (df_filtered['pm25'] <= pm25_range[1])]

st.write(f"Date filtrate: {len(df_filtered)} înregistrări")

# ------------------------------------------------------------
# VIZUALIZĂRI
# ------------------------------------------------------------

st.header("Analiza descriptivă")
# Create display version with date as string
df_display = df_filtered.copy()
df_display['date'] = df_display['date'].astype(str)
st.write(df_display.describe())

st.subheader("Distribuția PM2.5")
fig, ax = plt.subplots()
sns.histplot(df_filtered['pm25'], kde=True, ax=ax)
st.pyplot(fig)

st.subheader("Tendința în timp")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df_filtered['date'], df_filtered['pm25'])
ax.set_title("PM2.5 în timp")
st.pyplot(fig)

st.subheader("Hartă termică")
m = folium.Map(location=[42.5, 10], zoom_start=5)
heat_data = [[row['latitude'], row['longitude'], row['pm25']] for index, row in df_filtered.iterrows()]
HeatMap(heat_data).add_to(m)
folium_static(m)

st.header("Concluzii")
st.write("Explorează datele pentru a identifica tendințe și zone cu poluare ridicată.")