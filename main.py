import cv2
import customtkinter as ctk
from tkinter import Tk, Label, messagebox
from PIL import Image, ImageTk
import re
import json
import os
import shutil
import glob
import subprocess
import platform
import datetime
from rt100 import aggregate_class_counts
from tp import print_now

# install picamera2
# sudo apt install -y python3-picamera2

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("files/th.json")


try:
    from picamera2 import Picamera2
    picamera2_available = True
except ImportError:
    picamera2_available = False


class PrintInfo(ctk.CTk):
    def __init__(self, all_class_counts):
    # def __init__(self):
        super().__init__()
        self.geometry("800x640")
        self.title("CELLUMATIC")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=2)
        self.grid_rowconfigure(3, weight=1)
  
        self.all_class_counts = all_class_counts  
        # self.all_class_counts = {}
        print(self.all_class_counts)

        # 1st col
        self.title_text = ctk.CTkLabel(self, text="Patient's Information", font=('Arial', 20, 'bold'))
        self.title_text.grid(row=0, column=0, padx=40, pady=(20,0), sticky="nsew")

        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.grid(row=1, column=0, padx=(20,10), pady=(0,20), sticky="nsew")
        self.load_and_display_json()

        # 2nd col
        self.title_stats_text = ctk.CTkLabel(self, text="Differential Count", font=('Arial', 20, 'bold'))
        self.title_stats_text.grid(row=0, column=1, padx=40, pady=(20,0), sticky="nsew")

        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=1, column=1, padx=(10,20), pady=(0,20), sticky="nsew")
        
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)
        self.stats_frame.grid_columnconfigure(2, weight=1)

        self.data = [
            ("Segmenters", "0.51-0.67", str(self.all_class_counts.get("neutro", "0"))),
            ("Lymphocytes", "0.33-0.49", str(self.all_class_counts.get("lympho", "0"))),
            ("Monocytes", "0.02-0.06", str(self.all_class_counts.get("mono", "0"))),
            ("Eosinophil", "0.01-0.04", str(self.all_class_counts.get("eosino", "0"))),
            ("Basophil", "0.0-0.01", str(self.all_class_counts.get("baso", "0")))
        ]

        self.header1 = ctk.CTkLabel(self.stats_frame, text="Differential Count", font=('Arial', 16))
        self.header1.grid(row=0, column=0, padx=20, pady=(20,0), sticky="w")
        self.header2 = ctk.CTkLabel(self.stats_frame, text="Normal", font=('Arial', 16))
        self.header2.grid(row=0, column=1, padx=20, pady=(20,0), sticky="w")
        self.header3 = ctk.CTkLabel(self.stats_frame, text="Result", font=('Arial', 16))
        self.header3.grid(row=0, column=2, padx=20, pady=(20,0), sticky="w")

        for i, (cell_type, normal_value, result) in enumerate(self.data, start=1):
            ctk.CTkLabel(self.stats_frame, text=cell_type, font=('Arial', 20, 'bold')).grid(row=i, column=0, padx=20, pady=5, sticky="w")
            ctk.CTkLabel(self.stats_frame, text=normal_value, font=('Arial', 20, 'bold')).grid(row=i, column=1, padx=20, pady=5, sticky="w")
            ctk.CTkLabel(self.stats_frame, text=result, font=('Arial', 20, 'bold')).grid(row=i, column=2, padx=20, pady=5, sticky="w")

        # 3rd row
        self.print_button = ctk.CTkButton(self, text="PRINT",  font=('Arial', 24, 'bold'), command=self.sent_print)
        self.print_button.grid(row=2, columnspan=2, padx=20, pady=(30,20), sticky="nsew")

        self.back_button = ctk.CTkButton(self, text="Back",  font=('Arial', 24, 'bold'), fg_color="grey", hover_color="#5A5A5A", command=self.go_back)
        self.back_button.grid(row=3, column=0, padx=20, pady=(10,40), sticky="nsew")
        
        self.done_button = ctk.CTkButton(self, text="Done",  font=('Arial', 24, 'bold'), fg_color="green", hover_color="#006400", command=self.finished)
        self.done_button.grid(row=3, column=1, padx=20, pady=(10,40), sticky="nsew")


    def load_and_display_json(self):
        with open('user/patient_info.json', 'r') as file:
            data = json.load(file)
        labels = ["Name", "Address", "Date of Birth", "Age", "Sex"]
        attributes = ["name", "address", "date", "age", "sex"]

        self.header1 = ctk.CTkLabel(self.entry_frame, text=" ", font=('Arial', 16))
        self.header1.grid(row=0, column=0, padx=20, pady=(20,0), sticky="w")
        for i, (label, attr) in enumerate(zip(labels, attributes), start=1):
            ctk.CTkLabel(self.entry_frame, text=f"{label}: {data.get(attr, 'N/A')}", font=('Arial', 20, "bold")).grid(row=i, column=0, padx=20, pady=(10,0), sticky="w")


    def sent_print(self):
        print("printing")
        data_dict = {item[0]: item[1:] for item in self.data}
        print_now(data_dict)

    def finished(self):
        self.quit()
        self.destroy()
        clear_directory("user")
        app = MainMenu()
        app.after(500, lambda: app.wm_attributes('-fullscreen', 'true'))
        app.bind("<F11>", lambda event: app.attributes("-fullscreen", not app.attributes("-fullscreen")))
        app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
        app.mainloop()

    def go_back(self):
        self.quit()
        self.destroy()
        app = CameraApp()
        app.after(500, lambda: app.wm_attributes('-fullscreen', 'true'))
        app.bind("<F11>", lambda event: app.attributes("-fullscreen", not app.attributes("-fullscreen")))
        app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
        app.mainloop()



class CameraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1200x600")
        self.title("CELLUMATIC")

        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Frame for live camera feed
        self.live_view_frame = ctk.CTkFrame(self)
        self.live_view_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_label = Label(self.live_view_frame)
        self.video_label.pack(fill="both", expand=True)

        # right
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.controls_frame.grid_columnconfigure(0, weight=4)
        self.controls_frame.grid_rowconfigure(0, weight=1)
        self.controls_frame.grid_rowconfigure(1, weight=1)
        self.controls_frame.grid_rowconfigure(2, weight=2)
        self.controls_frame.grid_rowconfigure(3, weight=5)
        self.controls_frame.grid_rowconfigure(4, weight=1)
        self.controls_frame.grid_rowconfigure(5, weight=1)
        self.controls_frame.grid_rowconfigure(6, weight=1)

        if picamera2_available:
            self.start_button_picamera2 = ctk.CTkButton(self.controls_frame, text="Start Pi Camera", command=self.start_pi_camera, font=("Arial", 16, "bold"))
            self.start_button_picamera2.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        else:
            self.start_button_usb = ctk.CTkButton(self.controls_frame, text="Start USB Camera", command=self.start_usb_camera, font=("Arial", 16, "bold"))
            self.start_button_usb.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        self.num_images = ctk.CTkLabel(self.controls_frame, text="Images: ", font=('Arial', 14, 'bold'))
        self.num_images.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")
        self.capture_button = ctk.CTkButton(self.controls_frame, text="Capture", command=self.capture_image, fg_color="green", hover_color="#006400", font=("Arial", 16, "bold"))
        self.capture_button.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.open_folder = ctk.CTkButton(self.controls_frame, text="Open Captured Images", command=self.open_images, font=("Arial", 16, "bold"))
        self.open_folder.grid(row=4, column=0, sticky="nsew", padx=20, pady=10)

        self.back_button = ctk.CTkButton(self.controls_frame, text="Back", command=self.open_patientinfo, fg_color="grey", hover_color="#5A5A5A", font=("Arial", 16, "bold"))
        self.back_button.grid(row=5, column=0, sticky="nsew", padx=20, pady=10)
        self.next_button = ctk.CTkButton(self.controls_frame, text="Next", command=self.open_printpage, fg_color="green", hover_color="#006400", font=("Arial", 16, "bold"))
        self.next_button.grid(row=6, column=0, sticky="nsew", padx=20, pady=10)

        self.camera_source = None
        self.captured_images = []
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.update_images_count_id = None
        self.video_label_id = None

    def open_printpage(self):
        self.close_camera()
        photos_path = 'user/photos'
        all_class_counts = aggregate_class_counts(photos_path)
        self.quit()
        self.destroy()
        app = PrintInfo(all_class_counts)
        app.after(500, lambda: app.wm_attributes('-fullscreen', 'true'))
        app.bind("<F11>", lambda event: app.attributes("-fullscreen", not app.attributes("-fullscreen")))
        app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
        app.mainloop()


    def open_patientinfo(self):
        self.close_camera()
        self.destroy()
        clear_directory("user/photos")
        app = PatientInfo()
        app.after(500, lambda: app.wm_attributes('-fullscreen', 'true'))
        app.bind("<F11>", lambda event: app.attributes("-fullscreen", not app.attributes("-fullscreen")))
        app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
        app.mainloop()


    def start_usb_camera(self):
        self.start_button_usb.configure(state='disabled')
        self.camera_source = cv2.VideoCapture(0)
        self.update_video_label()


    def start_pi_camera(self):
        self.start_button_picamera2.configure(state='disabled')
        self.camera_source = Picamera2()
        self.camera_source.configure(self.camera_source.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
        self.camera_source.start()
        self.update_video_label()


    def update_video_label(self):
        frame = None
        if isinstance(self.camera_source, cv2.VideoCapture):
            ret, frame = self.camera_source.read()
            if not ret:
                print("Failed to capture frame from camera.")
                frame = None
        elif picamera2_available and isinstance(self.camera_source, Picamera2):
            try:
                frame = self.camera_source.capture_array()
            except Exception as e:
                print(f"Failed to capture frame from Picamera2: {e}")
                frame = None

        if frame is not None:
            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=im)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            except Exception as e:
                print(f"Error processing frame: {e}")
        else:
            print("No frame to display.")

        self.video_label_id = self.video_label.after(10, self.update_video_label)


    def capture_image(self):
        save_folder = "user/photos"
        os.makedirs(save_folder, exist_ok=True)

        if self.camera_source is not None and not picamera2_available:
            ret, frame = self.camera_source.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                timestamp = datetime.datetime.now().strftime("%H-%M-%S-%f")[:-3]
                filename = os.path.join(save_folder, f"photo_{timestamp}.png")
                image.save(filename)
                self.update_images_count_label()
        elif self.camera_source is not None and picamera2_available:
            try:
                frame = self.camera_source.capture_array()  # Captures the frame as a numpy array
                image = Image.fromarray(frame)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
                filename = os.path.join(save_folder, f"photo_{timestamp}.png")
                image.save(filename)  # Save the image file
                print(f"Image saved as {filename}")
                self.update_images_count_label()  # Update GUI or print confirmation
            except Exception as e:
                print(f"Failed to capture image: {e}")


    def update_images_count_label(self):
        folder_path = "user/photos"
        image_count = len(glob.glob(os.path.join(folder_path, "*.png")))
        self.num_images.configure(text=f"Images: {image_count}")

        if image_count >= 20:
            self.capture_button.configure(state='disabled')
        else:
            self.capture_button.configure(state='normal')

        self.update_images_count_id = self.after(1000, self.update_images_count_label)


    def close_camera(self):
        if isinstance(self.camera_source, cv2.VideoCapture):
            self.camera_source.release()
        elif picamera2_available and isinstance(self.camera_source, Picamera2):
            self.camera_source.stop_preview()


    def open_images(self):
        folder_path = os.path.join(self.base_path, "user/photos")
        os.makedirs(folder_path, exist_ok=True)
        if platform.system() == "Windows":
            os.startfile(folder_path)
        else:
            subprocess.run(["xdg-open", folder_path])



