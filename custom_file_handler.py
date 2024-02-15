from pathlib import Path
import yaml
from connexion.json_schema import ExtendedSafeLoader

class CustomFileHandler:
    def __init__(self, base_dir):
        self.base_dir = base_dir
    
    """Handler to resolve file refs."""
    def __call__(self, uri):
        path = Path(self.base_dir).resolve()
        with open(path) as fh:
            return yaml.load(fh, ExtendedSafeLoader)
