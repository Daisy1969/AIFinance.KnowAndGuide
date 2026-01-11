from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from finance_engine.market_data import MarketData
from finance_engine.portfolio_optimizer import PortfolioOptimizer
from finance_engine.strategy_builder import StrategyBuilder
from superhero_secure import SuperheroSecureConnector
import logging

app = Flask(__name__)
CORS(app) # Enable CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize engines
market_engine = MarketData()
optimizer_engine = PortfolioOptimizer()
strategy_engine = StrategyBuilder()
superhero_connector = SuperheroSecureConnector()

logger.info("Application Startup Complete. Version: Debug-Patch-2")

@app.route('/')
def home():
    return jsonify({"message": "KnowAndGuide Financial Engine Active", "status": "running", "version": "1.2.4 - WAKE UP RENDER"})

# ... (Existing recommend endpoint) ...

@app.route('/api/connect-superhero', methods=['POST'])
def connect_superhero():
    try:
        # Check if already running
        if superhero_connector.driver:
            return jsonify({"message": "Session already active", "status": "active"})
        
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
        
        success, msg = superhero_connector.start_login_session(username, password)
        if success:
            return jsonify({"message": msg, "status": "waiting_for_login"})
        else:
            return jsonify({"error": msg}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/superhero-status', methods=['GET'])
def superhero_status():
    try:
        is_logged_in, msg = superhero_connector.check_login_status()
        
        if is_logged_in:
            # If logged in, we can try to scrape immediately or wait for separate call
            # For now, let's return status so Frontend can show "Success! Fetching data..."
            return jsonify({"logged_in": True, "message": msg})
        else:
            return jsonify({"logged_in": False, "message": msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/superhero-holdings', methods=['GET'])
def superhero_holdings():
    try:
        data = superhero_connector.get_portfolio_holdings()
        if "error" in data:
            return jsonify(data), 400
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        user_profile = data # Contains age, horizon, currency, etc.
        
        # Check if we have connected holdings
        holdings = []
        # Check if superhero_connector has an active session and is logged in
        is_logged_in, _ = superhero_connector.check_login_status()
        if is_logged_in:
            portfolio_data = superhero_connector.get_portfolio_holdings()
            if 'holdings' in portfolio_data:
                holdings = portfolio_data['holdings']
        
        # Mock AI Logic for Buy/Sell (Placeholder for real engine)
        # In a real app, this would use the 'finance_engine' package
        strategy = {
            "allocation": {
                "Growth (VAS/VGS)": 60,
                "Defensive (Bonds)": 30,
                "Speculative": 10
            },
            "currency": user_profile.get('currency', 'AUD'),
            "recommendations": []
        }
        
        # Simple Logic: If holding cash, buy. If holding too much speculative, sell.
        if holdings:
            strategy['context'] = "Based on your existing portfolio..."
            strategy['recommendations'].append({
                "action": "HOLD",
                "ticker": "VAS",
                "reason": "Core holding, keep compounding."
            })
            strategy['recommendations'].append({
                "action": "BUY",
                "ticker": "IVV",
                "reason": f"Increase exposure to US markets (in {user_profile.get('currency', 'AUD')})."
            })
        else:
            strategy['context'] = "Starting fresh..."
            strategy['recommendations'].append({
                "action": "BUY",
                "ticker": "VGS",
                "reason": "Global diversification."
            })

        return jsonify(strategy)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommend-portfolio-optimization', methods=['POST']) # Renamed to avoid conflict
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
            
            # Identify columns
            try:
                sec_idx = header.index("Security")
                units_idx = header.index("Units")
            except ValueError:
                 return jsonify({"error": "CSV must contain 'Security' and 'Units' columns"}), 400
            
            portfolio_data = []
            for row in data_rows:
                if len(row) < 3: continue 
                try:
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

@app.route('/api/debug-selenium', methods=['GET'])
def debug_selenium():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        import shutil

        # Check paths
        chromium_path = shutil.which("chromium") or "/usr/bin/chromium"
        driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver" or shutil.which("chromium-driver")
        
        path_info = f"Chromium: {chromium_path}, Driver: {driver_path}"

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = chromium_path
        
        service = Service(driver_path) if driver_path else None
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        
        return jsonify({"status": "success", "message": "Browser launched successfully", "paths": path_info}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "paths": path_info if 'path_info' in locals() else "Unknown"}), 500

@app.route('/api/debug-screenshot', methods=['GET'])
def debug_screenshot():
    try:
        if not superhero_connector.driver:
            return jsonify({"error": "No active driver"}), 404
        
        path = "/tmp/screenshot.png"
        superhero_connector.driver.save_screenshot(path)
        return send_file(path, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
