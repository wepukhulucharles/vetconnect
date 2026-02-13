from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

import json
import requests
import base64

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import  *
from django.conf import settings

# mpesa
from mpesa.mpesa.core import MpesaClient

from guardian.shortcuts import get_objects_for_user

from collections import Counter


# Helper Functions 
today = datetime.date.today()
time = datetime.time()


from mpesa.mpesa import utils

app_users = AppUser.app_users.all()
vets = VetUser.vets.all()

# START MPESA 

# Generate M-Pesa access token
consumer_key = settings.MPESA_CONSUMER_KEY
consumer_secret = settings.MPESA_CONSUMER_SECRET
mpesa_base_url = settings.MPESA_BASE_URL

def generate_access_token():
    try:
        credentials = f"{consumer_key}:{consumer_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }
        response = requests.get(
            f"{mpesa_base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
        ).json()

        if "access_token" in response:
            return response["access_token"]
        else:
            raise Exception("Access token missing in response.")

    except requests.RequestException as e:
        raise Exception(f"Failed to connect to M-Pesa: {str(e)}")

def stk_push_success(amount, phone_number, transaction_id):
    cl = MpesaClient()
    stk_push_callback_url = 'https://api.darajambili.com/express-payment'
    account_reference = 'FindmyVet'
    transaction_desc = transaction_id
    callback_url = stk_push_callback_url
    r = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    return r


# Query STK Push status
def query_stk_push(checkout_request_id):
    print("Quering...")
    MPESA_SHORTCODE = settings.MPESA_EXPRESS_SHORTCODE
    MPESA_PASSKEY = settings.MPESA_PASSKEY

    try:
        token = generate_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (MPESA_SHORTCODE + MPESA_PASSKEY + timestamp).encode()
        ).decode()

        request_body = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        response = requests.post(
            f"{MPESA_BASE_URL}/mpesa/stkpushquery/v1/query",
            json=request_body,
            headers=headers,
        )
        print(response.json())
        return response.json()

    except requests.RequestException as e:
        print(f"Error querying STK status: {str(e)}")
        return {"error": str(e)}


