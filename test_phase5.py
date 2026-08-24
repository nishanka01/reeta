"""
==================================================
REETA — test_phase5.py
==================================================
PURPOSE:
    Simulates sending a request through the Multi-Agent
    LangGraph orchestration to verify routing and execution.
==================================================
"""

import asyncio
from orchestration.task_manager import task_manager

async def run_tests():
    print("==================================================")
    print("TEST 1: Research Workflow")
    print("==================================================")
    await task_manager.execute_task("Research the latest AI agents")

    print("\n==================================================")
    print("TEST 2: Coding Workflow")
    print("==================================================")
    await task_manager.execute_task("Write a python script to sort files")

    print("\n==================================================")
    print("TEST 3: Security Workflow")
    print("==================================================")
    await task_manager.execute_task("Is this URL safe? http://suspicious.com")

if __name__ == "__main__":
    asyncio.run(run_tests())
