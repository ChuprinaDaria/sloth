# Sphere-Based Integration System

## Огляд

Нова система інтеграцій на основі сфер діяльності (Sphere). Кожен користувач вибирає свою сферу при реєстрації, і йому показуються тільки релевантні інтеграції.

## Сфери (Spheres)

### 1. General (Загальна)
- Підходить для всіх типів бізнесу
- Має доступ до базових інтеграцій

### 2. Beauty & Wellness (Краса)
- Салони краси, спа, барбершопи, майстри
- Спеціалізовані інтеграції: Booksy, Dikidi, EasyWeek, Treatwell, Planity, Reservio, Salonized, SimplyBook.me, Square Appointments, Fresha

### 3. Health & Medical (Здоров'я)
- Медичні клініки, лікарі, стоматологи, фізіотерапевти
- Спеціалізовані інтеграції: Znany Lekarz/Doctoralia, Doctolib, Jameda, Doc.ua, Helsi, Patient Access, Zocdoc, Practo

## Інтеграції

### Загальні інтеграції (доступні всім сферам):

**Google Suite:**
- Google Calendar
- Google Meet
- Google Sheets
- Gmail

**Соціальні мережі та месенджери:**
- Telegram ⏰ (підтримує Working Hours)
- WhatsApp
- Instagram ⏰ (підтримує Working Hours)
- Facebook Messenger ⏰ (підтримує Working Hours)

**Scheduling:**
- Calendly
- Zoom

### Beauty інтеграції:

| Інтеграція | Країни |
|-----------|--------|
| Booksy | PL, US, GB, CA, AU |
| Dikidi | UA |
| EasyWeek | UA, PL |
| Treatwell | GB, DE, FR, ES, IT |
| Planity | FR, BE |
| Reservio | ES, CZ, SK |
| Salonized | NL, BE |
| SimplyBook.me | Global |
| Square Appointments | Global |
| Fresha | GB, Global |

### Health інтеграції:

| Інтеграція | Країни |
|-----------|--------|
| Znany Lekarz / Doctoralia | PL, ES, IT, BR, MX |
| Doctolib | FR, DE, IT |
| Jameda | DE |
| Doc.ua | UA |
| Helsi | UA |
| Patient Access | GB |
| Zocdoc | US |
| Practo | IN |

## Working Hours (Години роботи AI агента)

Для інтеграцій, які підтримують Working Hours (Telegram, Instagram, Facebook Messenger), користувач може налаштувати:

- **Дні тижня**: коли AI агент працює
- **Години роботи**: з якого до якого часу
- **Часовий пояс**: автоматично з профілю користувача

Приклад:
```
Понеділок-П'ятниця: 09:00 - 18:00
Субота: 10:00 - 14:00
Неділя: вимкнено
```

## Backend Architecture

### Models

#### Sphere (public schema)
```python
- name: CharField
- slug: SlugField
- description: TextField
- icon: CharField
- color: CharField
- is_active: BooleanField
- order: IntegerField
```

#### IntegrationType (public schema)
```python
- slug: SlugField
- name: CharField
- integration_type: CharField (choices)
- description: TextField
- spheres: ManyToManyField(Sphere)
- requires_oauth: BooleanField
- oauth_provider: CharField
- supports_webhooks: BooleanField
- supports_working_hours: BooleanField
- available_countries: JSONField
- is_active: BooleanField
- order: IntegerField
```

#### Profile (tenant schema)
```python
- user_id: IntegerField
- sphere_id: IntegerField  # NEW
- business_name: CharField
- ...
```

#### Integration (tenant schema)
```python
- user_id: IntegerField
- integration_type_id: IntegerField  # NEW
- integration_type_slug: CharField  # NEW
- status: CharField
- credentials_encrypted: TextField
- settings: JSONField
- ...
```

#### IntegrationWorkingHours (tenant schema)
```python
- integration: ForeignKey(Integration)
- weekday: IntegerField (0=Monday, 6=Sunday)
- start_time: TimeField
- end_time: TimeField
- is_enabled: BooleanField
```

### API Endpoints

