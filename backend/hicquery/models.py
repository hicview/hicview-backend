from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import Q
import uuid
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


DATA_STORAGE_ROOT = 'data-dev'
# Set the storage file system 
fs = FileSystemStorage(location=os.path.join(settings.BASE_DIR,DATA_STORAGE_ROOT))


# Upload the specific file to path "<query_id>/<filename>"
def query_upload_path(instance, filename):
    return 'query_{0}/{1}'.format(instance.id, filename)

class HiCQuery(models.Model):
    _MAX_LENGTH = 500
    _ALLOWED_FILE_TYPES = (
        'bed_file',
        'matrix_file',
        'model_3d_file',
        'linker_file',
    )
    _ALLOWED_GENERATE_TARGET_TYPES = (
        'model_3d_file',
        'linker_file',
    )
    _MODEL_3D_FILE_GENERATE_SOURCE = (
        'matrix_file',
    )
    _LINKER_FILE_GENERATE_SOURCE = (
        'bed_file',
        'matrix_file',
        'model_3d_file',
    )
    id = models.UUIDField(
        _('unique id of the hic view session'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    title = models.CharField(
        _('title of the session'),
        max_length=_MAX_LENGTH)
    create_date = models.DateTimeField(
        _('create date'),
        default=timezone.now)
    bed_file = models.FileField(upload_to=query_upload_path, storage=fs)
    matrix_file = models.FileField(upload_to=query_upload_path, storage=fs)
    model_3d_file = models.FileField(upload_to=query_upload_path, storage=fs)
    linker_file = models.FileField(upload_to=query_upload_path, storage=fs)

#    bed_file = models.FileField( storage=fs)
#    matrix_file = models.FileField( storage=fs)
#    model_3d_file = models.FileField( storage=fs)
#    linker_file = models.FileField( storage=fs)

