from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from .validators import *
from guardian.shortcuts import assign_perm

# Create your models here.

# VALIDATORS START

# def validate_vet(value):
#     user = User.objects.get(email=value)
#     if user.role is not "VET":
#         raise ValidationError("Sorry the User isn't a vet")
#     return value

# VALIDATORS END


specialization_choices  = (
    ('Small Animals', 'SMALL ANIMALS'),
    ('Large Animals', 'LARGE ANIMALS'),
    ('Poultry', 'Poultry'),
    # ('SA && LA', 'SMALL ANIMALS AND LARGE ANIMALS')
)

salutation_choices = (
    ('Dr', 'DOCTOR'),
    ('Prof', 'PROFESSOR')
)

satisfaction_choices = (
    ('Satisfied', 'SATISFIED'),
    ('Not Satisfied', 'NOT SATISFIED')
)

services_choices = (
    ('Consultation', 'CONSULTATION'),
    ('Surgery', "SURGERY"),
    ('Clinical Services', 'CLINICAL SERVICES'),
    ('Obstetrical Services', 'OBSTETRICAL SERVICES'),
    ('Nutrition Analysis', 'NUTRITION ANALYSIS'),
    ('Feed Formulation', 'FEED FORMULATION')
    
)

education_qualifications_choices = (
    ('K.C.P.E', 'K.C.P.E'),
    ('K.C.S.E', 'K.C.S.E'),
    ('CERTIFICATE', 'CERTIFICATE'),
    ('DIPLOMA', 'DIPLOMA'),
    ('DEGREE', 'DEGREE'),
    ('MASTERS DEGREE', 'MASTERS DEGREE'),
    ('Phd', 'Phd')
)

request_status_choices = (
    ('ACCEPTED', 'ACCEPTED'),
    ('REJECTED', 'REJECTED'),
    ('PENDING', 'PENDING')
)


# FOR THIS CREATE A COUNTY MODEL CLASS THAT HOLDS ALL THE TOWNS IN THE COUNTY...MAYBE LOOK FOR AN API SYSTEM 
county_choices = (
    ('Mombasa', 'MOMBASA'),
    ('Nairobi', 'NAIROBI'),
    ('Trans-Nzoia', 'TRANS-NZOIA'),
    ('West Pokot', 'WEST POKOT'),
    ('Marakwet', 'MARAKWET'),
    ('Isiolo', 'ISIOLO'),
    ('Kericho', 'KERICHO'),
    ('Uasin-Gishu', 'UASIN-GISHU')

)

town_choices = (
    ('Kitale', 'KITALE'),
    ('Eldoret', 'ELDORET'),
    ('Mombasa', 'Mombasa'),
    ('Nairobi', 'NAIROBI'),
    ('Kericho', 'KERICHO'),
    ('Kapenguria', 'KAPENGURIA'),
    ('Iten', 'ITEN'),
    ('Isiolo', 'ISIOLO'),
)

sex_choices = (
    ('M', 'MALE'),
    ('F', 'FEMALE')
)

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"
        VET = "VET", "Vet"
        APP_USER = "APPUSER", "App User"
        
    base_role = Role.ADMIN
    
    role = models.CharField(max_length=12, choices=Role.choices, default="ADMIN")
    
    # name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    middle_name = models.CharField(max_length=20, null=True, blank=True)
    surname = models.CharField(max_length=20, null=True)
    bio = models.TextField(null=True)
    

    avatar = models.ImageField(null=True, default="avatar.svg")

    county = models.CharField(max_length=20, choices=county_choices, null=True)
    town = models.CharField(max_length=20, choices=town_choices, null=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        permissions = [("dg_edit_user_profile", "OLP Can Edit User Profile")]
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        else:
            # ADD USER TO A GROUP BASED ON THEIR ASSIGNED ROLE 
            if self.is_superuser is False:
                try:
                    group = Group.objects.get(name=self.role)
                except:
                    group = Group.objects.create(name=self.role)
                    
                self.groups.add(group)
                
                
                admins = User.objects.filter(is_superuser=True)
                for admin in admins:
                    assign_perm("dg_edit_user_profile", admin, self )
                    
                # if self.role == "ADMIN":
                #     message = "Welcome Admin!"
                # elif self.role == "APPUSER":
                #     message = "Thank You For Joining! Get Solutions For all Your Animal Needs!"
                # elif self.role == "VET":
                #     message = "Thank You For Joining! Happy Consulting Doc!"
                    
                # try:
                #     welcome_notification = Notification.objects.get(
                #         user = self,
                #         message = message
                #     )
                # except:
                #     welcome_notification = None
                 
                # if welcome_notification is None:   
                #     welcome_notification = Notification.objects.create(
                #         user = self,
                #         message = message
                #     )
                # else:
                #     welcome_notification = Notification.objects.create(
                #         user = self,
                #         message = f"You Successfully Updated Your User Profile!"
                #     )
                # welcome_notification.save()
                
            
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.surname.lower().capitalize() if self.surname else ""} {self.first_name.lower().capitalize() if self.first_name else ""} {self.middle_name.lower().capitalize() if self.middle_name else ""}"
    
class VetUserManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.VET)
    
    
class AppUserManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.APP_USER)
    
class VetUser(User):
    base_role = User.Role.VET
    vets = VetUserManager()
    class Meta:
        proxy = True
        
class AppUser(User):
    base_role = User.Role.APP_USER
    
    app_users = AppUserManager()
    
    class Meta:
        proxy = True
    
    

class Vet(models.Model):
    user = models.OneToOneField(VetUser, on_delete=models.CASCADE)
    salutation = models.CharField(max_length=5, choices=salutation_choices, default='Dr')
    start_practice = models.DateField()
    services = models.CharField(max_length=50, choices = services_choices, default='Clinical Services')
    vet_speciality = models.CharField(max_length=20, choices = specialization_choices)
    consultations = models.IntegerField(default=0)
    successfull_consultations = models.IntegerField(default=0)
    licence_no = models.CharField(max_length=20, unique=True)
    licence_expired = models.BooleanField(default=True)
    client_rating = models.IntegerField(default = 0)
    referral_colleagues = models.ManyToManyField(VetUser, related_name="referral_colleagues", blank=True)
    
    education_background = models.ManyToManyField('EducationBackgroundDetail', blank=True, related_name='vet_education_background')
    
    vet_portfolio = models.ManyToManyField('Portfolio', blank=True, related_name='vet_portfolio')
    consultation_fee = models.IntegerField(default = 1)

    class Meta:
        ordering = ['licence_expired', '-successfull_consultations',  '-client_rating', 'start_practice']
        
        
        
    def __str__(self):
        return f"{self.user.surname if self.user.surname else ""} {self.user.first_name if self.user.first_name else ""} {self.user.middle_name if self.user.middle_name else ""}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.start_practice = datetime.date.today()
        return super().save(*args, **kwargs)
    
class ReferralColleagueRequest(models.Model):
    requesting_vet = models.ForeignKey(VetUser, on_delete=models.CASCADE, related_name="requesting_vet")
    colleague_requested = models.ForeignKey(VetUser, on_delete=models.CASCADE, related_name="requested_colleague")
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.TextField(choices=request_status_choices, max_length=8, default="PENDING")
    
    class Meta:
        permissions = [("dg_view_colleague_request", "OLP Can View Colleague Request"), ("dg_confirm_colleague_request", "OLP Can Confirm Colleague Request")]
        ordering = ['-timestamp']
    
class EducationBackgroundDetail(models.Model):
    vet = models.ForeignKey(Vet, on_delete=models.SET_NULL, null=True)
    institution = models.CharField(max_length=50)
    joined = models.DateField()
    exited = models.DateField()
    qualification = models.CharField(max_length=20, choices=education_qualifications_choices)
    
    class Meta:
        ordering = ['-joined']
        
    def __str__(self):
        return f"{self.institution}, from {self.joined} to {self.exited} - {self.qualification}"
    
    
    
class Portfolio(models.Model):
    vet = models.ForeignKey(Vet, on_delete=models.SET_NULL, null=True, related_name="vet_associated_portfolio")
    workplace = models.CharField(max_length=50)
    county = models.CharField(max_length=20)
    town = models.CharField(max_length=20)
    location_description = models.TextField()
    role = models.CharField(max_length=50, null=True)
    worked_from = models.DateField()
    worked_to = models.DateField(null=True, blank=True)
    referees = models.TextField()
    
    class Meta:
        ordering = ['-worked_from']
        
    def __str__(self):
        return f"{self.role}, {self.workplace} {self.county} County  from {self.worked_from} to {self.worked_to if self.worked_to is not None else "Date"}"
    



class VetComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="commented_on_vet")
    body = models.TextField()
    is_consultation = models.BooleanField(default=False)
    # is_satisfaction_comment = models.BooleanField(default=False)
    reply_to = models.ForeignKey('VetComment', on_delete=models.SET_NULL, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [("dg_view_comment", "OLP Can View Comment")]
        ordering = ['-updated', '-created']
        
class ConsultationSatisfactionComment(VetComment):
    consultationobject = models.OneToOneField('Consultation', on_delete=models.CASCADE, null=True)
    # satisfied = models.CharField(max_length=15, choices=satisfaction_choices, default='Satisfied')
    rate_vet = models.IntegerField(default=0, validators = [rate_validation])
    
    class Meta:
        permissions = [('dg_view_consultationcomment', 'OLP Can View ConsultationComment'), ("dg_can_leave_comment_for_vet", "OLP Can Leave Comment For Vet")]
        ordering = ['-updated', '-created']
    
    
        



class Consultation(models.Model):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vet = models.ForeignKey(VetUser, on_delete=models.SET_NULL, null=True, related_name="vet_consulted")
    secondary_consultants = models.ManyToManyField(VetUser, related_name="vets_consulted")
    correspondents = models.ManyToManyField(VetComment, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    # client_satisfied = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=request_status_choices,  default='PENDING')
    client_left_comment = models.BooleanField(default=False)
    paid_for = models.BooleanField(default=False)
    
    # def get_corrected_created_time(self):
    #     pass
    
    
    
    #PATIENT DETAILS
    patient_name = models.CharField(max_length=20, blank=True)
    
    #SIGNALMENT
    species = models.CharField(max_length=20, null=True)
    age = models.SmallIntegerField(null=True)
    sex = models.CharField(max_length=2, choices=sex_choices, null=True)
    breed = models.CharField(max_length=20, null=True)
    color = models.CharField(max_length=20, null=True)
    
    #HISTORY OF ILLNESS
    history_of_illness = models.TextField(null=True)
    
    # THIS APPLIES FOR CLIENT AND VET WHO HAVE CONSULTED BEFORE 
    # CONSULTATION_NO = MODELS.INTEGERFIELD()

    class Meta:
        permissions = [("dg_view_consultation", "OLP Can View Consultation"), ("request_consultation", "Can Request Consultation"), ("approve_consultation", "Can Approve Consultation")]
        ordering = ['-created']

class ConsultationFee(models.Model):
    transaction_id = models.CharField(max_length=13, null=True)
    mpesa_transaction_code = models.CharField(max_length=10, default="xxxxxxxxxx")
    timestamp = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    consultation = models.OneToOneField('ConsultationFee', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators = [validate_amount])
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="client")
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="consulting_vet")
    payment_number = models.CharField(max_length = 13, validators = [validatePhoneNumber], null = True)

class Appointment(models.Model):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="appointment_vet")
    scheduled_date = models.DateField(validators = [validate_appointment_date])
    scheduled_time_from = models.TimeField(null=True)
    scheduled_time_to = models.TimeField(null=True)
    venue = models.CharField(max_length=20, blank=True, null=True)
    appointment_on = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=request_status_choices,  default='PENDING')
    
    class Meta:
        permissions = [("dg_view_appointment", "OLP Can View Appointment"), ("request_appointment", "Can Request Appointment"), ("approve_appointment", "Can Approve Appointment")]
        ordering = ['scheduled_date', 'scheduled_time_from']
    # reason for appointment
    
    # def __str__(self):
    #     return f"Vet: { self.vet.user.first_name } { self.vet.user.last_name }, Client: {self.client.first_name} {self.client.last_name}, {self.scheduled_date}  From: {self.scheduled_time_from} To: {self.scheduled_time_to}"


class VetClinic(models.Model):
    name = models.CharField(max_length=50)
    county = models.CharField(max_length=20)
    town = models.CharField(max_length=20)
    location_description  = models.TextField()
    specialization = models.CharField(max_length=20, choices=specialization_choices)
    services = models.CharField(max_length=50, choices=services_choices)
    images = models.ImageField(null=True, default = "avatar.svg", upload_to="posted_images")
    # ratings = models.SmallIntegerField(max_length=5)
    # client_comments
    def __str__(self):
        return f"{self.name} {self.town} {self.county } County "
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    # I NEED TO ADD DIFFERENT CATEGORIES FOR NOTIFICATION EE COLLEAGUE REQUESTS, REGISTRATION WELCOME MESSAGES ETC
    
    class Meta:
        permissions = [("dg_view_notification", "OLP Can View Notification")]
        ordering = ['-timestamp']
    
    
# ADD A MODEL TO REPORT SUSPICIOUS ACCOUNT ACTIVITY
    
    


