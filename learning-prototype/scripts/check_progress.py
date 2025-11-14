#!/usr/bin/env python3
"""
Progress Tracker for ML Pipeline Learning Prototype
====================================================

This script helps you track your learning progress across all weeks.
Run it anytime to see what you've completed and what's next.

Usage:
    python check_progress.py            # Show overall progress
    python check_progress.py --week 1   # Show Week 1 progress
    python check_progress.py --report   # Generate detailed report
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# ANSI color codes
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RED = '\033[0;31m'
BOLD = '\033[1m'
NC = '\033[0m'  # No Color


class ProgressTracker:
    """Track learning progress across all weeks."""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.weeks = {
            1: {
                'name': 'Fundamentals & Setup',
                'files': [
                    '1-python-refresher.py',
                    '2-numpy-basics.py',
                    '3-pandas-intro.py',
                    '4-data-structures.py'
                ],
                'exercises': 'exercises/',
                'project': None
            },
            2: {
                'name': 'Data Pipeline',
                'files': [
                    '1-data-loading.py',
                    '2-data-validation.py',
                    '3-feature-engineering.py',
                    '4-preprocessing.py'
                ],
                'exercises': 'exercises/',
                'project': 'data_pipeline.py'
            },
            3: {
                'name': 'Model Training',
                'files': [
                    '1-model-training.py',
                    '2-evaluation.py',
                    '3-cross-validation.py',
                    '4-tuning.py'
                ],
                'exercises': 'exercises/',
                'project': 'training_pipeline.py'
            },
            4: {
                'name': 'MLOps',
                'files': [
                    '1-experiment-tracking.py',
                    '2-deployment.py',
                    '3-monitoring.py',
                    '4-ci-cd.py'
                ],
                'exercises': 'exercises/',
                'project': 'production_system/'
            }
        }

    def check_file_exists(self, week_num, filename):
        """Check if a file exists and has been modified."""
        week_folder = self.base_path / f'week-{week_num}-{self._get_week_slug(week_num)}'
        file_path = week_folder / filename

        if not file_path.exists():
            return {'exists': False, 'modified': False, 'size': 0}

        stat = file_path.stat()
        # Consider "modified" if file is > 1KB (has content beyond template)
        is_modified = stat.st_size > 1024

        return {
            'exists': True,
            'modified': is_modified,
            'size': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime)
        }

    def _get_week_slug(self, week_num):
        """Get URL-friendly week name."""
        slugs = {
            1: 'basics',
            2: 'data-pipeline',
            3: 'model-training',
            4: 'mlops'
        }
        return slugs.get(week_num, '')

    def get_week_progress(self, week_num):
        """Calculate progress for a specific week."""
        if week_num not in self.weeks:
            return None

        week_data = self.weeks[week_num]
        total_files = len(week_data['files'])
        completed_files = 0

        file_status = []
        for filename in week_data['files']:
            status = self.check_file_exists(week_num, filename)
            if status['modified']:
                completed_files += 1
            file_status.append((filename, status))

        progress_pct = (completed_files / total_files * 100) if total_files > 0 else 0

        return {
            'week': week_num,
            'name': week_data['name'],
            'total_files': total_files,
            'completed_files': completed_files,
            'progress_pct': progress_pct,
            'file_status': file_status
        }

    def print_week_progress(self, week_num, detailed=False):
        """Print progress for a specific week."""
        progress = self.get_week_progress(week_num)
        if not progress:
            print(f"{RED}Week {week_num} not found{NC}")
            return

        # Header
        print(f"\n{BOLD}{BLUE}Week {week_num}: {progress['name']}{NC}")
        print("=" * 60)

        # Progress bar
        completed = progress['completed_files']
        total = progress['total_files']
        pct = progress['progress_pct']

        bar_length = 40
        filled = int(bar_length * pct / 100)
        bar = '█' * filled + '░' * (bar_length - filled)

        color = GREEN if pct == 100 else YELLOW if pct > 50 else RED
        print(f"Progress: {color}{bar}{NC} {pct:.0f}% ({completed}/{total} files)")

        # File status
        if detailed:
            print(f"\n{BOLD}Files:{NC}")
            for filename, status in progress['file_status']:
                if status['modified']:
                    icon = f"{GREEN}✓{NC}"
                    size_kb = status['size'] / 1024
                    mod_time = status['modified_time'].strftime('%Y-%m-%d %H:%M')
                    print(f"  {icon} {filename} ({size_kb:.1f}KB, modified: {mod_time})")
                elif status['exists']:
                    print(f"  {YELLOW}○{NC} {filename} (not started)")
                else:
                    print(f"  {RED}✗{NC} {filename} (missing)")

    def print_overall_progress(self):
        """Print progress across all weeks."""
        print(f"\n{BOLD}{BLUE}╔═══════════════════════════════════════════════════════════════╗{NC}")
        print(f"{BOLD}{BLUE}║         ML Pipeline Learning - Progress Dashboard             ║{NC}")
        print(f"{BOLD}{BLUE}╚═══════════════════════════════════════════════════════════════╝{NC}")

        total_completed = 0
        total_files = 0

        for week_num in range(1, 5):
            progress = self.get_week_progress(week_num)
            if not progress:
                continue

            completed = progress['completed_files']
            total = progress['total_files']
            pct = progress['progress_pct']

            total_completed += completed
            total_files += total

            # Mini progress bar
            bar_length = 20
            filled = int(bar_length * pct / 100)
            bar = '▓' * filled + '░' * (bar_length - filled)

            color = GREEN if pct == 100 else YELLOW if pct > 0 else RED
            status_icon = "✓" if pct == 100 else "○" if pct > 0 else "✗"

            print(f"\n{color}{status_icon}{NC} {BOLD}Week {week_num}: {progress['name']}{NC}")
            print(f"  {color}{bar}{NC} {pct:.0f}% ({completed}/{total})")

        # Overall summary
        overall_pct = (total_completed / total_files * 100) if total_files > 0 else 0
        print(f"\n{BOLD}{'─' * 60}{NC}")
        print(f"{BOLD}Overall Progress: {total_completed}/{total_files} files ({overall_pct:.0f}%){NC}")

        # Next steps
        print(f"\n{BOLD}{BLUE}Next Steps:{NC}")
        for week_num in range(1, 5):
            progress = self.get_week_progress(week_num)
            if progress and progress['progress_pct'] < 100:
                print(f"  • Start Week {week_num}: {progress['name']}")
                print(f"    {BLUE}cd week-{week_num}-{self._get_week_slug(week_num)}{NC}")
                print(f"    {BLUE}cat README.md{NC}")
                break
        else:
            print(f"  {GREEN}🎉 Congratulations! You've completed all weeks!{NC}")
            print(f"  {BLUE}Ready for the capstone project!{NC}")

    def generate_report(self):
        """Generate a detailed progress report."""
        print(f"\n{BOLD}Generating detailed progress report...{NC}\n")

        report_path = self.base_path / 'progress_report.txt'
        with open(report_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("ML Pipeline Learning - Progress Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")

            for week_num in range(1, 5):
                progress = self.get_week_progress(week_num)
                if not progress:
                    continue

                f.write(f"Week {week_num}: {progress['name']}\n")
                f.write("-" * 60 + "\n")
                f.write(f"Progress: {progress['completed_files']}/{progress['total_files']} ")
                f.write(f"({progress['progress_pct']:.0f}%)\n\n")

                for filename, status in progress['file_status']:
                    if status['modified']:
                        f.write(f"  ✓ {filename}\n")
                    elif status['exists']:
                        f.write(f"  ○ {filename} (not started)\n")
                    else:
                        f.write(f"  ✗ {filename} (missing)\n")

                f.write("\n")

        print(f"{GREEN}✓ Report saved to: {report_path}{NC}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Track your ML Pipeline learning progress'
    )
    parser.add_argument(
        '--week',
        type=int,
        choices=[1, 2, 3, 4],
        help='Show progress for a specific week'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed file-level progress'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate a detailed progress report'
    )

    args = parser.parse_args()

    tracker = ProgressTracker()

    if args.report:
        tracker.generate_report()
    elif args.week:
        tracker.print_week_progress(args.week, detailed=True)
    else:
        tracker.print_overall_progress()
        if args.detailed:
            for week_num in range(1, 5):
                tracker.print_week_progress(week_num, detailed=True)


if __name__ == '__main__':
    main()
