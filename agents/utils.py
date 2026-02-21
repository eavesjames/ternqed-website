"""
Shared utilities for TernQED agents
"""
import os
import json
from datetime import datetime
from pathlib import Path
import anthropic


def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    else:
        # Try current directory
        env_path = Path.cwd() / '.env'
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value


# Load .env on module import
load_env()


def get_anthropic_client():
    """Get configured Anthropic API client"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return anthropic.Anthropic(api_key=api_key)


def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data, filepath):
    """Save JSON file"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    return filepath


def load_markdown(filepath):
    """Load markdown file with frontmatter parsing"""
    with open(filepath, 'r') as f:
        content = f.read()

    # Simple frontmatter extraction
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            body = parts[2].strip()
            return {'frontmatter': frontmatter, 'body': body, 'full': content}

    return {'frontmatter': '', 'body': content, 'full': content}


def save_markdown(filepath, frontmatter_dict, body):
    """Save markdown file with frontmatter"""
    import yaml

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    frontmatter_str = yaml.dump(frontmatter_dict, default_flow_style=False, sort_keys=False)

    full_content = f"""---
{frontmatter_str.strip()}
---

{body.strip()}
"""

    with open(filepath, 'w') as f:
        f.write(full_content)

    return filepath


def get_date_slug():
    """Get current date slug for filenames"""
    return datetime.now().strftime('%Y-%m-%d')


def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}\n")


def print_success(message):
    """Print success message"""
    print(f"✓ {message}")


def print_error(message):
    """Print error message"""
    print(f"✗ {message}")


def print_warning(message):
    """Print warning message"""
    print(f"⚠ {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ {message}")
