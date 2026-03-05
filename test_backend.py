#!/usr/bin/env python3
"""
Quick test script to verify backend API is working
Run this after starting the Flask server
"""

import requests
import sys
from pathlib import Path


def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
            print(f"   Response: {response.json()}")
            return True
        else:
            print("❌ Health Check: FAILED")
            print(f"   Status Code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Health Check: FAILED")
        print("   Error: Cannot connect to backend on http://localhost:5000")
        print("   Make sure Flask server is running!")
        return False

def test_info():
    """Test the info endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/info')
        if response.status_code == 200:
            print("✅ Info Endpoint: PASSED")
            info = response.json()
            print(f"   Name: {info.get('name')}")
            print(f"   Version: {info.get('version')}")
            print(f"   Capabilities: {len(info.get('capabilities', []))} features")
            return True
        else:
            print("❌ Info Endpoint: FAILED")
            return False
    except Exception as e:
        print(f"❌ Info Endpoint: FAILED - {e}")
        return False

def test_analyze(image_path):
    """Test the analyze endpoint with an actual image"""
    if not Path(image_path).exists():
        print(f"❌ Analyze Test: Image not found at {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post('http://localhost:5000/api/analyze', files=files)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Analyze Endpoint: PASSED")
                print(f"   Authenticity Score: {data.get('authenticityScore')}%")
                print(f"   Prediction: {data.get('prediction')}")
                print(f"   Hash: {data.get('hash')[:16]}...")
                return True
            else:
                print(f"❌ Analyze Endpoint: FAILED - {data.get('error')}")
                return False
        else:
            print(f"❌ Analyze Endpoint: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analyze Endpoint: FAILED - {e}")
        return False

def main():
    print("=" * 50)
    print("TrustChain-AV Backend API Test")
    print("=" * 50)
    print()
    
    # Test 1: Health check
    print("Test 1: Health Check")
    health_ok = test_health()
    print()
    
    if not health_ok:
        print("Backend is not running. Please start it with:")
        print("  cd backend")
        print("  python app.py")
        sys.exit(1)
    
    # Test 2: Info endpoint
    print("Test 2: System Information")
    info_ok = test_info()
    print()
    
    # Test 3: Analyze endpoint (if test image exists)
    print("Test 3: Image Analysis")
    test_image = Path(__file__).parent / "test_image.jpg"
    if test_image.exists():
        analyze_ok = test_analyze(str(test_image))
    else:
        print("⏭️  Skipping (no test image found at ./test_image.jpg)")
        print("   Place a JPG or PNG image at that location to test")
        analyze_ok = None
    
    print()
    print("=" * 50)
    if health_ok and info_ok:
        print("✅ Backend is Ready!")
        print("   Now you can start the frontend with:")
        print("   cd Frontend && npm run dev")
    else:
        print("❌ Backend Tests Failed")
        print("   Check the errors above")
    print("=" * 50)

if __name__ == '__main__':
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("Error: 'requests' package not installed")
        print("Install it with: pip install requests")
        sys.exit(1)
    
    main()
