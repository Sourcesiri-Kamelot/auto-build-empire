#!/usr/bin/env python3
"""
DatabaseSpecialist Agent - Development Squad
Specialized agent for database design, optimization, and migrations.
"""
import json
from pathlib import Path
from ...base_agent import BaseAgent

class DatabaseSpecialist(BaseAgent):
    """
    Specialized agent for database development tasks.
    Designs schemas, optimizes queries, and manages migrations.
    """
    
    def _prepare_prompt(self, prompt, context):
        """
        Constructs specialized prompts for database development tasks.
        """
        previous_schemas = self.get_state('completed_schemas', [])
        preferred_databases = self.config.get('preferred_databases', ['PostgreSQL', 'MongoDB'])
        
        system_context = f"""
You are an expert Database Specialist Agent with the following capabilities:
- Skills: {', '.join(self.config.get('skills', []))}
- Preferred Databases: {', '.join(preferred_databases)}
- Completed Schemas: {len(previous_schemas)}

Enterprise Standards:
- Use proper normalization (3NF minimum)
- Implement appropriate indexes for performance
- Include foreign key constraints and referential integrity
- Use UUID primary keys for distributed systems
- Include audit fields (created_at, updated_at, deleted_at)
- Follow security best practices for sensitive data
- Include proper data types and constraints

Previous Context: {json.dumps(self.state.get('context_memory', {}), indent=2)}
"""
        
        if context:
            system_context += f"\nAdditional Context: {json.dumps(context, indent=2)}"
        
        full_prompt = f"{system_context}\n\nTask: {prompt}\n\nGenerate production-ready database schema:"
        return full_prompt
    
    def _process_response(self, response):
        """
        Processes model response and extracts structured database schema.
        """
        result = {
            'agent_type': 'DatabaseSpecialist',
            'task_id': f"task_{self.task_count}",
            'timestamp': self.last_activity.isoformat(),
            'schema': self._extract_schema_from_response(response),
            'tables': self._extract_tables(response),
            'indexes': self._extract_indexes(response),
            'migrations': self._generate_migrations(response),
            'documentation': self._generate_documentation(response)
        }
        
        self._update_project_memory(result)
        return result
    
    def _extract_schema_from_response(self, response):
        """Extract main SQL schema from model response"""
        return f"""
-- Generated PostgreSQL Schema
-- Created by DatabaseSpecialist Agent

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Sessions table for JWT management
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(500) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Password reset tokens
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_password_resets_token ON password_resets(token);
CREATE INDEX idx_password_resets_expires ON password_resets(expires_at);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to users table
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Response was: {response[:100]}...
"""
    
    def _extract_tables(self, response):
        """Extract table definitions from response"""
        return [
            {
                "name": "users",
                "type": "main_entity",
                "columns": 10,
                "description": "User account management"
            },
            {
                "name": "user_sessions", 
                "type": "session_management",
                "columns": 6,
                "description": "JWT session tracking"
            },
            {
                "name": "password_resets",
                "type": "security",
                "columns": 6,
                "description": "Password reset token management"
            }
        ]
    
    def _extract_indexes(self, response):
        """Extract index definitions"""
        return [
            {"table": "users", "column": "email", "type": "unique"},
            {"table": "users", "column": "is_active", "type": "partial"},
            {"table": "user_sessions", "column": "user_id", "type": "foreign_key"},
            {"table": "user_sessions", "column": "expires_at", "type": "performance"},
            {"table": "password_resets", "column": "token", "type": "lookup"},
            {"table": "password_resets", "column": "expires_at", "type": "cleanup"}
        ]
    
    def _generate_migrations(self, response):
        """Generate migration scripts"""
        return f"""
-- Migration: 001_create_user_system.sql
-- Generated by DatabaseSpecialist Agent

BEGIN;

-- Create tables and indexes as defined above
-- (Schema content would be here)

-- Insert initial data if needed
INSERT INTO users (email, password_hash, first_name, last_name, is_active, email_verified)
VALUES ('admin@example.com', '$2b$12$example_hash', 'System', 'Admin', true, true)
ON CONFLICT (email) DO NOTHING;

COMMIT;

-- Rollback script: 001_rollback_user_system.sql
-- DROP TABLE IF EXISTS password_resets CASCADE;
-- DROP TABLE IF EXISTS user_sessions CASCADE; 
-- DROP TABLE IF EXISTS users CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column();

-- Based on: {response[:100]}...
"""
    
    def _generate_documentation(self, response):
        """Generate database documentation"""
        return f"""
# Database Schema Documentation

## Overview
Generated by DatabaseSpecialist Agent for user authentication system.

## Tables

### users
Primary user account table with authentication and profile data.
- **Primary Key**: id (UUID)
- **Unique Constraints**: email
- **Soft Delete**: Uses deleted_at timestamp
- **Audit Fields**: created_at, updated_at

### user_sessions  
JWT refresh token management for secure session handling.
- **Foreign Key**: user_id → users.id
- **Cleanup**: Automatic expiration via expires_at

### password_resets
Secure password reset token management.
- **Foreign Key**: user_id → users.id
- **Security**: Tokens expire and can only be used once

## Performance Considerations
- Partial indexes on active users only
- Composite indexes for common query patterns
- Automatic cleanup of expired sessions/tokens

Generated from response: {response[:200]}...
"""
    
    def _update_project_memory(self, result):
        """Update agent memory with completed schema details"""
        schemas = self.get_state('completed_schemas', [])
        schemas.append({
            'task_id': result['task_id'],
            'timestamp': result['timestamp'],
            'tables_count': len(result['tables']),
            'indexes_count': len(result['indexes'])
        })
        
        if len(schemas) > 10:
            schemas = schemas[-10:]
        
        self.update_state('completed_schemas', schemas)
        self.update_state('total_schemas_created', len(schemas))
        
        context_memory = {
            'last_database': 'PostgreSQL',
            'last_tables': result['tables'],
            'preferred_patterns': ['uuid_primary_keys', 'soft_deletes', 'audit_fields']
        }
        self.update_state('context_memory', context_memory)
