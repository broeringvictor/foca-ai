import pytest
from datetime import datetime, timedelta, timezone

from app.domain.value_objects.recoverty_code import RecoveryCode


class TestRecoveryCode:
    def test_create_recovery_code(self):
        before = datetime.now(timezone.utc)
        code = RecoveryCode()
        after = datetime.now(timezone.utc)
        assert len(code.code) > 0
        assert str(code.code) == code.code

        expected = timedelta(hours=1)
        assert before + expected <= code.expires_at <= after + expected

    def test_create_should_be_different(self):
        code01 = RecoveryCode()
        code02 = RecoveryCode()
        code03 = RecoveryCode()

        assert code01.code != code02.code != code03.code

    def test_verify_correct_code(self):
        code = RecoveryCode()
        assert code.verify(code.code) is True

    def test_verify_wrong_code(self):
        code = RecoveryCode()
        assert code.verify("codigo_errado") is False

    def test_verify_expired_raises(self):
        code = RecoveryCode(expires_at=datetime.now(timezone.utc) - timedelta(hours=1))
        with pytest.raises(ValueError, match="expirou"):
            code.verify(code.code)
