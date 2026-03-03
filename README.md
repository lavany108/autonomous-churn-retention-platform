#🚀 Autonomous Customer Churn Prediction & Intelligent Retention Platform

An end-to-end Machine Learning–based churn intelligence system that predicts customer churn probability, segments customers into risk tiers, and recommends actionable retention strategies through a REST-based web application.

Developed as part of Project 96 – AIML Semester Evaluation, GLA University.

📌 1. Problem Statement

Customer churn is a major challenge faced by subscription-based businesses such as SaaS companies, telecom operators, and digital platforms.

Traditional churn systems:

Are reactive rather than preventive

Only generate churn scores

Do not provide actionable retention guidance

Lack integration between prediction and business action

This project builds a structured churn intelligence platform that connects:

Prediction → Risk Segmentation → Retention Recommendation

🎯 2. Features Implemented
✅ Supervised Churn Prediction Model

Logistic Regression (Binary Classification)

Probability-based churn scoring

Model evaluation using Accuracy & ROC-AUC

Integrated ML pipeline using scikit-learn

✅ Feature Engineering Pipeline

Missing value handling

Categorical encoding (OneHotEncoder)

Numerical scaling (StandardScaler)

ColumnTransformer-based preprocessing

Unified Pipeline for training & inference

✅ Risk-Tier Segmentation System

Customers are categorized into business-ready risk tiers:

Probability Range	Risk Tier
0.00 – 0.20	Very Low
0.21 – 0.40	Low
0.41 – 0.60	Medium
0.61 – 0.80	High
0.81 – 1.00	Critical

This converts raw ML output into decision-ready intelligence.

✅ Intelligent Retention Recommendation Engine

A rule-based recommendation system suggests actions based on:

Churn probability

Contract type

Tenure

Monthly charges

Example actions:

Offer targeted discount

Promote long-term contract upgrade

Proactive support outreach

Loyalty incentives

✅ REST API Deployment (Backend)

Built using Flask.

Endpoint Implemented:

🔹 POST /predict
Request Example:
{
  "tenure": 5,
  "MonthlyCharges": 75,
  "Contract": "Month-to-month",
  "InternetService": "Fiber optic"
}
Response Example:
{
  "churn_prediction": 1,
  "churn_probability": 0.82,
  "risk_tier": "Critical",
  "recommended_action": "Offer targeted discount and loyalty upgrade"
}
✅ Interactive Dashboard (Frontend Layer)

Built using HTML, CSS, JavaScript

Customer input form

Animated churn probability bar

Colored risk-tier badges

Dynamic recommendation display

Asynchronous API communication (fetch)

🧠 3. Machine Learning Architecture
Preprocessing:

ColumnTransformer

StandardScaler (Numerical features)

OneHotEncoder (Categorical features)

Classifier:

Logistic Regression (Binary Classification)

The model outputs probability scores rather than just class labels to support risk segmentation and business logic.

🏗️ 4. System Architecture (Implemented Components)
Frontend Layer

Risk visualization interface

Customer data input form

Retention action display

Backend Layer

Flask REST API

Model loading using Joblib

Prediction & segmentation logic

JSON response handling

AI/ML Layer

Feature engineering pipeline

Logistic Regression churn model

Risk-tier classification logic

Rule-based retention engine

📂 5. Project Structure
autonomous-churn-retention-platform/
│
├── backend/
│   ├── app.py
│   ├── ml/
│   │   ├── train_model.py
│   │   ├── model.pkl
│   │   └── preprocessing pipeline
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── README.md
⚙️ 6. Installation & Setup
Clone Repository
git clone https://github.com/lavany108/autonomous-churn-retention-platform.git
cd autonomous-churn-retention-platform
Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python app.py

Server runs at:

http://localhost:5000
Frontend

Open frontend/index.html in your browser
OR use Live Server.

📊 7. Current Completion Status

✔ Data preprocessing & ML pipeline
✔ Logistic Regression model training
✔ Risk-tier segmentation
✔ Intelligent recommendation engine
✔ REST API integration
✔ Interactive frontend dashboard

The system is fully functional from input to prediction to business recommendation.

🎓 8. Academic Relevance

This project demonstrates:

Applied Machine Learning

Feature Engineering

Model Deployment

REST API Development

Frontend–Backend Integration

Decision Support System Design

👩‍💻 Author

Lavanya
B.Tech CSE (AIML)
GLA University