# View to query the STK status and return it to the frontend
def stk_status_view(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            checkout_request_id = data.get('checkout_request_id')
            print("CheckoutRequestID:", checkout_request_id)

            # Query the STK push status using your backend function
            status = query_stk_push(checkout_request_id)

            # Return the status as a JSON response
            return JsonResponse({"status": status})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def get_transaction_id():
    todays_transactions_count = ConsultationFee.objects.filter(created = today).count()
    year = today.year
    month = today.month
    day = today.day 
    return f"{year} + {month} + {day} + {todays_transactions_count + 1}"

# END MPESA
    

def sideMenuComponents(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    all_vets = Vet.objects.all()
    all_vets_count = all_vets.count

    user_county = request.user.county
    user_town = request.user.town

    # vets user may know

    known_vets = all_vets.filter(
        Q(user__county = user_county)|
        Q(user__town = user_town)
    )

    vets = all_vets.filter(
        Q(user__first_name__icontains=q) |
        Q(user__last_name__icontains=q)|
        Q(user__username__icontains = q) |
        Q(vet_speciality__icontains = q)
    )
    
    consultations = get_objects_for_user(
        request.user,
        "base.dg_view_consultation",
        klass = Consultation
    )
    
    if request.user.role == "APPUSER":
        consultations_count_with_vets = Counter([consultation.vet if consultation.client == request.user else '' for consultation in consultations.filter(status = "ACCEPTED")])
        print(consultations_count_with_vets)
    else:
        consultations_count_with_vets = 0
            
    pending_consultations = consultations.filter(status = "PENDING")
    # consultations = Consultation.objects.filter(
    #     Q(client__email = request.user.email)|
    #     Q(vet__user__email = request.user.email)
    # )
    
    appointments = get_objects_for_user(
        request.user,
        "base.dg_view_appointment",
        klass = Appointment
    ).filter(
        Q(scheduled_date__gte=today) &
        Q(scheduled_time_from__gte=time)
    ).filter(
        status = "PENDING"
    )
    
    colleague_requests = get_objects_for_user(
        request.user,
        "base.dg_view_colleague_request",
        klass = ReferralColleagueRequest
    )
    
    # NO NEED TO FILTER BY STATUS BECAUSE ALL ACCEPTED REQUESTS ARE DELETED FROM THE DATABASE
    pending_rejected_colleague_requests = colleague_requests.filter(
        # THIS IS IMPORTANT TO CHECK WHETHER HE/SHE HAS SENT OR RECEIVED A REQUEST ALREADY 
        Q(requesting_vet = request.user)|
        Q(colleague_requested = request.user)
    )
    
    # TO GET A LIST OF VETS A VET USER HAS COLLEAGUE REQUESTED AND THOSE HE / SHE HAS BEEN COLLEAGUE REQUESTED 
    pending_rejected_colleague_requests = [colleague_request.colleague_requested if colleague_request.requesting_vet == request.user else colleague_request.requesting_vet for colleague_request in pending_rejected_colleague_requests ]
    

    colleague_requests_count = colleague_requests.filter(
        colleague_requested = request.user,
        status = "PENDING"
    ).count()

    # appointments = Appointment.objects.filter(
    #     Q(client__email = request.user.email)|
    #     Q(vet__user__email = request.user.email)
    # )
    
    clinics = VetClinic.objects.all()
    
    vets_count = vets.count
    pending_consultations_count = pending_consultations.count
    appointments_count = appointments.count
    clinics_count = clinics.count
    
    # user_notifications = request.user.notification_set.filter(is_read=False)
    user_notifications = get_objects_for_user(
        request.user,
        "dg_view_notification",
        klass = Notification
    ).filter(
        is_read = False
    )
    print(f"notifications: {user_notifications}")

    return {
        'vets':vets,
        'known_vets':known_vets,
        # 'consultations':consultations,
        'vets_count':vets_count,
        'all_vets_count':all_vets_count,
        'consultations_with_vet':consultations_count_with_vets,
        'pending_consultations_count':pending_consultations_count,
        'appointments_count':appointments_count,
        'clinics_count':clinics_count,
        'notifications':user_notifications,
        'colleague_requests_count':colleague_requests_count,
        'pending_rejected_colleague_requests':pending_rejected_colleague_requests
        
    }
# End Helper Functions


# Create your views here.

@login_required(login_url='login-page')
def home(request):
    # q = request.GET.get('q') if request.GET.get('q') != None else ''
    # all_vets = Vet.objects.all()
    # all_vets_count = all_vets.count

    # user_county = request.user.county
    # user_town = request.user.town

    # # vets user may know

    # known_vets = all_vets.filter(
    #     Q(user__county = user_county)|
    #     Q(user__town = user_town)
    # )

    # vets = all_vets.filter(
    #     Q(user__first_name__icontains=q) |
    #     Q(user__last_name__icontains=q)|
    #     Q(user__username__icontains = q) |
    #     Q(vet_speciality__icontains = q)
    # )

    # consultations = Consultation.objects.filter(
    #     Q(client__email = request.user.email)|
    #     Q(vet__user__email = request.user.email)
    # )

    # appointments = Appointment.objects.filter(
    #     Q(client__email = request.user.email)|
    #     Q(vet__user__email = request.user.email)
    # )
    

    # # vets = Vet.objects.all()
    # vets_count = vets.count
    # consultations_count = consultations.count
    # appointments_count = appointments.count
    
    # CHECKING WHETHER USER IS A VETERINARIAN 
    # vet_profiles = Vet.objects.all().only('')
    # print(vet_profiles)
    
    
    
    context = sideMenuComponents(request)
    
    
        
    
    
    
        
    
        
    # context = {
    #     'vets':vets,
    #     'known_vets':known_vets,
    #     # 'consultations':consultations,
    #     'vets_count':vets_count,
    #     'all_vets_count':all_vets_count,
    #     'consultations_count':consultations_count,
    #     'appointments_count':appointments_count
    # }
    return render(request, 'base/home.html', context)

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login-page')

def registeruser(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, request.FILES)
        print(form.errors)
        if form.is_valid():
            user = AppUser.objects.create_user(
                username = form.cleaned_data.get("email"),
                first_name = form.cleaned_data.get("first_name"),
                middle_name = form.cleaned_data.get("middle_name"),
                surname = form.cleaned_data.get("surname"),
                email = form.cleaned_data.get("email"),
                county = form.cleaned_data.get("county"),
                town = form.cleaned_data.get("town"),
                bio = form.cleaned_data.get("bio"),
                avatar = form.cleaned_data.get("avatar")
            )
            user.set_password(form.cleaned_data.get("password1"))
            user.save()
            # login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    context = {
        'form': form
    }

    return render(request, 'base/login_register.html', context)



@login_required(login_url="login-page")
@permission_required("base.add_vet")
def registerVet(request):

    if request.method == "POST":

        userform = MyUserCreationForm(request.POST, request.FILES)
        vetprofileform = VetForm(request.POST)

        education_formset = EducationFormSet(request.POST)
        # portfolio_formset = PortfolioFormSet(request.POST, request.FILES)

        # ✅ Validate EVERYTHING first
        if (
            userform.is_valid()
            and vetprofileform.is_valid()
            and education_formset.is_valid()
           
        ):

            try:
                with transaction.atomic():

                    # 1️⃣ Create Custom User
                    vetuser = VetUser.objects.create_user(
                        username=userform.cleaned_data.get("email"),
                        first_name=userform.cleaned_data.get("first_name"),
                        middle_name=userform.cleaned_data.get("middle_name"),
                        surname=userform.cleaned_data.get("surname"),
                        email=userform.cleaned_data.get("email"),
                        county=userform.cleaned_data.get("county"),
                        town=userform.cleaned_data.get("town"),
                        bio=userform.cleaned_data.get("bio"),
                        avatar=userform.cleaned_data.get("avatar"),
                        password=userform.cleaned_data.get("password1"),
                    )

                    # 2️⃣ Get related Vet profile (created via signal)
                    vetprofile = Vet.objects.get(user=vetuser)

                    # 3️⃣ Update Vet profile fields from VetForm
                    vetprofile.salutation = vetprofileform.cleaned_data.get("salutation")
                    vetprofile.start_practice = vetprofileform.cleaned_data.get("start_practice")
                    vetprofile.services = vetprofileform.cleaned_data.get("services")
                    vetprofile.vet_speciality = vetprofileform.cleaned_data.get("vet_speciality")
                    vetprofile.licence_no = vetprofileform.cleaned_data.get("licence_no")
                    vetprofile.save()

                    # 4️⃣ Attach formsets to vet profile
                    education_formset.instance = vetprofile
                    # portfolio_formset.instance = vetprofile

                    # 5️⃣ Save formsets
                    education_formset.save()
                    # portfolio_formset.save()

                    return redirect("home")

            except Exception as e:
                messages.error(request, f"Error saving data: {e}")

        else:
            print(f"userform_errors: {userform.errors}")
            print(f"vetform_errors: {vetprofileform.errors}")
            print(f"education_formset_errors: {education_formset.errors}")
            # print(f"portfolio_formset_errors: {portfolio_formset.errors}")
            messages.error(request, "Please correct the errors below.")

    else:
        userform = MyUserCreationForm()
        vetprofileform = VetForm()
        education_formset = EducationFormSet()
        # portfolio_formset = PortfolioFormSet()

    context = {
        "form1": userform,
        "form2": vetprofileform,
        "form3": education_formset,
        # "form4": portfolio_formset,
    }

    return render(request, "base/register-vet.html", context)
  

def vetprofile(request, pk):
    # AM GOING TO MODIFY THIS SUCH THAT I ONLY QUERY THE USER, SEE THIER ROLE AND DISPLAY THEIR PROFILES ACCORDINGLY
    # vet = Vet.objects.get(id=pk)
    # comments_from_clients = VetComment.objects.filter(
    #     vet = vet,
    #     is_satisfaction_comment = True
    # )
    
    user = User.objects.get(id=pk)
    role = user.role
    page = role
    context  = sideMenuComponents(request)
    if role == "VET":
        vet = Vet.objects.get(user=user)
        
        comments_from_clients = get_objects_for_user(
            user,
            "base.dg_view_consultationcomment",
            klass = ConsultationSatisfactionComment
        )
        
        
        
        context['vet'] = vet
        context['comments'] = comments_from_clients
    
    elif role == "APPUSER":
        comments_for_vets = get_objects_for_user(
            user,
            "base.dg_view_consultationcomment",
            klass = ConsultationSatisfactionComment
        )
        context["comments"] = comments_for_vets
        context["user"] = user
    
    
    context["page"] = page
    return render(request, 'base/profile.html', context)

def colleagueRequests(request):
    colleague_requests = get_objects_for_user(
        request.user,
        "base.dg_view_colleague_request",
        klass = ReferralColleagueRequest
    )
    if request.user.is_superuser:
        colleague_requests = colleague_requests.filter(
            status = "PENDING"
        )
    else:
        colleague_requests = colleague_requests.filter(
            colleague_requested = request.user,
            status = "PENDING"
        )
    context = {
        "colleague_requests":colleague_requests
    }
    return render(request, 'base/colleague-requests.html', context)

def referralColleagueRequest(request, pk):
    colleague_requested_user = User.objects.get(id=pk)
    requesting_vet_user = request.user
    pending_or_rejected_requests = ReferralColleagueRequest.objects.filter(
        requesting_vet = requesting_vet_user,
        colleague_requested = colleague_requested_user
    ).filter(
        Q(status = "PENDING") |
        Q(status = "REJECTED")
    )
    
    if pending_or_rejected_requests.count() == 0:
        request = ReferralColleagueRequest.objects.create(
            requesting_vet = requesting_vet_user,
            colleague_requested = colleague_requested_user
        )
        request.save()
        # messages.success(request, "Colleague Request Sent!")
        
        return redirect("home")
    else:
        return redirect("home")

def confirmReferralColleagueRequest(request, pk):
    colleague_request = ReferralColleagueRequest.objects.get(id=pk)
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    if q == "ACCEPTED":
        colleague_request.status = "ACCEPTED"
    elif q == "REJECTED":
        colleague_request.status = "REJECTED"
    colleague_request.save()
    return redirect("colleague_requests")
    

def consultation(request, pk):
    consultation = Consultation.objects.get(id=pk)
    # still debating whether to be other consultations or previous consultations 
    # previousconsultations = Consultation.objects.filter(
    #     created__lt=consultation.created,
    #     client = consultation.client,
    #     vet = consultation.vet
    # )
    
    previousconsultations = get_objects_for_user(
        request.user,
        "base.dg_view_consultation",
        klass = Consultation
    ).filter(
        created__lt=consultation.created,
        client = consultation.client,
        vet = consultation.vet
    )
    
    if request.method == 'POST':
        correspondent = VetComment.objects.create(
            user=request.user,
            vet = consultation.vet,
            body=request.POST.get('body'),
            is_consultation = True
        )
        correspondent.save()
        consultation.correspondents.add(correspondent)
        return redirect('consultation', pk=consultation.id)

    context = {
        'consultation':consultation,
        'previousconsultations':previousconsultations
    }
    return render(request, 'base/consultation.html', context )

@login_required(login_url="login-page")
def consultations(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # all_consultations = Consultation.objects.filter(
    #     Q(client__email = request.user.email)|
    #     Q(vet__user__email = request.user.email)
        
    # )
    
    all_consultations = get_objects_for_user(
        request.user,
        "base.dg_view_consultation",
        klass = Consultation
    )
    
    consultation_requests = all_consultations.filter(status = 'PENDING')
    
    consultations = all_consultations.filter(status = 'ACCEPTED')
    
    consultations = consultations.filter(

        Q(vet__first_name__icontains = q)|
        Q(vet__last_name__icontains = q) |
        Q(vet__email__icontains = q) |
        Q(vet__username__icontains = q) |
        Q(client__username__icontains = q) |
        Q(client__email__icontains = q) |
        Q(client__first_name__icontains = q)|
        Q(client__last_name__icontains = q)
    )

    context = {
        'consultations':consultations,
        'consultation_requests':consultation_requests
    }
    return render(request, 'base/consultations.html', context)

@login_required(login_url="login-page")
@permission_required("base.request_consultation", login_url="login-page")
def requestConsultation(request):
    form = ConsultationFeeForm()
    form.fields["client"].queryset = app_users
    form.fields["vet"].queryset = vets
    if request.method == 'POST':
        form = ConsultationFeeForm(request.POST)
        if form.is_valid():
            # consultation_request = form.save(commit=False)
            
            # PENDING CONSULTATIONS BETWEEN THE SAME VET AND SAME CLIENT
            pending_consultations = Consultation.objects.filter(
                # client = consultation_request.client,
                # vet = consultation_request.vet,
                # status = 'PENDING'
                client = form.cleaned_data.get("client"),
                vet = form.cleaned_data.get("vet"),
                paid_for = True,
                status = "PENDING"
            )
            print(pending_consultations)
            if pending_consultations.count() == 0:
                # consultation_request.save()
                transaction_id = get_transaction_id()
                transaction = form.save(commit = False)
                transaction.transaction_id = transaction_id
                transaction.save()
                
                amount = int(transaction.amount)
                phone_number = transaction.payment_number
                
                # amount = int(form.cleaned_data.get("amount"))
                # phone_number = form.cleaned_data.get("payment_number")

                response = stk_push_success(amount, phone_number, transaction_id)
                print(response)

                if response.get("ResponseCode") == "0":
                    # return redirect('process_stk_push')
                    checkout_request_id = response["CheckoutRequestID"]
                    return render(request, 'base/pending.html', {"checkout_request_id": checkout_request_id})
                else:
                    errorMessage = response.get("errorMessage", "Failed to send STK push. Please try again.")
                    messages.error(request, errorMessage)
                    return render(request, 'base/consultation-form.html', {"form": form})
                
                
            else:
                messages.error(request, 'Sorry there already is a pending request!')
        messages.error(request, 'Something went wrong!')
    context = {
        'form':form
    }
    return render(request, 'base/consultation-form.html', context)

@login_required(login_url="login-page")
@permission_required("base.approve_consultation", login_url="login-page")
def confirmConsultation(request, pk):
    consultation = Consultation.objects.get(id=pk)
    if request.method == 'POST':
        approval_status = request.POST.get('approval_status')
        if approval_status == 'YES':
            consultation.status = 'ACCEPTED'
        else:
            consultation.status = 'REJECTED'
        consultation.save()
        return redirect('consultations')
    context = {
        'obj':consultation
    }
    return render(request, 'base/confirm-status.html', context)

def addConsultant(request, pk):
    consultation = Consultation.objects.get(id=pk)
    referral_colleagues = consultation.vet.vet.referral_colleagues.all()
    print(f"referral_colleagues: {referral_colleagues}")
    
    if request.method == "POST":
        vetuser_id = request.POST.get("vetuser_id")
        vet = VetUser.objects.get(id=vetuser_id)
        if vet not in consultation.secondary_consultants.all():
            consultation.secondary_consultants.add(vet)
            consultation.save()
            messages.success(request, "vet recruited successfully")
        else:
            messages.error(request, "Sorry the requested vet is already a consultant")
        return redirect("home")
        
        
    context = {
        "vets":referral_colleagues,
        "consultation":consultation
    }
    return render(request, 'base/refer-case.html', context)
    
        
@login_required(login_url="login-page")
def leaveCommentForVet(request, pk):
    consultation = Consultation.objects.get(id=pk)
    # vet = Vet.objects.get(user=consultation.vet)
    form = consultationsatisfactioncommentform()
    if request.method == 'POST':
        # comment_body = request.POST.get('comment_body')
        # satisfaction_status = request.POST.get('satisfaction_status')
        form = consultationsatisfactioncommentform(request.POST)
        
        if form.is_valid():
            consultationsatisfactioncomment = form.save(commit=False)
            consultationsatisfactioncomment.consultationobject = consultation
            consultationsatisfactioncomment.user = request.user
            consultationsatisfactioncomment.vet = consultation.vet
            consultationsatisfactioncomment.save()
       
        # comment = VetComment.objects.create(
        #     user = request.user,
        #     vet = consultation.vet,
        #     body = comment_body,
        #     is_satisfaction_comment = True
        # )
        # comment.save()
        # consultation.client_left_comment = True
        # if satisfaction_status == 'YES':
        #     consultation.client_satisfied = True
        #     consultation.save()
        #     vet.successfull_consultations += 1
        #     vet.save()
        # else:
        #     consultation.client_satisfied = False
        #     consultation.save()
        
        return redirect('home')
    context = {
        'consultation':consultation,
        'form':form
    }
    return render(request, 'base/leave-comment.html', context)
        
    

def appointments(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # appointments = Appointment.objects.filter(
    #     Q(client__email = request.user.email)|
    #     Q(vet__use__email = request.user.email)
    # )
    
    appointments = get_objects_for_user(
        request.user,
        "base.dg_view_appointment",
        klass = Appointment
    )

    appointments = appointments.filter(

        Q(vet__first_name__icontains = q)|
        Q(vet__last_name__icontains = q) |
        Q(vet__email__icontains = q) |
        Q(vet__username__icontains = q) |
        Q(client__username__icontains = q) |
        Q(client__email__icontains = q) |
        Q(client__first_name__icontains = q)|
        Q(client__last_name__icontains = q)
    )

    context = {
        'appointments':appointments
    }
    return render(request, 'base/appointments.html', context)

@login_required(login_url="login-page")
@permission_required("base.request_appointment", login_url="login-page")
def createAppointment(request):
    form = AppointmentForm()
    form.fields["client"].queryset = app_users
    form.fields["vet"].queryset = vets
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        print(form.errors)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            if appointment.scheduled_time_to <= appointment.scheduled_time_from:
                messages.error(request, 'sorry please choose a future date!')
                return redirect('create-appointment')
            # SHOULD RUN ON DJANGO SIGNALS 
            
            # STILL CANT TELL WHEN ANOTHER APPOINTMENT IS ONGOING 
            possible_conflicts = Appointment.objects.filter(
                vet = appointment.vet,
                scheduled_date=appointment.scheduled_date
                
                
                # this code broke 
                # scheduled_time_from__gte = appointment.scheduled_time_from, 
                # scheduled_time_from__lte=appointment.scheduled_time_to, 
                # scheduled_time_to__gte=appointment.scheduled_time_from, 
                # scheduled_time_to__lte=appointment.scheduled_time_to
                )
            for possible_conflict in possible_conflicts:
                if appointment.scheduled_time_from >= possible_conflict.scheduled_time_from and appointment.scheduled_time_from <= possible_conflict.scheduled_time_to or appointment.scheduled_time_to >= possible_conflict.scheduled_time_from and appointment.scheduled_time_to <= possible_conflict.scheduled_time_to:
                    messages.error(request, "Sorry the slot isn't open" )
                    return redirect('create-appointment')
            appointment.save()
            messages.success(request, 'You Successfully booked an appointment!')
            return redirect('home')
                    
           
            
            #IF NO CONFLICTS 
            # if conflicts.count() == 0:
            #     appointment.save()
            #     return redirect('home')
            # else:
            #     messages.error(request, "Sorry the slot isn't open" )
            #     return redirect('create-appointment')
        else:
            messages.error(request, 'Something went wrong!')
    context = {
        'form':form
    }
    return render(request, 'base/appointment-form.html',  context)
            
        
    

@login_required(login_url='login-page')
def updateUser(request):
    user = request.user
    form = UserProfileForm(instance=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            # thinking of how to make it work for all users without another view function 
            return redirect('home')
        
    return render(request, 'base/update-user.html', {'form': form})

@login_required(login_url='login-page')
def deleteComment(request, pk):
    comment  = VetComment.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        comment.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': comment})

def markNotificationRead(request, pk):
    notification = Notification.objects.get(id=pk)
    notification.is_read = True
    notification.save()
    return redirect("home")

def clinics(request):
    clinics = VetClinic.objects.all()
    context  = sideMenuComponents(request)
    context['clinics'] = clinics
    return render(request, 'base/clinics.html', context)
