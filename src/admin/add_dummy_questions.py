import uuid
from sqlalchemy.exc import SQLAlchemyError
from src.models.user_question import UserQuestion, DeptType, UserQuestionStatus
from src.config import Config  # Fixed import

class DummyQuestionGenerator:
    def __init__(self):
        """Initialize with dummy user ID"""
        self.dummy_user_id = uuid.uuid4()
        print(f"🔧 Using dummy user ID: {self.dummy_user_id}")
    
    @staticmethod
    def get_dummy_questions():
        """
        Generate dummy questions for different policies
        Returns dict with department and list of questions
        """
        questions = {
            "HR": {
                # Referral Bonus Policy (4 questions)
                "referral_bonus": [
                    "What is the referral bonus amount for new hires?",
                    "How do I claim my employee referral bonus?",
                    "When will I receive the referral bonus payment?",
                    "What are the eligibility criteria for referral bonus?"
                ],
                # Exit Policy (4 questions)
                "exit_policy": [
                    "What is the notice period for resignation?",
                    "How do I initiate the exit process?",
                    "What documents do I need to submit during exit?",
                    "Can I buy out my notice period?"
                ],
                # Leave Policy (4 questions)
                "leave_policy": [
                    "How many sick leaves am I entitled to annually?",
                    "What is the process to apply for maternity leave?",
                    "Can I carry forward unused vacation days?",
                    "How do I apply for emergency leave?"
                ],
                # Clear Desk Policy (4 questions)
                "clear_desk_policy": [
                    "What is the clear desk policy at end of day?",
                    "Can I leave personal items on my desk overnight?",
                    "What documents should be locked away daily?",
                    "Are there exceptions to the clear desk policy?"
                ],
                # Advanced Salary Option (4 questions)
                "advanced_salary": [
                    "How can I request an advance on my salary?",
                    "What is the maximum advance salary I can get?",
                    "How is advance salary deducted from future pay?",
                    "What are the eligibility criteria for salary advance?"
                ]
            },
            "IT": {
                # Asset Request (4 questions)
                "asset_request": [
                    "How do I request a new laptop for work?",
                    "What is the process to get additional monitor?",
                    "Can I request software license for my project?",
                    "How long does IT asset approval take?"
                ],
                # Password Change Request (4 questions)
                "password_change": [
                    "How do I reset my Windows login password?",
                    "Can I change my email password myself?",
                    "What if I forgot my system password?",
                    "How often should I change my passwords?"
                ]
            }
        }
        return questions
    
    def add_questions_to_db(self, session):
        """
        Add all dummy questions to the database
        
        Args:
            session: Database session
            
        Returns:
            dict: Results with counts and errors
        """
        result = {
            "success": False,
            "total_added": 0,
            "by_department": {},
            "errors": []
        }
        
        try:
            questions_data = self.get_dummy_questions()
            
            for dept_name, policies in questions_data.items():
                dept_enum = DeptType(dept_name)
                dept_count = 0
                
                print(f"\n📝 Adding questions for {dept_name} department...")
                
                for policy_name, questions in policies.items():
                    print(f"  📋 Adding {len(questions)} questions for {policy_name}")
                    
                    for i, question_text in enumerate(questions, 1):
                        try:
                            # Create UserQuestion instance
                            user_question = UserQuestion(
                                userid=self.dummy_user_id,
                                query=question_text,
                                answer=None,  # No answer initially
                                context=None,  # Null context as requested
                                status=UserQuestionStatus.pending,
                                dept=dept_enum
                            )
                            
                            session.add(user_question)
                            dept_count += 1
                            print(f"    ✅ Added: {question_text}")
                            
                        except Exception as e:
                            error_msg = f"Failed to add question '{question_text}': {e}"
                            print(f"    ❌ {error_msg}")
                            result["errors"].append(error_msg)
                            continue
                
                result["by_department"][dept_name] = dept_count
                result["total_added"] += dept_count
            
            # Commit all changes
            session.commit()
            print(f"\n🎉 Successfully added {result['total_added']} questions to database")
            result["success"] = True
            
        except SQLAlchemyError as e:
            print(f"❌ Database error: {e}")
            session.rollback()
            result["errors"].append(f"Database error: {e}")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            session.rollback()
            result["errors"].append(f"Unexpected error: {e}")
        
        return result
    
    @staticmethod
    def verify_questions_added(session):
        """
        Verify that questions were added correctly
        
        Args:
            session: Database session
            
        Returns:
            dict: Verification results
        """
        try:
            # Get pending questions by department
            pending_by_dept = UserQuestion.fetch_pending_by_dept(session)
            
            print("\n🔍 Verification Results:")
            print("=" * 50)
            
            total_pending = 0
            for dept, questions in pending_by_dept.items():
                count = len(questions)
                total_pending += count
                print(f"{dept}: {count} pending questions")
                
                # Show first 2 questions for each department
                for i, q in enumerate(questions[:2]):
                    print(f"  {i+1}. {q['query']}")
                if len(questions) > 2:
                    print(f"  ... and {len(questions) - 2} more")
            
            print(f"\nTotal pending questions: {total_pending}")
            print("=" * 50)
            
            return {
                "success": True,
                "total_pending": total_pending,
                "by_department": {dept: len(questions) for dept, questions in pending_by_dept.items()}
            }
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return {"success": False, "error": str(e)}

