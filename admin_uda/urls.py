from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from admin_uda import views
from admin_uda import registrationViews
from admin_uda import transactionViews
from admin_uda import authViews

urlpatterns = [

    # Authentication
    path('login',authViews.LoginView.as_view(),name='auth-login'),# Auth-Login
    path('recover-password',authViews.RecoverPasswordView.as_view(),name='auth-recoverpw'),# Auth-Recover-Password
    path('logout',authViews.logout,name ='auth-logout'),# Logout
    path('lock-screen',authViews.LockScreenView.as_view(),name='auth-lock-screen'),# Auth-Lock-Screen

    #UI pages 
    path('', views.dashboard,name='dashboard'),
    path('membership_upload_ui/', views.membership_upload_ui),
    path('user_management_ui/', views.user_management_ui),
    path('hygienist_upload_ui/', views.hygienist_upload_ui),
    path('message_center_ui/', views.message_center_ui),
    path('convention_workshop_ui/', views.convention_workshop_ui),
    path('convention_transaction_ui/', views.convention_transaction_ui),
    path('spring_transaction_ui/', views.spring_transaction_ui),
    path('fall_registration_ui/', views.fall_registration_ui),
    path('spring_registration_ui/', views.spring_registration_ui),
    path('fall_transaction_ui/', views.fall_transaction_ui),
    path('edit_profile_ui/', views.edit_profile_ui),
    path('exhibitor_registration_ui/', views.exhibitor_registration_ui),
    path('vendor_detail_ui/', views.vendor_detail_ui),
    path('vendor_edit_ui/', views.vendor_edit_ui),
    path('convention_registration_ui/', views.convention_registration_ui),
    path('forgot_password_template_ui/', views.forgot_password_template_ui),
    path('convention_edit_ui/', views.convention_edit_ui),
    path('convention_detail_ui/', views.convention_detail_ui),
    path('vendor_detail_print_ui/', views.vendor_detail_print_ui),
    path('convention_id_card_print_bulk_ui/', views.convention_id_card_print_bulk_ui),
    path('convention_id_card_print_ui/', views.convention_id_card_print_ui),
    path('mail_attachment_ui/', views.mail_attachment_ui),
    path('qr_search_ui/', views.qr_search_ui),
    path('send_sms/',views.send_sms),
    path('send_mail/',views.send_mail),
    path('myview/',views.myview),


    #Dev pages
    path('membership_upload/', views.membership_upload,name='membership'),
    path('user_management/', views.user_management,name="user_management"),
    path('user_management_operations',views.user_management_operations,name="user_management_operations"),
    path('delete_user_management/<id>/',views.delete_user_management,name="delete_user_management"),
    path('edit_user/',views.get_users,name="get_users"),    
    path('user_email_check/',views.user_email_check,name="user_email_check"),
    path('hygienist_upload/', views.hygienist_upload,name='hygienist'),
    path('convention_workshop/', views.convention_workshop,name="convention_workshop"),
    path('convention_workshop_form/', views.convention_workshop_form,name="convention_workshop_form"),
    path('fall_registration/', registrationViews.fall_registration,name="fall_registration"),
    path('ada_membership_address/',registrationViews.get_ada_membership_address,name="get_ada_membership_address"),
    path('ada_membership_info/',registrationViews.get_ada_membership_info,name="get_ada_membership_info"),
    path('spring_registration/',registrationViews.spring_registration, name="spring_registration"),
    path('convention_registration/', registrationViews.convention_registration,name="convention_registration"),
    path('fall_transaction/',transactionViews.fall_transaction, name="fall_transaction"),
    path('fall_transaction_operations/', transactionViews.fall_transaction_operations,name="fall_transaction_operations"),
    path('spring_transaction/', transactionViews.spring_transaction,name="spring_transaction"),
    path('spring_transaction_operations/', transactionViews.spring_transaction_operations,name="spring_transaction_operations"),
    path('message_center/', views.message_center,name='message_center'),
    path('message_center_operations/', views.message_center_operations,name='message_center_operations'),
    path('convention_transaction/', transactionViews.convention_transaction,name="convention_transaction"),
    path('convention_transaction_operations/', transactionViews.convention_transaction_operations,name="convention_transaction_operations"),
    path('convention_detail/<str:ids>/', transactionViews.convention_detail,name="convention_detail"),
    path('edit_profile/', views.edit_profile,name="edit_profile"),
    path('delete_profile_img/', views.delete_profile_img,name="delete_profile_img"),
    path('vendor_edit/<str:id>', registrationViews.vendor_edit,name="vendor_registration"),
    path('vendor_email_check/',registrationViews.vendor_email_check,name="vendor_email_check"),
    path('vendor_detail/<str:id>', registrationViews.vendor_detail,name="vendor_details"),
    path('exhibitor_registration/', registrationViews.exhibitor_registration,name="exhibitor_registration"),
    path('convention_id_card_print/<str:ids>/', transactionViews.convention_detail_idcard,name="convention_id_card_print"),
    path('convention_id_card_print_bulk/', transactionViews.convention_id_card_print_bulk,name="convention_id_card_print_bulk"),
    path('convention_detail_pdf/<str:ids>/', transactionViews.transactions_pdf,name="convention_detail_pdf"),
    path('qr_code/', include('qr_code.urls', namespace="qr_code")),
    path('convention_edit/<str:param1>/', registrationViews.convention_edit,name="convention_edit"),
    path('qr_search/', views.qr_search,name="qr_search"),
    path('qr_search_code/<str:ids>/<str:types>/', views.qrcode_search,name="qr_search_code"),
]