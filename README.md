# 🧠 Health Intelligence Platform
### Real-Time Biometric Monitoring + Autonomous Wellness Intervention Engine

**AI-powered corporate wellness intelligence platform** that combines:

- 📊 **wearable biometric monitoring**
- 🤖 **machine learning health score prediction**
- 📅 **autonomous calendar intervention**
- 🫀 **real-time anomaly detection**
- 🧘 **stress and sleep optimization**
- 🏢 **enterprise workforce wellness intelligence**

The platform predicts a user's **Health Score (0–100)** using wearable, sleep, lifestyle, and digital behavior data, then automatically triggers **calendar restructuring and wellness interventions**.

---

## 🚀 Key Features

### 📈 1) Real-Time Biometric Dashboard (Streamlit UI)
A premium executive dashboard for health intelligence.

### Includes:
- Sleep index monitoring
- Stress index detection
- Heart rate monitoring
- Blood oxygen analysis
- Daily step tracking
- Radar biometric profile
- 14-day health trend visualization
- Extended health analytics panel
- Risk severity badges
- Active issue flags

---

## 🖥️ UI Overview


<table>
  <tr>
    <td><b>Home / Landing Page</b></td>
    <td><b>Interest Selection</b></td>
  </tr>
  <tr>
    <td><img src="./UI/home_page.jpeg" width="400"/></td>
    <td><img src="./UI/interest_selection.jpeg" width="400"/></td>
  </tr>
  <tr>
    <td><b>Filters Page</b></td>
    <td><b>Trip Plans Page</b></td>
  </tr>
  <tr>
    <td><img src="./UI/trip_plans.jpeg" width="400"/></td>
    <td><img src="./UI/customizable_plan.jpeg" width="400"/></td>
  </tr>
</table>


### Dashboard Sections
### 🟢 Header
- Clair Health branding
- platform status
- real-time refresh timestamp

### 📊 KPI Cards
Top row executive cards:
- Sleep Index
- Stress Index
- Heart Rate
- Mood State
- Alert Level

### 📉 Monitoring Charts
- 14-day sleep score line chart
- heart rate trend chart
- daily steps bar chart
- biometric radar chart

### 📅 Schedule Intelligence
- current workday schedule
- pre-intervention calendar
- post-intervention calendar
- rescheduled meetings
- inserted recovery blocks

### ⚙️ Intervention Engine
Automatic actions:
- breathing breaks
- recovery blocks
- walk reminders
- sleep protocol alerts
- magnesium support suggestion
- elevated HR push alerts

---

## 🧠 Machine Learning Pipeline

The ML model predicts:

# 🎯 Target
`Health_Score`

### Input Features
```python
[
 'Steps', 'Calories_Burned', 'Distance_Covered',
 'Exercise_Duration', 'Exercise_Intensity',
 'Ambient_Temperature', 'Altitude', 'UV_Exposure',
 'Screen_Time', 'Age', 'Gender', 'Weight',
 'Height', 'Medical_Conditions', 'Smoker',
 'Alcohol_Consumption', 'Sleep_Duration',
 'Deep_Sleep_Duration', 'REM_Sleep_Duration',
 'Wakeups', 'Snoring', 'Heart_Rate',
 'Blood_Oxygen_Level', 'ECG',
 'Calories_Intake', 'Water_Intake',
 'Stress_Level', 'Mood',
 'Skin_Temperature', 'Body_Fat_Percentage',
 'Muscle_Mass'
]
```

### ⚙️ Model Used
- **XGBoost Regressor**
- Early stopping enabled
- Cross-validation
- Feature importance tracking
- Inference artifact export with Joblib

---

## 📊 Model Performance

### ✅ Evaluation Results
| Metric | Score |
|---|---:|
| Test RMSE | **0.9413** |
| Test MAE | **0.7455** |
| 5-Fold CV RMSE | **0.9608 ± 0.0085** |

