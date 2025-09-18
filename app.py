import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
try:
    from statsmodels.tsa.filters.hp_filter import hpfilter
except ImportError:
    st.error("The 'statsmodels' library is not installed. Please install it using 'pip install statsmodels'.")
    st.stop()

# FRED API Key
FRED_API_KEY = "467fe69919c067bbe2cf724fd86c501e"

# Dictionary of countries and their FRED country codes
COUNTRIES = {
    'Ghana': 'GHA',
    'Nigeria': 'NGA',
    'Kenya': 'KEN'
}

# Dictionary of economic indicators with exact FRED series IDs per country
ECONOMIC_INDICATORS = {
    'Ghana': {
        'inflation': 'FPCPITOTLZGGHA',
        'gdp': 'MKTGDPGHA646NWDB',
        'gdp_growth': 'GHANGDPRPCPPPT',
        'youth_unemployment': 'SLUEM1524ZSGHA',
        'lending_rate': 'DDDI12GHA156NWDB',
        'deposit_rate': 'DDDI01GHA156NWDB'
    },
    'Nigeria': {
        'inflation': 'FPCPITOTLZGNGA',
        'gdp': 'MKTGDPNGA646NWDB',
        'gdp_per_capita': 'NYGDPPCAPCDNGA',
        'gdp_growth': 'NGANGDPRPCPPPT',
        'unemployment': 'SLUEMTOTLZSNGA',
        'youth_unemployment': 'SLUEM1524ZSNGA',
        'lending_rate': 'DDDI12NGA156NWDB',
        'deposit_rate': 'DDDI01NGA156NWDB',
        'exchange_rate': 'EXNGUS',
        'current_account_balance_percent_gdp': 'BPBLTT01NGA637S'
    },
    'Kenya': {
        'inflation': 'FPCPITOTLZGKEN',
        'gdp': 'MKTGDPKEA646NWDB',
        'gdp_per_capita': 'NYGDPPCAPCDKEN',
        'gdp_growth': 'KENNGDPRPCPPPT',
        'unemployment': 'SLUEMTOTLZSKEN',
        'youth_unemployment': 'SLUEM1524ZSKEN',
        'lending_rate': 'DDDI12KEA156NWDB',
        'deposit_rate': 'DDDI01KEA156NWDB',
        'exchange_rate': 'EXKZUS',
        'current_account_balance_percent_gdp': 'BPBLTT01KEA637S'
    }
}

# Dictionary of chart colors per country
CHART_COLORS = {
    'Ghana': {
        'light': {'actual': '#28a745', 'trend': '#28a745', 'cycle': '#218838'},
        'dark': {'actual': '#20c997', 'trend': '#20c997', 'cycle': '#17a2b8'}
    },
    'Nigeria': {
        'light': {'actual': '#1a73e8', 'trend': '#1a73e8', 'cycle': '#6610f2'},
        'dark': {'actual': '#00ffcc', 'trend': '#00ffcc', 'cycle': '#ffeb3b'}
    },
    'Kenya': {
        'light': {'actual': '#6610f2', 'trend': '#6610f2', 'cycle': '#6f42c1'},
        'dark': {'actual': '#ffeb3b', 'trend': '#ffeb3b', 'cycle': '#ffd700'}
    }
}

# Function to fetch FRED data for a specific country
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_fred_data(country, series_dict):
    os.makedirs('data', exist_ok=True)
    data_frames = {}
    if country not in series_dict or not series_dict[country]:
        st.warning(f"No series IDs defined for {country}. Please contact the developer to update the series IDs.")
        return data_frames
    for indicator_name, series_id in series_dict[country].items():
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json().get('observations', [])
            if not data:
                st.warning(f"No data available for {indicator_name.replace('_', ' ').title()} in {country}.")
                continue
            df = pd.DataFrame(data)[['date', 'value']]
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'])
            csv_path = f'data/{indicator_name}_{country}.csv'
            df.to_csv(csv_path, index=False)
            data_frames[indicator_name] = df
        except requests.exceptions.RequestException as e:
            st.warning(f"Failed to fetch {indicator_name.replace('_', ' ').title()} for {country}: {str(e)}")
            continue
    return data_frames

