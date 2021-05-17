from django.urls import path
import Recommendation.views as views

urlpatterns = [
    path('recommend/', views.api_recommend, name = 'api_recommend')
]