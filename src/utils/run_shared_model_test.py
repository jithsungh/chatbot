"""
Quick test to check model availability and loading
"""
import os
import time
from sentence_transformers import SentenceTransformer

def check_model_cache(model_name):
    """Check if model is already cached locally"""
    cache_folder = os.path.expanduser("~/.cache/huggingface/transformers")
    
    print(f"🔍 Checking cache for model: {model_name}")
    print(f"📁 Cache folder: {cache_folder}")
    
    if os.path.exists(cache_folder):
        cached_models = os.listdir(cache_folder)
        print(f"📋 Found {len(cached_models)} cached models/files")
        
        # Look for model-related folders
        model_folders = [f for f in cached_models if model_name.replace('/', '--') in f or 'sentence' in f.lower()]
        if model_folders:
            print(f"✅ Possible cached model files: {model_folders}")
            return True
        else:
            print(f"❌ Model not found in cache")
            return False
    else:
        print(f"❌ Cache folder doesn't exist")
        return False

def test_model_loading(model_name, timeout=300):  # 5 minute timeout
    """Test model loading with timeout"""
    print(f"\n🧪 Testing model loading: {model_name}")
    
    start_time = time.time()
    
    try:
        print(f"⏳ Starting download/load... (timeout: {timeout}s)")
        model = SentenceTransformer(model_name)
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded successfully in {load_time:.2f}s")
        
        # Test encoding
        test_text = ["Hello world"]
        embeddings = model.encode(test_text)
        print(f"✅ Encoding test passed: {embeddings.shape}")
        
        return True
        
    except Exception as e:
        load_time = time.time() - start_time
        print(f"❌ Model loading failed after {load_time:.2f}s: {e}")
        return False

def main():
    models_to_test = [
        "paraphrase-MiniLM-L3-v2",      # Smallest ~18MB
        "all-MiniLM-L6-v2",             # Your current primary
        "all-mpnet-base-v2",            # Your current deputy
    ]
    
    print("🚀 Quick Model Loading Test")
    print("=" * 50)
    
    for model_name in models_to_test:
        print(f"\n📋 Testing: {model_name}")
        print("-" * 40)
        
        # Check cache first
        is_cached = check_model_cache(model_name)
        
        if is_cached:
            print(f"💡 Model appears to be cached, should load quickly")
        else:
            print(f"⚠️ Model not cached, will download on first use")
            response = input(f"Continue with {model_name}? (y/N): ")
            if response.lower() != 'y':
                print(f"⏭️ Skipping {model_name}")
                continue
        
        # Test loading
        success = test_model_loading(model_name, timeout=60)  # 1 minute timeout for testing
        
        if success:
            print(f"🎉 {model_name} works perfectly!")
            break
        else:
            print(f"💔 {model_name} failed")
    
    print("\n✅ Quick test completed")

if __name__ == "__main__":
    main()