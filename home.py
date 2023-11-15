import streamlit as st
import folium

import altair as alt
from streamlit_folium import st_folium, folium_static
import geopandas as gpd
import pandas as pd
import numpy as np
import json

# Page Configuration
# Page configuration for Simple PDF App
st.set_page_config(
    page_title="Global Water Scarcity Tracker",
    page_icon="💧",
    layout="wide",
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
    # Load the predictions data from the JSON file
    with open("updated_all_country_predictions.json", 'r') as file:
        predictions = json.load(file)
    return geo_data, predictions

geo_data, predictions = load_data()

# Set the range of years for the slider
min_year = 1975
max_year = int(geo_data["Year"].max())

year = st.slider("Select a year:", min_year, max_year, value=2019)

def create_choropleth_map(geo_data, predictions, year):
    m = folium.Map(location=[20, 0], zoom_start=2, tiles=None)

    # Add TileLayer with no_wrap set to True
    folium.TileLayer('cartodb positron', no_wrap=True).add_to(m)

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

map_ = create_choropleth_map(geo_data, predictions, year)
st_folium(map_, height=500, use_container_width=True)

st.title("Analyze Countries and Key Metrics")

metrics_tab, comparison_tab, global_tab = st.tabs(["Country Metrics", "Compare Countries", "Global Predictions"])

metric_colors = {
    "Freshwater Resources Per Capita (m³)": 'steelblue',
    "Annual Freshwater Use (m³)": 'darkorange',
    "Population": 'firebrick',
    "GDP Per Capita ($) PPP": 'mediumpurple'
}

with metrics_tab:
    # User can select a country
    countries_list = list(predictions.keys())
    default_index = countries_list.index("World") if "World" in countries_list else 0

    country_select = st.selectbox("Search for a Country", countries_list, index=default_index)
    
    # User can select a metric to visualize
    metric_select = st.selectbox("Select a Metric", list(metric_colors.keys()), help="Metrics selected are predicted using the Prophet time series forecasting models and do not take envrionmental, social, and political factors into account. All metrics are viewed independently.")

    st.divider()
    
    metric_column_mapping = {
        "Freshwater Resources Per Capita (m³)": 'Freshwater_Resources_Per_Capita_m3',
        "Annual Freshwater Use (m³)": 'Annual_Freshwater_Use',
        "Population": 'Historical_Population',
        "GDP Per Capita ($) PPP": 'GDP_Per_Capita'
    }
    
    metric_column = metric_column_mapping[metric_select]
    
    # Fetching the predictions for the selected country and metric
    selected_country_data = pd.DataFrame(predictions[country_select].get(metric_column, []))
    
    if not selected_country_data.empty:
        # Plotting the predicted metric (yhat) over time for the selected country using Altair
        line = alt.Chart(selected_country_data).mark_line(color=metric_colors[metric_select]).encode(
            x=alt.X('ds:O', axis=alt.Axis(title='Year', labelAngle=0)),
            y=alt.Y(f'yhat:Q', axis=alt.Axis(title=metric_select)),
        )
        
        # Shading between yhat_upper and yhat_lower
        area = alt.Chart(selected_country_data).mark_area(opacity=0.3, color=metric_colors[metric_select]).encode(
            x='ds:O',
            y='yhat_upper:Q',
            y2='yhat_lower:Q',
            tooltip=alt.value(None)
        )
        
        points = alt.Chart(selected_country_data).mark_point(color=metric_colors[metric_select], size=30).encode(
            x=alt.X('ds:O', title='Year'),
            y=alt.Y(f'yhat:Q', title=metric_select),
            tooltip=[
                alt.Tooltip('ds:O', title='Year'),
                alt.Tooltip('yhat:Q', title=metric_select, format=".2f"),
                alt.Tooltip('yhat_lower:Q', title='Lower Bound', format=".2f"),
                alt.Tooltip('yhat_upper:Q', title='Upper Bound', format=".2f")
            ]
        )
        
        chart = (area + line + points).properties(
            title={
                "text": f"{metric_select} Predictions Over Time for {country_select}",
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
        st.warning(f"No predictions available for {metric_select} in {country_select}.")



with comparison_tab:
    # Use a multiselect box to allow users to select multiple countries
    country_select = st.multiselect("Search for Countries", list(predictions.keys()))

    col1, col2 = st.columns(2)

    with col1: 
        multi_metric_select = st.selectbox("Select Metric", list(metric_colors.keys()))

    with col2:
        analysis_type = st.selectbox("Select Analysis Type", ['Nominal', 'Cumulative', 'YoY Growth Rate (%)', '3Yr Avg. Growth Rate (%)'])

    st.subheader(" ")

    # Map the selected metric to its appropriate column name
    metric_column = metric_column_mapping[multi_metric_select]

    # If countries are selected
    if country_select:
        # Fetching the predictions for the selected countries and metric
        all_selected_data = []
        for country in country_select:
            country_data = pd.DataFrame(predictions[country].get(metric_column_mapping[multi_metric_select], []))
            country_data['Country'] = country
            all_selected_data.append(country_data)

        filtered_data = pd.concat(all_selected_data)

        print(filtered_data.columns)

        if analysis_type == 'Cumulative':
            filtered_data['yhat'] = filtered_data.groupby('Country')['yhat'].transform(lambda x: x - x.iloc[0])
        elif analysis_type == 'YoY Growth Rate (%)':
            filtered_data['yhat'] = filtered_data.groupby('Country')['yhat'].pct_change() * 100
        elif analysis_type == '3Yr Avg. Growth Rate (%)':
            filtered_data['yhat'] = filtered_data.groupby('Country')['yhat'].pct_change(periods=3) * 100


        shade = alt.Chart(pd.DataFrame({'ds': [2020, 2040]})).mark_rect(opacity=0.4, color='lightgray').encode(
            x='min(ds):O',
            x2='max(ds):O',
            tooltip=alt.value(None),
        )

        base_chart = alt.Chart(filtered_data).encode(
            x=alt.X('ds:O', title='Year'),
            y=alt.Y('yhat:Q', title=multi_metric_select),
            color=alt.Color('Country:N', legend=alt.Legend(title="Country")),
            tooltip=['Country', alt.Tooltip('ds:O', title='Year'), alt.Tooltip('yhat:Q', title=multi_metric_select, format=".2f")]
        )

        historical_chart = base_chart.mark_line().encode(
            x=alt.X('ds:O', title='Year'),
            y=alt.Y('yhat:Q', title=multi_metric_select),
            color=alt.Color('Country:N', legend=alt.Legend(title="Country")),
            tooltip=['Country', alt.Tooltip('ds:O', title='Year'), alt.Tooltip('yhat:Q', title=multi_metric_select, format=".2f")]
        ).transform_filter(
            alt.datum.ds <= 2020
        ) + base_chart.mark_circle(size=30).transform_filter(
            alt.datum.ds <= 2020
        )

        predicted_chart = base_chart.mark_line(strokeDash=[2, 2]).encode(
            x=alt.X('ds:O', title='Year'),
            y=alt.Y('yhat:Q', title=multi_metric_select),
            color=alt.Color('Country:N', legend=alt.Legend(title="Country")),
            tooltip=['Country', alt.Tooltip('ds:O', title='Year'), alt.Tooltip('yhat:Q', title=multi_metric_select, format=".2f")]
        ).transform_filter(
            alt.datum.ds > 2019
        ) + base_chart.mark_circle(size=30).transform_filter(
            alt.datum.ds > 2019
        )

        # Combining both charts
        chart = (shade + historical_chart + predicted_chart).properties(
            title={
                "text": f"Comparison of {multi_metric_select} Over Time ({analysis_type})",
                "fontSize": 18,
                "fontWeight": "bold",
                "subtitle": "Dotted lines and shaded area represent predicted values post-2020 (Up to 2040).",
                "subtitleFontSize": 14,
                "anchor": "start"
            },
            width=800,
            height=500
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Please select at least one country to display the data.")


with global_tab:
    st.warning("Section under Construction - Check back in for updates")
