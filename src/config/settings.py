"""
Settings and configuration management.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
import yaml
from loguru import logger


class ServerConfig(BaseModel):
    """Server configuration."""
    name: str = "CodeCompass"
    version: str = "1.0.0"
    max_file_size_mb: int = 10
    max_search_results: int = 1000
    default_encoding: str = "utf-8"


class RepositoryConfig(BaseModel):
    """Repository configuration."""
    roots: List[str] = Field(default_factory=list)
    ignore_patterns: List[str] = Field(default_factory=lambda: [
        "**/node_modules/**",
        "**/.git/**",
        "**/__pycache__/**",
        "**/*.pyc",
        "**/dist/**",
        "**/build/**",
        "**/.venv/**",
        "**/venv/**",
        "**/.pytest_cache/**",
        "**/coverage/**",
        "**/.coverage",
        "**/htmlcov/**",
        "**/.mypy_cache/**",
        "**/.tox/**",
        "**/target/**",
        "**/Cargo.lock",
        "**/package-lock.json",
        "**/yarn.lock",
        "**/Pipfile.lock",
        "**/poetry.lock"
    ])


class SearchConfig(BaseModel):
    """Search configuration."""
    default_limit: int = 50
    max_limit: int = 1000
    case_sensitive: bool = False
    include_binary: bool = False
    file_extensions: List[str] = Field(default_factory=lambda: [
        "*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.java", "*.cpp", "*.c", "*.h",
        "*.go", "*.rs", "*.php", "*.rb", "*.swift", "*.kt", "*.scala", "*.r",
        "*.m", "*.sh", "*.bash", "*.zsh", "*.fish", "*.ps1", "*.bat", "*.cmd",
        "*.sql", "*.html", "*.css", "*.scss", "*.sass", "*.less", "*.xml",
        "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.conf",
        "*.md", "*.rst", "*.txt", "*.log"
    ])


class SemanticSearchConfig(BaseModel):
    """Semantic search configuration."""
    enabled: bool = True
    model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    index_path: str = "./indexes"
    rebuild_threshold_hours: int = 24


class TodoConfig(BaseModel):
    """TODO detection configuration."""
    patterns: List[str] = Field(default_factory=lambda: [
        "TODO", "FIXME", "HACK", "NOTE", "XXX", "BUG"
    ])
    case_sensitive: bool = False


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = "./logs/server.log"


class Settings(BaseModel):
    """Main settings class."""
    server: ServerConfig = Field(default_factory=ServerConfig)
    repositories: RepositoryConfig = Field(default_factory=RepositoryConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    semantic_search: SemanticSearchConfig = Field(default_factory=SemanticSearchConfig)
    todos: TodoConfig = Field(default_factory=TodoConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    @classmethod
    def load_from_file(cls, config_path: str = "config/default.yaml") -> "Settings":
        """Load settings from YAML file."""
        try:
            config_file = Path(config_path)
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                logger.info(f"Loaded configuration from {config_path}")
                return cls(**config_data)
            else:
                logger.warning(f"Config file not found: {config_path}, using defaults")
                return cls()
                
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return cls()
    
    @classmethod
    def load_from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        try:
            # Load from environment variables
            env_config = {}
            
            # Server config
            if os.getenv("MCP_SERVER_NAME"):
                env_config["server"] = {"name": os.getenv("MCP_SERVER_NAME")}
            
            if os.getenv("MCP_SERVER_VERSION"):
                env_config["server"] = env_config.get("server", {})
                env_config["server"]["version"] = os.getenv("MCP_SERVER_VERSION")
            
            # Repository roots
            if os.getenv("REPO_ROOT"):
                env_config["repositories"] = {"roots": [os.getenv("REPO_ROOT")]}
            
            # Logging level
            if os.getenv("LOG_LEVEL"):
                env_config["logging"] = {"level": os.getenv("LOG_LEVEL")}
            
            if env_config:
                logger.info("Loaded configuration from environment variables")
                return cls(**env_config)
            else:
                return cls()
                
        except Exception as e:
            logger.error(f"Error loading config from env: {e}, using defaults")
            return cls()
    
    def save_to_file(self, config_path: str = "config/default.yaml") -> None:
        """Save settings to YAML file."""
        try:
            config_file = Path(config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.dict(), f, default_flow_style=False, indent=2)
            
            logger.info(f"Saved configuration to {config_path}")
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get_repository_roots(self) -> List[str]:
        """Get repository roots, with fallback to current directory."""
        if self.repositories.roots:
            return self.repositories.roots
        else:
            return ["."]
    
    def is_file_allowed(self, file_path: str) -> bool:
        """Check if file is allowed based on configuration."""
        file_path = Path(file_path)
        
        # Check ignore patterns
        for pattern in self.repositories.ignore_patterns:
            if file_path.match(pattern):
                return False
        
        # Check file extensions
        if file_path.suffix:
            extension = f"*{file_path.suffix}"
            if extension not in self.search.file_extensions:
                return False
        
        return True
