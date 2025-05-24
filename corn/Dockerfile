FROM python:3.10-slim

# Установка системных зависимостей + wait-for-it
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    wget \
    && wget -O /usr/local/bin/wait-for-it.sh \
    https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh \
    && apt-get remove -y wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск сервера через wait-for-it (ожидание БД)
CMD ["sh", "-c", "/usr/local/bin/wait-for-it.sh db:5432 -- python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]