"""
Script to verify Pydantic v2 installation and functionality.
"""
import sys

try:
    import pydantic
    print("Pydantic version: {}".format(pydantic.__version__))
    
    major_version = int(pydantic.__version__.split(".")[0])
    if major_version >= 2:
        print("Pydantic v2+ detected")
        
        # Test Pydantic v2 functionality
        from pydantic import BaseModel, Field
        
        class TestModel(BaseModel):
            name: str = Field(..., min_length=2)
            age: int = Field(..., gt=0)
        
        test = TestModel(name="Test", age=30)
        print("Model validation works: {}".format(test))
        sys.exit(0)
    else:
        print("Pydantic v1 detected - needs upgrade")
        sys.exit(1)
except ImportError:
    print("Pydantic not installed")
    sys.exit(1)
except Exception as e:
    print("Error: {}".format(str(e)))
    sys.exit(1)
