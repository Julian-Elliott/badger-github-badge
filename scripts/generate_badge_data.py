#!/usr/bin/env python3
"""
GitHub Badge Data Generator
Fetches GitHub profile data and generates JSON files for Badger 2040 W consumption
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configuration
USERNAME = os.environ.get('USERNAME', 'Julian-Elliott')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
OUTPUT_DIR = 'data'
PUBLIC_DIR = 'public'

# GitHub API configuration
HEADERS = {
    'User-Agent': 'GitHub-Badge-Generator',
    'Accept': 'application/vnd.github.v3+json'
}

if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

# API URLs
USER_URL = f'https://api.github.com/users/{USERNAME}'
REPOS_URL = f'https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated'
EVENTS_URL = f'https://api.github.com/users/{USERNAME}/events?per_page=30'
CONTRIB_URL = f'https://github-contributions-api.jogruber.de/v4/{USERNAME}'

def ensure_directories():
    """Ensure output directories exist"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(f'{PUBLIC_DIR}/api', exist_ok=True)

def fetch_github_data(url: str, description: str) -> Dict[str, Any]:
    """Fetch data from GitHub API with error handling"""
    try:
        print(f"Fetching {description}...")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        # Check rate limit
        remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
        print(f"  ✓ Success ({remaining} requests remaining)")
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Failed to fetch {description}: {e}")
        return {}

def analyze_repositories(repos: List[Dict]) -> Dict[str, Any]:
    """Analyze repository data for statistics"""
    if not repos:
        return {
            'total_repos': 0,
            'total_stars': 0,
            'total_forks': 0,
            'languages': {},
            'topics': {},
            'most_starred': None,
            'recent_repo': None,
            'avg_stars': 0
        }
    
    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
    total_forks = sum(repo.get('forks_count', 0) for repo in repos)
    
    # Language analysis
    languages = {}
    topics = {}
    
    for repo in repos:
        # Count languages
        lang = repo.get('language')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
            
        # Count topics
        for topic in repo.get('topics', []):
            topics[topic] = topics.get(topic, 0) + 1
    
    # Sort by frequency
    languages = dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
    topics = dict(sorted(topics.items(), key=lambda x: x[1], reverse=True))
    
    # Find most starred repo
    most_starred = max(repos, key=lambda x: x.get('stargazers_count', 0))
    
    return {
        'total_repos': len(repos),
        'total_stars': total_stars,
        'total_forks': total_forks,
        'languages': languages,
        'topics': topics,
        'most_starred': {
            'name': most_starred.get('name'),
            'stars': most_starred.get('stargazers_count', 0),
            'url': most_starred.get('html_url')
        },
        'recent_repo': {
            'name': repos[0].get('name'),
            'updated_at': repos[0].get('updated_at'),
            'url': repos[0].get('html_url')
        } if repos else None,
        'avg_stars': total_stars // len(repos) if repos else 0
    }

def process_activity_events(events: List[Dict]) -> List[Dict]:
    """Process and simplify activity events"""
    processed_events = []
    
    for event in events[:10]:  # Keep top 10 events
        event_type = event.get('type', 'Unknown')
        repo_name = event.get('repo', {}).get('name', 'Unknown')
        created_at = event.get('created_at', '')
        
        # Simplify event descriptions
        if event_type == 'PushEvent':
            action = 'Pushed to'
            icon = '→'
        elif event_type == 'CreateEvent':
            action = 'Created'
            icon = '+'
        elif event_type == 'WatchEvent':
            action = 'Starred'
            icon = '⭐'
        elif event_type == 'ForkEvent':
            action = 'Forked'
            icon = '⑂'
        elif event_type == 'IssuesEvent':
            action = 'Issue on'
            icon = '!'
        elif event_type == 'PullRequestEvent':
            action = 'PR on'
            icon = '↗'
        else:
            action = event_type.replace('Event', '')
            icon = '•'
        
        processed_events.append({
            'type': event_type,
            'action': action,
            'icon': icon,
            'repo': repo_name,
            'repo_short': repo_name.split('/')[-1] if '/' in repo_name else repo_name,
            'created_at': created_at,
            'display': f"{icon} {action} {repo_name.split('/')[-1]}"
        })
    
    return processed_events

def generate_contribution_summary(contrib_data: Dict) -> Dict[str, Any]:
    """Generate contribution summary statistics"""
    if not contrib_data:
        return {
            'total_contributions': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'best_day': None,
            'recent_activity': []
        }
    
    contributions = contrib_data.get('contributions', [])
    total_contributions = contrib_data.get('totalContributions', 0)
    
    # Calculate streaks (simplified)
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    # Get recent contributions (last 84 days for 12x7 grid)
    recent_contribs = contributions[-84:] if len(contributions) >= 84 else contributions
    
    # Find best contribution day
    best_day = max(contributions, key=lambda x: x.get('contributionCount', 0)) if contributions else None
    
    return {
        'total_contributions': total_contributions,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'best_day': {
            'date': best_day.get('date'),
            'count': best_day.get('contributionCount', 0)
        } if best_day else None,
        'recent_activity': recent_contribs
    }

