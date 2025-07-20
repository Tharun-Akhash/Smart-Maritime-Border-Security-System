# 🚤 Maritime Border Monitoring System

A real-time boat tracking and border monitoring system for the Tamil Nadu - Sri Lanka maritime region. This Flask-based application uses machine learning to detect suspicious boat activities and provides automated alerts through Twilio integration.

## 🌟 Features

- **Real-time Geofence Monitoring**: Tracks boats in the Tamil Nadu - Sri Lanka maritime boundary
- **Machine Learning Detection**: Uses trained ML models to identify suspicious boat behavior
- **Automated Alerts**: Sends phone calls via Twilio when suspicious activity is detected
- **Interactive Web Interface**: User-friendly dashboard for monitoring boat positions
- **RESTful API**: Programmatic access for integration with other systems
- **Safe Zone Management**: Configurable 12km safe distance from international boundary

## 🗺️ Coverage Area

- **Tamil Nadu Coastline**: Chennai to Tuticorin
- **Sri Lanka Northern Coast**: Point Pedro to Pottuvil
- **International Maritime Boundary**: Simplified boundary line with safe zones
- **Alert Zones**: Within 12km of the international boundary

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Twilio Account (for SMS/Call alerts)
- Flask
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/maritime-border-monitoring.git
   cd maritime-border-monitoring
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual credentials
   nano .env
   ```

4. **Configure your .env file**
   ```env
   # Twilio Configuration
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ALERT_RECIPIENT_NUMBER=recipient_phone_number
   
   # Flask Configuration
   FLASK_SECRET_KEY=your_secure_secret_key
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

5. **Run the application**
   ```bash
   python app3.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## 📋 API Documentation

### Check Point Status

**Endpoint**: `POST /check-point`

**Request Body**:
```json
{
  "latitude": 9.2800,
  "longitude": 79.3100,
  "speed": 15.5,
  "direction": 180
}
```

**Response**:
```json
{
  "inside_safe_zone": true,
  "is_suspicious": false,
  "status_code": 1,
  "distance_to_boundary": 25.4,
  "message": "Safe: Boat is in safe zone. 25.4 km from boundary",
  "model_prediction": 0
}
```

### Get Geofence Configuration

**Endpoint**: `GET /geofence`

Returns the current geofence configuration including boundary points and safe distances.

## 🧠 Machine Learning Model

The system uses a trained machine learning model that analyzes:
- **Latitude & Longitude**: Boat position
- **Speed**: Boat velocity
- **Direction**: Heading direction
- **Zone Status**: Whether boat is in safe or alert zone
- **Behavior Pattern**: Historical behavior analysis

### Model Features
- Trained on historical boat movement data
- Detects anomalous patterns even in safe zones
- Provides binary classification (normal/suspicious)
- Integrated with geofence alerts for comprehensive monitoring

## 🛡️ Security Features

- **Environment Variables**: All sensitive data stored in `.env` file
- **Credential Validation**: Checks for required environment variables
- **Error Handling**: Graceful handling of missing credentials
- **Secure Configuration**: Production-ready security settings

## 📁 Project Structure

```
maritime-border-monitoring/
├── app3.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Your actual environment variables (not in git)
├── templates/
│   └── index1.html        # Web interface template
├── boat_border_model.pkl  # Trained ML model (if available)
├── scaler.pkl            # Feature scaler (if available)
└── README.md             # This file
```

## 🔧 Configuration

### Geofence Settings

The system is pre-configured with:
- **Safe Distance**: 12km from international boundary
- **Tamil Nadu Points**: Major coastal cities from Chennai to Tuticorin
- **Sri Lanka Points**: Northern coastline key locations
- **Boundary Line**: Simplified international maritime boundary

### Customization

You can modify the `GEOFENCE_CONFIG` in `app3.py` to:
- Adjust safe distance
- Add more boundary points
- Change alert thresholds
- Modify map center and zoom levels

## 🚨 Alert System

### Automatic Alerts Triggered When:
1. **Geofence Violation**: Boat enters restricted zone (within 12km of boundary)
2. **Suspicious Behavior**: ML model detects anomalous patterns
3. **Combined Factors**: Multiple risk factors detected simultaneously

### Alert Methods:
- **Phone Calls**: Automated voice calls via Twilio
- **Web Interface**: Real-time status updates
- **API Responses**: Programmatic alert information

## 🧪 Testing

Test the system with sample coordinates:

**Safe Zone Test**:
- Latitude: 11.4273, Longitude: 79.7662 (Cuddalore)

**Alert Zone Test**:
- Latitude: 9.2800, Longitude: 79.3100 (Near Rameswaram)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This system is designed for monitoring and educational purposes. It should not be used as the sole method for maritime security. Always consult with relevant maritime authorities and follow local regulations.

## 🆘 Support

If you encounter any issues:

1. Check that all environment variables are correctly set
2. Ensure Twilio credentials are valid and account has sufficient credits
3. Verify that required model files are present
4. Check the console for detailed error messages

## 🙏 Acknowledgments

- Twilio for communication services
- Flask community for the web framework
- Scikit-learn for machine learning capabilities
- OpenStreetMap for geographical data

## 📞 Contact

For questions or support, please open an issue on GitHub or contact the development team.

---

**⭐ Star this repository if you find it helpful!**
