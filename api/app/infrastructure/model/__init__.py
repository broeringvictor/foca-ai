from sqlalchemy.orm import registry

# Registry/metadata central para toda a camada de models.
table_registry = registry()


# Ao adicionar novos models, inclua-os aqui para adicionar aos metadados.
# TODO: METADADOS DOS MODELS