import pyrealsense2 as rs
import numpy as np
import cv2
import mediapipe as mp

# MediaPipe 손 인식 초기화
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# RealSense 설정
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

align_to = rs.stream.color
align = rs.align(align_to)

pipeline.start(config)

# 창 크기 조절 가능하게
cv2.namedWindow('Rock Paper Scissors', cv2.WINDOW_NORMAL)

# 화면 확대 비율 설정 (2배)
SCALE_FACTOR = 2.0

def count_fingers(hand_landmarks, handedness):
    """
    펴진 손가락 개수를 세는 함수
    """
    finger_tips = [8, 12, 16, 20]  # 검지, 중지, 약지, 새끼 끝
    finger_pips = [6, 10, 14, 18]  # 각 손가락의 두 번째 관절
    
    fingers_up = []
    
    # 엄지 체크 (왼손/오른손 구분)
    if handedness == "Right":
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
    else:
        if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
    
    # 나머지 4개 손가락 체크
    for tip, pip in zip(finger_tips, finger_pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
    
    return fingers_up

def recognize_gesture(fingers_up):
    """
    손가락 상태로 가위바위보 판단
    """
    finger_count = sum(fingers_up)
    
    # 보: 5개 손가락 모두 펴짐
    if finger_count == 5:
        return "보 (Paper)", (0, 255, 0)
    
    # 가위: 2개 손가락 펴짐
    elif finger_count == 2:
        if fingers_up[1] == 1 and fingers_up[2] == 1:
            return "가위 (Scissors)", (255, 255, 0)
        else:
            return f"{finger_count}개", (255, 255, 255)
    
    # 바위: 0~1개 손가락 펴짐
    elif finger_count <= 1:
        return "바위 (Rock)", (0, 0, 255)
    
    # 그 외
    else:
        return f"{finger_count}개", (255, 255, 255)

try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()
        
        if not color_frame or not depth_frame:
            continue
        
        color_image = np.asanyarray(color_frame.get_data())
        
        # RGB로 변환
        rgb_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        
        # 손 인식
        results = hands.process(rgb_image)
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                   results.multi_handedness):
                # 손 랜드마크 그리기
                mp_drawing.draw_landmarks(
                    color_image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
                
                # 왼손/오른손 확인
                hand_label = handedness.classification[0].label
                
                # 손가락 개수 세기
                fingers_up = count_fingers(hand_landmarks, hand_label)
                
                # 가위바위보 판단
                gesture, color = recognize_gesture(fingers_up)
                
                # 손목 위치
                wrist = hand_landmarks.landmark[0]
                wrist_x = int(wrist.x * 640)
                wrist_y = int(wrist.y * 480)
                
                # ⭐ 좌표 범위 체크 (에러 방지)
                wrist_x = max(0, min(wrist_x, 639))
                wrist_y = max(0, min(wrist_y, 479))
                
                # 거리 측정
                try:
                    distance = depth_frame.get_distance(wrist_x, wrist_y)
                except:
                    distance = 0.0
                
                # 결과 표시
                cv2.putText(color_image, gesture, 
                           (max(10, wrist_x - 50), max(40, wrist_y - 80)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           1.5, color, 3)
                
                cv2.putText(color_image, f"{hand_label} hand", 
                           (max(10, wrist_x - 50), max(80, wrist_y - 120)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (255, 255, 255), 2)
                
                cv2.putText(color_image, f"Distance: {distance:.2f}m", 
                           (max(10, wrist_x - 50), max(20, wrist_y - 40)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           0.6, (255, 255, 0), 2)
                
                # 콘솔 출력
                print(f"{hand_label}: {gesture} - Fingers: {sum(fingers_up)}")
        
        # ⭐ 이미지 확대 (실제 화면 크기 키우기)
        enlarged_image = cv2.resize(color_image, None, 
                                    fx=SCALE_FACTOR, fy=SCALE_FACTOR, 
                                    interpolation=cv2.INTER_LINEAR)
        
        cv2.imshow('Rock Paper Scissors', enlarged_image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
    hands.close()
