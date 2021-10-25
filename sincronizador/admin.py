from django.contrib import admin

# Register your models here.
from .models import Sinc_Config, Sinc_log, Sinc_Accs, Sinc_open, Sinc_view

admin.site.register(Sinc_Config)
admin.site.register(Sinc_log)
admin.site.register(Sinc_Accs)
admin.site.register(Sinc_open)
admin.site.register(Sinc_view)