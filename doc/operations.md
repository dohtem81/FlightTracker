# Operations

## Start / Rebuild
From repository root:

```powershell
docker compose up -d --build
```

## Check Health

Reader:
```powershell
Invoke-RestMethod -Uri http://localhost:8010/health | ConvertTo-Json
```

Reader data:
```powershell
Invoke-RestMethod -Uri "http://localhost:8010/api/states?limit=5" | ConvertTo-Json -Depth 4
```

Web UI:
- Open `http://localhost:8080`

## Useful Logs

Collector logs:
```powershell
docker logs flighttracker-api1 --tail 100
```

Reader logs:
```powershell
docker logs flighttracker-api-read --tail 100
```

Cassandra logs:
```powershell
docker logs cassandra1 --tail 100
```

## Common Issues

### No aircraft on map
- Confirm reader endpoint returns non-empty `states`.
- Verify collector logs for OAuth or OpenSky failures.
- Verify Cassandra is healthy and writable.

### `table latest_states does not exist`
- Backend includes schema self-heal and retry logic.
- If still persistent, restart backend stack after Cassandra is healthy.

### Credentials error
- Ensure `config/credentials.json` exists with `clientId` and `clientSecret`.
- Ensure file is mounted in compose and ignored by git.
