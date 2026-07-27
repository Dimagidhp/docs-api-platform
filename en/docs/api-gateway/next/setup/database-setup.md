---
title: "Setting Up the Database"
description: "Create the database and apply the Gateway Controller schema for PostgreSQL or SQL Server before starting the API Platform Gateway."
canonical_url: https://wso2.com/api-platform/docs/api-gateway/setup/database-setup/
md_url: https://wso2.com/api-platform/docs/api-gateway/setup/database-setup.md
tags:
  - api-gateway
  - configuration
  - postgresql
  - sqlserver
  - devops
author: WSO2 API Platform Documentation Team
last_updated: 2026-07-26
content_type: "how-to"
---

# Setting Up the Database

The Gateway Controller persists API configurations, subscriptions, applications, keys, and other metadata in a database. Three storage backends are supported, selected through `[controller.storage].type`:

| `type` | Description | Schema provisioning |
|--------|-------------|---------------------|
| `sqlite` (default) | Embedded, file-based database (`./data/gateway.db`). Single replica only. | Created and migrated automatically on startup |
| `postgres` | External PostgreSQL. Required for multi-replica, high-availability deployments. | Must be provisioned before the controller starts |
| `sqlserver` | External Microsoft SQL Server. Required for multi-replica, high-availability deployments. | Must be provisioned before the controller starts |

If you are using `sqlite`, there is nothing to do — the controller creates the database file itself on first start, and the rest of this page does not apply.
For **PostgreSQL** and **SQL Server**, the Gateway Controller connects to the database you point it at but does not run schema DDL against it.

## Before You Begin

- A running PostgreSQL or SQL Server instance that is reachable from every Gateway Controller replica.
- An administrative account on that instance that can create databases, logins, and tables.
- A database client on the machine you run the provisioning from — `psql` for PostgreSQL, `sqlcmd` for SQL Server.

## Get the Schema Scripts

The scripts ship inside the gateway distribution:

```text
wso2apip-api-gateway-<version>/
└── resources/
    └── gateway-controller/
        └── db-scripts/
            ├── gateway-controller-db.postgres.sql
            └── gateway-controller-db.sqlserver.sql
```

If you are deploying from container images or Helm rather than the distribution zip, download them from the repository instead:

- [gateway-controller-db.postgres.sql](https://github.com/wso2/api-platform/blob/main/gateway/gateway-controller/pkg/storage/gateway-controller-db.postgres.sql)
- [gateway-controller-db.sqlserver.sql](https://github.com/wso2/api-platform/blob/main/gateway/gateway-controller/pkg/storage/gateway-controller-db.sqlserver.sql)

!!! important
    Always use the scripts that ship with the gateway version you are deploying. Applying a script from a different release can leave the schema out of step with what the controller expects.

## Step 1 - Create the Database and User

Create an empty database and a dedicated account for the gateway.

=== "PostgreSQL"

    Connect as an administrator:

    ```bash
    psql "host=<db-host> port=5432 dbname=postgres user=<admin-user> sslmode=require"
    ```

    Create the database and role:

    ```sql
    CREATE DATABASE gateway_controller;
    CREATE USER gateway WITH PASSWORD 'your-db-password';
    GRANT ALL PRIVILEGES ON DATABASE gateway_controller TO gateway;
    ```

    Grant the role ownership of the schema the tables will live in, so it can read and write them once they exist:

    ```sql
    \c gateway_controller
    GRANT ALL ON SCHEMA public TO gateway;
    ```

=== "SQL Server"

    Connect as an administrator:

    ```bash
    sqlcmd -S <db-host>,1433 -U <admin-user> -P '<admin-password>'
    ```

    Create the database, login, and user:

    ```sql
    CREATE DATABASE gateway_controller;
    GO
    CREATE LOGIN gateway WITH PASSWORD = 'your-db-password';
    GO
    USE gateway_controller;
    GO
    CREATE USER gateway FOR LOGIN gateway;
    ALTER ROLE db_owner ADD MEMBER gateway;
    GO
    ```

## Step 2 - Apply the Schema

Run the script for your database against the database you just created.

=== "PostgreSQL"

    ```bash
    psql "host=<db-host> port=5432 dbname=gateway_controller user=<admin-user> sslmode=require" \
      -v ON_ERROR_STOP=1 \
      -f resources/gateway-controller/db-scripts/gateway-controller-db.postgres.sql
    ```

    `ON_ERROR_STOP=1` makes `psql` abort and return a non-zero exit code on the first failing statement, instead of continuing and leaving a partially created schema.

=== "SQL Server"

    ```bash
    sqlcmd -S <db-host>,1433 -d gateway_controller \
      -U <admin-user> -P '<admin-password>' -b \
      -i resources/gateway-controller/db-scripts/gateway-controller-db.sqlserver.sql
    ```

    `-b` makes `sqlcmd` exit with an error code if any statement in the batch fails.

    !!! tip
        `sqlcmd` v18 and later negotiate an encrypted connection by default and reject certificates they cannot validate. If your server uses a self-signed certificate, add `-C` to trust it, or `-N` together with a properly trusted certificate.

The scripts are idempotent — every object is guarded (`CREATE TABLE IF NOT EXISTS` on PostgreSQL, `IF OBJECT_ID(...) IS NULL` on SQL Server) — so re-running them is safe and creates only what is missing.

## Step 3 - Apply the Event Gateway Schema (Event Gateway Only)

The Event Gateway stores WebSub and WebBroker artifacts in the same database, in three tables the core script does not define: `websub_apis`, `webbroker_apis`, and `webhook_secrets`. Like the core schema, these are auto-created only for `sqlite`; for external databases you must apply them yourself.

Apply the matching supplemental script after Step 2:

- [eventgateway-db.postgres.sql](https://github.com/wso2/api-platform/blob/main/event-gateway/gateway-controller/pkg/dbschema/eventgateway-db.postgres.sql)
- [eventgateway-db.sqlserver.sql](https://github.com/wso2/api-platform/blob/main/event-gateway/gateway-controller/pkg/dbschema/eventgateway-db.sqlserver.sql)

=== "PostgreSQL"

    ```bash
    psql "host=<db-host> port=5432 dbname=gateway_controller user=<admin-user> sslmode=require" \
      -v ON_ERROR_STOP=1 -f eventgateway-db.postgres.sql
    ```

=== "SQL Server"

    ```bash
    sqlcmd -S <db-host>,1433 -d gateway_controller \
      -U <admin-user> -P '<admin-password>' -b \
      -i eventgateway-db.sqlserver.sql
    ```

Skip this step if you are not running the Event Gateway.

## Step 4 - Verify the Schema

Confirm the tables exist before starting the gateway.

=== "PostgreSQL"

    ```bash
    psql "host=<db-host> port=5432 dbname=gateway_controller user=<admin-user> sslmode=require" \
      -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
    ```

=== "SQL Server"

    ```bash
    sqlcmd -S <db-host>,1433 -d gateway_controller \
      -U <admin-user> -P '<admin-password>' \
      -Q "SELECT name FROM sys.tables ORDER BY name;"
    ```

The core schema creates 15 tables:

```text
api_keys                application_api_keys    applications
artifacts               certificates            events
gateway_states          llm_providers           llm_provider_templates
llm_proxies             mcp_proxies             rest_apis
secrets                 subscription_plans      subscriptions
```

If you also applied the Event Gateway script, `websub_apis`, `webbroker_apis`, and `webhook_secrets` are present as well.

## Step 5 - Point the Gateway Controller at the Database

With the schema in place, configure the connection in `configs/config.toml`.

=== "PostgreSQL"

    ```toml
    [controller.storage]
    type = "postgres"

    [controller.storage.postgres]
    host = "<db-host>"
    port = 5432
    database = "gateway_controller"
    user = "gateway"
    password = "your-db-password"
    sslmode = "require" # disable, require, verify-ca, verify-full
    ```

=== "SQL Server"

    SQL Server uses the unified `[controller.storage.database]` block. TLS behavior is controlled by `options` rather than PostgreSQL's `sslmode`.

    ```toml
    [controller.storage]
    type = "sqlserver"

    [controller.storage.database]
    driver = "sqlserver"
    host = "<db-host>"
    port = 1433
    database = "gateway_controller"
    user = "gateway"
    password = "your-db-password"

    [controller.storage.database.options]
    encrypt = "true" # disable, false, true, strict
    trust_server_certificate = "false"
    ```

Rather than writing the password into `config.toml`, supply it through the interpolation tokens the shipped config already uses, and set the values in `api-platform.env`:

```bash
# api-platform.env
APIP_GW_CONTROLLER_STORAGE_TYPE=postgres
APIP_GW_CONTROLLER_STORAGE_POSTGRES_HOST=<db-host>
APIP_GW_CONTROLLER_STORAGE_POSTGRES_DATABASE=gateway_controller
APIP_GW_CONTROLLER_STORAGE_POSTGRES_USER=gateway
APIP_GW_CONTROLLER_STORAGE_POSTGRES_PASSWORD=your-db-password
```

For SQL Server, the shipped Compose files supply the whole connection string through `APIP_GW_CONTROLLER_STORAGE_DATABASE_DSN`. See [Gateway Configuration and Environment Interpolation](./configuration.md) for how interpolation works, and [Configuring External Storage and Backends](./storage-and-backends.md) for the rest of the storage options.

Start the gateway:

```bash
docker compose up -d
```

On startup the controller logs that it connected to the external database and that schema auto-apply was skipped. That message is expected — it confirms the controller is relying on the schema you provisioned.

## Kubernetes Deployments

The Helm charts do not include a bootstrap job that provisions the schema, so the same steps apply: create the database and run the scripts before `helm install`. Run them from any host with network access to the database — a CI job, a bastion host, or a temporary pod in the cluster:

```bash
kubectl run psql-client --rm -it --restart=Never \
  --namespace <your-namespace> \
  --image=postgres:16 -- \
  psql "host=<db-host> port=5432 dbname=gateway_controller user=<admin-user> sslmode=require"
```

Once the schema exists, follow [Database Configuration](../deployment/production-deployment/database-configuration.md) to wire the chart to the database and inject the password from a Kubernetes secret.


## Restricting Runtime Privileges

Provisioning is the only step that needs schema-altering rights. Once the tables exist, the account the controller connects with only performs `SELECT`, `INSERT`, `UPDATE`, and `DELETE`. If your security policy calls for it, apply the schema with an administrative account and give the gateway's runtime account DML privileges only.

=== "PostgreSQL"

    ```sql
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gateway;
    GRANT USAGE ON SCHEMA public TO gateway;
    ```

=== "SQL Server"

    ```sql
    USE gateway_controller;
    GO
    ALTER ROLE db_datareader ADD MEMBER gateway;
    ALTER ROLE db_datawriter ADD MEMBER gateway;
    GO
    ```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| PostgreSQL: `ERROR: relation "artifacts" does not exist` | The schema was never applied, or was applied to a different database | Re-run Step 2 against the database named in `[controller.storage.postgres].database` |
| SQL Server: `Invalid object name 'dbo.artifacts'` | Same as above | Re-run Step 2 against the database named in `[controller.storage.database].database` |
| SQL Server: `Msg 1934 ... CREATE INDEX failed ... 'QUOTED_IDENTIFIER'` | The script is from a release before the `SET` options were added | Use the script shipped with your gateway version |
| `permission denied for table ...` at runtime | The runtime account lacks DML privileges on the provisioned tables | Grant the privileges shown in [Restricting Runtime Privileges](#restricting-runtime-privileges) |
| Event Gateway fails on `websub_apis` / `webbroker_apis` / `webhook_secrets` | The supplemental Event Gateway script was not applied | Run Step 3 |
| Controller connects but logs that schema auto-apply was skipped | Expected behavior for external databases | No action needed |

---

[← Configuration & Interpolation](./configuration.md) &nbsp;|&nbsp; [Storage & Backends →](./storage-and-backends.md)