### 🔍 Top Predictive Signals
- Blood Oxygen Level
- Sleep Duration
- Smoker
- ECG
- Exercise Duration
- Alcohol Consumption
- Stress Level
- Deep Sleep Ratio

---

## 🏗️ Project Architecture

```text
Vital-IQ/
│
├── app.py                         # Streamlit health intelligence platform
├── model_training.ipynb          # ML pipeline notebook
├── health_score_model.joblib     # trained model artifacts
├── personal_health_data.csv
├── activity_environment_data.csv
├── digital_interaction_data.csv
├── feature_importance.png
├── requirements.txt
├── auth_google.py
└── README.md
```

---

## ⚡ Data Pipeline

The project merges **3 wearable datasets**:

### 1️⃣ Activity + Environment
- steps
- calories burned
- distance
- UV exposure
- temperature
- altitude

### 2️⃣ Digital Behavior
- notifications
- screen time
- device interaction

### 3️⃣ Personal Health
- sleep stages
- oxygen level
- ECG
- stress
- mood
- body fat
- muscle mass

Merged using:
```python
["User_ID", "Timestamp"]
```

---

## 🧹 Preprocessing Pipeline

### Includes:
- Label Encoding
- One-Hot Encoding
- Frequency Encoding
- Missing value imputation
- Numeric coercion
- Automatic categorical fallback encoding

### Feature Engineering
- BMI
- Deep Sleep Ratio
- REM Sleep Ratio
- Calorie Balance

---

## 🤖 Autonomous Intervention Engine

The system automatically detects:

- poor sleep
- elevated stress
- cycle phase risk
- elevated resting HR
- low oxygen
- frequent wakeups
- low physical activity

### Triggered Actions
- 📅 reschedule meetings
- 😴 insert recovery blocks
- 🌬️ breathing breaks
- 🚶 movement blocks
- 🔔 push wellness reminders
- 💊 supplement support
- ❤️ cardiac risk alerts

---

## 📅 Google Calendar Integration

The platform can sync with **Google Calendar API**.

### Setup
Place your OAuth file:
```bash
credentials.json
```

Run:
```bash
python auth_google.py
```

This generates:
```bash
token.json
```

### Features
- read daily events
- move meetings
- insert new wellness events
- sync recovery blocks
- real-time schedule optimization

---

## ▶️ How to Run Locally

### 1) Clone Repository
```bash
git clone https://github.com/yourusername/vital-iq.git
cd vital-iq
```

### 2) Install Requirements
```bash
pip install -r requirements.txt
```

### 3) Launch Streamlit App
```bash
streamlit run app.py
```

---

## 📦 Requirements

```txt
streamlit
numpy
pandas
plotly
scikit-learn
xgboost
joblib
matplotlib
seaborn
google-api-python-client
google-auth
google-auth-oauthlib
kagglehub
```

---

## 🧠 Model Inference Example

```python
sample_user = df.sample(1).drop(columns=["Health_Score", "Anomaly_Flag"])
result = predict_health_score(sample_user)

print(result)
```

### Example Output
```python
{
    "predicted_health_score": 47.56,
    "top_contributing_features": {
        "Blood_Oxygen_Level": 56.86,
        "Steps": 19.10,
        "Calories_Intake": 5.81
    }
}
```

---

## 📌 Business Use Cases
Perfect for:

- 🏢 corporate wellness platforms
- 🏥 digital health startups
- ⌚ wearable health analytics
- 🤖 autonomous productivity assistants
- 📅 AI meeting optimization
- 🧘 employee burnout prevention
- 💼 HR wellness intelligence

---

## 🔮 Future Enhancements
- LLM-powered health coach
- SHAP explainability dashboard
- anomaly forecasting
- time-series health prediction (LSTM/Transformer)
- wearable API integration (Apple Health / Fitbit / Garmin)
- Slack/Teams intervention bot
- enterprise admin dashboards
- population health analytics

---

## 👨‍💻 Author
Built for **AI + Healthcare + Enterprise Productivity Intelligence**

If you like this project, ⭐ star the repo.