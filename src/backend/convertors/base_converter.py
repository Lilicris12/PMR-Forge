"""
PMR Forge - Base Model Converter
Base class for all model converters
"""

from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseModelConverter(ABC):
    """Abstract base class for model converters"""
    
    def __init__(self, context):
        """
        Initialize the converter
        
        Args:
            context: ConversionContext from the pipeline
        """
        self.context = context
        self.source_dir = context.temp_dir / "source"
        self.output_dir = context.temp_dir / "converted"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized {self.__class__.__name__} for {context.input_path}")
    
    @abstractmethod
    def convert(self):
        """
        Convert the model files
        
        This method must be implemented by subclasses
        """
        pass
    
    def _log(self, message: str):
        """Log a message"""
        logger.info(f"[{self.__class__.__name__}] {message}")
        self.context.log_messages.append(f"[{self.__class__.__name__}] {message}")
        print(f"[{self.__class__.__name__}] {message}")
    
    def _copy_file(self, src: Path, dst: Path):
        """Copy a file with logging"""
        import shutil
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        self._log(f"Copied: {src.name} -> {dst.name}")
    
    def _find_files(self, extensions: list) -> list:
        """Find files with specific extensions"""
        files = list(self.source_dir.rglob("*"))
        return [f for f in files if f.is_file() and f.suffix.lower() in extensions]
    
    def _find_file(self, name: str) -> Optional[Path]:
        """Find a specific file by name"""
        for f in self.source_dir.rglob("*"):
            if f.is_file() and f.name.lower() == name.lower():
                return f
        return None
    
    def _find_files_by_pattern(self, pattern: str) -> list:
        """Find files matching a pattern"""
        import fnmatch
        files = []
        for f in self.source_dir.rglob("*"):
            if f.is_file() and fnmatch.fnmatch(f.name.lower(), pattern.lower()):
                files.append(f)
        return files
    
    def _read_text_file(self, path: Path) -> Optional[str]:
        """Read a text file"""
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            self._log(f"Error reading {path}: {e}")
            return None
    
    def _write_text_file(self, path: Path, content: str):
        """Write a text file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        self._log(f"Created: {path}")
    
    def _parse_ini_file(self, path: Path) -> dict:
        """Parse an INI file"""
        import configparser
        
        config = configparser.ConfigParser()
        try:
            config.read(path)
            # Convert to nested dict
            result = {}
            for section in config.sections():
                result[section] = dict(config.items(section))
            return result
        except Exception as e:
            self._log(f"Error parsing INI file {path}: {e}")
            return {}
