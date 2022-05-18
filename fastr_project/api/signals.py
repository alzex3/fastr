from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.db.models.signals import post_save

from api.models import Order, OrderShop


@receiver(post_save, sender=Order)
def order_created_notification(instance, **kwargs):

    msg_body = f"""
    Hello, {instance.user.get_short_name()}!
    You're successfully created order on FASTRetail.com
    
    Order ID: {instance.id}
    Created Date: {instance.created_at.strftime('%d.%m.%Y')}
    
    Thanks for using our site!
    The FASTRetail team
    """

    msg = EmailMessage(
        subject='New order created on FASTRetail.com!',
        to=(instance.user.email,),
        body=msg_body,
    )
    msg.send()


@receiver(post_save, sender=OrderShop)
def order_received_notification(instance, created, **kwargs):

    if created:
        msg_body = f"""
        Hello, {instance.shop.user.get_short_name()}!
        You're received new order in your shop {instance.shop.name}
    
        Order ID: {instance.order.id}
        Created Date: {instance.order.created_at.strftime('%d.%m.%Y')}
    
        Thanks for using our site!
        The FASTRetail team
        """

        msg = EmailMessage(
            subject='New order received on FASTRetail.com!',
            to=(instance.shop.user.email,),
            body=msg_body,
        )
        msg.send()


@receiver(post_save, sender=OrderShop)
def order_updated_notification(instance, created, **kwargs):

    if not created:
        msg_body = f"""
        Hello, {instance.order.user.get_short_name()}!
        Shop {instance.shop.name} from your order has updated order status
        New order status: {instance.status}

        Order ID: {instance.order.id}
        Created Date: {instance.order.created_at.strftime('%d.%m.%Y')}

        Thanks for using our site!
        The FASTRetail team
        """

        msg = EmailMessage(
            subject='Shop has updated your order status on FASTRetail.com!',
            to=(instance.order.user.email,),
            body=msg_body,
        )
        msg.send()
