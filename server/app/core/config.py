import os

class Settings:
    PROJECT_NAME: str = "따릉이 API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")

settings = Settings()