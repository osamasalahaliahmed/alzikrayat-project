from pathlib import Path

from dotenv import dotenv_values

projectFolder = Path(__file__).resolve().parent.parent
settings = dotenv_values(projectFolder / ".env", interpolate=False)
uploadFolder = projectFolder / "public" / "images" / "uploads"
uploadFolder.mkdir(parents=True, exist_ok=True)
appHost = settings.get("APP_HOST", "127.0.0.1")
appPort = int(settings.get("APP_PORT", "8000"))  # pyright: ignore[reportArgumentType]
