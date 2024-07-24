class ClassRunEventData:
    def __init__(self, total_tally: int, percentage: float):
        self.total_tally = total_tally
        self.percentage = percentage

    def get_total_tally(self) -> int:
        return self.total_tally

    def get_percentage(self) -> float:
        return self.percentage