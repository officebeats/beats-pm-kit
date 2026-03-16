import json
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Path setup
CURRENT_FILE = Path(__file__).resolve()
SYSTEM_ROOT = CURRENT_FILE.parent.parent
BRAIN_ROOT = SYSTEM_ROOT.parent
SKILLS_FILE = SYSTEM_ROOT / "skills.json"
AGENTS_DIR = BRAIN_ROOT / ".agent" / "agents"

def clean_text(text: str) -> str:
    """Basic text cleaning for vectorization."""
    text = text.lower()
    # Remove markdown formatting, special chars, and numbers
    text = re.sub(r'[#\*_\-\[\]\(\)`!]', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return ' '.join(text.split())

class VortexRouter:
    """
    Local Semantic Router (The Vortex Engine).
    Implements TF-IDF + Cosine Similarity using NumPy.
    """
    
    def __init__(self):
        self.skills_data = self._load_data()
        self.vocabulary: Dict[str, int] = {}
        self.skill_vectors: np.ndarray = None
        self.agent_map: List[str] = []
        self.idf: np.ndarray = None
        
        self._initialize_vortex()

    def _load_data(self) -> Dict[str, str]:
        """Loads and consolidates text descriptions for each agent."""
        if not SKILLS_FILE.exists():
            return {}
            
        with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
            skills_raw = json.load(f)
            
        # We need to map skills back to agents
        # Note: agent_dispatcher.py has the definitive AGENT_SKILLS map.
        # But we can also derive it from the agents folder.
        
        agent_text: Dict[str, str] = {}
        
        # Load agent personas
        if AGENTS_DIR.exists():
            for agent_file in AGENTS_DIR.glob("*.md"):
                agent_name = agent_file.stem
                content = agent_file.read_text(encoding='utf-8')
                agent_text[agent_name] = clean_text(content)
                
        # Supplement with skill descriptions
        # (This is a simplified mapping, ideally we'd use AGENT_SKILLS from dispatcher)
        # For now, we enrich based on available skills
        for skill_name, info in skills_raw.items():
            desc = info.get("description", "")
            # Find which agent "owns" this skill text (heuristically)
            # In a full impl, we'd import AGENT_SKILLS
            pass 
            
        return agent_text

    def _initialize_vortex(self):
        """Initializes the TF-IDF matrix."""
        corpus = []
        self.agent_map = []
        
        for agent, text in self.skills_data.items():
            self.agent_map.append(agent)
            corpus.append(text)
            
        if not corpus:
            return

        # 1. Build Vocabulary
        all_words = set()
        for doc in corpus:
            all_words.update(doc.split())
        self.vocabulary = {word: i for i, word in enumerate(sorted(list(all_words)))}
        
        num_docs = len(corpus)
        num_words = len(self.vocabulary)
        
        # 2. Compute TF
        tf = np.zeros((num_docs, num_words))
        for i, doc in enumerate(corpus):
            words = doc.split()
            for word in words:
                if word in self.vocabulary:
                    tf[i, self.vocabulary[word]] += 1
            # Normalize TF (optional but recommended)
            doc_len = len(words)
            if doc_len > 0:
                tf[i] = tf[i] / doc_len
                
        # 3. Compute IDF
        df = np.sum(tf > 0, axis=0)
        self.idf = np.log(num_docs / (1 + df))
        
        # 4. Compute TF-IDF
        self.skill_vectors = tf * self.idf
        
        # Normalize vectors for cosine similarity (now just dot product)
        norms = np.linalg.norm(self.skill_vectors, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1
        self.skill_vectors = self.skill_vectors / norms

    def route_query(self, query: str, top_k: int = 2) -> List[str]:
        """Routes a query to the most relevant agents."""
        if self.skill_vectors is None:
            return ["staff-pm"] # Fallback
            
        clean_query = clean_text(query)
        words = clean_query.split()
        
        # Vectorize query
        q_vec = np.zeros(len(self.vocabulary))
        for word in words:
            if word in self.vocabulary:
                q_vec[self.vocabulary[word]] += 1
        
        # Apply normalization to query vector
        q_len = len(words)
        if q_len > 0:
            q_vec = q_vec / q_len
            
        # Apply IDF
        q_tfidf = q_vec * self.idf
        
        # Normalize
        norm = np.linalg.norm(q_tfidf)
        if norm > 0:
            q_tfidf = q_tfidf / norm
            
        # Compute similarities
        similarities = np.dot(self.skill_vectors, q_tfidf)
        
        # Get indices of top matches
        indices = np.argsort(similarities)[::-1]
        
        results = []
        for i in range(min(top_k, len(indices))):
            if similarities[indices[i]] > 0:
                results.append(self.agent_map[indices[i]])
                
        return results if results else ["staff-pm"]

# Singleton instance
_router = None

def get_vortex_router():
    global _router
    if _router is None:
        _router = VortexRouter()
    return _router

if __name__ == "__main__":
    # Internal test
    router = get_vortex_router()
    test_query = "i need someone to help me triage some bugs and check the metrics of our last release"
    print(f"Query: {test_query}")
    print(f"Recommended Agents: {router.route_query(test_query)}")
