from enum import StrEnum


class LawArea(StrEnum):
    """Áreas do direito cobradas na 1ª fase do Exame de Ordem (OAB)."""

    CONSTITUTIONAL = "direito_constitucional"
    HUMAN_RIGHTS = "direitos_humanos"
    ETHICS = "etica_profissional"
    PHILOSOPHY_OF_LAW = "filosofia_do_direito"
    INTERNATIONAL = "direito_internacional"
    TAX = "direito_tributario"
    ADMINISTRATIVE = "direito_administrativo"
    ENVIRONMENTAL = "direito_ambiental"
    CIVIL = "direito_civil"
    CONSUMER = "direito_do_consumidor"
    CHILD_AND_ADOLESCENT = "eca"
    BUSINESS = "direito_empresarial"
    CRIMINAL = "direito_penal"
    CIVIL_PROCEDURE = "direito_processual_civil"
    CRIMINAL_PROCEDURE = "direito_processual_penal"
    LABOR = "direito_do_trabalho"
    LABOR_PROCEDURE = "direito_processual_do_trabalho"
    SOCIAL_SECURITY = "direito_previdenciario"
    FINANCIAL = "direito_financeiro"
