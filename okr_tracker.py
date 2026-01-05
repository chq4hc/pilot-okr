"""
OKR Tracker Module

This module provides progress tracking and health monitoring capabilities for OKRs.
Implements tracking logic similar to Microsoft Viva Goals.

Author: OKR Team
Date: January 2026
"""

import datetime
import logging
from enum import Enum
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ============================================================================
# Status Enums
# ============================================================================

class OKRStatus(str, Enum):
    """Status labels for OKR progress tracking."""
    ON_TRACK = "On Track"
    BEHIND = "Behind"
    AT_RISK = "At Risk"
    POSTPONED = "Postponed"
    CLOSED = "Closed"


class AlertLevel(str, Enum):
    """Alert severity levels."""
    CRITICAL = "Critical"
    AT_RISK = "At Risk"
    NEEDS_ATTENTION = "Needs Attention"
    INFO = "Info"


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class ProgressSnapshot:
    """Snapshot of OKR progress at a point in time."""
    date: datetime.date
    actual_value: float
    actual_percent: float
    expected_percent: float
    status: OKRStatus
    notes: Optional[str] = None


@dataclass
class HealthAlert:
    """Health alert for OKR tracking."""
    level: AlertLevel
    message: str
    severity_score: int  # 0-10, higher is more severe


# ============================================================================
# Key Result Tracker
# ============================================================================

class KeyResultTracker:
    """Tracks progress for a single Key Result."""
    
    def __init__(
        self,
        text: str,
        baseline: float,
        target: float,
        deadline: datetime.date,
        owner: Optional[str] = None,
        parent_okr: Optional['OKRTracker'] = None
    ):
        """
        Initialize Key Result tracker.
        
        Args:
            text: Description of the key result
            baseline: Starting value
            target: Target value
            deadline: Due date
            owner: Person responsible
            parent_okr: Reference to parent OKRTracker for auto-update
        """
        self.text = text
        self.baseline = baseline
        self.target = target
        self.deadline = deadline
        self.owner = owner
        self.current_value = baseline
        self.history: List[ProgressSnapshot] = []
        self.parent_okr = parent_okr  # Link to parent OKR
        
        logger.info(f"Initialized KR tracker: {text}")
    
    def update_progress(
        self,
        value: float,
        date: Optional[datetime.date] = None,
        notes: Optional[str] = None,
        auto_update_parent: bool = True
    ) -> None:
        """
        Update the current progress value and automatically update parent OKR.
        
        Args:
            value: New progress value
            date: Date of update (defaults to today)
            notes: Optional notes about the update
            auto_update_parent: If True, automatically update parent OKR progress
        """
        date = date or datetime.date.today()
        self.current_value = value
        
        # Record snapshot
        snapshot = ProgressSnapshot(
            date=date,
            actual_value=value,
            actual_percent=self.get_progress_percent(),
            expected_percent=self.calculate_expected_progress(date),
            status=self.derive_status(date),
            notes=notes
        )
        self.history.append(snapshot)
        
        logger.info(f"Updated KR progress: {self.text} = {value} ({snapshot.actual_percent:.1f}%)")
        
        # Auto-update parent OKR if linked
        if auto_update_parent and self.parent_okr:
            self.parent_okr.update_from_key_results(date=date)
    
    def get_progress_percent(self) -> float:
        """Calculate current progress as percentage."""
        if self.target == self.baseline:
            return 100.0 if self.current_value >= self.target else 0.0
        
        progress = ((self.current_value - self.baseline) / (self.target - self.baseline)) * 100
        return max(0.0, min(100.0, progress))
    
    def calculate_expected_progress(
        self,
        current_date: Optional[datetime.date] = None
    ) -> float:
        """
        Calculate expected progress based on time elapsed.
        
        Args:
            current_date: Date to calculate for (defaults to today)
        
        Returns:
            Expected progress percentage (0-100)
        """
        # For this implementation, we need a start date
        # We'll use 3 months before deadline as default
        start_date = self.deadline - datetime.timedelta(days=90)
        current_date = current_date or datetime.date.today()
        
        total_duration = (self.deadline - start_date).days
        elapsed_duration = (current_date - start_date).days
        
        if elapsed_duration <= 0:
            return 0.0
        if elapsed_duration >= total_duration:
            return 100.0
        
        return (elapsed_duration / total_duration) * 100
    
    def derive_status(
        self,
        current_date: Optional[datetime.date] = None
    ) -> OKRStatus:
        """
        Determine current status based on progress vs expected.
        
        Logic:
        - At Risk: (Expected - Actual) > 25%
        - Behind: (Expected - Actual) > 0% and <= 25%
        - On Track: (Actual >= Expected)
        
        Args:
            current_date: Date to evaluate (defaults to today)
        
        Returns:
            OKRStatus enum value
        """
        actual = self.get_progress_percent()
        expected = self.calculate_expected_progress(current_date)
        diff = expected - actual
        
        if diff > 25:
            return OKRStatus.AT_RISK
        elif 0 < diff <= 25:
            return OKRStatus.BEHIND
        else:
            return OKRStatus.ON_TRACK
    
    def get_summary(self) -> Dict:
        """Get a summary of current status."""
        return {
            "text": self.text,
            "owner": self.owner,
            "baseline": self.baseline,
            "target": self.target,
            "current": self.current_value,
            "progress_percent": self.get_progress_percent(),
            "status": self.derive_status().value,
            "deadline": self.deadline.isoformat(),
            "updates_count": len(self.history)
        }


