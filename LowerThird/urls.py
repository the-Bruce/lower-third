from django.urls import path

from .views import DisplayView
urlpatterns = [
    path('', DisplayView.as_view()),
]