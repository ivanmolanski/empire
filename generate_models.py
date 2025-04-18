"""
Script to generate Pydantic v2 models from OpenAPI schema.
Run this after updating your OpenAPI schema to regenerate models.
"""
import subprocess
import os
from datetime import datetime

def generate_models():
    # Ensure the output directory exists
    os.makedirs("app", exist_ok=True)
    
    # Set the input and output paths
    input_path = "openapi.yaml"
    output_path = "models.py"  # Generate to top-level models.py
    app_output_path = "app/models.py"  # Also generate to app/models.py for flexibility
    
    # Command to generate Pydantic v2 models
    command = [
        "datamodel-codegen",
        "--input", input_path,
        "--output", output_path,
        "--target-python-version", "3.9",
        "--use-schema-description",
        "--field-constraints",
        "--use-standard-collections",
        "--output-model-type", "pydantic_v2.BaseModel"  # This is key for generating Pydantic v2 models
    ]
    
    # Execute the command
    print("Generating Pydantic v2 models from {}...".format(input_path))
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Models successfully generated at {}".format(output_path))
        
        # Also save to app directory
        with open(output_path, 'r') as f:
            content = f.read()
        
        with open(app_output_path, 'w') as f:
            f.write(content)
        
        print("Models also copied to {}".format(app_output_path))
        return True
    else:
        print("Error generating models: {}".format(result.stderr))
        return False

if __name__ == "__main__":
    generate_models()
