# ⚡ Quick Reference Card

## 🚀 Start in 30 Seconds

### Windows
```bash
cd "Implementation"
start.bat
```

### macOS/Linux
```bash
cd Implementation
chmod +x start.sh
./start.sh
```

Then open: **http://localhost:5173**

---

## 📡 API Quick Reference

### Test Backend Health
```bash
curl http://localhost:5000/api/health
```

### Analyze an Image
```bash
curl -X POST -F "image=@image.jpg" \
  http://localhost:5000/api/analyze
```

### Get System Info
```bash
curl http://localhost:5000/api/info
```

---

## 🔗 URLs

| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:5173 | React Dev Server |
| Backend | http://localhost:5000 | Flask API |
| Backend Health | http://localhost:5000/api/health | ✅ Endpoint |
| Analyze | http://localhost:5000/api/analyze | 📤 POST |

---

## 📁 Important Files

| File | Purpose | Status |
|------|---------|--------|
| `backend/app.py` | Flask API Server | ✨ NEW |
| `backend/requirements.txt` | Python Dependencies | ✨ NEW |
| `Frontend/src/App.tsx` | React Frontend | ✏️ UPDATED |
| `start.bat` | Windows Launcher | ✨ NEW |
| `start.sh` | macOS/Linux Launcher | ✨ NEW |

---

## 🛠️ Manual Setup (If Automated Scripts Fail)

### Backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

### Frontend (New Terminal)
```bash
cd Frontend
npm install
npm run dev
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | Check Python 3.8+: `python --version` |
| Port 5000 in use | Edit `backend/app.py` line: `port=5001` |
| Dependencies not found | Run: `pip install -r requirements.txt` |
| Frontend won't connect | Check backend running: `curl localhost:5000/api/health` |
| npm install fails | Delete `node_modules`, run: `npm cache clean --force && npm install` |

---

## 📊 Response Format

```json
{
  "success": true,
  "authenticityScore": 75.5,
  "sharpnessScore": 85.2,
  "colorVariance": 62.1,
  "prediction": "authentic",
  "hash": "abc123...",
  "blockchainStatus": "verified"
}
```

---

## ✨ Key Features

✅ Real-time image analysis  
✅ ResNet50 deep learning  
✅ SHA-256 blockchain hashing  
✅ No more Streamlit UI  
✅ Modern React frontend  
✅ REST API backend  
✅ CORS enabled  
✅ Error handling  

---

## 📚 Full Documentation

- **INTEGRATION_GUIDE.md** → Complete setup guide
- **README_INTEGRATION.md** → Full overview
- **ARCHITECTURE_DIAGRAMS.md** → System design
- **SETUP_SUMMARY.md** → Summary of changes

---

## ⌨️ Common Commands

```bash
# Activate Python venv
source backend/venv/bin/activate  # macOS/Linux
backend\venv\Scripts\activate     # Windows

# Install Python packages
pip install -r backend/requirements.txt

# Install npm packages
npm install

# Run Flask server
python backend/app.py

# Run React dev server
npm run dev

# Test backend API
python test_backend_check.py

# Build React for production
npm run build
```

---

## 🎯 What's New

| Feature | Before | Now |
|---------|--------|-----|
| UI | Streamlit | React |
| Backend | Built-in | Flask API |
| Communication | N/A | REST API |
| Scalability | Limited | High |
| Deployment | Streamlit Cloud | Anywhere |

---

## 💡 Pro Tips

1. **First run is slow** - ResNet50 model loads on first use (~2 min)
2. **Later runs are fast** - Model cached in memory
3. **Check console** - Press F12 in browser for error details
4. **Reload needed** - If you change backend code, restart Flask
5. **Hot reload works** - React dev server auto-reloads on file change

---

## 🔒 Supported File Types & Sizes

- **Formats:** JPG, PNG, JPEG
- **Max Size:** 16 MB
- **Image Dimensions:** Any (auto-resized to 224x224)

---

## 📞 Need Help?

1. Check browser console: **F12**
2. Check Flask terminal output
3. Read **INTEGRATION_GUIDE.md**
4. Test with: `python test_backend_check.py`
5. Try curl: `curl http://localhost:5000/api/health`

---

## 🎉 Success Checklist

- [ ] Both servers started
- [ ] Can access http://localhost:5173
- [ ] Can upload image
- [ ] Results display correctly
- [ ] No errors in console

**If all checked ✓, you're ready to go!**

---

*Last Updated: November 14, 2024*  
*Version: 1.0*  
*Status: Ready for Production* ✅
