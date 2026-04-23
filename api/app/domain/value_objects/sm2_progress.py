from datetime import date, datetime, timezone
from pydantic import BaseModel, Field
from app.domain.enums.card_status import CardStatus
from app.domain.enums.answer_quality import AnswerQuality


class Sm2Progress(BaseModel):
    """Estado de repetição espaçada (SM-2 adaptado)."""
    ease_factor: float = 2.5
    interval_days: int = 0
    next_review_date: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())
    card_status: CardStatus = CardStatus.NEW
    lapsed_count: int = 0

    @classmethod
    def create_default(cls) -> "Sm2Progress":
        return cls()


class Sm2Algorithm:
    MIN_EASE_FACTOR = 1.3
    EASE_FACTOR_PENALTY_ON_LAPSE = 0.20
    EASE_FACTOR_PENALTY_ON_HARD = 0.15
    LEARNING_INTERVAL_DAYS = 1
    FIRST_REVIEW_INTERVAL_DAYS = 3

    @staticmethod
    def calculate_next_review(
        current: Sm2Progress,
        quality: AnswerQuality,
        current_date: date | None = None
    ) -> Sm2Progress:
        if current_date is None:
            current_date = datetime.now(timezone.utc).date()

        if quality == AnswerQuality.AGAIN:
            return Sm2Algorithm._handle_lapse(current, current_date)

        if current.card_status in (CardStatus.NEW, CardStatus.LEARNING):
            return Sm2Algorithm._handle_learning(current, quality, current_date)

        return Sm2Algorithm._handle_review(current, quality, current_date)

    @staticmethod
    def _handle_review(current: Sm2Progress, quality: AnswerQuality, current_date: date) -> Sm2Progress:
        new_ease_factor = current.ease_factor
        new_interval = current.interval_days

        if quality == AnswerQuality.HARD:
            new_ease_factor = max(Sm2Algorithm.MIN_EASE_FACTOR, current.ease_factor - Sm2Algorithm.EASE_FACTOR_PENALTY_ON_HARD)
            new_interval = round(current.interval_days * 1.2)
        elif quality == AnswerQuality.EASY:
            new_ease_factor = Sm2Algorithm._calculate_new_ease_factor(current.ease_factor, quality)
            new_interval = round(current.interval_days * new_ease_factor * 1.3)
        else:  # GOOD
            new_ease_factor = Sm2Algorithm._calculate_new_ease_factor(current.ease_factor, quality)
            new_interval = round(current.interval_days * new_ease_factor)

        new_interval = max(new_interval, current.interval_days + 1)
        next_review_date = current_date.fromordinal(current_date.toordinal() + new_interval)

        return Sm2Progress(
            ease_factor=new_ease_factor,
            interval_days=new_interval,
            next_review_date=next_review_date,
            card_status=CardStatus.REVIEW,
            lapsed_count=current.lapsed_count
        )

    @staticmethod
    def _handle_learning(current: Sm2Progress, quality: AnswerQuality, current_date: date) -> Sm2Progress:
        if quality == AnswerQuality.HARD:
            next_date = current_date.fromordinal(current_date.toordinal() + Sm2Algorithm.LEARNING_INTERVAL_DAYS)
            return Sm2Progress(
                ease_factor=current.ease_factor,
                interval_days=Sm2Algorithm.LEARNING_INTERVAL_DAYS,
                next_review_date=next_date,
                card_status=CardStatus.LEARNING,
                lapsed_count=current.lapsed_count
            )

        new_interval = Sm2Algorithm.FIRST_REVIEW_INTERVAL_DAYS
        graduation_date = current_date.fromordinal(current_date.toordinal() + new_interval)
        new_ease_factor = Sm2Algorithm._calculate_new_ease_factor(current.ease_factor, quality)
        
        return Sm2Progress(
            ease_factor=new_ease_factor,
            interval_days=new_interval,
            next_review_date=graduation_date,
            card_status=CardStatus.REVIEW,
            lapsed_count=current.lapsed_count
        )

    @staticmethod
    def _handle_lapse(current: Sm2Progress, current_date: date) -> Sm2Progress:
        new_ease_factor = max(Sm2Algorithm.MIN_EASE_FACTOR, current.ease_factor - Sm2Algorithm.EASE_FACTOR_PENALTY_ON_LAPSE)
        new_lapsed_count = current.lapsed_count + 1
        next_review_date = current_date.fromordinal(current_date.toordinal() + Sm2Algorithm.LEARNING_INTERVAL_DAYS)

        return Sm2Progress(
            ease_factor=new_ease_factor,
            interval_days=Sm2Algorithm.LEARNING_INTERVAL_DAYS,
            next_review_date=next_review_date,
            card_status=CardStatus.LEARNING,
            lapsed_count=new_lapsed_count
        )

    @staticmethod
    def _calculate_new_ease_factor(old_ease_factor: float, quality: AnswerQuality) -> float:
        q = int(quality)
        updated = old_ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        return max(Sm2Algorithm.MIN_EASE_FACTOR, updated)
