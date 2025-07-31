from app.scope.step_logger import StepLogger
import os

# Simplified RAG agent without complex dependencies
# You can enhance this later with actual vector stores

logger = StepLogger()

# Simple policy document storage
POLICY_PATH = "policies/"
os.makedirs(POLICY_PATH, exist_ok=True)

# Simple in-memory policy storage for demo
POLICY_DOCS = {}

def upload_policy_docs(name: str = None, content: str = None):
    """
    Simple policy document upload - stores in memory for demo
    In production, this would use ChromaDB or similar
    """
    try:
        if name and content:
            POLICY_DOCS[name] = content
            return True
        
        # Load from files if no direct content provided
        policy_files = [f for f in os.listdir(POLICY_PATH) if f.endswith('.txt')]
        for file in policy_files:
            with open(os.path.join(POLICY_PATH, file), 'r', encoding='utf-8') as f:
                POLICY_DOCS[file] = f.read()
        
        return len(POLICY_DOCS) > 0
    except Exception as e:
        print(f"Error loading policy docs: {e}")
        return False

def fetch_policy_evidence(query: str, transaction_id: str = "unknown") -> str:
    """
    Simple policy retrieval - searches in stored documents
    In production, this would use vector similarity search
    """
    try:
        # Simple keyword matching for demo
        relevant_policies = []
        
        for doc_name, content in POLICY_DOCS.items():
            if any(keyword.lower() in content.lower() for keyword in query.split()):
                relevant_policies.append(content[:200] + "..." if len(content) > 200 else content)
        
        if not relevant_policies:
            # Load default policy if none found
            upload_policy_docs()
            for doc_name, content in POLICY_DOCS.items():
                if any(keyword.lower() in content.lower() for keyword in query.split()):
                    relevant_policies.append(content[:200] + "..." if len(content) > 200 else content)
        
        reason = relevant_policies[0] if relevant_policies else "No relevant policy clause found."
        
        logger.log_step(
            transaction_id=transaction_id,
            step=99,
            component="RAGPolicyRetriever",
            input_data={"query": query},
            description=reason,
            confidence=0.87
        )
        
        return reason
        
    except Exception as e:
        error_msg = f"Error retrieving policy evidence: {e}"
        logger.log_step(
            transaction_id=transaction_id,
            step=99,
            component="RAGPolicyRetriever",
            input_data={"query": query},
            description=error_msg,
            confidence=0.1
        )
        return error_msg

# Initialize with default policies on import
upload_policy_docs()