from flask import Flask, jsonify, request
from flask_cors import CORS
from finance_engine.market_data import MarketData
from finance_engine.portfolio_optimizer import PortfolioOptimizer
from finance_engine.strategy_builder import StrategyBuilder
import logging

app = Flask(__name__)
CORS(app) # Enable CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize engines
market_engine = MarketData()
optimizer_engine = PortfolioOptimizer()
strategy_engine = StrategyBuilder()

@app.route('/')
def home():
    return jsonify({"message": "KnowAndGuide Financial Engine Active", "status": "running"})

@app.route('/api/recommend', methods=['POST'])
def recommend_portfolio():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    age = data.get('age', 30)
    horizon = data.get('horizon', 'medium')
    goal_dividends = data.get('goal_dividends', False)
    # Default universe suited for ASX/Global mix
    # VAS: Aus Top 300, VGS: World ex-Aus, IVV: S&P500, BHP, CSL
    default_universe = ['VAS', 'VGS', 'IVV', 'BHP', 'CSL', 'CBA', 'NDQ']
    universe = data.get('assets', default_universe)
    
    try:
        # 1. Determine Risk Profile
        risk_profile = strategy_engine.map_profile_to_risk(age, horizon)
        
        # 2. Filter Universe
        filtered_assets = strategy_engine.filter_assets(universe, goal_dividends, market_engine)
        
        if len(filtered_assets) < 2:
             return jsonify({
                 "warning": "Not enough assets for optimization after filtering. Using default universe.",
                 "risk_profile": risk_profile,
                 "original_filtered": filtered_assets
             }), 200 # Fallback or just return warning

        # 3. Fetch Data
        prices = market_engine.get_prices(filtered_assets)
        if prices.empty:
             return jsonify({"error": "Failed to fetch price data"}), 500

        # 4. Optimize
        result = optimizer_engine.optimize(prices, risk_profile=risk_profile)
        
        return jsonify({
            "risk_profile": risk_profile,
            "universe": filtered_assets,
            "optimization": result
        })
    except Exception as e:
        logger.error(f"Error in recommend endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-portfolio', methods=['POST'])
def upload_portfolio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        import csv
        import io
        
        try:
            # Decode file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            rows = list(csv_input)
            
            # Logic to find header row (Superhero exports have metadata first)
            header_row_idx = 0
            for i, row in enumerate(rows):
                if row and "Security" in row and "Units" in row:
                    header_row_idx = i
                    break
            
            header = rows[header_row_idx]
            data_rows = rows[header_row_idx+1:]
            
            portfolio_data = []
            for row in data_rows:
                if len(row) < 3: continue 
                # Basic mapping (Security, Units)
                # Ensure we handle columns correctly based on header
                try:
                    sec_idx = header.index("Security")
                    units_idx = header.index("Units")
                    
                    holding = {
                        "ticker": row[sec_idx],
                        "units": row[units_idx]
                    }
                    portfolio_data.append(holding)
                except Exception as e:
                    continue
                    
            return jsonify({
                "message": "Portfolio processed successfully", 
                "holdings_count": len(portfolio_data),
                "holdings": portfolio_data
            })
            
        except Exception as e:
            return jsonify({"error": f"Failed to parse CSV: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
