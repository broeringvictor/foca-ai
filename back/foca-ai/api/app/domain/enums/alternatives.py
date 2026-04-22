from enum import StrEnum


class Alternative(StrEnum):
    """Alternativa de resposta de uma questão objetiva.

    OAB utiliza 4 alternativas (A-D).
    """

    A = "A"
    B = "B"
    C = "C"
    D = "D"
