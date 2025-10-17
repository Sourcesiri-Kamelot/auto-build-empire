#!/usr/bin/env python3
"""
WebsiteBuilder Agent (Architecture 3.0) - Digital Presence Squad
Full-stack agent for creating and deploying complete web applications.
"""
import json
import re
from pathlib import Path
from ...base_agent import BaseAgent

class WebsiteBuilder(BaseAgent):
    """
    An enterprise-grade agent that designs, builds, and prepares for deployment
    complete web applications, from frontend to backend.
    """

    def _prepare_prompt(self, prompt: str, context: dict) -> str:
        """Constructs a detailed prompt for a full-stack web development task."""
        self.logger.info("Preparing prompt for full-stack website build...")
        
        # Leverage Knowledge Engine for best practices
        dev_context = ""
        if self.knowledge_engine:
            knowledge_tool = self.get_tool("knowledge_query")
            if knowledge_tool:
                results = knowledge_tool(query="full-stack web development best practices", max_results=3)
                if results.get("success"):
                    dev_context = "\n".join([res['content'][:300] for res in results.get("results", [])])

        # Load system prompt
        try:
            prompt_path = Path(__file__).parent / "prompt.txt"
            with open(prompt_path, 'r') as f:
                system_prompt_template = f.read()
        except Exception as e:
            self.logger.error(f"Could not load prompt file: {e}")
            system_prompt_template = """You are a world-class Full-Stack Website Builder Agent.

YOUR CORE DIRECTIVE:
Translate a business concept into a complete, production-ready, and containerized web application.

AVAILABLE INTELLIGENCE:
[Retrieved Web Development Best Practices]
{development_context}

YOUR CURRENT MISSION:
Task: {task}

INSTRUCTIONS:
1. Deconstruct the Task: Break down the business requirement into core components
2. Design the Architecture: Define the technology stack
3. Generate Backend Code: Write server-side code with API endpoints
4. Generate Frontend Code: Write client-side code with UI components
5. Generate Deployment Scripts: Create Dockerfile and deployment configuration
6. Structure the Output: Format response with clear file markers
7. Return the complete set of code files as your final output"""

        full_prompt = system_prompt_template.format(
            skills=', '.join(self.config.get('skills', [])),
            development_context=dev_context or "No specific context found.",
            previous_context=json.dumps(self.get_state('context_memory', {}), indent=2),
            additional_context=json.dumps(context, indent=2) if context else "None",
            task=prompt
        )
        return full_prompt

    def _process_response(self, response: str) -> dict:
        """Processes the LLM response into a structured set of code files."""
        self.logger.info("Processing full-stack code generation response.")
        
        files_created = self._extract_and_write_code_files(response)
        
        result = {
            'agent_type': 'WebsiteBuilder',
            'task_id': f"website_build_{self.task_count}",
            'timestamp': self.last_activity.isoformat(),
            'summary': f"Generated {len(files_created)} files for the web application.",
            'files_created': files_created,
            'full_response': response,
            'project_structure': self._analyze_project_structure(files_created),
            'deployment_ready': self._check_deployment_readiness(files_created)
        }
        
        self._update_project_memory(result)
        
        # Generate project documentation
        self._generate_project_docs(result)
        
        return result

    def _extract_and_write_code_files(self, response: str) -> list:
        """Extracts code blocks from the response and writes them to files."""
        file_tool = self.get_tool("file_write")
        if not file_tool:
            self.logger.warning("File write tool not available. Cannot save generated code.")
            return []

        # Parse file markers from response (e.g., --- FILE: backend/main.py ---)
        file_pattern = r'---\s*FILE:\s*([^\s]+)\s*---\n(.*?)(?=---\s*FILE:|$)'
        matches = re.findall(file_pattern, response, re.DOTALL)
        
        output_dir = f"data/agent_outputs/website_{self.task_count}/"
        created_paths = []

        if matches:
            # Use parsed files from response
            for file_path, content in matches:
                full_path = f"{output_dir}{file_path.strip()}"
                save_result = file_tool(path=full_path, content=content.strip())
                if save_result.get("success"):
                    created_paths.append(full_path)
        else:
            # Fallback: Generate standard full-stack structure
            files_to_create = self._generate_default_fullstack_app()
            
            for file_path, content in files_to_create.items():
                full_path = f"{output_dir}{file_path}"
                save_result = file_tool(path=full_path, content=content)
                if save_result.get("success"):
                    created_paths.append(full_path)
        
        self.logger.info(f"Created {len(created_paths)} files in {output_dir}")
        return created_paths

    def _generate_default_fullstack_app(self) -> dict:
        """Generate a default full-stack application structure"""
        return {
            "backend/main.py": """from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="Enterprise Web App", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    id: int
    name: str
    description: str

# In-memory storage (replace with database in production)
items_db = []

@app.get("/")
def read_root():
    return {"message": "Enterprise Web App API", "status": "online"}

@app.get("/api/items", response_model=List[Item])
def get_items():
    return items_db

@app.post("/api/items", response_model=Item)
def create_item(item: Item):
    items_db.append(item)
    return item

@app.get("/api/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
""",
            "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Web App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-center mb-8">Enterprise Web App</h1>
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold mb-4">Items Management</h2>
            <div id="items-list" class="space-y-2"></div>
            <div class="mt-6">
                <input type="text" id="item-name" placeholder="Item name" class="border p-2 mr-2">
                <input type="text" id="item-desc" placeholder="Description" class="border p-2 mr-2">
                <button onclick="addItem()" class="bg-blue-500 text-white px-4 py-2 rounded">Add Item</button>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:8000/api';
        
        async function loadItems() {
            try {
                const response = await axios.get(`${API_BASE}/items`);
                const itemsList = document.getElementById('items-list');
                itemsList.innerHTML = response.data.map(item => 
                    `<div class="border p-3 rounded">
                        <h3 class="font-semibold">${item.name}</h3>
                        <p class="text-gray-600">${item.description}</p>
                    </div>`
                ).join('');
            } catch (error) {
                console.error('Error loading items:', error);
            }
        }
        
        async function addItem() {
            const name = document.getElementById('item-name').value;
            const description = document.getElementById('item-desc').value;
            
            if (!name || !description) return;
            
            try {
                await axios.post(`${API_BASE}/items`, {
                    id: Date.now(),
                    name: name,
                    description: description
                });
                document.getElementById('item-name').value = '';
                document.getElementById('item-desc').value = '';
                loadItems();
            } catch (error) {
                console.error('Error adding item:', error);
            }
        }
        
        // Load items on page load
        loadItems();
    </script>
</body>
</html>
""",
            "backend/requirements.txt": """fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
""",
            "Dockerfile": """FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "backend/main.py"]
