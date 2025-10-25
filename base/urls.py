from django.urls import path
from . import views



urlpatterns = [
    path('login/', views.loginPage, name="login-page"),
    path('logout/', views.logoutUser, name="logout-page"),
    path('register/', views.registeruser, name="register"),
    path('update-user/', views.updateUser, name="update-user"),


    path('', views.home, name='home'),
    path('profile/<str:pk>/', views.vetprofile, name='profile'),
    path('register-vet/', views.registerVet, name="register-vet"),
    path('colleague_requests/', views.colleagueRequests, name="colleague_requests"),
    path('colleague_request/<str:pk>/', views.referralColleagueRequest, name="colleague_request"),
    path('confirm_colleague_request/<str:pk>/', views.confirmReferralColleagueRequest, name="confirm-colleague-request"),
    
    path('consultation/<str:pk>/', views.consultation, name='consultation'),
    path('consultations/', views.consultations, name='consultations'),
    path('stk-status/', views.stk_status_view, name = 'stk_status'),
    path('request-consultation', views.requestConsultation, name='request-consultation'),
    path('confirm-consultation/<str:pk>/', views.confirmConsultation, name='confirm-consultation'),
    path('add-consultant/<str:pk>/', views.addConsultant, name="add-consultant"),
    path('appointments/', views.appointments, name='appointments'),
    
    path('delete-comment/<str:pk>/', views.deleteComment, name="delete-comment"),
    path('leave-comment/<str:pk>/', views.leaveCommentForVet, name='leave-comment-for-vet'),
    
    path('create-appointment/', views.createAppointment, name='create-appointment'),
    path('read-notification/<str:pk>/', views.markNotificationRead, name="mark-notification-read"),
    
    path('clinics/', views.clinics, name="clinics")

]