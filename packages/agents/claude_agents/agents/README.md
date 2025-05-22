# Claude Agents Architecture

## Overview
This directory contains the canonical implementation of agent classes for MindMeld v1.1.

## Agent Classes

- `base.py` - Base Agent class that all other agents inherit from
- `planner.py` - PlannerAgent for breaking down tasks into steps
- `executor.py` - ExecutorAgent for executing individual tasks
- `critic.py` - CriticAgent for evaluating outputs and providing feedback

## Implementation Notes

- All agents should follow the interfaces defined in the base Agent class
- Agents use the ClaudeAPIClient for LLM interactions

## Missing Vector Memory Components

**Critical Component Missing:** Vector memory agents from `/Users/cpconnor/projects/mindmeld-v1.1/src/agents/memory/` should be migrated here to provide:
- Semantic similarity search
- Memory persistence 
- Context-aware retrieval

**Migration Required:** The `VectorMemoryAgent` and `OptimizedVectorMemoryAgent` classes should be migrated to this directory.