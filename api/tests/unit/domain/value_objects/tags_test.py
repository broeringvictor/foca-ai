import pytest
from pydantic import TypeAdapter, ValidationError

from app.domain.value_objects.tags import Tags

tags_adapter: TypeAdapter[list[str]] = TypeAdapter(Tags)


def _validate(raw):
    return tags_adapter.validate_python(raw)


class TestTagsNormalization:
    def test_strips_whitespace(self):
        assert _validate(["  python  ", "fastapi "]) == ["python", "fastapi"]

    def test_drops_empty_strings(self):
        assert _validate(["python", "", "   ", "sqlalchemy"]) == ["python", "sqlalchemy"]

    def test_preserves_original_case(self):
        assert _validate(["Python", "FastAPI"]) == ["Python", "FastAPI"]

    def test_deduplicates_case_insensitive(self):
        assert _validate(["Python", "python", "PYTHON"]) == ["Python"]

    def test_deduplication_preserves_first_occurrence(self):
        assert _validate(["FastAPI", "fastapi", "Python"]) == ["FastAPI", "Python"]

    def test_empty_list_is_valid(self):
        assert _validate([]) == []


class TestTagsLengthValidation:
    def test_tag_at_max_length_is_valid(self):
        tag = "a" * 30
        assert _validate([tag]) == [tag]

    def test_tag_above_max_length_raises(self):
        with pytest.raises(ValidationError, match="Tag excede 30 caracteres"):
            _validate(["a" * 31])

    def test_up_to_twenty_tags_is_valid(self):
        tags = [f"tag{i}" for i in range(20)]
        assert _validate(tags) == tags

    def test_more_than_twenty_tags_raises(self):
        tags = [f"tag{i}" for i in range(21)]
        with pytest.raises(ValidationError, match="Quantidade máxima de tags excedida"):
            _validate(tags)

    def test_twenty_after_dedup_is_valid(self):
        tags = [f"tag{i}" for i in range(20)] + ["tag0", "tag1"]
        assert len(_validate(tags)) == 20


class TestTagsTypeValidation:
    def test_non_string_raises(self):
        with pytest.raises(ValidationError):
            _validate([123, "python"])

    def test_none_in_list_raises(self):
        with pytest.raises(ValidationError):
            _validate([None, "python"])
