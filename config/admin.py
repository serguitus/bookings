from django.contrib import admin

# Register your models here.
from .models import Agency
from .models import Office
from .models import BoardType
admin.site.register(Agency)
admin.site.register(Office)
admin.site.register(BoardType)
