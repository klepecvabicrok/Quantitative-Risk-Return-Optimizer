from pathlib import Path
import pandas as pd
import yfinance as yf

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)

def download_prices(ticker: str, start: str = "2020-01-01", end: str = "2024-01-01") -> pd.DataFrame:
    """
    Downloads and saves all price data for a given ticker with automatic column alignment.
    """
    clean_ticker = ticker.replace('/', '_')
    file_path = DATA_DIR / f"{clean_ticker}.csv"

    
    if file_path.exists():
        try:
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            if not df.empty and len(df.columns) >= 1 and pd.api.types.is_numeric_dtype(df.iloc[:, 0]):
                return df
        except Exception:
            pass  

    
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError(f"Za ticker {ticker} ni bilo mogoče prenesti podatkov.")

    # Flatten the MultiIndex columns  (‘Close’, ‘SPY’) → ‘Close’
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    
    if "Adj Close" not in df.columns and "Close" in df.columns:
        df["Adj Close"] = df["Close"]

    df.to_csv(file_path)
    return df