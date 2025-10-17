import sys
import time
sys.path.append('../')
from src.core.knowledge_engine import KnowledgeEngine

def test_knowledge_engine():
    knowledge_base_path = "/Volumes/heloimai 1/autonomous_enterprise_builder/knowledge_base"
    data_path = "/Volumes/heloimai 1/autonomous_enterprise_builder/data"
    
    engine = KnowledgeEngine(knowledge_base_path, data_path)
    engine.start()
    time.sleep(3)
    
    results = engine.query("machine learning", n_results=2)
    stats = engine.get_stats()
    
    engine.stop()
    print(f"Test complete. Stats: {stats}")

if __name__ == "__main__":
    test_knowledge_engine()
