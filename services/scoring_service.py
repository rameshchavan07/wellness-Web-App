"""
DayScore - Scoring Service
Calculates the daily DayScore (0-100) from fitness metrics.
"""

from config.settings import ScoringConfig


class ScoringService:
    """Calculates and normalizes the DayScore."""

    def __init__(self):
        self.weights = ScoringConfig.WEIGHTS
        self.ideals = ScoringConfig.IDEALS

    def calculate_score(self, metrics: dict) -> dict:
        """
        Calculate DayScore from fitness metrics.

        Args:
            metrics: dict with keys 'steps', 'sleep', 'calories', 'heart_rate'

        Returns:
            dict with overall score, component scores, and breakdown
        """
        steps = metrics.get("steps", 0)
        sleep = metrics.get("sleep", 0)        # hours
        calories = metrics.get("calories", 0)
        heart_rate = metrics.get("heart_rate", 0)  # resting BPM

        # Calculate individual component scores (0-100)
        step_score = self._score_steps(steps)
        sleep_score = self._score_sleep(sleep)
        calorie_score = self._score_calories(calories)
        hr_score = self._score_heart_rate(heart_rate)

        # Weighted total
        total = (
            step_score * self.weights["steps"]
            + sleep_score * self.weights["sleep"]
            + calorie_score * self.weights["calories"]
            + hr_score * self.weights["heart_rate"]
        )
        total = round(min(max(total, 0), 100), 1)

        return {
            "total_score": total,
            "breakdown": {
                "steps": {"value": steps, "score": round(step_score, 1), "weight": self.weights["steps"]},
                "sleep": {"value": sleep, "score": round(sleep_score, 1), "weight": self.weights["sleep"]},
                "calories": {"value": calories, "score": round(calorie_score, 1), "weight": self.weights["calories"]},
                "heart_rate": {"value": heart_rate, "score": round(hr_score, 1), "weight": self.weights["heart_rate"]},
            },
            "grade": self._get_grade(total),
            "message": self._get_motivational_message(total),
        }

    # ── Component Scoring ──────────────────────────────────────────

    def _score_steps(self, steps: int) -> float:
        """Score steps (0-100). Linear up to ideal, capped at 100."""
        ideal = self.ideals["steps"]
        if steps >= ideal:
            return 100.0
        return (steps / ideal) * 100

    def _score_sleep(self, hours: float) -> float:
        """Score sleep (0-100). Peak at 7-8 h, tapers outside."""
        min_h = self.ideals["sleep_min"]
        max_h = self.ideals["sleep_max"]
        if min_h <= hours <= max_h:
            return 100.0
        if hours < min_h:
            return max((hours / min_h) * 100, 0)
        # Over-sleeping penalty (gentler)
        over = hours - max_h
        return max(100 - (over * 15), 0)

    def _score_calories(self, calories: int) -> float:
        """Score calories burned (0-100)."""
        ideal = self.ideals["calories"]
        if calories >= ideal:
            return 100.0
        return (calories / ideal) * 100 if ideal else 0

    def _score_heart_rate(self, bpm: int) -> float:
        """Score resting heart rate (0-100). Lower is generally better."""
        if bpm == 0:
            return 50.0  # No data — neutral
        min_bpm = self.ideals["heart_rate_min"]
        max_bpm = self.ideals["heart_rate_max"]
        if min_bpm <= bpm <= max_bpm:
            # Best if in the lower half of normal
            mid = (min_bpm + max_bpm) / 2
            if bpm <= mid:
                return 100.0
            return 100 - ((bpm - mid) / (max_bpm - mid)) * 20
        if bpm < min_bpm:
            return max(100 - (min_bpm - bpm) * 3, 40)
        # Above max — concerning
        return max(100 - (bpm - max_bpm) * 5, 0)

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _get_grade(score: float) -> str:
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"

    @staticmethod
    def _get_motivational_message(score: float) -> str:
        if score >= 90:
            return "🌟 Outstanding! You're crushing your health goals!"
        elif score >= 80:
            return "🔥 Great job! Keep up the amazing work!"
        elif score >= 70:
            return "💪 Good progress! A little more effort and you'll be a star!"
        elif score >= 60:
            return "👍 Decent day. Small improvements make big differences!"
        elif score >= 50:
            return "🌱 Room to grow. Try a short walk or earlier bedtime!"
        else:
            return "💙 Every day is a fresh start. Let's build momentum!"
