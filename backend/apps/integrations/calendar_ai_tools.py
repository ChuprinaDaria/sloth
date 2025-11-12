"""
AI Agent Tools for Calendar Integration

These tools allow the AI Agent to interact with Google Calendar
based on natural language conversation.
"""
from datetime import datetime, timedelta
import re
from .google_calendar import GoogleCalendarService, BookingEmailService
from .models import Integration
from apps.accounts.middleware import TenantSchemaContext
import logging

logger = logging.getLogger(__name__)


class CalendarAITools:
    """
    Tools that AI Agent can use to work with calendar
    """

    def __init__(self, user_id, tenant_schema):
        self.user_id = user_id
        self.tenant_schema = tenant_schema
        self.calendar_service = None

        # Load integration with proper schema context
        try:
            with TenantSchemaContext(tenant_schema):
                integration = Integration.objects.get(
                    user_id=user_id,
                    integration_type='google_calendar',
                    status='active'
                )
                self.calendar_service = GoogleCalendarService(integration)
        except Integration.DoesNotExist:
            logger.warning(f"No Google Calendar integration for user {user_id}")

    def is_available(self):
        """Check if calendar integration is available"""
        return self.calendar_service is not None

    def check_availability(self, date_str, duration_minutes=60):
        """
        Check available time slots

        Args:
            date_str: "tomorrow", "next monday", "2024-11-15", etc.
            duration_minutes: appointment duration

        Returns:
            String with available times or error message
        """
        if not self.is_available():
            return "Calendar integration is not set up. Please connect Google Calendar first."

        try:
            with TenantSchemaContext(self.tenant_schema):
                # Parse date
                date = self._parse_date(date_str)

                # Get available slots
                result = self.calendar_service.get_available_slots_formatted(
                    date=date,
                    duration_minutes=duration_minutes
                )

                return result

        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return f"Sorry, I couldn't check availability: {str(e)}"

    def book_appointment(
        self,
        customer_name,
        customer_email,
        service,
        date_str,
        time_str,
        duration_minutes=60,
        create_meet=True
    ):
        """
        Book appointment

        Args:
            customer_name: "John Doe"
            customer_email: "john@example.com"
            service: "Haircut", "Manicure", etc.
            date_str: "tomorrow", "2024-11-15", etc.
            time_str: "14:00", "2:00 PM", etc.
            duration_minutes: duration
            create_meet: create Google Meet link

        Returns:
            Success message with details or error
        """
        if not self.is_available():
            return "Calendar integration is not set up."

        try:
            with TenantSchemaContext(self.tenant_schema):
                # Parse date and time
                date = self._parse_date(date_str)
                time = self._parse_time(time_str)

                # Combine into datetime
                appointment_datetime = datetime.combine(date, time)

                # Get timezone from integration
                import pytz
                tz_str = self.calendar_service.integration.settings.get('timezone', 'UTC')
                tz = pytz.timezone(tz_str)
                appointment_datetime = tz.localize(appointment_datetime)

                # Check if slot is available
                available_slots = self.calendar_service.get_available_slots(
                    date=date,
                    duration_minutes=duration_minutes
                )

                is_slot_available = any(
                    abs((slot - appointment_datetime).total_seconds()) < 60
                    for slot in available_slots
                )

                if not is_slot_available:
                    return f"Sorry, {time_str} on {date.strftime('%B %d')} is not available. Please choose another time."

                # Create appointment
                event = self.calendar_service.create_appointment(
                    summary=f"{service} - {customer_name}",
                    start_time=appointment_datetime,
                    duration_minutes=duration_minutes,
                    attendees=[customer_email] if customer_email else None,
                    description=f"Service: {service}\nCustomer: {customer_name}\nEmail: {customer_email}",
                    create_meet_link=create_meet
                )

                # Get user for organization name (User is in public schema, doesn't need TenantSchemaContext)
                from apps.accounts.models import User
                user = User.objects.get(id=self.user_id)
                business_name = user.organization.name if hasattr(user, 'organization') and user.organization else 'Our Business'

                # Send confirmation email
                if customer_email:
                    appointment_details = {
                        'service': service,
                        'duration': duration_minutes,
                        'business_name': business_name
                    }

                    BookingEmailService.send_confirmation(
                        to_email=customer_email,
                        customer_name=customer_name,
                        appointment_details=appointment_details,
                        calendar_event=event
                    )

                # Format success message
                meet_info = ""
                if create_meet and event.get('hangoutLink'):
                    meet_info = f"\n🎥 Google Meet: {event['hangoutLink']}"

                return f"""
✅ Appointment booked successfully!

📅 {service} for {customer_name}
🕐 {appointment_datetime.strftime('%A, %B %d at %I:%M %p')}
⏱️ Duration: {duration_minutes} minutes
{meet_info}
📧 Confirmation email sent to {customer_email}

Calendar link: {event.get('htmlLink', '')}
"""

        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return f"Sorry, I couldn't book the appointment: {str(e)}"

    def list_upcoming_appointments(self, days=7):
        """
        List upcoming appointments

        Returns:
            String with formatted list of appointments
        """
        if not self.is_available():
            return "Calendar integration is not set up."

        try:
            with TenantSchemaContext(self.tenant_schema):
                events = self.calendar_service.list_upcoming_events(max_results=10)

                if not events:
                    return "No upcoming appointments."

                # Format events
                lines = ["📅 Upcoming appointments:\n"]

                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    summary = event.get('summary', 'No title')

                    # Parse datetime
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))

                    lines.append(f"• {summary}")
                    lines.append(f"  {dt.strftime('%A, %B %d at %I:%M %p')}\n")

                return '\n'.join(lines)

        except Exception as e:
            logger.error(f"Error listing appointments: {e}")
            return "Sorry, I couldn't fetch appointments."

    def _parse_date(self, date_str):
        """
        Parse natural language date

        Examples:
            "today" → today's date
            "tomorrow" → tomorrow
            "next monday" → next monday
            "2024-11-15" → specific date
        """
        date_str = date_str.lower().strip()
        today = datetime.now().date()

        # Today
        if date_str in ['today', 'сьогодні']:
            return today

        # Tomorrow
        if date_str in ['tomorrow', 'завтра']:
            return today + timedelta(days=1)

        # Day after tomorrow
        if date_str in ['day after tomorrow', 'післязавтра']:
            return today + timedelta(days=2)

        # Next week
        if 'next week' in date_str or 'наступного тижня' in date_str:
            return today + timedelta(days=7)

        # Weekdays
        weekdays = {
            'monday': 0, 'понеділок': 0,
            'tuesday': 1, 'вівторок': 1,
            'wednesday': 2, 'середа': 2,
            'thursday': 3, 'четвер': 3,
            'friday': 4, "п'ятниця": 4,
            'saturday': 5, 'субота': 5,
            'sunday': 6, 'неділя': 6,
        }

        for day_name, day_num in weekdays.items():
            if day_name in date_str:
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                return today + timedelta(days=days_ahead)

        # Try parsing as ISO date (YYYY-MM-DD)
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

        # Try parsing as DD/MM/YYYY
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            pass

        # Default to today
        return today

    def _parse_time(self, time_str):
        """
        Parse time string

        Examples:
            "14:00" → 14:00
            "2:00 PM" → 14:00
            "10am" → 10:00
        """
        time_str = time_str.lower().strip()

        # Remove spaces
        time_str = time_str.replace(' ', '')

        # Try HH:MM format
        if ':' in time_str:
            time_str = time_str.replace('am', '').replace('pm', '')

            # Check if PM
            is_pm = 'pm' in time_str.lower()

            # Parse
            try:
                hour, minute = map(int, time_str.split(':')[:2])

                # Convert to 24h format
                if is_pm and hour < 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0

                return datetime.min.time().replace(hour=hour, minute=minute)
            except:
                pass

        # Try HHam/pm format
        match = re.match(r'(\d{1,2})(am|pm)', time_str)
        if match:
            hour = int(match.group(1))
            is_pm = match.group(2) == 'pm'

            if is_pm and hour < 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0

            return datetime.min.time().replace(hour=hour, minute=0)

        # Default to 9 AM
        return datetime.min.time().replace(hour=9, minute=0)


# Export for use in AI Agent
def get_calendar_tools_for_user(user_id, tenant_schema):
    """Get calendar tools instance for a user"""
    return CalendarAITools(user_id, tenant_schema)
