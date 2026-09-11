# Demo script
Start infrastructure with `docker compose up -d`, then run `D:\APOLLO\.venv\Scripts\python.exe -m app.cli --demo safety`, `--demo rag`, and `--demo booking`. Booking uses the fictional seeded patient and requires the real Redis lease, PostgreSQL atomic commit, and generated HTML/PDF confirmation. Email and calendar are simulated and labeled.
