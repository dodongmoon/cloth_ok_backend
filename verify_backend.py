import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    from main import app
    print("Backend verification successful: app imported correctly.")
except Exception as e:
    print(f"Backend verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
