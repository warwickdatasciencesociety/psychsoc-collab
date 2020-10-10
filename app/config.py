# config variables that eventually should be retrieved from a .env file

class Config:
    SECRET_KEY = "super-secret"

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/api/"
    JWT_REFRESH_COOKIE_PATH = "/token/refresh"
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_SECRET_KEY = "super-secret"

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@db:3306/psych_collab"
