"""Test execution tools for TI5 Motor Agent.

Runs SIL and HIL tests via subprocess, returning structured results.
"""

import os
import subprocess

_project_root = os.environ.get("TI5_PROJECT_ROOT", os.path.expanduser("~/test-ti5-kkw"))


def run_sil_test(test_file: str, test_class: str = None, verbose: bool = True) -> dict:
    """Run a SIL (Software-in-the-Loop) test.

    No hardware required. Safe to run anytime.

    Args:
        test_file: Test file path relative to scripts/, e.g. 'CAN_Test/tests/test_L0_phase0_can.py'
        test_class: Optional specific test class to run
        verbose: Show verbose output
    """
    full_path = os.path.join(_project_root, "scripts", test_file)
    if not os.path.exists(full_path):
        return {"success": False, "error": f"Test file not found: {full_path}"}

    test_dir = os.path.dirname(full_path)
    test_filename = os.path.basename(full_path)

    target = test_filename
    if test_class:
        target = f"{test_filename}::{test_class}"

    cmd = ["python3", "-m", "pytest", target]
    if verbose:
        cmd.extend(["-v", "--tb=short"])

    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    try:
        result = subprocess.run(
            cmd,
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

        passed = result.returncode == 0
        return {
            "success": True,
            "test_type": "SIL",
            "passed": passed,
            "return_code": result.returncode,
            "stdout": result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout,
            "stderr": result.stderr[-1000:] if result.stderr else "",
            "file": test_file,
            "class": test_class,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Test timed out after 120s", "test_type": "SIL"}
    except Exception as e:
        return {"success": False, "error": str(e), "test_type": "SIL"}


def run_hil_test(test_file: str, motor_id: int = None, test_class: str = None) -> dict:
    """Run a HIL (Hardware-in-the-Loop) test.

    REQUIRES: USB-CAN adapter + motor power.

    Args:
        test_file: Test file path relative to scripts/
        motor_id: Target motor ID (used for env variable)
        test_class: Optional specific test class to run
    """
    full_path = os.path.join(_project_root, "scripts", test_file)
    if not os.path.exists(full_path):
        return {"success": False, "error": f"Test file not found: {full_path}"}

    test_dir = os.path.dirname(full_path)
    test_filename = os.path.basename(full_path)

    target = test_filename
    if test_class:
        target = f"{test_filename}::{test_class}"

    cmd = ["python3", "-m", "pytest", target, "-v", "--tb=short"]

    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    if motor_id is not None:
        env["TEST_MOTOR_ID"] = str(motor_id)

    try:
        result = subprocess.run(
            cmd,
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=300,  # HIL tests may take longer
            env=env,
        )

        passed = result.returncode == 0
        return {
            "success": True,
            "test_type": "HIL",
            "passed": passed,
            "return_code": result.returncode,
            "stdout": result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout,
            "stderr": result.stderr[-1000:] if result.stderr else "",
            "file": test_file,
            "motor_id": motor_id,
            "class": test_class,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "HIL test timed out after 300s", "test_type": "HIL"}
    except Exception as e:
        return {"success": False, "error": str(e), "test_type": "HIL"}
