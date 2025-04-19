"""
Version compatibility checks for external dependencies like Google ADK
"""
import importlib
import logging
import sys
from typing import Dict, Tuple, List, Optional
import pkg_resources

logger = logging.getLogger(__name__)

# Define required versions of key dependencies
REQUIRED_VERSIONS = {
    "google-adk": "0.4.0",  # Minimum ADK version needed
    "fastapi": "0.103.0",
    "pydantic": "2.0.0",
    "mcp": "0.3.0",  # Model Context Protocol library
}

# Define specific ADK features our app depends on
ADK_REQUIRED_FEATURES = [
    ("google.adk.agents", "LlmAgent"),
    ("google.adk.tools.function_tool", "FunctionTool"),
    ("google.adk.tools.mcp_tool.conversion_utils", "adk_to_mcp_tool_type")
]

def check_package_version(package_name: str, min_version: str) -> Tuple[bool, str, Optional[str]]:
    """
    Check if a package meets the minimum version requirement.
    
    Args:
        package_name: Name of the package to check
        min_version: Minimum required version string
        
    Returns:
        Tuple of (is_compatible, installed_version, error_message)
    """
    try:
        installed_version = pkg_resources.get_distribution(package_name).version
        is_compatible = pkg_resources.parse_version(installed_version) >= pkg_resources.parse_version(min_version)
        error_msg = None if is_compatible else f"Requires at least {min_version}, found {installed_version}"
        return is_compatible, installed_version, error_msg
    except pkg_resources.DistributionNotFound:
        return False, None, f"Package {package_name} not found"
    except Exception as e:
        return False, None, f"Error checking {package_name} version: {str(e)}"

def check_module_feature(module_path: str, feature_name: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a specific feature (class, function) exists in a module.
    
    Args:
        module_path: Import path to the module
        feature_name: Name of the class or function to check for
        
    Returns:
        Tuple of (feature_exists, error_message)
    """
    try:
        module = importlib.import_module(module_path)
        feature_exists = hasattr(module, feature_name)
        error_msg = None if feature_exists else f"Feature {feature_name} not found in {module_path}"
        return feature_exists, error_msg
    except ImportError:
        return False, f"Module {module_path} not found"
    except Exception as e:
        return False, f"Error checking feature {feature_name} in {module_path}: {str(e)}"

def run_compatibility_check() -> Dict:
    """
    Run a full compatibility check of all required packages and features.
    
    Returns:
        Dictionary with check results including compatibility status and issues
    """
    results = {
        "is_compatible": True,
        "package_versions": {},
        "missing_features": [],
        "all_issues": []
    }
    
    # Check package versions
    for pkg_name, min_version in REQUIRED_VERSIONS.items():
        is_compatible, installed_version, error_msg = check_package_version(pkg_name, min_version)
        results["package_versions"][pkg_name] = {
            "required": min_version,
            "installed": installed_version,
            "compatible": is_compatible
        }
        
        if not is_compatible:
            results["is_compatible"] = False
            results["all_issues"].append(error_msg)
            
    # Check ADK features
    for module_path, feature_name in ADK_REQUIRED_FEATURES:
        feature_exists, error_msg = check_module_feature(module_path, feature_name)
        if not feature_exists:
            results["is_compatible"] = False
            results["missing_features"].append(f"{module_path}.{feature_name}")
            results["all_issues"].append(error_msg)
    
    # Log compatibility status
    if results["is_compatible"]:
        logger.info("All compatibility checks passed")
    else:
        logger.warning("Compatibility issues detected")
        for issue in results["all_issues"]:
            logger.warning(f"  - {issue}")
    
    return results

def verify_compatibility(exit_on_failure=False) -> bool:
    """
    Verify compatibility with required dependencies and features.
    
    Args:
        exit_on_failure: Whether to exit the application if compatibility check fails
    
    Returns:
        Boolean indicating whether the system is compatible
    """
    results = run_compatibility_check()
    
    if not results["is_compatible"] and exit_on_failure:
        logger.error("Incompatible environment detected. Exiting.")
        for issue in results["all_issues"]:
            logger.error(f"  - {issue}")
        sys.exit(1)
    
    return results["is_compatible"]

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run the check
    verify_compatibility(exit_on_failure=True)
    print("Environment compatibility check passed!")
