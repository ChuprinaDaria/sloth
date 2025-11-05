# Встановлення Docker та Docker Compose на сервері

## Перевірка поточного стану

```bash
# Перевірити чи встановлений Docker
docker --version

# Перевірити чи встановлений Docker Compose
docker-compose --version
# або
docker compose version
```

## Встановлення Docker

### Метод 1: Офіційний скрипт (рекомендовано)

```bash
# Оновити системні пакети
apt update && apt upgrade -y

# Встановити необхідні залежності
apt install -y curl wget git

# Завантажити та запустити офіційний скрипт встановлення Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Додати користувача root до групи docker (якщо потрібно)
usermod -aG docker root

# Перезавантажити сесію або виконати
newgrp docker

# Перевірити встановлення
docker --version
docker ps
```

### Метод 2: Через apt (Ubuntu/Debian)

```bash
# Оновити пакети
apt update

# Встановити необхідні пакети
apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Додати офіційний GPG ключ Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Додати репозиторій Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Встановити Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Перевірити
docker --version
docker compose version
```

## Встановлення Docker Compose

### Якщо Docker Compose не встановився автоматично

```bash
# Метод 1: Docker Compose Plugin (рекомендовано, сучасний підхід)
apt install -y docker-compose-plugin

# Перевірити
docker compose version

# Використання (замість docker-compose використовуйте docker compose)
docker compose up -d
docker compose ps
```

### Метод 2: Старий docker-compose (standalone)

```bash
# Встановити через apt
apt install -y docker-compose

# Або завантажити останню версію
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Перевірити
docker-compose --version
```

## Налаштування після встановлення

```bash
# Перезапустити Docker сервіс
systemctl restart docker
systemctl enable docker

# Перевірити статус
systemctl status docker

# Перевірити що все працює
docker ps
docker run hello-world
```

## Використання Docker Compose

### Якщо встановлений плагін (docker compose)

```bash
# Використовуйте без дефісу
docker compose up -d
docker compose ps
docker compose logs
docker compose down
```

### Якщо встановлений standalone (docker-compose)

```bash
# Використовуйте з дефісом
docker-compose up -d
docker-compose ps
docker-compose logs
docker-compose down
```

## Оновлення скриптів для використання docker compose

Якщо ви використовуєте плагін (docker compose без дефісу), можна створити alias:

```bash
# Додати в ~/.bashrc або /root/.bashrc
echo 'alias docker-compose="docker compose"' >> ~/.bashrc
source ~/.bashrc

# Тепер docker-compose працюватиме як docker compose
docker-compose --version
```

## Troubleshooting

### Помилка "Permission denied"

```bash
# Додати користувача до групи docker
usermod -aG docker $USER
newgrp docker

# Або для root
usermod -aG docker root
```

### Docker daemon не запускається

```bash
# Перевірити статус
systemctl status docker

# Перезапустити
systemctl restart docker

# Перевірити логи
journalctl -u docker
```

### Проблеми з мережею

```bash
# Перезапустити Docker
systemctl restart docker

# Перевірити Docker networks
docker network ls
```

## Швидка перевірка

```bash
# Всі команди для перевірки
docker --version
docker compose version
docker ps
docker run hello-world
```

---

**Після встановлення Docker та Docker Compose можна продовжити деплой Sloth AI!**

