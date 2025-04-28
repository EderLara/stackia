from django.urls import path
from .views import PrediccionView

urlpatterns = [
    path('', PrediccionView.as_view(), name='prediccion'),
]