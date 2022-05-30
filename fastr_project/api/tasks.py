from django.core.mail import EmailMessage

from celery import shared_task

from api.models import Order, OrderShop


@shared_task
def order_created_email(order_id):

    order = Order.objects.get(id=order_id)

    msg_body = f"""
    Hello, {order.user.get_short_name()}!
    You're successfully created order on FASTR.com

    Order ID: {order.id}
    Created Date: {order.created_at.strftime('%d.%m.%Y')}

    Thanks for using our site!
    The FASTR team
    """

    msg = EmailMessage(
        subject='New order created on FASTR.com!',
        to=(order.user.email,),
        body=msg_body,
    )
    msg.send()


@shared_task
def order_received_email(order_id):

    order = Order.objects.get(id=order_id)
    order_shops = OrderShop.objects.filter(order=order)

    for order_shop in order_shops:

        msg_body = f"""
        Hello, {order_shop.shop.user.get_short_name()}!
        You're received new order in your shop {order_shop.shop.name}
    
        Order ID: {order_shop.order.id}
        Created Date: {order_shop.order.created_at.strftime('%d.%m.%Y')}
    
        Thanks for using our site!
        The FASTR team
        """

        msg = EmailMessage(
            subject='New order received on FASTR.com!',
            to=(order_shop.shop.user.email,),
            body=msg_body,
        )
        msg.send()


@shared_task
def order_updated_email(order_shop_id):

    order_shop = OrderShop.objects.get(id=order_shop_id)

    msg_body = f"""
        Hello, {order_shop.order.user.get_short_name()}!
        Shop {order_shop.shop.name} from your order has updated order status
        New order status: {order_shop.status}

        Order ID: {order_shop.order.id}
        Created Date: {order_shop.order.created_at.strftime('%d.%m.%Y')}

        Thanks for using our site!
        The FASTR team
        """

    msg = EmailMessage(
        subject='Shop has updated your order status on FASTR.com!',
        to=(order_shop.order.user.email,),
        body=msg_body,
    )
    msg.send()