""",
            "docker-compose.yml": """version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    volumes:
      - ./frontend:/app/frontend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
    restart: unless-stopped
""",
            "nginx.conf": """events {
    worker_connections 1024;
}

http {
    upstream backend {
        server web:8000;
    }

    server {
        listen 80;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }
        
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
""",
            "README.md": """# Enterprise Web Application

Generated by WebsiteBuilder Agent (Architecture 3.0)

## Features
- FastAPI backend with REST API
- Responsive frontend with Tailwind CSS
- Docker containerization
- Nginx reverse proxy
- Production-ready configuration

## Quick Start

### Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
# Open index.html in browser or serve with local server
```

### Production (Docker)
```bash
docker-compose up -d
```

Access the application at http://localhost

## API Endpoints
- GET / - Health check
- GET /api/items - List all items
- POST /api/items - Create new item
- GET /api/items/{id} - Get specific item

## Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS
- **Deployment**: Docker + Docker Compose + Nginx
- **API**: RESTful design with OpenAPI documentation
"""
        }

    def _analyze_project_structure(self, files: list) -> dict:
        """Analyze the generated project structure"""
        structure = {
            'backend_files': [],
            'frontend_files': [],
            'config_files': [],
            'documentation': []
        }
        
        for file_path in files:
            if 'backend/' in file_path:
                structure['backend_files'].append(file_path)
            elif 'frontend/' in file_path:
                structure['frontend_files'].append(file_path)
            elif any(ext in file_path for ext in ['.yml', '.yaml', '.conf', 'Dockerfile']):
                structure['config_files'].append(file_path)
            elif '.md' in file_path:
                structure['documentation'].append(file_path)
        
        return structure

    def _check_deployment_readiness(self, files: list) -> bool:
        """Check if the project is ready for deployment"""
        required_files = ['Dockerfile', 'requirements.txt']
        file_names = [Path(f).name for f in files]
        return all(req in ' '.join(file_names) for req in required_files)

    def _generate_project_docs(self, result: dict):
        """Generate comprehensive project documentation"""
        file_tool = self.get_tool("file_write")
        if not file_tool:
            return

        project_summary = f"""# Website Build Summary

**Project ID**: {result['task_id']}
**Generated**: {result['timestamp']}
**Agent**: WebsiteBuilder (Architecture 3.0)

## Project Statistics
- **Files Created**: {len(result['files_created'])}
- **Backend Files**: {len(result['project_structure']['backend_files'])}
- **Frontend Files**: {len(result['project_structure']['frontend_files'])}
- **Config Files**: {len(result['project_structure']['config_files'])}
- **Deployment Ready**: {'Yes' if result['deployment_ready'] else 'No'}

## Generated Files
{chr(10).join(f"- {file}" for file in result['files_created'])}

## Next Steps
1. Review generated code
2. Customize business logic
3. Test locally: `docker-compose up`
4. Deploy to production environment

---
*Generated by WebsiteBuilder Agent - Architecture 3.0*
"""
        
        summary_path = f"data/agent_outputs/website_{self.task_count}/PROJECT_SUMMARY.md"
        file_tool(path=summary_path, content=project_summary)

    def _update_project_memory(self, result: dict):
        """Updates agent's state with details of the build."""
        builds = self.get_state('completed_builds', [])
        builds.append({
            'task_id': result['task_id'],
            'timestamp': result['timestamp'],
            'file_count': len(result.get('files_created', [])),
            'deployment_ready': result['deployment_ready']
        })
        
        # Keep last 10 builds
        if len(builds) > 10:
            builds = builds[-10:]
            
        self.update_state('completed_builds', builds)
        self.update_state('total_websites_built', len(builds))
        
        # Update context memory
        context_memory = {
            'last_build_type': 'fullstack_web_app',
            'recent_tech_stack': ['FastAPI', 'HTML/CSS/JS', 'Docker'],
            'deployment_patterns': ['docker-compose', 'nginx_proxy']
        }
        self.update_state('context_memory', context_memory)
        
        self.logger.info(f"Website builder memory updated. Total builds: {len(builds)}")
