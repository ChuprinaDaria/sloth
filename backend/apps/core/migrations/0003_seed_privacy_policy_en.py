from django.db import migrations
from django.utils import timezone


def create_english_privacy_policy(apps, schema_editor):
    PrivacyPolicy = apps.get_model('core', 'PrivacyPolicy')
    content_html = """
    <h2>Privacy Policy</h2>
    <p>Last updated: {date}</p>

    <p>This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use the Sloth AI platform (“Service”). By using the Service, you agree to the collection and use of information in accordance with this policy.</p>

    <h3>1. Information We Collect</h3>
    <ul>
      <li><strong>Account Data:</strong> name, email, phone (if provided), organization information.</li>
      <li><strong>Usage Data:</strong> logs, device/browser metadata, pages visited, timestamps.</li>
      <li><strong>Content You Provide:</strong> messages, uploaded files/photos, integration configuration.</li>
      <li><strong>Integrations:</strong> tokens/credentials you authorize (e.g., Google, Telegram) stored securely and used strictly to provide the Service.</li>
    </ul>

    <h3>2. How We Use Information</h3>
    <ul>
      <li>To provide and improve the Service and AI assistant features.</li>
      <li>To enable integrations (e.g., calendars, messaging, spreadsheets) per your setup.</li>
      <li>To ensure security, prevent abuse, and perform analytics and diagnostics.</li>
      <li>To communicate important updates and support messages.</li>
    </ul>

    <h3>3. Legal Basis</h3>
    <p>We process your data based on your consent, performance of a contract, legitimate interests, and/or legal obligations as applicable.</p>

    <h3>4. Data Sharing</h3>
    <p>We do not sell personal data. We share data with service providers and integration partners solely to operate the Service (e.g., cloud hosting, AI/ML APIs, calendar/messaging APIs) under appropriate safeguards.</p>

    <h3>5. Data Security</h3>
    <p>We use industry-standard security measures, including encryption for sensitive credentials and transport security (HTTPS). However, no method of transmission or storage is 100% secure.</p>

    <h3>6. Data Retention</h3>
    <p>We retain data for as long as necessary to provide the Service and comply with legal obligations. You may request deletion of your account and associated data, subject to legal requirements.</p>

    <h3>7. Your Rights</h3>
    <p>Depending on your jurisdiction, you may have rights to access, correct, delete, restrict, or port your data, and to withdraw consent. Contact us to exercise these rights.</p>

    <h3>8. International Transfers</h3>
    <p>Your data may be processed in countries other than your own. We implement appropriate safeguards for such transfers as required by law.</p>

    <h3>9. Children’s Privacy</h3>
    <p>The Service is not intended for children under 16. We do not knowingly collect data from children.</p>

    <h3>10. Changes to This Policy</h3>
    <p>We may update this Policy from time to time. Material changes will be communicated via the Service or email.</p>

    <h3>11. Contact</h3>
    <p>If you have questions or requests, contact: support@lazysoft.pl</p>
    """.format(date=timezone.now().date().isoformat())

    obj, created = PrivacyPolicy.objects.update_or_create(
        language='en',
        defaults={
            'title': 'Privacy Policy',
            'content': content_html,
            'is_active': True,
            'version': '1.0',
        }
    )


def noop_reverse(apps, schema_editor):
    # Do not delete policy on reverse to avoid losing content
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),  # adjust if the previous migration name differs
    ]

    operations = [
        migrations.RunPython(create_english_privacy_policy, noop_reverse),
    ]


