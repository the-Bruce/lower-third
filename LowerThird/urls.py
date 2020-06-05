from django.urls import path

from .views import DisplayView, ControlView
urlpatterns = [
    path('', DisplayView.as_view()),
    path('control/<slug:session>/', ControlView.as_view()),
]