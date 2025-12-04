# RealSense Hand Detection & Rock-Paper-Scissors Recognition

Intel RealSense D455F 카메라를 사용한 실시간 손 인식 및 가위바위보 제스처 인식 프로젝트

## Features

- 🖐️ 실시간 손 랜드마크 감지 (MediaPipe 기반)
- 📏 손까지의 거리 측정 (RealSense Depth)
- ✊✌️✋ 가위바위보 제스처 인식
- 👥 양손 동시 인식 지원

## Hardware Requirements

- Intel RealSense D455F Depth Camera
- USB 3.0 Port
- Ubuntu 22.04 LTS

## Software Requirements

- Python 3.10+
- OpenCV
- MediaPipe
- pyrealsense2

## Installation

### 1. RealSense SDK 설치
```bash
sudo apt-get install librealsense2-dkms librealsense2-utils librealsense2-dev -y
```

### 2. Python 패키지 설치
```bash
pip install -r requirements.txt
```

또는:
```bash
pip install opencv-python mediapipe pyrealsense2 --break-system-packages
```

## Usage

### 손 랜드마크 인식 및 가위바위보 판단
```bash
python scripts/hand_detection.py
```

**기능:**
- 손 랜드마크 21개 지점 표시


**인식 로직:**
- 바위 ✊: 0~1개 손가락
- 가위 ✌️: 2개 손가락
- 보 ✋: 5개 손가락

## Hand Landmarks

MediaPipe는 21개의 손 주요 지점을 감지합니다:

- 0: 손목 (WRIST)
- 1-4: 엄지손가락
- 5-8: 검지손가락
- 9-12: 중지손가락
- 13-16: 약지손가락
- 17-20: 새끼손가락

## Project Structure
```
realsense-hand-detection/
├── README.md
├── requirements.txt
├── scripts/
│   ├── hand_detection.py       # 손 랜드마크 인식 및 가위바위보 판단
│   
└── docs/
    └── installation.md
```

## Troubleshooting

### 카메라 연결 안 됨
```bash
# USB 연결 확인
lsusb | grep Intel

# 재부팅 후 재시도
sudo reboot
```

### Depth 이미지 깨짐
- 반사 표면(유리, 금속) 피하기
- Post-Processing 필터 활성화 권장
- 0.4m~6m 거리 유지

## License

MIT License

## Author

fhekwn549

## Acknowledgments

- Intel RealSense SDK
- Google MediaPipe
- OpenCV

## Updates
- 2025-12-04: Initial release
