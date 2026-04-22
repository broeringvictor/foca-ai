from typing import Protocol

from app.domain.value_objects.raw_exam import ExtractionOptions, RawExam


class IOABExtractorService(Protocol):
    def extract(self, pdf_bytes: bytes, options: ExtractionOptions) -> RawExam: ...
