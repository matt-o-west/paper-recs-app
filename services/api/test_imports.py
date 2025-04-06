try:
    import fastapi
    print("FastAPI imported successfully!")
    print(f"FastAPI version: {fastapi.__version__}")
    print(f"FastAPI path: {fastapi.__file__}")
except ImportError as e:
    print(f"Failed to import FastAPI: {e}")