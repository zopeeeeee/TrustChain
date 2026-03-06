# FastAPI

## What is FastAPI?

FastAPI is a modern Python web framework for building APIs (Application Programming Interfaces). An API is like a waiter in a restaurant -- you (the frontend) tell the waiter (the API) what you want, the waiter goes to the kitchen (the backend logic), and brings back your order (the response).

FastAPI is specifically designed for building **REST APIs** -- a style of API where you interact with resources using standard HTTP methods like GET (fetch data), POST (create data), PUT (update data), and DELETE (remove data).

### Why "Fast"?

The name "FastAPI" refers to two things:

1. **Fast to run**: It is one of the highest-performing Python web frameworks, comparable to Node.js and Go in benchmarks. This is because it is built on top of Starlette (an async web framework) and uses ASGI (Asynchronous Server Gateway Interface) instead of the older WSGI.

2. **Fast to develop**: It uses Python type hints to automatically generate documentation, validate incoming data, and provide editor autocomplete. You write less boilerplate code compared to older frameworks like Flask or Django REST Framework.

## How TrustChain-AV Uses FastAPI

### API Endpoints

TrustChain-AV exposes several API endpoints that the React frontend communicates with:

- **Health Check** (GET /api/health): Returns the system status and whether ML models are loaded -- like a heartbeat that says "I'm alive and ready"
- **Upload** (POST /api/uploads): Accepts a video file and returns a job ID immediately
- **Status** (GET /api/uploads/{id}/status): Returns the current processing status of a job (uploading, extracting frames, analyzing, etc.)
- **List** (GET /api/uploads): Returns a paginated list of all past analyses with search and filter support
- **Stats** (GET /api/uploads/stats): Returns aggregate counts (total analyses, how many real, how many fake)

### Asynchronous Processing

One of FastAPI's biggest strengths for TrustChain-AV is its **async support**. Here is why this matters:

Imagine a coffee shop with one barista. In a **synchronous** model, the barista takes one order, makes the entire coffee, hands it to the customer, then takes the next order. Everyone else waits.

In an **asynchronous** model, the barista takes an order, starts the coffee machine, and while it's brewing, takes the next order. The barista is always doing something useful instead of standing around waiting.

TrustChain-AV's ML analysis (ResNet-50, Wav2Vec2) takes significant time -- sometimes 30 seconds or more. Without async, the entire server would freeze while processing one video, and no other user could even check a status. With async:

1. User A uploads a video -- the server starts processing it in the background
2. While User A's video is being analyzed, User B can upload another video
3. User C can check the status of their earlier upload
4. Everyone gets served without waiting for everyone else's videos to finish

### Background Tasks

FastAPI provides a mechanism called **BackgroundTasks** that TrustChain-AV uses for the detection pipeline. When a video is uploaded:

1. The API immediately responds with "Here's your job ID" (fast response)
2. The actual heavy work (frame extraction, ML inference, fusion) runs in the background
3. The frontend polls the status endpoint to check progress

This pattern is essential because ML inference is CPU-intensive and can take a long time. You don't want the user's browser connection to time out waiting for a response.

### Lifespan Events

FastAPI has a concept called **lifespan** -- things that happen when the server starts up and shuts down. TrustChain-AV uses the startup lifespan to load ML models (ResNet-50, Wav2Vec2) into memory once. This is important because:

- Loading a model takes several seconds and hundreds of megabytes of RAM
- If models loaded on every request, each analysis would take much longer
- By loading once at startup, the models are ready in memory for instant use

Think of it like a restaurant pre-heating its ovens before opening. You don't want to wait for the oven to heat up every time someone orders a pizza.

### Automatic Validation with Pydantic

FastAPI uses a library called **Pydantic** to define the shape of data going in and out of the API. This is like having a form with required fields -- if someone submits a form without filling in the required fields, it gets rejected before any processing happens.

For example, when TrustChain-AV returns analysis results, Pydantic ensures the response always includes the right fields (verdict, confidence, visual score, etc.) in the right format. If something is missing or the wrong type, the error is caught immediately.

### Automatic API Documentation

FastAPI automatically generates interactive API documentation. When the backend is running, you can visit:

- **/docs** -- Swagger UI, an interactive page where you can try out API calls directly in the browser
- **/redoc** -- A more readable reference-style documentation

This is generated automatically from the route definitions and Pydantic models -- no extra documentation work needed.

## Key Concepts

| Concept | What It Means in TrustChain-AV |
|---------|-------------------------------|
| **Endpoint** | A specific URL path that accepts requests (e.g., /api/uploads) |
| **Route** | The mapping between a URL path and the function that handles it |
| **Request Body** | Data sent by the frontend to the backend (e.g., the uploaded video file) |
| **Response Model** | The shape of data the backend sends back (defined by Pydantic) |
| **Dependency Injection** | FastAPI's way of sharing common resources (like database connections) across routes |
| **Middleware** | Code that runs before/after every request (e.g., CORS headers for cross-origin access) |
| **ASGI** | The protocol that makes FastAPI async -- like a multi-lane highway vs. a single-lane road |

## How FastAPI Fits in the Architecture

```
Browser (React) --> HTTP Request --> FastAPI --> SQLAlchemy --> PostgreSQL
                                       |
                                       +--> Background Task --> ML Models --> Database Update
```

The frontend never talks to the database directly. Every interaction goes through FastAPI, which validates the request, performs the business logic, and returns a structured response. This separation keeps the system secure and organized.

## Further Reading

- [SQLAlchemy and Alembic](sqlalchemy-and-alembic.md) -- How FastAPI talks to the database
- [Docker and Containerization](docker-and-containerization.md) -- How FastAPI runs inside a container
