from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from fastapi import Depends, File, Form, UploadFile
from loguru import logger

from app.api.errors.exceptions import BadRequestError
from app.infrastructure.config.settings import get_settings

ALLOWED_MARKDOWN_EXTENSIONS = {".md", ".markdown"}
ALLOWED_MARKDOWN_MIME_TYPES = {
    "text/markdown",
    "text/plain",
    "application/octet-stream",
    "",
    None,
}
settings = get_settings()
MAX_FILENAME_LEN = settings.MAX_FILENAME_LEN
MAX_MARKDOWN_CONTENT_LEN = settings.MAX_MARKDOWN_CONTENT_LEN
MAX_MARKDOWN_BYTES = settings.MAX_MARKDOWN_BYTES


@dataclass(frozen=True)
class MarkdownUpload:
    filename: str
    extension: str
    content_type: str | None
    size_bytes: int
    checksum_sha256: str
    line_count: int
    heading_count: int
    content: str


async def get_markdown_upload(
    content_file: UploadFile | None = File(None),
) -> MarkdownUpload | None:
    if content_file is None:
        logger.info("study_note.upload: sem arquivo markdown no request")
        return None

    filename = content_file.filename or ""
    if not filename or Path(filename).name != filename:
        logger.warning("study_note.upload: nome de arquivo invalido")
        raise BadRequestError(
            "Nome do arquivo inválido",
            field="content_file",
            source="file",
        )

    if len(filename) > MAX_FILENAME_LEN:
        logger.warning("study_note.upload: filename excede limite len={}", len(filename))
        raise BadRequestError(
            "Nome do arquivo excede 255 caracteres",
            field="content_file",
            source="file",
        )

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_MARKDOWN_EXTENSIONS:
        logger.warning(
            "study_note.upload: extensao invalida filename={} extension={}",
            filename,
            extension,
        )
        raise BadRequestError(
            "Arquivo deve ser .md ou .markdown",
            field="content_file",
            source="file",
        )

    if content_file.content_type not in ALLOWED_MARKDOWN_MIME_TYPES:
        logger.warning(
            "study_note.upload: content-type invalido filename={} content_type={}",
            filename,
            content_file.content_type,
        )
        raise BadRequestError(
            "Content-Type do arquivo inválido para markdown",
            field="content_file",
            source="file",
        )

    if content_file.size is not None and content_file.size > MAX_MARKDOWN_BYTES:
        logger.warning(
            "study_note.upload: arquivo acima do limite (pre-read) filename={} size_bytes={}",
            filename,
            content_file.size,
        )
        raise BadRequestError(
            "Arquivo excede o tamanho máximo permitido",
            field="content_file",
            source="file",
        )

    raw = await content_file.read()
    size_bytes = len(raw)
    logger.info(
        "study_note.upload: arquivo recebido filename={} extension={} content_type={} size_bytes={}",
        filename,
        extension,
        content_file.content_type,
        size_bytes,
    )

    if size_bytes > MAX_MARKDOWN_BYTES:
        logger.warning(
            "study_note.upload: arquivo acima do limite filename={} size_bytes={} max_bytes={}",
            filename,
            size_bytes,
            MAX_MARKDOWN_BYTES,
        )
        raise BadRequestError(
            "Arquivo excede o tamanho máximo permitido",
            field="content_file",
            source="file",
        )

    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning("study_note.upload: arquivo nao UTF-8 filename={}", filename)
        raise BadRequestError(
            "Arquivo Markdown deve estar em UTF-8",
            field="content_file",
            source="file",
        )

    if "\x00" in content:
        logger.warning("study_note.upload: conteudo com byte nulo filename={}", filename)
        raise BadRequestError(
            "Arquivo contém bytes inválidos",
            field="content_file",
            source="file",
        )

    if len(content) > MAX_MARKDOWN_CONTENT_LEN:
        logger.warning(
            "study_note.upload: conteudo acima do limite filename={} content_len={} max_len={}",
            filename,
            len(content),
            MAX_MARKDOWN_CONTENT_LEN,
        )
        raise BadRequestError(
            "Conteúdo excede 20000 caracteres",
            field="content_file",
            source="file",
        )

    checksum_sha256 = sha256(raw).hexdigest()
    line_count = content.count("\n") + (1 if content else 0)
    heading_count = sum(1 for line in content.splitlines() if line.lstrip().startswith("#"))

    logger.info(
        "study_note.upload: validado filename={} size_bytes={} lines={} headings={} checksum_prefix={}",
        filename,
        size_bytes,
        line_count,
        heading_count,
        checksum_sha256[:12],
    )

    return MarkdownUpload(
        filename=filename,
        extension=extension,
        content_type=content_file.content_type,
        size_bytes=size_bytes,
        checksum_sha256=checksum_sha256,
        line_count=line_count,
        heading_count=heading_count,
        content=content,
    )


async def get_markdown_content(
    markdown_upload: MarkdownUpload | None = Depends(get_markdown_upload),
) -> str | None:
    if markdown_upload is None:
        return None
    return markdown_upload.content


def parse_tags(tags: str | None = Form(None)) -> list[str]:
    if not tags:
        return []

    parsed: list[str] = []
    seen: set[str] = set()
    for raw_tag in tags.split(","):
        tag = raw_tag.strip()
        if not tag:
            continue
        if len(tag) > 30:
            raise BadRequestError(
                "Tag excede 30 caracteres",
                field="tags",
                source="form",
            )
        lowered = tag.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        parsed.append(tag)

    if len(parsed) > 20:
        raise BadRequestError(
            "Quantidade máxima de tags excedida",
            field="tags",
            source="form",
        )

    return parsed
