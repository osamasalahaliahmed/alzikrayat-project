import pymysql

from app.config import settings


def getConnection():
    return pymysql.connect(  # pyright: ignore[reportCallIssue]
        host=settings.get("DB_HOST", "127.0.0.1"),
        port=int(settings.get("DB_PORT", "3306")),  # pyright: ignore[reportArgumentType]
        user=settings.get("DB_USER"),
        password=settings.get("DB_PASSWORD"),  # pyright: ignore[reportArgumentType]
        database=settings.get("DB_NAME", "alzikrayat"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
    )
