import streamlit as st
import folium
import matplotlib.pyplot as plt
import altair as alt
from streamlit_folium import st_folium, folium_static
import geopandas as gpd
import pandas as pd
import numpy as np

# Page Configuration
# Page configuration for Simple PDF App
st.set_page_config(
    page_title="Global Water Scarcity Tracker",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="expanded"
    )

# Streamlit UI
st.title("Global Water Scarcity Tracker 💧")

st.info("""
Water scarcity is an escalating global concern. As the demand for freshwater continues to rise due to population growth, urbanization, and increased agricultural needs, the available freshwater resources are depleting¹:

**Water Scarcity:** 87 out of 180 countries are projected to be water scarce by 2050.

**Declining Freshwater:** Freshwater availability per capita will decline in low-income countries.

**Emerging Hotspots:** Sub-Saharan Africa is expected to become the next hotspot of water scarcity.

**Transition of Water-Rich Countries:** Many water-rich countries are projected to become water-scarce by 2050.

""", icon="ℹ️")

with st.expander("📈 How are predictions made?"):
    st.markdown("""
    The predictive insights provided are based on advanced modeling techniques that are designed to forecast future scenarios based on past and current data patterns.
    """)

    st.info("""
    **Methodology:**

    **Data Preprocessing:** Before predictions, the data is cleaned and preprocessed to ensure accuracy.

    **Time-Series Prediction:** For predictive analytics, we use Facebook's Prophet, a ML tool known for its time-series based predictive modeling capabilities.
    """, icon="🛠️")

    st.warning("""    
    **Limitations:**

    **External Factors:** Our models do not consider various external factors like climate change, geopolitical events, and economic shifts which might influence water availability.

    **Continuous Refinement:** The models will need to be periodically refined and trained with new data to enhance the prediction accuracy. Currently using real-data up till 2019.
    
    **Disclaimer:** The predictions and insights provided here are for illustration and research purposes only. While we strive for accuracy, these predictions are based on current available data and modeling techniques, which have inherent limitations. It's essential to approach these insights with caution and not solely rely on them for making critical decisions.
    """, icon="⚠️")


    st.markdown("""
        """)


with st.sidebar:
    st.subheader("Updates Required:", anchor=False)
    st.warning("""
        1. Speed up re-rendering of dataset by storing GeoJSON in persistent database
        
        2. Improve UX for dynamic metrics per country 
        
        3. Implement ML model for water scarcity prediction based on persisting trends - project out to 2050 
    
        """
        )

    st.divider()

with st.sidebar:
    st.subheader("👨‍💻 Author: **Yaksh Birla**", anchor=False)
    
    st.subheader("🔗 Contact / Connect:", anchor=False)
    st.markdown(
        """
        - [Email](mailto:yb.codes@gmail.com)
        - [LinkedIn](https://www.linkedin.com/in/yakshb/)
        - [Github Profile](https://github.com/yakshb)
        - [Medium](https://medium.com/@yakshb)
        """
    )

    st.divider()
    st.subheader("Acknowledgements:")
    st.markdown(
        """
        - [Folium](https://python-visualization.github.io/folium/latest/user_guide/map.html)
        - [Our World in Data](https://ourworldindata.org/water-use-stress)
        - [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0048969721033015)
        - United Nations University Institute for Water, Environment and Health (UNU-INWEH)
        """
    )

@st.cache_data
def load_data():
    # Load GeoJSON file
    geo_data = gpd.read_file("data/predicted_data.geojson")
    # Load your CSV data
    data = pd.read_csv("data/Water_usage_combined.csv")
    return geo_data, data

geo_data, data = load_data()

# Set the range of years for the slider
min_year = 1975
max_year = int(geo_data["Year"].max())

year = st.slider("Select a year:", min_year, max_year, value=2019)

