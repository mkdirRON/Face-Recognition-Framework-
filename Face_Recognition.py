import os
import cv2
import sqlite3
import numpy as np
import face_recognition
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Function to initialize the database
def initialize_database(db_name="face_database.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            encoding BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to save face encoding to the database
def save_face_to_database(name, encoding, db_name="face_database.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    encoding_blob = np.array(encoding).tobytes()
    cursor.execute('INSERT INTO faces (name, encoding) VALUES (?, ?)', (name, encoding_blob))
    conn.commit()
    conn.close()
    print(f"Face encoding for '{name}' saved successfully.")

# Function to process a photo for face recognition
def process_face(photo_path):
    print("Processing face for recognition...")
    image = face_recognition.load_image_file(photo_path)
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings[0] if face_encodings else None

# --- Your Original Functions ---
def capturing_Face():
    initialize_database()
    home_directory = os.path.expanduser("~")
    path = os.path.join(home_directory, "Project_CloseEye", "Assets")

    if not os.path.exists(path):
        os.makedirs(path)

    while True:
        content = os.listdir(path)
        highest_number = 0
        for item in content:
            if item.startswith("photo_") and item.endswith(".jpg"):
                try:
                    number = int(item[6:-4])
                    highest_number = max(highest_number, number)
                except ValueError:
                    pass

        next_number = highest_number + 1
        new_file_name = f"photo_{next_number}.jpg"
        save_path = os.path.join(path, new_file_name)

        capture = cv2.VideoCapture(0)
        if not capture.isOpened():
            print("Failure to access camera")
            capture.release()
            cv2.destroyAllWindows()
            break

        while True:
            ret, frame = capture.read()
            if not ret:
                print("Failed to capture frame. Exiting...")
                break

            cv2.imshow('Capture_photo', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                print("Exiting without saving...")
                break
            elif key == 32:  # SPACE key
                cv2.imwrite(save_path, frame)
                print(f"Photo saved as {new_file_name} at {save_path}")

                face_encoding = process_face(save_path)
                if face_encoding is not None:
                    user_name = input("Enter your name for this photo: ").strip()
                    if user_name:
                        save_face_to_database(user_name, face_encoding)
                break
            elif key == ord('q'):
                continue

        capture.release()
        cv2.destroyAllWindows()
        break

def Face_Rec():
    initialize_database()
    home_dic = os.path.expanduser("~")
    InitialDir = os.path.join(home_dic, "Project_CloseEye", "Assets")

    if not os.path.exists(InitialDir):
        os.makedirs(InitialDir)

    root = tk.Tk()
    root.withdraw()

    while True:
        file_dialog = filedialog.askopenfilename(
            initialdir=InitialDir,
            title="Select a photo.",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )

        if not file_dialog:
            print("No File Selected. Exiting....")
            break

        print(f"Selected file: {file_dialog}")
        photo = cv2.imread(file_dialog)

        while True:
            if photo is None:
                print("Failure to load photo. Please Select an Accepted File Type")
                file_dialog = filedialog.askopenfilename(
                    initialdir=InitialDir,
                    title="Select a photo",
                    filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
                )
            else:
                break

        cv2.imshow("Pic", photo)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()

        if key == 27:  # ESC key
            print("Preparing file select...")
            continue
        else:
            print("Photo selected!")

            face_encoding = process_face(file_dialog)
            if face_encoding is not None:
                user_name = input("Enter your name for this photo: ").strip()
                if user_name:
                    save_face_to_database(user_name, face_encoding)
            break

# --- Database Viewer GUI ---
def database_viewer():
    initialize_database()
    root = tk.Tk()
    root.title("Face Database Viewer")
    root.geometry("500x400")

    def fetch_records():
        conn = sqlite3.connect("face_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM faces")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_record(record_id, tree):
        conn = sqlite3.connect("face_database.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faces WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Record deleted successfully.")
        display_records(tree)

    def display_records(tree):
        for row in tree.get_children():
            tree.delete(row)
        records = fetch_records()
        for record in records:
            tree.insert("", "end", values=record)

    columns = ("ID", "Name")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.pack(pady=20)

    display_records(tree)

    delete_button = tk.Button(root, text="Delete Selected Record", command=lambda: delete_selected(tree))
    delete_button.pack(pady=10)

    def delete_selected(tree):
        selected_item = tree.selection()
        if selected_item:
            record_id = tree.item(selected_item, "values")[0]
            delete_record(record_id, tree)
        else:
            messagebox.showwarning("Warning", "No record selected!")

    root.mainloop()

# --- Main Function ---
def main():
    home_dic = os.path.expanduser("~")
    InitialDir = os.path.join(home_dic, "Project_CloseEye", "Assets")

    if not os.path.exists(InitialDir):
        os.makedirs(InitialDir)

    while True:
        print("\nSelect an Option:")
        print("1. Capture a New Face")
        print("2. Recognize Face from Photo")
        print("3. View Database")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            capturing_Face()
        elif choice == "2":
            Face_Rec()
        elif choice == "3":
            database_viewer()
        elif choice == "4":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
