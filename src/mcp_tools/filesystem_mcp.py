"""File System MCP Tool for logging case files and evidence."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from src.config import CASE_FILES_DIR


class FileSystemMCP:
    """MCP tool for managing case files and evidence logging."""
    
    def __init__(self, case_files_dir: Path = CASE_FILES_DIR):
        self.case_files_dir = case_files_dir
        self.case_files_dir.mkdir(exist_ok=True)
        self.current_case_id: Optional[str] = None
        self.current_case_file: Optional[Path] = None
    
    def create_case_file(self, case_id: str, initial_data: Dict[str, Any]) -> Path:
        """
        Create a new case file for an investigation.
        
        Args:
            case_id: Unique identifier for the case
            initial_data: Initial case information
            
        Returns:
            Path to the created case file
        """
        self.current_case_id = case_id
        timestamp = datetime.now().isoformat()
        
        case_data = {
            'case_id': case_id,
            'created_at': timestamp,
            'status': 'investigating',
            'evidence': [],
            'timeline': [],
            'initial_data': initial_data
        }
        
        case_filename = f"case_{case_id}_{timestamp.replace(':', '-').split('.')[0]}.json"
        self.current_case_file = self.case_files_dir / case_filename
        
        self._write_case_file(case_data)
        self._log_event("case_created", {"case_id": case_id})
        
        return self.current_case_file
    
    def log_evidence(self, evidence_type: str, evidence_data: Dict[str, Any], 
                    source: str = "unknown") -> None:
        """
        Log evidence to the current case file.
        
        Args:
            evidence_type: Type of evidence (e.g., 'domain_check', 'scam_db_lookup')
            evidence_data: The evidence data
            source: Source of the evidence
        """
        if not self.current_case_file:
            raise ValueError("No active case file. Create a case file first.")
        
        case_data = self._read_case_file()
        
        evidence_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': evidence_type,
            'source': source,
            'data': evidence_data
        }
        
        case_data['evidence'].append(evidence_entry)
        case_data['timeline'].append({
            'timestamp': datetime.now().isoformat(),
            'event': f"Evidence collected: {evidence_type}",
            'source': source
        })
        
        self._write_case_file(case_data)
    
    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Log an event to the case timeline.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        self._log_event(event_type, event_data)
    
    def finalize_case(self, verdict: str, risk_score: float, 
                     summary: str, recommendations: List[str]) -> Dict[str, Any]:
        """
        Finalize the case with verdict and summary.
        
        Args:
            verdict: Final verdict (safe/suspicious/scam)
            risk_score: Risk score (0-100)
            summary: Case summary
            recommendations: List of recommendations
            
        Returns:
            Final case data
        """
        if not self.current_case_file:
            raise ValueError("No active case file.")
        
        case_data = self._read_case_file()
        case_data['status'] = 'completed'
        case_data['completed_at'] = datetime.now().isoformat()
        case_data['verdict'] = verdict
        case_data['risk_score'] = risk_score
        case_data['summary'] = summary
        case_data['recommendations'] = recommendations
        
        self._write_case_file(case_data)
        
        return case_data
    
    def _log_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Internal method to log events."""
        if not self.current_case_file:
            return
        
        case_data = self._read_case_file()
        case_data['timeline'].append({
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'data': event_data
        })
        self._write_case_file(case_data)
    
    def _read_case_file(self) -> Dict[str, Any]:
        """Read the current case file."""
        if not self.current_case_file or not self.current_case_file.exists():
            raise ValueError("Case file does not exist.")
        
        with open(self.current_case_file, 'r') as f:
            return json.load(f)
    
    def _write_case_file(self, case_data: Dict[str, Any]) -> None:
        """Write to the current case file."""
        if not self.current_case_file:
            raise ValueError("No active case file.")
        
        with open(self.current_case_file, 'w') as f:
            json.dump(case_data, f, indent=2)
    
    def get_case_summary(self) -> Dict[str, Any]:
        """Get summary of the current case."""
        if not self.current_case_file:
            return {}
        
        case_data = self._read_case_file()
        return {
            'case_id': case_data.get('case_id'),
            'status': case_data.get('status'),
            'evidence_count': len(case_data.get('evidence', [])),
            'verdict': case_data.get('verdict'),
            'risk_score': case_data.get('risk_score')
        }

