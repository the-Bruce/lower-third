from django.urls import path

from .views import CurrentState, UpdateState, CurrentStateRSS, CurrentStateListRSS
urlpatterns = [
    path('session_state/', CurrentState.as_view()),
    path('update/', UpdateState.as_view()),
    path('session_state/rss/<slug:session>/', CurrentStateRSS()),
    path('session_state/rss/<slug:session>/all/', CurrentStateListRSS())

]