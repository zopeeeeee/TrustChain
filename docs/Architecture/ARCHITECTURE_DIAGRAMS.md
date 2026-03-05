# TrustChain-AV Architecture & Integration Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER'S WEB BROWSER                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │             React Frontend (Port 5173)                      │ │
│  │                                                              │ │
│  │  ┌──────────────────┐         ┌──────────────────┐         │ │
│  │  │ Image Upload UI  │         │  Results Display │         │ │
│  │  └──────────────────┘         └──────────────────┘         │ │
│  │           │                           ▲                     │ │
│  │           │ File Upload               │ JSON Response       │ │
│  │           ▼                           │                     │ │
│  │  ┌──────────────────────────────────┐                      │ │
│  │  │   HTTP Client (Fetch API)         │                     │ │
│  │  │   POST /api/analyze              │                     │ │
│  │  │   FormData (multipart)           │                     │ │
│  │  └──────────────────────────────────┘                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                           │                                       │
│                      HTTP │ REST                                  │
│                    ┌───────┴────────┐                             │
└────────────────────┤ CORS Enabled   ├─────────────────────────────┘
                     └───────┬────────┘
                             │
                     ┌───────▼──────────┐
                     │  LOCALHOST:5000  │
                     └───────┬──────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    FLASK BACKEND (Port 5000)                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             HTTP Routes & Handlers                        │  │
│  │                                                            │  │
│  │  GET  /api/health      ──► HealthCheck()               │  │
│  │  POST /api/analyze     ──► ImageAnalysis()             │  │
│  │  GET  /api/info        ──► SystemInfo()                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                      ┌──────▼──────┐                            │
│                      │ Image Handler│                            │
│                      │ - File upload │                           │
│                      │ - Validation │                           │
│                      └──────┬───────┘                            │
│                             │                                    │
│       ┌─────────────────────┴──────────────────────┐            │
│       │                                             │            │
│       ▼                                             ▼            │
│  ┌─────────────┐                          ┌──────────────┐      │
│  │  PIL Image  │                          │ Image Metrics │      │
│  │  Processing │                          │  - Sharpness  │      │
│  └─────────────┘                          │  - Color Var  │      │
│       │                                    └──────────────┘      │
│       ▼                                             │            │
│  ┌─────────────────────────────────────────────────┴──────┐     │
│  │                  ResNet50 Model                        │     │
│  │  (Pre-trained ImageNet weights)                        │     │
│  │  - Input: 224x224 RGB                                 │     │
│  │  - Output: 2048-D Feature Vector                       │     │
│  └──────────────────┬─────────────────────────────────────┘     │
│                     │                                            │
│       ┌─────────────┴─────────────┐                            │
│       ▼                           ▼                            │
│  ┌──────────┐            ┌────────────────┐                   │
│  │ Features │            │ SHA-256 Hashing │                   │
│  │ Analysis │            │ (Blockchain)    │                   │
│  └─────────┬┘            └────────┬────────┘                   │
│            │                      │                            │
│       ┌────▼──────────────────────▼─────┐                     │
│       │  Authenticity Scoring           │                     │
│       │  & Prediction Logic             │                     │
│       │  (authentic/modified/ai-gen)    │                     │
│       └────┬──────────────────────┬─────┘                     │
│            │                      │                            │
│    ┌───────▼────────────┐  ┌──────▼──────┐                   │
│    │ JSON Response      │  │ Status Code  │                   │
│    │ - Scores           │  │ (200/400/500)│                   │
│    │ - Prediction       │  └──────┬───────┘                   │
│    │ - Hash             │         │                           │
│    │ - Blockchain Status│         │                           │
│    └────────┬───────────┘         │                           │
│             └─────────┬───────────┘                           │
└────────────────────────┼──────────────────────────────────────┘
                         │
                    HTTP Response
                      JSON Data
                         │
            ┌────────────▼────────────┐
            │                         │
         Browser                 Frontend
        Renders                    Updates
         Results                     UI
```

---

## Request-Response Flow Diagram

```
┌─────────────┐
│   USER      │ Selects image file
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ React Component  │ handleFileUpload()
└──────┬───────────┘
       │
       ├─ Create object URL for preview
       ├─ Set analyzing = true
       │
       ▼
┌──────────────────────────────┐
│ Create FormData object       │ new FormData()
│ - append('image', file)      │
└──────┬───────────────────────┘
       │
       ▼
┌────────────────────────────────────────┐
│ Fetch API Request                      │
│ POST http://localhost:5000/api/analyze│
│ Body: FormData (multipart/form-data)  │
│ Headers: CORS enabled                 │
└──────┬─────────────────────────────────┘
       │
       ▼ (Network transmission)
       
       ┌──────────────────────────────────┐
       │     FLASK BACKEND                │
       │                                  │
       │ @app.route('/api/analyze')      │
       │                                  │
       ▼──────────────────────────────────▼
       
