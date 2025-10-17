"""
Test complete Research Consortium (3 agents working together)
Methodical testing - NO PLACEHOLDERS
"""
import sys
import os
sys.path.append('.')

from app.agents.research_consortium.market_intel import MarketIntelAgent
from app.agents.research_consortium.user_research import UserResearchAgent
from app.agents.research_consortium.business_analyst import BusinessAnalystAgent
import json

def test_research_consortium():
    """Test complete Research Consortium collaboration"""
    
    print("🧪 Testing Research Consortium (3 Agents)...")
    
    # Initialize all research agents
    market_agent = MarketIntelAgent()
    user_agent = UserResearchAgent()
    business_agent = BusinessAnalystAgent()
    
    # Test business idea
    business_idea = "AI-powered sports coaching platform for youth"
    
    print(f"\n💡 Business Idea: {business_idea}")
    print("=" * 70)
    
    results = {}
    
    # Agent 1: Market Intelligence
    print("\n🔍 PHASE 1: Market Intelligence Analysis")
    market_result = market_agent.analyze_market(business_idea)
    
    if market_result["status"] == "completed":
        print(f"✅ Market Agent completed (Confidence: {market_result['confidence']})")
        results["market"] = market_result
    else:
        print(f"❌ Market Agent failed: {market_result['analysis']}")
        return False
    
    # Agent 2: User Research
    print("\n👥 PHASE 2: User Research Analysis")
    user_result = user_agent.analyze_users(business_idea)
    
    if user_result["status"] == "completed":
        print(f"✅ User Research Agent completed (Confidence: {user_result['confidence']})")
        results["users"] = user_result
    else:
        print(f"❌ User Research Agent failed: {user_result['analysis']}")
        return False
    
    # Agent 3: Business Analysis
    print("\n💰 PHASE 3: Business Analysis")
    business_result = business_agent.analyze_business(business_idea)
    
    if business_result["status"] == "completed":
        print(f"✅ Business Analyst completed (Confidence: {business_result['confidence']})")
        results["business"] = business_result
    else:
        print(f"❌ Business Analyst failed: {business_result['analysis']}")
        return False
    
    # Calculate consortium results
    total_confidence = (
        results["market"]["confidence"] + 
        results["users"]["confidence"] + 
        results["business"]["confidence"]
    ) / 3
    
    consortium_output = {
        "business_idea": business_idea,
        "research_consortium": {
            "market_intelligence": results["market"],
            "user_research": results["users"], 
            "business_analysis": results["business"]
        },
        "consortium_status": "completed",
        "consortium_confidence": total_confidence,
        "phase": "Research Consortium Complete"
    }
    
    # Save complete research results
    with open("research_consortium_results.json", "w") as f:
        json.dump(consortium_output, f, indent=2)
    
    print(f"\n🎯 RESEARCH CONSORTIUM SUMMARY:")
    print(f"✅ All 3 agents completed successfully")
    print(f"📈 Consortium confidence: {total_confidence:.2f}")
    print(f"💾 Complete research saved to: research_consortium_results.json")
    
    return True

if __name__ == "__main__":
    success = test_research_consortium()
    
    if success:
        print("\n🏆 RESEARCH CONSORTIUM COMPLETE!")
        print("Ready for next step: Build Architecture Council (Phase 2)")
    else:
        print("\n❌ Research Consortium failed - fix issues before proceeding")
