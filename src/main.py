#!/usr/bin/env python3
"""
AUTONOMOUS ENTERPRISE BUILDER - MAIN ENTRY POINT
Production-grade system initialization and orchestration
"""

import sys
import os
import yaml
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class EnterpriseContext:
    """Central configuration and context manager"""
    
    def __init__(self, config_path="config/main.yaml"):
        self.config_path = config_path
        self.config = self._load_master_config()
        self.paths = self.config.get("paths", {})
        self._setup_logging()
        
        print("[EnterpriseContext] Master configuration loaded successfully")
    
    def _load_master_config(self):
        """Load master configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                print(f"[EnterpriseContext] Configuration loaded from {self.config_path}")
                return config
        except FileNotFoundError:
            print(f"[EnterpriseContext] WARNING: Config not found at {self.config_path}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"[EnterpriseContext] ERROR: Invalid YAML in {self.config_path}: {e}")
            sys.exit(1)
    
    def _get_default_config(self):
        """Fallback configuration"""
        return {
            "system": {"name": "Autonomous Enterprise Builder", "version": "3.0"},
            "paths": {
                "knowledge_base": "knowledge_base",
                "models": "models", 
                "data": "data"
            },
            "services": {
                "knowledge_engine": {"enabled": True},
                "model_manager": {"enabled": True},
                "orchestrator": {"enabled": True}
            }
        }
    
    def _setup_logging(self):
        """Setup system logging"""
        log_config = self.config.get("logging", {})
        level = getattr(logging, log_config.get("level", "INFO"))
        format_str = log_config.get("format", "[%(name)s] %(message)s")
        
        logging.basicConfig(level=level, format=format_str)

def initialize_system(context):
    """Initialize all system components"""
    print("\n=== AUTONOMOUS ENTERPRISE BUILDER INITIALIZATION ===")
    
    services = context.config.get("services", {})
    
    # Initialize ModelManager
    if services.get("model_manager", {}).get("enabled", True):
        try:
            from src.core.model_manager import ModelManager
            model_manager = ModelManager()
            
            if services.get("model_manager", {}).get("test_connections", False):
                model_manager.test_connections()
                
            print("[System] ModelManager initialized successfully")
        except Exception as e:
            print(f"[System] ERROR: ModelManager failed to initialize: {e}")
            return None
    
    # Initialize KnowledgeEngine
    if services.get("knowledge_engine", {}).get("enabled", True):
        try:
            from src.core.knowledge_engine import KnowledgeEngine
            
            knowledge_engine = KnowledgeEngine(
                context.paths.get("knowledge_base"),
                context.paths.get("data"),
                model_manager
            )
            
            if services.get("knowledge_engine", {}).get("auto_start", True):
                knowledge_engine.start()
                
            print("[System] KnowledgeEngine initialized successfully")
        except Exception as e:
            print(f"[System] ERROR: KnowledgeEngine failed to initialize: {e}")
    
    # Initialize Orchestrator
    if services.get("orchestrator", {}).get("enabled", True):
        try:
            from src.core.orchestrator import Orchestrator
            orchestrator = Orchestrator()
            print("[System] Orchestrator initialized successfully")
            return orchestrator
        except Exception as e:
            print(f"[System] ERROR: Orchestrator failed to initialize: {e}")
            return None
    
    return None

def main():
    """Main system entry point"""
    print("🤖 AUTONOMOUS ENTERPRISE BUILDER v3.0")
    print("Production-Grade Autonomous System")
    print("="*50)
    
    # Initialize enterprise context
    try:
        context = EnterpriseContext()
    except Exception as e:
        print(f"FATAL: Failed to initialize enterprise context: {e}")
        return 1
    
    # Initialize system components
    orchestrator = initialize_system(context)
    
    if not orchestrator:
        print("FATAL: System initialization failed")
        return 1
    
    print("\n✅ SYSTEM ONLINE - Ready for autonomous operations")
    print("Use Ctrl+C to shutdown gracefully")
    
    try:
        # Keep system running
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[System] Graceful shutdown initiated...")
        
        # Cleanup
        if hasattr(orchestrator, 'knowledge_engine'):
            orchestrator.knowledge_engine.stop()
        
        print("[System] Shutdown complete")
        return 0
    
    except Exception as e:
        print(f"FATAL: Runtime error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
