from api import app
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Read configuration from .env file
    host = os.getenv("HOST", "127.0.0.1")  # Default to 127.0.0.1 if HOST is not set
    port = int(os.getenv("PORT", 8000))    # Default to 8000 if PORT is not set

    # Run FastAPI app on the specified host and port
    uvicorn.run(app, host=host, port=port, reload=False)



