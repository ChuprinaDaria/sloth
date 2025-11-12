# Як перевірити BACKEND_URL на сервері

## Правильна команда для перевірки:

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py shell -c "from django.conf import settings; print('BACKEND_URL:', settings.BACKEND_URL)"
```

Або через Django shell:

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py shell
```

Потім в Python shell:
```python
from django.conf import settings
print(settings.BACKEND_URL)
exit()
```

## Якщо BACKEND_URL все ще localhost:

1. **Перевірте чи .env файл правильний:**
```bash
cat /opt/sloth/backend/.env | grep BACKEND_URL
```

2. **Перевірте чи docker-compose читає .env:**
```bash
# Перевірте чи файл існує
ls -la /opt/sloth/backend/.env

# Перевірте чи docker-compose.prod.yml вказує на правильний шлях
grep -A 2 "env_file" /opt/sloth/docker-compose.prod.yml
```

3. **Повний перезапуск (якщо просто restart не допоміг):**
```bash
cd /opt/sloth
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

4. **Перевірте чи змінна передається в контейнер:**
```bash
docker compose -f docker-compose.prod.yml exec backend printenv | grep BACKEND_URL
```

## Якщо все ще не працює:

Можливо потрібно явно передати через environment в docker-compose.prod.yml:

```yaml
backend:
  environment:
    - BACKEND_URL=${BACKEND_URL}
```

Або встановити безпосередньо в docker-compose.prod.yml:
```yaml
backend:
  environment:
    - BACKEND_URL=https://sloth-ai.lazysoft.pl
```

