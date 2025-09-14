#!/usr/bin/env python3
"""
Run the Marketing Intelligence Dashboard with AI Insights
"""

import subprocess
import sys
import os

def main():    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/dashboard.py"])
    except KeyboardInterrupt:
        print("\nEnd")

if __name__ == "__main__":
    main()