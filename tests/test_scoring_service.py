import pytest
from services.scoring_service import ScoringService

def test_score_steps():
    service = ScoringService()
    # 5000 steps, ideal 10000 -> 50 score
    assert service._score_steps(5000) == 50.0
    assert service._score_steps(10000) == 100.0
    assert service._score_steps(15000) == 100.0

def test_score_sleep():
    service = ScoringService()
    # ideal is 7-8 hours
    assert service._score_sleep(7.5) == 100.0
    
    # 6 hours should be less than 100 (6/7 * 100 ≈ 85.7)
    score_6h = service._score_sleep(6.0)
    assert score_6h < 100.0
    assert round(score_6h, 1) == 85.7
    
    # 9 hours should have slight penalty (100 - (1 * 15) = 85.0)
    score_9h = service._score_sleep(9.0)
    assert score_9h < 100.0
    assert round(score_9h, 1) == 85.0

def test_calculate_score():
    service = ScoringService()
    metrics = {
        "steps": 10000,
        "sleep": 7.5,
        "calories": 2000,
        "heart_rate": 70
    }
    result = service.calculate_score(metrics)
    assert result["total_score"] == 100.0
    assert result["grade"] == "A+"

def test_calculate_score_average():
    service = ScoringService()
    metrics = {
        "steps": 5000,   # 50 score -> weight 0.3 = 15
        "sleep": 6.0,    # 85.7 score -> weight 0.3 = 25.71
        "calories": 1000,# 50 score -> weight 0.2 = 10
        "heart_rate": 80 # mid is 80 -> 100 score -> weight 0.2 = 20
                         # Wait, mind to max is 60 to 100, mid is 80.
    }
    result = service.calculate_score(metrics)
    assert result["total_score"] > 60.0
    assert "grade" in result
