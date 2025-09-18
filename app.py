import streamlit as st
import pandas as pd
import plotly.express as px
from fetch_data import get_inflation, get_gse_data, get_bank_data

st.title("Ghana Economy Snapshot")
tab1, tab2, tab3 = st.tabs(["Economy", "GSE Stocks", "Banks"])

# Economy Tab
with tab1:
    st.subheader("Economic Indicators")
    inflation_df = get_inflation()
    
    # Check if inflation_df is empty
    if inflation_df.empty:
        st.write("Failed to fetch inflation data.")
    else:
        st.write(f"Latest Inflation (2025): {inflation_df['value'].iloc[-1]}%")
        fig = px.line(inflation_df, x='date', y='value', title="Inflation Trend")
        st.plotly_chart(fig)

# GSE Stocks Tab
with tab2:
    st.subheader("Top GSE Stocks")
    gse_df = get_gse_data()
    
    # Check if gse_df is empty
    if gse_df.empty:
        st.write("Failed to fetch GSE data.")
    else:
        st.dataframe(gse_df)
        fig = px.bar(gse_df, x='stock', y='ytd_return', title="GSE Performance 2025")
        st.plotly_chart(fig)

# Banks Tab
with tab3:
    st.subheader("Bank Products")
    banks_df = get_bank_data()
    
    # Check if banks_df is empty
    if banks_df.empty:
        st.write("Failed to fetch bank data.")
    else:
        st.table(banks_df)
        st.write("Compare savings and investment options.")
