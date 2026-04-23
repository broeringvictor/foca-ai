from datetime import date
from app.domain.enums.card_status import CardStatus
from app.domain.enums.answer_quality import AnswerQuality
from app.domain.value_objects.sm2_progress import Sm2Progress, Sm2Algorithm


def test_initial_progress():
    progress = Sm2Progress.create_default()
    assert progress.ease_factor == 2.5
    assert progress.interval_days == 0
    assert progress.card_status == CardStatus.NEW


def test_good_review_on_new_card():
    progress = Sm2Progress.create_default()
    today = date(2024, 1, 1)
    
    # Good review on a New card should graduate it to Review status
    next_progress = Sm2Algorithm.calculate_next_review(progress, AnswerQuality.GOOD, current_date=today)
    
    assert next_progress.card_status == CardStatus.REVIEW
    assert next_progress.interval_days == 3
    assert next_progress.next_review_date == date(2024, 1, 4)


def test_again_review_on_review_card():
    # Setup a card in Review status
    progress = Sm2Progress(
        ease_factor=2.5,
        interval_days=10,
        next_review_date=date(2024, 1, 1),
        card_status=CardStatus.REVIEW,
        lapsed_count=0
    )
    today = date(2024, 1, 1)
    
    # "Again" should put it back to Learning and apply penalty
    next_progress = Sm2Algorithm.calculate_next_review(progress, AnswerQuality.AGAIN, current_date=today)
    
    assert next_progress.card_status == CardStatus.LEARNING
    assert next_progress.interval_days == 1
    assert next_progress.ease_factor < 2.5
    assert next_progress.lapsed_count == 1

def test_counters_and_success_rate():
    progress = Sm2Progress.create_default()
    today = date(2024, 1, 1)
    
    # First correct answer (GOOD)
    p1 = Sm2Algorithm.calculate_next_review(progress, AnswerQuality.GOOD, current_date=today)
    assert p1.correct_count == 1
    assert p1.wrong_count == 0
    assert p1.total_attempts == 1
    assert p1.success_rate == 1.0
    
    # Second correct answer (EASY)
    p2 = Sm2Algorithm.calculate_next_review(p1, AnswerQuality.EASY, current_date=today)
    assert p2.correct_count == 2
    assert p2.wrong_count == 0
    assert p2.total_attempts == 2
    assert p2.success_rate == 1.0
    
    # One wrong answer (AGAIN)
    p3 = Sm2Algorithm.calculate_next_review(p2, AnswerQuality.AGAIN, current_date=today)
    assert p3.correct_count == 2
    assert p3.wrong_count == 1
    assert p3.total_attempts == 3
    assert abs(p3.success_rate - 0.666) < 0.01
