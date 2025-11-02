import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================
#  LOAD DATA
# =========================================
merged_df = pd.read_csv("merged_bike_data_cleaned.csv")
merged_df['dteday'] = pd.to_datetime(merged_df['dteday'])

# =========================================
#  MAP KONDISI CUACA
# =========================================
weather_labels = {
    1: "Clear / Few Clouds",
    2: "Mist / Cloudy",
    3: "Light Snow / Rain",
    4: "Heavy Rain / Snow / Fog"
}
merged_df['weather_desc'] = merged_df['weathersit'].map(weather_labels)

# Mapping season menjadi kategori
season_labels = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
merged_df['season_cat'] = merged_df['season'].map(season_labels)

# =========================================
#  SIDEBAR FILTER
# =========================================
st.sidebar.header("Filter Data")

# Filter tanggal
min_date = merged_df['dteday'].min().date()
max_date = merged_df['dteday'].max().date()

start_date, end_date = st.sidebar.date_input(
    "Pilih rentang tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

filtered_data = merged_df[(merged_df['dteday'].dt.date >= start_date) & (merged_df['dteday'].dt.date <= end_date)]

# Filter cuaca
weather_options = st.sidebar.multiselect(
    "Pilih kondisi cuaca",
    options=merged_df['weather_desc'].unique(),
    default=merged_df['weather_desc'].unique()
)
filtered_data = filtered_data[filtered_data['weather_desc'].isin(weather_options)]

# Filter musim
season_options = st.sidebar.multiselect(
    "Pilih musim",
    options=merged_df['season_cat'].unique(),
    default=merged_df['season_cat'].unique()
)
filtered_data = filtered_data[filtered_data['season_cat'].isin(season_options)]

# Filter level permintaan
filtered_data['demand_level'] = pd.qcut(filtered_data['cnt_day'], q=3, labels=['Low','Medium','High'])
demand_options = st.sidebar.multiselect(
    "Pilih level permintaan",
    options=['Low','Medium','High'],
    default=['Low','Medium','High']
)
filtered_data = filtered_data[filtered_data['demand_level'].isin(demand_options)]

# =========================================
#  DASHBOARD TITLE
# =========================================
st.title("🚴 Bike Sharing Dashboard")
st.markdown("Visualisasi penyewaan sepeda harian dan faktor-faktor yang memengaruhinya")

# =========================================
#  METRIK TOTAL
# =========================================
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Daily Rentals", value=int(filtered_data['cnt_day'].sum()))
with col2:
    st.metric("Total Hourly Rentals", value=int(filtered_data['cnt_hour'].sum()))

# =========================================
#  TREND PENYEWAAN HARIAN
# =========================================
st.subheader("📈 Tren Penyewaan Harian")
daily_df = filtered_data.groupby('dteday')['cnt_day'].sum().reset_index()
daily_df.rename(columns={'cnt_day':'total_rentals'}, inplace=True)

fig_daily = px.line(
    daily_df,
    x='dteday',
    y='total_rentals',
    title='Total Penyewaan Sepeda per Hari',
    labels={'dteday':'Tanggal', 'total_rentals':'Jumlah Penyewaan'},
    hover_data={'total_rentals': True, 'dteday': True}
)
st.plotly_chart(fig_daily, use_container_width=True)

# =========================================
#  PENYEWAAN PER JAM
# =========================================
st.subheader("⏰ Penyewaan per Jam")
hourly_df = filtered_data.groupby('hr')['cnt_hour'].sum().reset_index()
hourly_df.rename(columns={'cnt_hour':'total_rentals'}, inplace=True)

fig_hourly = px.bar(
    hourly_df,
    x='hr',
    y='total_rentals',
    title='Total Penyewaan Sepeda per Jam',
    labels={'hr':'Jam', 'total_rentals':'Jumlah Penyewaan'},
    color='total_rentals',
    color_continuous_scale='Blues'
)
st.plotly_chart(fig_hourly, use_container_width=True)

# =========================================
#  PENYEWAAN BERDASARKAN CUACA
# =========================================
st.subheader("🌤 Penyewaan Berdasarkan Kondisi Cuaca")

weather_df = filtered_data.groupby('weather_desc')['cnt_hour'].mean().reset_index()
weather_df.rename(columns={'cnt_hour':'avg_rentals'}, inplace=True)

fig_weather = px.bar(
    weather_df,
    x='weather_desc',
    y='avg_rentals',
    title='Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca (Per Jam)',
    labels={'weather_desc':'Kondisi Cuaca','avg_rentals':'Rata-rata Penyewaan'},
    color='weather_desc',
    color_discrete_map={
        "Clear / Few Clouds": "#87CEFA",
        "Mist / Cloudy": "#4682B4",
        "Light Snow / Rain": "#1E90FF",
        "Heavy Rain / Snow / Fog": "#0D47A1"
    }
)
st.plotly_chart(fig_weather, use_container_width=True)

# Insight cuaca
st.markdown("""
**Insight:**  
- Cuaca **Clear/Few Clouds** rata-rata penyewa tertinggi (~204 per jam), menunjukkan cuaca cerah mendorong aktivitas bersepeda.  
- Cuaca **Mist/Cloudy** moderat (~175 per jam), aktivitas bersepeda sedikit menurun.  
- Cuaca **Light Snow/Rain** menurun (~111 per jam).  
- Cuaca **Heavy Rain/Snow/Fog** paling rendah (~74 per jam), cuaca ekstrim menurunkan aktivitas.
""")

# =========================================
#  PENYEWAAN BERDASARKAN DEMAND LEVEL & MUSIM
# =========================================
st.subheader("📊 Segmentasi Permintaan Berdasarkan Musim")

season_demand = filtered_data.groupby(['season_cat','demand_level'])['cnt_day'].count().reset_index()
season_demand.rename(columns={'cnt_day':'days_count'}, inplace=True)

fig_season = px.bar(
    season_demand,
    x='season_cat',
    y='days_count',
    color='demand_level',
    barmode='group',
    title='Segmentasi Permintaan Sepeda Berdasarkan Musim',
    labels={'season_cat':'Musim','days_count':'Jumlah Hari','demand_level':'Tingkat Permintaan'},
    category_orders={'season_cat':['Spring','Summer','Fall','Winter'],'demand_level':['Low','Medium','High']}
)
st.plotly_chart(fig_season, use_container_width=True)

# Insight musim
st.markdown("""
**Insight:**  
- **Fall & Summer** memiliki jumlah hari permintaan tinggi, aktivitas bersepeda meningkat karena cuaca mendukung.  
- **Spring & Winter** memiliki jumlah hari permintaan rendah/seimbang, kemungkinan karena cuaca kurang mendukung.
""")

# =========================================
#  PENYEWAAN BERDASARKAN DEMAND LEVEL & CUACA
# =========================================
st.subheader("📊 Segmentasi Permintaan Berdasarkan Kondisi Cuaca")

weather_demand = filtered_data.groupby(['weather_desc','demand_level'])['cnt_day'].count().reset_index()
weather_demand.rename(columns={'cnt_day':'days_count'}, inplace=True)

fig_weather2 = px.bar(
    weather_demand,
    x='weather_desc',
    y='days_count',
    color='demand_level',
    barmode='group',
    title='Segmentasi Permintaan Sepeda Berdasarkan Kondisi Cuaca',
    labels={'weather_desc':'Kondisi Cuaca','days_count':'Jumlah Hari','demand_level':'Tingkat Permintaan'},
    category_orders={'demand_level':['Low','Medium','High'],'weather_desc':sorted(weather_demand['weather_desc'].unique())}
)
st.plotly_chart(fig_weather2, use_container_width=True)

# Insight demand level vs cuaca
st.markdown("""
**Insight:**  
- Cuaca **cerah** mendominasi permintaan tinggi.  
- Cuaca **hujan/salju** cenderung dominan permintaan rendah, menunjukkan cuaca ekstrim mengurangi aktivitas.
""")

st.markdown("---")
st.caption("© 2025 Bike Sharing Analysis Dashboard – Dibuat dengan Streamlit & Plotly")