# ============================================================================
# OKR Tracker
# ============================================================================

class OKRTracker:
    """
    Track progress and health for an Objective and its Key Results.
    
    Implements tracking logic similar to Microsoft Viva Goals.
    """
    
    # Threshold constants
    RISK_THRESHOLD = 25.0  # Progress gap % for "At Risk"
    HIGH_SCORE_THRESHOLD = 80.0  # Threshold for "too easy" warning
    
    def __init__(
        self,
        name: str,
        start_date: datetime.date,
        end_date: datetime.date,
        initial_value: float = 0,
        target_value: float = 100
    ):
        """
        Initialize OKR tracker.
        
        Args:
            name: Name/description of the objective
            start_date: Start date of the OKR period
            end_date: End date/deadline
            initial_value: Starting progress value
            target_value: Target value to achieve
        """
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.initial_value = initial_value
        self.target_value = target_value
        self.actual_value = initial_value
        self.key_results: List[KeyResultTracker] = []
        self.history: List[ProgressSnapshot] = []
        self.status = OKRStatus.ON_TRACK
        
        logger.info(f"Initialized OKR tracker: {name} ({start_date} to {end_date})")
    
    def add_key_result(self, kr: KeyResultTracker) -> None:
        """
        Add a Key Result to track and link it to this OKR.
        
        Args:
            kr: KeyResultTracker instance
        """
        # Link the KR to this OKR for auto-updates
        kr.parent_okr = self
        self.key_results.append(kr)
        logger.info(f"Added KR to {self.name}: {kr.text}")
    
    def update_progress(
        self,
        value: float,
        date: Optional[datetime.date] = None,
        notes: Optional[str] = None
    ) -> None:
        """
        Update objective-level progress manually.
        
        Note: Progress is typically auto-calculated from key results.
        Use this method only for manual override.
        
        Args:
            value: New progress value
            date: Date of update (defaults to today)
            notes: Optional notes
        """
        date = date or datetime.date.today()
        self.actual_value = value
        self.status = self.derive_status(date)
        
        # Record snapshot
        snapshot = ProgressSnapshot(
            date=date,
            actual_value=value,
            actual_percent=self.get_actual_progress_percent(),
            expected_percent=self.calculate_expected_progress(date),
            status=self.status,
            notes=notes
        )
        self.history.append(snapshot)
        
        logger.info(
            f"Updated OKR progress: {self.name} = {value} "
            f"({snapshot.actual_percent:.1f}%, {self.status.value})"
        )
    
    def update_from_key_results(
        self,
        date: Optional[datetime.date] = None,
        notes: Optional[str] = None
    ) -> None:
        """
        Automatically update OKR progress based on Key Results progress.
        
        This method calculates the average progress of all key results
        and updates the OKR accordingly.
        
        Args:
            date: Date of update (defaults to today)
            notes: Optional notes
        """
        if not self.key_results:
            logger.warning(f"No key results to calculate progress for {self.name}")
            return
        
        date = date or datetime.date.today()
        
        # Calculate average progress from all key results
        kr_progress_percentages = [kr.get_progress_percent() for kr in self.key_results]
        avg_progress_percent = sum(kr_progress_percentages) / len(kr_progress_percentages)
        
        # Convert percentage to actual value
        delta = self.target_value - self.initial_value
        new_actual_value = self.initial_value + (delta * avg_progress_percent / 100)
        
        # Update the OKR
        self.actual_value = new_actual_value
        self.status = self.derive_status(date)
        
        # Record snapshot
        snapshot = ProgressSnapshot(
            date=date,
            actual_value=new_actual_value,
            actual_percent=self.get_actual_progress_percent(),
            expected_percent=self.calculate_expected_progress(date),
            status=self.status,
            notes=notes or f"Auto-updated from {len(self.key_results)} key results"
        )
        self.history.append(snapshot)
        
        logger.info(
            f"Auto-updated OKR progress from KRs: {self.name} = {new_actual_value:.1f} "
            f"({snapshot.actual_percent:.1f}%, {self.status.value})"
        )
    
    def calculate_expected_progress(
        self,
        current_date: Optional[datetime.date] = None
    ) -> float:
        """
        Calculate expected progress percentage based on time elapsed.
        
        Args:
            current_date: Date to calculate for (defaults to today)
        
        Returns:
            Expected progress percentage (0-100)
        """
        if not current_date:
            current_date = datetime.date.today()
        
        total_duration = (self.end_date - self.start_date).days
        elapsed_duration = (current_date - self.start_date).days
        
        if elapsed_duration <= 0:
            return 0.0
        if elapsed_duration >= total_duration:
            return 100.0
        
        return (elapsed_duration / total_duration) * 100
    
    def get_actual_progress_percent(self) -> float:
        """
        Calculate actual progress percentage.
        
        Returns:
            Actual progress percentage (0-100)
        """
        total_delta = self.target_value - self.initial_value
        current_delta = self.actual_value - self.initial_value
        
        if total_delta == 0:
            return 0.0
        
        progress = (current_delta / total_delta) * 100
        return max(0.0, min(100.0, progress))
    
    def derive_status(
        self,
        current_date: Optional[datetime.date] = None
    ) -> OKRStatus:
        """
        Determine status based on progress vs expected.
        
        Logic from Microsoft Viva Goals:
        - At Risk: (Expected - Actual) > 25%
        - Behind: (Expected - Actual) > 0% and <= 25%
        - On Track: (Actual >= Expected)
        
        Args:
            current_date: Date to evaluate (defaults to today)
        
        Returns:
            OKRStatus enum value
        """
        actual = self.get_actual_progress_percent()
        expected = self.calculate_expected_progress(current_date)
        diff = expected - actual
        
        if diff > self.RISK_THRESHOLD:
            return OKRStatus.AT_RISK
        elif 0 < diff <= self.RISK_THRESHOLD:
            return OKRStatus.BEHIND
        else:
            return OKRStatus.ON_TRACK
    
    def get_health_alerts(
        self,
        current_date: Optional[datetime.date] = None
    ) -> List[HealthAlert]:
        """
        Get health alerts based on tracking data.
        
        Implements Viva Goals 'Needs Attention' and 'At Risk' alerts.
        
        Args:
            current_date: Date to evaluate (defaults to today)
        
        Returns:
            List of HealthAlert objects
        """
        alerts = []
        actual = self.get_actual_progress_percent()
        expected = self.calculate_expected_progress(current_date)
        today = current_date or datetime.date.today()
        
        # Alert 1: Past due date
        if today > self.end_date and actual < 100:
            alerts.append(HealthAlert(
                level=AlertLevel.CRITICAL,
                message="Objective is past its due date and not completed.",
                severity_score=10
            ))
        
        # Alert 2: Significant progress gap
        gap = expected - actual
        if gap > self.RISK_THRESHOLD:
            alerts.append(HealthAlert(
                level=AlertLevel.AT_RISK,
                message=f"Progress is off by {gap:.1f}% from expected.",
                severity_score=8
            ))
        elif 0 < gap <= self.RISK_THRESHOLD:
            alerts.append(HealthAlert(
                level=AlertLevel.NEEDS_ATTENTION,
                message=f"Progress is {gap:.1f}% behind expected.",
                severity_score=5
            ))
        
        # Alert 3: Score too high (goal not ambitious enough)
        if actual > self.HIGH_SCORE_THRESHOLD and today < self.end_date:
            alerts.append(HealthAlert(
                level=AlertLevel.NEEDS_ATTENTION,
                message=f"Progress ({actual:.1f}%) is unusually high. Consider setting more ambitious goals.",
                severity_score=3
            ))
        
        # Alert 4: No Key Results
        if not self.key_results:
            alerts.append(HealthAlert(
                level=AlertLevel.NEEDS_ATTENTION,
                message="Objective has no key results defined. Alignment unclear.",
                severity_score=6
            ))
        
        # Alert 5: Key Results at risk
        at_risk_krs = [
            kr for kr in self.key_results
            if kr.derive_status(today) == OKRStatus.AT_RISK
        ]
        if at_risk_krs:
            alerts.append(HealthAlert(
                level=AlertLevel.AT_RISK,
                message=f"{len(at_risk_krs)} key result(s) are at risk.",
                severity_score=7
            ))
        
        # Sort alerts by severity (highest first)
        alerts.sort(key=lambda x: x.severity_score, reverse=True)
        
        return alerts
    
    def get_summary(self) -> Dict:
        """
        Get a comprehensive summary of the OKR status.
        
        Returns:
            Dictionary with summary information
        """
        today = datetime.date.today()
        alerts = self.get_health_alerts(today)
        
        # Calculate KR statistics
        kr_summaries = [kr.get_summary() for kr in self.key_results]
        kr_statuses = [kr.derive_status(today) for kr in self.key_results]
        
        return {
            "name": self.name,
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat(),
                "days_remaining": (self.end_date - today).days
            },
            "progress": {
                "actual_percent": self.get_actual_progress_percent(),
                "expected_percent": self.calculate_expected_progress(today),
                "actual_value": self.actual_value,
                "target_value": self.target_value
            },
            "status": self.status.value,
            "key_results": {
                "count": len(self.key_results),
                "on_track": kr_statuses.count(OKRStatus.ON_TRACK),
                "behind": kr_statuses.count(OKRStatus.BEHIND),
                "at_risk": kr_statuses.count(OKRStatus.AT_RISK),
                "details": kr_summaries
            },
            "alerts": [
                {
                    "level": alert.level.value,
                    "message": alert.message,
                    "severity": alert.severity_score
                }
                for alert in alerts
            ],
            "update_count": len(self.history)
        }
    
    def get_progress_trend(self, days: int = 30) -> List[Tuple[datetime.date, float]]:
        """
        Get progress trend over recent days.
        
        Args:
            days: Number of recent days to include
        
        Returns:
            List of (date, progress_percent) tuples
        """
        cutoff_date = datetime.date.today() - datetime.timedelta(days=days)
        recent_snapshots = [
            (s.date, s.actual_percent)
            for s in self.history
            if s.date >= cutoff_date
        ]
        return recent_snapshots


