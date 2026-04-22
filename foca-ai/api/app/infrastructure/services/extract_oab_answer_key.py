import io
import re
from typing import Dict

import pdfplumber
from loguru import logger

from app.domain.enums.alternatives import Alternative


class ExtractOABAnswerKeyService:
    """Extrai o gabarito de um PDF oficial da FGV/OAB."""

    # Regex para encontrar o bloco de um tipo específico de prova
    # Ex: "45º EXAMEDE ORDEM - PROVA TIPO 1"
    TYPE_HEADER_RE = re.compile(
        r"(\d+)[º°]?\s*EXAMEDE\s*ORDEM\s*-\s*PROVA\s*TIPO\s*(\d+)", re.IGNORECASE
    )

    def extract(self, pdf_bytes: bytes, exam_type: int = 1) -> Dict[int, Alternative]:
        """
        Extrai o gabarito para um tipo de prova específico.
        Retorna um dicionário {numero_questao: alternativa_correta}.
        """
        logger.info("extract.answer_key: start exam_type={}", exam_type)
        
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # Geralmente o gabarito definitivo está na primeira página
            text = pdf.pages[0].extract_text() or ""
            
        if not text:
            logger.error("extract.answer_key: no_text_found")
            raise ValueError("Não foi possível extrair texto do PDF do gabarito")

        return self._parse_text(text, exam_type)

    def _parse_text(self, text: str, target_type: int) -> Dict[int, Alternative]:
        # Divide o texto pelos cabeçalhos de "PROVA TIPO X"
        segments = self.TYPE_HEADER_RE.split(text)
        # O split com grupos no regex retorna: [texto_antes, edicao, tipo, texto_depois, ...]
        
        target_content = ""
        for i in range(1, len(segments), 3):
            edition = segments[i]
            exam_type = int(segments[i+1])
            content = segments[i+2]
            
            if exam_type == target_type:
                target_content = content
                logger.info("extract.answer_key: found_type_block edition={} type={}", edition, exam_type)
                break
                
        if not target_content:
            logger.error("extract.answer_key: target_type_not_found type={}", target_type)
            raise ValueError(f"Bloco do Gabarito Tipo {target_type} não encontrado no PDF")

        # Agora extraímos os números e as letras
        # O formato é:
        # 1 2 3 ... 20
        # A B C ... D
        # 21 22 ... 40
        # ...
        
        # Vamos pegar todas as sequências de letras isoladas (A, B, C, D) 
        # e números que aparecem no bloco.
        
        # Filtra apenas o que parece ser gabarito (letras A-D isoladas e números)
        all_tokens = re.findall(r"\b([A-D]|\d{1,2})\b", target_content)
        
        numbers = []
        answers = []
        
        for token in all_tokens:
            if token.isdigit():
                numbers.append(int(token))
            else:
                answers.append(token)
                
        if len(numbers) != len(answers):
            logger.warning(
                "extract.answer_key: mismatch numbers={} answers={}", 
                len(numbers), len(answers)
            )
            # Tenta recuperar pareando os primeiros 80 (ou o que houver de menor)
            limit = min(len(numbers), len(answers))
            numbers = numbers[:limit]
            answers = answers[:limit]

        result = {
            num: Alternative(ans) 
            for num, ans in zip(numbers, answers)
        }
        
        logger.info("extract.answer_key: success total={}", len(result))
        return result
