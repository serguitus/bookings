"""
reservas utils
"""
from django.core.exceptions import ValidationError


ERROR_MODEL_NOT_FOUND = 'Invalid %s PK'


def load_locked_model_object(pk, model_class, allow_empty_pk=True):
    db_model_object = None
    # verify if not new
    if pk:
        # load agency_invoice from db
        db_model_object = model_class.objects.select_for_update().get(pk=pk)
        if not db_model_object:
            raise ValidationError(ERROR_MODEL_NOT_FOUND % model_class.__name__)
    elif not allow_empty_pk:
        raise ValidationError(ERROR_MODEL_NOT_FOUND % model_class.__name__)
    return db_model_object
