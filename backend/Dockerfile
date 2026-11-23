# --- Етап 1: Збірка проєкту ---
FROM node:18-bullseye-slim AS builder

WORKDIR /app

# Встановлюємо openssl та сертифікати, щоб Prisma коректно визначила OpenSSL 1.1.x
RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
COPY src/prisma ./src/prisma

RUN npm ci
RUN ./node_modules/.bin/prisma generate --schema=./src/prisma/schema.prisma

COPY . .
RUN npx nx build api --prod

# --- Етап 2: Продакшн-образ ---
FROM node:18-bullseye-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

RUN groupadd -r api && useradd -r -g api -d /app api

COPY --from=builder /app/dist/api ./api
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src/prisma ./src/prisma

RUN chown -R api:api /app
USER api

EXPOSE 3000

CMD ["sh", "-c", "./node_modules/.bin/prisma migrate deploy --schema=./src/prisma/schema.prisma && node api/main.js"]