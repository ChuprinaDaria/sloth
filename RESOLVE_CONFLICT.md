# Вирішення конфлікту на сервері

## На сервері виконайте:

```bash
cd /opt/sloth

# 1. Перевірити на якій гілці ви
git branch

# 2. Перейти на main (якщо не на main)
git checkout main

# 3. Відкинути локальні зміни і використати версію з main
git checkout --theirs docker-compose.prod.yml
git add docker-compose.prod.yml

# 4. Або просто скопіювати правильний файл
git checkout origin/main -- docker-compose.prod.yml
git add docker-compose.prod.yml

# 5. Завершити merge
git commit -m "Вирішено конфлікт - використано версію з main"

# 6. Оновити з main
git pull origin main
```

## Альтернатива - повний скид:

```bash
cd /opt/sloth

# Якщо локальні зміни не важливі
git reset --hard origin/main
git pull origin main
```

## Після вирішення конфлікту:

```bash
# Перебілдити backend
docker compose -f docker-compose.prod.yml build backend
docker compose -f docker-compose.prod.yml up -d --build backend

# Перевірити статус
docker compose -f docker-compose.prod.yml ps
```

