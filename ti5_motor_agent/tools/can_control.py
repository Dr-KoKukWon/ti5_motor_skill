"""CAN bus control tools for TI5 Motor Agent.

Wraps ti5_can.py to provide CAN communication as agent tools.
Requires libcontrolcan.so and USB-CAN hardware for actual operation.
"""

import sys
import os
import math

# Global CAN device instance
_can_instance = None
_project_root = os.environ.get("TI5_PROJECT_ROOT", os.path.expanduser("~/test-ti5-kkw"))

# Encoder constants
ENCODER_PPR = 65536
POSITION_CNT_PER_REV = 4 * ENCODER_PPR  # 262,144

# Joint gear ratios (HW verified 2026-04-09)
JOINT_GEAR = {
    16: 121, 17: 121, 18: 121,  # L shoulder
    19: 101,                     # L elbow
    20: 101, 21: 101, 22: 101,  # L wrist
    23: 121, 24: 121, 25: 121,  # R shoulder
    26: 101,                     # R elbow
    27: 101, 28: 101, 29: 101,  # R wrist
}

ERROR_STATUS = {
    0: "Normal", 1: "SoftwareError", 2: "Overvoltage", 3: "Undervoltage",
    4: "StartupError", 5: "SpeedFeedbackError", 6: "Overcurrent",
    7: "EncoderCommError", 8: "MotorOverheat", 9: "PCBOverheat",
}


def _get_can():
    """Get or import Ti5CAN class."""
    global _can_instance
    if _can_instance is not None:
        return _can_instance

    can_test_dir = os.path.join(_project_root, "scripts", "CAN_Test")
    if can_test_dir not in sys.path:
        sys.path.insert(0, can_test_dir)

    try:
        from ti5_can import Ti5CAN
        return Ti5CAN
    except (ImportError, FileNotFoundError) as e:
        return None


def can_open(channel: int = 0) -> dict:
    """Open CAN bus device.

    Args:
        channel: 0=left arm (IDs 16-22), 1=right arm (IDs 23-29)
    """
    global _can_instance

    Ti5CAN = _get_can()
    if Ti5CAN is None:
        return {"success": False, "error": "Ti5CAN not available. Check libcontrolcan.so and TI5_PROJECT_ROOT."}

    if isinstance(Ti5CAN, type):
        _can_instance = Ti5CAN()

    ok = _can_instance.open(can_index=channel)
    if ok:
        arm = "left" if channel == 0 else "right"
        return {"success": True, "message": f"CAN CH{channel} ({arm} arm) opened at 1Mbps"}
    else:
        _can_instance = None
        return {"success": False, "error": f"VCI_OpenDevice failed for CH{channel}. Check USB-CAN connection."}


def can_close() -> dict:
    """Close CAN bus device."""
    global _can_instance
    if _can_instance is None:
        return {"success": True, "message": "No device was open"}

    ok = _can_instance.close()
    _can_instance = None
    return {"success": ok, "message": "CAN device closed" if ok else "VCI_CloseDevice failed"}


def can_send_command(motor_id: int, cmd_code: int, param: int = None) -> dict:
    """Send a CAN command to a motor.

    Args:
        motor_id: Motor CAN ID (16-29)
        cmd_code: Command code
        param: Optional int32 parameter for write commands
    """
    if _can_instance is None:
        return {"success": False, "error": "CAN device not open. Call can_open() first."}

    if not (1 <= motor_id <= 40):
        return {"success": False, "error": f"Invalid motor_id {motor_id}. Must be 1-40."}

    # Safety: block cmd 46 (CAN ID change)
    if cmd_code == 46:
        return {"success": False, "error": "cmd 46 (CAN ID change) is FORBIDDEN. Risk of bricking motor."}

    try:
        if param is not None:
            ok = _can_instance.send_command(motor_id, cmd_code, param=param)
        else:
            ok = _can_instance.send_command(motor_id, cmd_code)
        return {"success": ok, "motor_id": motor_id, "cmd": cmd_code, "param": param}
    except Exception as e:
        return {"success": False, "error": str(e)}


def can_read_register(motor_id: int, cmd_code: int, wait_ms: int = 100) -> dict:
    """Read a register from a motor.

    Args:
        motor_id: Motor CAN ID (16-29)
        cmd_code: Read command code
        wait_ms: Timeout in ms
    """
    if _can_instance is None:
        return {"success": False, "error": "CAN device not open. Call can_open() first."}

    try:
        value = _can_instance.read_register(motor_id, cmd_code, wait_ms=wait_ms)
        if value is None:
            return {"success": False, "error": f"No response from motor {motor_id} for cmd {cmd_code}"}

        result = {"success": True, "motor_id": motor_id, "cmd": cmd_code, "raw_value": value}

        # Add interpreted values for known registers
        if cmd_code == 10:  # Status
            result["status"] = ERROR_STATUS.get(value, f"Unknown({value})")
        elif cmd_code == 8:  # Current position
            result["degrees"] = round(value / POSITION_CNT_PER_REV * 360.0, 4)
        elif cmd_code == 9:  # Target position
            result["degrees"] = round(value / POSITION_CNT_PER_REV * 360.0, 4)
        elif cmd_code == 100:  # Motor model
            result["model_raw"] = value

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def convert_units(value: float, from_unit: str, to_unit: str, gear_ratio: float = 101) -> dict:
    """Convert between motor control units.

    Supports: degrees, radians, position_counts (CAN register),
              out_position_counts, deg_per_sec, speed_cmd, rpm
    """
    TWO_PI = 2.0 * math.pi

    # First convert to a common base (degrees for position, deg/s for speed)
    if from_unit == "degrees":
        base_deg = value
    elif from_unit == "radians":
        base_deg = math.degrees(value)
    elif from_unit == "position_counts":
        base_deg = value / POSITION_CNT_PER_REV * 360.0
    elif from_unit == "out_position_counts":
        base_deg = value / (gear_ratio * ENCODER_PPR) * 360.0
    elif from_unit == "deg_per_sec":
        base_dps = value
    elif from_unit == "speed_cmd":
        import ctypes
        signed = ctypes.c_int32(int(value)).value
        base_dps = (signed * 360.0) / (gear_ratio * 100.0)
    elif from_unit == "rpm":
        base_dps = value * 6.0  # 1 RPM = 6 deg/s
    else:
        return {"error": f"Unknown from_unit: {from_unit}"}

    # Position conversions
    if from_unit in ("degrees", "radians", "position_counts", "out_position_counts"):
        if to_unit == "degrees":
            result = base_deg
        elif to_unit == "radians":
            result = math.radians(base_deg)
        elif to_unit == "position_counts":
            result = int(base_deg / 360.0 * POSITION_CNT_PER_REV)
        elif to_unit == "out_position_counts":
            result = int(base_deg / 360.0 * gear_ratio * ENCODER_PPR)
        else:
            return {"error": f"Cannot convert position to speed unit: {to_unit}"}
    # Speed conversions
    elif from_unit in ("deg_per_sec", "speed_cmd", "rpm"):
        if to_unit == "deg_per_sec":
            result = base_dps
        elif to_unit == "speed_cmd":
            result = int(base_dps * gear_ratio * 100.0 / 360.0)
        elif to_unit == "rpm":
            result = base_dps / 6.0
        else:
            return {"error": f"Cannot convert speed to position unit: {to_unit}"}
    else:
        return {"error": f"Unknown from_unit: {from_unit}"}

    return {
        "input": value,
        "from": from_unit,
        "to": to_unit,
        "result": result,
        "gear_ratio": gear_ratio,
    }
