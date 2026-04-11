## 관련 스크립트 — 기존 도구를 먼저 사용할 것

| 작업 | 명령어 |
|------|--------|
| 엔코더 262,144 검증 (HIL) | `python3 experiments/axis-19/verify_262144.py --motor-id <ID>` |
| 5도 이동 검증 (HIL) | `python3 experiments/axis-16/move_5deg.py` |
| 엔코더 x4 판별 (HIL) | `python3 scripts/CAN_Test/hil_encoder_x4_test.py <CAN_ID>` |
| 엔코더 x4 SIL 검증 | `cd scripts/Single_Motor_Test_py && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest test_L1_encoder_x4_verify.py -v` |
| 단위 변환 모듈 (import) | `from single_motor_logic import degrees_to_counts, counts_to_degrees, ENCODER_PPR` |

---

# TI5 Encoder Settings

## Two Scales Coexist (ISSUE-017, HIL verified 2026-04-10)

| Scale | Counts/Rev | Counts/Deg | Usage |
|-------|-----------|-----------|-------|
| **Position register** (cmd 8/30) | **262,144** (= 4 × 65536 = 2^18) | **728.2** | CAN position command/feedback |
| **Out position** | gear_ratio × 65536 | 22,027 (ratio=121) / 18,386 (ratio=101) | Motor Controls UI, degrees_to_counts() |

**Ratio (HIL confirmed, R²=0.999995)**:

```
Out position / Position = gear_ratio / 4
```

- Shoulder (ratio 121): 121/4 = **30.25×** (실측 평균 30.37, 이론 대비 0.4%)
- Elbow/Wrist (ratio 101): 101/4 = **25.25×** (예측값, HIL 미검증)

Note: 262,144 cnt/rev 값과 비율 공식은 HIL 실측으로 확정됨.
"4"의 물리적 메커니즘(quadrature vs 18비트 앱솔루트 엔코더)만 데이터시트 미확보로 미확인.

## Correct CAN Position Conversion

```python
POSITION_CNT_PER_REV = 262144  # HIL verified, 출력축 1회전

# degrees → Position register counts (for cmd 30)
counts = int(degrees / 360.0 * POSITION_CNT_PER_REV)

# Position register counts → degrees (for cmd 8)
degrees = counts / POSITION_CNT_PER_REV * 360.0
```

## Out Position Conversion (motor_utils / single_motor_logic.py)

```python
ENCODER_PPR = 65536

# Output-shaft degrees → Out position counts
encoder_count = int(degrees / 360.0 * gear_ratio * ENCODER_PPR)

# Out position counts → degrees
degrees = (encoder_count / (gear_ratio * ENCODER_PPR)) * 360.0
```

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| ENCODER_PPR | 65,536 (2^16) | Motor shaft counts per revolution |
| POSITION_CNT_PER_REV | 262,144 (2^18) | CAN Position register counts/rev |
| j2p (ratio 101) | 1,052,379 | Encoder steps per radian |
| j2p (ratio 121) | 1,261,653 | Encoder steps per radian |
| n2p | 655.36 | RPM → steps/sec conversion |

## Joint Gear Ratios (HW verified 2026-04-09)

| Joint | CAN ID (L/R) | Gear Ratio | Motor Model |
|-------|-------------|-----------|-------------|
| Shoulder (P/R/Y) | 16-18 / 23-25 | **121** | CRA-RI60-70 |
| Elbow (R) | 19 / 26 | **101** | CRA-RI50-60 |
| Wrist (Y/P/R) | 20-22 / 27-29 | **101** | CRA-RI40-52 |

## DANGER: Scale Mismatch

Using `degrees_to_counts(5, 121)` for cmd 30 sends 110,136 counts → physically moves ~150° (30.25× overshoot).
Correct: `int(5 / 360.0 * 262144)` = 3,640 counts → physically moves 5° (verified with protractor).

## Quick Reference (ratio 101)

| Conversion | Formula | Example |
|-----------|---------|---------|
| deg → encoder | `deg × 18,385.6` | 90° = 1,654,702 |
| rad → encoder | `rad × 1,052,379` | 1 rad = 1,052,379 |
| deg/s → speed cmd | `dps × 28.06` | 10°/s = 281 |
