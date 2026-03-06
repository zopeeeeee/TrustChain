# PostgreSQL

## What is PostgreSQL?

PostgreSQL (often called "Postgres") is a **relational database management system** (RDBMS). In simple terms, it is a highly reliable and powerful program that stores, organizes, and retrieves data.

### The Filing Cabinet Analogy

Think of PostgreSQL as a giant, intelligent filing cabinet:

- The **database** is the entire cabinet
- Each **table** is a drawer in the cabinet (e.g., one drawer for uploads, another for blockchain records)
- Each **row** in a table is a file folder in that drawer (e.g., one folder per video analysis)
- Each **column** is a label on the folder (e.g., filename, verdict, confidence)

Unlike a physical filing cabinet, PostgreSQL can:
- Search through millions of folders in milliseconds
- Ensure that two people editing the same folder at the same time do not corrupt each other's changes
- Automatically enforce rules (e.g., "every upload must have a filename")
- Recover from crashes without losing committed data

## Why PostgreSQL for TrustChain-AV?

### Relational Data

TrustChain-AV's data is naturally relational. An upload has one verdict, one set of scores, and (eventually) one blockchain registration. These relationships map cleanly to tables with columns. This is different from a document database (like MongoDB) where data is stored as flexible JSON blobs.

### ACID Compliance

PostgreSQL guarantees four properties known as ACID:

- **Atomicity**: A group of operations either all succeed or all fail. If the system crashes halfway through saving analysis results, the partial save is rolled back automatically.
- **Consistency**: The database enforces rules you define. If you say "verdict must be either REAL or FAKE," PostgreSQL will reject any attempt to store something else.
- **Isolation**: Two analyses running at the same time do not interfere with each other. Each one sees a consistent view of the data.
- **Durability**: Once the database says "saved," the data survives a power outage or crash. It is written to disk, not just held in memory.

For a system that provides trust guarantees about media authenticity, these properties are essential. You cannot have analysis results silently disappearing or getting corrupted.

### UUID Primary Keys

TrustChain-AV uses UUIDs (Universally Unique Identifiers) as primary keys instead of sequential numbers (1, 2, 3...). A UUID looks like: `550e8400-e29b-41d4-a716-446655440000`.

Why? Sequential IDs leak information. If your analysis has ID 47, someone can guess there are 46 other analyses and try IDs 1-46. UUIDs are random and unpredictable, making it impossible to enumerate or guess other users' results.

### JSON Support

PostgreSQL can store and query JSON data natively. While TrustChain-AV primarily uses regular columns, this flexibility is valuable for storing ML model metadata or blockchain transaction details that may have varying structures.

## How TrustChain-AV Uses PostgreSQL

### The Uploads Table

This is the central table that tracks every video analysis:

```
uploads
+------------+------------------+
| Column     | Type             |
+------------+------------------+
| id         | UUID (primary)   |
| filename   | text             |
| status     | text             |
| verdict    | text (nullable)  |
| confidence | float (nullable) |
| visual_score| float (nullable)|
| audio_score | float (nullable)|
| file_hash  | text (nullable)  |
| created_at | timestamp        |
| completed_at| timestamp       |
+------------+------------------+
```

When a user uploads a video, a new row is inserted with the filename and status "uploading." As the pipeline progresses, the status column is updated. When analysis completes, the verdict, confidence, and scores are filled in.

### Queries TrustChain-AV Runs

Here are the kinds of questions the application asks PostgreSQL (expressed in plain English):

- "Create a new row for this upload with filename X"
- "Update upload ABC's status to 'visual_analysis'"
- "Get all uploads sorted by date, 10 per page, page 3"
- "How many uploads have a REAL verdict? How many FAKE?"
- "Find all uploads where the filename contains 'interview'"
- "Get the full details of upload with ID XYZ"

PostgreSQL handles all of these efficiently, even with thousands of records.

### Connection Pooling

Opening a database connection is expensive -- like making a phone call, there is setup overhead (dialing, ringing, picking up). Instead of opening a new connection for every request, TrustChain-AV uses **connection pooling** via asyncpg. This maintains a pool of open connections that requests can borrow and return, like a library lending system.

### Running in Docker

In TrustChain-AV, PostgreSQL runs inside its own Docker container using the official `postgres:16-alpine` image. Alpine is a minimal Linux distribution, so the image is small. The database data is stored in a Docker **volume** called `pgdata`, which means the data survives even if the container is deleted and recreated.

The backend container connects to the database container using Docker's internal networking. The hostname is simply `db` (the service name in Docker Compose), not `localhost`.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Table** | A structured collection of rows and columns (like a spreadsheet) |
| **Row** | A single record in a table (one upload, one analysis result) |
| **Column** | A named field with a specific data type (e.g., verdict is text) |
| **Primary Key** | A unique identifier for each row (TrustChain-AV uses UUIDs) |
| **Query** | A request to read, insert, update, or delete data |
| **Index** | A data structure that speeds up searches on specific columns |
| **Transaction** | A group of operations that succeed or fail as a unit |
| **Volume** | A Docker-managed storage location that persists data across container restarts |

## Further Reading

- [SQLAlchemy and Alembic](sqlalchemy-and-alembic.md) -- How Python code interacts with PostgreSQL
- [Docker and Containerization](docker-and-containerization.md) -- How PostgreSQL runs in a container
