import pytest
from app.domain.value_objects.password import Password



@pytest.fixture
def valid_password() -> Password:
    return Password.create("senha_valida_123")


# ── create() ──────────────────────────────────────────────────────────────────


class TestPasswordCreate:
    """Agrupa testes relacionados ao mesmo comportamento."""

    def test_hash_is_not_plain_text(self, valid_password: Password):
        # O hash nunca deve ser igual ao texto original
        assert valid_password.hashed_value != "senha_valida_123"

    def test_hash_starts_with_argon2_prefix(self, valid_password: Password):
        # Garante que o algoritmo correto está sendo usado
        assert valid_password.hashed_value.startswith("$argon2")

    def test_two_hashes_of_same_password_are_different(self):
        # Argon2 usa salt aleatório — cada hash deve ser único
        p1 = Password.create("senha_valida_123")
        p2 = Password.create("senha_valida_123")
        assert p1.hashed_value != p2.hashed_value

    def test_strips_whitespace_before_hashing(self):
        # "  senha  " deve ser tratada igual a "senha_valida_123"
        p = Password.create("  senha_valida_123  ")
        assert p.verify("senha_valida_123")

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="ao menos 8"):
            Password.create("123")

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="no máximo 50"):
            Password.create("a" * 51)

    def test_exactly_8_chars_is_valid(self):
        Password.create("12345678")  # não deve lançar

    def test_exactly_50_chars_is_valid(self):
        Password.create("a" * 50)  # não deve lançar


# ── verify() ──────────────────────────────────────────────────────────────────


class TestPasswordVerify:
    def test_correct_password_returns_true(self, valid_password: Password):
        assert valid_password.verify("senha_valida_123") is True

    def test_wrong_password_returns_false(self, valid_password: Password):
        assert valid_password.verify("senha_errada") is False

    def test_empty_string_returns_false(self, valid_password: Password):
        assert valid_password.verify("") is False

    def test_verify_is_case_sensitive(self, valid_password: Password):
        assert valid_password.verify("SENHA_VALIDA_123") is False


# ── from_hash() ───────────────────────────────────────────────────────────────


class TestPasswordFromHash:
    def test_reconstructed_password_verifies_correctly(self):
        # Simula o ciclo completo: criar → salvar hash → reconstruir → verificar
        original = Password.create("senha_valida_123")
        hash_salvo = original.hashed_value  # o que vai pro banco

        reconstruido = Password.from_hash(hash_salvo)  # leitura do banco

        assert reconstruido.verify("senha_valida_123") is True

    def test_from_hash_does_not_rehash(self):
        original = Password.create("senha_valida_123")
        reconstruido = Password.from_hash(original.hashed_value)

        # O hash deve ser idêntico — from_hash não processa nada
        assert reconstruido.hashed_value == original.hashed_value


# ── imutabilidade (frozen=True) ───────────────────────────────────────────────


class TestPasswordImmutability:
    def test_cannot_overwrite_hashed_value(self, valid_password: Password):
        with pytest.raises(Exception):
            valid_password.hashed_value = "outro_hash"  # type: ignore[misc]
