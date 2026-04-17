import io
import re

import pdfplumber
from loguru import logger

from app.domain.value_objects.raw_exam import (
    ExtractionOptions,
    RawExam,
    RawQuestion,
)

TITLE_RE = re.compile(r"(\d+)[ºO°]\s+EXAME\s+DE\s+ORDEM\s+UNIFICADO", re.IGNORECASE)
TYPE_RE = re.compile(r"TIPO\s+(\d+)\s*[–-]\s*(\w+)", re.IGNORECASE)
QUESTIONNAIRE_RE = re.compile(r"question[aá]rio\s+de\s+percep", re.IGNORECASE)
QUESTION_START_RE = re.compile(r"^\s*(\d{1,3})\s*$", re.MULTILINE)
ALTERNATIVE_SPLIT_RE = re.compile(r"^\(([A-D])\)\s*", re.MULTILINE)


class ExtractOABQuestionService:
    """Implementação de ``IOABExtractorService`` usando pdfplumber."""

    def extract(self, pdf_bytes: bytes, options: ExtractionOptions) -> RawExam:
        logger.info(
            "extract.oab: start pdf_bytes={} header={} footer={} split={}",
            len(pdf_bytes),
            options.header_height,
            options.footer_height,
            options.column_split,
        )
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            logger.info("extract.oab: pdf_opened pages={}", len(pdf.pages))
            header = self._extract_header(pdf)
            text = self._extract_questions_text(pdf, options)

        questions = self._parse_questions(text)
        logger.info(
            "extract.oab: done edition={} type={} color={} questions={}",
            header["edition"],
            header["exam_type"],
            header["color"],
            len(questions),
        )
        return RawExam(**header, questions=questions)

    # ── header (capa) ─────────────────────────────────────────────────────────

    @staticmethod
    def _extract_header(pdf) -> dict:
        text = pdf.pages[0].extract_text() or ""
        title_match = TITLE_RE.search(text)
        type_match = TYPE_RE.search(text)

        if not title_match or not type_match:
            logger.warning("extract.oab: header_not_recognized")
            raise ValueError("Cabeçalho do exame não reconhecido na 1ª página")

        return {
            "edition": int(title_match.group(1)),
            "name": title_match.group(0).upper(),
            "exam_type": int(type_match.group(1)),
            "color": type_match.group(2).upper(),
        }

    # ── corpo (questões) ──────────────────────────────────────────────────────

    @staticmethod
    def _extract_body_text(page, options: ExtractionOptions) -> str:
        top = options.header_height
        bottom = page.height - options.footer_height
        split = options.column_split

        left_bbox = (0, top, split, bottom)
        right_bbox = (split, top, page.width, bottom)

        left = page.crop(left_bbox).extract_text() or ""
        right = page.crop(right_bbox).extract_text() or ""
        return f"{left}\n{right}"

    def _extract_questions_text(self, pdf, options: ExtractionOptions) -> str:
        full_text = "\n".join(
            self._extract_body_text(p, options) for p in pdf.pages[1:]
        )
        match = QUESTIONNAIRE_RE.search(full_text)
        if match:
            logger.info(
                "extract.oab: questionnaire_tail_trimmed chars_before_trim={}",
                len(full_text) - match.start(),
            )
            full_text = full_text[: match.start()]
        return full_text.rstrip()

    # ── parser ────────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def _parse_questions(cls, text: str) -> list[RawQuestion]:
        starts = list(QUESTION_START_RE.finditer(text))
        questions: list[RawQuestion] = []

        for i, match in enumerate(starts):
            number = int(match.group(1))
            block_start = match.end()
            block_end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
            block = text[block_start:block_end]

            parts = ALTERNATIVE_SPLIT_RE.split(block)
            if len(parts) < 9:
                continue

            alts = {parts[j]: parts[j + 1] for j in range(1, len(parts) - 1, 2)}
            if not all(letter in alts for letter in "ABCD"):
                continue

            try:
                questions.append(
                    RawQuestion(
                        number=number,
                        statement=cls._normalize(parts[0]),
                        alternative_a=cls._normalize(alts["A"]),
                        alternative_b=cls._normalize(alts["B"]),
                        alternative_c=cls._normalize(alts["C"]),
                        alternative_d=cls._normalize(alts["D"]),
                    )
                )
            except Exception:
                continue

        questions.sort(key=lambda q: q.number)
        logger.info(
            "extract.oab: parsed_questions total={} candidate_blocks={}",
            len(questions),
            len(starts),
        )
        return questions
