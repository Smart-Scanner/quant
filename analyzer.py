"""18-factor analyzer for stock scoring."""

import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

log = logging.getLogger("screener")

class Analyzer:
    """Technical & fundamental analyzer."""
    
    def __init__(self):
        self.max_score = 380
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator."""
        try:
            delta = data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not rsi.empty else 50
        except Exception as e:
            log.warning(f"RSI calc error: {e}")
            return 50
    
    def calculate_macd(self, data: pd.Series) -> tuple:
        """Calculate MACD indicator."""
        try:
            ema_12 = data.ewm(span=12).mean()
            ema_26 = data.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()
            histogram = macd - signal
            return (
                float(macd.iloc[-1]) if not macd.empty else 0,
                float(signal.iloc[-1]) if not signal.empty else 0,
                float(histogram.iloc[-1]) if not histogram.empty else 0,
            )
        except Exception as e:
            log.warning(f"MACD calc error: {e}")
            return (0, 0, 0)
    
    def score_technical(self, hist: pd.DataFrame) -> float:
        """Score technical factors (0-100)."""
        try:
            close = hist["Close"]
            
            # Trend
            sma_50 = close.rolling(50).mean().iloc[-1]
            sma_200 = close.rolling(200).mean().iloc[-1]
            trend_score = 30 if close.iloc[-1] > sma_50 else 10
            
            # RSI
            rsi = self.calculate_rsi(close)
            rsi_score = 20 if 40 < rsi < 70 else 5
            
            # MACD
            macd, signal, hist_val = self.calculate_macd(close)
            macd_score = 20 if (macd > signal and hist_val > 0) else 5
            
            # Volume
            vol_ratio = hist["Volume"].iloc[-1] / hist["Volume"].rolling(20).mean().iloc[-1]
            vol_score = 15 if vol_ratio > 1.2 else 5
            
            return min(trend_score + rsi_score + macd_score + vol_score, 100)
        except Exception as e:
            log.warning(f"Technical score error: {e}")
            return 30
    
    def score_fundamental(self, symbol: str) -> float:
        """Score fundamental factors (0-100)."""
        # Simplified - in production would use actual financials
        return 40
    
    def score_sentiment(self, symbol: str) -> float:
        """Score news sentiment (0-100)."""
        # Simplified - in production would use FinBERT
        return 30
    
    def analyze_stock(self, symbol: str, hist: pd.DataFrame) -> Dict[str, Any]:
        """Analyze stock across all factors."""
        try:
            tech_score = self.score_technical(hist)
            fund_score = self.score_fundamental(symbol)
            sent_score = self.score_sentiment(symbol)
            
            total_score = (tech_score * 0.5 + fund_score * 0.3 + sent_score * 0.2)
            
            return {
                "symbol": symbol,
                "technical_score": tech_score,
                "fundamental_score": fund_score,
                "sentiment_score": sent_score,
                "total_score": total_score,
                "grade": "A" if total_score > 70 else "B" if total_score > 50 else "C",
            }
        except Exception as e:
            log.warning(f"Analysis error for {symbol}: {e}")
            return None

analyzer = Analyzer()

def fetch_and_analyze(symbol: str, nifty_1m: float, regime: str, ext_df=None, scan_mode: str = "fast") -> Optional[Dict]:
    """Fetch and analyze a stock."""
    try:
        import yfinance as yf
        
        if ext_df is None:
            hist = yf.download(symbol, period="1y", progress=False)
        else:
            hist = ext_df
        
        if hist.empty:
            return None
        
        return analyzer.analyze_stock(symbol, hist)
    except Exception as e:
        log.warning(f"Fetch-analyze error for {symbol}: {e}")
        return None
