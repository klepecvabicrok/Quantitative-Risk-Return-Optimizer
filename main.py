from pathlib import Path
import pandas as pd
import numpy as np

from src.data_loader import download_prices
from src.risk_metrics import sharpe_ratio, conditional_var
from src.optimization import optimize_max_sharpe, optimize_min_cvar
from src.visualization import save_analysis_plots

def main():
    print("=== QRRE QUANTITATIVE PIPELINE START ===")
    
    tickers = {
        'SPY': 'S&P 500 ETF',
        'VGK': 'Europe ETF',
        'BND': 'Bond ETF',
        'QQQ': 'Nasdaq ETF'
    }

    raw_series = {}
    for ticker in tickers.keys():
        df = download_prices(ticker, start="2020-01-01", end="2024-01-01")
        
        # Select the “Close” or “Adj Close” column
        if 'Close' in df.columns:
            s = df['Close']
        elif 'Adj Close' in df.columns:
            s = df['Adj Close']
        else:
            s = df.iloc[:, 0]

        # If a DataFrame is returned instead of a Series, we take the first column
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]
            
        s = pd.to_numeric(s, errors='coerce')
        s.name = ticker
        raw_series[ticker] = s

    # combine all the series into a single DataFrame and calculate the daily returns
    close_df = pd.DataFrame(raw_series).dropna()
    returns = close_df.pct_change().dropna()

    # Portfolio Optimization
    w_equal = np.ones(len(tickers)) / len(tickers)
    w_sharpe = optimize_max_sharpe(returns, risk_free_rate=0.02)
    w_cvar = optimize_min_cvar(returns, alpha=0.95)

    strategies = {
        'Equal Weight': w_equal,
        'Max Sharpe': w_sharpe,
        'Min CVaR': w_cvar
    }

    
    results = []
    for name, weights in strategies.items():
        port_daily = returns.values @ weights
        ann_return = port_daily.mean() * 252
        ann_vol = port_daily.std() * np.sqrt(252)
        sharpe = sharpe_ratio(pd.Series(port_daily), risk_free_rate=0.02)
        cvar_95 = conditional_var(port_daily, 0.95) * np.sqrt(252)

        results.append({
            'Strategy': name,
            'Expected Return': f"{ann_return*100:.2f}%",
            'Annual Volatility': f"{ann_vol*100:.2f}%",
            'Sharpe Ratio': f"{sharpe:.3f}",
            'CVaR 95% (Annual)': f"{cvar_95*100:.2f}%",
            'Allocation': " | ".join([f"{t}: {w:.1%}" for t, w in zip(tickers.keys(), weights)])
        })

    summary_df = pd.DataFrame(results)
    summary_df.to_csv("data/portfolio_strategies_formatted.csv", index=False)
    
    save_analysis_plots(close_df, returns)
    
    print("\nPROCESSED RESULTS:")
    print(summary_df.to_string(index=False))
    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()