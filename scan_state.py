"""Scanner state and scan context management."""

import threading
import time

class ScanState:
    """Track scanner state during scans."""
    
    def __init__(self):
        self.is_scanning = False
        self.progress = 0
        self.total = 0
        self.lock = threading.Lock()
    
    def status(self) -> dict:
        """Get current scan status."""
        with self.lock:
            return {
                "scanning": self.is_scanning,
                "progress": self.progress,
                "total": self.total,
            }
    
    def start_scan(self, total: int):
        """Mark scan as started."""
        with self.lock:
            self.is_scanning = True
            self.progress = 0
            self.total = total
    
    def update_progress(self, count: int):
        """Update scan progress."""
        with self.lock:
            self.progress = count
    
    def finish_scan(self):
        """Mark scan as finished."""
        with self.lock:
            self.is_scanning = False

scan_state = ScanState()
