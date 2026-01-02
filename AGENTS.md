# AGENTS.md — MOVAL (Desktop Delivery Management)

This file guides coding agents (e.g., OpenAI Codex) working on this repository.
The goal is to keep all changes aligned with the project documentation (IEEE 830 SRS, RF/UC specs, UML diagrams)
and the current scope.

---

## 0) Current scope (do not change)

- Product type: **Desktop application** (downloadable). NOT a web app. NOT a mobile app.
- Roles: **Admin**, **Courier**, **Customer**.
- Database: **Relational DB** (PostgreSQL or MySQL/MariaDB). Must include **at least 3 related tables**.
- Access rule: **Only Admins may have direct DB access**. Couriers and Customers must use application logic only.

If a request conflicts with this scope, do not implement it—open an issue or propose a documented change.

---

## 1) Source of truth (documentation)

Before implementing features, read and follow:

- `docs/srs/` — IEEE 830 SRS
- `docs/requirements/` — RF/UC PDFs (e.g., “Register user” use case)
- `docs/uml/` or `diagrams/plantuml/` — UML diagrams (Use Case, Sequence, Domain Model)
- `docs/decisions/` — architectural decisions (if present)

Rule: If documentation and code disagree, do not guess. Propose a change and reference the doc section/RF/UC.

---

## 2) Key business rules (must be enforced)

### 2.1 Roles and permissions
- **Admin**
  - Create users (Admin/Courier and optionally Customer).
  - Assign shipments/packages to couriers.
  - View couriers’ performance, ranking/statistics.
  - Manage/resolve incidents.
  - Rate couriers’ workdays (if specified in SRS/RF).
- **Courier**
  - Start/end workday.
  - View assigned shipments and update delivery status.
  - Report incidents.
  - View own profile and stats (if specified).
- **Customer**
  - Self-register (role must be CUSTOMER).
  - View own orders/shipments.
  - Rate delivery (1–5) and optional comment.
  - Report incidents.

### 2.2 Registration (UC/RF “Register user”)
- Email must be **unique**.
- Password policy: **>= 8 chars** including uppercase + lowercase + number.
- Customer self-registration must **auto-assign role=CUSTOMER** (no role selector).
- Admin can create Admin/Courier accounts (role selectable for Admin).
- All user creation events should be tracked (audit log).

### 2.3 Ratings
- Rating score must be an integer in **[1..5]**.
- Rating belongs to a delivery and is authored by the customer who owns that delivery.

### 2.4 Delivery states (example)
Use a controlled state machine (adjust to SRS):
PENDING → ASSIGNED → PICKUP → EN_ROUTE → DELIVERED (or INCIDENT)

---

## 3) Database requirements (relational)

- Must enforce referential integrity:
  - foreign keys
  - uniqueness constraints (e.g., user.email)
  - checks (e.g., rating 1..5)
- Minimum recommended entities:
  - users (with role)
  - shipments/deliveries + package details
  - ratings
  - workdays (jornadas) and incidents (if included in requirements)

Do NOT migrate to NoSQL (Firebase/Firestore).

---

## 4) Repository layout (expected)

Recommended structure:
- `src/` — application code
- `db/` — schema, migrations, seed
- `docs/` — SRS, RF/UC, UML sources and exports
- `tests/` — unit/integration tests
- `scripts/` — helper scripts

If the current repo differs, follow the existing conventions and only propose restructuring if requested.

---

## 5) Implementation guidance (architecture)

Prefer a layered approach:
- UI layer (desktop screens/windows)
- Use cases / application services (e.g., RegisterUser, Login, AssignShipment)
- Domain model (entities: User, Courier, Customer, Shipment, Rating, Incident, Workday)
- Persistence layer (repositories / ORM mappings)

Avoid mixing UI code with DB logic directly.

---

## 6) What agents SHOULD do

- Implement features explicitly described in SRS/RF/UC.
- Keep changes small and traceable.
- Reference requirements in PR descriptions and commit messages:
  - Example: `RF9 - Rate delivery`, `UC-RegisterUser`.
- Update UML PlantUML sources when behavior changes.
- Add minimal tests for critical flows.

---

## 7) What agents MUST NOT do

- Do not turn the project into a web/mobile app.
- Do not switch to NoSQL.
- Do not add major new features (payments, maps APIs, push notifications) unless documented and requested.
- Do not commit secrets (passwords, DB URLs, tokens).

---

## 8) Testing / quality checklist

Before submitting changes:
- [ ] Registration: unique email + password policy + correct role assignment
- [ ] Authorization: role restrictions respected
- [ ] DB constraints still valid
- [ ] Common failures handled (duplicate email, invalid inputs, DB errors)
- [ ] Documentation/diagrams updated if needed