# ============================================================================
# JSON Loading Functions
# ============================================================================

def create_tracker_from_json(
    json_data: Dict,
    start_date: datetime.date,
    end_date: datetime.date
) -> OKRTracker:
    """
    Create OKRTracker and KeyResultTracker instances from JSON data.
    
    Args:
        json_data: Dictionary containing OKR data with 'objective' and 'key_results'
        start_date: Start date for the OKR period
        end_date: End date/deadline for the OKR
    
    Returns:
        OKRTracker instance with KeyResultTracker instances added
    
    Example JSON structure:
        {
            "objective": "Increase revenue by 50%",
            "key_results": [
                {
                    "text": "Acquire 100 new customers",
                    "baseline": "0",
                    "target": "100", 
                    "deadline": "2026-03-31",
                    "owner": "Sales Team"
                }
            ]
        }
    """
    # Create OKR tracker
    objective_text = json_data.get("objective", "Unnamed Objective")
    tracker = OKRTracker(
        name=objective_text,
        start_date=start_date,
        end_date=end_date,
        initial_value=0,
        target_value=100
    )
    
    # Process key results
    key_results = json_data.get("key_results", [])
    
    for kr_data in key_results:
        try:
            # Extract KR data
            text = kr_data.get("text", "Unnamed Key Result")
            baseline = _parse_numeric_value(kr_data.get("baseline", "0"))
            target = _parse_numeric_value(kr_data.get("target", "100"))
            owner = kr_data.get("owner")
            
            # Parse deadline
            deadline_str = kr_data.get("deadline")
            if deadline_str:
                kr_deadline = _parse_date(deadline_str, default=end_date)
            else:
                kr_deadline = end_date
            
            # Create and add KR tracker
            kr_tracker = KeyResultTracker(
                text=text,
                baseline=baseline,
                target=target,
                deadline=kr_deadline,
                owner=owner
            )
            
            tracker.add_key_result(kr_tracker)
            
        except Exception as e:
            logger.warning(f"Failed to create tracker for KR '{kr_data.get('text', 'unknown')}': {e}")
            continue
    
    logger.info(
        f"Created OKR tracker '{objective_text}' with {len(tracker.key_results)} key results"
    )
    
    return tracker


