import tkinter as tk
import cv2
import os
from PIL import Image, ImageTk
import openpyxl
import numpy as np
import face_recognition

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("照相鏡頭應用程式")
        
        self.video_capture = cv2.VideoCapture(0)  # 訪問第一個攝像頭
        
        self.canvas = tk.Canvas(root, width=self.video_capture.get(3), height=self.video_capture.get(4))
        self.canvas.pack()
        
        self.employee_id_label = tk.Label(root, text="員工編號：")
        self.employee_id_label.pack()
        self.employee_id_entry = tk.Entry(root)
        self.employee_id_entry.pack()
        
        self.employee_name_label = tk.Label(root, text="員工姓名：")
        self.employee_name_label.pack()
        self.employee_name_entry = tk.Entry(root)
        self.employee_name_entry.pack()
        
        self.capture_button = tk.Button(root, text="拍照", command=self.capture_photo)
        self.capture_button.pack()
        
        self.update()
        
    def update(self):
        ret, frame = self.video_capture.read()
        if ret:
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.root.after(10, self.update)
        
    def capture_photo(self):
        ret, frame = self.video_capture.read()
        if ret:
            employee_id = self.employee_id_entry.get()
            if not employee_id:
                print("請輸入員工編號")
                return
            
            employee_name = self.employee_name_entry.get()
            if not employee_name:
                print("請輸入員工姓名")
                return
            
            image_name = f"{employee_name}"  # 使用姓名作為檔名
            folder_path = "photos"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            jpg_folder = os.path.join(folder_path, "jpg")
            npy_folder = os.path.join(folder_path, "npy")
            
            if not os.path.exists(jpg_folder):
                os.makedirs(jpg_folder)
            if not os.path.exists(npy_folder):
                os.makedirs(npy_folder)
            
            # 儲存成 .jpg 文件
            jpg_path = os.path.join(jpg_folder, f"{image_name}.jpg")
            cv2.imwrite(jpg_path, frame)
            print(f"照片已保存為 {jpg_path}")
            
            # 儲存成 .npy 文件
            image_array = np.array(frame)
            face_embedding = self.get_face_embedding(image_array)
            if face_embedding is not None:
                face_embedding_flattened = face_embedding.flatten()
                npy_path = os.path.join(npy_folder, f"{image_name}.npy")
                np.save(npy_path, face_embedding_flattened)
                print(f"特徵嵌入已保存為 {npy_path}")
            
            self.record_to_excel(employee_id, employee_name, jpg_path, npy_path)
    
    def get_face_embedding(self, face_image):
        rgbface = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        face_embedding = face_recognition.face_encodings(rgbface)
        return face_embedding[0].flatten() if len(face_embedding) > 0 else None
    
    def record_to_excel(self, employee_id, employee_name, jpg_path, npy_path):
        excel_file = "employee_records.xlsx"
        if not os.path.exists(excel_file):
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["員工編號", "員工姓名", "JPG檔案", "NPY檔案"])
        else:
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active

        # 取得檔案名稱的基本名稱
        jpg_filename = os.path.basename(jpg_path)
        npy_filename = os.path.basename(npy_path)

        sheet.append([employee_id, employee_name, jpg_filename, npy_filename])
        workbook.save(excel_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.mainloop()
