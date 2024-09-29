# Используем официальный базовый образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в рабочую директорию
COPY . /app

# Устанавливаем переменную окружения для Flask
ENV PORT=8080

# Открываем порт
EXPOSE 8080

# Запускаем приложение
CMD ["python", "Visualization.py"]