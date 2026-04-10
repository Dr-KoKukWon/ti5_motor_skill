# TI5 Motor Initialization Sequence

## Full Sequence

```
CAN Open → Status Check → Fault Clear → Enable → Vel Limit → Command → Disable → Close
 (VCI)      (cmd 10)      (cmd 11)     (cmd 1)  (cmd 36/37) (30/31/29/28) (cmd 2)  (VCI)
```

## Step 1: CAN Device Open

```python
can = Ti5CAN()
can.open(device_type=4, device_index=0, can_index=0)  # 0=left arm, 1=right arm
```

VCI API sequence: VCI_OpenDevice → VCI_InitCAN → VCI_ClearBuffer → VCI_StartCAN
- Baudrate: 1 Mbps (Timing0=0x00, Timing1=0x14)
- AccMask=0xFFFFFFFF (accept all frames)
- ISSUE-013: Requires 2s delay after VCI_CloseDevice before reopening
- ISSUE-014: VCI_FindUsbDevice2 must NOT be called while device is open (corrupts handle)

## Step 2: Status Check (cmd 10)

```python
status = can.read_register(motor_id, 10, wait_ms=100)
# 0=Normal, 1=SoftwareError, 2=Overvoltage, 3=Undervoltage, 4=StartupError
# 5=SpeedFeedbackError, 6=Overcurrent, 7=EncoderCommError, 8=MotorOverheat, 9=PCBOverheat
```

## Step 3: Fault Clear (cmd 11, if needed)

```python
can.send_command(motor_id, 11)  # Clear fault
```

## Step 4: Motor Enable (cmd 1)

```python
can.send_command(motor_id, 1)  # Enable
time.sleep(0.05)               # Stabilization delay
```

## Step 5: Velocity Limit (cmd 36/37, before position control)

```python
speed_raw = int(abs(deg_per_sec) * gear_ratio * 100.0 / 360.0)
can.send_command(motor_id, 36, param=speed_raw)    # Positive limit
can.send_command(motor_id, 37, param=-speed_raw)   # Negative limit
time.sleep(0.02)
```

## Step 6: Command

| Mode | CMD | Parameter |
|------|-----|-----------|
| Position (direct) | 30 | encoder counts |
| Position (trapezoid) | 31 | encoder counts |
| Speed | 29 | speed command |
| Current | 28 | milliamps |
| Emergency Stop | 82 | 0 |

## Step 7: Shutdown (ALWAYS execute)

```python
can.send_command(motor_id, 2)  # Disable motor
can.close()                     # VCI_CloseDevice
```

## Safety Limits

| Parameter | Limit | Constant |
|-----------|-------|----------|
| Position | ±716° (±12.5 rad) | MAX_POSITION_DEG |
| Speed | ±1031°/s (±18 rad/s) | MAX_SPEED_DPS |
| Current | ±40,000 mA (40A) | MAX_CURRENT_MA |
| Home warning | 30° (use trapezoid above) | HOME_WARN_DEG |

## CAN Channel Mapping (verified)

| Channel | CAN IDs | Arm |
|---------|---------|-----|
| CH0 | 16-22 | Left arm |
| CH1 | 23-29 | Right arm |

## Mirror Sign Convention

Left arm: +1, Right arm: -1 (sign inversion required, collision risk if omitted)
