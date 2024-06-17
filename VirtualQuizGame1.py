import csv
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import mediapipe
import time

cap = cv2.VideoCapture(0)

cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8)


class MCQ():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userAns = None

    def update(self, cursor, bboxs):
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)


# Import CSV file
pathCSV = "Mcqs.csv"
with open(pathCSV, newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]

# Create objects for each MCQ
mcqList = []
for q in dataAll:
    mcqList.append(MCQ(q))

print("Total MCQs created: ", len(mcqList))
qNo = 0
qTotal = len(dataAll)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if qNo < qTotal:
        mcq = mcqList[qNo]
        img, bbox = cvzone.putTextRect(img, mcq.question, [100, 100], 2, 2, colorR=(255, 0, 0), offset=50, border=5, colorB=(255, 255, 255))
        img, bbox1 = cvzone.putTextRect(img, mcq.choice1, [300, 250], 2, 2, colorR=(255, 0, 0), offset=50, border=5, colorB=(255, 255, 255))
        img, bbox2 = cvzone.putTextRect(img, mcq.choice2, [800, 250], 2, 2, colorR=(255, 0, 0), offset=50, border=5, colorB=(255, 255, 255))
        img, bbox3 = cvzone.putTextRect(img, mcq.choice3, [300, 400], 2, 2, colorR=(255, 0, 0), offset=50, border=5, colorB=(255, 255, 255))
        img, bbox4 = cvzone.putTextRect(img, mcq.choice4, [800, 400], 2, 2, colorR=(255, 0, 0), offset=50, border=5, colorB=(255, 255, 255))

        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8]
            length, info, img = detector.findDistance(lmList[8][0:2], lmList[12][0:2], img)
            if 20 <= length <= 30:
                mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                print(mcq.userAns)
                if mcq.userAns is not None:
                    time.sleep(0.3)
                    qNo += 1
    else:
        score = 0
        for mcq in mcqList:
            if mcq.answer == mcq.userAns:
                score += 1
        score = round((score / qTotal) * 100, 2)
        img, _ = cvzone.putTextRect(img, "Your Quiz Completed ", [250, 300], 2, 2, colorR=(255, 0, 0), offset=50, border=5, colorB=(255, 255, 255))
        img, _ = cvzone.putTextRect(img, f'Your Score: {score}%', [700, 300], 2, 2, colorR=(255, 0, 0), offset=50, border=5, colorB=(255, 255, 255))
        print(score)
        
        # Show the final screen for a while then exit
        cv2.imshow("Image", img)
        cv2.waitKey(5000)  # Display the final score for 5 seconds
        break  # Exit the loop when the quiz is finished

    # Draw progress bar
    barValue = 150 + (950 // qTotal) * qNo
    cv2.rectangle(img, (150, 600), (barValue, 650), (0, 255, 0), cv2.FILLED)
    cv2.rectangle(img, (150, 600), (1100, 650), (255, 255, 255), 5, cv2.FILLED)
    # Percentage
    img, _ = cvzone.putTextRect(img, f'{round((qNo / qTotal) * 100)}%', [1130, 635], 2, 2, colorR=(255, 0, 0), offset=16, border=5, colorB=(255, 255, 255))

    cv2.imshow("Image", img)
    cv2.waitKey(1)

# Release the capture and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
