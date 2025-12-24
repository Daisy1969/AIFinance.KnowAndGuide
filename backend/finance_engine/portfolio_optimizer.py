from pypfopt import EfficientFrontier, risk_models, expected_returns
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    def __init__(self):
        pass

    def optimize(self, prices: pd.DataFrame, risk_profile: str = "balanced", constraints: dict = None):
        """
        Calculates optimal weights using Mean-Variance Optimization.
        """
        if prices.empty:
            return {}

        # 1. Calculate expected returns and sample covariance
        mu = expected_returns.mean_historical_return(prices)
        S = risk_models.sample_cov(prices)

        # 2. Optimize for Efficient Frontier
        ef = EfficientFrontier(mu, S)

        # Apply basic constraints if any (e.g. max weight per asset)
        # ef.add_constraint(lambda w: w <= 0.30)
        
        try:
            if risk_profile == "high_growth":
                # Maximize Sharpe Ratio
                ef.max_sharpe()
            elif risk_profile == "conservative":
                # Minimize Volatility
                ef.min_volatility()
            else:
                # Balanced/Default: Max Sharpe
                ef.max_sharpe()
                
            weights = ef.clean_weights()
            performance = ef.portfolio_performance(verbose=False)
            
            return {
                "weights": weights,
                "performance": {
                    "expected_return": performance[0],
                    "volatility": performance[1],
                    "sharpe_ratio": performance[2]
                }
            }
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return {}
