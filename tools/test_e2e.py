#!/usr/bin/env python
"""
End-to-end tests for Empire multi-agent system
"""
import os
import sys
import argparse
import logging
import json
import time
import asyncio
from typing import Dict, Any, List, Optional
import httpx

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.core import empire
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("e2e-tests")

class TestSuite:
    """Test suite for end-to-end testing of the Empire system"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results = {}
        self.client = None
    
    async def setup(self):
        """Set up the test environment"""
        self.client = httpx.AsyncClient(base_url=self.api_url, timeout=60.0)
    
    async def teardown(self):
        """Clean up the test environment"""
        if self.client:
            await self.client.aclose()
    
    async def run_api_test(self, name: str, method: str, endpoint: str, data: Optional[Dict] = None, 
                           expected_status: int = 200) -> bool:
        """Run a test against a specific API endpoint"""
        logger.info(f"Running API test: {name}")
        
        try:
            if method.lower() == "get":
                response = await self.client.get(endpoint)
            elif method.lower() == "post":
                response = await self.client.post(endpoint, json=data)
            elif method.lower() == "put":
                response = await self.client.put(endpoint, json=data)
            elif method.lower() == "delete":
                response = await self.client.delete(endpoint)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return False
            
            logger.info(f"Response status: {response.status_code}")
            
            # Check status code
            if response.status_code != expected_status:
                logger.error(f"Expected status {expected_status}, got {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
            
            # Try to parse response as JSON
            try:
                response_data = response.json()
                logger.info(f"Response data: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                logger.info(f"Response text: {response.text}")
            
            return True
        except Exception as e:
            logger.error(f"Error in API test {name}: {str(e)}")
            return False
    
    async def test_website_creation(self) -> bool:
        """Test the complete website creation flow"""
        logger.info("Testing website creation flow")
        
        # 1. First discover a niche
        niche_data = {
            "niche": "healthy recipes",
            "keywords": ["vegan recipes", "gluten-free meals", "low-carb dinners"],
            "target_audience": "health-conscious home cooks",
            "budget": 500.0,
            "duration": 30
        }
        
        niche_success = await self.run_api_test(
            "Niche Discovery",
            "post",
            "/niche/discover",
            data=niche_data
        )
        
        if not niche_success:
            return False
        
        # 2. Create a website based on the niche
        website_data = {
            "domain": "healthyrecipesfinder.com",
            "content": "A website for discovering healthy, easy-to-make recipes for various dietary needs.",
            "design": "Clean, modern design with food imagery",
            "budget": 800.0,
            "deadline": "2025-05-15"
        }
        
        website_success = await self.run_api_test(
            "Website Creation",
            "post",
            "/website/create",
            data=website_data
        )
        
        if not website_success:
            return False
        
        # 3. View the created website
        view_success = await self.run_api_test(
            "Website View",
            "get",
            f"/website/view?domain={website_data['domain']}"
        )
        
        return view_success
    
    async def test_llm_switching(self) -> bool:
        """Test LLM provider switching"""
        # Switch to OpenRouter
        openrouter_success = await self.run_api_test(
            "Switch to OpenRouter",
            "post",
            "/llm/switch-provider",
            data={"provider": "openrouter"}
        )
        
        if not openrouter_success:
            return False
        
        # Switch to Gemini
        gemini_success = await self.run_api_test(
            "Switch to Gemini",
            "post",
            "/llm/switch-provider",
            data={"provider": "gemini"}
        )
        
        return gemini_success
    
    async def test_analytics(self) -> bool:
        """Test analytics endpoints"""
        # Test website analytics
        analytics_success = await self.run_api_test(
            "Website Analytics",
            "get",
            "/analytics/website?website_id=healthyrecipesfinder.com"
        )
        
        if not analytics_success:
            return False
        
        # Test monetization analytics
        monetization_success = await self.run_api_test(
            "Website Monetization",
            "get",
            "/analytics/monetization?website_id=healthyrecipesfinder.com"
        )
        
        return monetization_success
    
    async def test_agent_communication(self) -> bool:
        """Test communication between agents using the core framework"""
        logger.info("Testing agent communication")
        
        try:
            # Set up test agents
            from app.core.agent import Agent
            
            # Create two test agents
            agent1 = Agent(name="TestAgent1")
            agent2 = Agent(name="TestAgent2")
            
            # Register with Empire
            empire.register_agent(agent1)
            empire.register_agent(agent2)
            
            # Send a message from agent1 to agent2
            message_content = {"test": "Hello from agent1"}
            message_id = empire.message_bus.send_message(
                sender_id=agent1.agent_id,
                recipient_id=agent2.agent_id,
                content=message_content
            )
            
            # Check if message was received
            messages = empire.message_bus.get_messages_for_agent(agent2.agent_id)
            
            if not messages or len(messages) == 0:
                logger.error("No messages received")
                return False
            
            received_message = messages[0]
            logger.info(f"Message received: {received_message}")
            
            if received_message["sender_id"] != agent1.agent_id:
                logger.error(f"Expected sender {agent1.agent_id}, got {received_message['sender_id']}")
                return False
            
            if received_message["content"] != message_content:
                logger.error(f"Message content doesn't match. Expected {message_content}, got {received_message['content']}")
                return False
            
            logger.info("Agent communication test passed")
            return True
        except Exception as e:
            logger.error(f"Error in agent communication test: {str(e)}")
            return False
    
    async def test_workflow_orchestration(self) -> bool:
        """Test the workflow orchestration system"""
        logger.info("Testing workflow orchestration")
        
        try:
            # Create a simple test workflow
            workflow = empire.orchestrator.create_workflow(
                name="test_workflow",
                description="Test workflow for end-to-end testing"
            )
            
            # Add steps to the workflow
            workflow.add_step(
                name="step1",
                description="First step",
                agent_type="WebsiteAgent",
                action="analyze_website",
                parameters={"url": "https://example.com"}
            )
            
            workflow.add_step(
                name="step2",
                description="Second step",
                agent_type="SEOAgent",
                action="optimize_website",
                parameters={"domain": "example.com"},
                depends_on=["step1"]
            )
            
            # Run the workflow (don't actually execute)
            plan = workflow.create_execution_plan()
            
            logger.info(f"Workflow execution plan created with {len(plan)} steps")
            for step in plan:
                logger.info(f"Step: {step['name']} - Agent: {step['agent_type']}")
            
            return len(plan) == 2  # Verify that both steps are in the plan
        except Exception as e:
            logger.error(f"Error in workflow orchestration test: {str(e)}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        await self.setup()
        
        try:
            self.results = {
                "website_creation": await self.test_website_creation(),
                "llm_switching": await self.test_llm_switching(),
                "analytics": await self.test_analytics(),
                "agent_communication": await self.test_agent_communication(),
                "workflow_orchestration": await self.test_workflow_orchestration()
            }
        finally:
            await self.teardown()
        
        # Print summary
        logger.info("\n=== End-to-End Test Results ===")
        all_passed = True
        for test_name, passed in self.results.items():
            logger.info(f"{test_name}: {'PASSED' if passed else 'FAILED'}")
            all_passed = all_passed and passed
        
        logger.info(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
        
        return self.results

async def main():
    """Main entry point for the test script"""
    parser = argparse.ArgumentParser(description="End-to-end tests for Empire system")
    parser.add_argument('--api-url', default="http://localhost:8000", help="URL of the FastAPI server")
    parser.add_argument('--test', choices=['all', 'website', 'llm', 'analytics', 'agent', 'workflow'],
                      default='all', help="Which test to run (default: all)")
    
    args = parser.parse_args()
    
    test_suite = TestSuite(api_url=args.api_url)
    
    try:
        if args.test == 'all':
            await test_suite.run_all_tests()
        elif args.test == 'website':
            result = await test_suite.test_website_creation()
            logger.info(f"Website Creation Test: {'PASSED' if result else 'FAILED'}")
        elif args.test == 'llm':
            result = await test_suite.test_llm_switching()
            logger.info(f"LLM Switching Test: {'PASSED' if result else 'FAILED'}")
        elif args.test == 'analytics':
            result = await test_suite.test_analytics()
            logger.info(f"Analytics Test: {'PASSED' if result else 'FAILED'}")
        elif args.test == 'agent':
            result = await test_suite.test_agent_communication()
            logger.info(f"Agent Communication Test: {'PASSED' if result else 'FAILED'}")
        elif args.test == 'workflow':
            result = await test_suite.test_workflow_orchestration()
            logger.info(f"Workflow Orchestration Test: {'PASSED' if result else 'FAILED'}")
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
