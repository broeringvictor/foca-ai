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


class TestNameCompositeNames:
    """Nomes compostos comuns no Brasil."""

    def test_compound_first_name(self):
        name = Name(first_name="Ana Clara", last_name="Silva")
        assert name.first_name == "Ana Clara"
        assert name.value == "Ana Clara Silva"

    def test_compound_last_name(self):
        name = Name(first_name="João", last_name="da Silva")
        assert name.last_name == "Da Silva"
        assert name.value == "João Da Silva"

    def test_compound_first_and_last_name(self):
        name = Name(first_name="João Pedro", last_name="dos Santos")
        assert name.first_name == "João Pedro"
        assert name.last_name == "Dos Santos"

    def test_name_with_apostrophe(self):
        name = Name(first_name="D'Artagnan", last_name="Silva")
        assert name.first_name == "D'Artagnan"


class TestNameImmutability:
    """O Name é um Value Object imutável (frozen=True)."""

    def test_cannot_change_first_name(self):
        name = Name(first_name="João", last_name="Silva")
        with pytest.raises(Exception):
            name.first_name = "Carlos"  # type: ignore[misc]

    def test_cannot_change_last_name(self):
        name = Name(first_name="João", last_name="Silva")
        with pytest.raises(Exception):
            name.last_name = "Costa"  # type: ignore[misc]
