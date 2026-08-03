---
title: "Set up the database"
description: "Configure the API Portal & MCP Hub to run on SQLite, PostgreSQL, or Microsoft SQL Server, including connection settings, schema, and TLS."
canonical_url: https://wso2.com/api-platform/docs/cloud/api-portal/setting-up/database/
md_url: https://wso2.com/api-platform/docs/cloud/api-portal/setting-up/database.md
tags:
  - cloud
  - api-portal
  - database
  - setting-up
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-03
content_type: "how-to"
---

{% raw %}

# Set up the database

The API Portal & MCP Hub stores its organization, catalog, application, subscription, and key data in a relational database. You can run it on any of three drivers:

| Driver | `driver` value | Best for |
|---|---|---|
| SQLite | `sqlite` | Single-node deployments, evaluation, and development |
| PostgreSQL | `postgres` | Production and high-availability deployments |
| Microsoft SQL Server | `mssql` | Production deployments standardized on SQL Server |

You select the driver and its connection settings in the `[api_portal.database]` section of `config.toml`. For the full field reference, see [Configurations](../references/configurations.md).

!!! note "Where the schema comes from"
    SQLite applies its schema automatically at startup, so no manual step is needed. PostgreSQL and SQL Server require you to apply the schema before the portal connects—see [Apply the schema for PostgreSQL or SQL Server](#apply-the-schema-for-postgresql-or-sql-server).

## Choose a driver

Set `driver` in `config.toml`, along with the connection fields the driver uses:

```toml
[api_portal.database]
driver = "sqlite"             # sqlite | postgres | mssql

# SQLite only
path = "./api-portal.db"

# PostgreSQL / MSSQL only
host = "localhost"
port = 5432                   # 1433 for MSSQL
name = "api_portal"
user = "postgres"
password = ""
```

Each field can also be supplied through an environment variable, which is useful for containerized deployments. The `config.toml` shipped with the portal reads these tokens:

| Field | Environment variable |
|---|---|
| `driver` | `APIP_AP_DATABASE_DRIVER` |
| `path` | `APIP_AP_DATABASE_PATH` |
| `host` | `APIP_AP_DATABASE_HOST` |
| `port` | `APIP_AP_DATABASE_PORT` |
| `name` | `APIP_AP_DATABASE_NAME` |
| `user` | `APIP_AP_DATABASE_USER` |
| `password` | `APIP_AP_DATABASE_PASSWORD` |

An environment variable takes effect only where `config.toml` references it with an `{{ env "..." }}` token. There's no automatic environment-variable override for arbitrary fields, so keep the tokens in place if you rely on them.

## SQLite

SQLite is the default driver and needs no external database server.

1. Set the driver and the database file path:

    ```toml
    [api_portal.database]
    driver = "sqlite"
    path = "./data/api-portal.db"
    ```

2. Make sure the directory that holds the file exists and is writable by the portal process. Under Docker Compose, the `/app/data` directory is created for you by the data volume mount. When you run the portal directly with `npm start`, create the target directory yourself first.
3. Start the portal. It applies the SQLite schema in-process on the first run, so the tables are ready without any further action.

!!! note "Path is relative to the working directory"
    A relative `path` resolves against the process working directory. Under Docker Compose that's `/app`, so `./data/api-portal.db` maps to `/app/data/api-portal.db`.

## PostgreSQL

1. Provision a PostgreSQL database and a user with privileges on it.
2. Apply the PostgreSQL schema (see [Apply the schema for PostgreSQL or SQL Server](#apply-the-schema-for-postgresql-or-sql-server)).
3. Point the portal at the database:

    ```toml
    [api_portal.database]
    driver = "postgres"
    host = "localhost"
    port = 5432
    name = "api_portal"
    user = "postgres"
    password = "<your_password>"
    ```

4. Configure the [connection pool](#connection-pool) and [TLS](#tls-for-postgresql-and-sql-server) as needed, then start the portal.

## Microsoft SQL Server

1. Provision a SQL Server database and a login with privileges on it.
2. Apply the SQL Server schema (see [Apply the schema for PostgreSQL or SQL Server](#apply-the-schema-for-postgresql-or-sql-server)).
3. Point the portal at the database. SQL Server listens on port `1433` by default:

    ```toml
    [api_portal.database]
    driver = "mssql"
    host = "localhost"
    port = 1433
    name = "api_portal"
    user = "sa"
    password = "<your_password>"
    ```

4. Configure the [connection pool](#connection-pool) and [TLS](#tls-for-postgresql-and-sql-server) as needed, then start the portal.

## Apply the schema for PostgreSQL or SQL Server

Unlike SQLite, the portal doesn't create tables for PostgreSQL or SQL Server. Apply the matching schema script against an empty database before the portal connects, as a provisioning or CI step. The scripts ship with the distribution under `resources/api-portal/db-scripts/`:

| Driver | Schema script |
|---|---|
| PostgreSQL | `schema.postgres.sql` |
| SQL Server | `schema.sqlserver.sql` |

For example, apply the PostgreSQL schema with `psql`:

```bash
psql -h localhost -U postgres -d api_portal -f schema.postgres.sql
```

For SQL Server, apply `schema.sqlserver.sql` with `sqlcmd` or another SQL Server client.

## Connection pool

The `postgres` and `mssql` drivers use a connection pool. The defaults suit most deployments; tune them for your load:

```toml
[api_portal.database]
max_open_conns = 50
min_open_conns = 2
pool_idle_timeout_ms = 10000
pool_connection_timeout_ms = 30000
pool_request_timeout_ms = 30000         # MSSQL only — per-query execution timeout
```

!!! warning "Pool settings are validated at startup"
    For the `postgres` and `mssql` drivers, `max_open_conns` must be an integer of at least 1, the remaining pool settings must be non-negative integers, and `min_open_conns` must not exceed `max_open_conns`. An invalid value stops startup with a `[FATAL]` message rather than reaching the connection pool.

SQLite ignores these settings.

## TLS for PostgreSQL and SQL Server

To encrypt the database connection, set `ssl_mode`. The default is `disable`:

```toml
[api_portal.database]
ssl_mode = "verify-full"                        # disable | verify-full
ssl_root_cert = "./resources/security/ca.pem"   # CA certificate, used by verify-full
```

With `verify-full`, the portal verifies the server certificate against the CA certificate at `ssl_root_cert`. Provide a CA certificate the database server's certificate chains to.

## Next steps

- Set the required [security keys](../references/configurations.md#security) before starting the portal.
- Configure [authentication](authentication/overview.md).
- Return to the [Getting Started](../getting-started.md) guide to run the portal.

{% endraw %}
