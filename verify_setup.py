#!/usr/bin/env python3
"""
ERP RAG System - Setup Verification Script
This script checks if your environment is properly configured for local development.
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10 or higher"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python version: {version.major}.{version.minor}.{version.micro} (Required: 3.10+)")
        return False

def check_data_file():
    """Check if data file exists"""
    data_file = Path(__file__).parent / "data" / "erp_chunks.json"
    if data_file.exists():
        size_mb = data_file.stat().st_size / (1024 * 1024)
        print(f"✅ Data file found: {data_file.name} ({size_mb:.2f} MB)")
        return True
    else:
        print(f"❌ Data file not found: {data_file}")
        return False

def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path(__file__).parent / "backend" / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if "GEMINI_API_KEY=" in content:
                if "GEMINI_API_KEY=your_actual_api_key_here" in content or "GEMINI_API_KEY=" == content.strip():
                    print(f"⚠️  .env file found but API key not configured")
                    print(f"   Edit {env_file} and add your Gemini API key")
                    return False
                else:
                    # API key is set but we don't show it for security
                    print(f"✅ .env file configured with API key")
                    return True
            else:
                print(f"❌ .env file doesn't contain GEMINI_API_KEY")
                return False
    else:
        print(f"❌ .env file not found: {env_file}")
        print(f"   Create it by copying: {env_file.parent / '.env.example'}")
        return False

def check_backend_structure():
    """Check if backend structure is correct"""
    backend_path = Path(__file__).parent / "backend"
    required_files = [
        "app/main.py",
        "app/agent.py",
        "app/rag_engine.py",
        "app/retrieval.py",
        "app/utils.py",
        "requirements.txt"
    ]
    
    missing = []
    for file in required_files:
        if not (backend_path / file).exists():
            missing.append(file)
    
    if not missing:
        print(f"✅ Backend structure is correct")
        return True
    else:
        print(f"❌ Missing backend files:")
        for file in missing:
            print(f"   - {file}")
        return False

def check_dependencies():
    """Check if key dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'google.generativeai',
        'faiss',
        'rank_bm25'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if not missing:
        print(f"✅ All required packages are installed")
        return True
    else:
        print(f"❌ Missing packages:")
        for package in missing:
            print(f"   - {package}")
        print(f"\n   Install with: pip install -r backend/requirements.txt")
        return False

def main():
    """Run all checks"""
    print("=" * 50)
    print("ERP RAG System - Setup Verification")
    print("=" * 50)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Data File", check_data_file),
        ("Environment File", check_env_file),
        ("Backend Structure", check_backend_structure),
        ("Dependencies", check_dependencies),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error during check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Summary: {passed}/{total} checks passed")
    print("=" * 50)
    
    if passed == total:
        print("\n✅ Your setup is ready! Run the backend with:")
        print("   cd backend")
        print("   uvicorn app.main:app --reload")
    else:
        print("\n❌ Please fix the issues above before running the backend")
        print("\nFor detailed setup instructions, see SETUP.md")

if __name__ == "__main__":
    main()
