## Migrations

### Run migrations

```bash
alembic upgrade head
```

### Create db migration

```bash
alembic revision --autogenerate -m 'Migration message'
```

## Development

```bash
docker compose -f compose.yml -f compose.dev.yml up -d
```
