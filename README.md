# Radicale Custom Fork – Shared Calendar Symlinks

This is a custom fork of [tomsquest/docker-radicale](https://github.com/tomsquest/docker-radicale) that adds **shared collection support** using symlinks. This allows multiple users to see shared calendars alongside their private calendars, while maintaining **read/write access** for all shared calendars.

---

## Features

- Shared collections appear **inside each user’s personal collection**.
- Users retain their **private calendars**.
- Symlinks are created automatically on container startup.
- `SHARED_COLLECTIONS` is configurable via environment variables.
- Fully compatible with the upstream Radicale Docker image.

---

## Example Use Case

**Family calendar setup:**

- Users: `bob`, `alice`, `dad`
- Each user has a **private calendar**.
- A shared collection called `familycalendar` contains one calendar per family member:
  - /data/collections/collection-root/familycalendar/bob.ics
  - /data/collections/collection-root/familycalendar/alice.ics
  - /data/collections/collection-root/familycalendar/dad.ics
- After symlink creation, users see shared calendars inside their personal collection:
  - /data/collections/collection-root/bob/bob.ics # private
  - /data/collections/collection-root/bob/familycalendar -> ../familycalendar # shared
- Same for `alice` and `dad`.  

✅ All shared calendars are **read/write**, while private calendars remain isolated.

---

## Environment Variables

| Variable            | Default                       | Description                                         |
|--------------------|-------------------------------|-----------------------------------------------------|
| UID                | 1065                          | UID to run Radicale inside container               |
| GID                | 100                           | GID to run Radicale inside container               |
| COLLECTION_ROOT    | /data/collections/collection-root | Root folder for user collections                  |
| SHARED_COLLECTIONS | empty                         | Comma-separated list of shared collections to symlink for all users |

**Example in `docker-compose.yml`:**

```yaml
environment:
  - UID=1065
  - GID=100
  - COLLECTION_ROOT=/data/collections/collection-root
  - SHARED_COLLECTIONS=/familycalendar

Folder Structure
Before Symlinks

/data/collections/collection-root/
├── bob/                  🧑
│   └── bob.ics           📅 private
├── alice/                 👩
│   └── alice.ics          📅 private
├── dad/                  👨
│   └── dad.ics           📅 private
└── familycalendar/       👪 shared
    ├── bob.ics           📅 shared
    ├── alice.ics          📅 shared
    └── dad.ics           📅 shared

After Symlinks

/data/collections/collection-root/
├── bob/                  🧑
│   ├─ bob.ics           📅 private
│   └─ familycalendar 🔗 ──> ../familycalendar  # shared
├── alice/                 👩
│   ├─ alice.ics          📅 private
│   └─ familycalendar 🔗 ──> ../familycalendar  # shared
├── dad/                  👨
│   ├─ dad.ics           📅 private
│   └─ familycalendar 🔗 ──> ../familycalendar  # shared
└── familycalendar/       👪 shared
    ├─ bob.ics           📅 shared
    ├─ alice.ics          📅 shared
    └─ dad.ics           📅 shared

Quick Start Diagram

┌─────────────────────────────┐
│ Environment Variables       │
│-----------------------------│
│ UID=1065                    │
│ GID=100                     │
│ COLLECTION_ROOT=/data/...   │
│ SHARED_COLLECTIONS=/familycalendar
└─────────────┬──────────────┘
              │
              ▼
┌─────────────────────────────┐
│ Container Startup           │
│-----------------------------│
│ 1️⃣ Run create_symlinks.py  │
│ 2️⃣ Create symlinks for     │
│    each user to shared      │
│    collections              │
└─────────────┬──────────────┘
              │
              ▼
┌─────────────────────────────┐
│ Folder Structure After      │
│ Symlinks                    │
│-----------------------------│
│ bob/                        │
│ ├─ bob.ics  📅 private       │
│ └─ familycalendar 🔗 ─────► /data/.../familycalendar/  │
│ alice/                       │
│ ├─ alice.ics  📅 private      │
│ └─ familycalendar 🔗 ─────► /data/.../familycalendar/  │
│ dad/                        │
│ ├─ dad.ics  📅 private       │
│ └─ familycalendar 🔗 ─────► /data/.../familycalendar/  │
└─────────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│ Radicale & CalDAV Clients   │
│-----------------------------│
│ Users can now access        │
│ both private and shared     │
│ calendars in the same view  │
└─────────────────────────────┘

Assigning Rights to Shared Calendars

Creating symlinks is not enough—you must also grant access to the shared calendars in Radicale’s rights file.
Otherwise, users won’t see the shared collections in the GUI or CalDAV clients.
Example rights entries:

# Allow all users read/write access to shared collection "familycalendar"
[familycalendar]
user: .+
collection: familycalendar(|/.*)
permissions: RW

    user: .+ means all authenticated users.

    collection can include subfolders using (|/.*) syntax.

    permissions: RW gives read/write access to the shared calendar(s).

After updating the rights file, restart the container or reload Radicale to apply changes:

docker-compose restart radicale

Setup Instructions

    Build the custom image:

docker build -t radicale-custom -f Dockerfile.custom .

    Run the container:

docker-compose up -d

    Add shared collections under COLLECTION_ROOT if not already present.

    Verify symlinks inside each user folder:

/data/collections/collection-root/bob/familycalendar -> ../familycalendar

    Add new shared calendars: place the .ics files in the shared collection folder and restart the container or rerun the symlink script manually:

docker exec -it radicale su-exec 1065:100 python3 /usr/local/bin/create_symlinks.py

Notes / Best Practices

    Keep SHARED_COLLECTIONS empty by default if you don’t want any pre-linked collections.

    The symlink script is idempotent; safe to run multiple times.

    Ensure correct UID/GID for permissions; otherwise, symlink creation may fail.

    Users’ private calendars remain untouched.

    Compatible with CalDAV clients like DavX5, Thunderbird, or Apple Calendar.

License

Same as the upstream tomsquest/docker-radicale
repository (MIT License).