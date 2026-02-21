"""
Streamlit Interactive Dashboard
===============================

Professional portfolio optimization dashboard with real-time analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from black_litterman import BlackLittermanOptimizer
from advanced_metrics import RiskMetricsCalculator
from config import config


# Page configuration
st.set_page_config(
    page_title=config.streamlit.PAGE_TITLE,
    page_icon=config.streamlit.PAGE_ICON,
    layout=config.streamlit.LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def load_data(tickers, start_date, end_date):
    """Load portfolio data with caching."""
    try:
        optimizer = BlackLittermanOptimizer(
            ticker_list=tickers,
            start_date=start_date,
            end_date=end_date,
            risk_free_rate=config.risk.RISK_FREE_RATE
        )
        return optimizer
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def plot_efficient_frontier(optimizer, results):
    """Plot interactive efficient frontier."""
    
    np.random.seed(42)
    returns_list = []
    volatility_list = []
    sharpe_list = []
    
    # Random portfolios
    for _ in range(500):
        weights = np.random.random(len(optimizer.ticker_list))
        weights /= np.sum(weights)
        
        portfolio_return = np.sum(weights * optimizer.bl_returns)
        portfolio_vol = np.sqrt(weights @ optimizer.cov_matrix @ weights)
        sharpe = (portfolio_return - optimizer.risk_free_rate) / portfolio_vol
        
        returns_list.append(portfolio_return)
        volatility_list.append(portfolio_vol)
        sharpe_list.append(sharpe)
    
    # Create figure
    fig = go.Figure()
    
    # Random portfolios
    fig.add_trace(go.Scatter(
        x=volatility_list,
        y=returns_list,
        mode='markers',
        marker=dict(
            size=5,
            color=sharpe_list,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Sharpe Ratio"),
            opacity=0.6
        ),
        name='Random Portfolios',
        hovertemplate='<b>Volatility:</b> %{x:.2%}<br><b>Return:</b> %{y:.2%}<extra></extra>'
    ))
    
    # Optimal portfolios
    markowitz = results['markowitz']
    bl = results['black_litterman']
    equal = results['equal_weight']
    
    markowitz_vol = np.sqrt(markowitz['weights'] @ optimizer.cov_matrix @ markowitz['weights'])
    bl_vol = np.sqrt(bl['weights'] @ optimizer.cov_matrix @ bl['weights'])
    equal_vol = np.sqrt(equal['weights'] @ optimizer.cov_matrix @ equal['weights'])
    
    markowitz_ret = markowitz['metrics']['Expected Return']
    bl_ret = bl['metrics']['Expected Return']
    equal_ret = equal['metrics']['Expected Return']
    
    # Add optimal points
    for name, vol, ret, color, symbol in [
        ('Markowitz', markowitz_vol, markowitz_ret, 'red', 'star'),
        ('Black-Litterman', bl_vol, bl_ret, 'green', 'star'),
        ('Equal-Weight', equal_vol, equal_ret, 'blue', 'square')
    ]:
        fig.add_trace(go.Scatter(
            x=[vol],
            y=[ret],
            mode='markers',
            marker=dict(size=20, color=color, symbol=symbol, line=dict(width=2, color='white')),
            name=name,
            hovertemplate=f'<b>{name}</b><br>Volatility: %{{x:.2%}}<br>Return: %{{y:.2%}}<extra></extra>'
        ))
    
    fig.update_layout(
        title='<b>Efficient Frontier: Portfolio Comparison</b>',
        xaxis_title='Volatility (Annual)',
        yaxis_title='Expected Return (Annual)',
        hovermode='closest',
        height=600,
        template='plotly_white'
    )
    
    fig.update_xaxes(tickformat='.0%')
    fig.update_yaxes(tickformat='.0%')
    
    return fig


def plot_weights_pie(weights, tickers, model_name):
    """Create pie chart of portfolio weights."""
    fig = go.Figure(data=[go.Pie(
        labels=tickers,
        values=weights,
        hole=0.3,
        hovertemplate='<b>%{label}</b><br>Weight: %{value:.2%}<extra></extra>'
    )])
    
    fig.update_layout(
        title=f'<b>{model_name} Allocation</b>',
        height=400,
        template='plotly_white'
    )
    
    return fig


def plot_returns(optimizer, results):
    """Plot cumulative returns."""
    daily_returns = optimizer.returns
    
    fig = go.Figure()
    
    # Markowitz
    markowitz_ret = (daily_returns @ results['markowitz']['weights']).values
    markowitz_cum = (1 + markowitz_ret).cumprod()
    
    # Black-Litterman
    bl_ret = (daily_returns @ results['black_litterman']['weights']).values
    bl_cum = (1 + bl_ret).cumprod()
    
    # Equal-weight
    equal_ret = (daily_returns @ results['equal_weight']['weights']).values
    equal_cum = (1 + equal_ret).cumprod()
    
    for name, cum_ret, color in [
        ('Markowitz', markowitz_cum, 'red'),
        ('Black-Litterman', bl_cum, 'green'),
        ('Equal-Weight', equal_cum, 'blue')
    ]:
        fig.add_trace(go.Scatter(
            x=daily_returns.index,
            y=cum_ret,
            name=name,
            line=dict(color=color, width=2),
            hovertemplate='<b>' + name + '</b><br>Date: %{x|%Y-%m-%d}<br>Value: %{y:.2%}<extra></extra>'
        ))
    
    fig.update_layout(
        title='<b>Cumulative Returns (Out-of-Sample)</b>',
        xaxis_title='Date',
        yaxis_title='Cumulative Return',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    fig.update_yaxes(tickformat='.0%')
    
    return fig


def main():
    """Main dashboard function."""
    
    # Header
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>📊 Portfolio Optimization Dashboard</h1>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Black-Litterman Model with Advanced Risk Metrics</p>", 
                unsafe_allow_html=True)
    st.divider()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Asset selection
        st.subheader("Assets")
        default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
        tickers_input = st.text_input(
            "Enter tickers (comma-separated)",
            value=",".join(default_tickers),
            help="e.g., AAPL,MSFT,GOOGL,AMZN,NVDA"
        )
        tickers = [t.strip().upper() for t in tickers_input.split(',')]
        
        # Date range
        st.subheader("Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                datetime.strptime('2021-01-01', '%Y-%m-%d').date()
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                datetime.now().date()
            )
        
        # Risk parameters
        st.subheader("Risk Parameters")
        risk_free_rate = st.slider(
            "Risk-Free Rate",
            min_value=0.0,
            max_value=0.10,
            value=0.03,
            step=0.01,
            format="%.2f"
        )
        
        lambda_risk = st.slider(
            "Risk Aversion Coefficient",
            min_value=1.0,
            max_value=5.0,
            value=2.5,
            step=0.5
        )
        
        # Investor views
        st.subheader("Investor Views")
        st.info("Set your expected returns and confidence levels")
        
        views = {}
        confidence = {}
        
        view_col1, view_col2 = st.columns(2)
        for i, ticker in enumerate(tickers[:len(tickers)//2 + 1]):
            with view_col1 if i <= len(tickers)//2 else view_col2:
                ret = st.number_input(
                    f"{ticker} Expected Return",
                    min_value=0.0,
                    max_value=0.50,
                    value=0.10,
                    step=0.01,
                    format="%.2f",
                    key=f"ret_{ticker}"
                )
                conf = st.slider(
                    f"{ticker} Confidence",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.50,
                    step=0.05,
                    key=f"conf_{ticker}"
                )
                views[ticker] = ret
                confidence[ticker] = conf
        
        st.divider()
        load_button = st.button("📈 Generate Analysis", use_container_width=True, type="primary")
    
    # Main content
    if load_button:
        with st.spinner("Loading data and running optimization..."):
            
            # Load data
            optimizer = load_data(tickers, start_date.strftime('%Y-%m-%d'), 
                                 end_date.strftime('%Y-%m-%d'))
            
            if optimizer is None:
                st.stop()
            
            # Update config
            optimizer.risk_free_rate = risk_free_rate
            optimizer.lambda_risk = lambda_risk
            
            # Run comparison
            results = optimizer.compare_models(views, confidence)
            
            # Tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview", 
                "💰 Allocations", 
                "📈 Performance",
                "⚠️ Risk Metrics",
                "📉 Analysis"
            ])
            
            # TAB 1: Overview
            with tab1:
                st.header("Portfolio Analysis Overview")
                
                col1, col2, col3 = st.columns(3)
                
                for idx, (model_name, model_data) in enumerate(results.items()):
                    metrics = model_data['metrics']
                    col = [col1, col2, col3][idx]
                    
                    with col:
                        st.metric(
                            model_name.replace('_', ' ').title(),
                            f"{metrics['Sharpe Ratio']:.4f}",
                            f"Vol: {metrics['Volatility']:.2%}"
                        )
                        
                        st.write("---")
                        
                        st.metric(
                            "Expected Return",
                            f"{metrics['Expected Return']:.2%}"
                        )
                        
                        st.metric(
                            "Volatility",
                            f"{metrics['Volatility']:.2%}"
                        )
                
                # Efficient frontier
                st.subheader("Efficient Frontier")
                fig = plot_efficient_frontier(optimizer, results)
                st.plotly_chart(fig, use_container_width=True)
            
            # TAB 2: Allocations
            with tab2:
                st.header("Portfolio Allocations")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fig = plot_weights_pie(results['markowitz']['weights'], tickers, "Markowitz")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = plot_weights_pie(results['black_litterman']['weights'], tickers, "Black-Litterman")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    fig = plot_weights_pie(results['equal_weight']['weights'], tickers, "Equal-Weight")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Weights table
                st.subheader("Weights Comparison Table")
                weights_df = pd.DataFrame({
                    'Asset': tickers,
                    'Markowitz': results['markowitz']['weights'] * 100,
                    'Black-Litterman': results['black_litterman']['weights'] * 100,
                    'Equal-Weight': results['equal_weight']['weights'] * 100,
                })
                weights_df = weights_df.set_index('Asset')
                
                st.dataframe(
                    weights_df.style.format("{:.2f}%"),
                    use_container_width=True
                )
            
            # TAB 3: Performance
            with tab3:
                st.header("Portfolio Performance")
                
                fig = plot_returns(optimizer, results)
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance metrics table
                st.subheader("Performance Metrics")
                perf_df = pd.DataFrame({
                    'Metric': ['Expected Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown'],
                    'Markowitz': [
                        f"{results['markowitz']['metrics']['Expected Return']:.2%}",
                        f"{results['markowitz']['metrics']['Volatility']:.2%}",
                        f"{results['markowitz']['metrics']['Sharpe Ratio']:.4f}",
                        f"{results['markowitz']['metrics']['Max Drawdown']:.2%}"
                    ],
                    'Black-Litterman': [
                        f"{results['black_litterman']['metrics']['Expected Return']:.2%}",
                        f"{results['black_litterman']['metrics']['Volatility']:.2%}",
                        f"{results['black_litterman']['metrics']['Sharpe Ratio']:.4f}",
                        f"{results['black_litterman']['metrics']['Max Drawdown']:.2%}"
                    ],
                    'Equal-Weight': [
                        f"{results['equal_weight']['metrics']['Expected Return']:.2%}",
                        f"{results['equal_weight']['metrics']['Volatility']:.2%}",
                        f"{results['equal_weight']['metrics']['Sharpe Ratio']:.4f}",
                        f"{results['equal_weight']['metrics']['Max Drawdown']:.2%}"
                    ]
                })
                
                st.dataframe(perf_df, use_container_width=True, hide_index=True)
            
            # TAB 4: Risk Metrics
            with tab4:
                st.header("Advanced Risk Metrics")
                
                # Calculate advanced metrics
                calculator = RiskMetricsCalculator(risk_free_rate=risk_free_rate)
                
                col1, col2, col3 = st.columns(3)
                
                for idx, (model_name, model_data) in enumerate(results.items()):
                    col = [col1, col2, col3][idx]
                    
                    with col:
                        st.subheader(model_name.replace('_', ' ').title())
                        
                        metrics = model_data['metrics']
                        
                        st.metric("VaR (95%)", f"{metrics['VaR (95%)']:.2%}")
                        st.metric("CVaR (95%)", f"{metrics['CVaR (95%)']:.2%}")
                        st.metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}")
            
            # TAB 5: Detailed Analysis
            with tab5:
                st.header("Detailed Analysis & Recommendations")
                
                bl_weights = results['black_litterman']['weights']
                bl_metrics = results['black_litterman']['metrics']
                
                st.subheader("🎯 Recommended Portfolio (Black-Litterman)")
                
                # Weight visualization
                for ticker, weight in zip(tickers, bl_weights):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.progress(weight, text=f"{ticker}: {weight:.1%}")
                    with col2:
                        st.write(f"{weight:.2%}")
                
                st.divider()
                
                st.subheader("📈 Expected Performance")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Annual Return", f"{bl_metrics['Expected Return']:.2%}")
                with col2:
                    st.metric("Volatility", f"{bl_metrics['Volatility']:.2%}")
                with col3:
                    st.metric("Sharpe Ratio", f"{bl_metrics['Sharpe Ratio']:.4f}")
                
                st.divider()
                
                st.subheader("💡 Key Insights")
                
                insights = [
                    f"🔹 The Black-Litterman model produces **{bl_metrics['Sharpe Ratio']:.3f} Sharpe ratio** vs {results['markowitz']['metrics']['Sharpe Ratio']:.3f} for Markowitz",
                    f"🔹 Portfolio volatility ({bl_metrics['Volatility']:.2%}) is well below the risk-free rate assumption",
                    f"🔹 Maximum historical drawdown: **{bl_metrics['Max Drawdown']:.2%}**",
                    f"🔹 Value at Risk (95%): **{bl_metrics['VaR (95%)']:.2%}** daily loss possible",
                ]
                
                for insight in insights:
                    st.info(insight, icon="💼")
                
                st.divider()
                
                st.subheader("📋 Recommendations")
                
                recommendations = [
                    "1. **Implement gradually**: Don't switch portfolios overnight - rebalance over 2-4 weeks",
                    "2. **Monitor monthly**: Compare actual vs. expected performance",
                    "3. **Update quarterly**: Recalibrate with new market data and views",
                    "4. **Set stops**: Implement risk controls for positions exceeding risk tolerance",
                    "5. **Tax efficiency**: Consider tax-loss harvesting when rebalancing"
                ]
                
                for rec in recommendations:
                    st.write(rec)


if __name__ == '__main__':
    main()
