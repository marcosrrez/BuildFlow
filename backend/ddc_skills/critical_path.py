import pandas as pd
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from collections import defaultdict


class ActivityStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"


@dataclass
class Activity:
    activity_id: str
    name: str
    duration: int  # days
    predecessors: List[str]
    early_start: int = 0
    early_finish: int = 0
    late_start: int = 0
    late_finish: int = 0
    total_float: int = 0
    free_float: int = 0
    is_critical: bool = False
    status: ActivityStatus = ActivityStatus.NOT_STARTED
    percent_complete: float = 0
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None


@dataclass
class CriticalPathResult:
    critical_path: List[str]
    project_duration: int
    activities: Dict[str, Activity]
    near_critical: List[str]  # Float < 5 days
    total_float_days: int


class CriticalPathAnalyzer:
    """Analyze project critical path."""

    NEAR_CRITICAL_THRESHOLD = 5  # days

    def __init__(self, project_start: date):
        self.project_start = project_start
        self.activities: Dict[str, Activity] = {}

    def add_activity(self,
                     activity_id: str,
                     name: str,
                     duration: int,
                     predecessors: List[str] = None):
        """Add activity to network."""

        self.activities[activity_id] = Activity(
            activity_id=activity_id,
            name=name,
            duration=duration,
            predecessors=predecessors or []
        )

    def import_from_dataframe(self, df: pd.DataFrame):
        """Import activities from DataFrame."""
        for _, row in df.iterrows():
            preds = row.get('predecessors', '')
            if pd.isna(preds):
                pred_list = []
            else:
                pred_list = [p.strip() for p in str(preds).split(',') if p.strip()]

            self.add_activity(
                activity_id=str(row['activity_id']),
                name=row['name'],
                duration=int(row['duration']),
                predecessors=pred_list
            )

    def _forward_pass(self):
        """Calculate early start and early finish (forward pass)."""

        # Topological sort
        sorted_activities = self._topological_sort()

        for activity_id in sorted_activities:
            activity = self.activities[activity_id]

            # Early start = max(early finish of all predecessors)
            if not activity.predecessors:
                activity.early_start = 0
            else:
                activity.early_start = max(
                    self.activities[pred].early_finish
                    for pred in activity.predecessors
                    if pred in self.activities
                )

            activity.early_finish = activity.early_start + activity.duration

    def _backward_pass(self):
        """Calculate late start and late finish (backward pass)."""

        # Find project duration
        project_duration = max(a.early_finish for a in self.activities.values())

        # Build successors map
        successors = defaultdict(list)
        for activity_id, activity in self.activities.items():
            for pred in activity.predecessors:
                if pred in self.activities:
                    successors[pred].append(activity_id)

        # Reverse topological order
        sorted_activities = self._topological_sort()[::-1]

        for activity_id in sorted_activities:
            activity = self.activities[activity_id]

            # Late finish = min(late start of all successors)
            if activity_id not in successors or not successors[activity_id]:
                activity.late_finish = project_duration
            else:
                activity.late_finish = min(
                    self.activities[succ].late_start
                    for succ in successors[activity_id]
                )

            activity.late_start = activity.late_finish - activity.duration

            # Calculate floats
            activity.total_float = activity.late_start - activity.early_start
            activity.is_critical = activity.total_float == 0

    def _topological_sort(self) -> List[str]:
        """Topological sort of activities."""

        visited = set()
        result = []

        def visit(activity_id: str):
            if activity_id in visited:
                return
            visited.add(activity_id)

            activity = self.activities.get(activity_id)
            if activity:
                for pred in activity.predecessors:
                    if pred in self.activities:
                        visit(pred)
                result.append(activity_id)

        for activity_id in self.activities:
            visit(activity_id)

        return result

    def calculate_critical_path(self) -> CriticalPathResult:
        """Calculate critical path and all float values."""

        self._forward_pass()
        self._backward_pass()

        # Find critical path
        critical_activities = [
            a.activity_id for a in self.activities.values()
            if a.is_critical
        ]

        # Near-critical activities
        near_critical = [
            a.activity_id for a in self.activities.values()
            if 0 < a.total_float <= self.NEAR_CRITICAL_THRESHOLD
        ]

        project_duration = max(a.early_finish for a in self.activities.values())
        total_float = sum(a.total_float for a in self.activities.values())

        return CriticalPathResult(
            critical_path=critical_activities,
            project_duration=project_duration,
            activities=self.activities,
            near_critical=near_critical,
            total_float_days=total_float
        )

    def get_schedule_dates(self) -> pd.DataFrame:
        """Get schedule with dates."""

        data = []
        for activity in self.activities.values():
            early_start_date = self.project_start + timedelta(days=activity.early_start)
            early_finish_date = self.project_start + timedelta(days=activity.early_finish)
            late_start_date = self.project_start + timedelta(days=activity.late_start)
            late_finish_date = self.project_start + timedelta(days=activity.late_finish)

            data.append({
                'Activity ID': activity.activity_id,
                'Name': activity.name,
                'Duration': activity.duration,
                'Early Start': early_start_date,
                'Early Finish': early_finish_date,
                'Late Start': late_start_date,
                'Late Finish': late_finish_date,
                'Total Float': activity.total_float,
                'Critical': 'Yes' if activity.is_critical else 'No'
            })

        return pd.DataFrame(data)

    def analyze_delay_impact(self,
                             activity_id: str,
                             delay_days: int) -> Dict[str, Any]:
        """Analyze impact of delay on project."""

        activity = self.activities.get(activity_id)
        if not activity:
            return {}

        absorbed_by_float = min(delay_days, activity.total_float)
        project_delay = max(0, delay_days - activity.total_float)

        # Find affected activities
        affected = []
        if project_delay > 0:
            # Activities that could be affected (successors)
            for a in self.activities.values():
                if activity_id in a.predecessors:
                    affected.append(a.activity_id)

        return {
            'activity': activity_id,
            'delay_days': delay_days,
            'available_float': activity.total_float,
            'absorbed_by_float': absorbed_by_float,
            'project_delay': project_delay,
            'affected_activities': affected,
            'is_critical_delay': project_delay > 0
        }

    def suggest_acceleration(self,
                             target_reduction: int) -> List[Dict[str, Any]]:
        """Suggest activities to accelerate to meet target."""

        result = self.calculate_critical_path()
        suggestions = []

        # Focus on critical activities
        for activity_id in result.critical_path:
            activity = self.activities[activity_id]

            # Assume can reduce by 20% max
            max_reduction = int(activity.duration * 0.2)

            if max_reduction > 0:
                suggestions.append({
                    'activity': activity_id,
                    'name': activity.name,
                    'current_duration': activity.duration,
                    'max_reduction': max_reduction,
                    'reason': 'Critical path activity'
                })

        # Sort by potential impact
        return sorted(suggestions, key=lambda x: x['max_reduction'], reverse=True)

    def export_analysis(self, output_path: str) -> str:
        """Export analysis to Excel."""

        result = self.calculate_critical_path()

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary_df = pd.DataFrame([{
                'Project Start': self.project_start,
                'Project Duration': result.project_duration,
                'Project Finish': self.project_start + timedelta(days=result.project_duration),
                'Critical Activities': len(result.critical_path),
                'Near-Critical Activities': len(result.near_critical),
                'Total Float (days)': result.total_float_days
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Schedule
            schedule_df = self.get_schedule_dates()
            schedule_df.to_excel(writer, sheet_name='Schedule', index=False)

            # Critical Path
            critical_df = pd.DataFrame([
                {
                    'Activity': a_id,
                    'Name': self.activities[a_id].name,
                    'Duration': self.activities[a_id].duration
                }
                for a_id in result.critical_path
            ])
            critical_df.to_excel(writer, sheet_name='Critical Path', index=False)

        return output_path
