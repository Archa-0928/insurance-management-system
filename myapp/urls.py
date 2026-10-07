"""insurance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .import views


urlpatterns = [
    path('',views.index,name="index"),
    path('login/',views.login,name='login'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('company_register/',views.company_register,name='company_register'),
    path('user_register/',views.user_register,name='user_register'),

    path('admin_home/',views.admin_home,name='admin_home'),
    path('admin_view_insurancecompany/',views.admin_view_insurancecompany,name='admin_view_insurancecompany'),

    path('user_home/',views.user_home,name='user_home'),

    path('admin_view_users/',views.admin_view_users,name='admin_view_users'),
    path('admin_approve_user/<int:user_id>/', views.admin_approve_user, name='admin_approve_user'),
    path('admin_reject_user/<int:user_id>/', views.admin_reject_user, name='admin_reject_user'),
    path('company_home/', views.company_home, name='company_home'),
    path('admin_view_complaint/',views.admin_view_complaint,name='admin_view_complaint'),
    path('admin_send_reply/<int:id>',views.admin_send_reply,name='admin_send_reply'),
    path('company_send_complaint/',views.company_send_complaint,name='company_send_complaint'),
    path('user_send_complaint/',views.user_send_complaint,name='user_send_complaint'),
    path('user_enquiry/', views.user_enquiry, name='user_enquiry'),
    path('user_submit_claim/', views.user_submit_claim, name='user_submit_claim'),
    path('company_view_claim/', views.company_view_claim, name='company_view_claim'),
    path('company_view_claim_detail/<int:claim_id>/', views.company_view_claim_detail),

    path('fraud_detection_view/', views.fraud_detection_view, name='fraud_detection_view'),

    path('user_view_claim_status/', views.user_view_claim_status, name='user_view_claim_status'),
    path('update_claim_status/<int:claim_id>', views.update_claim_status, name='update_claim_status'),


    path('user_home_page', views.user_home_page, name='user_home_page'),
    path('user_submit_claim_post/', views.user_submit_claim_post, name='user_submit_claim_post'),




    path('user_view_insurance_company/', views.user_view_insurance_company, name='user_view_insurance_company'),
    path('user_upload_damage/<id>/', views.user_upload_damage, name='user_upload_damage'),
    path('user_view_damage/<id>/', views.user_view_damage, name='user_view_damage'),



    path('insurance_view_damage/', views.insurance_view_damage, name='insurance_view_damage'),
    path('insurance_damage_details/<int:id>/', views.insurance_damage_details, name='insurance_damage_details'),
    path('analyze_damage/<int:id>/',views.analyze_damage,name='analyze_damage'),


    path('fraud_detection_ocr_view/',views.fraud_detection_ocr_view,name='fraud_detection_ocr_view'),


    path('user_fraud_document_upload/',views.user_fraud_document_upload,name='user_fraud_document_upload'),
    path('company_fraud_documents/',views.company_fraud_documents,name='company_fraud_documents'),
    path('user_fraud_document_history/',views.user_fraud_document_history,name='user_fraud_document_history'),


    path('insurance_view_own_upload_ocr/',views.insurance_view_own_upload_ocr,name='insurance_view_own_upload_ocr'),

    path('download-fraud-document/<int:document_id>/',views.download_fraud_document,name='download_fraud_document'),

path(
    'download-fraud-result/<int:document_id>/',
    views.download_fraud_result,
    name='download_fraud_result'
),

    path(
        'verify-fraud-document/<int:document_id>/',
        views.company_verify_fraud_document,
        name='company_verify_fraud_document'
    ),

    path(
        'reject-fraud-document/<int:document_id>/',
        views.company_reject_fraud_document,
        name='company_reject_fraud_document'
    ),


]
