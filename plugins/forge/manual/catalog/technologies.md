# Technology catalog

Defaults for building products. Statuses are defined in [README.md](README.md). Choose with the project's requirements in hand. Any deviation from an `Adopted` default needs a stated reason.

## Languages and frameworks

### C# / ASP.NET Core

- **Purpose:** Typed backend services and APIs.
- **Use cases:** Business APIs, line-of-business systems, high-throughput services.
- **Trade-offs:** Strong tooling and performance. Heavier images than Go. Windows-centric legacy patterns exist.
- **Security:** Built-in authentication and authorization, data protection and anti-forgery. Keep the SDK patched.
- **Cost:** Runs on Linux containers. No license cost for .NET.
- **Operational complexity:** Low to medium.
- **Alternatives:** Python/FastAPI, Node.js/TypeScript.
- **Status:** Adopted

### Entity Framework Core

- **Purpose:** ORM for .NET with migrations.
- **Use cases:** CRUD-heavy domains on relational databases.
- **Trade-offs:** Productivity versus hidden N+1 queries and generated SQL. Use raw SQL or Dapper for hot paths.
- **Security:** Parameterized by default. Avoid `FromSqlRaw` with interpolated input.
- **Cost:** None.
- **Operational complexity:** Low. Migrations need the expand/contract discipline.
- **Alternatives:** Dapper.
- **Status:** Adopted

### Python / FastAPI

- **Purpose:** Async Python APIs with typed models (Pydantic).
- **Use cases:** APIs, automation services, data and ML-adjacent backends.
- **Trade-offs:** Fast to build. The runtime is slower than .NET or Go. Typing is only enforced with mypy or pyright.
- **Security:** Validate with Pydantic models. Pin dependencies and audit them with pip-audit.
- **Cost:** None.
- **Operational complexity:** Low.
- **Alternatives:** ASP.NET Core, Node.js.
- **Status:** Adopted

### TypeScript / Node.js

- **Purpose:** JavaScript runtime with static typing.
- **Use cases:** APIs sharing types with the frontend, tooling, serverless functions.
- **Trade-offs:** Large ecosystem, but dependency sprawl means supply-chain risk.
- **Security:** Use lockfiles and `npm audit`. Avoid unmaintained packages.
- **Cost:** None.
- **Operational complexity:** Low.
- **Alternatives:** Python, .NET.
- **Status:** Adopted

### Next.js

- **Purpose:** React framework with server rendering and routing.
- **Use cases:** Web frontends, full-stack apps with light backend needs.
- **Trade-offs:** Fast delivery. Hosting is coupled to platform features. Rapid version churn.
- **Security:** Keep server-only code and secrets out of client bundles. Validate server actions.
- **Cost:** Static or edge hosting is cheap. SSR has compute cost.
- **Operational complexity:** Low to medium.
- **Alternatives:** Vite + React SPA, Astro for content sites.
- **Status:** Adopted

## Data stores

### PostgreSQL

- **Purpose:** General-purpose relational database.
- **Use cases:** Default system of record. JSONB for semi-structured data.
- **Trade-offs:** Feature-rich. Needs tuning and vacuum awareness at scale.
- **Security:** TLS, least-privilege roles, no superuser for apps.
- **Cost:** Open source. Managed offerings cost by instance size.
- **Operational complexity:** Medium self-hosted, low managed.
- **Alternatives:** MySQL, SQL Server.
- **Status:** Adopted

### MySQL

- **Purpose:** Relational database.
- **Use cases:** Existing ecosystems and hosting that standardize on it.
- **Trade-offs:** Mature and fast reads. Fewer advanced features than PostgreSQL.
- **Security:** Same as PostgreSQL.
- **Cost:** Open source.
- **Operational complexity:** Medium self-hosted, low managed.
- **Alternatives:** PostgreSQL.
- **Status:** Adopted

### SQL Server

- **Purpose:** Relational database in the Microsoft ecosystem.
- **Use cases:** Enterprises already licensed. Tight .NET integration.
- **Trade-offs:** Strong tooling, but licensing cost and weaker portability.
- **Security:** Integrated authentication, TDE, least-privilege logins.
- **Cost:** License cost beyond the Express edition.
- **Operational complexity:** Medium.
- **Alternatives:** PostgreSQL.
- **Status:** Adopted (when already required)

## Infrastructure and delivery

### Docker and Docker Compose

- **Purpose:** Container images and local multi-service environments.
- **Use cases:** Reproducible builds, local development, deployment artifacts.
- **Trade-offs:** Portability versus image hygiene work.
- **Security:** Non-root user, minimal base images, image scanning, no secrets in layers.
- **Cost:** None.
- **Operational complexity:** Low.
- **Alternatives:** Podman.
- **Status:** Adopted

### Kubernetes / OpenShift

- **Purpose:** Container orchestration platform.
- **Use cases:** Many services, autoscaling, platform teams. OpenShift adds enterprise policy and a developer platform.
- **Trade-offs:** Powerful but operationally heavy for small teams.
- **Security:** RBAC, network policies, pod security standards, secret encryption.
- **Cost:** Control-plane and node costs plus operations time.
- **Operational complexity:** High.
- **Alternatives:** Managed container services or PaaS.
- **Status:** Assess (learning). Trial only with a demonstrated need.

### Terraform / OpenTofu

- **Purpose:** Declarative multi-provider provisioning.
- **Use cases:** Cloud infrastructure, DNS, SaaS configuration.
- **Trade-offs:** Large ecosystem. State management is the main risk. Terraform is under the BSL license; OpenTofu is MPL.
- **Security:** Encrypted, locked remote state. Plan review. Scan modules.
- **Cost:** Free CLI.
- **Operational complexity:** Medium.
- **Alternatives:** Provider-native IaC, Pulumi.
- **Status:** Adopted

### Ansible

- **Purpose:** Agentless configuration management over SSH or WinRM.
- **Use cases:** Configuring long-lived servers and network devices.
- **Trade-offs:** Simple YAML, but slow at scale and idempotency depends on the module.
- **Security:** Vault for secrets, least-privilege become.
- **Cost:** Free.
- **Operational complexity:** Low to medium.
- **Alternatives:** Cloud-init, immutable images.
- **Status:** Adopted (for host configuration only)

### GitHub Actions

- **Purpose:** CI/CD integrated with GitHub.
- **Use cases:** Build, test, scan, release and deploy with OIDC to clouds.
- **Trade-offs:** Convenient. Third-party actions are a supply-chain risk, so pin them by SHA.
- **Security:** OIDC instead of static keys, least-privilege `permissions:`, pinned actions.
- **Cost:** Free minutes on public repos. Metered on private repos.
- **Operational complexity:** Low.
- **Alternatives:** GitLab CI, Azure Pipelines.
- **Status:** Adopted
