from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'surname',  'email', 'password1', 'password2', 'county', 'town', 'bio', 'avatar']
        
# class VetUserCreationForm(UserCreationForm):
#     class Meta:
#         model = VetUser
#         fields = ['first_name', 'middle_name', 'surname',  'email', 'password1', 'password2']
        
        
class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar',  'bio']
        
class AppointmentForm(ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'vet', 'scheduled_date', 'scheduled_time_from', 'scheduled_time_to', 'venue']
        
class VetForm(ModelForm):
    class Meta:
        model = Vet
        fields = ['salutation', 'start_practice', 'services', 'vet_speciality','licence_no' ]
        
class ConsultationForm(ModelForm):
    class Meta:
        model = Consultation
        fields = ['client', 'vet']
        
class ConsultationFeeForm(ModelForm):
    class Meta:
        model = ConsultationFee
        fields = ['client', 'vet', 'amount', 'payment_number']
        
class EducationBackgroundDetailForm(ModelForm):
    class Meta:
        model = EducationBackgroundDetail
        fields = ['institution', 'joined', 'exited', 'qualification']
        
class PortfolioForm(ModelForm):
    class Meta:
        model = Portfolio
        fields = ['workplace', 'county', 'town', 'location_description', 'role', 'worked_from', 'worked_to', 'referees']
        
class consultationsatisfactioncommentform(ModelForm):
    class Meta:
        model = ConsultationSatisfactionComment
        fields = ['body', 'rate_vet']