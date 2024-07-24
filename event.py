class Event:
    def __init__(self, name: str, duration: int, proportion: int):
        self.name = name
        self.duration = duration
        self.proportion = proportion

    def get_name(self) -> str:
        return self.name

    def get_duration(self) -> int:
        return self.duration

    def get_proportion(self) -> int:
        return self.proportion

    def __str__(self) -> str:
        return f"{self.name} - {self.duration} - {self.proportion}"
