import os
import sys
from flask import Flask, render_template, request, flash, jsonify
import joblib
import numpy as np
from twilio.rest import Client
import json
import math
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, template_folder='templates')

# Secret key for flash messages - now from environment
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key_change_this')

# Get current working directory
base_dir = os.getcwd()

# Load the saved model and scaler
model_path = os.path.join(base_dir, "boat_border_model.pkl")
scaler_path = os.path.join(base_dir, "scaler.pkl")

# Fixed Geofence Configuration for Tamil Nadu - Sri Lanka Maritime Region
GEOFENCE_CONFIG = {
    # Tamil Nadu coastline coordinates (from north to south)
    "tamil_nadu_points": [
        {"lat": 13.6288, "lng": 80.1931}, # Chennai North
        {"lat": 13.0827, "lng": 80.2707}, # Chennai
        {"lat": 12.6195, "lng": 80.1952}, # Mahabalipuram
        {"lat": 11.9314, "lng": 79.8333}, # Pondicherry
        {"lat": 11.4273, "lng": 79.7662}, # Cuddalore
        {"lat": 10.7870, "lng": 79.8380}, # Karaikal
        {"lat": 10.3833, "lng": 79.8500}, # Nagapattinam
        {"lat": 9.2800, "lng": 79.3100},  # Rameswaram
        {"lat": 8.7642, "lng": 78.1348}   # Tuticorin
    ],
    
    # Sri Lanka northern coastline
    "sri_lanka_points": [
        {"lat": 9.8152, "lng": 80.0299},  # Point Pedro
        {"lat": 9.6700, "lng": 80.2500},  # Mullaitivu
        {"lat": 8.9500, "lng": 81.0000},  # Trincomalee
        {"lat": 8.3400, "lng": 81.3300},  # Batticaloa
        {"lat": 7.2800, "lng": 81.6700}   # Pottuvil
    ],
    
    # International maritime boundary line (simplified)
    "boundary_line": [
        {"lat": 10.0500, "lng": 80.0300},
        {"lat": 9.5000, "lng": 79.9000},
        {"lat": 9.2200, "lng": 79.8000},
        {"lat": 8.9000, "lng": 79.7000},
        {"lat": 8.2000, "lng": 79.3500}
    ],
    
    # Safe zone distance from boundary (in km)
    "safe_distance_km": 12, # International waters typically start at 12 nautical miles
     
    # Center point for map focus
    "center": {"lat": 9.0000, "lng": 79.8000},
    "zoom_level": 7
}

# Twilio configuration - now from environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
ALERT_RECIPIENT_NUMBER = os.environ.get('ALERT_RECIPIENT_NUMBER')

# Validate that required environment variables are set
required_env_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER', 'ALERT_RECIPIENT_NUMBER']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    print(f"Warning: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file and ensure all required variables are set.")

# Load model and scaler on startup if available
model = None
scaler = None
try:
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("Model and scaler loaded successfully")
    else:
        print("Warning: Model or Scaler file not found!")
        print("Current directory contents:", os.listdir(base_dir))
except Exception as e:
    print(f"Error loading model or scaler: {e}")

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

def check_boundary_distance(lat, lng, boundary_points):
    """
    Check the distance from a point to the boundary line
    Returns: distance in km to the closest point on the boundary
    """
    # Find minimum distance to any point on the boundary
    min_distance = float('inf')
    for point in boundary_points:
        distance = haversine(lat, lng, point["lat"], point["lng"])
        if distance < min_distance:
            min_distance = distance
    
    return min_distance

def check_geofence_status(lat, lng):
    """
    Check if a point is within the safe zone
    Returns:
        1 if inside safe zone (not near boundary)
        0 if outside safe zone (near or crossed boundary)
    """
    # Check distance to boundary line
    distance_to_boundary = check_boundary_distance(lat, lng, GEOFENCE_CONFIG["boundary_line"])
    
    # If closer to boundary than safe distance, consider it in alert zone
    if distance_to_boundary <= GEOFENCE_CONFIG["safe_distance_km"]:
        return 0, distance_to_boundary  # Alert zone
    else:
        return 1, distance_to_boundary  # Safe zone

def make_twilio_call(message):
    """
    Make a call using Twilio to alert about suspicious boat activity
    """
    # Check if Twilio credentials are available
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, ALERT_RECIPIENT_NUMBER]):
        print("Twilio credentials not available. Skipping call.")
        return False
        
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # TwiML to be executed when the call is answered
        twiml = f"""
        <Response>
            <Say>Alert! {message} Please check the monitoring system immediately.</Say>
            <Pause length="1"/>
            <Say>This is an automated call from the boat border monitoring system.</Say>
        </Response>
        """
        
        # Make the call
        call = client.calls.create(
            twiml=twiml,
            to=ALERT_RECIPIENT_NUMBER,
            from_=TWILIO_PHONE_NUMBER
        )
        
        print(f"Alert call initiated. Call SID: {call.sid}")
        return True
        
    except Exception as e:
        print(f"Failed to make Twilio call: {e}")
        return False

