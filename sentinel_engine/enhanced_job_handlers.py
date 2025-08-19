"""
Sentinel Engine Phase 2 - Enhanced Job Handlers
Complete job processing system for revenue generation
"""
import asyncio
import json
import logging
import os
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiofiles
import requests

logger = logging.getLogger(__name__)

class EnhancedJobHandlers:
    """Enhanced job handlers for complete Phase 2 functionality"""
    
    def __init__(self):
        self.handlers = {
            'echo': self.handle_echo,
            'llm_request': self.handle_llm_request,
            'git_clone': self.handle_git_clone,
            'git_status': self.handle_git_status,
            'file_read': self.handle_file_read,
            'file_write': self.handle_file_write,
            'file_list': self.handle_file_list,
            'shell_exec': self.handle_shell_exec,
            'web_request': self.handle_web_request,
            'build_project': self.handle_build_project,
            'test_endpoint': self.handle_test_endpoint
        }
        
        # Safe commands whitelist
        self.safe_commands = {
            'dir', 'ls', 'pwd', 'whoami', 'date', 'echo', 'type', 'cat',
            'git', 'python', 'pip', 'node', 'npm', 'dotnet', 'docker'
        }
    
    async def handle_job(self, job_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route job to appropriate handler"""
        try:
            if job_type not in self.handlers:
                return {
                    'success': False,
                    'error': f'Unknown job type: {job_type}',
                    'available_types': list(self.handlers.keys())
                }
            
            handler = self.handlers[job_type]
            result = await handler(payload)
            
            return {
                'success': True,
                'job_type': job_type,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Job handler error for {job_type}: {str(e)}")
            return {
                'success': False,
                'job_type': job_type,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def handle_echo(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Echo test handler"""
        message = payload.get('message', 'Hello from Sentinel Engine Phase 2!')
        return {
            'echo': message,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'success'
        }
    
    async def handle_llm_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LLM requests through multi-LLM orchestrator"""
        from .multi_llm_orchestrator import multi_llm
        
        prompt = payload.get('prompt')
        task_type = payload.get('task_type', 'general')
        use_consensus = payload.get('use_consensus', False)
        budget_limit = payload.get('budget_limit', 1.0)
        
        if not prompt:
            raise ValueError("Prompt is required for LLM requests")
        
        result = await multi_llm.route_task(prompt, task_type, use_consensus, budget_limit)
        
        return {
            'llm_result': result,
            'usage_summary': multi_llm.get_usage_summary()
        }
    
    async def handle_git_clone(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Clone git repository"""
        try:
            import git
            from git import Repo
        except ImportError:
            raise ValueError("GitPython not available. Run: pip install gitpython")
        
        repo_url = payload.get('repo_url')
        target_dir = payload.get('target_dir', './repos')
        branch = payload.get('branch', 'main')
        
        if not repo_url:
            raise ValueError("repo_url is required")
        
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        clone_path = Path(target_dir) / repo_name
        
        if clone_path.exists():
            repo = Repo(clone_path)
            origin = repo.remotes.origin
            origin.pull()
            operation = 'pulled'
        else:
            repo = Repo.clone_from(repo_url, clone_path, branch=branch)
            operation = 'cloned'
        
        return {
            'operation': operation,
            'repo_url': repo_url,
            'local_path': str(clone_path),
            'branch': repo.active_branch.name,
            'latest_commit': repo.head.commit.hexsha[:8]
        }
    
    async def handle_git_status(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get git repository status"""
        try:
            import git
            from git import Repo
        except ImportError:
            raise ValueError("GitPython not available")
        
        repo_path = payload.get('repo_path', '.')
        
        if not Path(repo_path).exists():
            raise ValueError("Repository path does not exist")
        
        repo = Repo(repo_path)
        
        return {
            'repo_path': repo_path,
            'branch': repo.active_branch.name,
            'latest_commit': repo.head.commit.hexsha[:8],
            'commit_message': repo.head.commit.message.strip(),
            'is_dirty': repo.is_dirty(),
            'untracked_files': repo.untracked_files[:10],  # Limit to 10
            'modified_files': [item.a_path for item in repo.index.diff(None)][:10]
        }
    
    async def handle_file_read(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents"""
        file_path = payload.get('file_path')
        encoding = payload.get('encoding', 'utf-8')
        max_size = payload.get('max_size', 100000)  # 100KB default
        
        if not file_path:
            raise ValueError("file_path is required")
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.stat().st_size > max_size:
            raise ValueError(f"File too large. Max size: {max_size} bytes")
        
        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            content = await f.read()
        
        return {
            'file_path': str(file_path),
            'content': content,
            'size_bytes': file_path.stat().st_size,
            'encoding': encoding
        }
    
    async def handle_file_write(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file"""
        file_path = payload.get('file_path')
        content = payload.get('content', '')
        encoding = payload.get('encoding', 'utf-8')
        create_dirs = payload.get('create_dirs', True)
        
        if not file_path:
            raise ValueError("file_path is required")
        
        file_path = Path(file_path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
            await f.write(content)
        
        return {
            'file_path': str(file_path),
            'bytes_written': len(content.encode(encoding)),
            'encoding': encoding
        }
    
    async def handle_file_list(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """List files in directory"""
        directory = payload.get('directory', '.')
        pattern = payload.get('pattern', '*')
        limit = payload.get('limit', 50)
        
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        files = []
        for path in directory.glob(pattern):
            if len(files) >= limit:
                break
                
            files.append({
                'name': path.name,
                'path': str(path),
                'size': path.stat().st_size if path.is_file() else 0,
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'modified_time': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            })
        
        return {
            'directory': str(directory),
            'pattern': pattern,
            'file_count': len(files),
            'files': files
        }
    
    async def handle_shell_exec(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell command (sandboxed)"""
        command = payload.get('command')
        working_dir = payload.get('working_dir', '.')
        timeout = payload.get('timeout', 30)
        
        if not command:
            raise ValueError("command is required")
        
        # Parse and validate command
        cmd_parts = command.strip().split()
        if not cmd_parts:
            raise ValueError("Empty command")
        
        base_command = cmd_parts[0].lower()
        
        if base_command not in self.safe_commands:
            raise ValueError(f"Command '{base_command}' not allowed. Safe commands: {', '.join(sorted(self.safe_commands))}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'command': command,
                'working_dir': working_dir,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            raise ValueError(f"Command timed out after {timeout} seconds")
    
    async def handle_web_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP web request"""
        url = payload.get('url')
        method = payload.get('method', 'GET').upper()
        headers = payload.get('headers', {})
        data = payload.get('data')
        timeout = payload.get('timeout', 10)
        
        if not url:
            raise ValueError("url is required")
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data if data else None,
            timeout=timeout
        )
        
        return {
            'url': url,
            'method': method,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': response.text[:1000],  # Limit content
            'success': 200 <= response.status_code < 300
        }
    
    async def handle_build_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Build a project"""
        project_path = payload.get('project_path', '.')
        build_type = payload.get('build_type', 'auto')
        
        project_path = Path(project_path)
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")
        
        # Auto-detect build type
        if build_type == 'auto':
            if (project_path / 'package.json').exists():
                build_type = 'node'
            elif (project_path / 'requirements.txt').exists():
                build_type = 'python'
            elif any(project_path.glob('*.csproj')):
                build_type = 'dotnet'
        
        # Define build commands
        commands = []
        if build_type == 'python':
            if (project_path / 'requirements.txt').exists():
                commands = ['pip install -r requirements.txt']
        elif build_type == 'node':
            commands = ['npm install']
            if (project_path / 'package.json').exists():
                commands.append('npm run build')
        elif build_type == 'dotnet':
            commands = ['dotnet restore', 'dotnet build']
        
        # Execute commands
        results = []
        for cmd in commands:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            results.append({
                'command': cmd,
                'exit_code': result.returncode,
                'stdout': result.stdout[-500:],  # Last 500 chars
                'stderr': result.stderr[-500:],
                'success': result.returncode == 0
            })
            
            if result.returncode != 0:
                break
        
        return {
            'project_path': str(project_path),
            'build_type': build_type,
            'commands_executed': len(results),
            'overall_success': all(r['success'] for r in results),
            'results': results
        }
    
    async def handle_test_endpoint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Test API endpoint"""
        url = payload.get('url', 'http://127.0.0.1:8001/healthz')
        expected_status = payload.get('expected_status', 200)
        timeout = payload.get('timeout', 5)
        
        try:
            response = requests.get(url, timeout=timeout)
            
            return {
                'url': url,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': response.status_code == expected_status,
                'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                'content_preview': response.text[:200]
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }

# Global instance
enhanced_handlers = EnhancedJobHandlers()
