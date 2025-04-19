#!/usr/bin/env python
"""
Test script for LLM provider switching functionality
"""
import os
import sys
import argparse
import logging
import json
import time
from typing import Dict, Any
import httpx
import asyncio

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.services.llm_agent import llm_switch_agent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("llm-switch-test")

async def test_switch_via_api(api_url: str = "http://localhost:8000") -> bool:
    """Test LLM provider switching via the API endpoint"""
    logger.info("Testing LLM switching via API endpoint")
    
    async with httpx.AsyncClient(base_url=api_url, timeout=30.0) as client:
        # Test switching to OpenRouter
        try:
            response = await client.post("/llm/switch-provider", json={"provider": "openrouter"})
            logger.info(f"OpenRouter switch response: {response.status_code} - {response.text}")
            if response.status_code != 200:
                logger.error(f"Failed to switch to OpenRouter: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error switching to OpenRouter: {str(e)}")
            return False
            
        # Wait a moment for the switch to take effect
        await asyncio.sleep(2)
        
        # Test switching to Gemini
        try:
            response = await client.post("/llm/switch-provider", json={"provider": "gemini"})
            logger.info(f"Gemini switch response: {response.status_code} - {response.text}")
            if response.status_code != 200:
                logger.error(f"Failed to switch to Gemini: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error switching to Gemini: {str(e)}")
            return False
            
    logger.info("API provider switching test passed")
    return True

async def test_direct_llm_agent() -> bool:
    """Test switching via direct calls to the LLM agent"""
    logger.info("Testing direct LLM agent switching")
    
    try:
        # Test with a simple prompt to verify the LLM is working
        test_prompt = "Write a one-sentence description of a website that helps users find healthy recipes."
        
        # Test with OpenRouter
        logger.info("Testing with OpenRouter...")
        result = await llm_switch_agent.generate_content(test_prompt, provider="openrouter")
        logger.info(f"OpenRouter result: {result[:100]}..." if len(result) > 100 else result)
        
        # Test with Gemini
        logger.info("Testing with Gemini...")
        result = await llm_switch_agent.generate_content(test_prompt, provider="gemini")
        logger.info(f"Gemini result: {result[:100]}..." if len(result) > 100 else result)
        
        logger.info("Direct LLM agent test passed")
        return True
    except Exception as e:
        logger.error(f"Error in direct LLM agent test: {str(e)}")
        return False

async def test_environment_variables() -> bool:
    """Test that environment variables are correctly loaded"""
    logger.info("Testing environment variables...")
    
    # Check that the required environment variables are set
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    openrouter_model = os.getenv("OPENROUTER_MODEL")
    gemini_model = os.getenv("FALLBACK_LLM_MODEL", "gemini-2.0-flash-thinking-exp-01-21")
    
    if not openrouter_key:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        return False
    
    if not gemini_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        return False
        
    if not openrouter_model:
        logger.warning("OPENROUTER_MODEL environment variable not set, using default")
    
    if gemini_model != "gemini-2.0-flash-thinking-exp-01-21":
        logger.warning(f"FALLBACK_LLM_MODEL has unexpected value: {gemini_model}")
        logger.warning("Expected: gemini-2.0-flash-thinking-exp-01-21")
    
    logger.info(f"OpenRouter model: {openrouter_model if openrouter_model else 'Not set'}")
    logger.info(f"Gemini model: {gemini_model}")
    
    logger.info("Environment variables test passed")
    return True

async def run_tests():
    """Run all LLM provider switching tests"""
    results = {}
    
    # Test environment variables
    results["environment_variables"] = await test_environment_variables()
    
    # Test switching via the API
    results["api_switching"] = await test_switch_via_api()
    
    # Test direct LLM agent
    results["direct_agent"] = await test_direct_llm_agent()
    
    # Print summary
    logger.info("\n=== Test Results Summary ===")
    all_passed = True
    for test_name, passed in results.items():
        logger.info(f"{test_name}: {'PASSED' if passed else 'FAILED'}")
        all_passed = all_passed and passed
    
    logger.info(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed

def main():
    """Main entry point for the test script"""
    parser = argparse.ArgumentParser(description="Test LLM provider switching functionality")
    parser.add_argument('--api-url', default="http://localhost:8000", help="URL of the FastAPI server")
    
    args = parser.parse_args()
    
    try:
        success = asyncio.run(run_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Tests cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