def load_tracker_from_json_file(
    file_path: str,
    start_date: datetime.date,
    end_date: datetime.date
) -> OKRTracker:
    """
    Load OKR tracker from a JSON file.
    
    Args:
        file_path: Path to JSON file
        start_date: Start date for the OKR period
        end_date: End date/deadline for the OKR
    
    Returns:
        OKRTracker instance
    """
    import json
    from pathlib import Path
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    return create_tracker_from_json(json_data, start_date, end_date)


def _parse_numeric_value(value: any) -> float:
    """
    Parse a value to float, handling various formats.
    
    Args:
        value: Value to parse (can be string, int, float)
    
    Returns:
        Parsed float value
    """
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove common non-numeric characters
        cleaned = value.strip().lower()
        
        # Handle special cases
        if cleaned in ("none", "n/a", "na", "null", ""):
            return 0.0
        
        # Extract numeric part
        import re
        numeric_match = re.search(r'-?\d+\.?\d*', cleaned)
        if numeric_match:
            return float(numeric_match.group())
    
    # Default fallback
    return 0.0


def _parse_date(date_str: str, default: datetime.date) -> datetime.date:
    """
    Parse a date string to datetime.date.
    
    Supports formats:
    - ISO format: "2026-03-31"
    - Common formats: "March 31, 2026", "31/03/2026", "Q1 2026"
    
    Args:
        date_str: Date string to parse
        default: Default date if parsing fails
    
    Returns:
        Parsed date or default
    """
    if not date_str:
        return default
    
    date_str = date_str.strip()
    
    # Try ISO format first
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass
    
    # Try common formats
    formats = [
        "%B %d, %Y",     # March 31, 2026
        "%d/%m/%Y",      # 31/03/2026
        "%m/%d/%Y",      # 03/31/2026
        "%Y/%m/%d",      # 2026/03/31
        "%d-%m-%Y",      # 31-03-2026
    ]
    
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    # Handle quarter formats (Q1 2026, Q2 2026, etc.)
    import re
    quarter_match = re.match(r'Q(\d)\s*(\d{4})', date_str, re.IGNORECASE)
    if quarter_match:
        quarter = int(quarter_match.group(1))
        year = int(quarter_match.group(2))
        
        # Map quarter to end month
        quarter_end_month = {1: 3, 2: 6, 3: 9, 4: 12}
        month = quarter_end_month.get(quarter, 3)
        
        # Get last day of the month
        if month == 12:
            return datetime.date(year, 12, 31)
        else:
            next_month = datetime.date(year, month + 1, 1)
            return next_month - datetime.timedelta(days=1)
    
    # If all parsing fails, return default
    logger.warning(f"Could not parse date '{date_str}', using default: {default}")
    return default


