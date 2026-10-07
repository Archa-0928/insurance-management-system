from django.contrib.auth import authenticate, login as auth_login,logout
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User,Group
from .models import Insurancecompany,Userprofile,Complaint,Claim
from django.contrib import messages
from django.utils import timezone
import json
from django.http import JsonResponse, HttpResponse
import random
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request,'index.html')




def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        print(user,'userdata============')
        print(username,password,'username,password')

        if user is not None:
            if user.is_active:
                auth_login(request, user)


                if user.groups.filter(name='admin').exists():
                    return redirect('admin_home')
                elif user.groups.filter(name='Insurance company').exists():
                    return redirect('company_home')
                elif user.groups.filter(name='user').exists():
                    return redirect('/user_home_page')
                else:
                    # return redirect('/user_home')
                    return redirect('/user_home_page')

            else:
                messages.error(request, "Your account is not approved yet.")
                return redirect('login')

        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'login.html')



@login_required(login_url='login')
@never_cache
def logout_user(request):
    logout(request)
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('login')




@never_cache
def company_register(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        companyname = request.POST['companyname']
        phone = request.POST['phone']
        address = request.POST['address']
        place = request.POST['place']
        license_proof = request.FILES['license_proof']


        if User.objects.filter(username=username).exists():
            return render(request, 'company_register.html', {'error': 'Username already exists'})


        user = User.objects.create_user(username=username, password=password, email=email)
        group = Group.objects.get(name='Insurance company')
        user.groups.add(group)


        Insurancecompany.objects.create(
            USER=user,
            companyname=companyname,
            email=email,
            phone=phone,
            address=address,
            place=place,
            license_proof=license_proof
        )

        messages.success(request, "Company registered successfully! Please log in.")
        return redirect('login')

    return render(request, 'company_register.html')





@login_required(login_url='login')
@never_cache
def admin_home(request):
    company=Insurancecompany.objects.all()
    company_count=company.count()
    request.session['company_count']=company_count

    users=Userprofile.objects.all()
    users_count=users.count()
    request.session['users_count']=users_count

    complaint=Complaint.objects.all()
    complaint_count=complaint.count()
    request.session['complaint_count']=complaint_count

    reply=Complaint.objects.filter(reply='')
    reply_count=reply.count()
    request.session['reply_count']=reply_count

    return render(request,'admin_home.html',
                  {
                      'company_count':company_count,
                      'users_count':users_count,
                      'complaint_count':complaint_count,
                      'reply_count':reply_count,
                  })


@never_cache
def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']
        address = request.POST['address']
        id_proof = request.FILES['id_proof']
        full_name = request.POST['full_name']


        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('/user_register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name  # store full_name in first_name (or split later)
        group = Group.objects.get(name='user')
        user.groups.add(group)
        user.save()



        Userprofile.objects.create(
            USER=user,
            email=email,
            phone=phone,
            address=address,
            id_proof=id_proof,
            status="pending"
        )

        messages.success(request, "Registration successful! Please wait for admin approval.")
        return redirect('/login/')

    return render(request, 'user_register.html')




@login_required(login_url='login')
@never_cache
def admin_view_insurancecompany(request):
    company = Insurancecompany.objects.all().order_by('-id')
    return render(request, 'admin_view_insurancecompany.html', {'company': company})



@never_cache
def user_home(request):
    return render(request,'user_home.html')

@login_required(login_url='login')
@never_cache
def admin_view_users(request):
    users = Userprofile.objects.all().order_by('-id')
    return render(request, 'admin_view_users.html', {'users': users})


@never_cache
def admin_approve_user(request, user_id):

    user = get_object_or_404(User, id=user_id)

    profile = get_object_or_404(Userprofile, USER=user)


    user.is_active = True
    user.save()
    profile.status = "approved"
    profile.save()

    messages.success(request, f"User {user.username} has been approved.")
    return redirect('admin_view_users')



@never_cache
def admin_reject_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Userprofile, USER=user)

    user.is_active = False
    user.save()
    profile.status = "rejected"
    profile.save()

    messages.success(request, f"User {user.username} has been rejected.")
    return redirect('admin_view_users')




@never_cache
def company_home(request):
    # return render(request,'company_home.html')
    return render(request,'company/companyhome.html')



@login_required(login_url='login')
@never_cache
def admin_view_complaint(request):
    complaints = Complaint.objects.all().order_by('-date')
    return render(request, 'admin_view_complaint.html', {'complaints': complaints})


@login_required(login_url='login')
@never_cache
def admin_send_reply(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    if request.method == 'POST':
        reply = request.POST.get('reply')
        complaint.reply = reply
        complaint.save()
        messages.success(request, 'Reply sent successfully.')
        return redirect('admin_view_complaint')
    return render(request, 'admin_send_reply.html', {'complaint': complaint})


@login_required(login_url='login')
@never_cache
def user_send_complaint(request):
    user = request.user
    if request.method == 'POST':
        title = request.POST.get('title')
        complaint_text = request.POST.get('complaint')
        if complaint_text:
            Complaint.objects.create(SENDER=user,title=title,description=complaint_text, date=timezone.now().date())
            messages.success(request, 'Complaint submitted successfully.')
            return redirect('user_send_complaint')
        else:
            messages.error(request, 'Complaint text cannot be empty.')

    complaints = Complaint.objects.filter(SENDER=user).order_by('-date')
    return render(request, 'user_send_complaint.html', {'complaints': complaints})

@login_required(login_url='login')
@never_cache
def user_view_complaint_reply(request):
    request.user = Userprofile.objects.get(user=request.user)
    complaints = Complaint.objects.filter(sender=request.user)
    return render(request, 'user_view_complaint_replies.html', {'complaints': complaints})

@login_required(login_url='login')
@never_cache
def company_send_complaint(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        complaint_text = request.POST.get('complaint')

        if complaint_text.strip():
            Complaint.objects.create(SENDER=request.user,title=title,description=complaint_text,date=timezone.now().date())
            messages.success(request, "Your complaint has been submitted successfully.")
        else:
            messages.error(request, "Complaint text cannot be empty.")

        return redirect('company_send_complaint')

    complaints = Complaint.objects.filter(SENDER=request.user).order_by('-date')
    return render(request, 'company_send_complaint.html', {'complaints': complaints})


@login_required(login_url='login')
@never_cache
def user_enquiry(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").lower().strip()

            greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
            farewells = ["bye", "goodbye", "see you", "thank you", "thanks"]

            # Basic conversational replies
            if any(greet in user_message for greet in greetings):
                reply = random.choice([
                    "Hello! 👋 How can I help with your insurance enquiry today?",
                    "Hi there! 😊 What would you like to know about your policy or claim?",
                    "Hey! I'm here to assist with insurance questions. Fire away!"
                ])
            elif any(farewell in user_message for farewell in farewells):
                reply = random.choice([
                    "You're welcome! If you need more help, just type anytime. 👋",
                    "Glad I could help. Have a great day!",
                    "Thanks for chatting! 😊"
                ])
            # Insurance Claim Enquiries
            elif "claim process" in user_message or ("how" in user_message and "claim" in user_message):
                reply = "To file a claim, go to 'My Claims', click 'Submit New Claim', fill out the required details, upload necessary documents, and submit."
            elif ("claim" in user_message and "documents" in user_message) or "claim docs" in user_message:
                reply = "Typically, you'll need your policy document, claim form, proof of loss/damage, and personal identification. Check your claim type for specifics."
            elif "claim status" in user_message or ("status" in user_message and "claim" in user_message):
                reply = "To check your claim status, visit 'My Claims' in your dashboard and select your claim number for real-time updates."
            elif "claim period" in user_message or "last date" in user_message:
                reply = "The maximum claim period varies by policy but is usually 30 days from the incident. Please verify for your specific policy."
            elif "claim rejected" in user_message or "rejection" in user_message:
                reply = "If your claim is rejected, you’ll receive the reason via email or dashboard. You can submit an appeal or contact support for clarification."
            elif ("claim" in user_message and "in progress" in user_message) or ("pending" in user_message and "claim" in user_message):
                reply = "If your claim is in progress, our team is reviewing your documents. You'll be notified of any additional requirements or decision soon."
            elif "settle" in user_message and "claim" in user_message:
                reply = "Most approved claims are settled within 7-10 working days after approval. You'll receive a notification once payment is processed."
            elif "claim support" in user_message or ("help" in user_message and "claim" in user_message):
                reply = "For personalized claim help, email support@insurancecompany.com or call 1800-123-456. I can also guide you step by step!"
            # General insurance/user account
            elif "policy" in user_message:
                reply = "You can view your active policies under 'My Policies' in your dashboard. Do you want details about a specific policy?"
            elif "renew" in user_message or "renewal" in user_message:
                reply = "Policy renewals can be managed from 'My Policies' in your dashboard. Need help with a renewal?"
            elif "premium" in user_message or "amount" in user_message:
                reply = "To view your premium and payment history, check the 'Payments' section in your account."
            elif "payment" in user_message or "pay" in user_message:
                reply = "Make payments or see your payment status under the 'Payments' section of your dashboard."
            elif "complaint" in user_message:
                reply = "You can submit a complaint from the 'Complaints' section and track its reply there. Need help with this?"
            elif "contact" in user_message or "help" in user_message or "support" in user_message:
                reply = "Contact our support at support@insurancecompany.com or call 1800-123-456. I’m also here for general questions!"
            elif "features" in user_message or "services" in user_message:
                reply = "We offer policy management, claims submission and tracking, renewals, payments, and dedicated support!"
            elif "working hours" in user_message or "timings" in user_message:
                reply = "Our support team is available Monday to Saturday, 9 AM to 6 PM."
            elif "where" in user_message and "branch" in user_message:
                reply = "Find your nearest branch on the 'Contact' page of our website."
            elif user_message in ["", " "]:
                reply = "Please type your enquiry and I'll be happy to help!"
            else:
                reply = "I'm here to assist! You can ask about your claim process, required documents, claim status, settlement times, policies, renewals, payments, complaints, or contact info."

            return JsonResponse({"reply": reply})
        except json.JSONDecodeError:
            return JsonResponse({"reply": "⚠️ Invalid input. Please try again."}, status=400)
        except Exception as e:
            return JsonResponse({"reply": f"⚠️ Server error: {str(e)}. Please try later."}, status=500)

    return render(request, 'user_enquiry.html')




# @login_required(login_url='login')

def user_submit_claim(request):


    claim = Claim()

    INSURANCE=Insurancecompany.objects.all()

    return render(request, 'user_submit_claim.html',{'data':INSURANCE})

def user_submit_claim_post(request):
    print(request.POST,'post======')
    user_profile = Userprofile.objects.get(USER=request.user)
    full_name = request.POST["full_name"]
    date_of_birth = request.POST["date_of_birth"]
    gender = request.POST["gender"]
    nationality = request.POST["nationality"]
    pan_number = request.POST["pan_number"]
    marital_status = request.POST["marital_status"]
    address = request.POST["address"]
    phone_number = request.POST["phone_number"]
    email_address = request.POST["email_address"]
    account_number = request.POST["account_number"]
    branch_name = request.POST["branch_name"]
    ifsc_code = request.POST["ifsc_code"]
    months_as_customer = request.POST["months_as_customer"]
    age = request.POST["age"]
    policy_number = request.POST["policy_number"]
    policy_bind_date = request.POST["policy_bind_date"]
    policy_state = request.POST["policy_state"]
    policy_csl = request.POST["policy_csl"]
    policy_deductable = request.POST["policy_deductable"]
    policy_annual_premium = request.POST["policy_annual_premium"]
    umbrella_limit = request.POST["umbrella_limit"]
    insured_zip = request.POST["insured_zip"]
    insured_sex = request.POST["insured_sex"]
    insured_education_level = request.POST["insured_education_level"]
    insured_occupation = request.POST["insured_occupation"]
    insured_hobbies = request.POST["insured_hobbies"]
    insured_relationship = request.POST["insured_relationship"]
    capital_gains = request.POST["capital_gains"]
    incident_type = request.POST["incident_type"]
    collision_type = request.POST["collision_type"]
    incident_severity = request.POST["incident_severity"]
    authorities_contacted = request.POST["authorities_contacted"]
    incident_state = request.POST["incident_state"]
    incident_city = request.POST["incident_city"]
    incident_location = request.POST["incident_location"]
    incident_hour_of_the_day = request.POST["incident_hour_of_the_day"]
    number_of_vehicles_involved = request.POST["number_of_vehicles_involved"]
    property_damage = request.POST["property_damage"]
    bodily_injuries = request.POST["bodily_injuries"]
    witnesses = request.POST["witnesses"]
    police_report_available = request.POST["police_report_available"]
    total_claim_amount = request.POST["total_claim_amount"]
    injury_claim = request.POST["injury_claim"]
    property_claim = request.POST["property_claim"]
    vehicle_claim = request.POST["vehicle_claim"]
    auto_make = request.POST["auto_make"]
    auto_model = request.POST["auto_model"]
    auto_year = request.POST["auto_year"]
    capital_loss = request.POST["capital_loss"]
    incident_date = request.POST["incident_date"]
    insurance = request.POST["insurance"]
    status = "Pending"

    insuranse_data=Insurancecompany.objects.get(id=insurance)
    Claim.objects.create(
        USERPROFILE=user_profile,
        INSURANCE=insuranse_data,
        full_name=full_name,
        date_of_birth=date_of_birth,
        gender=gender,
        nationality=nationality,
        pan_number=pan_number,
        marital_status=marital_status,
        address=address,
        phone_number=phone_number,
        email_address=email_address,
        account_number=account_number,
        branch_name=branch_name,
        ifsc_code=ifsc_code,
        months_as_customer=months_as_customer,
        age=age,
        policy_number=policy_number,
        policy_bind_date=policy_bind_date,
        policy_state=policy_state,
        policy_csl=policy_csl,
        policy_deductable=policy_deductable,
        policy_annual_premium=policy_annual_premium,
        umbrella_limit=umbrella_limit,
        insured_zip=insured_zip,
        insured_sex=insured_sex,
        insured_education_level=insured_education_level,
        insured_occupation=insured_occupation,
        insured_hobbies=insured_hobbies,
        insured_relationship=insured_relationship,
        capital_gains=capital_gains,
        capital_loss=capital_loss,
        incident_date=incident_date,
        incident_type=incident_type,
        collision_type=collision_type,
        incident_severity=incident_severity,
        authorities_contacted=authorities_contacted,
        incident_state=incident_state,
        incident_city=incident_city,
        incident_location=incident_location,
        incident_hour_of_the_day=incident_hour_of_the_day,
        number_of_vehicles_involved=number_of_vehicles_involved,
        property_damage=property_damage,
        bodily_injuries=bodily_injuries,
        witnesses=witnesses,
        police_report_available=police_report_available,
        total_claim_amount=total_claim_amount,
        injury_claim=injury_claim,
        property_claim=property_claim,
        vehicle_claim=vehicle_claim,
        auto_make=auto_make,
        auto_model=auto_model,
        auto_year=auto_year,
        status=status
    )
    #
    # claim.USERPROFILE_id = request.user.userprofile.id
    # claim.save()

    messages.success(request, "Your claim has been submitted successfully!")
    return redirect('/user_home_page')















@login_required(login_url='login')
@never_cache
def company_view_claim(request):
    claims = Claim.objects.filter(INSURANCE__USER_id=request.user.id)
    return render(request, 'company_view_claim.html', {'claims': claims})

@login_required(login_url='login')
@never_cache
def company_view_claim_detail(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    return render(request, 'company_view_claim_detail.html', {'claim': claim})






import os
import pandas as pd
import joblib
from django.shortcuts import render
from django.conf import settings

# Load model once at server start
MODEL_PATH = os.path.join(settings.BASE_DIR, 'myapp', 'fraud_detection_model.pkl')
model_pipeline = joblib.load(MODEL_PATH)

# All model features
FEATURES = [
    'months_as_customer', 'age', 'policy_number', 'policy_bind_date', 'policy_state',
    'policy_csl', 'policy_deductable', 'policy_annual_premium', 'umbrella_limit',
    'insured_zip', 'insured_sex', 'insured_education_level', 'insured_occupation',
    'insured_hobbies', 'insured_relationship', 'capital-gains', 'capital-loss',
    'incident_date', 'incident_type', 'collision_type', 'incident_severity',
    'authorities_contacted', 'incident_state', 'incident_city', 'incident_location',
    'incident_hour_of_the_day', 'number_of_vehicles_involved', 'property_damage',
    'bodily_injuries', 'witnesses', 'police_report_available', 'total_claim_amount',
    'injury_claim', 'property_claim', 'vehicle_claim', 'auto_make', 'auto_model',
    'auto_year'
]

DATE_COLS = ['policy_bind_date', 'incident_date']
NUM_COLS = [
    'months_as_customer', 'age', 'policy_number', 'policy_deductable',
    'policy_annual_premium', 'umbrella_limit', 'insured_zip', 'capital-gains',
    'capital-loss', 'incident_hour_of_the_day', 'number_of_vehicles_involved',
    'bodily_injuries', 'witnesses', 'total_claim_amount', 'injury_claim',
    'property_claim', 'vehicle_claim', 'auto_year'
]

def fraud_detection_view(request):
    context = {'features': FEATURES, 'result': None}

    if request.method == 'POST':
        new_data = {}
        for feature in FEATURES:
            new_data[feature] = request.POST.get(feature)

        # Convert date fields
        for col in DATE_COLS:
            if new_data[col]:
                try:
                    date_val = pd.to_datetime(new_data[col], format='%Y-%m-%d')
                    new_data[col] = (date_val - pd.Timestamp('1899-12-30')).days
                except ValueError:
                    new_data[col] = None

        # Convert numerical fields
        for col in NUM_COLS:
            try:
                new_data[col] = float(new_data[col]) if new_data[col] else None
            except ValueError:
                new_data[col] = None

        # Create DataFrame
        new_df = pd.DataFrame([new_data])

        # Predict
        prediction = model_pipeline.predict(new_df)
        probability = model_pipeline.predict_proba(new_df)[:, 1][0]

        result_text = "Fraud Detected" if prediction[0] == 1 else "No Fraud"
        context['result'] = {
            'prediction': result_text,
            'probability': f"{probability:.4f}"
        }

    return render(request, 'fraud_detection_form.html', context)


@login_required(login_url='login')
@never_cache
def update_claim_status(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Approved', 'Rejected']:
            claim.status = new_status
            claim.save()
            messages.success(request, f'Claim {claim.id} status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status update.')
        return redirect('company_view_claim')

    return redirect('company_view_claim')


@login_required(login_url='login')
@never_cache
def user_view_claim_status(request):
    user_profile = Userprofile.objects.get(USER=request.user)

    claims = Claim.objects.filter(USERPROFILE=user_profile).order_by('-id')

    if request.method == 'GET' and 'claim_id' in request.GET:
        claim_id = request.GET.get('claim_id')
        claims = claims.filter(id=claim_id)
        if not claims.exists():
            messages.error(request, 'Claim not found or you do not have permission to view it.')

    return render(request, 'user_view_claim_status.html', {'claims': claims})





def user_home_page(request):
    return render(request,'user/userhome.html')





def user_view_insurance_company(request):
    var=Insurancecompany.objects.all()
    return render(request,'user/view insurancecompany.html',{'data':var})




#
# from django.shortcuts import render, redirect, get_object_or_404
#
# from .models import (
#     Insurancecompany,
#     Damage_image_check,
#     Userprofile
# )
#
#
# def user_upload_damage(request, id):
#
#     insurance = get_object_or_404(
#         Insurancecompany,
#         id=id
#     )
#
#     if request.method == 'POST':
#
#         frontimage = request.FILES.get('frontimage')
#         backimage = request.FILES.get('backimage')
#         leftside = request.FILES.get('leftside')
#         rightsideimage = request.FILES.get('rightsideimage')
#         topimage = request.FILES.get('topimage')
#         bottumimage = request.FILES.get('bottumimage')
#
#         userdata = get_object_or_404(
#             Userprofile,
#             USER_id=request.user.id
#         )
#
#         Damage_image_check.objects.create(
#             USER=userdata,
#             INSURANCE=insurance,
#             frontimage=frontimage,
#             backimage=backimage,
#             leftside=leftside,
#             rightsideimage=rightsideimage,
#             topimage=topimage,
#             bottumimage=bottumimage,
#             image_overall_damage_description='',
#             status='Pending Analysis'
#         )
#
#         return redirect(
#             'user_view_damage',
#             id=insurance.id
#         )
#
#     return render(
#         request,
#         'user/upload damage.html',
#         {
#             'insurance': insurance
#         }
#     )
#
#
# def user_view_damage(request, id):
#
#     insurance = get_object_or_404(
#         Insurancecompany,
#         id=id
#     )
#
#     damage = Damage_image_check.objects.filter(
#         USER=request.user.userprofile,
#         INSURANCE=insurance
#     ).order_by('-date')
#
#     return render(
#         request,
#         'user/view damage.html',
#         {
#             'insurance': insurance,
#             'data': damage
#         }
#     )
#
#
# from django.shortcuts import render, get_object_or_404
# from .models import Damage_image_check, Insurancecompany
#
#
# def insurance_view_damage(request):
#
#
#     insurance = get_object_or_404(
#         Insurancecompany,
#         USER_id=request.user.id
#     )
#
#
#     damage = Damage_image_check.objects.filter(
#         INSURANCE=insurance
#     ).order_by('-date')
#
#     return render(
#         request,
#         'company/view damage.html',
#         {
#             'data': damage,
#             'insurance': insurance
#         }
#     )
#
#
#
#
#
# def insurance_damage_details(request, id):
#
#     insurance = get_object_or_404(
#         Insurancecompany,
#         USER_id=request.user.id
#     )
#
#     damage = get_object_or_404(
#         Damage_image_check,
#         id=id,
#         INSURANCE=insurance
#     )
#
#     return render(
#         request,
#         'company/damage details.html',
#         {
#             'damage': damage,
#             'insurance': insurance
#         }
#     )
#




from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Insurancecompany,
    Damage_image_check,
    Userprofile
)

# Gemini analysis function
# This function is located in analyze_damage.py
from .analyze_damage import analyze_damage


# =========================================================
# USER - VIEW INSURANCE COMPANIES
# =========================================================

def user_view_insurance_company(request):

    data = Insurancecompany.objects.all()

    return render(
        request,
        'user/view insurancecompany.html',
        {
            'data': data
        }
    )


# =========================================================
# USER - UPLOAD VEHICLE DAMAGE IMAGES
# =========================================================

def user_upload_damage(request, id):

    # Get selected insurance company
    insurance = get_object_or_404(
        Insurancecompany,
        id=id
    )

    if request.method == 'POST':

        # Get logged-in user's profile
        userdata = get_object_or_404(
            Userprofile,
            USER_id=request.user.id
        )

        # Get uploaded images
        frontimage = request.FILES.get('frontimage')
        backimage = request.FILES.get('backimage')
        leftside = request.FILES.get('leftside')
        rightsideimage = request.FILES.get('rightsideimage')
        topimage = request.FILES.get('topimage')
        bottumimage = request.FILES.get('bottumimage')

        # Check whether all six images were uploaded
        if not frontimage:
            return render(
                request,
                'user/upload damage.html',
                {
                    'insurance': insurance,
                    'error': 'Please upload the front image.'
                }
            )

        if not backimage:
            return render(
                request,
                'user/upload damage.html',
                {
                    'insurance': insurance,
                    'error': 'Please upload the back image.'
                }
            )

        if not leftside:
            return render(
                request,
                'user/upload damage.html',
                {
                    'insurance': insurance,
                    'error': 'Please upload the left-side image.'
                }
            )

        if not rightsideimage:
            return render(
                request,
                'user/upload damage.html',
                {
                    'insurance': insurance,
                    'error': 'Please upload the right-side image.'
                }
            )

        if not topimage:
            return render(
                request,
                'user/upload damage.html',
                {
                    'insurance': insurance,
                    'error': 'Please upload the top image.'
                }
            )

        if not bottumimage:
            return render(
                request,
                'user/upload damage.html',
                {
                    'insurance': insurance,
                    'error': 'Please upload the bottom image.'
                }
            )

        # Create damage submission
        Damage_image_check.objects.create(
            USER=userdata,
            INSURANCE=insurance,

            frontimage=frontimage,
            backimage=backimage,
            leftside=leftside,
            rightsideimage=rightsideimage,
            topimage=topimage,
            bottumimage=bottumimage,

            image_overall_damage_description='',

            status='Pending Analysis'
        )

        # Go to user's damage page
        return redirect(
            'user_view_damage',
            id=insurance.id
        )

    # GET request
    return render(
        request,
        'user/upload damage.html',
        {
            'insurance': insurance
        }
    )


# =========================================================
# USER - VIEW OWN DAMAGE SUBMISSIONS
# =========================================================

def user_view_damage(request, id):

    # Selected insurance company
    insurance = get_object_or_404(
        Insurancecompany,
        id=id
    )

    # Logged-in user's profile
    userdata = get_object_or_404(
        Userprofile,
        USER_id=request.user.id
    )

    # Get only this user's submissions
    # for the selected insurance company
    damage = Damage_image_check.objects.filter(
        USER=userdata,
        INSURANCE=insurance
    ).order_by('-date')

    return render(
        request,
        'user/view damage.html',
        {
            'insurance': insurance,
            'data': damage
        }
    )


# =========================================================
# INSURANCE COMPANY - VIEW DAMAGE SUBMISSIONS
# =========================================================

def insurance_view_damage(request):

    # Get the insurance company of
    # the currently logged-in user
    insurance = get_object_or_404(
        Insurancecompany,
        USER_id=request.user.id
    )

    # Only show damage submissions belonging
    # to this insurance company
    damage = Damage_image_check.objects.filter(
        INSURANCE=insurance
    ).order_by('-date')

    return render(
        request,
        'company/view damage.html',
        {
            'data': damage,
            'insurance': insurance
        }
    )


# =========================================================
# INSURANCE COMPANY - VIEW DAMAGE DETAILS
# =========================================================

def insurance_damage_details(request, id):

    # Get logged-in insurance company
    insurance = get_object_or_404(
        Insurancecompany,
        USER_id=request.user.id
    )

    # Get selected damage record
    #
    # INSURANCE=insurance prevents one insurance
    # company from viewing another company's record.
    damage = get_object_or_404(
        Damage_image_check,
        id=id,
        INSURANCE=insurance
    )

    return render(
        request,
        'company/damage details.html',
        {
            'damage': damage,
            'insurance': insurance
        }
    )





import os

from django.conf import settings
from django.shortcuts import render

from .fraud_ocr import process_uploaded_document


def fraud_detection_ocr_view(request):

    context = {
        'result': None,
        'extracted_data': None,
        'ocr_text': None,
        'error': None,
    }

    if request.method == 'POST':

        uploaded_file = request.FILES.get(
            'document'
        )

        if not uploaded_file:

            context['error'] = (
                "Please select a PDF, DOCX, JPG, "
                "JPEG or PNG file."
            )

            return render(
                request,
                'fraud_ocr_upload.html',
                context
            )

        allowed_extensions = [
            '.pdf',
            '.docx',
            '.jpg',
            '.jpeg',
            '.png'
        ]

        extension = os.path.splitext(
            uploaded_file.name
        )[1].lower()

        if extension not in allowed_extensions:

            context['error'] = (
                "Invalid file format. "
                "Only PDF, DOCX, JPG, JPEG and PNG "
                "files are allowed."
            )

            return render(
                request,
                'fraud_ocr_upload.html',
                context
            )

        file_path = None

        try:

            # ==========================================
            # CREATE UPLOAD DIRECTORY
            # ==========================================

            upload_dir = os.path.join(
                settings.MEDIA_ROOT,
                'fraud_documents'
            )

            os.makedirs(
                upload_dir,
                exist_ok=True
            )

            # ==========================================
            # SAFE FILE NAME
            # ==========================================

            original_name = os.path.basename(
                uploaded_file.name
            )

            file_path = os.path.join(
                upload_dir,
                original_name
            )

            # ==========================================
            # SAVE FILE
            # ==========================================

            with open(
                file_path,
                'wb+'
            ) as destination:

                for chunk in uploaded_file.chunks():

                    destination.write(chunk)

            # ==========================================
            # PROCESS
            # ==========================================

            result = process_uploaded_document(
                file_path,
                extension
            )

            context['ocr_text'] = result.get(
                'ocr_text',
                ''
            )

            context['extracted_data'] = result.get(
                'extracted_data',
                {}
            )

            context['result'] = result.get(
                'result'
            )

        except Exception as e:

            context['error'] = (
                f"Processing error: {str(e)}"
            )

        finally:

            # ==========================================
            # DELETE TEMP FILE
            # ==========================================

            if file_path and os.path.exists(
                file_path
            ):

                try:

                    os.remove(file_path)

                except Exception:

                    pass

    return render(
        request,
        'company/fraud_ocr_upload.html',
        context
    )




import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import Userprofile, Insurancecompany, UserFraudDocument
from .fraud_ocr import process_uploaded_document


# ============================================================
# USER - UPLOAD FRAUD DOCUMENT
# ============================================================

@login_required
def user_fraud_document_upload(request):

    user_profile = get_object_or_404(
        Userprofile,
        USER=request.user
    )

    insurance_companies = Insurancecompany.objects.all()

    context = {
        'insurance_companies': insurance_companies,
        'result': None,
        'extracted_data': None,
        'ocr_text': None,
        'error': None,
    }

    if request.method == 'POST':

        uploaded_file = request.FILES.get('document')
        insurance_id = request.POST.get('insurance')

        # ----------------------------------------------------
        # CHECK FILE
        # ----------------------------------------------------

        if not uploaded_file:
            context['error'] = 'Please select a document.'
            return render(
                request,
                'user/user_fraud_document_upload.html',
                context
            )

        # ----------------------------------------------------
        # CHECK INSURANCE COMPANY
        # ----------------------------------------------------

        if not insurance_id:
            context['error'] = 'Please select an insurance company.'
            return render(
                request,
                'user/user_fraud_document_upload.html',
                context
            )

        insurance_company = get_object_or_404(
            Insurancecompany,
            id=insurance_id
        )

        # ----------------------------------------------------
        # CHECK FILE TYPE
        # ----------------------------------------------------

        allowed_extensions = [
            '.pdf',
            '.docx',
            '.jpg',
            '.jpeg',
            '.png'
        ]

        extension = os.path.splitext(
            uploaded_file.name
        )[1].lower()

        if extension not in allowed_extensions:

            context['error'] = (
                'Invalid file type. '
                'Only PDF, DOCX, JPG, JPEG and PNG are allowed.'
            )

            return render(
                request,
                'user/user_fraud_document_upload.html',
                context
            )

        # ----------------------------------------------------
        # CREATE DATABASE RECORD
        # ----------------------------------------------------

        fraud_document = UserFraudDocument.objects.create(

            USER=user_profile,

            INSURANCE=insurance_company,

            document=uploaded_file,

            original_filename=uploaded_file.name,

            file_type=extension.replace(
                '.',
                ''
            ).upper(),

            status='Processing',

            verification_status='Pending'
        )

        # ----------------------------------------------------
        # PROCESS OCR + ML
        # ----------------------------------------------------

        try:

            file_path = fraud_document.document.path

            processed_result = process_uploaded_document(
                file_path,
                extension
            )

            # -----------------------------------------------
            # GET RESULTS
            # -----------------------------------------------

            ocr_text = processed_result.get(
                'ocr_text',
                ''
            )

            extracted_data = processed_result.get(
                'extracted_data',
                {}
            )

            result = processed_result.get(
                'result',
                {}
            )

            # -----------------------------------------------
            # SAVE OCR + EXTRACTED DATA
            # -----------------------------------------------

            fraud_document.ocr_text = ocr_text

            fraud_document.extracted_data = extracted_data

            # -----------------------------------------------
            # SAVE ML RESULT
            # -----------------------------------------------

            fraud_document.prediction = result.get(
                'prediction'
            )

            fraud_document.prediction_value = result.get(
                'prediction_value'
            )

            fraud_document.probability = result.get(
                'probability'
            )

            fraud_document.status = 'Completed'

            fraud_document.error_message = ''

            fraud_document.save()

            # -----------------------------------------------
            # SHOW RESULT
            # -----------------------------------------------

            context['result'] = result

            context['extracted_data'] = extracted_data

            context['ocr_text'] = ocr_text

            messages.success(
                request,
                'Document uploaded and processed successfully.'
            )

        except Exception as e:

            fraud_document.status = 'Failed'

            fraud_document.error_message = str(e)

            fraud_document.save()

            context['error'] = (
                'Document processing failed: '
                + str(e)
            )

    return render(
        request,
        'user/user_fraud_document_upload.html',
        context
    )


# ============================================================
# COMPANY - VIEW PENDING DOCUMENTS
# ============================================================

@login_required
def company_fraud_documents(request):

    documents = UserFraudDocument.objects.filter(
        status='Completed',
        verification_status='Pending'
    ).select_related(
        'USER',
        'INSURANCE'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'company/company_fraud_documents.html',
        {
            'documents': documents
        }
    )


# ============================================================
# COMPANY - VERIFY DOCUMENT
# ============================================================

@login_required
def company_verify_fraud_document(
    request,
    document_id
):

    if request.method != 'POST':
        return redirect(
            'company_fraud_documents'
        )

    document = get_object_or_404(
        UserFraudDocument,
        id=document_id
    )

    verification_note = request.POST.get(
        'verification_note',
        ''
    )

    document.verification_status = 'Verified'

    document.verified_by = request.user

    document.verified_at = timezone.now()

    document.verification_note = verification_note

    document.save()

    messages.success(
        request,
        'Claim verified successfully.'
    )

    return redirect(
        'company_fraud_documents'
    )


# ============================================================
# COMPANY - REJECT DOCUMENT
# ============================================================

@login_required
def company_reject_fraud_document(
    request,
    document_id
):

    if request.method != 'POST':
        return redirect(
            'company_fraud_documents'
        )

    document = get_object_or_404(
        UserFraudDocument,
        id=document_id
    )

    verification_note = request.POST.get(
        'verification_note',
        ''
    )

    document.verification_status = 'Rejected'

    document.verified_by = request.user

    document.verified_at = timezone.now()

    document.verification_note = verification_note

    document.save()

    messages.success(
        request,
        'Claim rejected.'
    )

    return redirect(
        'company_fraud_documents'
    )


# ============================================================
# USER - VIEW MY DOCUMENTS
# ============================================================

@login_required
def user_fraud_document_history(request):

    user_profile = get_object_or_404(
        Userprofile,
        USER=request.user
    )

    documents = UserFraudDocument.objects.filter(
        USER=user_profile
    ).select_related(
        'INSURANCE'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'user/user_fraud_document_history.html',
        {
            'documents': documents
        }
    )



@login_required
def insurance_view_own_upload_ocr(request):

    data = UserFraudDocument.objects.filter(
        INSURANCE__USER_id=request.user.id
    ).select_related(
        'USER',
        'INSURANCE',
        'verified_by'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'company/view_user_upload_ocr.html',
        {
            'data': data
        }
    )


# ============================================================
# DOWNLOAD ORIGINAL UPLOADED DOCUMENT
# ============================================================

@login_required
def download_fraud_document(request, document_id):

    document = get_object_or_404(
        UserFraudDocument,
        id=document_id,
        INSURANCE__USER_id=request.user.id
    )

    if not document.document:
        return HttpResponse(
            'Document not available.',
            status=404
        )

    response = HttpResponse(
        document.document.open('rb').read(),
        content_type='application/octet-stream'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="{document.original_filename}"'
    )

    return response


# ============================================================
# DOWNLOAD OCR / AI RESULT
# ============================================================

@login_required
def download_fraud_result(request, document_id):

    document = get_object_or_404(
        UserFraudDocument,
        id=document_id,
        INSURANCE__USER_id=request.user.id
    )

    response = HttpResponse(
        content_type='text/plain; charset=utf-8'
    )

    filename = (
        f"fraud_analysis_result_{document.id}.txt"
    )

    response['Content-Disposition'] = (
        f'attachment; filename="{filename}"'
    )

    response.write(
        "============================================\n"
    )
    response.write(
        "       INSURANCE CLAIM ANALYSIS REPORT\n"
    )
    response.write(
        "============================================\n\n"
    )

    response.write(
        f"Document : {document.original_filename}\n"
    )

    response.write(
        f"File Type : {document.file_type}\n"
    )

    response.write(
        f"Uploaded : "
        f"{document.created_at.strftime('%d-%m-%Y %H:%M')}\n"
    )

    response.write(
        f"Processing Status : {document.status}\n"
    )

    response.write(
        "\n--------------------------------------------\n"
    )

    response.write(
        "AI FRAUD ANALYSIS\n"
    )

    response.write(
        "--------------------------------------------\n\n"
    )

    response.write(
        f"Prediction : "
        f"{document.prediction or 'N/A'}\n"
    )

    response.write(
        f"Prediction Value : "
        f"{document.prediction_value if document.prediction_value is not None else 'N/A'}\n"
    )

    if document.probability is not None:
        response.write(
            f"Probability : "
            f"{document.probability}%\n"
        )
    else:
        response.write(
            "Probability : N/A\n"
        )

    response.write(
        "\n--------------------------------------------\n"
    )

    response.write(
        "COMPANY VERIFICATION\n"
    )

    response.write(
        "--------------------------------------------\n\n"
    )

    response.write(
        f"Verification Status : "
        f"{document.verification_status}\n"
    )

    if document.verified_by:
        response.write(
            f"Verified By : "
            f"{document.verified_by.username}\n"
        )
    else:
        response.write(
            "Verified By : N/A\n"
        )

    if document.verified_at:
        response.write(
            f"Verified At : "
            f"{document.verified_at.strftime('%d-%m-%Y %H:%M')}\n"
        )
    else:
        response.write(
            "Verified At : N/A\n"
        )

    response.write(
        f"Verification Note : "
        f"{document.verification_note or 'N/A'}\n"
    )

    response.write(
        "\n--------------------------------------------\n"
    )

    response.write(
        "EXTRACTED INFORMATION\n"
    )

    response.write(
        "--------------------------------------------\n\n"
    )

    if document.extracted_data:

        try:

            extracted_data = document.extracted_data

            for key, value in extracted_data.items():

                response.write(
                    f"{key} : {value}\n"
                )

        except Exception:

            response.write(
                str(document.extracted_data)
            )

    else:

        response.write(
            "No extracted information available.\n"
        )

    response.write(
        "\n--------------------------------------------\n"
    )

    response.write(
        "OCR TEXT\n"
    )

    response.write(
        "--------------------------------------------\n\n"
    )

    response.write(
        document.ocr_text or
        "No OCR text available."
    )

    return response


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from .models import UserFraudDocument


@login_required
def company_verify_fraud_document(request, document_id):

    if request.method != 'POST':
        return redirect('insurance_view_own_upload_ocr')

    document = get_object_or_404(
        UserFraudDocument,
        id=document_id,
        INSURANCE__USER_id=request.user.id
    )

    document.verification_status = 'Verified'
    document.verified_by = request.user
    document.verified_at = timezone.now()
    document.verification_note = request.POST.get(
        'verification_note',
        ''
    ).strip()

    document.save()

    return redirect('/insurance_view_own_upload_ocr/')

@login_required
def company_reject_fraud_document(request, document_id):

    if request.method != 'POST':
        return redirect('insurance_view_own_upload_ocr')

    document = get_object_or_404(
        UserFraudDocument,
        id=document_id,
        INSURANCE__USER_id=request.user.id
    )

    document.verification_status = 'Rejected'
    document.verified_by = request.user
    document.verified_at = timezone.now()
    document.verification_note = request.POST.get(
        'verification_note',
        ''
    ).strip()

    document.save()

    return redirect('/insurance_view_own_upload_ocr/')