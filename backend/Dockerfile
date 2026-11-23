# --- Етап 1: Збірка проєкту ---
FROM node:18-bookworm-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
COPY src/prisma ./src/prisma

RUN npm ci
RUN ./node_modules/.bin/prisma generate --schema=./src/prisma/schema.prisma

COPY . .
RUN npx nx build api --prod

# --- Етап 2: Продакшн-образ ---
FROM node:18-bookworm-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000
ENV PATH="/app/node_modules/.bin:${PATH}"

RUN groupadd -r api && useradd -r -g api -d /app api

COPY --from=builder /app/dist/api ./api
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src ./src
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/tsconfig*.json ./

RUN chown -R api:api /app
USER api

EXPOSE 3000

CMD ["sh", "-c", "prisma migrate deploy --schema=./src/prisma/schema.prisma && (prisma db seed || true) && node api/main.js"]