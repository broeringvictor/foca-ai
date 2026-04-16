from enum import StrEnum


class LawArea(StrEnum):
    """Áreas do direito cobradas na 1ª fase do Exame de Ordem (OAB)."""

    CONSTITUTIONAL = "constitutional"
    HUMAN_RIGHTS = "human_rights"
    ETHICS = "ethics"
    PHILOSOPHY_OF_LAW = "philosophy_of_law"
    INTERNATIONAL = "international"
    TAX = "tax"
    ADMINISTRATIVE = "administrative"
    ENVIRONMENTAL = "environmental"
    CIVIL = "civil"
    CONSUMER = "consumer"
    CHILD_AND_ADOLESCENT = "child_and_adolescent"
    BUSINESS = "business"
    CRIMINAL = "criminal"
    CIVIL_PROCEDURE = "civil_procedure"
    CRIMINAL_PROCEDURE = "criminal_procedure"
    LABOR = "labor"
    LABOR_PROCEDURE = "labor_procedure"
    SOCIAL_SECURITY = "social_security"
    FINANCIAL = "financial"