def add_dummy_questions():
    """
    Main function to add dummy questions to the database
    """
    print("🚀 Starting dummy question generation...")
    
    # Create database session using Config
    session = Config.get_session()
    
    try:
        # Initialize generator
        generator = DummyQuestionGenerator()
        
        # Add questions to database
        result = generator.add_questions_to_db(session)
        
        # Print summary
        print("\n" + "=" * 60)
        print("DUMMY QUESTIONS SUMMARY")
        print("=" * 60)
        print(f"Success: {result['success']}")
        print(f"Total Questions Added: {result['total_added']}")
        
        if result['by_department']:
            print("\nBreakdown by Department:")
            for dept, count in result['by_department'].items():
                print(f"  {dept}: {count} questions")
        
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
        
        # Verify questions were added
        if result['success']:
            print("\n🔍 Verifying questions in database...")
            verification = generator.verify_questions_added(session)
            
            if verification['success']:
                expected_total = 28  # 7 policies × 4 questions each
                actual_total = verification['total_pending']
                
                if actual_total >= expected_total:
                    print("✅ All dummy questions added successfully!")
                else:
                    print(f"⚠️ Expected {expected_total} questions, but found {actual_total}")
            else:
                print(f"❌ Verification failed: {verification.get('error', 'Unknown error')}")
        
        print("=" * 60)
        return result
        
    except Exception as e:
        print(f"❌ Script failed: {e}")
        return {"success": False, "error": str(e)}
        
    finally:
        session.close()

def clear_dummy_questions():
    """
    Helper function to clear all pending questions (for testing)
    """
    print("🧹 Clearing existing dummy questions...")
    
    session = Config.get_session()  # Fixed to use Config
    try:
        # Delete all pending questions
        deleted_count = session.query(UserQuestion).filter(
            UserQuestion.status == UserQuestionStatus.pending
        ).delete()
        
        session.commit()
        print(f"✅ Cleared {deleted_count} pending questions from database")
        return {"success": True, "deleted_count": deleted_count}
        
    except Exception as e:
        print(f"❌ Failed to clear questions: {e}")
        session.rollback()
        return {"success": False, "error": str(e)}
        
    finally:
        session.close()

if __name__ == "__main__":
    # Uncomment the line below if you want to clear existing questions first
    # clear_dummy_questions()
    
    # Add dummy questions
    result = add_dummy_questions()
    
    if not result["success"]:
        exit(1)