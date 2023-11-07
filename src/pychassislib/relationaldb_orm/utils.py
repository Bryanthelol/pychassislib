from datetime import datetime
from sqlalchemy.orm import class_mapper


def model_to_dict(model):
    if not model:
        return
    model_dict = {}
    for key, column in class_mapper(model.__class__).c.items():
        if isinstance(getattr(model, key), datetime):
            model_dict[column.name] = str(getattr(model, key))
        else:
            model_dict[column.name] = getattr(model, key, None)
    return model_dict