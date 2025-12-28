from datetime import datetime

class AnalysisResult:
    def __init__(self, report_id, care_score, explanation, metrics):
        self.report_id = report_id
        self.care_score = care_score
        self.explanation = explanation
        self.metrics = metrics # List of calculated deviations
        self.generated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "report_id": self.report_id,
            "care_score": self.care_score,
            "explanation": self.explanation,
            "metrics": self.metrics,
            "generated_at": self.generated_at
        }