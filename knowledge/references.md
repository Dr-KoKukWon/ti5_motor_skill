## 프로젝트 내 주요 파일 위치

| 리소스 | 경로 |
|--------|------|
| CAN 통신 래퍼 | `scripts/CAN_Test/ti5_can.py` |
| 모터/관절 스펙 | `scripts/Single_Motor_Test_py/single_motor_logic.py` |
| CAN 드라이버 (.so) | `scripts/CAN_Test/libcontrolcan.so` |
| 프로젝트 문서 | `docs/` (이슈: `docs/issues_and_fixes/`) |
| 원점 설정 파일 | `config/motor_home_position.yaml` |

---

# TI5 External References

## Official Links

| Resource | URL |
|----------|-----|
| GitHub Organization | https://github.com/ti5robot |
| Gitee Mirror | https://gitee.com/ti5robot |
| Official Website | https://www.ti5robot.com |

## Core SDK Repositories

| Repo | URL | Description |
|------|-----|-------------|
| multiMotorInterfaceCPP | https://github.com/ti5robot/multiMotorInterfaceCPP | Multi-motor CAN SDK (135KB), **current project uses this** |
| mechanical_arm_5_0_SDK | https://github.com/ti5robot/mechanical_arm_5_0_SDK | Single arm 6-DOF SDK (1.4MB) |
| mechanical_arm_5_0_python | https://github.com/ti5robot/mechanical_arm_5_0_python | Python bindings for arm SDK |
| multiMotorTCPAPI | https://github.com/ti5robot/multiMotorTCPAPI | TCP/IP motor control |

## Humanoid Arm Control

| Repo | URL | Description |
|------|-----|-------------|
| HumanoidDualArmSolver | https://github.com/ti5robot/HumanoidDualArmSolver | Dual-arm 7-DOF×2 IK/FK solver |
| LeftArmMotionSolver | https://github.com/ti5robot/LeftArmMotionSolver | Left arm IK/FK |
| RightArmMotionSolver | https://github.com/ti5robot/RightArmMotionSolver | Right arm IK/FK |

## ROS Integration

| Repo | URL | ROS Version |
|------|-----|-------------|
| ROS2Ti5DualArmManipulation | https://github.com/ti5robot/ROS2Ti5DualArmManipulation | ROS 2 + MoveIt2 |
| ROS2humble | https://github.com/ti5robot/ROS2humble | ROS 2 Humble env |
| Ti5HandROS2SDK | https://github.com/ti5robot/Ti5HandROS2SDK | 5-finger hand (RS485) |

## Simulation

| Repo | URL | Platform |
|------|-----|----------|
| ti5_mujoco (Kong) | Community | MuJoCo, 29-DOF, CPU |
| ti5_isaaclab (Kong) | Community | Isaac Lab, 29-DOF, GPU |

## SDK Architecture

```
User Code → Ti5BASIC.h → libmylibti5_multi_motor.so (135KB) → libcontrolcan.so (89KB) → USB-CAN → Motor
```

## Motor Models

| Model | Gear Ratio | KT (Nm/A) | Max Torque | Used For |
|-------|-----------|----------|-----------|----------|
| CRA-RI40-52 | 101 | 0.050 | 11 Nm | Wrist |
| CRA-RI50-60 | 101 | 0.089 | 34 Nm | Elbow |
| CRA-RI60-70 | 121 | 0.096 | 66 Nm | Shoulder |

## Unconfirmed / Needed

- CRA motor full datasheet (torque curves, thermal limits)
- Motor Controls V1.1.6 software manual (only screenshots available)
- ZLG USBCAN2 driver manual (only controlcan.h API wrapped)
- ti5robot official technical manual
