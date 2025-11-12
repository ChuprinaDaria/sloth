"""
Google Calendar Integration with OAuth2 and AI-powered booking

Features:
- OAuth2 authentication flow
- Check available time slots
- Create appointments with Google Meet links
- Send email confirmations
- AI Agent integration for automatic booking from chat
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """
    Service for Google Calendar integration
    """

    # OAuth2 scopes - Calendar + Sheets/Drive + Gmail (read/send) for email features
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        # Gmail scopes required for email integration tools
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
    ]

    def __init__(self, integration):
        """Initialize with Integration instance"""
        self.integration = integration
        self.credentials = None
        self.service = None

        # Load credentials
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from integration"""
        creds_dict = self.integration.get_credentials()

        if not creds_dict.get('access_token'):
            raise ValueError("No access token found")

        self.credentials = Credentials(
            token=creds_dict.get('access_token'),
            refresh_token=creds_dict.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.SCOPES
        )

        # Refresh token if expired
        if self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                # Save refreshed token
                creds_dict['access_token'] = self.credentials.token
                if self.credentials.expiry:
                    creds_dict['token_expiry'] = self.credentials.expiry.isoformat()
                self.integration.set_credentials(creds_dict)
                self.integration.save()
                logger.info(f"Refreshed Google Calendar token for integration {self.integration.id}")
            except Exception as e:
                logger.error(f"Error refreshing Google Calendar token: {e}")
                raise ValueError(f"Failed to refresh expired token: {str(e)}")

        # Build service
        self.service = build('calendar', 'v3', credentials=self.credentials)

    @staticmethod
    def get_authorization_url(redirect_uri):
        """
        Get Google OAuth2 authorization URL

        Returns URL to redirect user for authorization
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=GoogleCalendarService.SCOPES,
            redirect_uri=redirect_uri
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force to get refresh_token
        )

        return authorization_url, state

    @staticmethod
    def exchange_code_for_tokens(code, redirect_uri):
        """
        Exchange authorization code for access & refresh tokens

        Returns: {'access_token': '...', 'refresh_token': '...'}
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=GoogleCalendarService.SCOPES,
            redirect_uri=redirect_uri
        )

        flow.fetch_token(code=code)

        credentials = flow.credentials

        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }

    def get_available_slots(self, date=None, duration_minutes=60, business_hours=(9, 18)):
        """
        Get available time slots for a specific date

        Args:
            date: datetime.date object (default: today)
            duration_minutes: appointment duration
            business_hours: tuple (start_hour, end_hour) e.g. (9, 18) = 9 AM to 6 PM

        Returns:
            List of available datetime slots
        """
        if date is None:
            date = datetime.now().date()

        # Get user's timezone from integration settings
        timezone_str = self.integration.settings.get('timezone', 'UTC')
        tz = pytz.timezone(timezone_str)

        # Define time range for the day
        start_of_day = tz.localize(datetime.combine(date, datetime.min.time().replace(hour=business_hours[0])))
        end_of_day = tz.localize(datetime.combine(date, datetime.min.time().replace(hour=business_hours[1])))

        try:
            # Get busy times from Google Calendar
            body = {
                "timeMin": start_of_day.isoformat(),
                "timeMax": end_of_day.isoformat(),
                "items": [{"id": "primary"}]
            }

            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars']['primary']['busy']

            # Convert busy times to datetime objects
            busy_periods = []
            for busy in busy_times:
                start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                busy_periods.append((start, end))

            # Generate all possible slots
            available_slots = []
            current_time = start_of_day

            while current_time + timedelta(minutes=duration_minutes) <= end_of_day:
                slot_end = current_time + timedelta(minutes=duration_minutes)

                # Check if this slot overlaps with any busy period
                is_available = True
                for busy_start, busy_end in busy_periods:
                    if (current_time < busy_end and slot_end > busy_start):
                        is_available = False
                        break

                if is_available:
                    available_slots.append(current_time)

                # Move to next slot (e.g., every 30 minutes)
                current_time += timedelta(minutes=30)

            return available_slots

        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []

    def create_appointment(
        self,
        summary,
        start_time,
        duration_minutes=60,
        attendees=None,
        description='',
        create_meet_link=True
    ):
        """
        Create appointment in Google Calendar

        Args:
            summary: Event title (e.g. "Haircut for John Doe")
            start_time: datetime object
            duration_minutes: duration
            attendees: list of email addresses
            description: event description
            create_meet_link: bool - create Google Meet link

        Returns:
            Event object with 'id', 'htmlLink', 'hangoutLink' (Google Meet)
        """
        end_time = start_time + timedelta(minutes=duration_minutes)

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': self.integration.settings.get('timezone', 'UTC'),
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': self.integration.settings.get('timezone', 'UTC'),
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 60},       # 1 hour before
                ],
            },
        }

        # Add attendees
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        # Add Google Meet link
        if create_meet_link:
            event['conferenceData'] = {
                'createRequest': {
                    'requestId': f"meet-{start_time.timestamp()}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }

        try:
            # Create event
            event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1 if create_meet_link else 0,
                sendUpdates='all'  # Send email to attendees
            ).execute()

            logger.info(f"Created event: {event['id']}")

            return event

        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            raise

    def list_upcoming_events(self, max_results=10):
        """List upcoming events"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            return events

        except Exception as e:
            logger.error(f"Error listing events: {e}")
            return []

    def cancel_appointment(self, event_id):
        """Cancel appointment"""
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()

            logger.info(f"Cancelled event: {event_id}")
            return True

        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return False

    def get_available_slots_formatted(self, date=None, duration_minutes=60):
        """
        Get available slots formatted for AI Agent

        Returns human-readable string of available times
        """
        slots = self.get_available_slots(date, duration_minutes)

        if not slots:
            return "No available slots for this date."

        # Format slots
        formatted_slots = []
        for slot in slots:
            formatted_slots.append(slot.strftime('%I:%M %p'))

        return f"Available times: {', '.join(formatted_slots)}"


class BookingEmailService:
    """
    Service for sending booking confirmation emails
    """

    @staticmethod
    def send_confirmation(
        to_email,
        customer_name,
        appointment_details,
        calendar_event
    ):
        """
        Send appointment confirmation email

        Args:
            to_email: customer email
            customer_name: customer name
            appointment_details: dict with service, date, time, etc.
            calendar_event: Google Calendar event object
        """
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        # Extract details
        start_time = datetime.fromisoformat(
            calendar_event['start']['dateTime'].replace('Z', '+00:00')
        )

        subject = f"Appointment Confirmation - {appointment_details.get('service', 'Service')}"

        # Get Google Meet link if available
        meet_link = calendar_event.get('hangoutLink', '')

        # HTML message
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #d946ef;">Appointment Confirmed! ✅</h2>

                <p>Hi {customer_name},</p>

                <p>Your appointment has been successfully booked!</p>

                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Appointment Details:</h3>
                    <p><strong>Service:</strong> {appointment_details.get('service', 'Service')}</p>
                    <p><strong>Date:</strong> {start_time.strftime('%A, %B %d, %Y')}</p>
                    <p><strong>Time:</strong> {start_time.strftime('%I:%M %p')}</p>
                    <p><strong>Duration:</strong> {appointment_details.get('duration', 60)} minutes</p>
                    {f'<p><strong>Location:</strong> {appointment_details.get("location", "")}</p>' if appointment_details.get('location') else ''}
                </div>

                {f'''
                <div style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2e7d32;">🎥 Video Consultation</h3>
                    <p>Join via Google Meet:</p>
                    <a href="{meet_link}" style="display: inline-block; background-color: #4caf50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Join Meeting</a>
                </div>
                ''' if meet_link else ''}

                <div style="margin: 20px 0;">
                    <p><strong>📅 Add to Calendar:</strong></p>
                    <a href="{calendar_event.get('htmlLink', '')}" style="color: #d946ef;">View in Google Calendar</a>
                </div>

                <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⏰ Reminder:</strong> You'll receive an email reminder 24 hours before your appointment.</p>
                </div>

                <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>

                <p style="margin-top: 30px;">
                    See you soon!<br>
                    <strong>{appointment_details.get('business_name', 'Our Team')}</strong>
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="font-size: 12px; color: #666;">
                    This is an automated confirmation email. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """

        # Plain text fallback
        plain_message = f"""
        Appointment Confirmed!

        Hi {customer_name},

        Your appointment has been successfully booked!

        Appointment Details:
        - Service: {appointment_details.get('service', 'Service')}
        - Date: {start_time.strftime('%A, %B %d, %Y')}
        - Time: {start_time.strftime('%I:%M %p')}
        - Duration: {appointment_details.get('duration', 60)} minutes

        {f"Google Meet Link: {meet_link}" if meet_link else ""}

        Calendar: {calendar_event.get('htmlLink', '')}

        See you soon!
        {appointment_details.get('business_name', 'Our Team')}
        """

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Sent confirmation email to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
            return False
