#!/usr/bin/env python3
import time
import random
import hashlib
import json
from collections import defaultdict
from datetime import datetime

class VersionController:
    def __init__(self):
        self.versions = defaultdict(list)
        .releases = []
        .branches = ['main', 'develop', 'staging', 'release', 'hotfix']
        self.tags = {}
        self.commits = []
        self.artifacts = {}
        self.current_version = {}
        
    def generate_commit(self, branch='main'):
        commit_id = hashlib.sha1(str(random.random()).encode()).hexdigest()
        
        commit = {
            'id': commit_id,
            'branch': branch,
            'message': random.choice([
                'Fix: resolve memory leak',
                'Feature: add new API endpoint',
                'Update: improve performance',
                'Refactor: clean up code',
                'Docs: update documentation',
                'Test: add unit tests',
                'Chore: update dependencies',
                'Fix: resolve race condition',
                'Feature: implement caching',
                'Security: patch vulnerability'
            ]),
            'author': f"dev{random.randint(1, 10)}@company.com",
            'timestamp': time.time() - random.randint(0, 604800),
            'files_changed': random.randint(1, 20),
            'insertions': random.randint(10, 500),
            'deletions': random.randint(0, 200),
            'parent': None
        }
        
        if self.commits:
            commit['parent'] = self.commits[-1]['id']
        
        return commit
    
    def create_version(self, component, version_str):
        version = {
            'component': component,
            'version': version_str,
            'commits': [],
            'created_at': time.time(),
            'build_id': f"build_{int(time.time())}_{random.randint(1000, 9999)}",
            'status': 'active',
            'metadata': {
                'environment': random.choice(['development', 'staging', 'production']),
                'deployed_by': f"user_{random.randint(1, 100)}",
                'deployment_strategy': random.choice(['rolling', 'blue-green', 'canary'])
            }
        }
        
        self.versions[component].append(version)
        self.current_version[component] = version
        return version
    
    def generate_version_string(self):
        major = random.randint(1, 5)
        minor = random.randint(0, 20)
        patch = random.randint(0, 50)
        return f"{major}.{minor}.{patch}"
    
    def create_release(self, version_str, branch='main'):
        release = {
            'id': f"release_{int(time.time())}_{random.randint(1000, 9999)}",
            'version': version_str,
            'branch': branch,
            'commits': [],
            'created_at': time.time(),
            'published_at': time.time() + random.randint(0, 3600),
            'author': f"release_manager_{random.randint(1, 5)}",
            'artifacts': []
        }
        
        for _ in range(random.randint(5, 20)):
            commit = self.generate_commit(branch)
            self.commits.append(commit)
            release['commits'].append(commit['id'])
        
        self.releases.append(release)
        return release
    
    def tag_version(self, component, version_str, tag_name):
        tag = {
            'component': component,
            'version': version_str,
            'tag': tag_name,
            'created_at': time.time(),
            'author': f"user_{random.randint(1, 100)}",
            'message': f"Tag {tag_name} for version {version_str}"
        }
        
        self.tags[tag_name] = tag
        return tag
    
    def compare_versions(self, v1, v2):
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1
        return 0
    
    def get_latest_version(self, component):
        if component not in self.versions or not self.versions[component]:
            return None
        
        versions = [v['version'] for v in self.versions[component]]
        return max(versions, key=lambda v: [int(x) for x in v.split('.')])
    
    def get_version_history(self, component, limit=10):
        if component not in self.versions:
            return []
        
        sorted_versions = sorted(
            self.versions[component],
            key=lambda v: [int(x) for x in v['version'].split('.')],
            reverse=True
        )
        
        return sorted_versions[:limit]
    
    def rollback_version(self, component, target_version):
        if component not in self.current_version:
            return False
        
        current = self.current_version[component]['version']
        comparison = self.compare_versions(target_version, current)
        
        if comparison >= 0:
            return False
        
        for version in self.versions[component]:
            if version['version'] == target_version:
                self.current_version[component] = version
                return True
        
        return False
    
    def generate_build_artifact(self, component, version_str):
        artifact_id = f"artifact_{component}_{version_str}_{int(time.time())}"
        
        artifact = {
            'id': artifact_id,
            'component': component,
            'version': version_str,
            'build_time': time.time(),
            'size': random.randint(1024, 102400),
            'checksum': hashlib.sha256(f"{component}{version_str}{random.random()}".encode()).hexdigest(),
            'format': random.choice(['zip', 'tar.gz', 'jar', 'docker']),
            'build_server': f"builder-{random.randint(1, 5)}.internal"
        }
        
        self.artifacts[artifact_id] = artifact
        return artifact
    
    def simulate_version_workflow(self, iterations=50):
        components = ['api', 'web', 'worker', 'scheduler', 'cli']
        
        for i in range(iterations):
            component = random.choice(components)
            
            if random.random() > 0.7 or component not in self.current_version:
                version = self.generate_version_string()
                self.create_version(component, version)
                
                if random.random() > 0.5:
                    tag_name = f"v{version.replace('.', '_')}"
                    self.tag_version(component, version, tag_name)
                
                if random.random() > 0.6:
                    self.generate_build_artifact(component, version)
            
            elif random.random() > 0.8:
                versions = self.versions[component]
                if len(versions) > 1:
                    target = versions[-2]['version']
                    self.rollback_version(component, target)
            
            if random.random() > 0.9:
                release_version = self.generate_version_string()
                self.create_release(release_version)
    
    def get_version_stats(self):
        stats = {
            'total_components': len(self.versions),
            'total_versions': sum(len(v) for v in self.versions.values()),
            'total_releases': len(self.releases),
            'total_tags': len(self.tags),
            'total_commits': len(self.commits),
            'total_artifacts': len(self.artifacts),
            'components': {}
        }
        
        for component, versions in self.versions.items():
            stats['components'][component] = {
                'versions': len(versions),
                'latest': self.get_latest_version(component),
                'current': self.current_version.get(component, {}).get('version')
            }
        
        return stats
    
    def export_version_manifest(self, component):
        if component not in self.versions:
            return None
        
        manifest = {
            'component': component,
            'generated': datetime.now().isoformat(),
            'current_version': self.current_version.get(component, {}).get('version'),
            'versions': []
        }
        
        for version in self.versions[component]:
            manifest['versions'].append({
                'version': version['version'],
                'created_at': version['created_at'],
                'build_id': version['build_id'],
                'status': version['status']
            })
        
        return manifest

def main():
    vc = VersionController()
    vc.simulate_version_workflow(100)
    stats = vc.get_version_stats()
    
    print(f"Version controller: {stats['total_components']} components, "
          f"{stats['total_versions']} versions, {stats['total_releases']} releases")

if __name__ == "__main__":
    main()