**Accounts app:**
- `GET /api/accounts/spheres/` - List all active spheres
- `GET /api/accounts/spheres/{slug}/` - Get sphere details
- `GET /api/accounts/integration-types/` - List all integration types
- `GET /api/accounts/integration-types/?sphere_id=1` - Filter by sphere
- `GET /api/accounts/integration-types/?sphere_slug=beauty` - Filter by sphere slug
- `GET /api/accounts/integration-types/{slug}/` - Get integration type details

**Integrations app:**
- `GET /api/integrations/api/` - List user's integrations
- `POST /api/integrations/api/` - Create new integration
- `GET /api/integrations/api/{id}/` - Get integration details
- `PUT /api/integrations/api/{id}/` - Update integration
- `DELETE /api/integrations/api/{id}/` - Delete integration
- `POST /api/integrations/api/{id}/activate/` - Activate integration
- `POST /api/integrations/api/{id}/deactivate/` - Deactivate integration
- `GET /api/integrations/api/{id}/working_hours/` - Get working hours
- `POST /api/integrations/api/{id}/working_hours/` - Set working hours

**Working Hours:**
- `GET /api/integrations/api/working-hours/` - List all working hours
- `POST /api/integrations/api/working-hours/` - Create working hour
- `PUT /api/integrations/api/working-hours/{id}/` - Update working hour
- `DELETE /api/integrations/api/working-hours/{id}/` - Delete working hour

### Management Commands

**Populate initial data:**
```bash
python manage.py populate_spheres_integrations
```

This command creates:
- 3 spheres (General, Beauty, Health)
- 28 integration types
- M2M relationships between spheres and integrations

## Frontend Integration

### Registration Flow

1. User fills basic info (name, email, password)
2. User selects **Sphere** from dropdown:
   - General
   - Beauty & Wellness
   - Health & Medical
3. User completes registration
4. sphere_id is saved to Profile

### Integrations Page

**Available Integrations Tab:**
- Shows integrations filtered by user's sphere
- Each integration shows:
  - Name, icon, description
  - "Connect" button
  - Country availability badge

**Connected Integrations Tab:**
- Shows user's active integrations
- Each integration shows:
  - Status badge
  - Settings button
  - Working Hours button (if supported)
  - Disconnect button

### Working Hours Modal

For integrations that support working hours (Telegram, Instagram, Facebook Messenger):

```
┌─────────────────────────────────┐
│ Working Hours for Telegram      │
├─────────────────────────────────┤
│ Monday    [x] 09:00 - 18:00    │
│ Tuesday   [x] 09:00 - 18:00    │
│ Wednesday [x] 09:00 - 18:00    │
│ Thursday  [x] 09:00 - 18:00    │
│ Friday    [x] 09:00 - 18:00    │
│ Saturday  [ ] 10:00 - 14:00    │
│ Sunday    [ ]                   │
│                                 │
│         [Cancel]  [Save]        │
└─────────────────────────────────┘
```

## Subscription Packages

### Package 2 (Starter) - Найдешевший платний
- Всі базові інтеграції
- Sphere-specific інтеграції
- Working Hours для Meta та Telegram
- До 1000 повідомлень/місяць

### Package 3 (Professional)
- Все з Package 2
- **Embeddings з відгуків клієнтів**
- **Розумна аналітика для інтеграцій:**
  - Найпопулярніші години запитів
  - Топ питання клієнтів
  - Sentiment analysis відгуків
  - Рекомендації по покращенню обслуговування

## Implementation Checklist

### Backend ✅
- [x] Create Sphere model
- [x] Create IntegrationType model
- [x] Update Integration model
- [x] Create IntegrationWorkingHours model
- [x] Add sphere_id to Profile
- [x] Django Admin configuration
- [x] Create management command
- [x] Create serializers
- [x] Create API ViewSets
- [x] Configure URL routing

### Frontend
- [ ] Update RegisterForm with sphere selection
- [ ] Create API services
- [ ] Create Integrations Page
- [ ] Create Integration Connect components
- [ ] Create Working Hours component
- [ ] Add routing

### Testing
- [ ] Test sphere selection at registration
- [ ] Test integration filtering by sphere
- [ ] Test integration connection flow
- [ ] Test working hours configuration
- [ ] Test embeddings (Package 3)
- [ ] Test analytics (Package 3)

## Next Steps

1. Run migrations
2. Populate initial data
3. Update frontend
4. Test integration flows
5. Add OAuth handlers for each integration
6. Implement embeddings and analytics for Package 3
