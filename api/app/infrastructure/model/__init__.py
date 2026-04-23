from sqlalchemy.orm import registry

# Registry/metadata central para toda a camada de models, dessa forma preciso apenas importar do init.
table_registry = registry()


# Ao adicionar novos models, inclua-os aqui para adicionar aos metadados.
from . import user_model as user_model  # noqa: E402
from . import exam_model as exam_model  # noqa: E402
from . import question_model as question_model  # noqa: E402
from . import study_note_model as study_note_model  # noqa: E402
from . import question_detail_view as question_detail_view  # noqa: E402
from . import exam_stats_view as exam_stats_view  # noqa: E402
from . import study_model as study_model  # noqa: E402
