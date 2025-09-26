"""
Comprehensive test script for the question processing pipeline
"""
import sys
import time
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all imports work correctly"""
    print("🧪 Testing imports...")
    try:
        start = time.perf_counter()
        from src.admin.filter import QuestionFilter
        temptime = time.perf_counter() - start
        print(f"⏱️ Importing QuestionFilter took {temptime:.2f} seconds")
        from src.service.question_deduplicator import fetch_and_deduplicate_pending_questions
        temptime = time.perf_counter() - temptime
        print(f"⏱️ Importing fetch_and_deduplicate_pending_questions took {temptime:.2f} seconds")
        from src.service.question_summarizer import QuestionSummarizer
        temptime = time.perf_counter() - temptime
        print(f"⏱️ Importing QuestionSummarizer took {temptime:.2f} seconds")
        from src.models.admin_question import AdminQuestion, AdminQuestionStatus
        temptime = time.perf_counter() - temptime
        print(f"⏱️ Importing AdminQuestion took {temptime:.2f} seconds")
        from src.models.user_question import DeptType, UserQuestion, UserQuestionStatus
        end = time.perf_counter() - temptime
        print(f"⏱️ Importing UserQuestion took {end:.2f} seconds")
        total_time = end - start
        print(f"⏱️ Total import time: {total_time:.2f} seconds")
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_question_summarizer():
    """Test QuestionSummarizer independently"""
    print("\n🧪 Testing QuestionSummarizer...")
    try:
        from src.service.question_summarizer import QuestionSummarizer
        
        # Test data
        test_cluster = [
            {"query": "How to reset password?"},
            {"query": "Password reset procedure?"},
            {"query": "I forgot my password"}
        ]
        
        summarizer = QuestionSummarizer()
        prompt = summarizer.generate_prompt(test_cluster)
        
        print("✅ QuestionSummarizer prompt generation successful")
        print(f"Generated prompt length: {len(prompt)} characters")
        return True
        
    except Exception as e:
        print(f"❌ QuestionSummarizer test failed: {e}")
        return False

def test_department_enum():
    """Test department enum conversion"""
    print("\n🧪 Testing department enum conversion...")
    try:
        from src.admin.filter import QuestionFilter
        from src.models.user_question import DeptType
        
        # Test valid departments  
        valid_depts = ["HR", "IT", "Security"]
        for dept in valid_depts:
            result = QuestionFilter._get_dept_enum(dept)
            assert result == DeptType(dept), f"Failed for {dept}"
        
        # Test invalid/unassigned
        invalid_result = QuestionFilter._get_dept_enum("InvalidDept")
        assert invalid_result is None, "Should return None for invalid department"
        
        unassigned_result = QuestionFilter._get_dept_enum("Unassigned")
        assert unassigned_result is None, "Should return None for Unassigned"
        
        print("✅ Department enum conversion test successful")
        return True
        
    except Exception as e:
        print(f"❌ Department enum test failed: {e}")
        return False

def test_filter_initialization():
    """Test QuestionFilter initialization"""
    print("\n🧪 Testing QuestionFilter initialization...")
    try:
        from src.admin.filter import QuestionFilter
        
        # Test initialization
        filter_instance = QuestionFilter()
        assert hasattr(filter_instance, 'summarizer'), "Filter should have summarizer attribute"
        
        print("✅ QuestionFilter initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ QuestionFilter initialization test failed: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🚀 Starting comprehensive pipeline tests...\n")
    
    tests = [
        # ("Import Test", test_imports),
        ("QuestionSummarizer Test", test_question_summarizer),
        ("Department Enum Test", test_department_enum),
        ("Filter Initialization Test", test_filter_initialization),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Pipeline should work correctly.")
        
        # Try to run the actual pipeline test
        try:
            from src.admin.filter import test_pipeline
            print("\n🔥 Running actual pipeline test...")
            test_pipeline()
        except Exception as e:
            print(f"⚠️ Pipeline test couldn't run: {e}")
    else:
        print("⚠️ Some tests failed. Please fix the issues before running the pipeline.")

if __name__ == "__main__":
    main()