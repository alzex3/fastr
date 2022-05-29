from django.core.mail import EmailMessage

from celery import shared_task

from users.models import User


@shared_task
def user_registered_notification(user_id):

    user = User.objects.get(id=user_id)

    msg_body = f"""
    Hello, {user.get_short_name()}!
    You're successfully sign up on FASTRetail.com

    Thanks for using our site!
    The FASTRetail team
    """

    msg = EmailMessage(
        subject='Welcome to FASTRetail.com!',
        to=(user.email,),
        body=msg_body,
    )
    msg.send()
