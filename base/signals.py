
from django.shortcuts import render, redirect
from .models import EducationBackgroundDetail, Portfolio, VetUser, Vet, Appointment, Consultation, VetComment, ConsultationSatisfactionComment, ConsultationFee, ReferralColleagueRequest, Notification
from django.contrib.auth.models import Group

from django.db.models.signals import pre_save, post_save, m2m_changed
from django.db.models import Sum, Avg
from django.dispatch import receiver


from guardian.shortcuts import assign_perm


@receiver(post_save, sender=VetUser)
def createVetProfile(sender, instance, created, **kwargs):
    if created:
        vetprofile = Vet.objects.create(user=instance)
        vetprofile.save()
        
@receiver(post_save, sender=ReferralColleagueRequest)
def confirmReferralColleagueRequest(sender, instance, created, **kwargs):
    requesting_vet = instance.requesting_vet.vet
    colleague_requested = instance.colleague_requested.vet
    if created:
        colleague_requested_notification = Notification.objects.create(
            user = colleague_requested.user,
            message = f"You have a Colleague Request from {requesting_vet.user} "
        )
        colleague_requested_notification.save()
        
        assign_perm("dg_view_colleague_request", requesting_vet.user, instance)
        assign_perm("dg_view_colleague_request", colleague_requested.user, instance)
        assign_perm("dg_confirm_colleague_request", colleague_requested.user, instance)
    else:
        if instance.status == "ACCEPTED":
            if colleague_requested not in requesting_vet.referral_colleagues.all():
                requesting_vet.referral_colleagues.add(colleague_requested.user)
            if requesting_vet not in colleague_requested.referral_colleagues.all():
                colleague_requested.referral_colleagues.add(requesting_vet.user)
            accepted_notification = Notification.objects.create(
                user = requesting_vet.user,
                message = f"Your Colleague Request to {colleague_requested.user} has been accepted! "
            )
            accepted_notification.save()
            instance.delete()
            
        elif instance.status == "REJECTED":
            rejected_notification = Notification.objects.create(
                user = requesting_vet.user,
                message = f"Oops Your Colleague Request to {colleague_requested.user} has been rejected! "
            )
            rejected_notification.save()
            
            

@receiver(post_save, sender=Notification)
def assignNotificationPermissions(sender, instance, created, **kwargs):
    if created:
        assign_perm("dg_view_notification", instance.user, instance)

    

@receiver(post_save, sender=EducationBackgroundDetail)
def addEducationBackground(sender, instance, created, **kwargs):
    if created:
        vet = instance.vet
        vet.education_background.add(instance)
        vet.save()
        
@receiver(post_save, sender=Portfolio)
def buildPortfolio(sender, instance, created, **kwargs):
    if created:
        vet = instance.vet
        vet.vet_portfolio.add(instance)
        vet.save()
        
@receiver(post_save, sender=Appointment)
def assignAppointmentPerms(sender, instance, created, **kwargs):
    if created:
        assign_perm("dg_view_appointment", instance.client, instance)
        assign_perm("dg_view_appointment", instance.vet, instance)
        

# @receiver(post_save, sender=ConsultationFee)
# def requestConsultation(sender, instance, created, **kwargs):
#     if created:
#         new_consultation = Consultation.objects.create(
#             vet = instance.vet,
#             client = instance.client,
#             paid_for = True
#         )
#         new_consultation.save()
        
    
        
        
       
