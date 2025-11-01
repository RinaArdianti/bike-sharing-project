import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

sns.set(style='darkgrid')


data = pd.read_csv("merged_bike_data_cleaned.csv")  


data['dteday'] = pd.to_datetime(data['dteday']).dt.date
data.sort_values(by='dteday', inplace=True)
data.reset_index(drop=True, inplace=True)


def create_daily_rentals(df):
    daily_df = df.groupby('dteday')['cnt_day'].sum().reset_index()
    daily_df.rename(columns={'cnt_day': 'total_rentals'}, inplace=True)
    return daily_df

def create_hourly_rentals(df):
    hourly_df = df.groupby('hr')['cnt_hour'].sum().reset_index()
    hourly_df.rename(columns={'cnt_hour': 'total_rentals'}, inplace=True)
    return hourly_df

def create_weather_rentals(df):
    weather_df = df.groupby('weathersit')['cnt_day'].sum().reset_index()
    weather_df.rename(columns={'cnt_day': 'total_rentals'}, inplace=True)
    return weather_df

def create_demand_rentals(df):
    demand_df = df.groupby('demand_level')['cnt_day'].sum().reset_index()
    demand_df.rename(columns={'cnt_day': 'total_rentals'}, inplace=True)
    return demand_df


st.sidebar.header("Filter Data")


min_date = data['dteday'].min()
max_date = data['dteday'].max()


if not isinstance(min_date, pd.Timestamp):
    min_date = pd.to_datetime(min_date).date()
if not isinstance(max_date, pd.Timestamp):
    max_date = pd.to_datetime(max_date).date()

start_date, end_date = st.sidebar.date_input(
    "Pilih rentang tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)


filtered_data = data[(data['dteday'] >= start_date) & (data['dteday'] <= end_date)]


st.title("🚴 Bike Sharing Dashboard")
st.markdown("Visualisasi penyewaan sepeda harian dan faktor-faktor yang memengaruhinya")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Daily Rentals", value=int(filtered_data['cnt_day'].sum()))
with col2:
    st.metric("Total Hourly Rentals", value=int(filtered_data['cnt_hour'].sum()))




st.subheader("📈 Tren Penyewaan Harian")
daily_df = create_daily_rentals(filtered_data)
fig1 = px.line(daily_df, x='dteday', y='total_rentals', title='Total Daily Rentals')
st.plotly_chart(fig1, use_container_width=True)


st.subheader("⏰ Penyewaan per Jam")
hourly_df = create_hourly_rentals(filtered_data)
fig2, ax = plt.subplots(figsize=(12,6))
sns.barplot(x='hr', y='total_rentals', data=hourly_df, palette="Blues_d", ax=ax)
ax.set_xlabel("Jam")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig2)


st.subheader("🌤 Penyewaan Berdasarkan Cuaca")
weather_df = create_weather_rentals(filtered_data)
fig3, ax = plt.subplots(figsize=(8,5))
sns.barplot(x='weathersit', y='total_rentals', data=weather_df, palette="coolwarm", ax=ax)
ax.set_xlabel("Cuaca (weathersit)")
ax.set_ylabel("Jumlah Penyewaan")
st.pyplot(fig3)


if 'demand_level' in filtered_data.columns:
    st.subheader("📊 Penyewaan Berdasarkan Demand Level")
    demand_df = create_demand_rentals(filtered_data)
    fig4 = px.bar(demand_df, x='demand_level', y='total_rentals', color='demand_level',
                  title="Penyewaan per Demand Level")
    st.plotly_chart(fig4, use_container_width=True)
