# Python asosidagi obraz
FROM python:3.10-slim

# Kerakli tizim vositalarini o'rnatish
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Ollamani yuklab olish va o'rnatish
RUN curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama && chmod +x /usr/bin/ollama

# Ishchi katalogni yaratish
WORKDIR /app
COPY . .

# Python kutubxonalarini o'rnatish
RUN pip install --no-cache-dir -r requirements.txt

# Portni ochish
EXPOSE 10000

# Script yaratish: Ollamani fonda yoqish, modelni yuklash va keyin FastAPI ni yoqish
RUN echo '#!/bin/bash\nollama serve &\nsleep 5\nollama pull llama3.2:1b\nuvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}' > start.sh
RUN chmod +x start.sh

# Start scriptni ishga tushirish
CMD ["./start.sh"]