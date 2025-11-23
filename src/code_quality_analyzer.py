import ast
import complexity
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import logging

class CodeQualityAnalyzer:
    """Analyze code quality metrics across the repository"""
    
    def analyze_repository_complexity(self, repo_path: str) -> Dict:
        """Analyze code complexity across the repository"""
        complexity_metrics = {}
        
        for py_file in Path(repo_path).rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as file:
                    tree = ast.parse(file.read())
                    
                # Calculate basic metrics
                metrics = self.calculate_file_metrics(tree, py_file)
                complexity_metrics[str(py_file)] = metrics
                
            except Exception as e:
                logging.warning(f"Could not analyze {py_file}: {str(e)}")
                
        return complexity_metrics
    
    def calculate_file_metrics(self, tree: ast.AST, file_path: Path) -> Dict:
        """Calculate code quality metrics for a file"""
        return {
            'file_name': file_path.name,
            'lines_of_code': self.count_lines(file_path),
            'function_count': len([node for node in ast.walk(tree) 
                                 if isinstance(node, ast.FunctionDef)]),
            'class_count': len([node for node in ast.walk(tree) 
                              if isinstance(node, ast.ClassDef)]),
            'complexity_score': self.calculate_cyclomatic_complexity(tree)
        }
    
    def create_quality_dashboard(self, metrics: Dict, save_path: str):
        """Create code quality visualization dashboard"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Complexity distribution
        complexities = [m['complexity_score'] for m in metrics.values()]
        axes[0,0].hist(complexities, bins=20, alpha=0.7, color='skyblue')
        axes[0,0].set_title('Code Complexity Distribution')
        axes[0,0].set_xlabel('Cyclomatic Complexity')
        axes[0,0].set_ylabel('Number of Files')
        
        # Lines of code vs complexity
        locs = [m['lines_of_code'] for m in metrics.values()]
        axes[0,1].scatter(locs, complexities, alpha=0.6)
        axes[0,1].set_title('Lines of Code vs Complexity')
        axes[0,1].set_xlabel('Lines of Code')
        axes[0,1].set_ylabel('Complexity Score')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')