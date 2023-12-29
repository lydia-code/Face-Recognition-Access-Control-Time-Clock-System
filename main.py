import cv2
import face_recognition
import numpy as np
from scipy.spatial import distance
from PIL import ImageFont, ImageDraw, ImageTk, Image
import tkinter as tk
from datetime import datetime
import pandas as pd
import paho.mqtt.client as mqtt
import threading
import os


font_label = ('Arial', 32)
font_button = ('Arial', 24)
font_label2 = ('Arial', 18)
main_window = tk.Tk()
main_window.geometry('700x680')
videoFrame = tk.Frame(main_window,bg = 'white').pack()
cap = cv2.VideoCapture(0)
ui_display = tk.Label(videoFrame)
ui_display.pack()

r1 = tk.Label(main_window,text='',font=font_label)
b1 = tk.Button(main_window,text='下班',font=font_button)
b2 = tk.Button(main_window,text='上班',font=font_button)
r2 = tk.Label(main_window,text='',font=font_label2)

output_path = "records.xlsx"
b_data = pd.DataFrame(columns=["id", "name", "state" , "date", "time"])
try:
    b_data = pd.read_excel(output_path, engine='openpyxl')
except FileNotFoundError:
    b_data = pd.DataFrame(columns=["id", "name", "state", "date", "time"])

# 從dlib加載人臉識別模型
face_rec_model = face_recognition.api.face_encodings

# 使用face_recognition獲取人臉嵌入的函數
def get_face_embedding(face_image):
    rgbface = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
    #print('face_image', face_image)
    face_embedding = face_rec_model(rgbface)
    #face_embedding = face_rec_model(face_image)
    return face_embedding[0] if len(face_embedding) > 0 else None

# 計算兩個人臉嵌入之間的相似度的函數
def cosine_similarity(embedding1, embedding2):
    return 1 - distance.cosine(embedding1, embedding2)

# 從面部嵌入列表中查找最相似面部的函數
def find_most_similar(target_embedding, face_embeddings):
    similarities = [cosine_similarity(target_embedding, embedding) for embedding in face_embeddings]
    most_similar_index = np.argmax(similarities)
    most_similar_similarity = similarities[most_similar_index]
    #print(similarities)
    return most_similar_index, most_similar_similarity




# 捕獲幀、檢測人臉並保存嵌入的功能
def grab_face_and_save_embedding():
        global b_data
        ret, frame = cap.read()  
        frame1 = frame.copy()
            # Convert the frame to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame1)
            # Get face locations using face_recognition
        face_locations = face_recognition.face_locations(rgb_frame)
            #print(rgb_frame)
        for face_location in face_locations:
            # Extract face location coordinates (top, right, bottom, left)
            top, right, bottom, left = face_location
            
            # Crop the face region from the frame
            face_image = frame[top:bottom, left:right]
            face_embedding = get_face_embedding(face_image)
            # Get the face embedding using face_recognition
            
            similarity_threshold = 0.92
            if face_embedding is not None:
                target=face_embedding 
                most_similar_index, most_similar_similarity = find_most_similar(target, face_embeddings)
                if most_similar_similarity >= similarity_threshold:
                    id,score=find_most_similar(target,face_embeddings)
                    #frame=draw_text(frame,database[id][0],(left-20, top-20))       
                    target_id = data.iloc[id][1]
                    number = data.iloc[id][0]
                #print(target_id)
                    #if target_id in data == True:
                    
                    mqtt_send_msg = "open"
                    client.publish(mqtt_topic_tx, mqtt_send_msg)

                else:
                    target_id = '非公司人員'
                #r1.config(text=f"{target_id}")
                


            else:
                target_id = '非公司人員'
            r1.config(text=f"{target_id}")
            if b1.cget("state") == "active":
                date1 = datetime.now().strftime("%Y-%m-%d")
                time1 = datetime.now().strftime("%H:%M:%S")
                work = '下班打卡'
                r2_text = f"{target_id}-{work}-{date1}-{time1}"
                r2.config(text=r2_text)

                b_data = b_data.append({"id":number, "name": target_id, "state": work, "date": date1, "time": time1}, ignore_index=True)
                b_data.to_excel(output_path, index=False, sheet_name="Sheet1")
                
            
            if b2.cget("state") == "active":
                date1 = datetime.now().strftime("%Y-%m-%d")
                time1 = datetime.now().strftime("%H:%M:%S")
                work = '上班打卡'
                r2_text = f"{target_id}-{work}-{date1}-{time1}"
                r2.config(text=r2_text)
                
                b_data = b_data.append({"id":number, "name": target_id, "state": work, "date": date1, "time": time1}, ignore_index=True)
                b_data.to_excel(output_path, index=False, sheet_name="Sheet1")
                #with open("Attendance_record.txt", "a") as file:
                    #file.write(r2_text + "\n")
            

            
        frame2 = Image.fromarray(rgb_frame)
        capture_tk = ImageTk.PhotoImage(image=frame2)
        ui_display.imgtk = capture_tk
        ui_display.configure(image=capture_tk)
        ui_display.after(1, grab_face_and_save_embedding) 
        

if __name__ == "__main__":
#load face db
    path = 'employee_records.xlsx'
    data = pd.read_excel(path, engine='openpyxl')
    face_embeddings=[]        
    db_dir='photos/npy/'
    
    for index, row in data.iterrows():
        #print(data)
        face_embeddings.append(np.load(db_dir+row[3]))

mqtt_server = "mqttgo.io"
mqtt_port = 1883
mqtt_topic_tx = "MQTT/1234"
mqtt_topic_rx = "MQTT/re"

item_on = False

# 子執行緒的工作函數
def mqtt_sub():
    client.loop_forever()
  
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(mqtt_topic_rx)


# 當接收到從伺服器發送的訊息時要進行的動作
def on_message(client, userdata, msg):
    global item_on
    # 轉換編碼utf-8才看得懂中文
    print(msg.topic+" "+ msg.payload.decode('utf-8'))
    if(msg.payload.decode('utf-8') == "s0"):
        item_on = True
        print("item_on is on")
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_server, mqtt_port, 60)
# 建立一個子執行緒，拿來做mqtt sub
t = threading.Thread(target = mqtt_sub)
# 執行該子執行緒
t.start()



grab_face_and_save_embedding()

#output_path = "records.xlsx"
#b_data.to_excel(output_path, index=False, sheet_name="Sheet1")
#print(f"Records saved to {output_path}")


b1.place(x=420, y=550)
b2.place(x=220, y=550)
r1.place(x=300, y=495)
r2.place(x=180, y=620)
main_window.update()
main_window.mainloop()

