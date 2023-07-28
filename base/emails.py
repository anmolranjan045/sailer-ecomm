from django.conf import settings
from django.core.mail import send_mail

def send_account_activation_email(email, email_token, instance):
    subject = 'Your account needs to be verified'
    email_from = settings.EMAIL_HOST_USER
    message = f'Hi {instance}!, Click on the link to activate your account at SAILER.COM http://127.0.0.1:8000/accounts/activate/{email_token}'
    
    send_mail(subject, message, email_from, [email])
    


def send_forget_password_mail(email, username, token):
    subject = 'Your forget-password link'
    message = f'Hi {username}, Click on the link to reset your password http://127.0.0.1:8000/accounts/email-password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True