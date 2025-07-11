#!/usr/bin/env python3
"""
Script để chạy các test và tạo báo cáo coverage
"""
import os
import subprocess
import sys
import pathlib


def run_tests():
    """Chạy các test và tạo báo cáo coverage"""
    print("Đang chạy tests với pytest và coverage...")
    
    # Tạo thư mục cho báo cáo coverage nếu chưa tồn tại
    if not os.path.exists("coverage_reports"):
        os.makedirs("coverage_reports")
    
    # Thiết lập PYTHONPATH để có thể import module app
    current_dir = pathlib.Path(__file__).parent.absolute()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(current_dir)
    
    # Chạy pytest trực tiếp với môi trường đã thiết lập
    # Sử dụng các tham số đơn giản để tránh xung đột với pytest.ini
    result = subprocess.run(
        [
            "python", "-m", "pytest", 
            "tests/",
            "--cov=app",
            "--cov-report=term",
            "--cov-report=html:coverage_reports/html",
            "--cov-report=xml:coverage_reports/coverage.xml",
        ],
        capture_output=True,
        text=True,
        env=env
    )
    
    # In kết quả
    print(result.stdout)
    if result.stderr:
        print("Lỗi:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
    
    # Trả về mã thoát của pytest
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