┌──────────────────┐
│ Extract image    │ file = request.files['image']
│ from request     │ file_bytes = file.read()
└──────┬───────────┘
       │
       ├─ Validate file type ✓
       ├─ Validate file size ✓
       │
       ▼
┌──────────────────┐
│ Open PIL Image   │ Image.open(io.BytesIO())
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────┐
│ analyze_image(image, file_bytes) │
└──────┬───────────────────────────┘
       │
       ├─ Calculate sharpness
       ├─ Calculate color variance
       ├─ Load ResNet50 model
       ├─ Extract features
       ├─ Generate SHA-256 hash
       ├─ Calculate authenticity score
       ├─ Determine prediction
       │
       ▼
┌────────────────────────┐
│ Return result dict:    │
│ {                      │
│   success: true,       │
│   authenticityScore,   │
│   sharpnessScore,      │
│   colorVariance,       │
│   prediction,          │
│   label,               │
│   hash,                │
│   blockchainStatus     │
│ }                      │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ JSON Response (200 OK) │
│ Content-Type: JSON     │
└──────┬─────────────────┘
       │
       ▼ (Network transmission)
       
┌────────────────────────────────┐
│ Frontend receives response      │
│ response.json()                │
└──────┬─────────────────────────┘
       │
       ├─ Check if success = true
       ├─ Extract scores & data
       ├─ Set analyzing = false
       │
       ▼
┌────────────────────────┐
│ Update React State     │
│ setAnalysisData(data)  │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ React Re-renders       │
│ components with        │
│ new analysis data      │
└──────┬─────────────────┘
       │
       ▼
┌────────────────────────┐
│ User sees:             │
│ - Authenticity Meter   │
│ - Prediction Badge     │
│ - Scores (3 cards)     │
│ - Hash                 │
│ - Insights             │
└────────────────────────┘
```

---

## File Upload Process (Detailed)

```
Browser                          React Component              Flask Backend
  │                                    │                            │
  │ 1. User selects image              │                            │
  │ from file system                   │                            │
  ├───────────────────────────────────►│                            │
  │                            onChange │                            │
  │                                    │ 2. Create object URL       │
  │                                    │    for preview             │
  │                                    │ 3. Create FormData         │
  │                                    │    formData.append(        │
  │                                    │    'image', file)          │
  │                                    │                            │
  │                                    │ 4. Fetch POST              │
  │                                    ├───────────────────────────►│
  │                                    │    /api/analyze            │
  │                                    │    multipart/form-data     │
  │                                    │                            │
  │                                    │      5. File received      │
  │                                    │         from request       │
  │                                    │                            │
  │                                    │      6. PIL Image.open()   │
  │                                    │      7. Load ResNet50      │
  │                                    │      8. Extract features   │
  │                                    │      9. Calculate metrics  │
  │                                    │     10. Generate hash      │
  │                                    │     11. Calculate scores   │
  │                                    │                            │
  │                                    │◄───────────────────────────┤
  │                                    │    JSON response           │
  │                                    │    (200 OK)               │
  │                                    │                            │
  │                                    │ 12. Parse JSON            │
  │                                    │ 13. Update state          │
  │                                    │ 14. Trigger re-render     │
  │                                    │                            │
  │◄───────────────────────────────────┤                            │
  │   15. Display results               │                            │
  │   - Meter                           │                            │
  │   - Badges                          │                            │
  │   - Metrics                         │                            │
  │   - Hash                            │                            │
  │                                    │                            │
```

---

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR SCENARIOS                           │
└─────────────────────────────────────────────────────────────┘

1. FRONTEND ERRORS
   │
   ├─► No image selected
   │   └─► UI shows: "No image file provided"
   │
   ├─► Invalid file type
   │   └─► UI shows: "Invalid file type. Allowed: jpg, jpeg, png"
   │
   ├─► File too large
   │   └─► UI shows: "File too large. Maximum 16MB"
   │
   ├─► Backend not running
   │   └─► UI shows: "Error connecting to backend"
   │
   └─► Network error
       └─► UI shows: "Network connection error"

2. BACKEND ERRORS (HTTP Status)
   │
   ├─► 400 Bad Request
   │   └─► No image file
   │       No file selected
   │       Invalid file type
   │
   ├─► 413 Payload Too Large
   │   └─► File exceeds size limit
   │
   ├─► 500 Internal Server Error
   │   └─► Model loading error
   │       Image processing error
   │       Unexpected exception
   │
   └─► 503 Service Unavailable
       └─► Server temporarily down

3. RESPONSE HANDLING
   │
   ├─► Success (200 OK, success: true)
   │   └─► Display results
   │
   ├─► Error response (200 OK, success: false)
   │   └─► Show error message
   │
   └─► HTTP error (4xx, 5xx)
       └─► Show connection error alert
```

---

## State Machine Diagram

