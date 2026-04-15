import pytest
from app.domain.value_objects.name import Name



class TestCreateName:


    def test_normalize_with_valid_name(self):
        name = Name(first_name="geNtiL JOãO dA", last_name="Silva")
        assert name.first_name == "Gentil João Da"
        assert name.last_name == "Silva"
        assert name.value == "Gentil João Da Silva"


    def test_value_is_full_name(self):
        name = Name(first_name="Maria", last_name="Costa")

        assert name.value == "Maria Costa"

    def test_str_returns_full_name(self):
        name = Name(first_name="Carlos", last_name="Pereira")

        assert str(name) == "Carlos Pereira"

class TestNameFirstNameValidation:
    def test_empty_first_name_raises(self):
        with pytest.raises(ValueError, match="não pode ser vazio"):
            Name(first_name="", last_name="Silva")

    def test_too_short_first_name_raises(self):
        with pytest.raises(ValueError, match="ao menos 2 caracteres"):
            Name(first_name="A", last_name="Silva")

    def test_too_long_first_name_raises(self):
        with pytest.raises(ValueError, match="no máximo 48 caracteres"):
            Name(first_name="A" * 49, last_name="Silva")

    def test_first_name_with_numbers_raises(self):
        with pytest.raises(ValueError, match="caracteres inválidos"):
            Name(first_name="Jo4o", last_name="Silva")

    def test_first_name_starting_with_hyphen_raises(self):
        with pytest.raises(ValueError, match="não pode começar ou terminar"):
            Name(first_name="-João", last_name="Silva")

    def test_first_name_ending_with_apostrophe_raises(self):
        with pytest.raises(ValueError, match="não pode começar ou terminar"):
            Name(first_name="João'", last_name="Silva")

    def test_consecutive_special_chars_raises(self):
        with pytest.raises(ValueError, match="caracteres especiais consecutivos"):
            Name(first_name="Jo--ão", last_name="Silva")

    def test_hyphenated_first_name_is_valid(self):
        name = Name(first_name="Ana-Clara", last_name="Silva")

        assert name.first_name == "Ana-Clara"

    def test_first_name_with_accent_is_valid(self):
        name = Name(first_name="Renée", last_name="Silva")

        assert name.first_name == "Renée"


class TestNameLastNameValidation:
    def test_empty_last_name_raises(self):
        with pytest.raises(ValueError, match="não pode ser vazio"):
            Name(first_name="João", last_name="")

    def test_too_short_last_name_raises(self):
        with pytest.raises(ValueError, match="ao menos 2 caracteres"):
            Name(first_name="João", last_name="S")

    def test_too_long_last_name_raises(self):
        with pytest.raises(ValueError, match="no máximo 48 caracteres"):
            Name(first_name="João", last_name="S" * 49)

    def test_last_name_with_numbers_raises(self):
        with pytest.raises(ValueError, match="caracteres inválidos"):
            Name(first_name="João", last_name="Si1va")


class TestNameFullNameValidation:
    def test_full_name_too_long_raises(self):
        # first(24) + space + last(26) = 51 chars
        with pytest.raises(ValueError, match="no máximo 50 caracteres"):
            Name(first_name="A" * 24, last_name="B" * 26)

    def test_full_name_exactly_50_chars_is_valid(self):
        # first(24) + space + last(25) = 50 chars
        name = Name(first_name="Aa" * 12, last_name="Bb" * 12 + "B")

        assert len(name.value) == 50