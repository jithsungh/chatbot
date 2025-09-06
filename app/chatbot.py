import os
import warnings
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()

class AdaptiveKnowledgeChatbot:
    def __init__(self, persist_directory="./chroma_db", collection_name="manuals"):
        """Initialize the chatbot with all required components"""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._setup_embeddings()
        self._setup_vectorstore()
        self._setup_llm()
        self._setup_memory()
        self._setup_chain()
    
    def _setup_embeddings(self):
        """Initialize the embedding model"""
        try:
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("✅ Embedding model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            raise
    
    def _setup_vectorstore(self):
        """Initialize ChromaDB vectorstore"""
        try:
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_model
            )
            
            # Check if vectorstore has any documents
            collection_count = self.vectorstore._collection.count()
            print(f"✅ ChromaDB loaded with {collection_count} documents")
            
            if collection_count == 0:
                print("⚠️  Warning: No documents found in knowledge base. Run feed.py first.")
            
            # Setup retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
        except Exception as e:
            print(f"❌ Error setting up vectorstore: {e}")
            raise
    
    def _setup_llm(self):
        """Initialize Groq LLaMA model"""
        try:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.llm = ChatGroq(
                api_key=groq_api_key,
                model_name="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=1000
            )
            print("✅ Groq LLaMA model initialized successfully")
        except Exception as e:
            print(f"❌ Error setting up LLM: {e}")
            raise
    
    def _setup_memory(self):
        """Initialize conversation memory"""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="question",
                output_key="answer"
            )
        print("✅ Conversation memory initialized")
    
    def _setup_chain(self):
        """Initialize the conversational retrieval chain"""
        try:
            # Improved prompt template - less restrictive but still controlled
            prompt_template = """Use the provided CONTEXT to answer the question. If the CONTEXT contains relevant information, provide a clear, direct answer. If the CONTEXT doesn't contain the answer, you may use general knowledge for basic facts, arithmetic, or common knowledge questions.

CONTEXT:
{context}

CHAT_HISTORY:
{chat_history}

QUESTION: {question}

ANSWER:"""

            self.prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "chat_history", "question"]
            )
            
            # Create the conversational retrieval chain
            self.qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.retriever,
                memory=self.memory,
                combine_docs_chain_kwargs={"prompt": self.prompt},
                return_source_documents=True,
                verbose=False
            )
            print("✅ Conversational chain initialized successfully")
        except Exception as e:
            print(f"❌ Error setting up chain: {e}")
            raise
    
    def ask_question(self, question: str) -> dict:
        """
        Ask a question to the chatbot
        
        Args:
            question (str): The user's question
            
        Returns:
            dict: Contains 'answer', 'source_documents', 'confidence', and 'context'
        """
        try:
            # Get retrieved documents first for context extraction
            retrieved_docs = self.retriever.get_relevant_documents(question)
            
            # Use invoke method (newer LangChain API)
            result = self.qa_chain.invoke({"question": question})
            
            # Calculate confidence based on source document relevance
            confidence = self._calculate_confidence(result.get('source_documents', []))
            
            # Extract context from retrieved documents
            context_texts = [doc.page_content for doc in retrieved_docs]
            
            return {
                "answer": result["answer"],
                "source_documents": result.get("source_documents", []),
                "confidence": confidence,
                "context": context_texts,
                "success": True
            }
        except Exception as e:
            print(f"❌ Error processing question: {e}")
            return {
                "answer": "I'm sorry, I encountered an error while processing your question.",
                "source_documents": [],
                "confidence": 0.0,
                "context": [],
                "success": False,
                "error": str(e)
            }
    
    def _calculate_confidence(self, source_docs) -> float:
        """Calculate confidence score based on retrieved documents"""
        if not source_docs:
            return 0.1  # Low confidence if no relevant docs found
        
        # Simple confidence calculation based on number of relevant docs
        if len(source_docs) >= 3:
            return 0.9
        elif len(source_docs) >= 2:
            return 0.7
        else:
            return 0.5
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        print("✅ Conversation memory cleared")
    
    def get_vectorstore_info(self):
        """Get information about the vectorstore"""
        try:
            count = self.vectorstore._collection.count()
            return {
                "document_count": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            print(f"❌ Error getting vectorstore info: {e}")
            return None