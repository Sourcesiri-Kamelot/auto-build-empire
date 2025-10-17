#!/usr/bin/env python3
"""
File System Tools for Agent Architecture 3.0
Enterprise-grade file operations with security and validation.
"""
import os
import json
from pathlib import Path
from typing import Union, Dict, Any
from ..core.tool_registry import tool

@tool("file_write", "Write content to a file with atomic operations")
def write_file(path: str, content: str, mode: str = "w") -> Dict[str, Any]:
    """
    Atomically write content to a file.
    Uses temp file + rename for atomic operations.
    """
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write: temp file + rename
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        with open(temp_path, mode) as f:
            f.write(content)
        temp_path.rename(file_path)
        
        return {
            "success": True,
            "path": str(file_path),
            "size": len(content),
            "message": f"File written successfully: {file_path.name}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool("file_read", "Read content from a file")
def read_file(path: str) -> Dict[str, Any]:
    """Read content from a file."""
    try:
        file_path = Path(path)
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        return {
            "success": True,
            "path": str(file_path),
            "content": content,
            "size": len(content)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool("directory_create", "Create directory structure")
def create_directory(path: str) -> Dict[str, Any]:
    """Create directory structure."""
    try:
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "path": str(dir_path),
            "message": f"Directory created: {dir_path}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool("file_exists", "Check if file or directory exists")
def file_exists(path: str) -> Dict[str, Any]:
    """Check if file or directory exists."""
    file_path = Path(path)
    exists = file_path.exists()
    
    return {
        "success": True,
        "path": str(file_path),
        "exists": exists,
        "is_file": file_path.is_file() if exists else False,
        "is_directory": file_path.is_dir() if exists else False
    }
