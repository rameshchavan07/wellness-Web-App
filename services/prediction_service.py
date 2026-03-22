"""
DayScore - Prediction Service
Uses scikit-learn to analyze the last 14-30 days of daily scores 
and forecast tomorrow's DayScore.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from config.firebase_config import get_firestore_client
from datetime import datetime, timedelta

class PredictionService:
    """Provides ML forecasting for DayScore metrics."""

    def __init__(self):
        self.db = get_firestore_client()

    def get_historical_data(self, user_id: str, days: int = 30) -> list:
        """Fetch the last N days of data from Firestore 'daily_scores' collection."""
        if not self.db:
            return self._generate_demo_history(days)

        try:
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            docs = self.db.collection("daily_scores")\
                        .where("user_id", "==", user_id)\
                        .where("timestamp", ">=", cutoff)\
                        .order_by("timestamp", direction="ASCENDING")\
                        .get()
            
            data = [doc.to_dict() for doc in docs]
            return data if data else self._generate_demo_history(days)
        except Exception as e:
            print(f"Error fetching history for prediction: {e}")
            return self._generate_demo_history(days)

    def predict_tomorrow(self, user_id: str) -> dict:
        """
        Train a Ridge Regression model to predict tomorrow's score.
        Identifies the feature (steps, sleep, calories) that is pulling the score down the most.
        """
        data = self.get_historical_data(user_id)
        
        if len(data) < 3:
            return {
                "success": False, 
                "message": "Not enough data for an accurate prediction yet. Keep using DayScore!"
            }

        df = pd.DataFrame(data)
        
        # Features & Target
        # If 'day_score' doesn't exist (legacy), compute it or use random for fallback
        if "day_score" not in df.columns:
            df["day_score"] = df.apply(lambda row: min(100, (row.get("steps", 0)/100) + (row.get("sleep", 0)*10)), axis=1)

        features = ["steps", "sleep", "calories"]
        
        # Ensure columns exist
        for f in features:
            if f not in df.columns:
                df[f] = 0.0

        X = df[features].values
        y = df["day_score"].values

        # Scale features for accurate coefficient interpretation
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train model
        model = Ridge(alpha=1.0)
        model.fit(X_scaled, y)

        # Predict tomorrow assuming they do the *average* of their last 3 days
        recent_3 = df.tail(3)[features].mean().values
        recent_3_scaled = scaler.transform([recent_3])
        predicted_score = float(model.predict(recent_3_scaled)[0])
        predicted_score = max(0.0, min(100.0, predicted_score))

        # Determine which feature to focus on (the one with highest positive weight 
        # but where their recent average is lowest compared to history)
        
        # Coefficients tell us how much each feature impacts the score
        coefs = dict(zip(features, model.coef_))
        
        # Find feature where (Historical Max - Recent Avg) * Coef is highest
        # meaning "you are falling behind on this, and it hurts your score"
        biggest_impact_feature = "steps"
        max_impact = -9999
        
        for f in features:
            if coefs[f] > 0:
                hist_max = df[f].max()
                recent_avg = df[f].tail(3).mean()
                gap = hist_max - recent_avg
                impact = gap * coefs[f]
                if impact > max_impact:
                    max_impact = impact
                    biggest_impact_feature = f

        # Formulate insight
        feature_names = {
            "steps": "daily step count",
            "sleep": "sleep duration",
            "calories": "active calories"
        }

        return {
            "success": True,
            "predicted_score": round(predicted_score),
            "focus_metric": feature_names.get(biggest_impact_feature, biggest_impact_feature),
            "message": f"Based on your recent trends, you might score around **{round(predicted_score)}** tomorrow. Focus on your **{feature_names.get(biggest_impact_feature, biggest_impact_feature)}** to push it higher!"
        }

    def _generate_demo_history(self, days: int) -> list:
        import random
        history = []
        for i in range(days, 0, -1):
            dt = datetime.utcnow() - timedelta(days=i)
            steps = random.randint(4000, 12000)
            sleep = random.uniform(5.0, 8.5)
            cal = random.randint(1500, 2500)
            score = (steps/10000)*40 + (min(sleep, 8)/8)*30 + (cal/2000)*30
            
            history.append({
                "date": dt.strftime("%Y-%m-%d"),
                "timestamp": dt.isoformat(),
                "steps": steps,
                "sleep": round(sleep, 1),
                "calories": cal,
                "day_score": round(min(100, score))
            })
        return history
