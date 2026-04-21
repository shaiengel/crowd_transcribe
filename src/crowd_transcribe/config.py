from dataclasses import dataclass, field
import os

from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env.secret", override=True)


@dataclass
class Config:
    aws_region: str = field(default_factory=lambda: os.getenv("AWS_REGION", "us-east-1"))
    aws_profile: str = field(default_factory=lambda: os.getenv("AWS_PROFILE", "portal"))
    s3_bucket: str = field(default_factory=lambda: os.getenv("S3_BUCKET", ""))
    db_host: str = field(default_factory=lambda: os.getenv("DB_HOST", "127.0.0.1"))
    db_port: str = field(default_factory=lambda: os.getenv("DB_PORT", "1433"))
    db_name: str = field(default_factory=lambda: os.getenv("DB_NAME", ""))
    db_user: str = field(default_factory=lambda: os.getenv("DB_USER", ""))
    db_password: str = field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
    db_driver_windows: str = field(default_factory=lambda: os.getenv("DB_DRIVER_WINDOWS", "ODBC Driver 17 for SQL Server"))
    sqlite_path: str = field(default_factory=lambda: os.getenv("SQLITE_PATH", "media.db"))
