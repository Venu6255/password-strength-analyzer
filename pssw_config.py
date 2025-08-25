import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # Password analysis settings
    MIN_PASSWORD_LENGTH = 4
    MAX_PASSWORD_LENGTH = 100
    
    # Wordlist settings
    MAX_WORDLIST_SIZE = 10000
    WORDLIST_FORMATS = ['txt', 'csv']
    
    # File paths
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    DOWNLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'downloads')
    
    # Ensure download folder exists
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
    
    # Common password patterns
    COMMON_PATTERNS = [
        'password', '123456', 'qwerty', 'abc123', 'letmein',
        'admin', 'welcome', 'monkey', 'dragon', 'master'
    ]
    
    # Leetspeak replacements
    LEET_REPLACEMENTS = {
        'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'],
        's': ['$', '5'], 't': ['7'], 'l': ['1'], 'g': ['9']
    }