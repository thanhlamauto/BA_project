"""
Configuration Management
Environment-based configuration for local development and production
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ba_project')
    BENTOML_ENDPOINT = os.getenv('BENTOML_ENDPOINT', 'http://localhost:3000')
    GRAFANA_CLOUD_API_KEY = os.getenv('GRAFANA_CLOUD_API_KEY', '')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    # MongoDB Database name
    MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'ba_project')

    # Logging configuration
    USE_MONGODB_LOGGING = os.getenv('USE_MONGODB_LOGGING', 'false').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/ba_project')
    USE_MONGODB_LOGGING = False  # Use CSV logging in development by default


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    USE_MONGODB_LOGGING = True  # Use MongoDB logging in production
    # MongoDB Atlas URI from environment
    # BentoCloud endpoint from environment


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    MONGODB_URI = 'mongodb://localhost:27017/ba_project_test'
    USE_MONGODB_LOGGING = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on ENVIRONMENT variable"""
    env = os.getenv('ENVIRONMENT', 'development')
    return config.get(env, config['default'])()
