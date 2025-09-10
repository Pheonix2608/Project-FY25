import json
import secrets
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext

class APIKeyManager:
    def __init__(self, api_keys_file: str = "utils/api_keys.json"):
        self.api_keys_file = Path(api_keys_file)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._ensure_api_keys_file()
        
    def _ensure_api_keys_file(self):
        """Ensure the API keys file exists and is properly initialized."""
        if not self.api_keys_file.exists():
            self.api_keys_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_api_keys({})
    
    def _load_api_keys(self) -> Dict:
        """Load API keys from the JSON file."""
        try:
            with open(self.api_keys_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    def _save_api_keys(self, api_keys: Dict):
        """Save API keys to the JSON file."""
        with open(self.api_keys_file, 'w') as f:
            json.dump(api_keys, f, indent=4)
    
    def generate_api_key(self, user_id: str, expiration_days: int = 30) -> str:
        """Generate a new API key for a user."""
        api_key = secrets.token_urlsafe(32)
        hashed_key = self.pwd_context.hash(api_key)
        
        api_keys = self._load_api_keys()
        api_keys[user_id] = {
            "key_hash": hashed_key,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=expiration_days)).isoformat(),
            "rate_limit": {
                "calls_per_minute": 60,
                "calls_per_day": 1000
            }
        }
        
        self._save_api_keys(api_keys)
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify an API key and return the associated user_id if valid."""
        api_keys = self._load_api_keys()
        
        for user_id, key_data in api_keys.items():
            if self.pwd_context.verify(api_key, key_data["key_hash"]):
                # Check if key has expired
                expires_at = datetime.fromisoformat(key_data["expires_at"])
                if expires_at > datetime.now():
                    return user_id
        return None
    
    def get_rate_limits(self, user_id: str) -> Dict:
        """Get rate limits for a user."""
        api_keys = self._load_api_keys()
        if user_id in api_keys:
            return api_keys[user_id].get("rate_limit", {
                "calls_per_minute": 60,
                "calls_per_day": 1000
            })
        return None
    
    def update_rate_limits(self, user_id: str, calls_per_minute: int, calls_per_day: int):
        """Update rate limits for a user."""
        api_keys = self._load_api_keys()
        if user_id in api_keys:
            api_keys[user_id]["rate_limit"] = {
                "calls_per_minute": calls_per_minute,
                "calls_per_day": calls_per_day
            }
            self._save_api_keys(api_keys)
