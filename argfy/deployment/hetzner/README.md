# Hetzner Deployment Runbook

## SSH Access
```bash
ssh root@<IP>
```

## View Logs
```bash
docker logs argfy-backend-1
docker logs argfy-frontend-1
docker logs argfy-postgres-1
```

## Restore a Backup
```bash
# List backups
ls -la /backups/postgres/

# Restore latest
gunzip -c /backups/postgres/argfy_<date>.sql.gz | docker exec -i argfy-postgres-1 psql -U argfy -d argfy
```

## Rotate Secrets
Secrets are managed via Coolify UI:
1. Go to Project > argfy > Environment
2. Update the secret value
3. Redeploy the affected service

## Scale Up (CPX21 -> CPX31)
1. Hetzner Cloud Console: stop VPS, resize to CPX31, start
2. Coolify will auto-detect new resources
3. Optionally adjust `WEB_CONCURRENCY` if scheduler is moved out

## Stop Scheduler (Runaway)
```bash
docker exec argfy-backend-1 python -c "from app.scheduler import scheduler; scheduler.shutdown(wait=False)"
```
