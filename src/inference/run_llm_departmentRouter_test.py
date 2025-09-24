# src/inference/run_llm_test.py
import time
# from src.inference.DepartmentRouter import DepartmentRouter
# from src.inference.FastRouter import FastDepartmentRouter
from src.inference.HybridRouter import HybridDepartmentRouter
from src.inference.test_questions import QUESTIONS

def run_tests():
    router = HybridDepartmentRouter()
    total = len(QUESTIONS)
    correct = 0
    wrong_cases = []

    start = time.perf_counter()        # <-- start timer

    for q, expected in QUESTIONS:
        result = router.route_query(q)
        if result.strip().lower() == expected.strip().lower():
            correct += 1
        else:
            wrong_cases.append((q, expected, result))

    end = time.perf_counter()          # <-- end timer
    elapsed = end - start

    # --- Print analysis ---
    print("\n=== TEST RESULTS ===")
    print(f"Total Questions: {total}")
    print(f"Correct: {correct}")
    print(f"Wrong: {len(wrong_cases)}")
    print(f"Accuracy: {correct/total:.2%}")
    print(f"Time Taken: {elapsed:.2f} seconds\n")

    if wrong_cases:
        print("❌ Wrong Predictions:")
        for idx, (q, exp, got) in enumerate(wrong_cases, start=1):
            print(f"{idx}. Q: {q}")
            print(f"   Expected: {exp}")
            print(f"   Got: {got}\n")

if __name__ == "__main__":
    run_tests()
