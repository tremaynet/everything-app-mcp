#!/usr/bin/env python3

import json
import subprocess
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class PyrightMonitor:
    def __init__(self, project_root: str = None):
        """Initialize the Pyright Monitor
        
        Args:
            project_root: Root directory of the project to analyze
        """
        self.project_root = project_root or os.getcwd()
        self.results_dir = os.path.join(self.project_root, 'mcp_results')
        os.makedirs(self.results_dir, exist_ok=True)
    
    def check_pyright_installed(self) -> bool:
        """Check if pyright is installed"""
        try:
            subprocess.run(['pyright', '--version'], 
                          capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_pyright(self) -> bool:
        """Install pyright using npm"""
        try:
            print(f"{Colors.BLUE}Installing pyright...{Colors.ENDC}")
            subprocess.run(['npm', 'install', '-g', 'pyright'], 
                         check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.ERROR}Failed to install pyright: {e}{Colors.ENDC}")
            return False
    
    def run_pyright(self, file_path: Optional[str] = None) -> Dict:
        """Run pyright on the specified file or entire project
        
        Args:
            file_path: Optional specific file to analyze
            
        Returns:
            Dict containing the pyright analysis results
        """
        cmd = ['pyright', '--outputjson']
        
        if file_path:
            cmd.append(file_path)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            # Pyright exits with non-zero code when it finds problems
            if e.stdout:
                try:
                    return json.loads(e.stdout)
                except json.JSONDecodeError:
                    pass
            
            print(f"{Colors.ERROR}Error running pyright: {e}{Colors.ENDC}")
            return {'generalDiagnostics': []}
        except json.JSONDecodeError as e:
            print(f"{Colors.ERROR}Failed to parse pyright output: {e}{Colors.ENDC}")
            return {'generalDiagnostics': []}
    
    def filter_problems(self, data: Dict, severity: Optional[str] = None, 
                        file_pattern: Optional[str] = None) -> List[Dict]:
        """Filter problems based on severity and file pattern
        
        Args:
            data: Pyright analysis results
            severity: Optional severity to filter by ('error', 'warning', 'information')
            file_pattern: Optional regex pattern to match filenames
            
        Returns:
            Filtered list of problems
        """
        problems = data.get('generalDiagnostics', [])
        
        if severity:
            severity = severity.lower()
            problems = [p for p in problems if p.get('severity', '').lower() == severity]
        
        if file_pattern:
            pattern = re.compile(file_pattern)
            problems = [p for p in problems if 'file' in p and pattern.search(p['file'])]
        
        return problems
    
    def save_results(self, data: Dict, filename: Optional[str] = None) -> str:
        """Save analysis results to a JSON file
        
        Args:
            data: Analysis results to save
            filename: Optional custom filename
            
        Returns:
            Path to the saved file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pyright_results_{timestamp}.json"
        
        file_path = os.path.join(self.results_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return file_path
    
    def print_problems_summary(self, problems: List[Dict]) -> None:
        """Print a summary of the problems found"""
        if not problems:
            print(f"{Colors.GREEN}No problems found!{Colors.ENDC}")
            return
        
        error_count = sum(1 for p in problems if p.get('severity', '').lower() == 'error')
        warning_count = sum(1 for p in problems if p.get('severity', '').lower() == 'warning')
        info_count = sum(1 for p in problems if p.get('severity', '').lower() == 'information')
        
        print(f"{Colors.BOLD}\nSummary:{Colors.ENDC}")
        print(f"{Colors.ERROR}Errors: {error_count}{Colors.ENDC}")
        print(f"{Colors.WARNING}Warnings: {warning_count}{Colors.ENDC}")
        print(f"{Colors.BLUE}Information: {info_count}{Colors.ENDC}")
        print(f"Total: {len(problems)}")
    
    def print_detailed_problems(self, problems: List[Dict], max_display: int = 10) -> None:
        """Print detailed information about each problem
        
        Args:
            problems: List of problems to display
            max_display: Maximum number of problems to display
        """
        if not problems:
            return
        
        print(f"\n{Colors.BOLD}Detailed Problems:{Colors.ENDC}")
        
        for i, problem in enumerate(problems[:max_display]):
            severity = problem.get('severity', '').lower()
            color = Colors.ERROR if severity == 'error' else \
                  Colors.WARNING if severity == 'warning' else Colors.BLUE
            
            file_path = problem.get('file', 'Unknown file')
            line = problem.get('range', {}).get('start', {}).get('line', 0) + 1
            column = problem.get('range', {}).get('start', {}).get('character', 0) + 1
            message = problem.get('message', 'No message')
            
            print(f"\n{color}{i+1}. [{severity.upper()}] {file_path}:{line}:{column}{Colors.ENDC}")
            print(f"   {message}")
        
        if len(problems) > max_display:
            print(f"\n... and {len(problems) - max_display} more problems")
    
    def analyze_file(self, file_path: str) -> Tuple[int, int, int]:
        """Analyze a specific file and return problem counts
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Tuple of (error_count, warning_count, info_count)
        """
        print(f"\n{Colors.BOLD}Analyzing {file_path}...{Colors.ENDC}")
        
        if not os.path.exists(file_path):
            print(f"{Colors.ERROR}File not found: {file_path}{Colors.ENDC}")
            return (0, 0, 0)
        
        results = self.run_pyright(file_path)
        problems = results.get('generalDiagnostics', [])
        
        error_count = sum(1 for p in problems if p.get('severity', '').lower() == 'error')
        warning_count = sum(1 for p in problems if p.get('severity', '').lower() == 'warning')
        info_count = sum(1 for p in problems if p.get('severity', '').lower() == 'information')
        
        self.print_problems_summary(problems)
        self.print_detailed_problems(problems)
        
        results_file = self.save_results(results, f"pyright_{os.path.basename(file_path)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        print(f"\nDetailed results saved to: {results_file}")
        
        return (error_count, warning_count, info_count)

    def analyze_project(self) -> Dict[str, Tuple[int, int, int]]:
        """Analyze the entire project and return file-specific problem counts
        
        Returns:
            Dict mapping filenames to (error_count, warning_count, info_count) tuples
        """
        print(f"\n{Colors.BOLD}Analyzing entire project...{Colors.ENDC}")
        
        results = self.run_pyright()
        problems = results.get('generalDiagnostics', [])
        
        # Group problems by file
        files_problems = {}
        for problem in problems:
            file_path = problem.get('file')
            if not file_path:
                continue
                
            if file_path not in files_problems:
                files_problems[file_path] = []
            
            files_problems[file_path].append(problem)
        
        # Analyze problem counts by file
        file_stats = {}
        for file_path, file_problems in files_problems.items():
            error_count = sum(1 for p in file_problems if p.get('severity', '').lower() == 'error')
            warning_count = sum(1 for p in file_problems if p.get('severity', '').lower() == 'warning')
            info_count = sum(1 for p in file_problems if p.get('severity', '').lower() == 'information')
            
            file_stats[file_path] = (error_count, warning_count, info_count)
        
        self.print_problems_summary(problems)
        
        # Print summary by file
        if file_stats:
            print(f"\n{Colors.BOLD}Problems by file:{Colors.ENDC}")
            
            for file_path, (errors, warnings, infos) in sorted(
                file_stats.items(), 
                key=lambda x: sum(x[1]), 
                reverse=True
            ):
                total = errors + warnings + infos
                color = Colors.ERROR if errors > 0 else Colors.WARNING if warnings > 0 else Colors.BLUE
                print(f"{color}{file_path}: {errors} errors, {warnings} warnings, {infos} info ({total} total){Colors.ENDC}")
        
        results_file = self.save_results(results, f"pyright_project_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        print(f"\nDetailed results saved to: {results_file}")
        
        return file_stats

def main():
    """Main entry point for the script"""
    monitor = PyrightMonitor()
    
    if not monitor.check_pyright_installed():
        print(f"{Colors.WARNING}Pyright not found. Attempting to install...{Colors.ENDC}")
        if not monitor.install_pyright():
            print(f"{Colors.ERROR}Please install pyright manually: npm install -g pyright{Colors.ENDC}")
            sys.exit(1)
    
    args = sys.argv[1:]
    
    if not args:
        # No arguments, analyze the whole project
        monitor.analyze_project()
    else:
        # Analyze specific files
        for file_path in args:
            monitor.analyze_file(file_path)

if __name__ == "__main__":
    main()