from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from robots.models import Robot
from .models import Order
from email.header import Header

@receiver(post_save, sender=Robot)
def notify_customers(sender, instance, created, **kwargs):
    """
    Уведомляет клиента с первым заказом на робота.
    """
    if created:  # Обрабатываем только при создании нового робота
        # Фильтруем заказы по серийному номеру робота и сортируем по id
        matching_orders = Order.objects.filter(robot_serial=f"{instance.model}-{instance.version}").order_by('id')

        if matching_orders.exists():
            # Берём первый заказ в очереди
            first_order = matching_orders.first()

            # Формируем сообщение
            subject = str(Header("Your Robot is Now Available!", "utf-8"))
            message = f"""
            Добрый день!
            Недавно вы интересовались нашим роботом модели {instance.model}, версии {instance.version}.
            Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами.
            """

            # Отправляем письмо клиенту
            send_mail(
                subject,
                message,
                'noreply@r4c.com',  # Отправитель
                [first_order.customer.email],  # Получатель
                fail_silently=False,
            )

            # Удаляем заказ после уведомления (опционально)
            first_order.delete()
