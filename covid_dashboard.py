import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# --- Data Sources ---
url_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
url_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
url_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

# --- Load and cache data ---
@st.cache_data
def load_data():
    confirmed = pd.read_csv(url_confirmed)
    deaths = pd.read_csv(url_deaths)
    recovered = pd.read_csv(url_recovered)
    return confirmed, deaths, recovered

confirmed, deaths, recovered = load_data()

# --- Data Processing ---
confirmed_country = confirmed.drop(columns=["Province/State", "Lat", "Long"]).groupby("Country/Region").sum()
deaths_country = deaths.drop(columns=["Province/State", "Lat", "Long"]).groupby("Country/Region").sum()
recovered_country = recovered.drop(columns=["Province/State", "Lat", "Long"]).groupby("Country/Region").sum()

# Transpose for time series line chart
confirmed_ts = confirmed_country.T
confirmed_ts.index = pd.to_datetime(confirmed_ts.index, format="%m/%d/%y")

# --- Sidebar ---
st.sidebar.title("COVID-19 Dashboard")
country = st.sidebar.selectbox("Select a country", confirmed_country.index)

# --- Line Chart ---
st.title(f"COVID-19 Trend in {country}")
fig = px.line(confirmed_ts, y=country, x=confirmed_ts.index, title=f"{country} - Confirmed Cases Over Time")
st.plotly_chart(fig)
st.metric("Total Confirmed Cases", int(confirmed_ts[country].iloc[-1]))

# --- Global Trend Plot ---
st.subheader("Global Confirmed Cases Over Time")
fig2, ax2 = plt.subplots()
confirmed_ts.sum(axis=1).plot(ax=ax2, figsize=(10, 4), title='Global Confirmed Cases Over Time')
ax2.set_xlabel("Date")
ax2.set_ylabel("Cases")
ax2.grid(True)
st.pyplot(fig2)

# --- Top 5 Countries Bar Chart ---
st.subheader("Top 5 Countries - Confirmed Cases")
top5 = confirmed_country.iloc[:, -1].sort_values(ascending=False).head(5)
fig3, ax3 = plt.subplots()
top5.plot(kind='barh', ax=ax3, title='Top 5 Countries - Confirmed Cases')
ax3.set_xlabel("Total Cases")
st.pyplot(fig3)

# --- Compare Cases vs Deaths ---
st.subheader("Top 10 Countries - Cases vs Deaths")
compare_df = pd.DataFrame({
    'Confirmed': confirmed_country.sum(axis=1),
    'Deaths': deaths_country.sum(axis=1)
}).sort_values('Confirmed', ascending=False).head(10)
fig4, ax4 = plt.subplots()
compare_df.plot(kind='bar', ax=ax4, figsize=(10, 4), title='Top 10 Countries: Cases vs Deaths')
ax4.set_ylabel("Count")
ax4.grid(True)
st.pyplot(fig4)

# --- Death and Recovery Rates ---
total_confirmed = confirmed_country.sum(axis=1)
total_deaths = deaths_country.sum(axis=1)
total_recovered = recovered_country.sum(axis=1)

death_rate = (total_deaths / total_confirmed) * 100
recovery_rate = (total_recovered / total_confirmed) * 100

rates_df = pd.DataFrame({
    "Country/Region": total_confirmed.index,
    "Confirmed": total_confirmed.values,
    "Deaths": total_deaths.values,
    "Recovered": total_recovered.values,
    "Death Rate (%)": death_rate.values,
    "Recovery Rate (%)": recovery_rate.values
}).sort_values("Confirmed", ascending=False)

# --- Scatter Plot: Confirmed vs Deaths ---
_df_4 = pd.DataFrame({
    'Country/Region': total_confirmed.index,
    'Confirmed': total_confirmed.values,
    'Deaths': total_deaths.values
})
fig5, ax5 = plt.subplots()
_df_4.plot(kind='scatter', x='Confirmed', y='Deaths', s=32, alpha=0.7, ax=ax5, title="Confirmed vs Deaths")
st.pyplot(fig5)

# --- Interactive Bar Chart (Plotly) ---
top10 = rates_df.head(10)
fig6 = px.bar(top10,
              x='Country/Region',
              y='Confirmed',
              color='Country/Region',
              title='Top 10 Countries - Confirmed COVID-19 Cases',
              text='Confirmed')
st.plotly_chart(fig6)

# --- Interactive Scatter (Death vs Recovery Rate) ---
fig7 = px.scatter(top10,
                  x='Recovery Rate (%)',
                  y='Death Rate (%)',
                  size='Confirmed',
                  color='Country/Region',
                  title='Death vs Recovery Rate (Top 10 Countries)',
                  hover_name='Country/Region')
st.plotly_chart(fig7)