# ============================================================================
# Utility Functions
# ============================================================================

def calculate_okr_health_score(tracker: OKRTracker) -> Tuple[int, str]:
    """
    Calculate overall health score for an OKR.
    
    Args:
        tracker: OKRTracker instance
    
    Returns:
        Tuple of (score 0-100, description)
    """
    alerts = tracker.get_health_alerts()
    actual = tracker.get_actual_progress_percent()
    expected = tracker.calculate_expected_progress()
    
    # Start with base score of 100
    score = 100
    
    # Deduct points for alerts
    for alert in alerts:
        score -= alert.severity_score
    
    # Deduct points based on progress gap
    gap = expected - actual
    if gap > 0:
        score -= min(30, gap)  # Max 30 point deduction for gap
    
    # Ensure score is in valid range
    score = max(0, min(100, score))
    
    # Determine description
    if score >= 80:
        description = "Excellent - On track with no major concerns"
    elif score >= 60:
        description = "Good - Minor attention needed"
    elif score >= 40:
        description = "Fair - Requires attention and action"
    elif score >= 20:
        description = "Poor - Significant issues need addressing"
    else:
        description = "Critical - Immediate intervention required"
    
    return score, description


def format_tracker_report(tracker: OKRTracker) -> str:
    """
    Format a tracker summary as a readable report.
    
    Args:
        tracker: OKRTracker instance
    
    Returns:
        Formatted string report
    """
    summary = tracker.get_summary()
    health_score, health_desc = calculate_okr_health_score(tracker)
    
    report = f"""
OKR TRACKING REPORT
{'='*60}

Objective: {summary['name']}
Period: {summary['period']['start']} to {summary['period']['end']}
Days Remaining: {summary['period']['days_remaining']}

PROGRESS
--------
Actual:   {summary['progress']['actual_percent']:.1f}% ({summary['progress']['actual_value']}/{summary['progress']['target_value']})
Expected: {summary['progress']['expected_percent']:.1f}%
Status:   {summary['status']}

HEALTH SCORE: {health_score}/100 - {health_desc}

KEY RESULTS ({summary['key_results']['count']})
-----------
On Track: {summary['key_results']['on_track']}
Behind:   {summary['key_results']['behind']}
At Risk:  {summary['key_results']['at_risk']}

ALERTS ({len(summary['alerts'])})
------
"""
    
    if summary['alerts']:
        for i, alert in enumerate(summary['alerts'], 1):
            report += f"{i}. [{alert['level']}] {alert['message']}\n"
    else:
        report += "No alerts - Everything looks good!\n"
    
    return report


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example 1: Create and track an OKR manually
    start = datetime.date(2026, 1, 1)
    end = datetime.date(2026, 3, 31)
    
    # Create objective tracker
    okr = OKRTracker(
        name="Launch Version 3.0 Product",
        start_date=start,
        end_date=end,
        initial_value=0,
        target_value=100
    )
    
    # Add key results
    kr1 = KeyResultTracker(
        text="Complete 50 user interviews",
        baseline=0,
        target=50,
        deadline=end,
        owner="Research Team"
    )
    kr2 = KeyResultTracker(
        text="Achieve 90% test coverage",
        baseline=65,
        target=90,
        deadline=end,
        owner="QA Team"
    )
    
    okr.add_key_result(kr1)
    okr.add_key_result(kr2)
    
    # Simulate progress update (KR updates will auto-update OKR)
    print("\n📝 Updating Key Results...")
    kr1.update_progress(10)
    print(f"KR1 updated → OKR now at: {okr.get_actual_progress_percent():.1f}%")
    
    kr2.update_progress(72)
    print(f"KR2 updated → OKR now at: {okr.get_actual_progress_percent():.1f}%")
    
    # Get report
    print(format_tracker_report(okr))
    
    # Check health
    alerts = okr.get_health_alerts()
    print(f"\nFound {len(alerts)} alert(s):")
    for alert in alerts:
        print(f"  [{alert.level.value}] {alert.message}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Demonstrate manual update of multiple KRs
    print("📊 Batch Update Example:")
    kr1.update_progress(25, notes="Week 2 progress")
    kr2.update_progress(85, notes="Testing sprint complete")
    print(f"Final OKR Progress: {okr.get_actual_progress_percent():.1f}%")
    print(f"Final OKR Status: {okr.status.value}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 3: Create tracker from JSON
    json_data = {
        "objective": "Double sales over the next two years",
        "key_results": [
            {
                "text": "Identify a new ICP (Ideal Customer Profile) to target",
                "baseline": "0",
                "target": "1",
                "deadline": "Q4 2026",
                "owner": "Product Manager"
            },
            {
                "text": "Boost engagement on digital platforms",
                "baseline": "1000",
                "target": "1250",
                "deadline": "2026-03-31",
                "owner": "Marketing Team"
            },
            {
                "text": "Expand the sales team",
                "baseline": "10",
                "target": "13",
                "deadline": "2026-06-30",
                "owner": "HR Manager"
            }
        ]
    }
    
    print("\nCreating tracker from JSON...")
    tracker_from_json = create_tracker_from_json(
        json_data,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 12, 31)
    )
    
    print(f"\nCreated: {tracker_from_json.name}")
    print(f"Key Results: {len(tracker_from_json.key_results)}")
    for i, kr in enumerate(tracker_from_json.key_results, 1):
        print(f"  {i}. {kr.text} ({kr.baseline} → {kr.target})")
