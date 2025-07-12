import os
import cv2
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "YourDatabaseURL",
    "storageBucket": "YourStorageBucketURL"
})

bucket = storage.bucket()  
capture = cv2.VideoCapture(0)
if not capture.isOpened():
    print("Failed to open camera.")
    exit()
ret, img = capture.read()
if not ret:
    print("Failed to grab frame.")
    exit()

capture.set(cv2.CAP_PROP_FRAME_WIDTH, 697)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 438)

imgbackground= cv2.imread('Resourses\\background.png')
foldermodepath='Resourses\\modes'
modepathlist=os.listdir(foldermodepath)
imgmodelist = []
for i in modepathlist:
    imgmodelist.append(cv2.imread(os.path.join(foldermodepath, i)))
#print(len(imgmodelist))

#print("Available modes:" + str(modepathlist))

#load the encodings
file = open('encodings.p', 'rb')
encodeListWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListWithIds
print("Encoding loaded successfully.")

modeType = 0
id=-1
counter = 0
StudentImg=[]



while True:
    success, img = capture.read()
    img_resized = cv2.resize(img, (697, 438))

    imgS= cv2.resize(img_resized, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame= face_recognition.face_locations(imgS)
    encodeCurFrame= face_recognition.face_encodings(imgS, faceCurFrame)


    imgbackground[158:158+438,101:101+697] = img_resized
    imgbackground[87:87+633,866:866+414] = imgmodelist[modeType]


    if faceCurFrame:
        for encodeFace, faceLoc in zip (encodeCurFrame, faceCurFrame):
            matches= face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            #print("matches:", matches)
            #print("faceDis:", faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = studentIds[matchIndex].upper()
                #print("Name:", name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox= (101 + x1,158 + y1, x2 - x1, y2 - y1)
                imgbackground = cvzone.cornerRect(imgbackground, bbox, rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgbackground, "Recognizing...", (200, 300))
                    cv2.imshow('Background', imgbackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1



        if counter != 0:

            if counter == 1:
                StudentInfo = db.reference(f'Students/{id}').get()
                #print("StudentInfo:", StudentInfo) 
                blob = bucket.blob(f'images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8) 
                StudentImg= cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                # Update last attendance time
                datetimeObj= datetime.strptime(StudentInfo['last_attendance'], "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now() - datetimeObj).total_seconds()

                print(secondElapsed)
                # Update attendance count
                
                if secondElapsed > 30:
                    print("Updating attendance...")
                    # Update attendance in Firebase
                    ref = db.reference(f'Students/{id}')
                    StudentInfo['attendance'] += 1

                    ref.child('attendance').set(StudentInfo['attendance'])
                    ref.child('last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    print(f"✅ Attendance updated for {StudentInfo['name']}. New count: {StudentInfo['attendance']}")
               
                else:
            
                    modeType = 3
                    counter = 0
                    imgbackground[87:87+633,866:866+414] = imgmodelist[modeType]
              

                


            if modeType != 3:
                    
                if 10 < counter < 20:
                    modeType = 2
                
                imgbackground[87:87+633,866:866+414] = imgmodelist[modeType]

                
                if counter <= 10:
                    cv2.putText(imgbackground, str(StudentInfo['attendance']), (866 + 70, 165), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    
                    cv2.putText(imgbackground, str(id), (866 + 168, 556), cv2.FONT_HERSHEY_COMPLEX, 0.80, (255, 255, 255), 2)
                    cv2.putText(imgbackground, str(StudentInfo['branch']), (866 + 168, 614), cv2.FONT_HERSHEY_COMPLEX, 0.80, (255, 255, 255), 2)
                    cv2.putText(imgbackground, str(StudentInfo['year']), (1006 + 67, 667), cv2.FONT_HERSHEY_COMPLEX, 0.60, (90, 90, 90), 1)
                    cv2.putText(imgbackground, str(StudentInfo['yearOfJoining']), (1006 + 169, 667), cv2.FONT_HERSHEY_COMPLEX, 0.60, (90, 90, 90), 1)
                    cv2.putText(imgbackground, str(StudentInfo['section']), (866 + 94, 667), cv2.FONT_HERSHEY_COMPLEX, 0.60, (90, 90, 90), 1)

                    (w, h), _ = cv2.getTextSize(str(StudentInfo['name']), cv2.FONT_HERSHEY_COMPLEX, 1, 2)
                    offset = (414 - w) // 2
                    cv2.putText(imgbackground, str(StudentInfo['name']), (866 + offset, 498), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 2)
                    imgbackground[220:220+216, 965:965+216] = StudentImg 

                
                counter += 1


                if counter >= 20:
                    counter = 0
                    modeType = 0
                    StudentImg = []
                    StudentInfo=[]
                    imgbackground[87:87+633,866:866+414] = imgmodelist[modeType]

    else:
        modeType = 0
        counter = 0



    cv2.imshow('Background', imgbackground)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break








