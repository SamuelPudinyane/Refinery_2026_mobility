"""
Configuration settings for the Mobility App
This file contains all configuration settings for different environments
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with common settings"""
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP = os.getenv('FLASK_APP', 'app.py')
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Database Configuration
    DB_NAME = os.getenv('DB_NAME', 'rand_refinary')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    @staticmethod
    def get_database_url():
        """
        Generate database URL from environment variables
        Priority: DATABASE_URL > Individual DB parameters
        """
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Handle Heroku postgres:// to postgresql:// conversion
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        
        # Construct from individual parameters
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    
    @staticmethod
    def get_psycopg2_params():
        """
        Get connection parameters for psycopg2
        Returns a dictionary of connection parameters
        """
        return {
            'dbname': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'host': Config.DB_HOST,
            'port': Config.DB_PORT
        }


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_ECHO = True  # Print SQL queries in console


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Override with production database if available
    @staticmethod
    def get_database_url():
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        return Config.get_database_url()


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    
    # Use test database
    DB_NAME = os.getenv('TEST_DB_NAME', 'rand_refinary_test')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration based on environment
    
    Args:
        env (str): Environment name ('development', 'production', 'testing')
    
    Returns:
        Config: Configuration class for the specified environment
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
