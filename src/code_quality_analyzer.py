"""
This module provides functionality for analyzing the quality of the codebase.
"""
import ast
import radon.complexity as complexity
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CodeQualityAnalyzer:
    """
    A class to analyze the quality of the codebase.
    """

    def analyze_repository_complexity(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze code complexity across the repository.

        Args:
            repo_path (str): The path to the repository.

        Returns:
            Dict[str, Any]: A dictionary of complexity metrics.
        """
        complexity_metrics = {}

        for py_file in Path(repo_path).rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8") as file:
                    tree = ast.parse(file.read())

                # Calculate basic metrics
                metrics = self.calculate_file_metrics(tree, py_file)
                complexity_metrics[str(py_file)] = metrics

            except Exception as e:
                logging.warning(f"Could not analyze {py_file}: {str(e)}")

        return complexity_metrics

    def calculate_file_metrics(self, tree: ast.AST, file_path: Path) -> Dict[str, Any]:
        """
        Calculate code quality metrics for a file.

        Args:
            tree (ast.AST): The abstract syntax tree of the file.
            file_path (Path): The path to the file.

        Returns:
            Dict[str, Any]: A dictionary of code quality metrics.
        """
        return {
            "file_name": file_path.name,
            "lines_of_code": self.count_lines(file_path),
            "function_count": len(
                [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            ),
            "class_count": len(
                [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            ),
            "complexity_score": self.calculate_cyclomatic_complexity(tree),
        }

    def count_lines(self, file_path: Path) -> int:
        """
        Count the number of lines in a file.

        Args:
            file_path (Path): The path to the file.

        Returns:
            int: The number of lines in the file.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            return len(file.readlines())

    def calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """
        Calculate the cyclomatic complexity of a file.

        Args:
            tree (ast.AST): The abstract syntax tree of the file.

        Returns:
            int: The cyclomatic complexity of the file.
        """
        v = complexity.ComplexityVisitor.from_ast(tree)
        return v.total_complexity

    def create_quality_dashboard(self, metrics: Dict[str, Any], save_path: str) -> None:
        """
        Create code quality visualization dashboard.

        Args:
            metrics (Dict[str, Any]): A dictionary of complexity metrics.
            save_path (str): The path to save the dashboard to.
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Complexity distribution
        complexities = [m["complexity_score"] for m in metrics.values()]
        axes[0, 0].hist(complexities, bins=20, alpha=0.7, color="skyblue")
        axes[0, 0].set_title("Code Complexity Distribution")
        axes[0, 0].set_xlabel("Cyclomatic Complexity")
        axes[0, 0].set_ylabel("Number of Files")

        # Lines of code vs complexity
        locs = [m["lines_of_code"] for m in metrics.values()]
        axes[0, 1].scatter(locs, complexities, alpha=0.6)
        axes[0, 1].set_title("Lines of Code vs Complexity")
        axes[0, 1].set_xlabel("Lines of Code")
        axes[0, 1].set_ylabel("Complexity Score")

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
