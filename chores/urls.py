from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='chores/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('setup-household/', views.create_or_join_household, name='create_or_join_household'),
    path('chore/<int:pk>/complete/', views.mark_chore_complete, name='mark_chore_complete'),
    path('chore/<int:pk>/review/', views.review_chore, name='review_chore'),
]