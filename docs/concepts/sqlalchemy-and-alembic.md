# SQLAlchemy and Alembic

## The Problem: Talking to a Database

Applications need to store data permanently -- not just in memory that disappears when the server restarts. Databases solve this, but there is a fundamental mismatch: Python thinks in **objects** (classes, attributes, methods), while databases think in **tables** (rows, columns, SQL queries).

Writing raw SQL queries everywhere is tedious, error-prone, and makes it hard to switch databases later. This is where SQLAlchemy comes in.

## What is SQLAlchemy?

SQLAlchemy is an **ORM** -- an Object-Relational Mapper. It acts as a translator between Python objects and database tables.

### The Analogy

Imagine you speak English and need to communicate with someone who speaks French. You could learn French (write raw SQL), or you could use a translator (SQLAlchemy). The translator listens to you in English, converts it to French, sends it, gets the French response, and translates it back to English for you.

With SQLAlchemy:
- A Python **class** represents a database **table**
- An **instance** of that class represents a **row** in the table
- **Attributes** of the instance represent **columns** in the row

### Example in Plain English

Without an ORM, to get all uploads with a "FAKE" verdict, you would write something like:

> "Run this SQL: SELECT * FROM uploads WHERE verdict = 'FAKE' ORDER BY created_at DESC"

With SQLAlchemy, you say:

> "Give me all Upload objects where verdict equals FAKE, sorted by created_at descending"

Both produce the same result, but the SQLAlchemy version is pure Python -- no SQL string manipulation, no risk of SQL injection attacks, and your editor can autocomplete the field names.

## How TrustChain-AV Uses SQLAlchemy

### The Upload Model

TrustChain-AV has a central database table called `uploads` that stores everything about each video analysis. Think of it as a spreadsheet where each row is one analysis job:

| Column | What It Stores |
|--------|---------------|
| id | A unique identifier (UUID) for each upload |
| filename | The original name of the uploaded video file |
| status | Where the job is in the pipeline (uploading, extracting_frames, visual_analysis, etc.) |
| verdict | The final result: REAL or FAKE |
| confidence | How certain the system is (0.0 to 1.0) |
| visual_score | The score from the visual analysis model |
| audio_score | The score from the audio analysis model |
| file_hash | The SHA-256 fingerprint of the video file |
| created_at | When the upload was submitted |
| completed_at | When the analysis finished |

SQLAlchemy lets the backend code interact with this table as if it were just a Python class. When a new video is uploaded, the code creates a new Upload object, fills in its attributes, and tells SQLAlchemy to save it. SQLAlchemy handles converting that into the right SQL INSERT statement.

### Async SQLAlchemy

TrustChain-AV uses the **async** version of SQLAlchemy. Going back to the coffee shop analogy from the FastAPI doc:

- **Regular SQLAlchemy**: The barista walks to the storage room, waits for the door to open, gets the coffee beans, walks back. Nobody else gets served during this time.
- **Async SQLAlchemy**: The barista sends a message to the storage room asking for beans, and while waiting for the delivery, serves other customers. When the beans arrive, the barista picks up where they left off.

Database queries involve waiting -- waiting for the network, waiting for the disk, waiting for the database to process the query. Async SQLAlchemy lets the server do other useful work during that waiting time instead of blocking.

### Sessions and Transactions

Every interaction with the database happens inside a **session**. A session is like a shopping cart:

1. You add items to the cart (queue up database operations)
2. You go to checkout (commit the transaction)
3. Everything either succeeds together or fails together

This "all or nothing" behavior is called a **transaction**. It prevents the database from ending up in a half-updated state. For example, when TrustChain-AV updates both the verdict and the confidence score, either both get saved or neither does.

## What is Alembic?

Alembic is a **database migration tool** for SQLAlchemy. To understand why it is needed, consider this scenario:

You build your app with an uploads table that has 5 columns. A month later, you need to add a `processing_time` column. You cannot just change your Python code -- the actual database table still has 5 columns. You need to tell the database: "Hey, add this new column."

That instruction is called a **migration**.

### The Analogy

Think of Alembic as a version control system (like Git) but for your database structure:

- **Git** tracks changes to your code files over time
- **Alembic** tracks changes to your database tables over time

Each migration is a step that describes what changed:
- "Add a `file_hash` column to the uploads table"
- "Create a new `blockchain_records` table"
- "Change the `confidence` column from integer to float"

### Why Migrations Matter

Without migrations, setting up the project on a new system would require manually creating every table and column. With Alembic:

1. You clone the project
2. Run `alembic upgrade head` (one command)
3. Alembic replays every migration in order, building your database from scratch to the current state

This is exactly what TrustChain-AV's Docker setup does -- when the backend container starts, it automatically runs `alembic upgrade head` to ensure the database schema is up to date.

### Migration History

Each migration has a unique ID and knows which migration came before it, forming a chain:

```
Initial tables --> Add status column --> Add file_hash column --> Add completed_at column --> ...
```

Alembic can move forward (upgrade) or backward (downgrade) along this chain. This means if a migration causes problems, you can roll it back.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **ORM** | Object-Relational Mapper -- translates between Python objects and database rows |
| **Model** | A Python class that maps to a database table |
| **Session** | A workspace for database operations, grouped into transactions |
| **Transaction** | A set of operations that either all succeed or all fail together |
| **Migration** | A versioned change to the database structure (add table, add column, etc.) |
| **upgrade head** | Apply all pending migrations to bring the database to the latest version |
| **downgrade** | Undo a migration, reverting the database to a previous version |

## How It Fits Together

```
Python Code (Upload object)
    |
    v
SQLAlchemy (translates to SQL)
    |
    v
asyncpg (sends SQL over the network asynchronously)
    |
    v
PostgreSQL (stores the data on disk)
```

And for schema changes:

```
Developer changes the model
    |
    v
Alembic generates a migration file
    |
    v
alembic upgrade head (runs on deploy/startup)
    |
    v
PostgreSQL table structure updated
```

## Further Reading

- [PostgreSQL](postgresql.md) -- The database that SQLAlchemy talks to
- [FastAPI](fastapi.md) -- The framework that uses SQLAlchemy for data persistence
