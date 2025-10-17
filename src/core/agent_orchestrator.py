#!/usr/bin/env python3
"""
Agent Architecture 3.0: The Enterprise AgentOrchestrator
The central brain of the Autonomous Enterprise Builder.
Loads, manages, and dispatches tasks to the entire 140+ agent swarm.
"""
import os
import sys
import yaml
import importlib
import logging
from pathlib import Path
from datetime import datetime

# Add project root for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import existing enterprise components
try:
    from .knowledge_engine import KnowledgeEngine
    from .model_manager import ModelManager
    from .tool_registry import ToolRegistry
    from ..agents.base_agent import MockStateManager
except ImportError:
    # Fallback for standalone execution
    sys.path.append(str(PROJECT_ROOT / "src"))
    from core.knowledge_engine import KnowledgeEngine
    from core.model_manager import ModelManager
    from core.tool_registry import ToolRegistry
    from agents.base_agent import MockStateManager

class AgentOrchestrator:
    """
    The central orchestrator for the entire agent ecosystem.
    Manages 140+ agents across multiple specialized teams.
    """
    
    def __init__(self, config_root=None):
        self.project_root = PROJECT_ROOT
        self.config_root = self.project_root / (config_root or "config")
        self.logger = logging.getLogger("Agency.Orchestrator")
        
        # Agent management
        self.agents = {}
        self.teams = {}
        self.skills_registry = {}
        self.agent_status = {}
        
        # Initialize enterprise services
        self.logger.info("=== INITIALIZING ENTERPRISE SERVICES ===")
        self._initialize_services()
        
        # Load agent configuration
        self.logger.info("=== LOADING AGENT ECOSYSTEM ===")
        self._load_agent_ecosystem()
        
        self.logger.info(f"=== ORCHESTRATOR ONLINE: {len(self.agents)} AGENTS READY ===")
    
    def _initialize_services(self):
        """Initialize all core enterprise services with proper integration"""
        try:
            # Initialize ModelManager first
            self.logger.info("Initializing ModelManager...")
            model_manager = ModelManager()
            
            # Initialize KnowledgeEngine with ModelManager
            self.logger.info("Initializing KnowledgeEngine...")
            knowledge_engine = KnowledgeEngine(
                knowledge_base_path=str(self.project_root / "knowledge_base"),
                data_path=str(self.project_root / "data"),
                model_manager=model_manager  # ✅ Proper integration
            )
            
            # Initialize mock services for Step 1
            self.logger.info("Initializing StateManager (Mock)...")
            state_manager = MockStateManager(self.project_root / "data" / "agent_states")
            
            self.logger.info("Initializing ToolRegistry (Production)...")
            tool_registry = ToolRegistry(str(self.project_root / "src" / "tools"))
            
            # Service registry
            self.services = {
                "model_manager": model_manager,
                "knowledge_engine": knowledge_engine,
                "state_manager": state_manager,
                "tool_registry": tool_registry
            }
            
            self.logger.info("✅ All enterprise services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize services: {e}", exc_info=True)
            raise
    
    def _load_agent_ecosystem(self):
        """Load the complete agent ecosystem from hierarchical configuration"""
        try:
            # Load master registry
            registry_path = self.config_root / "agents" / "registry.yaml"
            if not registry_path.exists():
                raise FileNotFoundError(f"Agent registry not found: {registry_path}")
            
            with open(registry_path, 'r') as f:
                registry = yaml.safe_load(f)
            
            # Load each team
            for team_info in registry.get("agent_teams", []):
                team_name = team_info['name']
                team_config_file = team_info['config_file']
                
                self.logger.info(f"Loading team: {team_name}")
                self._load_team(team_name, team_config_file)
            
            # Build skills registry for intelligent dispatch
            self._build_skills_registry()
            
            self.logger.info(f"✅ Loaded {len(self.teams)} teams with {len(self.agents)} total agents")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load agent ecosystem: {e}", exc_info=True)
            raise
    
    def _load_team(self, team_name, config_file):
        """Load a specific agent team from configuration"""
        team_config_path = self.config_root / "agents" / config_file
        
        if not team_config_path.exists():
            self.logger.warning(f"Team config not found: {team_config_path}")
            return
        
        with open(team_config_path, 'r') as f:
            team_config = yaml.safe_load(f)
        
        # Store team metadata
        self.teams[team_name] = {
            'config': team_config.get('team_info', {}),
            'agents': [],
            'coordination': team_config.get('coordination', {}),
            'performance': team_config.get('performance', {})
        }
        
        # Load individual agents
        for agent_id, agent_config in team_config.get("agents", {}).items():
            full_agent_id = f"{team_name}.{agent_id}"
            
            try:
                agent = self._instantiate_agent(full_agent_id, agent_config)
                if agent:
                    self.agents[full_agent_id] = agent
                    self.teams[team_name]['agents'].append(full_agent_id)
                    self.agent_status[full_agent_id] = 'ready'
                    
                    self.logger.info(f"  ✅ Loaded agent: {full_agent_id}")
                else:
                    self.logger.warning(f"  ❌ Failed to load agent: {full_agent_id}")
                    
            except Exception as e:
                self.logger.error(f"  ❌ Error loading agent {full_agent_id}: {e}")
    
    def _instantiate_agent(self, agent_id, config):
        """Dynamically instantiate a single agent"""
        try:
            # Import the agent class
            module_path = config['path']
            class_name = config['class']
            
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            
            # Instantiate with enterprise services
            agent = agent_class(agent_id, config, self.services)
            
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to instantiate agent {agent_id}: {e}", exc_info=True)
            return None
    
    def _build_skills_registry(self):
        """Build registry mapping skills to agents for intelligent dispatch"""
        for agent_id, agent in self.agents.items():
            skills = agent.config.get('skills', [])
            for skill in skills:
                if skill not in self.skills_registry:
                    self.skills_registry[skill] = []
                self.skills_registry[skill].append(agent_id)
        
        self.logger.info(f"✅ Skills registry built: {len(self.skills_registry)} skills mapped")
    
    def find_best_agent_for_skill(self, skill, context=None):
        """
        Intelligent agent selection based on skill and context.
        Future: Will use KnowledgeEngine for context-aware selection.
        """
        candidate_agents = self.skills_registry.get(skill, [])
        
        if not candidate_agents:
            self.logger.warning(f"No agents found with skill: {skill}")
            return None
        
        # For Step 1: Simple selection (first available agent)
        # Step 2: Will add load balancing and context matching
        for agent_id in candidate_agents:
            if self.agent_status.get(agent_id) == 'ready':
                self.logger.info(f"Selected agent '{agent_id}' for skill '{skill}'")
                return self.agents[agent_id]
        
        self.logger.warning(f"No available agents for skill: {skill}")
        return None
    
    def execute_mission(self, skill, prompt, context=None):
        """
        Execute a mission by dispatching to the best available agent.
        This is the main interface for task execution.
        """
        self.logger.info(f"🚀 MISSION START: Skill='{skill}', Prompt='{prompt[:100]}...'")
        
        # Find the best agent
        agent = self.find_best_agent_for_skill(skill, context)
        if not agent:
            error_msg = f"No agent available for skill: {skill}"
            self.logger.error(f"❌ MISSION FAILED: {error_msg}")
            return {"error": error_msg, "skill": skill}
        
        # Update agent status
        agent_id = agent.agent_id
        self.agent_status[agent_id] = 'executing'
        
        try:
            # Execute the task
            self.logger.info(f"Dispatching to agent: {agent_id}")
            result = agent.execute_task(prompt, context)
            
            # Update status
            self.agent_status[agent_id] = 'ready'
            
            self.logger.info(f"✅ MISSION COMPLETED: Agent={agent_id}")
            return {
                "success": True,
                "agent_id": agent_id,
                "skill": skill,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.agent_status[agent_id] = 'error'
            error_msg = f"Agent {agent_id} execution failed: {str(e)}"
            self.logger.error(f"❌ MISSION FAILED: {error_msg}", exc_info=True)
            return {"error": error_msg, "agent_id": agent_id, "skill": skill}
    
    def get_system_status(self):
        """Get comprehensive system status for monitoring"""
        team_status = {}
        for team_name, team_info in self.teams.items():
            team_agents = team_info['agents']
            team_status[team_name] = {
                'total_agents': len(team_agents),
                'ready_agents': sum(1 for aid in team_agents if self.agent_status.get(aid) == 'ready'),
                'executing_agents': sum(1 for aid in team_agents if self.agent_status.get(aid) == 'executing'),
                'error_agents': sum(1 for aid in team_agents if self.agent_status.get(aid) == 'error')
            }
        
        return {
            'total_agents': len(self.agents),
            'total_teams': len(self.teams),
            'total_skills': len(self.skills_registry),
            'system_status': 'online',
            'team_status': team_status,
            'timestamp': datetime.now().isoformat()
        }
    
    def list_available_skills(self):
        """List all available skills in the system"""
        return list(self.skills_registry.keys())
    
    def get_agents_by_team(self, team_name):
        """Get all agents in a specific team"""
        team_info = self.teams.get(team_name)
        if team_info:
            return team_info['agents']
        return []

def setup_logging():
    """Setup enterprise-grade logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(PROJECT_ROOT / "agency.log")
        ]
    )

def main():
    """Main entry point for testing the orchestrator"""
    setup_logging()
    
    try:
        # Initialize the orchestrator
        orchestrator = AgentOrchestrator()
        
        print("\n" + "="*80)
        print("🚀 AUTONOMOUS ENTERPRISE AGENCY - ORCHESTRATOR ONLINE 🚀")
        print("="*80)
        
        # Display system status
        status = orchestrator.get_system_status()
        print(f"\n📊 SYSTEM STATUS:")
        print(f"   Total Agents: {status['total_agents']}")
        print(f"   Total Teams: {status['total_teams']}")
        print(f"   Available Skills: {status['total_skills']}")
        
        # Display available skills
        skills = orchestrator.list_available_skills()
        print(f"\n🎯 AVAILABLE SKILLS: {', '.join(skills[:10])}{'...' if len(skills) > 10 else ''}")
        
        # Test mission execution
        print(f"\n🚀 TESTING MISSION EXECUTION...")
        result = orchestrator.execute_mission(
            skill="fastapi",
            prompt="Create a FastAPI backend for a task management system with user authentication",
            context={"project_type": "enterprise", "database": "postgresql"}
        )
        
        print(f"\n📋 MISSION RESULT:")
        if result.get('success'):
            print(f"   ✅ Success! Agent: {result['agent_id']}")
            print(f"   📝 Result Type: {type(result['result']).__name__}")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*80)
        print("🎉 ORCHESTRATOR TEST COMPLETE")
        print("="*80 + "\n")
        
    except Exception as e:
        logging.error(f"Orchestrator initialization failed: {e}", exc_info=True)
        print(f"❌ FAILED TO START ORCHESTRATOR: {e}")

if __name__ == "__main__":
    main()