```
                    ┌─────────────────────┐
                    │   INITIAL STATE     │
                    │ uploadedImage: null │
                    │ analyzing: false    │
                    │ analysisData: null  │
                    └────────┬────────────┘
                             │
                    User selects image
                             │
                    ┌────────▼──────────────────┐
                    │   IMAGE SELECTED          │
                    │ uploadedImage: set        │
                    │ analyzing: true           │
                    │ analysisData: null        │
                    └────────┬─────────────────┘
                             │
              API request sent to backend
                             │
                    ┌────────▼──────────────────┐
                    │   ANALYZING              │
                    │ uploadedImage: set       │
                    │ analyzing: true          │
                    │ analysisData: null       │
                    │                          │
                    │ Shows loading spinner    │
                    └────────┬─────────────────┘
                             │
        ┌─────────────────────┴─────────────────┐
        │                                       │
    Success                              Error/Timeout
        │                                       │
        ▼                                       ▼
┌──────────────────────────┐         ┌──────────────────────────┐
│   RESULTS READY          │         │   ERROR STATE            │
│ uploadedImage: set       │         │ uploadedImage: set       │
│ analyzing: false         │         │ analyzing: false         │
│ analysisData: populated  │         │ analysisData: null       │
│                          │         │                          │
│ Shows:                   │         │ Shows:                   │
│ - Authenticity meter     │         │ - Error message          │
│ - Prediction badge       │         │ - Retry option           │
│ - Three metric cards     │         │ - Reset button           │
│ - Hash & blockchain      │         │                          │
│ - AI insights            │         │                          │
└──────┬───────────────────┘         └──────────────────────────┘
       │                                      │
       │ User clicks Reset                    │
       └──────────────┬───────────────────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │   INITIAL STATE     │ (Cycle repeats)
            │ uploadedImage: null │
            │ analyzing: false    │
            │ analysisData: null  │
            └─────────────────────┘
```

---

## Technology Stack Layers

```
┌──────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                     │
│  (What users see in their browser)                       │
│                                                          │
│  React Components                                        │
│  ├─ App.tsx                                             │
│  ├─ FileUploader                                        │
│  ├─ ImagePreview                                        │
│  ├─ AuthenticityMeter                                   │
│  ├─ AnalysisResults                                     │
│  └─ BlockchainSection                                   │
│                                                          │
│  UI Library: Radix UI Components                         │
│  Styling: TailwindCSS                                    │
│  Icons: Lucide React                                     │
└──────────────────────────────────────────────────────────┘
                          │
                    REST API (HTTP)
                    JSON Exchange
                          │
┌──────────────────────────────────────────────────────────┐
│                   API LAYER                              │
│  (HTTP endpoints)                                        │
│                                                          │
│  Flask Web Framework                                     │
│  ├─ GET  /api/health                                    │
│  ├─ GET  /api/info                                      │
│  └─ POST /api/analyze                                   │
│                                                          │
│  Middleware:                                             │
│  ├─ CORS                                                │
│  ├─ File validation                                     │
│  └─ Error handling                                      │
└──────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────────────────────────────────────┐
│                  PROCESSING LAYER                        │
│  (Analysis logic)                                        │
│                                                          │
│  Image Processing Pipeline                              │
│  ├─ PIL/Pillow (Image loading)                          │
│  ├─ OpenCV (Image analysis)                             │
│  │  ├─ Laplacian (Sharpness detection)                  │
│  │  └─ Variance (Color distribution)                    │
│  ├─ PyTorch (Deep learning framework)                   │
│  │  └─ ResNet50 (Pre-trained model)                     │
│  └─ Hashlib (SHA-256 generation)                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────────────────────────────────────┐
│                    MODEL LAYER                           │
│  (Pre-trained weights & assets)                         │
│                                                          │
│  ResNet50 (ImageNet pre-trained)                        │
│  ├─ 50 convolutional layers                             │
│  ├─ 2048-D feature vectors                              │
│  ├─ ~100MB model weights                                │
│  └─ Cached in memory after first load                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Port Configuration

```
Machine: localhost (127.0.0.1)

Frontend (React)
  │
  ├─ Port: 5173 (or 5174, 5175 if taken)
  ├─ Protocol: HTTP
  ├─ Command: npm run dev
  └─ URL: http://localhost:5173

Backend (Flask)
  │
  ├─ Port: 5000
  ├─ Protocol: HTTP
  ├─ Command: python app.py
  └─ URL: http://localhost:5000

Communication
  │
  └─ Frontend sends requests to: http://localhost:5000/api/...
  └─ CORS allows cross-origin requests
  └─ Requests sent as: POST multipart/form-data or GET

Network Path:
Browser (5173) ──HTTP──► Flask Server (5000)
     ▲                          │
     │                          │
     └──────Response (JSON)─────┘
```

---

This comprehensive architecture ensures:
- ✅ Clean separation of concerns
- ✅ Scalability
- ✅ Maintainability
- ✅ Easy debugging
- ✅ Future extensibility
