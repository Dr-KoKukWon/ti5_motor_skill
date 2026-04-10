# Encoder Ratio Verification — 실험 방법

## 목적

CAN Position register와 Out position 간 비율 공식을 검증:

```
Out position / Position = gear_ratio / 4
```

## 필요 장비

- USB-CAN 어댑터 (CANalyst-II / ZLG USBCAN-2A)
- 대상 모터 + 전원
- **Motor Controls V1.1.6** 소프트웨어 (Windows)
- 각도기 (물리 각도 교차 검증용, 선택)

## 실험 절차

### Step 1: Motor Controls 연결

1. USB-CAN 어댑터를 PC에 연결
2. Motor Controls V1.1.6 실행
3. 대상 모터 CAN ID 선택 (Equipment selection)
4. "Status display" 패널에서 **Position(cnt)**와 **Out position(cnt)** 확인

### Step 2: 데이터 수집 (최소 5개 위치)

1. 모터를 **수동 또는 명령으로** 다양한 위치로 이동
2. 각 위치에서 스크린샷 촬영 (Position, Out position 값 기록)
3. **양방향** 데이터 포함 (양수/음수 위치 모두)
4. **원점 근처 + 원점에서 먼 위치** 모두 포함 (영점 오프셋 영향 확인용)

기록 양식:

| 물리 각도 (추정) | Position(cnt) | Out position(cnt) | 비고 |
|-----------------|--------------|-------------------|------|
| | | | |

### Step 3: 절대 비율 계산

각 측정점에서:

```
absolute_ratio = Out_position / Position
```

주의: 원점 근처(Position < 1000)에서는 영점 오프셋(~50 counts)으로 비율이 왜곡됨.
이는 오류가 아니라 두 레지스터의 영점 차이.

### Step 4: 델타 비율 계산 (핵심)

영점 오프셋을 제거하기 위해 연속 측정 간 차이로 계산:

```python
for i in range(1, len(data)):
    delta_pos = data[i].position - data[i-1].position
    delta_out = data[i].out_position - data[i-1].out_position
    delta_ratio = delta_out / delta_pos
    print(f"Delta ratio: {delta_ratio:.4f}")
```

**예상값**: gear_ratio / 4 (기어비 121 → 30.25, 기어비 101 → 25.25)

### Step 5: 판정 기준

| 항목 | 통과 기준 |
|------|----------|
| 델타 비율 평균 | 이론값(gear_ratio/4) 대비 ±2% 이내 |
| 델타 비율 표준편차 | < 1.0 |
| 최소 측정점 | 5개 이상 (양수/음수 포함) |

### Step 6: 추가 검증 — move_5deg.py (선택)

CAN 명령으로 정밀 검증:

```bash
cd experiments/axis-16
python3 move_5deg.py --wait   # 이동 후 각도기 측정 대기
```

1. 현재 Position(cnt) 읽기
2. 5° 오프셋 계산: `int(5 / 360.0 * 262144) = 3640 counts`
3. 목표 = 현재 + 3640 전송 (cmd 30)
4. 도달 후 Position(cnt) 재읽기
5. 물리 각도 각도기로 측정
6. 일치 여부 확인 (허용 오차 ±0.5°)

## 기존 실측 결과 (CAN ID 16, gear_ratio=121)

Motor Controls V1.1.6 스크린샷 6장 (2026-04-10):

| 물리 각도 | Position(cnt) | Out position(cnt) | Out/Pos | 이론(30.25) 대비 |
|-----------|--------------|-------------------|---------|-----------------|
| -9.6° | -8,003 | -241,367 | 30.16 | -0.3% |
| -5.3° | -5,034 | -149,971 | 29.80 | -1.5% |
| 0.9° | 672 | 21,632 | 32.19 | +6.4% (영점 오프셋) |
| 8.3° | 5,011 | 152,711 | 30.48 | +0.8% |
| 15.2° | 10,059 | 305,987 | 30.42 | +0.6% |
| 20.6° | 14,006 | 426,141 | 30.43 | +0.6% |

델타 비율: 평균 30.37 (이론 30.25 대비 +0.4%), R²=0.999995

move_5deg.py 결과: 5° 명령 → 3,640 counts → 물리 5.00° (각도기 실측, 오차 0.01°)

## 미검증 모터 (다음 실험 대상)

| 모터 | CAN ID | Gear Ratio | 예측 비율 | 상태 |
|------|--------|-----------|----------|------|
| L_ELBOW_R | 19 | 101 | 25.25 | **미검증** |
| L_WRIST_Y | 20 | 101 | 25.25 | **미검증** |
| R_SHOULDER_P | 23 | 121 | 30.25 | **미검증** (CH1) |
| R_ELBOW_R | 26 | 101 | 25.25 | **미검증** |

## 보고 양식

```
## Encoder Ratio Verification — CAN ID XX (gear_ratio=YYY)
- 날짜:
- 장비: Motor Controls V1.1.6
- CAN 채널: CH0/CH1
- 측정점: N개

| 물리 각도 | Position(cnt) | Out position(cnt) | Out/Pos |
|-----------|--------------|-------------------|---------|

- 델타 비율 평균:
- 이론값(gear_ratio/4):
- 오차:
- 판정: PASS / FAIL
```
