from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('skills/', views.skills_view, name='skills'),
    path('profile/', views.profile_view, name='profile'),
    path('resume/', views.resume_view, name='resume'),
    
    path('jobs/', views.job_list_view, name='job_list'),
    path('jobs/create/', views.job_create_view, name='job_create'),
    path('jobs/<int:job_id>/', views.job_detail_view, name='job_detail'),
    
    path('applicants/', views.applicants_view, name='applicants'),
    path('applicants/job/<int:job_id>/', views.applicants_view, name='applicants_by_job'),
    path('my-applications/', views.applications_view, name='my_applications'),
]
