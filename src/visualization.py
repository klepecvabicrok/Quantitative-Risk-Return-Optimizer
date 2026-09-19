import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def save_analysis_plots(close_prices: pd.DataFrame, returns: pd.DataFrame, output_path: str = "outputs/real_data_analysis.png"):
    """Generates and saves visual analytics without blocking execution."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Normalized Price Evolution
    norm_prices = close_prices / close_prices.iloc[0] * 100
    norm_prices.plot(ax=axes[0], linewidth=1.5)
    axes[0].set_title('Normalized Asset Prices (Base=100)', fontweight='bold')
    axes[0].set_ylabel('Price Index')
    axes[0].grid(True, alpha=0.3)

    # Correlation Heatmap
    sns.heatmap(returns.corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=axes[1])
    axes[1].set_title('Correlation Matrix', fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()