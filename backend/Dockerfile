# --- Етап 1: Збірка проєкту ---
FROM node:18-alpine AS builder

WORKDIR /app

# Копіюємо маніфести залежностей та схему Prisma
COPY package*.json ./
COPY src/prisma ./src/prisma

RUN npm ci
RUN npx prisma generate --schema=./src/prisma/schema.prisma

# Копіюємо решту коду та збираємо проєкт через Nx
COPY . .
RUN npx nx build api --prod

# --- Етап 2: Продакшн-образ ---
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

RUN addgroup --system api && adduser --system -G api api

# Копіюємо зібраний бандл, залежності та схему/міграції Prisma
COPY --from=builder /app/dist/api ./api
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src/prisma ./src/prisma

RUN chown -R api:api /app
USER api

EXPOSE 3000

# Спочатку накатуємо міграції в БД, потім запускаємо API
CMD ["sh", "-c", "npx prisma migrate deploy --schema=./src/prisma/schema.prisma && node api"]