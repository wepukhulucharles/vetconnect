from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from .models import *
# Register your models here.

class UserAdmin(GuardedModelAdmin):
    list_display = ['email', 'first_name', 'middle_name', 'surname']
    


class AppointmentAdmin(GuardedModelAdmin):
    list_display = ['client', 'vet', 'scheduled_date', 'scheduled_time_from', 'scheduled_time_to']

class ConsultationAdmin(GuardedModelAdmin):
    list_display = ['client', 'created', 'status', 'client_left_comment']
    
class ConsultationFeeAdmin(GuardedModelAdmin):
    list_display = ['client', 'vet', 'amount']
    
class ConsultationSatisfactionCommentAdmin(GuardedModelAdmin):
    list_display = ['user', 'vet', 'rate_vet']

admin.site.register(User, UserAdmin)
admin.site.register(Vet)
admin.site.register(EducationBackgroundDetail)
admin.site.register(Portfolio)
admin.site.register(VetComment)
admin.site.register(ConsultationSatisfactionComment, ConsultationSatisfactionCommentAdmin)
admin.site.register(Consultation, ConsultationAdmin)
admin.site.register(ConsultationFee, ConsultationFeeAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(VetClinic)

admin.site.register(VetUser)
admin.site.register(ReferralColleagueRequest)
admin.site.register(Notification)