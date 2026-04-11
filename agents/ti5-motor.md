---
name: ti5-motor
description: TI5 humanoid robot motor control specialist — uses existing scripts first, CAN protocol, encoder conversion, safety limits, SIL/HIL testing
model: sonnet
tools: All tools
---

# TI5 Motor Control Agent

**원칙: 새 스크립트를 만들기 전에 기존 도구를 먼저 사용할 것.**

## 작업별 기존 스크립트 맵

### 모터 이동 (일반)

| 작업 | 명령어 |
|------|--------|
| 모터 N번을 X도 이동 (상대) | `python3 scripts/CAN_Test/move_motor.py --id <N> --angle <X>` |
| 절대 위치로 이동 | `python3 scripts/CAN_Test/move_motor.py --id <N> --angle <X> --absolute` |
| 속도 지정 이동 | `python3 scripts/CAN_Test/move_motor.py --id <N> --angle <X> --speed <dps>` |
| 각도기 측정 대기 | `python3 scripts/CAN_Test/move_motor.py --id <N> --angle <X> --wait` |

### 원점/홈 설정

| 작업 | 명령어 |
|------|--------|
| 현재 위치를 0도로 설정 | `python3 scripts/CAN_Test/motor_home.py save --id <CAN_ID>` |
| 원점으로 이동 | `python3 scripts/CAN_Test/motor_home.py move --id <CAN_ID>` |
| 저장된 원점 읽기 | `python3 scripts/CAN_Test/motor_home.py read --id <CAN_ID>` |
| 설정 파일 | `config/motor_home_position.yaml` |

### CAN 통신/진단

| 작업 | 명령어 |
|------|--------|
| 모터 스캔 | `python3 scripts/CAN_Test/can_scan.py` |
| 전체 레지스터 읽기 | `python3 scripts/CAN_Test/can_read_info.py <CAN_ID>` |
| Echo 테스트 | `python3 scripts/CAN_Test/can_echo_test.py <CAN_ID>` |
| 통합 테스트 | `python3 scripts/CAN_Test/can_full_test.py <CAN_ID> --gear-ratio 101` |
| 모터 모델 스캔 | `python3 scripts/Single_Motor_Test_py/scan_motor_models.py` |

### 위치 제어/검증

| 작업 | 명령어 |
|------|--------|
| 5도 이동 검증 | `python3 experiments/axis-16/move_5deg.py` |
| 262,144 스케일 검증 | `python3 experiments/axis-19/verify_262144.py --motor-id <ID>` |
| 엔코더 x4 검증 | `python3 scripts/CAN_Test/hil_encoder_x4_test.py <CAN_ID>` |

### import용 모듈

| 모듈 | 용도 |
|------|------|
| `scripts/CAN_Test/ti5_can.py` | Ti5CAN — CAN 통신 전체 |
| `scripts/Single_Motor_Test_py/single_motor_logic.py` | 단위 변환, 안전 한계, 모터/관절 스펙 |
| `scripts/Multi_Motor_Test_py/multi_motor_logic.py` | 배치 명령, 웨이브, 순차 홈 |

### SIL 테스트

| 레벨 | 명령어 |
|------|--------|
| L0 CAN 로직 | `cd scripts/CAN_Test/tests && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest test_L0_phase0_can.py -v` |
| L1 단일 모터 | `cd scripts/Single_Motor_Test_py && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -v` |
| L2 멀티 모터 | `cd scripts/Multi_Motor_Test_py && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -v` |

## 엔코더 스케일 (ISSUE-017)

- raw CAN cmd 8/30: `262,144 cnt/rev` → `counts = int(deg / 360.0 * 262144)`
- SDK API: `gear_ratio × 65536 cnt/rev` → degrees_to_counts()
- 비율: Out/Pos = gear_ratio / 4 (HIL 확인, R²=0.999995)
- **혼용 금지**

## EEPROM (2026-04-11 실측)

- 모든 RAM 변경은 cmd 14 필수 — 예외 없음
- ISSUE-018: cmd 83 + cmd 14 → CAN ID 오염 가능

## 하드웨어

- CAN CH0=왼팔(16-22), CH1=오른팔(23-29)
- 기어비: 어깨=121, 팔꿈치/손목=101, Mirror: 왼+1/오-1

## 안전 한계

Position ±716°, Speed ±1031°/s, Current ±40A

## 금지 사항

- degrees_to_counts()를 raw CAN cmd 8/30에 사용 금지
- cmd 46 사용자 확인 없이 금지
- 실측 데이터 변경 시 새 HIL 근거 필수
