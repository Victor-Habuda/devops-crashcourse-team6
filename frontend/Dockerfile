# --- Етап 1: Збірка Angular через Bun ---
FROM oven/bun:1-alpine AS builder

WORKDIR /app

COPY package.json bun.lock* ./
RUN bun install

COPY . .
RUN bun run build

# --- Етап 2: Роздача статики через Nginx ---
FROM nginx:alpine AS runner

# Видаляємо дефолтний конфіг Nginx і додаємо наш
RUN rm -rf /usr/share/nginx/html/*
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Angular application-білдер кладе файли в dist/<назва-проєкту>/browser
COPY --from=builder /app/dist/*/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]