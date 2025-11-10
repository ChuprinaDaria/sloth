"""
Email Service - Booking confirmations and notifications
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


class EmailService:
    """
    Сервіс для відправки email підтверджень
    """

    @staticmethod
    def send_booking_confirmation(customer_email, customer_name, booking_details):
        """
        Відправити підтвердження бронювання

        Args:
            customer_email: email клієнта
            customer_name: ім'я клієнта
            booking_details: dict з деталями бронювання:
                - service: назва послуги
                - date: дата
                - time: час
                - duration: тривалість
                - meet_link: посилання на Google Meet (опційно)
                - salon_name: назва салону
                - salon_address: адреса салону
                - salon_phone: телефон салону
        """
        try:
            subject = f"✅ Підтвердження запису - {booking_details['service']}"

            # Форматування повідомлення
            message = f"""
Вітаємо, {customer_name}! 🎉

Ваш запис успішно підтверджено!

📅 Деталі запису:
━━━━━━━━━━━━━━━━━━━━━━
📌 Послуга: {booking_details['service']}
📅 Дата: {booking_details['date']}
🕐 Час: {booking_details['time']}
⏱️ Тривалість: {booking_details.get('duration', '60 хвилин')}

📍 {booking_details.get('salon_name', 'Наш салон')}
🏠 {booking_details.get('salon_address', '')}
📞 {booking_details.get('salon_phone', '')}
"""

            # Додати Google Meet посилання якщо є
            if booking_details.get('meet_link'):
                message += f"\n🎥 Google Meet: {booking_details['meet_link']}\n"

            message += """
━━━━━━━━━━━━━━━━━━━━━━

💡 Підказки:
• Приходьте за 5-10 хвилин до початку
• Якщо потрібно перенести запис - повідомте заздалегідь
• Збережіть це повідомлення як нагадування

Чекаємо на вас! ✨

---
Це автоматичне повідомлення від Sloth AI
Якщо у вас є питання - відповідайте на цей email
"""

            # Відправити email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer_email],
                fail_silently=False,
            )

            return {
                'success': True,
                'message': 'Email sent successfully'
            }

        except Exception as e:
            print(f"Error sending booking confirmation email: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def send_booking_reminder(customer_email, customer_name, booking_details, hours_before=24):
        """
        Відправити нагадування про запис

        Args:
            customer_email: email клієнта
            customer_name: ім'я клієнта
            booking_details: деталі запису
            hours_before: за скільки годин до запису
        """
        try:
            subject = f"🔔 Нагадування про запис - {booking_details['service']}"

            message = f"""
{customer_name}, нагадуємо про ваш запис! ⏰

📅 Завтра о {booking_details['time']}
📌 Послуга: {booking_details['service']}
📍 {booking_details.get('salon_name', 'Наш салон')}

Чекаємо на вас! 😊

---
Якщо потрібно перенести - повідомте якнайшвидше
"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer_email],
                fail_silently=False,
            )

            return {'success': True}

        except Exception as e:
            print(f"Error sending reminder: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def send_cancellation_notice(customer_email, customer_name, booking_details):
        """
        Відправити повідомлення про скасування
        """
        try:
            subject = f"❌ Скасування запису - {booking_details['service']}"

            message = f"""
{customer_name}, ваш запис було скасовано.

Скасований запис:
• Дата: {booking_details['date']}
• Час: {booking_details['time']}
• Послуга: {booking_details['service']}

Якщо хочете записатися на інший час - напишіть нам!

---
З повагою, {booking_details.get('salon_name', 'Наш салон')}
"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer_email],
                fail_silently=False,
            )

            return {'success': True}

        except Exception as e:
            print(f"Error sending cancellation: {e}")
            return {'success': False, 'error': str(e)}
