"""
Non-blocking startup health check to identify issues before main app starts
"""
import sys
import os
import time
import threading
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def check_basic_imports() -> Dict[str, Any]:
    """Check if basic imports work without triggering model loading"""
    print("🧪 Testing basic imports...")
    results = {"success": True, "errors": [], "timing": {}}
    
    try:
        start = time.perf_counter()
        
        # Test basic config import (should be fast)
        from src.config import Config
        results["timing"]["config"] = time.perf_counter() - start
        print(f"✅ Config imported in {results['timing']['config']:.2f}s")
        
        # Test if departments are configured
        print(f"📋 Departments: {Config.DEPARTMENTS}")
        
        # Test database connection with timeout
        print("🔗 Testing database connection...")
        db_result = {"success": False, "error": None, "timing": 0}
        
        def test_db_connection():
            try:
                start_db = time.perf_counter()
                session = Config.get_session()
                from sqlalchemy import text
                session.execute(text("SELECT 1"))

                session.close()
                db_result["timing"] = time.perf_counter() - start_db
                db_result["success"] = True
            except Exception as e:
                db_result["error"] = str(e)
        
        # Run database test in thread with timeout
        db_thread = threading.Thread(target=test_db_connection)
        db_thread.daemon = True
        db_thread.start()
        db_thread.join(timeout=15.0)  # 15 second timeout
        
        if db_thread.is_alive():
            results["errors"].append("Database connection timeout (15s) - database may not be running")
            print(f"⏰ Database connection timeout - database may not be running")
            print(f"💡 Hint: Make sure your database server is running")
        elif db_result["success"]:
            results["timing"]["database"] = db_result["timing"]
            print(f"✅ Database connected in {results['timing']['database']:.2f}s")
        else:
            results["errors"].append(f"Database connection failed: {db_result['error']}")
            print(f"❌ Database connection failed: {db_result['error']}")
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Basic import failed: {e}")
        print(f"❌ Basic import failed: {e}")
    
    return results

def check_model_availability() -> Dict[str, Any]:
    """Check model availability without loading them"""
    print("\n🧪 Checking model availability...")
    results = {"success": True, "errors": [], "cached_models": []}
    
    try:
        import os
        cache_folder = os.path.expanduser("~/.cache/huggingface/transformers")
        
        models_to_check = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]
        
        if os.path.exists(cache_folder):
            cached_files = os.listdir(cache_folder)
            print(f"📁 HuggingFace cache exists with {len(cached_files)} items")
            
            for model_name in models_to_check:
                model_files = [f for f in cached_files if model_name.replace('/', '--') in f or 'sentence' in f.lower()]
                if model_files:
                    results["cached_models"].append(model_name)
                    print(f"✅ Model {model_name} appears to be cached")
                else:
                    print(f"⚠️ Model {model_name} not cached (will download on first use)")
        else:
            print(f"⚠️ HuggingFace cache folder not found")
            
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Model availability check failed: {e}")
        print(f"❌ Model availability check failed: {e}")
    
    return results

def check_routes_import() -> Dict[str, Any]:
    """Check if route imports work without initializing components"""
    print("\n🧪 Testing route imports...")
    results = {"success": True, "errors": []}
    
    def test_single_route(route_name, import_path):
        """Test a single route import with its own timeout"""
        route_result = {"success": False, "error": None, "completed": False}
        
        def single_import():
            try:
                print(f"   Testing {route_name}...")
                module_path, class_name = import_path.rsplit('.', 1)
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
                route_result["success"] = True
                route_result["completed"] = True
                print(f"   ✅ {route_name} imported successfully")
            except Exception as e:
                route_result["error"] = str(e)
                route_result["completed"] = True
                print(f"   ❌ {route_name} import failed: {e}")
        
        # Run single route test with timeout
        route_thread = threading.Thread(target=single_import)
        route_thread.daemon = True
        route_thread.start()
        route_thread.join(timeout=5.0)  # 5 second timeout per route
        
        if not route_result["completed"]:
            error_msg = f"{route_name} import timeout (5s) - likely hanging on heavy dependencies"
            results["errors"].append(error_msg)
            print(f"   ⏰ {error_msg}")
            results["success"] = False
        elif not route_result["success"]:
            results["errors"].append(f"{route_name} import failed: {route_result['error']}")
            results["success"] = False
    
    # Test each route individually with separate timeouts
    routes_to_test = [
        ("AdminRoutes", "src.app.routes.AdminRoutes"),
        ("QueryRoutes", "src.app.routes.QueryRoutes"),
        ("AdminAuthRoutes", "src.app.routes.AdminAuthRoutes")
    ]
    
    for route_name, import_path in routes_to_test:
        test_single_route(route_name, import_path)
    
    return results

def main():
    """Run all health checks"""
    print("🚀 Running Startup Health Checks")
    print("=" * 60)
    
    # Run checks in order of dependency
    checks = [
        ("Basic Imports", check_basic_imports),
        ("Model Availability", check_model_availability), 
        ("Route Imports", check_routes_import)
    ]
    
    all_results = []
    total_errors = []
    
    for check_name, check_func in checks:
        print(f"\n📋 Running {check_name}...")
        try:
            result = check_func()
            all_results.append((check_name, result))
            if not result["success"]:
                total_errors.extend(result["errors"])
        except Exception as e:
            error_msg = f"{check_name} crashed: {e}"
            total_errors.append(error_msg)
            print(f"❌ {error_msg}")
            all_results.append((check_name, {"success": False, "errors": [error_msg]}))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 STARTUP HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    passed_checks = sum(1 for _, result in all_results if result["success"])
    total_checks = len(checks)
    
    print(f"Checks passed: {passed_checks}/{total_checks}")
    
    for check_name, result in all_results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{check_name:<20} {status}")
    
    if total_errors:
        print(f"\n❌ Issues found ({len(total_errors)}):")
        for error in total_errors:
            print(f"   - {error}")
        print("\n💡 Fix these issues before starting your application")
        return False
    else:
        print("\n🎉 All health checks passed!")
        print("💡 Your application should start normally")
        
        # Show optimization suggestions
        cached_models = []
        for _, result in all_results:
            if "cached_models" in result:
                cached_models.extend(result["cached_models"])
        
        if cached_models:
            print(f"⚡ Cached models available: {cached_models}")
        else:
            print("⚠️ No models cached - first startup will be slower")
        
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)