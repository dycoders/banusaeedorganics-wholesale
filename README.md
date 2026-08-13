# BSO Wholesale Integration for ERPNext 16

Receives signed Banu Saeed Organics WordPress wholesale inquiries and creates or updates ERPNext Leads.

## Install

From the ERPNext bench directory:

```bash
bench get-app /path/to/bso_wholesale_integration
bench --site YOUR-SITE install-app bso_wholesale_integration
bench --site YOUR-SITE set-config bso_wholesale_secret 'PASTE-A-32-CHARACTER-OR-LONGER-RANDOM-SECRET'
bench --site YOUR-SITE migrate
bench restart
```

Endpoint:

```text
https://YOUR-ERP-DOMAIN/api/method/bso_wholesale_integration.api.receive_wholesale_lead
```

Use the exact same secret in the WordPress plugin settings. Generate one with:

```bash
openssl rand -hex 32
```

The app adds four custom fields to Lead and never creates a Customer.

