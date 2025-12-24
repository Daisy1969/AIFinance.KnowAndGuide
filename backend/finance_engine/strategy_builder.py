class StrategyBuilder:
    def __init__(self):
        pass

    def map_profile_to_risk(self, age: int, horizon: str, goals: list = None) -> str:
        """
        Maps user demographics to a risk profile string.
        """
        # Normalize inputs
        horizon = horizon.lower()
        
        # Heuristic Logic
        if horizon in ['short', '<1yr']:
            return "conservative"
        
        if age < 40 and horizon in ['long', '5yr+']:
            return "high_growth"
            
        if age > 60:
            return "conservative"
            
        return "balanced"

    def filter_assets(self, universe: list, goal_dividends: bool, market_data_engine) -> list:
        """
        Filters the asset universe based on goals (e.g., only high yield).
        """
        if not goal_dividends:
            return universe
            
        filtered = []
        for ticker in universe:
            yield_val = market_data_engine.get_dividend_yield(ticker)
            if yield_val > 0.04: # 4% threshold
                filtered.append(ticker)
        
        if not filtered:
            return universe # Fallback to full universe if filter allows nothing
            
        return filtered
