from datetime import date, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.domain.entities.exam import Exam


class TestCreateExam:
    def test_creates_with_all_fields(self):
        exam = Exam.create(
            name="XL Exame de Ordem Unificado",
            edition=40,
            year=2024,
            board="FGV",
            first_phase_date=date(2024, 3, 24),
            second_phase_date=date(2024, 5, 19),
        )

        assert exam.name == "XL Exame de Ordem Unificado"
        assert exam.edition == 40
        assert exam.year == 2024
        assert exam.board == "FGV"
        assert exam.first_phase_date == date(2024, 3, 24)
        assert exam.second_phase_date == date(2024, 5, 19)

    def test_creates_with_only_required_fields(self):
        exam = Exam.create(
            name="XL Exame de Ordem Unificado",
            edition=40,
            year=2024,
            board="FGV",
        )

        assert exam.first_phase_date is None
        assert exam.second_phase_date is None


class TestExamDefaults:
    def test_generates_id_automatically(self):
        exam = Exam.create(
            name="XL Exame de Ordem Unificado",
            edition=40,
            year=2024,
            board="FGV",
        )

        assert isinstance(exam.id, UUID)

    def test_sets_created_at_and_updated_at(self):
        exam = Exam.create(
            name="XL Exame de Ordem Unificado",
            edition=40,
            year=2024,
            board="FGV",
        )

        assert isinstance(exam.created_at, datetime)
        assert isinstance(exam.updated_at, datetime)


class TestExamValidation:
    def test_name_too_short_raises(self):
        with pytest.raises(ValidationError):
            Exam.create(name="abc", edition=40, year=2024, board="FGV")

    def test_name_too_long_raises(self):
        with pytest.raises(ValidationError):
            Exam.create(name="a" * 151, edition=40, year=2024, board="FGV")

    def test_edition_must_be_positive(self):
        with pytest.raises(ValidationError):
            Exam.create(name="Exame OAB", edition=0, year=2024, board="FGV")

    def test_year_must_be_within_range(self):
        with pytest.raises(ValidationError):
            Exam.create(name="Exame OAB", edition=40, year=1999, board="FGV")
        with pytest.raises(ValidationError):
            Exam.create(name="Exame OAB", edition=40, year=2101, board="FGV")

    def test_board_too_short_raises(self):
        with pytest.raises(ValidationError):
            Exam.create(name="Exame OAB", edition=40, year=2024, board="F")

    def test_board_too_long_raises(self):
        with pytest.raises(ValidationError):
            Exam.create(name="Exame OAB", edition=40, year=2024, board="a" * 101)

