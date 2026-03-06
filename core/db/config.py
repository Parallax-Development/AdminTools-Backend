import os
from pathlib import Path

SQL_BACKENDS = {
    "postgres": "django.db.backends.postgresql",
    "mysql": "django.db.backends.mysql",
    "sqlite": "django.db.backends.sqlite3",
    "oracle": "django.db.backends.oracle",
    "sqlserver": "mssql",
}

SQL_DEFAULT_PORTS = {
    "postgres": "5432",
    "mysql": "3306",
    "oracle": "1521",
    "sqlserver": "1433",
}


def get_domain_backend():
    backend = os.getenv("DOMAIN_DB_BACKEND", os.getenv("DB_BACKEND", "sqlite")).lower()
    if backend == "postgresql":
        backend = "postgres"
    if backend == "mssql":
        backend = "sqlserver"
    return backend


def get_django_backend():
    backend = get_domain_backend()
    if backend == "mongodb":
        backend = os.getenv("DJANGO_DB_BACKEND", "sqlite").lower()
    return backend


def install_mysql_driver():
    driver = os.getenv("MYSQL_DRIVER", "pymysql").lower()
    if driver == "pymysql":
        import pymysql

        pymysql.install_as_MySQLdb()


def build_django_databases(base_dir: Path):
    backend = get_django_backend()
    if backend == "mysql":
        install_mysql_driver()
    if backend == "sqlite":
        db_path = os.getenv("SQLITE_PATH", str(base_dir / "db.sqlite3"))
        return {"default": {"ENGINE": SQL_BACKENDS[backend], "NAME": db_path}}
    engine = SQL_BACKENDS.get(backend, SQL_BACKENDS["sqlite"])
    name = os.getenv("DB_NAME", "parallax_admin")
    user = os.getenv("DB_USER", "parallax")
    password = os.getenv("DB_PASSWORD", "parallax")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", SQL_DEFAULT_PORTS.get(backend, ""))
    return {
        "default": {
            "ENGINE": engine,
            "NAME": name,
            "USER": user,
            "PASSWORD": password,
            "HOST": host,
            "PORT": port,
        }
    }


def get_mongo_settings():
    return {
        "uri": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "db": os.getenv("MONGO_DB", "parallax_admin"),
    }
