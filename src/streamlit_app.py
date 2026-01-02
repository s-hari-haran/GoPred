"""Streamlit dashboard for Prophet-based portfolio forecasts - Neobrutalism Style."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Local data file path
DATA_FILE = Path(__file__).parent / "data" / "predictions.json"

# Page config
st.set_page_config(
    page_title="GoPred - A Prediction Model",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Neobrutalism CSS
st.markdown("""
<style>
    /* Import bold fonts */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Root variables */
    :root {
        --bg-primary: #FFFEF0;
        --bg-card: #FFFFFF;
        --accent-yellow: #FFE566;
        --accent-blue: #7EB8FF;
        --accent-pink: #FFB8D4;
        --accent-green: #B8FFB8;
        --accent-orange: #FFB366;
        --accent-purple: #C4B8FF;
        --text-primary: #1A1A1A;
        --border-color: #1A1A1A;
        --shadow: 4px 4px 0px #1A1A1A;
        --shadow-hover: 6px 6px 0px #1A1A1A;
    }
    
    /* Main background */
    .stApp {
        background-color: var(--bg-primary) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }
    
    /* Main title styling */
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #1A1A1A;
        text-align: center;
        padding: 1rem 2rem;
        background: var(--accent-yellow);
        border: 4px solid #1A1A1A;
        box-shadow: var(--shadow);
        margin-bottom: 2rem;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Card styling */
    .neo-card {
        background: var(--bg-card);
        border: 3px solid #1A1A1A;
        box-shadow: var(--shadow);
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    .neo-card:hover {
        box-shadow: var(--shadow-hover);
        transform: translate(-2px, -2px);
    }
    
    .neo-card-yellow { background: var(--accent-yellow); }
    .neo-card-blue { background: var(--accent-blue); }
    .neo-card-pink { background: var(--accent-pink); }
    .neo-card-green { background: var(--accent-green); }
    .neo-card-orange { background: var(--accent-orange); }
    .neo-card-purple { background: var(--accent-purple); }
    
    /* Metric styling */
    .metric-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #1A1A1A;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1A1A1A;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    .metric-delta-positive {
        color: #00AA00;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .metric-delta-negative {
        color: #CC0000;
        font-weight: 700;
        font-size: 1rem;
    }
    
    /* Table styling */
    .dataframe {
        font-family: 'JetBrains Mono', monospace !important;
        border: 3px solid #1A1A1A !important;
    }
    
    .dataframe th {
        background: var(--accent-yellow) !important;
        color: #1A1A1A !important;
        font-weight: 700 !important;
        border: 2px solid #1A1A1A !important;
    }
    
    .dataframe td {
        border: 2px solid #1A1A1A !important;
    }
    
    /* Streamlit elements override */
    .stSelectbox > div > div {
        border: 3px solid #1A1A1A !important;
        border-radius: 0 !important;
        box-shadow: var(--shadow);
    }
    
    .stButton > button {
        background: var(--accent-yellow) !important;
        color: #1A1A1A !important;
        border: 3px solid #1A1A1A !important;
        border-radius: 0 !important;
        box-shadow: var(--shadow);
        font-weight: 700 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        box-shadow: var(--shadow-hover);
        transform: translate(-2px, -2px);
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        padding: 0.75rem 1.5rem;
        background: #1A1A1A;
        color: #FFFFFF;
        display: inline-block;
        margin: 1.5rem 0 1rem 0;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Ticker tag */
    .ticker-tag {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        background: var(--accent-blue);
        border: 2px solid #1A1A1A;
        box-shadow: 2px 2px 0px #1A1A1A;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        margin: 0.2rem;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: var(--accent-pink);
        border: 4px solid #1A1A1A;
        box-shadow: var(--shadow);
    }
    
    .empty-state h2 {
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    
    .empty-state code {
        background: #1A1A1A;
        color: var(--accent-yellow);
        padding: 0.5rem 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


def load_predictions() -> pd.DataFrame:
    """Load predictions from local JSON file."""
    if not DATA_FILE.exists():
        return pd.DataFrame()
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        if "as_of_date" in df.columns:
            df["as_of_date"] = pd.to_datetime(df["as_of_date"]).dt.date
        return df
    except (json.JSONDecodeError, FileNotFoundError):
        return pd.DataFrame()


def create_weights_chart(weights_df: pd.DataFrame) -> go.Figure:
    """Create a neobrutalist pie chart for portfolio weights."""
    colors = ['#FFE566', '#7EB8FF', '#FFB8D4', '#B8FFB8', '#FFB366', '#C4B8FF',
              '#FF9999', '#99FFCC', '#FF99FF', '#CCFF99', '#99CCFF', '#FFCC99']
    
    fig = go.Figure(data=[go.Pie(
        labels=weights_df['ticker'],
        values=weights_df['portfolio_weight'],
        hole=0.4,
        marker=dict(
            colors=colors[:len(weights_df)],
            line=dict(color='#1A1A1A', width=3)
        ),
        textinfo='label+percent',
        textfont=dict(size=14, family='Space Grotesk', color='#1A1A1A'),
        hovertemplate='<b>%{label}</b><br>Weight: %{value:.1%}<extra></extra>'
    )])
    
    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=20, r=20),
        height=350,
        font=dict(family='Space Grotesk')
    )
    
    return fig


def create_price_chart(ticker_data: pd.DataFrame) -> go.Figure:
    """Create a neobrutalist line chart for price predictions."""
    fig = go.Figure()
    
    # Add a line for each ticker
    colors = ['#7EB8FF', '#FFB8D4', '#B8FFB8', '#FFB366', '#C4B8FF', '#FFE566']
    
    for i, (ticker, group) in enumerate(ticker_data.groupby('ticker')):
        group = group.sort_values('as_of_date')
        fig.add_trace(go.Scatter(
            x=group['as_of_date'],
            y=group['predicted_price'],
            name=ticker,
            mode='lines+markers',
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=10, line=dict(color='#1A1A1A', width=2))
        ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#FFFFFF',
        margin=dict(t=40, b=40, l=60, r=40),
        height=400,
        font=dict(family='Space Grotesk', color='#1A1A1A'),
        legend=dict(
            bgcolor='#FFE566',
            bordercolor='#1A1A1A',
            borderwidth=2,
            font=dict(size=12)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            linecolor='#1A1A1A',
            linewidth=3,
            title='Date',
            title_font=dict(size=14, family='Space Grotesk')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            linecolor='#1A1A1A',
            linewidth=3,
            title='Predicted Price ($)',
            title_font=dict(size=14, family='Space Grotesk')
        )
    )
    
    return fig


def main():
    # Title
    st.markdown('<div class="main-title">🚀 GOPRED</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_predictions()
    
    if df.empty:
        st.markdown("""
        <div class="empty-state">
            <h2>🚀 No predictions yet!</h2>
            <p style="font-size: 1.2rem; margin-bottom: 1.5rem;">Run the optimization script to generate predictions:</p>
            <code>python -m src.main</code>
            <p style="margin-top: 1.5rem; font-size: 1rem;">Then refresh this page to see results.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Get latest date data
    available_dates = sorted(df["as_of_date"].unique(), reverse=True)
    latest_date = available_dates[0]
    date_df = df[df["as_of_date"] == latest_date].copy().sort_values("portfolio_weight", ascending=False)
    
    # Date selector
    st.markdown('<div class="section-header">📅 PREDICTION DATE</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_date = st.selectbox(
            "Select date",
            options=available_dates,
            format_func=lambda d: d.strftime("%B %d, %Y"),
            label_visibility="collapsed"
        )
        date_df = df[df["as_of_date"] == selected_date].copy().sort_values("portfolio_weight", ascending=False)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Portfolio Weights Section
    st.markdown('<div class="section-header">🎯 OPTIMAL PORTFOLIO WEIGHTS</div>', unsafe_allow_html=True)
    
    col_chart, col_table = st.columns([1, 1])
    
    with col_chart:
        fig = create_weights_chart(date_df)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_table:
        # Create styled table data
        table_data = date_df[['ticker', 'predicted_price', 'predicted_return', 'portfolio_weight']].copy()
        table_data['predicted_price'] = table_data['predicted_price'].apply(lambda x: f"${x:,.2f}")
        table_data['predicted_return'] = table_data['predicted_return'].apply(lambda x: f"{x*100:+.2f}%")
        table_data['portfolio_weight'] = table_data['portfolio_weight'].apply(lambda x: f"{x*100:.1f}%")
        table_data.columns = ['TICKER', 'PREDICTED PRICE', 'EXPECTED RETURN', 'WEIGHT']
        
        st.dataframe(
            table_data,
            hide_index=True,
            use_container_width=True,
            height=350
        )
    
    # Stock Cards Section
    st.markdown('<div class="section-header">💹 STOCK PREDICTIONS</div>', unsafe_allow_html=True)
    
    # Display top stocks as cards
    card_colors = ['neo-card-blue', 'neo-card-pink', 'neo-card-green', 'neo-card-orange', 'neo-card-purple', 'neo-card-yellow']
    
    # Create rows of 4 cards
    rows = [date_df.iloc[i:i+4] for i in range(0, len(date_df), 4)]
    
    for row_data in rows:
        cols = st.columns(4)
        for idx, (_, stock) in enumerate(row_data.iterrows()):
            with cols[idx]:
                color = card_colors[idx % len(card_colors)]
                return_val = stock['predicted_return']
                delta_class = "metric-delta-positive" if return_val >= 0 else "metric-delta-negative"
                delta_symbol = "▲" if return_val >= 0 else "▼"
                
                st.markdown(f"""
                <div class="neo-card {color}">
                    <div class="metric-label">{stock['ticker']}</div>
                    <div class="metric-value">${stock['predicted_price']:,.2f}</div>
                    <div class="{delta_class}">{delta_symbol} {return_val*100:+.2f}%</div>
                    <div style="margin-top: 0.5rem; font-size: 0.85rem; font-weight: 600;">
                        Weight: {stock['portfolio_weight']*100:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Historical Chart Section (if multiple dates)
    if len(available_dates) > 1:
        st.markdown('<div class="section-header">📊 PRICE HISTORY</div>', unsafe_allow_html=True)
        
        # Get top 6 stocks by weight for the chart
        top_tickers = date_df.nlargest(6, 'portfolio_weight')['ticker'].tolist()
        chart_data = df[df['ticker'].isin(top_tickers)]
        
        fig = create_price_chart(chart_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 1rem; border-top: 3px solid #1A1A1A;">
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;">
            GoPred - A Prediction Model | Prophet + Markowitz | 
            <span style="background: #FFE566; padding: 0.2rem 0.5rem; border: 2px solid #1A1A1A;">NEOBRUTALISM</span>
        </span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
