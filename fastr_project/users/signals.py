from django.core.mail import EmailMessage
from django.dispatch import Signal, receiver


user_registered = Signal()


@receiver(user_registered)
def user_registered_notification(user, **kwargs):

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
