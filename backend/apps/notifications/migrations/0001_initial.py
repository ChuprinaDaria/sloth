from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS push_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expo_push_token VARCHAR(255) UNIQUE NOT NULL,
                device_name VARCHAR(255) DEFAULT '',
                device_type VARCHAR(50) DEFAULT 'mobile',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                last_used_at TIMESTAMP NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_push_tokens_user_active
            ON push_tokens(user_id, is_active);
            """,
            reverse_sql="DROP TABLE IF EXISTS push_tokens;"
        ),

        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS notification_settings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                enabled BOOLEAN DEFAULT true,
                frequency VARCHAR(20) DEFAULT 'all',
                quiet_hours_enabled BOOLEAN DEFAULT true,
                quiet_hours_start TIME DEFAULT '22:00',
                quiet_hours_end TIME DEFAULT '08:00',
                critical_enabled BOOLEAN DEFAULT true,
                important_enabled BOOLEAN DEFAULT true,
                useful_enabled BOOLEAN DEFAULT true,
                vip_messages BOOLEAN DEFAULT true,
                integration_issues BOOLEAN DEFAULT true,
                negative_reviews BOOLEAN DEFAULT true,
                smart_analytics BOOLEAN DEFAULT true,
                holidays_reminders BOOLEAN DEFAULT true,
                achievements BOOLEAN DEFAULT true,
                pending_conversations BOOLEAN DEFAULT true,
                weekly_reports BOOLEAN DEFAULT true,
                pricing_recommendations BOOLEAN DEFAULT true,
                content_recommendations BOOLEAN DEFAULT true,
                max_notifications_per_day INTEGER DEFAULT 3,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_notification_settings_user
            ON notification_settings(user_id);
            """,
            reverse_sql="DROP TABLE IF EXISTS notification_settings;"
        ),

        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS notification_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                notification_type VARCHAR(100) NOT NULL,
                priority VARCHAR(20) NOT NULL,
                title VARCHAR(255) NOT NULL,
                body TEXT NOT NULL,
                data JSONB DEFAULT '{}',
                status VARCHAR(20) DEFAULT 'sent',
                error_message TEXT DEFAULT '',
                expo_response JSONB DEFAULT '{}',
                sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_notification_logs_user_sent
            ON notification_logs(user_id, sent_at);

            CREATE INDEX IF NOT EXISTS idx_notification_logs_type_sent
            ON notification_logs(notification_type, sent_at);
            """,
            reverse_sql="DROP TABLE IF EXISTS notification_logs;"
        ),
    ]
