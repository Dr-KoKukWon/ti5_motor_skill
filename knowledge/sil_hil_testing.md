## 테스트 실행 명령어 (복사해서 바로 실행)

### SIL (하드웨어 불필요)
```bash
# L0 CAN 로직
cd scripts/CAN_Test/tests && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest test_L0_phase0_can.py -v

# L1 단일 모터
cd scripts/Single_Motor_Test_py && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -v

# L2 멀티 모터
cd scripts/Multi_Motor_Test_py && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -v
```

### HIL (USB-CAN + 모터 전원 필요)
```bash
python3 scripts/CAN_Test/can_scan.py              # 모터 스캔
python3 scripts/CAN_Test/can_read_info.py <ID>     # 레지스터 읽기
python3 scripts/CAN_Test/can_full_test.py <ID> --gear-ratio 101  # 통합 테스트
python3 scripts/CAN_Test/motor_home.py save --id <ID>  # 원점 설정
```

---

# TI5 SIL / HIL Testing Methods

## Test Hierarchy

| Level | Scope | SIL Files | HIL Files |
|-------|-------|-----------|-----------|
| L0 | CAN protocol logic | test_L0_phase0_can.py | test_H0_phase0_hil.py |
| L1 | Single motor control | test_L1_single_motor_logic.py, test_L1_single_motor_commands.py, test_L1_encoder_x4_verify.py | test_H1_single_motor_hw.py |
| L2 | Multi-motor sync | test_L2_multi_motor_sync.py, test_L2_cross_validation.py | test_H2_multi_motor_hw.py |

## SIL Execution (no hardware needed)

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest <test_file> -v --tb=short
```

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 is REQUIRED (ROS2 plugin conflict prevention).

### SIL Mock Pattern

```python
from unittest.mock import MagicMock, patch
with patch("ti5_can.ctypes.CDLL") as mock_cdll:
    mock_cdll.return_value = MagicMock()
    can = Ti5CAN(lib_path="/fake/libcontrolcan.so")
    can._opened = True
    can.send = MagicMock(return_value=True)
```

### SIL Test Coverage

- Unit conversions (degrees↔counts, speed, current)
- Safety limit checks (position ±716°, speed ±1031°/s, current ±40A)
- CAN frame encoding (1-byte read vs 5-byte write)
- Impedance clamping (kp 0-500, kd 0-5, pos ±12.5 rad)
- Motor/Joint spec lookups (14 joints, 3 motor models)
- Cross-module consistency (single_motor_logic ↔ ti5_can)
- Batch command preparation (multi-motor)
- Wave math (sine generation, ramp-down)

## HIL Execution (USB-CAN + motors required)

```bash
sudo pytest test_H0_phase0_hil.py -v  # or use plugdev group
```

### HIL Fixture Pattern (module-scoped, single device)

```python
@pytest.fixture(scope="module")
def can_device():
    can = Ti5CAN()
    if not can.open(device_type=4, can_index=0):
        pytest.skip("CAN device open failed")
    yield can
    can.close()
    time.sleep(2.0)  # ISSUE-013: USB handle release delay
```

### HIL Test Coverage

- Device open/close
- Bus scan (14 motors, IDs 16-29)
- Register reads (status, position, voltage, temp, model)
- Echo write (position unchanged, 3 cycles, ±10 counts tolerance)
- Target readback verification
- Electrical safety (20V ≤ bus voltage ≤ 80V, temp ≤ 80°C)
- Position stability on idle (drift ≤ 10 counts)

### Standalone HIL Tools

| Tool | Purpose | Motor Movement |
|------|---------|---------------|
| can_scan.py | Bus scan, discover motor IDs | No |
| can_read_info.py | Read all registers | No |
| can_echo_test.py | Echo test (TX/RX verify) | No |
| can_move_zero.py | Move to home position | **YES** |
| can_full_test.py | 6-step integration test | Optional |
| hil_encoder_x4_test.py | Encoder ×4 PPR verification | **YES** |
| verify_262144.py | Encoder scale verification (262,144 cnt/rev) | **YES** |

## Reporting Rules

- ALWAYS label results as SIL or HIL
- HIL results must include responding motor IDs and status values
- On failure: include which step failed and raw error message
