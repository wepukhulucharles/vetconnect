from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'


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
        widgets = {
            'start_practice': forms.DateInput(attrs={'class': 'form__input', 'type': 'date', 'placeholder': 'eg 2018'})
        }

        
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
    
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'eg University of Nairobi'}),
            'joined': forms.DateInput(attrs={'class': 'form__input', 'type': 'date', 'placeholder': 'eg 2018'}),
            'exited': forms.DateInput(attrs={'class': 'form__input', 'type': 'date', 'placeholder': 'eg 2023'}),
            'qualification': forms.Select(attrs={'class': 'form__input', 'placeholder': 'eg Degree in Veterinary Medicine'}),
        }

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['workplace', 'county', 'town', 'location_description', 'role', 'worked_from', 'worked_to', 'referees']   

        widgets = {
            'workplace': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Title'}),
            'county': forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Description'}),
            'town': forms.TextInput(attrs={'class': 'form__input'}),
            'location_description': forms.Textarea(attrs={'class': 'form__input'}),
            'worked_from': forms.DateInput(attrs={'class': 'form__input'}),
            'worked_to': forms.DateInput(attrs={'class': 'form__input'}),
            'role': forms.TextInput(attrs={'class': 'form__input'}),
            'referees': forms.Textarea(attrs={'class': 'form__input'})
        }


#Education formset
EducationFormSet = inlineformset_factory(
    Vet,
    EducationBackgroundDetail,
    form=EducationBackgroundDetailForm,
    extra=1,
    can_delete=True
)



        
class PortfolioForm(ModelForm):
    class Meta:
        model = Portfolio
        fields = ['workplace', 'county', 'town', 'location_description', 'role', 'worked_from', 'worked_to', 'referees']
        
#portfolio formset
PortfolioFormSet = inlineformset_factory(
    Vet,
    Portfolio,
    form=PortfolioForm,
    extra=1,
    can_delete=True
)

class consultationsatisfactioncommentform(ModelForm):
    class Meta:
        model = ConsultationSatisfactionComment
        fields = ['body', 'rate_vet']