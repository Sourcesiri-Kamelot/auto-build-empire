#!/usr/bin/env python3
"""
Code Analysis Tools for Agent Architecture 3.0
Enterprise-grade code linting, formatting, and analysis capabilities.
"""
import ast
import re
from typing import Dict, Any, List
from ..core.tool_registry import tool

@tool("code_lint", "Analyze and lint code for quality and standards")
def lint_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code for quality, style, and potential issues.
    """
    try:
        issues = []
        metrics = {}
        
        if language.lower() == "python":
            # Basic Python analysis
            try:
                tree = ast.parse(code)
                metrics["ast_nodes"] = len(list(ast.walk(tree)))
                metrics["functions"] = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                metrics["classes"] = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "message": str(e),
                    "line": e.lineno,
                    "severity": "error"
                })
            
            # Style checks
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if len(line) > 100:
                    issues.append({
                        "type": "line_length",
                        "message": f"Line too long ({len(line)} > 100 characters)",
                        "line": i,
                        "severity": "warning"
                    })
                
                if line.strip().endswith('  '):
                    issues.append({
                        "type": "trailing_whitespace",
                        "message": "Trailing whitespace",
                        "line": i,
                        "severity": "info"
                    })
        
        metrics["lines_of_code"] = len([l for l in code.split('\n') if l.strip()])
        metrics["total_lines"] = len(code.split('\n'))
        
        return {
            "success": True,
            "language": language,
            "issues": issues,
            "metrics": metrics,
            "quality_score": max(0, 100 - len(issues) * 5)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool("code_format", "Format code according to enterprise standards")
def format_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Format code according to enterprise coding standards.
    """
    try:
        formatted_code = code
        changes = []
        
        if language.lower() == "python":
            # Basic formatting improvements
            lines = code.split('\n')
            formatted_lines = []
            
            for line in lines:
                # Remove trailing whitespace
                original_line = line
                line = line.rstrip()
                if original_line != line:
                    changes.append("Removed trailing whitespace")
                
                formatted_lines.append(line)
            
            formatted_code = '\n'.join(formatted_lines)
        
        return {
            "success": True,
            "language": language,
            "original_code": code,
            "formatted_code": formatted_code,
            "changes": changes,
            "improved": len(changes) > 0
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool("code_complexity", "Analyze code complexity metrics")
def analyze_complexity(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code complexity using various metrics.
    """
    try:
        complexity = {
            "cyclomatic_complexity": 1,  # Base complexity
            "cognitive_complexity": 0,
            "maintainability_index": 100
        }
        
        if language.lower() == "python":
            # Count control flow statements
            control_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with']
            for keyword in control_keywords:
                complexity["cyclomatic_complexity"] += code.count(f'{keyword} ')
                complexity["cognitive_complexity"] += code.count(f'{keyword} ')
            
            # Adjust maintainability based on complexity
            complexity["maintainability_index"] = max(0, 100 - complexity["cyclomatic_complexity"] * 5)
        
        return {
            "success": True,
            "language": language,
            "complexity": complexity,
            "recommendations": [
                "Consider breaking down complex functions" if complexity["cyclomatic_complexity"] > 10 else "Complexity is acceptable",
                "Add more comments for clarity" if complexity["cognitive_complexity"] > 15 else "Code clarity is good"
            ]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