def analyze_boat_data(latitude, longitude, speed, direction):
    """
    Analyze boat data and determine if it's suspicious
    Returns:
        - is_suspicious: bool - whether the boat is suspicious
        - zone_status: int - 0 for alert zone, 1 for safe zone
        - zone_message: str - descriptive message about zone
        - distance: float - distance to boundary in km
        - model_prediction: int or None - ML model prediction if available
    """
    # Check geofence status first
    zone_status, distance = check_geofence_status(latitude, longitude)
    
    # Default values
    is_suspicious = False
    model_prediction = None
    
    if zone_status == 0:
        # In alert zone - automatically suspicious
        is_suspicious = True
        zone_message = f"ALERT: Boat is in restricted zone! {distance:.2f} km from boundary"
    else:
        zone_message = f"Safe: Boat is in safe zone. {distance:.2f} km from boundary"
        
        # If in safe zone but model exists, check with model as secondary verification
        if model is not None and scaler is not None:
            try:
                # Use a default behavior_label of 0 (normal)
                behavior_label = 0
                new_boat_data = [[latitude, longitude, speed, direction, zone_status, behavior_label]]
                new_boat_scaled = scaler.transform(new_boat_data)
                model_prediction = model.predict(new_boat_scaled)[0]
                
                # If model predicts suspicious despite safe zone
                if model_prediction == 1:
                    is_suspicious = True
                    zone_message += " WARNING: Behavior appears suspicious!"
            except Exception as e:
                print(f"Error using model: {e}")
    
    return is_suspicious, zone_status, zone_message, distance, model_prediction

@app.route('/', methods=['GET', 'POST'])
def predict_boat_status():
    prediction_result = None
    zone_message = None
    distance = None
    
    if request.method == 'POST':
        try:
            # Collect input data from form
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])
            speed = float(request.form['speed'])
            direction = float(request.form['direction'])
            
            # Analyze boat data
            is_suspicious, zone_status, zone_message, distance, model_prediction = analyze_boat_data(
                latitude, longitude, speed, direction
            )
            
            # Set prediction result based on analysis
            prediction_result = 1 if is_suspicious else 0
            
            # If suspicious, trigger alert
            if is_suspicious:
                alert_message = f"Suspicious boat detected at coordinates: {latitude}, {longitude}. Speed: {speed}, Direction: {direction}. {zone_message}"
                call_status = make_twilio_call(alert_message)
                
                if call_status:
                    flash(f"{zone_message} Phone alert has been sent.")
                else:
                    flash(f"{zone_message} Failed to send phone alert.")
            else:
                flash(zone_message)
                
        except Exception as e:
            error_msg = f"Error processing request: {e}"
            print(error_msg)
            flash(error_msg)
    
    return render_template('index1.html', 
                           prediction=prediction_result,
                           zone_message=zone_message,
                           distance=distance,
                           geofence_config=json.dumps(GEOFENCE_CONFIG))

@app.route('/geofence', methods=['GET'])
def get_geofence():
    """Return the current geofence configuration"""
    return jsonify(GEOFENCE_CONFIG)

@app.route('/check-point', methods=['POST'])
def api_check_point():
    """API endpoint to check if coordinates are within safe zone"""
    try:
        data = request.json
        if 'latitude' in data and 'longitude' in data:
            lat = float(data['latitude'])
            lng = float(data['longitude'])
            
            # Get speed and direction if available, otherwise use defaults
            speed = float(data.get('speed', 0))
            direction = float(data.get('direction', 0))
            
            # Analyze boat data
            is_suspicious, zone_status, zone_message, distance, model_prediction = analyze_boat_data(
                lat, lng, speed, direction
            )
            
            # If suspicious, trigger alert
            if is_suspicious:
                alert_message = f"Alert! Boat detected in restricted zone at coordinates: {lat}, {lng}."
                if 'speed' in data and 'direction' in data:
                    alert_message += f" Speed: {speed}, Direction: {direction}."
                make_twilio_call(alert_message)
            
            return jsonify({
                "inside_safe_zone": zone_status == 1,
                "is_suspicious": is_suspicious,
                "status_code": zone_status,
                "distance_to_boundary": distance,
                "message": zone_message,
                "model_prediction": model_prediction
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
    return jsonify({"status": "error", "message": "Invalid data"}), 400

if __name__ == '__main__':
    # Get debug mode from environment or default to True
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(debug=debug_mode)