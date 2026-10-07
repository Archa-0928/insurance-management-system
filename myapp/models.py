from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Userprofile(models.Model):
    USER=models.OneToOneField(User,on_delete=models.CASCADE)
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    id_proof=models.FileField(upload_to='license_proof/')
    status=models.CharField(max_length=100,default='pending')


class Insurancecompany(models.Model):
    USER=models.OneToOneField(User,on_delete=models.CASCADE)
    companyname=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    place=models.CharField(max_length=100)
    license_proof=models.FileField(upload_to='license_proof/')




class Claim(models.Model):
    USERPROFILE=models.ForeignKey(Userprofile,on_delete=models.CASCADE)
    INSURANCE=models.ForeignKey(Insurancecompany,on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, default='')
    date_of_birth = models.CharField(max_length=20, default='')
    gender = models.CharField(max_length=20, default='')
    nationality = models.CharField(max_length=50, default='')

    pan_number = models.CharField(max_length=20, default='')
    marital_status = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=200, default='')
    phone_number = models.CharField(max_length=20, default='')
    email_address = models.CharField(max_length=100, default='')


    account_number = models.CharField(max_length=50, default='0')
    branch_name = models.CharField(max_length=100, default='')
    ifsc_code = models.CharField(max_length=20, default='')


    months_as_customer = models.CharField(max_length=10, default='0')
    age = models.CharField(max_length=10, default='0')
    policy_number = models.CharField(max_length=50, default='')
    policy_bind_date = models.CharField(max_length=20, default='')
    policy_state = models.CharField(max_length=20, default='')
    policy_csl = models.CharField(max_length=50, default='')
    policy_deductable = models.CharField(max_length=20, default='0')
    policy_annual_premium = models.CharField(max_length=20, default='0')
    umbrella_limit = models.CharField(max_length=20, default='0')
    insured_zip = models.CharField(max_length=20, default='')
    insured_sex = models.CharField(max_length=10, default='')
    insured_education_level = models.CharField(max_length=50, default='')
    insured_occupation = models.CharField(max_length=50, default='')
    insured_hobbies = models.CharField(max_length=100, default='')
    insured_relationship = models.CharField(max_length=50, default='')
    capital_gains = models.CharField(max_length=20, default='0')
    capital_loss = models.CharField(max_length=20, default='0')


    incident_date = models.CharField(max_length=20, default='')
    incident_type = models.CharField(max_length=50, default='')
    collision_type = models.CharField(max_length=50, default='')
    incident_severity = models.CharField(max_length=50, default='')
    authorities_contacted = models.CharField(max_length=50, default='')
    incident_state = models.CharField(max_length=20, default='')
    incident_city = models.CharField(max_length=50, default='')
    incident_location = models.CharField(max_length=100, default='')
    incident_hour_of_the_day = models.CharField(max_length=10, default='0')
    number_of_vehicles_involved = models.CharField(max_length=10, default='0')
    property_damage = models.CharField(max_length=10, default='No')
    bodily_injuries = models.CharField(max_length=10, default='0')
    witnesses = models.CharField(max_length=10, default='0')
    police_report_available = models.CharField(max_length=10, default='No')


    total_claim_amount = models.CharField(max_length=20, default='0')
    injury_claim = models.CharField(max_length=20, default='0')
    property_claim = models.CharField(max_length=20, default='0')
    vehicle_claim = models.CharField(max_length=20, default='0')

    auto_make = models.CharField(max_length=50, default='')
    auto_model = models.CharField(max_length=50, default='')
    auto_year = models.CharField(max_length=10, default='')

    status=models.CharField(max_length=50,default='pending')



class Complaint(models.Model):
    SENDER=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=50)
    description=models.CharField(max_length=100)
    reply=models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)


from django.db import models
from django.utils import timezone


class Damage_image_check(models.Model):

    USER = models.ForeignKey(Userprofile,on_delete=models.CASCADE)

    INSURANCE = models.ForeignKey(Insurancecompany,on_delete=models.CASCADE)

    frontimage = models.FileField(upload_to='vehicle_damage/front/')

    backimage = models.FileField(upload_to='vehicle_damage/back/')

    leftside = models.FileField(upload_to='vehicle_damage/left/')

    rightsideimage = models.FileField(upload_to='vehicle_damage/right/')

    topimage = models.FileField(upload_to='vehicle_damage/top/')

    bottumimage = models.FileField(upload_to='vehicle_damage/bottom/')

    image_overall_damage_description = models.TextField(blank=True,null=True)

    status = models.CharField( max_length=100,default='Pending Analysis')

    date = models.DateTimeField(default=timezone.now)




from django.db import models
from django.contrib.auth.models import User


class UserFraudDocument(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    VERIFICATION_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]

    USER = models.ForeignKey(
        Userprofile,
        on_delete=models.CASCADE,
        related_name='fraud_documents'
    )

    INSURANCE = models.ForeignKey(
        Insurancecompany,
        on_delete=models.CASCADE,
    )

    # Uploaded insurance document
    document = models.FileField(
        upload_to='fraud_documents/'
    )

    original_filename = models.CharField(
        max_length=255
    )

    file_type = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # OCR
    ocr_text = models.TextField(
        blank=True,
        null=True
    )

    # Extracted 40 fields
    extracted_data = models.JSONField(
        blank=True,
        null=True
    )

    # ML prediction
    prediction = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    prediction_value = models.IntegerField(
        blank=True,
        null=True
    )

    probability = models.FloatField(
        blank=True,
        null=True
    )

    # OCR/ML processing
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # ==========================================
    # COMPANY VERIFICATION
    # ==========================================

    verification_status = models.CharField(
        max_length=30,
        choices=VERIFICATION_CHOICES,
        default='Pending'
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_fraud_documents'
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    verification_note = models.TextField(
        blank=True,
        null=True
    )

    # Error
    error_message = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.USER.username} - "
            f"{self.original_filename}"
        )