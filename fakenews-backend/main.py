"""
Entry point — run with:

    python main.py            ← development (auto-reload)
    uvicorn app.main:app      ← production (Render / Railway)
"""

import uvicorn
from app.config import get_config

config = get_config()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        log_level=config.LOG_LEVEL.lower(),
    )
