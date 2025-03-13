import logging
from typing import Optional
from pathlib import Path


class DocstraLogger:
    """Logger for Docstra with support for log level and file output."""

    def __init__(self, log_level: Optional[str] = None, log_file: Optional[str] = None):
        """Initialize the logger.
        
        Args:
            log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional path to a log file
        """
        self.logger = logging.getLogger("docstra")
        
        # Clear existing handlers to avoid duplicates
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        # Set up formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Set up file handler if log_file is specified
        if log_file:
            # Ensure parent directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Set log level (default to INFO if not specified)
        level = self._parse_log_level(log_level) if log_level else logging.INFO
        self.logger.setLevel(level)
    
    def _parse_log_level(self, log_level: str) -> int:
        """Parse string log level to logging constant.
        
        Args:
            log_level: String representation of log level
            
        Returns:
            Logging level constant
        """
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(log_level.upper(), logging.INFO)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)
