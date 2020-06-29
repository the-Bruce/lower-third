from django.urls import path

from .views import CurrentState, UpdateState
urlpatterns = [
    path('get/', CurrentState.as_view()),
    path('update/', UpdateState.as_view()),
]