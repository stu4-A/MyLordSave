# careers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Home & registration
    path('', views.home_page, name='home'),
    path('register/', views.register_view, name='register'),

    # ----------------------------
    # Student URLs
    # ----------------------------
    path('list/', views.opportunity_list, name='opportunity_list'),
    path('opportunity/<int:pk>/', views.opportunity_detail, name='opportunity_detail'),
    path('opportunity/<int:pk>/save_toggle/', views.save_toggle, name='save_toggle'),
    path('opportunity/<int:pk>/apply/', views.apply_opportunity, name='apply_opportunity'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.edit_profile, name='edit_profile'),

    # ----------------------------
    # Lecturer URLs
    # ----------------------------
    path('manage/', views.manage_opportunities, name='manage_opportunities'),
    path('manage/create/', views.create_opportunity, name='create_opportunity'),
    path('manage/<int:pk>/edit/', views.edit_opportunity, name='edit_opportunity'),
    path('manage/<int:pk>/delete/', views.delete_opportunity, name='delete_opportunity'),
     path('manage/<int:pk>/applications/', views.view_applications, name='view_applications'),
]
