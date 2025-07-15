#!/usr/bin/env python3
"""
Test runner script with coverage reporting
"""
import os
import subprocess
import sys
import pathlib


def run_tests():
    """Run tests and generate coverage reports"""
    print("Running tests with pytest and coverage...")

    # Create coverage reports directory if it doesn't exist
    if not os.path.exists("coverage_reports"):
        os.makedirs("coverage_reports")

    # Set up PYTHONPATH for app module imports
    current_dir = pathlib.Path(__file__).parent.absolute()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(current_dir)

    # Run pytest with configured environment
    # Use simple parameters to avoid conflicts with pytest.ini
    result = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "tests/",
            "--cov=app",
            "--cov-report=term",
            "--cov-report=html:coverage_reports/html",
            "--cov-report=xml:coverage_reports/coverage.xml",
        ],
        capture_output=True,
        text=True,
        env=env,
    )

    # Print results
    print(result.stdout)
    if result.stderr:
        print("Error:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)

    # Return pytest exit code
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