# Custom CSS for website-like design with centered headers
if selected_theme := st.sidebar.radio("Select Theme", ["Light", "Dark"], key="theme_selector"):
    if selected_theme == "Light":
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #f5f5f5;
                color: #1a1a1a;
                font-family: 'EB Garamond', Garamond, serif;
                margin: 0;
                padding: 0;
            }
            .main-header {
                background-color: #ffffff;
                padding: 20px 40px;
                border-bottom: 2px solid #1a73e8;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            .main-header h1 {
                font-family: 'EB Garamond', Garamond, serif;
                font-size: 36px;
                font-weight: 700;
                color: #1a73e8;
                margin: 0;
                text-align: center;
            }
            .main-header p {
                font-size: 20px;
                color: #4a4a4a;
                margin: 10px 0 0;
                font-family: 'EB Garamond', Garamond, serif;
                text-align: center;
            }
            .stPlotlyChart {
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                padding: 20px;
                margin-bottom: 30px;
            }
            .stTabs [data-baseweb="tab-list"] {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 8px;
                border-bottom: 1px solid #d3d3d3;
                margin-bottom: 30px;
                display: flex;
                justify-content: center;
            }
            .stTabs [data-baseweb="tab"] {
                color: #1a1a1a;
                font-family: 'EB Garamond', Garamond, serif;
                font-size: 22px;
                font-weight: 600;
                padding: 15px 30px;
                margin: 0 10px;
                border-radius: 8px;
                transition: background-color 0.3s ease;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: #1a73e8;
                color: #ffffff;
                border-bottom: 4px solid #135ab6;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e6f0fa;
            }
            h1, h2, h3 {
                font-family: 'EB Garamond', Garamond, serif;
                color: #1a1a1a;
                text-align: center;
                display: flex;
                justify-content: center;
                width: 100%;
            }
            h2 {
                font-size: 28px;
                font-weight: 600;
                margin-bottom: 20px;
            }
            .stMarkdown p {
                font-size: 20px;
                line-height: 1.8;
                color: #1a1a1a;
                margin-bottom: 20px;
                text-align: center;
            }
            .stSelectbox label {
                font-size: 20px;
                color: #1a1a1a;
                font-weight: 600;
                text-align: center;
                display: block;
            }
            .sidebar .sidebar-content {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 20px;
            }
            .sidebar .stRadio > label {
                font-size: 20px;
                color: #1a1a1a;
                text-align: center;
            }
            .footer {
                background-color: #ffffff;
                padding: 20px 40px;
                border-top: 1px solid #d3d3d3;
                text-align: center;
                margin-top: 40px;
            }
            .footer p {
                font-size: 18px;
                color: #4a4a4a;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:  # Dark
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #1c2526;
                color: #e6e6e6;
                font-family: 'EB Garamond', Garamond, serif;
                margin: 0;
                padding: 0;
            }
            .main-header {
                background-color: #2a2a2a;
                padding: 20px 40px;
                border-bottom: 2px solid #00ffcc;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                margin-bottom: 30px;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            .main-header h1 {
                font-family: 'EB Garamond', Garamond, serif;
                font-size: 36px;
                font-weight: 700;
                color: #00ffcc;
                margin: 0;
                text-align: center;
            }
            .main-header p {
                font-size: 20px;
                color: #b0b0b0;
                margin: 10px 0 0;
                font-family: 'EB Garamond', Garamond, serif;
                text-align: center;
            }
            .stPlotlyChart {
                background-color: #2a2a2a;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                padding: 20px;
                margin-bottom: 30px;
            }
            .stTabs [data-baseweb="tab-list"] {
                background-color: #2a2a2a;
                padding: 15px;
                border-radius: 8px;
                border-bottom: 1px solid #555555;
                margin-bottom: 30px;
                display: flex;
                justify-content: center;
            }
            .stTabs [data-baseweb="tab"] {
                color: #e6e6e6;
                font-family: 'EB Garamond', Garamond, serif;
                font-size: 22px;
                font-weight: 600;
                padding: 15px 30px;
                margin: 0 10px;
                border-radius: 8px;
                transition: background-color 0.3s ease;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: #00ffcc;
                color: #1c2526;
                border-bottom: 4px solid #00ccaa;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #4a4a4a;
            }
            h1, h2, h3 {
                font-family: 'EB Garamond', Garamond, serif;
                color: #e6e6e6;
                text-align: center;
                display: flex;
                justify-content: center;
                width: 100%;
            }
            h2 {
                font-size: 28px;
                font-weight: 600;
                margin-bottom: 20px;
            }
            .stMarkdown p {
                font-size: 20px;
                line-height: 1.8;
                color: #e6e6e6;
                margin-bottom: 20px;
                text-align: center;
            }
            .stSelectbox label {
                font-size: 20px;
                color: #e6e6e6;
                font-weight: 600;
                text-align: center;
                display: block;
            }
            .sidebar .sidebar-content {
                background-color: #2a2a2a;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                margin: 20px;
            }
            .sidebar .stRadio > label {
                font-size: 20px;
                color: #e6e6e6;
                text-align: center;
            }
            .footer {
                background-color: #2a2a2a;
                padding: 20px 40px;
                border-top: 1px solid #555555;
                text-align: center;
                margin-top: 40px;
            }
            .footer p {
                font-size: 18px;
                color: #b0b0b0;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# Header
st.markdown(
    """
    <div class="main-header">
        <h1>EconCentr</h1>
        <p>A platform for Economics, Finance, and Business enthusiasts</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Tabs
about_tab, data_tab, thoughts_tab, partners_tab = st.tabs(["About Us", "Our Data", "Econ Thoughts", "Partners"])

# Common Plotly layout settings with watermark
def apply_chart_layout(fig, title, theme):
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
                'size': 28,
                'family': 'EB Garamond, Garamond, serif',
                'color': '#1a1a1a' if theme == "Light" else '#e6e6e6',
                'weight': 'bold'
            }
        },
        width=1100,
        height=700,
        margin=dict(l=80, r=80, t=120, b=80),
        plot_bgcolor='#ffffff' if theme == "Light" else '#2a2a2a',
        paper_bgcolor='#ffffff' if theme == "Light" else '#2a2a2a',
        font=dict(
            family='EB Garamond, Garamond, serif',
            color='#1a1a1a' if theme == "Light" else '#e6e6e6',
            size=18
        ),
        xaxis=dict(
            tickfont=dict(
                family='EB Garamond, Garamond, serif',
                color='#1a1a1a' if theme == "Light" else '#e6e6e6',
                size=16
            ),
            gridcolor='#d3d3d3' if theme == "Light" else '#555555',
            zerolinecolor='#d3d3d3' if theme == "Light" else '#555555'
        ),
        yaxis=dict(
            tickfont=dict(
                family='EB Garamond, Garamond, serif',
                color='#1a1a1a' if theme == "Light" else '#e6e6e6',
                size=16
            ),
            gridcolor='rgba(0,0,0,0)',  # Remove horizontal grid lines
            zerolinecolor='#d3d3d3' if theme == "Light" else '#555555'
        ),
        annotations=[
            dict(
                text="EconCentr by Osman John Froko",
                x=0.98,
                y=0.02,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(
                    family='EB Garamond, Garamond, serif',
                    size=10,
                    color='#999999' if theme == "Light" else '#666666'
                ),
                opacity=0.3
            )
        ]
    )
    return fig

# About Us Tab
with about_tab:
    st.subheader("About EconCentr")
    st.markdown("""
    **Mission Statement**  
    EconCentr is dedicated to fostering a vibrant community of Economics, Finance, and Business enthusiasts. Our mission is to provide a free, accessible platform where individuals can showcase their ideas, essays, and insights on economic policies, financial strategies, and business innovations without the need for formal publication. We aim to empower voices from all backgrounds to contribute to the global economic discourse.

    **Vision Statement**  
    We envision EconCentr as a leading hub for open, inclusive, and thought-provoking discussions in Economics. By offering a space for both seasoned professionals and emerging thinkers to share their perspectives, we strive to inspire informed policy-making and innovative solutions that drive economic progress worldwide.
    """)

# Our Data Tab
with data_tab:
    st.subheader("Economic Indicators")
    st.caption("Data sourced from FRED (Federal Reserve Economic Data)")
    
    # Country selection dropdown
    selected_country = st.selectbox("Select Country", sorted(list(COUNTRIES.keys())), key="country_selector")
    
    # Fetch data for the selected country
    data_frames = fetch_fred_data(selected_country, ECONOMIC_INDICATORS)
    
    if not data_frames:
        st.warning(f"No data available for {selected_country}. Please select another country or contact the developer to update series IDs.")
    else:
        for indicator, df in data_frames.items():
            if df.empty:
                continue
            df = df.dropna(subset=['value'])
            if len(df) == 0:
                continue
            
            # Actual Data Chart
            fig_actual = px.area(df, x='date', y='value',
                                 labels={'value': 'Value', 'date': 'Date'})
            fig_actual.update_traces(
                fill='tozeroy',
                line_color=CHART_COLORS[selected_country][selected_theme.lower()]['actual']
            )
            fig_actual = apply_chart_layout(fig_actual, f"{indicator.replace('_', ' ').title()} Actual Data", selected_theme)
            st.plotly_chart(fig_actual, use_container_width=True)
            
            if len(df) > 4:
                try:
                    cycle, trend = hpfilter(df['value'], lamb=6.25)
                    df['trend'] = trend
                    df['cycle'] = cycle
                    col1, col2 = st.columns(2)
                    
                    # Trend Chart
                    with col1:
                        fig_trend = px.area(df, x='date', y='trend',
                                            labels={'trend': 'Trend Value', 'date': 'Date'})
                        fig_trend.update_traces(
                            fill='tozeroy',
                            line_color=CHART_COLORS[selected_country][selected_theme.lower()]['trend']
                        )
                        fig_trend = apply_chart_layout(fig_trend, f"{indicator.replace('_', ' ').title()} Trend", selected_theme)
                        st.plotly_chart(fig_trend, use_container_width=True)
                    
                    # Cyclical Chart
                    with col2:
                        fig_cycle = px.area(df, x='date', y='cycle',
                                            labels={'cycle': 'Cyclical Value', 'date': 'Date'})
                        fig_cycle.update_traces(
                            fill='tozeroy',
                            line_color=CHART_COLORS[selected_country][selected_theme.lower()]['cycle']
                        )
                        fig_cycle = apply_chart_layout(fig_cycle, f"{indicator.replace('_', ' ').title()} Cyclical", selected_theme)
                        st.plotly_chart(fig_cycle, use_container_width=True)
                except Exception:
                    pass

# Econ Thoughts Tab
with thoughts_tab:
    st.subheader("Econ Thoughts")
    st.markdown("""
    Econ Thoughts is your space to share and explore ideas on economics, finance, and business. Whether you're analyzing fiscal policies, market trends, or business strategies, this platform welcomes essays, opinions, and discussions from enthusiasts at all levels. Stay tuned for a submission system where you can contribute your insights and engage with a global community of thinkers.
    """)

# Partners Tab
with partners_tab:
    st.subheader("Our Partners")
    st.markdown("""
    EconCentr collaborates with academic institutions, economic research organizations, and industry leaders to advance the study and discussion of economics. We are actively seeking partners who share our vision of making economic knowledge accessible to all. More information on our partnerships will be available soon.
    """)

# Footer
st.markdown(
    """
    <div class="footer">
        <p>&copy; 2025 EconCentr. All rights reserved. Powered by FRED.</p>
    </div>
    """,
    unsafe_allow_html=True
)