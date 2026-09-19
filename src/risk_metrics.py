import subprocess
import numpy as np
import pandas as pd


def value_at_risk(returns: np.ndarray, alpha: float = 0.95) -> float:
    """Calculates Historical Value at Risk (VaR)."""
    if len(returns) == 0:
        return 0.0
    return float(np.percentile(returns, (1.0 - alpha) * 100))

def conditional_var(returns: np.ndarray, alpha: float = 0.95) -> float:
    """Calculates Conditional Value at Risk (CVaR / Expected Shortfall)."""
    if len(returns) == 0:
        return 0.0
    var_val = value_at_risk(returns, alpha)
    tail = returns[returns <= var_val]
    return float(tail.mean()) if len(tail) > 0 else float(var_val)

def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02, trading_days: int = 252) -> float:
    """Calculates exact annualized Sharpe Ratio."""
    if len(returns) == 0:
        return 0.0
    daily_rf = risk_free_rate / trading_days
    excess_returns = returns - daily_rf
    std_dev = excess_returns.std()
    if std_dev == 0 or np.isnan(std_dev):
        return 0.0
    return float((excess_returns.mean() / std_dev) * np.sqrt(trading_days))

def max_drawdown(price_series: pd.Series) -> float:
    """Calculates Maximum Drawdown of a price series."""
    peak = price_series.cummax()
    drawdown = (price_series - peak) / peak
    return float(drawdown.min())

def verify_with_r(ticker: str = "SPY") -> dict:
    """
    Compares the results of the CVaR and Sharpe ratio calculations between Python and R.
    """
    csv_file = f"data/{ticker}.csv"
    
    result = subprocess.run(
        ["Rscript", "scripts/verify_metrics.R", csv_file],
        capture_output=True,
        text=True,
        check=True
    )
    
    r_results = {}
    for line in result.stdout.strip().split("\n"):
        if ":" in line:
            k, v = line.split(":")
            r_results[k] = float(v)

    
    df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
    daily_returns = df["Close"].pct_change().dropna()

    py_cvar = conditional_var(daily_returns.values, alpha=0.95)
    py_sharpe = sharpe_ratio(daily_returns, risk_free_rate=0.02)

    return {
        "Metric": ["CVaR (Historical 95%)", "Sharpe Ratio (Annual)"],
        "Python": [py_cvar, py_sharpe],
        "R (PerformanceAnalytics)": [r_results.get("R_CVAR95"), r_results.get("R_SHARPE")],
        "Difference": [abs(py_cvar - r_results.get("R_CVAR95", 0)), abs(py_sharpe - r_results.get("R_SHARPE", 0))]
    }