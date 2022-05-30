from django.core.mail import EmailMessage

from celery import shared_task

from users.models import User


@shared_task
def user_registered_email(user_id):

    user = User.objects.get(id=user_id)

    msg_body = f"""
    Hello, {user.get_short_name()}!
    You're successfully sign up on FASTR.com

    Thanks for using our site!
    The FASTR team
    """

    msg = EmailMessage(
        subject='Welcome to FASTR.com!',
        to=(user.email,),
        body=msg_body,
    )
    msg.send()


@shared_task
def user_password_reset_email(user_id, uid, token):

    user = User.objects.get(id=user_id)

    msg_body = f"""
    Hello, {user.get_short_name()}!
    You're receiving this email because someone requested a password reset for your user account on FASTR.com.
    
    Your recovery data:
    UID: {uid}
    Token: {token}
    
    Thanks for using our site!
    The FASTR team
    """

    msg = EmailMessage(
        subject='Password reset on FASTR.com',
        to=(user.email,),
        body=msg_body,
    )
    msg.send()
