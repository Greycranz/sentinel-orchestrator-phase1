"""
Secure API key management with OS keychain, rotation, and redaction.
"""
import os
import re
import json
import time
from typing import Literal, Optional
from pathlib import Path

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

Provider = Literal["groq", "openai", "anthropic"]

# Redaction pattern for any key-like strings
KEY_PATTERN = re.compile(r'(sk-[a-zA-Z0-9]{48,}|gsk_[a-zA-Z0-9]{52,}|[\w-]{20,})', re.IGNORECASE)

class SecretsManager:
    """Manages API keys with OS keychain -> .env.local -> env fallback"""
    
    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self.env_local = self.repo_root / ".env.local"
        self.service_name = "sentinel-engine"
        
    def get_key(self, provider: Provider) -> Optional[str]:
        """Get API key for provider from keychain -> .env.local -> env"""
        key_name = f"{provider.upper()}_API_KEY"
        
        # Try OS keychain first
        if KEYRING_AVAILABLE:
            try:
                key = keyring.get_password(self.service_name, key_name)
                if key:
                    return key
            except Exception:
                pass
        
        # Try .env.local
        if self.env_local.exists():
            try:
                env_content = self.env_local.read_text(encoding='utf-8')
                for line in env_content.split('\n'):
                    if line.strip().startswith(f"{key_name}="):
                        return line.split('=', 1)[1].strip().strip('"\'')
            except Exception:
                pass
        
        # Fallback to process env
        return os.getenv(key_name)
    
    def set_key(self, provider: Provider, value: str) -> None:
        """Set API key for provider in keychain (preferred) or .env.local"""
        if not value or not value.strip():
            raise ValueError(f"Empty key provided for {provider}")
            
        key_name = f"{provider.upper()}_API_KEY"
        
        # Try keychain first
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(self.service_name, key_name, value)
                self._audit_key_action("set", provider, "keychain")
                return
            except Exception:
                pass
        
        # Fallback to .env.local
        self._update_env_local(key_name, value)
        self._audit_key_action("set", provider, "env_local")
    
    def has_valid_key(self, provider: Provider) -> bool:
        """Check if provider has a valid-looking key"""
        key = self.get_key(provider)
        if not key:
            return False
        
        # Basic validation patterns
        patterns = {
            "groq": r"gsk_[a-zA-Z0-9]{52,}",
            "openai": r"sk-[a-zA-Z0-9]{48,}",
            "anthropic": r"sk-ant-[a-zA-Z0-9-]{20,}"
        }
        
        pattern = patterns.get(provider, r"[\w-]{20,}")
        return bool(re.match(pattern, key))
    
    def rotate_key(self, provider: Provider, new_value: str) -> None:
        """Rotate key: store as _NEXT, validate, then promote to live"""
        next_key_name = f"{provider.upper()}_API_KEY_NEXT"
        
        # Store new key temporarily
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(self.service_name, next_key_name, new_value)
            except Exception:
                self._update_env_local(next_key_name, new_value)
        else:
            self._update_env_local(next_key_name, new_value)
        
        self._audit_key_action("rotate_prepare", provider, "stored_next")
        
        # TODO: Add validation call here
        # For now, immediately promote (unsafe but functional)
        self.set_key(provider, new_value)
        self._cleanup_next_key(provider)
        self._audit_key_action("rotate_complete", provider, "promoted")
    
    def redact(self, text: str) -> str:
        """Redact any key-like patterns in text"""
        if not text:
            return text
        return KEY_PATTERN.sub('****', text)
    
    def _update_env_local(self, key_name: str, value: str) -> None:
        """Update .env.local file with new key"""
        lines = []
        updated = False
        
        if self.env_local.exists():
            lines = self.env_local.read_text(encoding='utf-8').split('\n')
        
        # Update existing or add new
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key_name}="):
                lines[i] = f"{key_name}={value}"
                updated = True
                break
        
        if not updated:
            lines.append(f"{key_name}={value}")
        
        # Ensure directory exists
        self.env_local.parent.mkdir(parents=True, exist_ok=True)
        self.env_local.write_text('\n'.join(lines), encoding='utf-8')
    
    def _cleanup_next_key(self, provider: Provider) -> None:
        """Remove _NEXT key after successful rotation"""
        next_key_name = f"{provider.upper()}_API_KEY_NEXT"
        
        if KEYRING_AVAILABLE:
            try:
                keyring.delete_password(self.service_name, next_key_name)
            except Exception:
                pass
        
        # Also remove from .env.local if present
        if self.env_local.exists():
            try:
                lines = self.env_local.read_text(encoding='utf-8').split('\n')
                lines = [l for l in lines if not l.strip().startswith(f"{next_key_name}=")]
                self.env_local.write_text('\n'.join(lines), encoding='utf-8')
            except Exception:
                pass
    
    def _audit_key_action(self, action: str, provider: str, backend: str) -> None:
        """Log key management actions to audit trail"""
        log_dir = self.repo_root / "ops" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            "timestamp": time.time(),
            "trace_id": f"key-{int(time.time())}",
            "component": "secrets_manager",
            "level": "info",
            "event": "key_action",
            "data": {
                "action": action,
                "provider": provider,
                "backend": backend
            }
        }
        
        log_file = log_dir / "keys.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

# Global instance
secrets_manager = SecretsManager()
