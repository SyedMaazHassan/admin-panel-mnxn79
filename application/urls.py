from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('admin-panel', views.SurveyList.as_view(), name="admin-panel"),
    path('add-survey/',views.surveyform,name='add-survey'),
    path('survey-response/<int:pk>/',views.checkresponses,name='responses'),
    
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
