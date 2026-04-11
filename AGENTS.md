# TI5 Motor Control Agent

TI5 모터 제어 전문 에이전트. **기존 스크립트와 설정 파일을 먼저 확인하고 활용할 것.**

## 기존 스크립트 — 작업별 사용 맵

**새 스크립트를 만들기 전에 반드시 아래 기존 도구를 확인하고 사용할 것.**

### 모터 이동 (일반)

| 작업 | 스크립트 | 사용법 |
|------|---------|--------|
| 모터 N번을 X도 이동 (상대) | `scripts/CAN_Test/move_motor.py` | `python3 move_motor.py --id <N> --angle <X>` |
| 절대 위치로 이동 | `scripts/CAN_Test/move_motor.py` | `python3 move_motor.py --id <N> --angle <X> --absolute` |
| 속도 지정 이동 | `scripts/CAN_Test/move_motor.py` | `python3 move_motor.py --id <N> --angle <X> --speed <dps>` |
| 각도기 측정 대기 | `scripts/CAN_Test/move_motor.py` | `python3 move_motor.py --id <N> --angle <X> --wait` |

### 원점/홈 설정

| 작업 | 스크립트 | 사용법 |
|------|---------|--------|
| 현재 위치를 0도로 설정 | `scripts/CAN_Test/motor_home.py` | `python3 motor_home.py save --id 18` |
| 원점으로 이동 | `scripts/CAN_Test/motor_home.py` | `python3 motor_home.py move --id 18` |
| 저장된 원점 읽기 | `scripts/CAN_Test/motor_home.py` | `python3 motor_home.py read --id 18` |
| 원점 설정 파일 | `config/motor_home_position.yaml` | 모든 14관절 홈 위치 저장 |

### CAN 통신/진단

| 작업 | 스크립트 |
|------|---------|
| 모터 스캔 | `scripts/CAN_Test/can_scan.py` |
| 전체 레지스터 읽기 | `scripts/CAN_Test/can_read_info.py <motor_id>` |
| Echo 테스트 (부동 확인) | `scripts/CAN_Test/can_echo_test.py <motor_id>` |
| 통합 테스트 (6단계) | `scripts/CAN_Test/can_full_test.py <motor_id> --gear-ratio 101` |
| 모터 모델 스캔 | `scripts/Single_Motor_Test_py/scan_motor_models.py` |

### 위치 제어/검증

| 작업 | 스크립트 |
|------|---------|
| 5도 이동 검증 | `experiments/axis-16/move_5deg.py` |
| 엔코더 262,144 검증 | `experiments/axis-19/verify_262144.py` |
| 엔코더 x4 HIL 검증 | `scripts/CAN_Test/hil_encoder_x4_test.py` |
| 원점 이동 | `scripts/CAN_Test/can_move_zero.py <motor_id>` |

### CAN 래퍼/로직 (import용)

| 모듈 | 용도 |
|------|------|
| `scripts/CAN_Test/ti5_can.py` | Ti5CAN 클래스 — CAN 통신 전체 |
| `scripts/Single_Motor_Test_py/single_motor_logic.py` | 단위 변환, 안전 한계, 모터/관절 스펙 |
| `scripts/Multi_Motor_Test_py/multi_motor_logic.py` | 배치 명령, 웨이브, 순차 홈 |

### SIL 테스트 (하드웨어 불필요)

```bash
# L0 — CAN_Test 단위 테스트
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest scripts/CAN_Test/ -v --tb=short

# L1 — Single Motor 단위 테스트
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest scripts/Single_Motor_Test_py/ -v --tb=short

# L2 — Multi Motor 단위 테스트
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest scripts/Multi_Motor_Test_py/ -v --tb=short
```

> HIL 테스트는 USB-CAN 어댑터 + 모터 전원 필요. 결과 보고 시 **SIL/HIL 라벨 명시 필수**.

---

## 하드웨어 (실측)

- CAN IDs: L=16-22 (왼팔 CH0), R=23-29 (오른팔 CH1)
- 기어비: 어깨(16-18,23-25)=121, 팔꿈치(19,26)=101, 손목(20-22,27-29)=101
- 모터 모델: 어깨=CRA-RI60-70, 팔꿈치=CRA-RI50-60, 손목=CRA-RI40-52
- Mirror sign: 왼팔 +1, 오른팔 -1 (누락 시 충돌 위험)

## 엔코더 스케일 (ISSUE-017)

두 스케일 혼용 시 30× 오버슈트 발생:

| 스케일 | Counts/Rev | 용도 |
|--------|-----------|------|
| Position register (cmd 8/30) | 262,144 (4×65536) | raw CAN 명령 |
| Out position | gear_ratio × 65536 | degrees_to_counts() / SDK API |

raw CAN cmd 30: `counts = int(degrees / 360.0 * 262144)` — degrees_to_counts() 사용 금지

## 초기화 순서

```
CAN Open → Status(cmd 10) → Fault Clear(cmd 11) → Enable(cmd 1) → Vel Limit(cmd 36/37) → Command → Disable(cmd 2) → Close
```

알려진 이슈: ISSUE-013 (재오픈 전 2s 딜레이), ISSUE-014 (VCI_FindUsbDevice2 핸들 오염)

## EEPROM (2026-04-11 실측)

- 모든 RAM 변경은 cmd 14 필수 — **예외 없음** (cmd 46 포함)
- cmd 46 단독: 전원 재투입 시 원래 ID로 복귀
- ISSUE-018: cmd 83(offset) + cmd 14 → CAN ID 오염 가능

## 안전 한계

Position ±716°, Speed ±1031°/s, Current ±40A, 원점 30° 초과 시 trapezoid(cmd 31)

## SDK 구조

```text
User Code → Ti5BASIC.h → libmylibti5_multi_motor.so (135KB) → libcontrolcan.so → USB-CAN → Motor
```

## 주요 문서

- 엔코더: `docs/09-unit-conversion-guide.md`, `docs/issues_and_fixes/017-position-register-scale-mismatch.md`
- CMD 코드: `docs/04-cmd-code-reference.md` (101개 문서화)
- SDK 비교: `docs/sdk-comparison-libmylibti5-vs-multi_motor.md`
- 전체 이슈: `docs/issues_and_fixes/`

## 금지 사항

- degrees_to_counts()를 raw CAN cmd 8/30에 사용 금지
- cmd 46 (CAN ID 변경) 사용자 확인 없이 금지
- VCI_FindUsbDevice2를 장치 열린 상태에서 호출 금지
- 실측 데이터 변경 시 새 HIL 근거 필수
