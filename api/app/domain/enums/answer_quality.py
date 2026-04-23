from enum import IntEnum


class AnswerQuality(IntEnum):
    AGAIN = 0  # Forgot
    HARD = 3   # Hard
    GOOD = 4   # Good
    EASY = 5   # Easy