def generate_compact_data():
    """Generate compact data optimized for Badger 2040 W"""
    print("=== Generating GitHub Badge Data ===")
    
    # Fetch all data
    user_data = fetch_github_data(USER_URL, "user profile")
    repos_data = fetch_github_data(REPOS_URL, "repositories")
    events_data = fetch_github_data(EVENTS_URL, "recent events")
    contrib_data = fetch_github_data(CONTRIB_URL, "contributions")
    
    # Process repositories
    repos_list = repos_data if isinstance(repos_data, list) else []
    repo_stats = analyze_repositories(repos_list)
    
    # Process events
    events_list = events_data if isinstance(events_data, list) else []
    activity = process_activity_events(events_list)
    
    # Process contributions
    contrib_summary = generate_contribution_summary(contrib_data)
    
    # Generate timestamp
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create compact profile data
    profile_data = {
        'username': user_data.get('login', USERNAME),
        'name': user_data.get('name', USERNAME),
        'bio': user_data.get('bio', ''),
        'company': user_data.get('company', ''),
        'location': user_data.get('location', ''),
        'blog': user_data.get('blog', ''),
        'public_repos': user_data.get('public_repos', 0),
        'followers': user_data.get('followers', 0),
        'following': user_data.get('following', 0),
        'created_at': user_data.get('created_at', ''),
        'updated_at': timestamp,
        'avatar_url': user_data.get('avatar_url', ''),
        'html_url': user_data.get('html_url', f'https://github.com/{USERNAME}')
    }
    
    # Create comprehensive badge data
    badge_data = {
        'profile': profile_data,
        'stats': repo_stats,
        'activity': activity,
        'contributions': contrib_summary,
        'meta': {
            'generated_at': timestamp,
            'username': USERNAME,
            'data_sources': {
                'profile': bool(user_data),
                'repos': bool(repos_list),
                'events': bool(events_list),
                'contributions': bool(contrib_data)
            }
        }
    }
    
    # Save individual files for different use cases
    files_to_save = {
        'badge_full.json': badge_data,
        'badge_compact.json': {
            'profile': {
                'username': profile_data['username'],
                'name': profile_data['name'],
                'public_repos': profile_data['public_repos'],
                'followers': profile_data['followers'],
                'following': profile_data['following']
            },
            'stats': {
                'total_stars': repo_stats['total_stars'],
                'total_forks': repo_stats['total_forks'],
                'languages': dict(list(repo_stats['languages'].items())[:5]),
                'most_starred': repo_stats['most_starred']
            },
            'activity': activity[:5],
            'updated_at': timestamp
        },
        'profile.json': profile_data,
        'stats.json': repo_stats,
        'activity.json': activity,
        'contributions.json': contrib_summary
    }
    
    # Save to both data and public directories
    for filename, data in files_to_save.items():
        # Save to data directory (for repository)
        with open(f'{OUTPUT_DIR}/{filename}', 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save to public directory (for GitHub Pages)
        with open(f'{PUBLIC_DIR}/api/{filename}', 'w') as f:
            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
    
    # Generate simple text files for basic consumption
    with open(f'{PUBLIC_DIR}/api/badge_simple.txt', 'w') as f:
        f.write(f"{profile_data['username']}\n")
        f.write(f"{profile_data['name']}\n")
        f.write(f"{profile_data['public_repos']}\n")
        f.write(f"{profile_data['followers']}\n")
        f.write(f"{profile_data['following']}\n")
        f.write(f"{repo_stats['total_stars']}\n")
        f.write(f"{repo_stats['total_forks']}\n")
        f.write(f"{list(repo_stats['languages'].keys())[0] if repo_stats['languages'] else 'None'}\n")
        f.write(f"{repo_stats['most_starred']['name'] if repo_stats['most_starred'] else 'None'}\n")
        f.write(f"{timestamp}\n")
    
    print(f"\n=== Data Generation Complete ===")
    print(f"Profile: {profile_data['name']} (@{profile_data['username']})")
    print(f"Repos: {repo_stats['total_repos']} ({repo_stats['total_stars']} stars)")
    print(f"Languages: {', '.join(list(repo_stats['languages'].keys())[:3])}")
    print(f"Recent activity: {len(activity)} events")
    print(f"Generated at: {timestamp}")
    
    return badge_data

if __name__ == '__main__':
    ensure_directories()
    generate_compact_data()
