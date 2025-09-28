import json
import uuid
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from src.service.question_deduplicator import fetch_and_deduplicate_pending_questions
from src.service.question_summarizer import QuestionSummarizer
from src.models.admin_question import AdminQuestion, AdminQuestionStatus
from src.models.user_question import DeptType, UserQuestion, UserQuestionStatus

class QuestionFilter:
    
    def __init__(self):
        """Initialize with summarizer instance"""
        try:
            self.summarizer = QuestionSummarizer()
        except Exception as e:
            print(f"❌ Failed to initialize QuestionSummarizer: {e}")
            raise

    @staticmethod
    def _get_dept_enum(dept_string: str) -> Optional[DeptType]:
        """Convert department string to DeptType enum"""
        try:
            if dept_string == "Unassigned" or not dept_string:
                return None
            return DeptType(dept_string)
        except ValueError:
            print(f"⚠️ Unknown department: {dept_string}, treating as unassigned")
            return None

    @staticmethod
    def _mark_user_questions_as_processed(session, clustered_by_dept):
        """Mark original user questions as processed"""
        try:
            with session.no_autoflush:  # Prevent autoflush during this operation
                processed_count = 0
                for dept, clusters in clustered_by_dept.items():
                    for cluster in clusters:
                        for question_dict in cluster:
                            try:
                                question_id = uuid.UUID(question_dict["id"])
                                user_question = session.query(UserQuestion).filter(
                                    UserQuestion.id == question_id
                                ).first()
                                if user_question:
                                    user_question.status = UserQuestionStatus.processed
                                    processed_count += 1
                            except (ValueError, KeyError) as e:
                                print(f"⚠️ Invalid question ID format: {question_dict.get('id', 'unknown')}")
                                continue
                print(f"✅ Marked {processed_count} user questions as processed")
                return processed_count
        except Exception as e:
            print(f"❌ Error marking user questions as processed: {e}")
            raise
            # return 0

    def filter_and_process_questions(self, session, similarity_threshold=0.4, default_admin_id=None):
        """
        Fetch pending user questions, deduplicate and cluster them,
        then summarize each cluster into representative questions.

        Store the summarized questions back into the database as AdminQuestion entries.
        Return the number of summarized questions added.
        
        Args:
            session: Database session
            similarity_threshold: Threshold for clustering similar questions
            default_admin_id: Default admin ID to use (can be None if field is nullable)
        
        Returns:
            dict: Results containing count and any errors
        """
        result = {
            "success": False,
            "questions_added": 0,
            "questions_processed": 0,
            "errors": []
        }

        try:
            # Use no_autoflush context to prevent premature flushes
            with session.no_autoflush:
                # Step 1: Fetch and deduplicate pending questions
                print("🔍 Fetching and deduplicating pending questions...")
                clustered_by_dept = fetch_and_deduplicate_pending_questions(
                    session, similarity_threshold, debug_mode=False  # Set to False for production
                )
                
                if not clustered_by_dept:
                    print("ℹ️ No pending questions found")
                    result["success"] = True
                    return result

                print(f"📊 Found clusters in departments: {list(clustered_by_dept.keys())}")

                # Step 2: Summarize clusters into representative questions
                print("🤖 Summarizing question clusters...")
                try:
                    summarized_by_dept = self.summarizer.summarize_clusters(clustered_by_dept)
                except Exception as e:
                    error_msg = f"Failed to summarize clusters: {e}"
                    print(f"❌ {error_msg}")
                    result["errors"].append(error_msg)
                    return result

                # Step 3: Store summarized questions in AdminQuestion table
                print("💾 Storing summarized questions to database...")
                count = 0
                
                for dept, summaries in summarized_by_dept.items():
                    dept_enum = self._get_dept_enum(dept)
                    
                    for summary_json in summaries:
                        try:
                            # Try to parse the JSON response from LLM
                            parsed = json.loads(summary_json)
                            representative_question = parsed.get("representative_question", "")
                            acceptance_criteria = parsed.get("acceptance_criteria", "")
                            
                            if not representative_question:
                                print(f"⚠️ Empty representative question for dept {dept}, skipping")
                                continue
                                
                            # Calculate frequency based on original questions count
                            original_questions = parsed.get("original_questions", [])
                            frequency = len(original_questions) if isinstance(original_questions, list) else 1
                            
                        except (json.JSONDecodeError, KeyError) as e:
                            print(f"⚠️ Failed to parse LLM response for dept {dept}: {e}")
                            print(f"Raw response: {summary_json[:200]}...")
                            # Use raw response as fallback
                            representative_question = summary_json[:500]  # Truncate if too long
                            frequency = 1

                        try:
                            # Create new AdminQuestion with explicit field mapping
                            new_admin_question = AdminQuestion(
                                id=uuid.uuid4(),  # Explicitly set ID
                                adminid=default_admin_id,
                                question=representative_question,
                                notes=acceptance_criteria,
                                answer=None,  # Explicitly set answer as None
                                status=AdminQuestionStatus.pending,
                                dept=dept_enum,
                                frequency=frequency,
                                vectordbid=None  # Explicitly set vectordbid as None
                            )
                            session.add(new_admin_question)
                            count += 1
                            print(f"✅ Added question for {dept}: {representative_question[:100]}...")
                            
                        except Exception as e:
                            error_msg = f"Failed to create AdminQuestion for dept {dept}: {e}"
                            print(f"❌ {error_msg}")
                            result["errors"].append(error_msg)
                            continue

                # Step 4: Mark original user questions as processed
                print("🔄 Marking original user questions as processed...")
                procesed_count = self._mark_user_questions_as_processed(session, clustered_by_dept)

                # Manual flush to check for errors before commit
                print("🔄 Flushing changes to database...")
                session.flush()

            # Commit all changes outside the no_autoflush block
            print("💾 Committing changes...")
            session.commit()
            print(f"🎉 Successfully processed {count} question clusters")
            
            result["success"] = True
            result["questions_added"] = count
            result["questions_processed"] = procesed_count

        except SQLAlchemyError as e:
            print(f"❌ Database error: {e}")
            session.rollback()
            result["errors"].append(f"Database error: {e}")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            session.rollback()
            result["errors"].append(f"Unexpected error: {e}")

        return result

# Test function to validate the pipeline
def test_pipeline():
    """Test function to validate the question processing pipeline"""
    from src.config import Config
     
    session = Config.get_session()
    try:
        # Initialize filter instance
        question_filter = QuestionFilter()
        
        result = question_filter.filter_and_process_questions(
            session=session,
            similarity_threshold=0.4,
            default_admin_id=None  # Using None since adminid is now nullable
        )
        
        print("\n" + "="*50)
        print("PIPELINE TEST RESULTS")
        print("="*50)
        print(f"Success: {result['success']}")
        print(f"Questions Added: {result['questions_added']}")
        if result.get('questions_processed'):
            print(f"Questions Processed: {result['questions_processed']}")
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        print("="*50)
        
        return result
        
    except Exception as e:
        print(f"❌ Test pipeline failed: {e}")
        return {"success": False, "errors": [str(e)]}
    finally:
        session.close()

# if __name__ == "__main__":
#     test_pipeline()