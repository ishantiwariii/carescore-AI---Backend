from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Import Routes
from routes.auth_routes import auth_bp
from routes.report_routes import report_bp
from routes.analysis_routes import analysis_bp
from routes.history_routes import history_bp
from routes.download_routes import download_bp

load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for frontend

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(report_bp, url_prefix='/api/report')
app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
app.register_blueprint(history_bp, url_prefix='/api/history')
app.register_blueprint(download_bp, url_prefix='/api/download')

@app.route('/')
def home():
    return {"status": "Carescore AI Backend is Running 🟢", "db": "Supabase"}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
