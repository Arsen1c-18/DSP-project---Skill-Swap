# Configuration for Skill Swap Platform

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# File paths
SKILLS_FILE = os.path.join(DATA_DIR, 'skills.csv')
USERS_FILE = os.path.join(DATA_DIR, 'users.csv')
SKILL_RELATIONSHIPS_FILE = os.path.join(DATA_DIR, 'skill_relationships.csv')

# Application settings
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Recommendation settings
TOP_RECOMMENDATIONS = 10
MIN_MATCH_SCORE = 0.3

# NLP settings
MAX_TASK_KEYWORDS = 5
TEXT_SIMILARITY_WEIGHT = 0.4
SKILL_MATCH_WEIGHT = 0.6
