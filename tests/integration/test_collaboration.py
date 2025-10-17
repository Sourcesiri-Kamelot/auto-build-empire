"""
Test collaboration between Market Intel and User Research agents
Methodical testing - NO PLACEHOLDERS
"""
import sys
import os
sys.path.append('.')

from app.agents.research_consortium.market_intel import MarketIntelAgent
from app.agents.research_consortium.user_research import UserResearchAgent
import json

def test_two_agent_collaboration():
    """Test basic collaboration between 2 agents"""
    
    print("🧪 Testing 2-Agent Collaboration...")
    
    # Initialize agents
    market_agent = MarketIntelAgent()
    user_agent = UserResearchAgent()
    
    # Test business idea
    business_idea = "AI-powered sports coaching platform for youth"
    
    print(f"\n💡 Business Idea: {business_idea}")
    print("=" * 60)
    
    # Agent 1: Market Analysis
    print("\n🔍 PHASE 1: Market Intelligence Analysis")
    market_result = market_agent.analyze_market(business_idea)
    
    if market_result["status"] == "completed":
        print(f"✅ Market Agent completed (Confidence: {market_result['confidence']})")
        print(f"📊 Analysis length: {len(market_result['analysis'])} characters")
    else:
        print(f"❌ Market Agent failed: {market_result['analysis']}")
        return False
    
    # Agent 2: User Research  
    print("\n👥 PHASE 2: User Research Analysis")
    user_result = user_agent.analyze_users(business_idea)
    
    if user_result["status"] == "completed":
        print(f"✅ User Agent completed (Confidence: {user_result['confidence']})")
        print(f"📊 Analysis length: {len(user_result['analysis'])} characters")
    else:
        print(f"❌ User Agent failed: {user_result['analysis']}")
        return False
    
    # Combine results
    combined_research = {
        "business_idea": business_idea,
        "market_analysis": market_result,
        "user_research": user_result,
        "collaboration_status": "successful",
        "total_confidence": (market_result["confidence"] + user_result["confidence"]) / 2
    }
    
    # Save results
    with open("collaboration_test_results.json", "w") as f:
        json.dump(combined_research, f, indent=2)
    
    print(f"\n🎯 COLLABORATION SUMMARY:")
    print(f"✅ Both agents completed successfully")
    print(f"📈 Combined confidence: {combined_research['total_confidence']:.2f}")
    print(f"💾 Results saved to: collaboration_test_results.json")
    
    return True

if __name__ == "__main__":
    success = test_two_agent_collaboration()
    
    if success:
        print("\n🏆 2-AGENT COLLABORATION TEST PASSED!")
        print("Ready for next step: Build 3rd agent or enhance collaboration")
    else:
        print("\n❌ Collaboration test failed - fix issues before proceeding")
