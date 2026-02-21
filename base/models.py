from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.utils import timezone
from .validators import *
from .constants import *
from guardian.shortcuts import assign_perm
import datetime
from .managers import (OptimizedConsultationManager, OptimizedAppointmentManager, 
                       OptimizedNotificationManager)

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STAFF = "STAFF", "Staff"
        VET = "Vets", "Veterinarians"
        APP_USER = "Users", "Regular Users"
        
    base_role = Role.ADMIN
    
    role = models.CharField(max_length=12, choices=Role.choices, default="ADMIN")
    
    # name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    middle_name = models.CharField(max_length=20, null=True, blank=True)
    surname = models.CharField(max_length=20, null=True)
    bio = models.TextField(null=True)
    

    avatar = models.ImageField(null=True, default="avatar.svg")

    county = models.CharField(max_length=20, choices=COUNTY_CHOICES, null=True)
    town = models.CharField(max_length=20, choices=TOWN_CHOICES, null=True)


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
                except Group.DoesNotExist:
                    group = Group.objects.create(name=self.role)
                    
                self.groups.add(group)
                
                
                admins = User.objects.filter(is_superuser=True)
                for admin in admins:
                    assign_perm("dg_edit_user_profile", admin, self )
                
            
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
    salutation = models.CharField(max_length=5, choices=SALUTATION_CHOICES, default='Dr')
    start_practice = models.DateField()
    services = models.CharField(max_length=50, choices=SERVICES_CHOICES, default='Clinical Services')
    vet_speciality = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES, db_index=True)
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
        indexes = [
            models.Index(fields=['licence_expired', '-client_rating'], name='vet_active_rating_idx'),
        ]
        
        
        
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
    status = models.TextField(choices=REQUEST_STATUS_CHOICES, max_length=8, default="PENDING")
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        permissions = [("dg_view_colleague_request", "OLP Can View Colleague Request"), ("dg_confirm_colleague_request", "OLP Can Confirm Colleague Request")]
        ordering = ['-timestamp']
        constraints = [
            models.UniqueConstraint(
                fields=['requesting_vet', 'colleague_requested'],
                condition=models.Q(status='PENDING'),
                name='unique_pending_colleague_request'
            )
        ]
    
class EducationBackgroundDetail(models.Model):
    vet = models.ForeignKey(Vet, on_delete=models.SET_NULL, null=True)
    institution = models.CharField(max_length=50)
    joined = models.DateField()
    exited = models.DateField()
    qualification = models.CharField(max_length=20, choices=EDUCATION_QUALIFICATIONS_CHOICES)
    
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
    rate_vet = models.IntegerField(default=0, validators = [rate_validation])
    
    # NEW: Enhanced review system
    review_text = models.TextField(null=True, blank=True)
    vet_response = models.TextField(null=True, blank=True)
    vet_response_date = models.DateTimeField(null=True, blank=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(null=True, blank=True)
    
    class Meta:
        permissions = [('dg_view_consultationcomment', 'OLP Can View ConsultationComment'), ("dg_can_leave_comment_for_vet", "OLP Can Leave Comment For Vet")]
        ordering = ['-updated', '-created']
    
    
        



class Consultation(models.Model):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vet = models.ForeignKey(VetUser, on_delete=models.SET_NULL, null=True, related_name="vet_consulted")
    secondary_consultants = models.ManyToManyField(VetUser, related_name="vets_consulted")
    correspondents = models.ManyToManyField(VetComment, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    status = models.CharField(max_length=15, choices=CONSULTATION_STATUS_CHOICES, default='PENDING', db_index=True)
    client_left_comment = models.BooleanField(default=False)
    paid_for = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # PATIENT DETAILS
    patient_name = models.CharField(max_length=20, blank=True)
    
    # SIGNALMENT
    species = models.CharField(max_length=20, null=True)
    age = models.SmallIntegerField(null=True)
    sex = models.CharField(max_length=2, choices=SEX_CHOICES, null=True)
    breed = models.CharField(max_length=20, null=True)
    color = models.CharField(max_length=20, null=True)
    
    # HISTORY OF ILLNESS
    history_of_illness = models.TextField(null=True)

    class Meta:
        permissions = [("dg_view_consultation", "OLP Can View Consultation"), ("request_consultation", "Can Request Consultation"), ("approve_consultation", "Can Approve Consultation")]
        ordering = ['-created']
        indexes = [
            models.Index(fields=['status', '-created'], name='consult_status_created_idx'),
        ]

class ConsultationFee(models.Model):
    transaction_id = models.CharField(max_length=13, null=True)
    mpesa_transaction_code = models.CharField(max_length=10, default="xxxxxxxxxx")
    timestamp = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    consultation = models.OneToOneField('Consultation', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators = [validate_amount])
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="client")
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="consulting_vet")
    payment_number = models.CharField(max_length = 13, validators = [validatePhoneNumber], null = True)
    
    # NEW: Enhanced payment tracking
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    refunded_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(null=True, blank=True)

class Appointment(models.Model):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="appointment_vet")
    scheduled_date = models.DateField(validators = [validate_appointment_date])
    scheduled_time_from = models.TimeField(null=True)
    scheduled_time_to = models.TimeField(null=True)
    venue = models.CharField(max_length=20, blank=True, null=True)
    appointment_on = models.BooleanField(default=True)
    status = models.CharField(max_length=15, choices=APPOINTMENT_STATUS_CHOICES, default='PENDING', db_index=True)
    buffer_time_minutes = models.IntegerField(default=30)
    
    class Meta:
        permissions = [("dg_view_appointment", "OLP Can View Appointment"), ("request_appointment", "Can Request Appointment"), ("approve_appointment", "Can Approve Appointment")]
        ordering = ['scheduled_date', 'scheduled_time_from']
        indexes = [
            models.Index(fields=['status', 'scheduled_date'], name='appt_status_scheduled_idx'),
        ]


class VetClinic(models.Model):
    name = models.CharField(max_length=50)
    county = models.CharField(max_length=20)
    town = models.CharField(max_length=20)
    location_description  = models.TextField()
    specialization = models.CharField(max_length=20, choices=SPECIALIZATION_CHOICES)
    services = models.CharField(max_length=50, choices=SERVICES_CHOICES)
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
    
    # NEW: Enhanced notification system
    category = models.CharField(max_length=20, choices=NOTIFICATION_CATEGORY_CHOICES, default='SYSTEM')
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        permissions = [("dg_view_notification", "OLP Can View Notification")]
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'is_read', '-timestamp'], name='notif_user_read_ts_idx'),
        ]


# NEW MODELS FOR ENHANCED FUNCTIONALITY

class VetAvailability(models.Model):
    """Store vet working hours and availability"""
    vet = models.ForeignKey(Vet, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('vet', 'day_of_week')
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.vet} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class AuditLog(models.Model):
    """Track all critical actions for compliance and debugging"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=AUDIT_ACTION_CHOICES)
    model_name = models.CharField(max_length=50, db_index=True)
    object_id = models.IntegerField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id'], name='action_log_model_obj_idx'),
            models.Index(fields=['user', 'timestamp'], name='action_log_user_ts_idx'),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.model_name}#{self.object_id} by {self.user} at {self.timestamp}"