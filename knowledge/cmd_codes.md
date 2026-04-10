# TI5 CAN Command Code Reference

## Core Commands

| CMD | Name | Direction | Parameter | Description |
|-----|------|-----------|-----------|-------------|
| 1 | MOTOR_ENABLE | Write | None | Enable motor drive |
| 2 | MOTOR_DISABLE | Write | None | Disable motor drive |
| 3 | GET_RUN_MODE | Read | — | Current control mode |
| 4 | GET_IQ | Read | — | Measured Iq current |
| 5 | GET_IQ_REF | Read | — | Reference Iq current |
| 6 | GET_SPEED | Read | — | Current speed |
| 7 | GET_SPEED_REF | Read | — | Reference speed |
| 8 | GET_CURRENT_POSITION | Read | — | Current position (262,144 cnt/rev) |
| 9 | GET_TARGET_POSITION | Read | — | Target position |
| 10 | GET_STATUS | Read | — | Error status (0=Normal, 1-9=Error) |
| 11 | CLEAR_FAULT | Write | None | Acknowledge/clear fault |
| 20 | GET_BUS_VOLTAGE | Read | — | DC bus voltage |
| 28 | SET_TARGET_CURRENT | Write | int32 mA | Target current (milliamps) |
| 29 | SET_TARGET_SPEED | Write | int32 | Target speed (SDK units) |
| 30 | SET_TARGET_POSITION | Write | int32 counts | Target position (direct) |
| 31 | SET_TARGET_POSITION_TRAPEZOID | Write | int32 counts | Target position (trapezoid profile) |
| 36 | SET_VELOCITY_LIMIT_POS | Write | int32 | Positive velocity limit |
| 37 | SET_VELOCITY_LIMIT_NEG | Write | int32 | Negative velocity limit |
| 49 | GET_TEMP | Read | — | Motor coil temperature |
| 50 | GET_HEATSINK_TEMP | Read | — | Heatsink temperature |
| 82 | EMERGENCY_STOP | Write | 0 | Emergency stop (zero current) |
| 84 | GET_POSITION_OFFSET | Read | — | Position offset |
| 100 | GET_MOTOR_MODEL | Read | — | Motor model register |
| 101 | GET_HW_VERSION | Read | — | Hardware version |

## CAN Frame Format

- Read command: DataLen=1, Data[0]=cmd_code
- Write command: DataLen=5, Data[0]=cmd_code, Data[1..4]=param (little-endian int32)
- Response: DataLen=5, Data[0]=cmd_code, Data[1..4]=value (little-endian int32)
- CAN ID: Standard 11-bit, range 1-40

## Error Status Codes (cmd 10 response)

| Code | Meaning |
|------|---------|
| 0 | Normal |
| 1 | SoftwareError |
| 2 | Overvoltage |
| 3 | Undervoltage |
| 4 | StartupError |
| 5 | SpeedFeedbackError |
| 6 | Overcurrent |
| 7 | EncoderCommunicationError |
| 8 | MotorTemperatureTooHigh |
| 9 | PCBTemperatureTooHigh |

## EEPROM Save Warning

- RAM changes require cmd 14 to persist to EEPROM
- Only cmd 46 (ID change) auto-saves
- **cmd 46 FORBIDDEN** without explicit user confirmation (can brick motor)
