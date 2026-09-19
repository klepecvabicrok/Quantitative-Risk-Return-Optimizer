import numpy as np
import pandas as pd
from scipy.optimize import minimize
from src.risk_metrics import conditional_var

def optimize_max_sharpe(returns_df: pd.DataFrame, risk_free_rate: float = 0.02) -> np.ndarray:
    """Finds maximum Sharpe ratio weights using SciPy SLSQP optimizer."""
    num_assets = returns_df.shape[1]
    mean_returns = returns_df.mean().values * 252
    cov_matrix = returns_df.cov().values * 252

    def negative_sharpe(weights):
        port_return = weights @ mean_returns
        port_vol = np.sqrt(weights.T @ cov_matrix @ weights)
        if port_vol == 0:
            return 0.0
        return -(port_return - risk_free_rate) / port_vol

    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
    bounds = tuple((0.05, 0.60) for _ in range(num_assets))
    init_weights = np.ones(num_assets) / num_assets

    res = minimize(negative_sharpe, init_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    if not res.success:
        raise RuntimeError(f"Sharpe optimization failed: {res.message}")
    return res.x

def optimize_min_cvar(returns_df: pd.DataFrame, alpha: float = 0.95) -> np.ndarray:
    """Finds minimal CVaR portfolio weights."""
    num_assets = returns_df.shape[1]
    returns_matrix = returns_df.values

    def objective(weights):
        port_returns = returns_matrix @ weights
        # We minimize negative CVaR to minimize loss severity
        return -conditional_var(port_returns, alpha)

    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
    bounds = tuple((0.05, 0.60) for _ in range(num_assets))
    init_weights = np.ones(num_assets) / num_assets

    res = minimize(objective, init_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    if not res.success:
        raise RuntimeError(f"CVaR optimization failed: {res.message}")
    return res.x