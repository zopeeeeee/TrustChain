# TrustChain-AV: Frontend-Backend Integration Guide

## Overview

This project has been updated to connect the frontend (React/TypeScript) with a Flask backend API. The Streamlit UI has been completely removed and replaced with a REST API architecture.

## Architecture

```
Frontend (React)  ←→  Flask API  ←→  PyTorch/ResNet50
├── App.tsx                ├── /api/analyze
├── Components             ├── /api/health
└── UI Elements            └── /api/info
                           
                           Backend Processing
                           ├── Image Analysis
                           ├── ResNet50 Features
                           ├── Quality Metrics
                           └── SHA-256 Hashing
```

## Setup Instructions

### 1. Backend Setup

#### Prerequisites
- Python 3.8 or higher
- pip package manager

#### Installation

1. Navigate to the backend folder:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

#### Running the Backend

```bash
python app.py
```

The Flask server will start on `http://localhost:5000`

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * WARNING: This is a development server. Do not use it in production.
```

### 2. Frontend Setup

#### Prerequisites
- Node.js 16.x or higher
- npm or yarn package manager

#### Installation

1. Navigate to the frontend folder:
```bash
cd Frontend
```

2. Install dependencies:
```bash
npm install
```

#### Running the Frontend

```bash
npm run dev
```

The development server will start. Open your browser to the provided URL (typically `http://localhost:5173`)

## API Endpoints

### 1. Health Check
**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy"
}
```

### 2. Image Analysis
**Endpoint:** `POST /api/analyze`

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Form data with `image` file field

**Response:**
```json
{
  "success": true,
  "authenticityScore": 75.5,
  "sharpnessScore": 85.2,
  "colorVariance": 62.1,
  "prediction": "authentic",
  "label": "Likely Original / Authentic",
  "interpretation": ["Natural sharpness → typical of real images."],
  "hash": "a1b2c3d4e5f6...",
  "blockchainStatus": "verified"
}
```

### 3. System Information
**Endpoint:** `GET /api/info`

**Response:**
```json
{
  "name": "TrustChain-AV",
  "version": "1.1",
  "description": "AI-based Image Authenticity Verification using ResNet and Blockchain Hashing",
  "capabilities": [...]
}
```

## How It Works

### Frontend to Backend Flow

1. User uploads an image through the React UI
2. Frontend sends the image to `/api/analyze` endpoint
3. Backend processes the image:
   - Loads pre-trained ResNet50 model
   - Extracts deep features from the image
   - Calculates sharpness and color variance metrics
   - Generates SHA-256 hash
   - Computes authenticity score
4. Backend returns analysis results
5. Frontend displays results in real-time

### Analysis Metrics

- **Authenticity Score**: Combined metric based on sharpness, feature distribution, and color variance
- **Sharpness Score**: Edge detection analysis using Laplacian filter
- **Color Variance**: Statistical distribution of color values
- **SHA-256 Hash**: Unique fingerprint for blockchain verification

## Troubleshooting

### Issue: "Cannot connect to backend"
**Solution:** 
- Ensure Flask server is running on `http://localhost:5000`
- Check if port 5000 is not blocked by firewall
- Verify CORS is enabled (Flask-CORS is configured)

### Issue: "Module not found" errors in backend
**Solution:**
- Activate virtual environment
- Run `pip install -r requirements.txt` again
- Check Python version (3.8+)

### Issue: Frontend doesn't show analysis results
**Solution:**
- Check browser console for errors (F12)
- Verify backend API response in Network tab
- Ensure image format is supported (JPG, PNG)

### Issue: Slow analysis
**Solution:**
- First run loads the ResNet50 model (~100MB), subsequent runs are faster
- For production, consider caching the model
- Use GPU acceleration if available

## Development Notes

### Key Files Modified

1. **backend/app.py** - New Flask API (replaces Streamlit UI)
2. **backend/requirements.txt** - Python dependencies
3. **Frontend/src/App.tsx** - Updated to call backend API instead of mock data

### Model Information

- **ResNet50**: Pre-trained on ImageNet
- **Input Size**: 224x224 pixels
- **Feature Extraction**: 2048-dimensional feature vectors
- **Normalization**: ImageNet standard (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

## Next Steps

1. **Production Deployment**: Use production WSGI servers (Gunicorn, uWSGI)
2. **Model Fine-tuning**: Train on deepfake/AI-generated image datasets
3. **Database Integration**: Store analysis history and blockchain records
4. **Authentication**: Add user authentication and API keys
5. **Performance Optimization**: Model quantization, caching, batch processing

## Project Structure

```
Implementation/
├── backend/
│   ├── app.py                      # Flask API (NEW)
│   ├── requirements.txt            # Python dependencies (NEW)
│   └── Image Processing.py         # Original Streamlit version (deprecated)
└── Frontend/
    ├── src/
    │   ├── App.tsx                 # Updated with API calls
    │   ├── components/
    │   └── styles/
    ├── package.json                # Updated with proxy
    └── vite.config.ts
```

## Version Info

- **Backend Version**: 1.1 (Flask API)
- **Frontend Version**: 0.1.0
- **Last Updated**: November 2024
