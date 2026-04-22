import pytest
from unittest.mock import MagicMock, patch
from app.infrastructure.services.extract_oab_question import ExtractOABQuestionService
from app.domain.value_objects.raw_exam import ExtractionOptions, RawExam

class TestExtractOABQuestionService:

    @pytest.fixture
    def service(self):
        return ExtractOABQuestionService()

    @pytest.fixture
    def mock_options(self):
        return ExtractionOptions(
            header_height=65,
            footer_height=60,
            column_split=298
        )

    def test_normalize_removes_extra_whitespaces(self, service):
        text = "  Texto   com\nmuitos   espaços  "
        normalized = service._normalize(text)
        assert normalized == "Texto com muitos espaços"

    def test_extract_header_success(self, service):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        # Simula o texto da primeira página de um exame da OAB
        mock_page.extract_text.return_value = "45º EXAME DE ORDEM UNIFICADO\nTIPO 1 – BRANCA"
        mock_pdf.pages = [mock_page]

        header = service._extract_header(mock_pdf)

        assert header["edition"] == 45
        assert "45º EXAME DE ORDEM UNIFICADO" in header["name"]
        assert header["exam_type"] == 1
        assert header["color"] == "BRANCA"

    def test_extract_header_failure(self, service):
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto inválido"
        mock_pdf.pages = [mock_page]

        with pytest.raises(ValueError, match="Cabeçalho do exame não reconhecido"):
            service._extract_header(mock_pdf)

    def test_parse_questions_basic(self, service):
        text = """
1
Enunciado da questão 1.
(A) Alternativa A1
(B) Alternativa B1
(C) Alternativa C1
(D) Alternativa D1
2
Enunciado da questão 2.
(A) Alternativa A2
(B) Alternativa B2
(C) Alternativa C2
(D) Alternativa D2
"""
        questions = service._parse_questions(text)

        assert len(questions) == 2
        assert questions[0].number == 1
        assert questions[0].statement == "Enunciado da questão 1."
        assert questions[0].alternative_a == "Alternativa A1"
        assert questions[1].number == 2
        assert questions[1].alternative_d == "Alternativa D2"

    def test_parse_questions_with_noise(self, service):
        # Texto com ruído que deve ser filtrado (ex: menos de 4 alternativas identificadas)
        text = """
1
Questão incompleta.
(A) Só tem uma
2
Questão completa.
(A) Alt A
(B) Alt B
(C) Alt C
(D) Alt D
"""
        questions = service._parse_questions(text)

        # A primeira questão deve ser ignorada porque não tem todas as alternativas (A-D)
        assert len(questions) == 1
        assert questions[0].number == 2

    @patch("pdfplumber.open")
    def test_extract_orchestration(self, mock_pdf_open, service, mock_options):
        # Mock do pdfplumber context manager
        mock_pdf = MagicMock()
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        # Mock dos métodos internos para testar a orquestração
        with patch.object(service, "_extract_header") as mock_header, \
             patch.object(service, "_extract_questions_text") as mock_text, \
             patch.object(service, "_parse_questions") as mock_parse:

            mock_header.return_value = {
                "edition": 45,
                "name": "45º EXAME",
                "exam_type": 1,
                "color": "BRANCA"
            }
            mock_text.return_value = "Texto das questões"
            mock_parse.return_value = []

            result = service.extract(b"dummy pdf content", mock_options)

            assert isinstance(result, RawExam)
            assert result.edition == 45
            mock_header.assert_called_once()
            mock_text.assert_called_once()
            mock_parse.assert_called_once_with("Texto das questões")

