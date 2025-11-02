import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================
# 1️⃣ LOAD DATA
# =========================================
merged_df = pd.read_csv("merged_bike_data_cleaned.csv")
merged_df['dteday'] = pd.to_datetime(merged_df['dteday'])

# =========================================
# 2️⃣ MAP KONDISI CUACA
# =========================================
weather_labels = {
    1: "Clear / Few Clouds",
    2: "Mist / Cloudy",
    3: "Light Snow / Rain",
    4: "Heavy Rain / Snow / Fog"
}
merged_df['weather_desc'] = merged_df['weathersit'].map(weather_labels)

# =========================================
# 3️⃣ SIDEBAR FILTER
# =========================================
st.sidebar.header("Filter Data")
min_date = merged_df['dteday'].min().date()
max_date = merged_df['dteday'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Pilih rentang tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

filtered_data = merged_df[(merged_df['dteday'].dt.date >= start_date) & (merged_df['dteday'].dt.date <= end_date)]

# =========================================
# 4️⃣ DASHBOARD TITLE
# =========================================
st.title("🚴 Bike Sharing Dashboard")
st.markdown("Visualisasi penyewaan sepeda harian dan faktor-faktor yang memengaruhinya")

# =========================================
# 5️⃣ METRIK TOTAL
# =========================================
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Daily Rentals", value=int(filtered_data['cnt_day'].sum()))
with col2:
    st.metric("Total Hourly Rentals", value=int(filtered_data['cnt_hour'].sum()))

# =========================================
# 6️⃣ TREND PENYEWAAN HARIAN
# =========================================
st.subheader("📈 Tren Penyewaan Harian")
daily_df = filtered_data.groupby('dteday')['cnt_day'].sum().reset_index()
daily_df.rename(columns={'cnt_day': 'total_rentals'}, inplace=True)

fig_daily = px.line(
    daily_df,
    x='dteday',
    y='total_rentals',
    title='Total Penyewaan Sepeda per Hari',
    labels={'dteday': 'Tanggal', 'total_rentals': 'Jumlah Penyewaan'}
)
st.plotly_chart(fig_daily, use_container_width=True)

# =========================================
# 7️⃣ PENYEWAAN PER JAM
# =========================================
st.subheader("⏰ Penyewaan per Jam")
hourly_df = filtered_data.groupby('hr')['cnt_hour'].sum().reset_index()
hourly_df.rename(columns={'cnt_hour': 'total_rentals'}, inplace=True)

fig_hourly = px.bar(
    hourly_df,
    x='hr',
    y='total_rentals',
    title='Total Penyewaan Sepeda per Jam',
    labels={'hr': 'Jam', 'total_rentals': 'Jumlah Penyewaan'},
    color='total_rentals',
    color_continuous_scale='Blues'
)
st.plotly_chart(fig_hourly, use_container_width=True)

# =========================================
# 8️⃣ PENYEWAAN BERDASARKAN CUACA
# =========================================
st.subheader("🌤 Penyewaan Berdasarkan Kondisi Cuaca")
weather_df = filtered_data.groupby('weather_desc')['cnt_hour'].mean().reset_index()
weather_df.rename(columns={'cnt_hour': 'avg_rentals'}, inplace=True)

fig_weather = px.bar(
    weather_df,
    x='weather_desc',
    y='avg_rentals',
    title='Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca (Per Jam)',
    labels={'weather_desc': 'Kondisi Cuaca', 'avg_rentals': 'Rata-rata Penyewaan'},
    color='weather_desc',
    color_discrete_map={
        "Clear / Few Clouds": "#87CEFA",      # light blue
        "Mist / Cloudy": "#4682B4",           # steel blue
        "Light Snow / Rain": "#1E90FF",       # dodger blue
        "Heavy Rain / Snow / Fog": "#0D47A1"  # dark blue
    }
)


st.plotly_chart(fig_weather, use_container_width=True)

# =========================================
# 9️⃣ PENYEWAAN BERDASARKAN DEMAND LEVEL
# =========================================
filtered_data['demand_level'] = pd.qcut(filtered_data['cnt_day'], q=3, labels=['Low', 'Medium', 'High'])

# Musim vs demand
st.subheader("📊 Segmentasi Permintaan Berdasarkan Musim")
season_demand = filtered_data.groupby(['season', 'demand_level'])['cnt_day'].count().reset_index()
season_demand.rename(columns={'cnt_day': 'days_count'}, inplace=True)

# Mapping season menjadi kategori
season_labels = {1:"Spring", 2:"Summer", 3:"Fall", 4:"Winter"}
filtered_data['season_cat'] = filtered_data['season'].map(season_labels)

# Buat chart dengan kategori string
fig_season = px.bar(
    filtered_data.groupby(['season_cat','demand_level'])['cnt_day'].count().reset_index().rename(columns={'cnt_day':'days_count'}),
    x='season_cat',
    y='days_count',
    color='demand_level',
    barmode='group',
    title='Segmentasi Permintaan Sepeda Berdasarkan Musim',
    labels={'season_cat':'Musim', 'days_count':'Jumlah Hari', 'demand_level':'Tingkat Permintaan'},
    category_orders={'season_cat':['Spring','Summer','Fall','Winter'], 'demand_level':['Low','Medium','High']}
)

st.plotly_chart(fig_season, use_container_width=True)

# Cuaca vs demand
st.subheader("📊 Segmentasi Permintaan Berdasarkan Kondisi Cuaca")
weather_demand = filtered_data.groupby(['weather_desc', 'demand_level'])['cnt_day'].count().reset_index()
weather_demand.rename(columns={'cnt_day': 'days_count'}, inplace=True)
weather_order = sorted(weather_demand['weather_desc'].unique())

fig_weather2 = px.bar(
    weather_demand,
    x='weather_desc',
    y='days_count',
    color='demand_level',
    barmode='group',
    title='Segmentasi Permintaan Sepeda Berdasarkan Kondisi Cuaca',
    labels={'weather_desc': 'Kondisi Cuaca', 'days_count': 'Jumlah Hari', 'demand_level': 'Tingkat Permintaan'},
    category_orders={'demand_level': ['Low', 'Medium', 'High'], 'weather_desc': weather_order}
)
st.plotly_chart(fig_weather2, use_container_width=True)

st.markdown("---")
st.caption("© 2025 Bike Sharing Analysis Dashboard – Dibuat dengan Streamlit & Plotly")
