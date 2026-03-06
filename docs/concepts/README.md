# TrustChain-AV -- Concept Documentation

This folder contains detailed explanations of every major concept and technology used in TrustChain-AV. Each document explains the "what" and "why" in simple language with real-world analogies and examples -- no code.

## The Problem

- [Deepfake Detection](deepfake-detection.md) -- What are deepfakes, why they are dangerous, and how detection systems like TrustChain-AV approach the problem

## Machine Learning

- [ResNet-50 and Fine-Tuning](resnet50-fine-tuning.md) -- How a pre-trained image recognition model is adapted to spot visual artifacts in deepfake videos
- [Wav2Vec2](wav2vec2.md) -- How a speech representation model detects synthetic or manipulated audio
- [Voice Activity Detection (VAD)](vad-voice-activity-detection.md) -- How the system decides whether a video contains speech before running audio analysis
- [Multimodal Fusion](multimodal-fusion.md) -- How visual and audio signals are combined into a single REAL/FAKE verdict

## Cryptography and Blockchain

- [SHA-256 Hashing](sha256-hashing.md) -- How cryptographic fingerprints prove a file has not been tampered with
- [Blockchain and Smart Contracts](blockchain-and-smart-contracts.md) -- How Ethereum and Solidity provide a permanent, tamper-proof record of media authenticity

## Backend

- [FastAPI](fastapi.md) -- The Python web framework that powers the REST API and background job processing
- [SQLAlchemy and Alembic](sqlalchemy-and-alembic.md) -- How the application talks to the database and manages schema changes over time
- [PostgreSQL](postgresql.md) -- The relational database that stores uploads, results, and blockchain records

## Frontend

- [React and Vite](react-and-vite.md) -- The JavaScript library and build tool that power the user interface

## Infrastructure

- [Docker and Containerization](docker-and-containerization.md) -- How containers package the entire application into a portable, reproducible environment
