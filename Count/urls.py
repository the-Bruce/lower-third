from django.urls import path

from .views import MainView, GraphView, GraphTodayView

app_name = 'count'
urlpatterns = [
    path('', MainView.as_view(), name='main'),
    path('graph/<int:year>/<int:month>/<int:day>/', GraphView.as_view(), name='graph'),
    path('graph/', GraphTodayView.as_view(), name='graph_today'),
]