@receiver(post_save, sender=Consultation)
def assignConsultationPerms(sender, instance, created, **kwargs):
    consultations = Consultation.objects.filter(vet=instance.vet, client=instance.client)
    if created:
        vetuser = instance.vet
        consultation_fees = ConsultationFee.objects.filter(client=instance.client, vet=vetuser, amount__gt=0).order_by('-created')
            
        if consultation_fees.count() > 0:
            consultation_fee = consultation_fees.first()
            if consultation_fee.consultation is None and instance.paid_for is False:
                consultation_fee.consultation = instance
                consultation_fee.save()
        
        vet = Vet.objects.get(user=vetuser)
        vet.consultations += 1
        vet.save()
        assign_perm("dg_view_consultation", vetuser, instance)
        
        assign_perm("dg_view_consultation", instance.client, instance)
        if instance.status == "PENDING":
            try:
                consultation_request_notification = Notification.objects.get(
                    user = instance.vet,
                    message = f"You have a Consultation Request From {instance.client}"
                )
            except:
                consultation_request_notification = None
                
                
            if consultation_request_notification is None :
                consultation_request_notification = Notification.objects.create(
                    user = instance.vet,
                    message = f"You have a Consultation Request From {instance.client}"
                )
                consultation_request_notification.save()
                assign_perm("dg_view_notification", instance.vet, consultation_request_notification)
            #IN SITUATIONS WHERE THERE EXISTS SUCH A MESSAGE, CHECK HOW MANY CONSULTATIONS ARE THERE
                
    else:
        if instance.status == "ACCEPTED":
            try:
                consultation_accepted_notification = Notification.objects.get(
                    user = instance.client,
                    message = f"Your Consultation Request to {instance.vet.vet.salutation} {instance.vet} has been Accepted!"
                )
            except:
                consultation_accepted_notification = None
                
           
            if consultation_accepted_notification is None:
                consultation_accepted_notification = Notification.objects.create(
                    user = instance.client,
                    message = f"Your Consultation Request to {instance.vet.vet.salutation} {instance.vet} has been Accepted!"
                )
                consultation_accepted_notification.save()
                assign_perm("dg_view_notification", instance.client, consultation_accepted_notification)
        elif instance.status == "REJECTED":
            try:
                consultation_rejected_notification = Notification.objects.get(
                    user = instance.client,
                    message = f"Oops! Your Consultation Request to {instance.vet.vet.salutation} {instance.vet} has been Rejected!"
                )
            except:
                consultation_rejected_notification = None
            if consultation_rejected_notification is None:
                consultation_rejected_notification = Notification.objects.create(
                    user = instance.client,
                    message = f"Oops! Your Consultation Request to {instance.vet.vet.salutation} {instance.vet} has been Rejected!"
                )
                consultation_rejected_notification.save()
                assign_perm("dg_view_notification", instance.client, consultation_rejected_notification)
            
@receiver(m2m_changed, sender=Consultation.secondary_consultants.through)
def assignConsultationPermsToVets(sender, instance, action, **kwargs):
    if action == "post_add":
        vetusers = instance.secondary_consultants.all()
        for vetuser in vetusers:
            # FIND A WAY TO FIND ONE WITHOUT PERMISSIONS FOR THIS CONSULTATION
            assign_perm("dg_view_consultation", vetuser, instance)
        
        
        
        
@receiver(post_save, sender=VetComment)
def assignCommentPerms(sender, instance, created, **kwargs):
    if created:
        assign_perm("dg_view_comment", instance.user, instance)
        assign_perm("dg_view_comment", instance.vet, instance)
        
@receiver(post_save, sender=ConsultationSatisfactionComment)
def consultationcomment(sender, instance, created, **kwargs):
    if created:
        consultation = instance.consultationobject
        vetuser = consultation.vet
        vet = Vet.objects.get(user=vetuser)
        consultation.client_left_comment = True
        vet_average_ratings = ConsultationSatisfactionComment.objects.filter(vet=vet.user).aggregate(avg = Avg('rate_vet'))['avg']
        vet.client_rating = vet_average_ratings
        if instance.rate_vet > 5:
            vet.successfull_consultations += 1
        vet.save()
        # if instance.satisfied == 'Satisfied':
        #     consultation.client_satisfied = True
        #     consultation.save()
        #     vet.successfull_consultations += 1
        #     vet.save()
        # elif instance.satisfied == 'Not Satisfied':
        #     consultation.client_satisfied = False
        #     consultation.save()
        # ASSIGN OBJECT PERMISSIONS
        assign_perm("dg_view_consultationcomment", instance.user, instance)
        assign_perm("dg_view_consultationcomment", instance.vet, instance)
    
        
        
        

        
        

