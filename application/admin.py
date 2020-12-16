from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SurveyInfo)
admin.site.register(Questions)
admin.site.register(Answers)