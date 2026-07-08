# verify_installation.py
"""
Script to verify all required packages are installed correctly
Run with: python verify_installation.py
"""

import sys
import importlib

# List of required packages and their import names
required_packages = {
    # Core Framework
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "python-multipart": "multipart",
    
    # Document Processing
    "PyPDF2": "PyPDF2",
    "python-docx": "docx",
    "pdfplumber": "pdfplumber",
    "chardet": "chardet",
    
    # AI/ML
    "sentence-transformers": "sentence_transformers",
    "torch": "torch",
    "chromadb": "chromadb",
    "transformers": "transformers",
    "accelerate": "accelerate",
    
    # Utilities
    "python-dotenv": "dotenv",
    "pydantic": "pydantic",
    "aiofiles": "aiofiles",
    "pandas": "pandas",
    "pyodbc": "pyodbc"
}

print("=" * 60)
print("📦 Package Verification for Chat-with-Files Project")
print("=" * 60)
print(f"🐍 Python Version: {sys.version}")
print("-" * 60)

installed = []
missing = []
version_errors = []

for package_name, import_name in required_packages.items():
    try:
        module = importlib.import_module(import_name)
        
        # Try to get version
        try:
            if hasattr(module, "__version__"):
                version = module.__version__
            elif hasattr(module, "version"):
                version = module.version
            else:
                version = "unknown"
        except:
            version = "unknown"
        
        installed.append((package_name, version))
        print(f"✅ {package_name:25} v{version}")
        
    except ImportError:
        missing.append(package_name)
        print(f"❌ {package_name:25} NOT INSTALLED")

print("-" * 60)

# Summary
print(f"\n📊 Summary:")
print(f"   ✅ Installed: {len(installed)} packages")
print(f"   ❌ Missing: {len(missing)} packages")

if missing:
    print(f"\n⚠️ Missing packages: {', '.join(missing)}")
    print("\n🔧 Install missing packages with:")
    print(f"   pip install {' '.join(missing)}")

print("=" * 60)

# Check PyTorch specifically
print("\n🔥 PyTorch Details:")
try:
    import torch
    print(f"   PyTorch version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    print(f"   Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
except:
    print("   ❌ PyTorch not installed")

print("=" * 60)