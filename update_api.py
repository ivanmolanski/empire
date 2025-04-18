"""
Script to update API and restart uvicorn server.
This script will:
1. Generate models using datamodel-code-generator
2. Check routes directory
3. Restart uvicorn server
"""
import subprocess
import os
import time

def update_api():
    print("🔹 Step 1: Generating models")
    try:
        result = subprocess.run(["python", "generate_models.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Models generated successfully!")
        else:
            print(f"Error generating models: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to generate models: {str(e)}")
        return False
    
    print("\n🔹 Step 2: Checking routes")
    routes_dir = "app/routes"
    
    if os.path.exists(routes_dir):
        print(f"Routes directory found at {routes_dir}")
    else:
        print(f"Routes directory not found at {routes_dir}")
        return False
    
    print("\n✅ API updated successfully!")
    return True

def restart_uvicorn():
    print("\n🔄 Restarting uvicorn server...")
    try:
        # Check if uvicorn is running
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        if "uvicorn" in result.stdout:
            print("📡 Stopping existing uvicorn process...")
            subprocess.run(["pkill", "-f", "uvicorn"])
            time.sleep(2)  # Give it time to shut down
        
        # Start uvicorn in the background
        print("📡 Starting uvicorn...")
        subprocess.Popen(["uvicorn", "app.main:app", "--reload"], 
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        print("Uvicorn server started!")
        return True
    except Exception as e:
        print(f"❌ Failed to restart uvicorn: {str(e)}")
        return False

if __name__ == "__main__":
    if update_api():
        restart_uvicorn()
