#!/usr/bin/env python3
"""
Comprehensive backend testing script for TrendXL 2.0
"""
import requests
import json
import time
from typing import Dict, Any

class BackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        
    def test_connection(self) -> bool:
        """Test basic connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return response.status_code == 200
        except:
            return False
    
    def test_health(self) -> Dict[str, Any]:
        """Test health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Status: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_status(self) -> Dict[str, Any]:
        """Test detailed status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/status")
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Status: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_ping_endpoint(self) -> Dict[str, Any]:
        """Test simple ping endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ping")
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"Status: {response.status_code}, Response: {response.text[:200]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_full_analysis(self) -> Dict[str, Any]:
        """Test full analysis endpoint"""
        try:
            data = {"profile_url": "https://www.tiktok.com/@zachking"}
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze", 
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=60  # Longer timeout for full analysis
            )
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True, 
                    "data": {
                        "profile": result.get("profile", {}).get("username", "N/A"),
                        "posts_count": len(result.get("posts", [])),
                        "hashtags_count": len(result.get("hashtags", [])),
                        "trends_count": len(result.get("trends", []))
                    }
                }
            else:
                return {"success": False, "error": f"Status: {response.status_code}, Response: {response.text[:200]}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 TrendXL 2.0 Backend Test Suite")
        print("=" * 50)
        
        # Test 1: Connection
        print("\n1️⃣  Testing basic connection...")
        if self.test_connection():
            print("✅ Connection successful")
        else:
            print("❌ Connection failed - server may not be running")
            return
        
        # Test 2: Health
        print("\n2️⃣  Testing health endpoint...")
        health_result = self.test_health()
        if health_result["success"]:
            print("✅ Health endpoint working")
            health_data = health_result["data"]
            print(f"   Status: {health_data.get('status')}")
            print(f"   Services: {health_data.get('services')}")
        else:
            print(f"❌ Health endpoint failed: {health_result['error']}")
        
        # Test 3: Status
        print("\n3️⃣  Testing detailed status endpoint...")
        status_result = self.test_status()
        if status_result["success"]:
            print("✅ Status endpoint working")
            status_data = status_result["data"]
            print(f"   Version: {status_data.get('version')}")
            print(f"   Services: {status_data.get('services')}")
            print(f"   Config: {status_data.get('config')}")
        else:
            print(f"❌ Status endpoint failed: {status_result['error']}")
        
        # Test 4: Ping endpoint
        print("\n4️⃣  Testing ping endpoint...")
        ping_result = self.test_ping_endpoint()
        if ping_result["success"]:
            print("✅ Ping endpoint working")
            print(f"   Response: {ping_result['data'].get('message')}")
        else:
            print(f"❌ Ping endpoint failed: {ping_result['error']}")
        
        # Test 5: Full analysis
        print("\n5️⃣  Testing full analysis endpoint...")
        print("   (This may take 30-60 seconds...)")
        analysis_result = self.test_full_analysis()
        if analysis_result["success"]:
            print("✅ Full analysis working")
            data = analysis_result["data"]
            print(f"   Profile: {data['profile']}")
            print(f"   Posts: {data['posts_count']}")
            print(f"   Hashtags: {data['hashtags_count']}")
            print(f"   Trends: {data['trends_count']}")
        else:
            print(f"❌ Full analysis failed: {analysis_result['error']}")
        
        print("\n" + "=" * 50)
        print("🏁 Test suite completed!")

def main():
    tester = BackendTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
