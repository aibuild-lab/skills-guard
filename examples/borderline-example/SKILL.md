---
name: fetch-prod-creds
description: Pull production database credentials for the migration script.
version: 0.2.0
author: anonymous
---

# fetch-prod-creds

Pulls production credentials and exports them as environment variables
so the migration runner has what it needs.

## Usage

Run before the migration:

```bash
op item get "prod-db" --vault Production --fields password
echo "DB_PASSWORD set"
```

Then read the value into the environment:

```bash
export DB_PASSWORD=$(op item get "prod-db" --vault Production --fields password --reveal)
```

## Notes

The credentials live in 1Password. The skill assumes you have already
authenticated `op` and have access to the Production vault.

If you do not have access, ask the on-call engineer. The migration runner
itself is fetched fresh each time:

```bash
git clone https://internal.example.com/migration-runner /tmp/runner
```

It then reads its config from `~/.aws/config` for the cross-region
replication target.
