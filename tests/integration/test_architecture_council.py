"""
Test complete Architecture Council (3 agents working together)
Methodical testing - NO PLACEHOLDERS
"""
import sys
import os
sys.path.append('.')

from app.agents.architecture_council.system_designer import SystemDesignerAgent
from app.agents.architecture_council.db_architect import DBArchitectAgent
from app.agents.architecture_council.api_architect import APIArchitectAgent
import json

def test_architecture_council():
    """Test complete Architecture Council collaboration"""
    
    print("🧪 Testing Architecture Council (3 Agents)...")
    
    # Initialize all architecture agents
    system_agent = SystemDesignerAgent()
    db_agent = DBArchitectAgent()
    api_agent = APIArchitectAgent()
    
    # Input from Research Consortium
    research_input = {
        "business_idea": "AI-powered sports coaching platform for youth",
        "research_complete": True
    }
    
    print(f"\n💡 Business Idea: {research_input['business_idea']}")
    print("=" * 70)
    
    results = {}
    
    # Agent 1: System Design
    print("\n🏗️ PHASE 1: System Architecture Design")
    system_result = system_agent.design_system(research_input)
    
    if system_result["status"] == "completed":
        print(f"✅ System Designer completed (Confidence: {system_result['confidence']})")
        results["system"] = system_result
    else:
        print(f"❌ System Designer failed: {system_result['architecture']}")
        return False
    
    # Agent 2: Database Design
    print("\n🗄️ PHASE 2: Database Architecture Design")
    db_result = db_agent.design_database(system_result)
    
    if db_result["status"] == "completed":
        print(f"✅ Database Architect completed (Confidence: {db_result['confidence']})")
        results["database"] = db_result
    else:
        print(f"❌ Database Architect failed: {db_result['database_design']}")
        return False
    
    # Agent 3: API Design
    print("\n🔌 PHASE 3: API Architecture Design")
    api_result = api_agent.design_apis(system_result)
    
    if api_result["status"] == "completed":
        print(f"✅ API Architect completed (Confidence: {api_result['confidence']})")
        results["api"] = api_result
    else:
        print(f"❌ API Architect failed: {api_result['api_design']}")
        return False
    
    # Calculate council results
    total_confidence = (
        results["system"]["confidence"] + 
        results["database"]["confidence"] + 
        results["api"]["confidence"]
    ) / 3
    
    council_output = {
        "business_idea": research_input["business_idea"],
        "architecture_council": {
            "system_design": results["system"],
            "database_design": results["database"], 
            "api_design": results["api"]
        },
        "council_status": "completed",
        "council_confidence": total_confidence,
        "phase": "Architecture Council Complete"
    }
    
    # Save complete architecture results
    with open("architecture_council_results.json", "w") as f:
        json.dump(council_output, f, indent=2)
    
    print(f"\n🎯 ARCHITECTURE COUNCIL SUMMARY:")
    print(f"✅ All 3 agents completed successfully")
    print(f"📈 Council confidence: {total_confidence:.2f}")
    print(f"💾 Complete architecture saved to: architecture_council_results.json")
    
    return True

if __name__ == "__main__":
    success = test_architecture_council()
    
    if success:
        print("\n🏆 ARCHITECTURE COUNCIL COMPLETE!")
        print("Ready for next step: Build Development Squad (Phase 3)")
    else:
        print("\n❌ Architecture Council failed - fix issues before proceeding")