class PatientInfo(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x640")
        self.title("CELLUMATIC")

        # Create a frame to hold the entries and labels
        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")

        # Configure the grid within the frame for layout
        self.entry_frame.grid_rowconfigure(0, weight=1)
        self.entry_frame.grid_rowconfigure(1, weight=1)
        self.entry_frame.grid_rowconfigure(2, weight=1)
        self.entry_frame.grid_rowconfigure(3, weight=1)
        self.entry_frame.grid_rowconfigure(4, weight=1)
        self.entry_frame.grid_rowconfigure(5, weight=1)
        self.entry_frame.grid_columnconfigure(0, weight=1)
        self.entry_frame.grid_columnconfigure(1, weight=1)

        # Adjusting main window grid configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=4)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_text = ctk.CTkLabel(self, text="Patient's Information", font=('Arial', 20, 'bold'))
        self.title_text.grid(row=0, padx=40, pady=(20,0), sticky="nsew")

        # Place labels and entries inside the frame
        self.u_name_lbl = ctk.CTkLabel(self.entry_frame, text="Name", font=('Arial', 14, 'bold'))
        self.u_name_lbl.grid(row=0, column=0, padx=40, pady=0, sticky="sw")
        self.u_name = ctk.CTkEntry(self.entry_frame, placeholder_text="Name",  font=('Arial', 18, 'bold'),  textvariable=self.create_uppercase_var())
        self.u_name.grid(row=1, column=0, padx=40, pady=(0,10), sticky="nsew")

        self.u_addr_lbl = ctk.CTkLabel(self.entry_frame, text="Address", font=('Arial', 14, 'bold'))
        self.u_addr_lbl.grid(row=2, column=0, padx=40, pady=0, sticky="sw")
        self.u_addr = ctk.CTkEntry(self.entry_frame, placeholder_text="Address",  font=('Arial', 18, 'bold'),  textvariable=self.create_uppercase_var())
        self.u_addr.grid(row=3, column=0, padx=40, pady=(0,10), sticky="nsew")

        # Place labels and entries inside the frame
        self.u_date_lbl = ctk.CTkLabel(self.entry_frame, text="Date of Birth", font=('Arial', 14, 'bold'))
        self.u_date_lbl.grid(row=0, column=1, padx=40, pady=0, sticky="sw")
        self.u_date = ctk.CTkEntry(self.entry_frame, placeholder_text="Date",  font=('Arial', 18, 'bold'),  textvariable=self.create_uppercase_var())
        self.u_date.grid(row=1, column=1, padx=40, pady=(0,10), sticky="nsew")

        self.u_age_lbl = ctk.CTkLabel(self.entry_frame, text="Age", font=('Arial', 14, 'bold'))
        self.u_age_lbl.grid(row=2, column=1, padx=40, pady=0, sticky="sw")
        self.u_age = ctk.CTkEntry(self.entry_frame, placeholder_text="Age",  font=('Arial', 18, 'bold'),  textvariable=self.create_uppercase_var())
        self.u_age.grid(row=3, column=1, padx=40, pady=(0,10), sticky="nsew")
        
        self.u_sex_lbl = ctk.CTkLabel(self.entry_frame, text="Sex", font=('Arial', 14, 'bold'))
        self.u_sex_lbl.grid(row=4, column=1, padx=40, pady=0, sticky="sw")
        self.u_sex = ctk.CTkEntry(self.entry_frame, placeholder_text="Sex",  font=('Arial', 18, 'bold'),  textvariable=self.create_uppercase_var())
        self.u_sex.grid(row=5, column=1, padx=40, pady=(0,40), sticky="nsew")

        # Place labels and entries inside the frame
        self.next_button = ctk.CTkButton(self, text="Next",  font=('Arial', 24, 'bold'), command=self.open_camera)
        self.next_button.grid(row=2, padx=100, pady=10, sticky="nsew")


    def save_to_json(self):
        patient_info = {
            "name": self.u_name.get(),
            "address": self.u_addr.get(),
            "date": self.u_date.get(),
            "age": self.u_age.get(),
            "sex": self.u_sex.get().upper() 
        }

        with open("user/patient_info.json", "w") as json_file:
            json.dump(patient_info, json_file, indent=4)
        
        return True


    def create_uppercase_var(self):
        var = ctk.StringVar()
        var.trace_add("write", lambda *args: var.set(var.get().upper()))
        return var


    def open_camera(self):
        if not all([self.u_name.get(), self.u_addr.get(), self.u_date.get(), self.u_age.get(), self.u_sex.get()]):
            messagebox.showerror("Error", "All fields must be filled out")
            return
        
        if not self.u_age.get().isdigit():
            messagebox.showerror("Error", "Age must be a number")
            return

        if not re.match(r"\d{2}-\d{2}-\d{4}", self.u_date.get()):
            messagebox.showerror("Error", "Date must be in MM-DD-YYYY format")
            return

        if self.u_sex.get().upper() not in ["MALE", "FEMALE"]:
            messagebox.showerror("Error", "Sex must be either MALE or FEMALE")
            return

        if self.save_to_json(): 
            self.destroy()
            app = CameraApp()
            app.after(500, lambda: app.wm_attributes('-fullscreen', 'true'))
            app.bind("<F11>", lambda event: app.attributes("-fullscreen", not app.attributes("-fullscreen")))
            app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
            app.mainloop()



class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x640")
        self.title("CELLUMATIC")
        self.init_ui()

    def init_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.my_image = ctk.CTkImage(light_image=Image.open("files/logo.png"),
                                        dark_image=Image.open("files/logo.png"),
                                        size=(320, 320))

        self.image_label = ctk.CTkLabel(self, image=self.my_image, text="")
        self.image_label.grid(row=0, padx=100, pady=(50,10), sticky="nsew")

        self.open_camera_button = ctk.CTkButton(self, text="START",  font=('Arial', 24, 'bold'), command=self.patient_info)
        self.open_camera_button.grid(row=1, padx=100, pady=10, sticky="nsew")

    def patient_info(self):
        self.destroy()
        app = PatientInfo()
        app.after(500, lambda: app.wm_attributes('-fullscreen', 'true'))
        app.bind("<F11>", lambda event: app.attributes("-fullscreen", not app.attributes("-fullscreen")))
        app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
        app.mainloop()


def clear_directory(directory_path):
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


if __name__ == "__main__":
    clear_directory("user")
    
    app = MainMenu()
    app.after(500, lambda: app.wm_attributes('-fullscreen', 'true'))
    app.bind("<F11>", lambda event: app.attributes("-fullscreen", not app.attributes("-fullscreen")))
    app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
    app.mainloop()