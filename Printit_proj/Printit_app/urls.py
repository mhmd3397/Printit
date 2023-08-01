from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('home_authenticated/', views.home_authenticated,
         name='home_authenticated'),
    path('my-ideas/', views.my_ideas, name='my_ideas'),
    path('create-idea/', views.create_idea, name='create_idea'),
    path('logout/', views.logout, name='logout'),
    path('user/<int:user_id>/', views.user_ideas, name='user_ideas'),
    path('idea/<int:idea_id>/', views.view_idea, name='view_idea'),
    path('idea/<int:idea_id>/edit/', views.edit_idea, name='edit_idea'),
    path('idea/<int:idea_id>/delete/', views.delete_idea, name='delete_idea'),
]
