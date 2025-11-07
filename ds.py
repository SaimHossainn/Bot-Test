import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json

app = Flask(__name__, template_folder='.', static_folder='.')

# Load configuration
def load_config():
    config = {}
    try:
        # Try to load from .env file
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value
        else:
            # Default configuration
            config = {
                "VERIFICATION_ENABLED": "true",
                "VERIFICATION_TYPE": "one_click",
                "VERIFICATION_TITLE": "Verification Required",
                "VERIFICATION_DESCRIPTION": "Please verify yourself to access the server",
                "VERIFICATION_SEND_METHOD": "dm"
            }
    except Exception as e:
        print(f"Error loading config: {e}")
        # Default configuration
        config = {
            "VERIFICATION_ENABLED": "true",
            "VERIFICATION_TYPE": "one_click",
            "VERIFICATION_TITLE": "Verification Required",
            "VERIFICATION_DESCRIPTION": "Please verify yourself to access the server",
            "VERIFICATION_SEND_METHOD": "dm"
        }
    return config

# Save configuration
def save_config(config):
    try:
        with open('.env', 'w') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Global config variable
config = load_config()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    global config
    try:
        new_config = request.get_json()
        config.update(new_config)
        if save_config(config):
            return jsonify({"status": "success", "message": "Configuration updated successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to save configuration"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    global config
    config = {
        "VERIFICATION_ENABLED": "true",
        "VERIFICATION_TYPE": "one_click",
        "VERIFICATION_TITLE": "Verification Required",
        "VERIFICATION_DESCRIPTION": "Please verify yourself to access the server",
        "VERIFICATION_SEND_METHOD": "dm"
    }
    save_config(config)
    return jsonify({"status": "success", "message": "Configuration reset to defaults"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🌐 Dashboard running successfully")
    app.run(host='0.0.0.0', port=port, debug=False)