#!/usr/bin/env python3
"""Production ModelManager verification test"""

import sys
sys.path.append('../')

from src.core.model_manager import ModelManager

def test_production_models():
    print("=== PRODUCTION MODEL MANAGER VERIFICATION ===")
    
    # Initialize production ModelManager
    model_manager = ModelManager()
    
    # Test all connections
    model_manager.test_connections()
    
    # Test capability routing
    print("\n=== TESTING CAPABILITY ROUTING ===")
    
    capabilities = ["general_purpose", "code_generation", "creative_writing"]
    
    for capability in capabilities:
        print(f"\nTesting {capability}:")
        model = model_manager.get_model(capability)
        
        if model:
            try:
                response = model.generate(f"Test {capability} - respond with capability name")
                print(f"  Response: {response[:100]}...")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"  No model available for {capability}")
    
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    test_production_models()
