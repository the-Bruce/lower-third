from django.urls import path

from .views import CurrentState
urlpatterns = [
    path('session_state/', CurrentState.as_view()),
]