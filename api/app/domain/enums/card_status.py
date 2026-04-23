from enum import IntEnum


class CardStatus(IntEnum):
    NEW = 0
    LEARNING = 1
    REVIEW = 2
    RELEARNING = 3
