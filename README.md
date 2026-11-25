- docker compose up --build -d
- http://localhost:4200

## Deployment from GitHub Container Registry (GHCR)

The project supports two Docker Compose workflows:

- `docker-compose.yml` builds the backend and frontend locally from source.
- `docker-compose.ghcr.yml` pulls prebuilt backend and frontend images published by GitHub Actions after successful CI checks.

### Requirements

Docker Engine and Docker Compose v2.

### Start the published application

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholder `POSTGRES_PASSWORD` and `JWT_SECRET` values with long, random secrets. Keep `POSTGRES_PASSWORD` alphanumeric because it is interpolated into a database URL. Do not commit `.env`.

```bash
docker compose -f docker-compose.ghcr.yml config --quiet
docker compose -f docker-compose.ghcr.yml pull
docker compose -f docker-compose.ghcr.yml up -d --no-build
docker compose -f docker-compose.ghcr.yml ps
```

Open http://localhost:4201 (or `http://<server-ip>:4201` from another computer). The backend API is exposed at port `3001`. If these host ports are already in use, change `FRONTEND_PORT` and `BACKEND_PORT` in `.env` before starting.

To check the API:

```bash
curl -f http://localhost:3001/api/articles
curl -f http://localhost:4201/api/articles
```

To stop the GHCR deployment without deleting the database volume:

```bash
docker compose -f docker-compose.ghcr.yml down
```

To update to the latest published images:

```bash
docker compose -f docker-compose.ghcr.yml pull
docker compose -f docker-compose.ghcr.yml up -d --no-build
```

To deploy an exact CI/CD build, set `IMAGE_TAG=sha-<full-commit-sha>` in `.env` and run the same `pull` and `up` commands. Both images are selected by the same tag.

**Note:** The default GHCR Compose project is named `realworld-ghcr`. It uses its own PostgreSQL volume, separate from the source-build Compose project. The two stacks can coexist when their host ports do not overlap.
