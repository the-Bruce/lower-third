from django.urls import path

from .views import DisplayView, ControlView, SessionView

app_name = "lower_third"
urlpatterns = [
    path('', DisplayView.as_view()),
    path('control/', SessionView.as_view(), name='session_select'),
    path('control/<slug:session>/', ControlView.as_view(), name='control'),
]