def create_choropleth_map(geo_data, data, year):
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodb positron")
    
    year_data = geo_data[geo_data["Year"] == year]
    
    cap_value = 18000
    year_data['Adjusted_Freshwater'] = np.where(year_data['Freshwater_Resources_Per_Capita_m3'] > cap_value, cap_value, year_data['Freshwater_Resources_Per_Capita_m3'])
    
    bins = list(year_data['Adjusted_Freshwater'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1]))

    popup = folium.GeoJsonPopup(
        fields=["Country", "Country_Code", "Annual_Freshwater_Use", "GDP_Per_Capita", "Freshwater_Resources_Per_Capita_m3"],
        aliases=["Country:", "Country Code:", "Annual Freshwater Use:", "GDP Per Capita:", "Freshwater Availability (m^3/person/year):"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: solid 1px #ADA9A9;
            padding: 5px;
            """,
        max_width=800,
    )

    choropleth = folium.Choropleth(
        geo_data=year_data,
        name="choropleth",
        data=year_data,
        columns=["Country_Code", "Adjusted_Freshwater"],
        key_on="feature.properties.Country_Code",  # This assumes that Country_Code is nested inside properties in your GeoJSON
        fill_color="RdYlBu",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"Freshwater Availability (m^3/person/year) - {year}",
        bins=bins,
        reset=True
    ).add_to(m)
    
    choropleth.geojson.add_child(popup)

    return m

map_ = create_choropleth_map(geo_data, data, year)
st_folium(map_, height=500, use_container_width=True)

st.title("Analyze Countries and Key Metrics")

metrics_tab, comparison_tab, global_tab = st.tabs(["Country Metrics", "Compare Countries", "Global Predictions"])

metric_colors = {
    "Freshwater Resources Per Capita (m³)": 'steelblue',
    "Annual Freshwater Use (m³)": 'darkorange',
    "Agriculture Freshwater Withdrawal (%)": 'forestgreen',
    "Population": 'firebrick',
    "GDP Per Capita ($)": 'mediumpurple'
}

with metrics_tab:
    # User can select a country
    country_select = st.selectbox("Search for a Country", data['Country'].unique())
    
    # User can select a metric to visualize
    metric_select = st.selectbox("Select a Metric", list(metric_colors.keys()))

    st.divider()
    
    # Mapping selected metric to the corresponding column in the dataframe
    metric_column_mapping = {
        "Freshwater Resources Per Capita (m³)": 'Freshwater_Resources_Per_Capita_m3',
        "Annual Freshwater Use (m³)": 'Annual_Freshwater_Use',
        "Agriculture Freshwater Withdrawal (%)": 'Agriculture_Freshwater_Withdrawal_Percent',
        "Population": 'Historical_Population',
        "GDP Per Capita ($)": 'GDP_Per_Capita'
    }
    
    metric_column = metric_column_mapping[metric_select]
    
    # Filtering data based on selected country
    selected_country_data = data[data['Country'] == country_select].dropna(subset=[metric_column])
    
    if not selected_country_data.empty:
        # Plotting the selected metric over time for the selected country using Altair
        line = alt.Chart(selected_country_data).mark_line(color=metric_colors[metric_select]).encode(
            x=alt.X('Year:O', axis=alt.Axis(title='Year', labelAngle=0)),
            y=alt.Y(f'{metric_column}:Q', axis=alt.Axis(title=metric_select)),
        )
        
        points = alt.Chart(selected_country_data).mark_point(color=metric_colors[metric_select], size=30).encode(
            x=alt.X('Year:O'),
            y=alt.Y(f'{metric_column}:Q'),
            tooltip=['Year', metric_column]
        )
        
        chart = (line + points).properties(
            title={
                "text": f"{metric_select} Over Time for {country_select}",
                "fontSize": 16,
                "fontWeight": "bold"
            },
            width=700,
            height=400
        ).configure_axis(
            grid=True,
            labelFontSize=12,
            titleFontSize=12
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning(f"No data available for {metric_select} in {country_select}.")


with comparison_tab:
    # Use a multiselect box to allow users to select multiple countries
    country_select = st.multiselect("Search for Countries", geo_data['Country'].unique())

    st.subheader(" ")

    # If countries are selected
    if country_select:
        filtered_data = geo_data[geo_data['Country'].isin(country_select)].copy()
        filtered_data = filtered_data[['Country', 'Year', 'Freshwater_Resources_Per_Capita_m3']]

        shade = alt.Chart(pd.DataFrame({'Year': [2020, 2050]})).mark_rect(opacity=0.4, color='lightgray').encode(
            x='min(Year):O',
            x2='max(Year):O',
            tooltip=alt.value(None),
        )

        base_chart = alt.Chart(filtered_data).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Freshwater_Resources_Per_Capita_m3:Q', title='Freshwater Resources Per Capita (m³)'),
            color=alt.Color('Country:N', legend=alt.Legend(title="Country")),
            tooltip=['Country', 'Year', 'Freshwater_Resources_Per_Capita_m3']
        )
        
        # Solid line with points for historical data
        historical_chart = base_chart.mark_line().encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Freshwater_Resources_Per_Capita_m3:Q', title='Freshwater Resources Per Capita (m³)'),
            color=alt.Color('Country:N', legend=alt.Legend(title="Country")),
            tooltip=['Country', 'Year', 'Freshwater_Resources_Per_Capita_m3']
        ).transform_filter(
            alt.datum.Year <= 2020
        ) + base_chart.mark_circle(size=30).transform_filter(
            alt.datum.Year <= 2020
        )

        # Dotted line with points for predicted data
        predicted_chart = base_chart.mark_line(strokeDash=[2, 2]).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Freshwater_Resources_Per_Capita_m3:Q', title='Freshwater Resources Per Capita (m³)'),
            color=alt.Color('Country:N', legend=alt.Legend(title="Country")),
            tooltip=['Country', 'Year', 'Freshwater_Resources_Per_Capita_m3']
        ).transform_filter(
            alt.datum.Year > 2019
        ) + base_chart.mark_circle(size=30).transform_filter(
            alt.datum.Year > 2019
        )

        # Combining both charts
        chart = (shade + historical_chart + predicted_chart).properties(
            title={
                "text": "Comparison of Freshwater Resources Per Capita Over Time",
                "fontSize": 18,
                "fontWeight": "bold",
                "subtitle": "Dotted lines represent predicted values post-2020 (Up to 2049).",
                "subtitleFontSize": 14,
                "anchor": "start"
            },
            width=800,
            height=500
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Please select at least one country to display the data.")
