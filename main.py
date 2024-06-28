import os
import hashlib
from PIL import Image, ImageTk
from tkinter import Tk, filedialog, Button, Text, Scrollbar, Toplevel, Label, Canvas, RIGHT, Y, END, LabelFrame
from collections import defaultdict

class DuplicateImageFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("MODSEN")

        self.directories = []
        self.duplicate_images = defaultdict(list)
        self.image_references = defaultdict(list)  # To store references to ImageTk.PhotoImage objects

        # GUI Elements
        self.select_frame = LabelFrame(self.root, text="Select Directories")
        self.select_frame.pack(padx=20, pady=20, fill='both', expand=True)

        self.select_button = Button(self.select_frame, text="Select Directories", command=self.select_directories)
        self.select_button.pack(pady=10)

        self.directory_count_label = Label(self.select_frame, text="Directories selected: 0")
        self.directory_count_label.pack(pady=5)

        self.refresh_button = Button(self.select_frame, text="Refresh Directories", command=self.refresh_directories)
        self.refresh_button.pack(pady=5)

        self.find_button = Button(self.root, text="Find Duplicates", command=self.find_duplicates)
        self.find_button.pack(pady=10)

        self.view_button = Button(self.root, text="View Duplicates", command=self.view_duplicates)
        self.view_button.pack(pady=10)

        self.results_text = Text(self.root, wrap='word', height=15, width=60)
        self.results_text.pack(padx=10, pady=10)

        self.scrollbar = Scrollbar(self.root, command=self.results_text.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.results_text.config(yscrollcommand=self.scrollbar.set)

    def select_directories(self):
        """ Prompt user to select directories one by one. """
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            self.directories.append(directory)
            self.directory_count_label.config(text=f"Directories selected: {len(self.directories)}")

    def refresh_directories(self):
        """ Clear selected directories and update interface for re-selection. """
        self.directories = []
        self.directory_count_label.config(text="Directories selected: 0")
        self.select_button.config(text="Select Directories")

    def calculate_hash(self, file_path, hash_size=8):
        """ Calculate hash of an image file. """
        try:
            image = Image.open(file_path)
            image_hash = hashlib.md5(image.tobytes()).hexdigest()
            return image_hash[:hash_size], image
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None, None

    def find_duplicates(self):
        """ Find duplicate images in selected directories. """
        if not self.directories:
            self.results_text.delete(1.0, END)
            self.results_text.insert(END, "No directories selected.")
            return
        
        self.duplicate_images = defaultdict(list)
        self.image_references = defaultdict(list)  # Clear existing references

        for directory in self.directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Calculate hash of the image
                    image_hash, image = self.calculate_hash(file_path)
                    if image_hash and image:
                        self.duplicate_images[image_hash].append((file_path, image))

        # Display results in the text widget
        self.display_results()

    def display_results(self):
        """ Display results in the text widget. """
        self.results_text.delete(1.0, END)  # Clear previous results

        if self.duplicate_images:
            self.results_text.insert(END, "Duplicate images found:\n\n")
            for image_list in self.duplicate_images.values():
                if len(image_list) > 1:
                    for file_path, _ in image_list:
                        self.results_text.insert(END, f"{file_path}\n")
                    self.results_text.insert(END, "\n")
        else:
            self.results_text.insert(END, "No duplicate images found.")

    def view_duplicates(self):
        """ Display all found duplicates in a new window with option to delete them. """
        if not self.duplicate_images:
            self.results_text.delete(1.0, END)
            self.results_text.insert(END, "No duplicates found.")
            return

        top = Toplevel(self.root)
        top.title("Found Duplicates")

        canvas = Canvas(top, width=800, height=600)
        canvas.pack(padx=10, pady=10)

        def delete_image(image_path):
            # Remove from self.duplicate_images
            for image_list in self.duplicate_images.values():
                for i, (path, _) in enumerate(image_list):
                    if path == image_path:
                        del image_list[i]
                        break
            # Remove reference to ImageTk.PhotoImage
            for img_list in self.image_references.values():
                for j, (path, img_ref) in enumerate(img_list):
                    if path == image_path:
                        del img_list[j]
                        break
            # Update display
            canvas.delete("all")
            display_images()

        def display_images():
            x, y = 10, 10
            for image_list in self.duplicate_images.values():
                if len(image_list) > 1:
                    for file_path, image in image_list:
                        # Check if PhotoImage already exists
                        img_ref = None
                        for path, ref in self.image_references[file_path]:
                            if path == file_path:
                                img_ref = ref
                                break
                        if img_ref is None:
                            # Resize image to fit canvas
                            img = image.copy()
                            img.thumbnail((400, 400))  # Resize image to fit canvas
                            img_ref = ImageTk.PhotoImage(img)
                            self.image_references[file_path].append((file_path, img_ref))
                        canvas.create_image(x, y, anchor='nw', image=img_ref)
                        label = Label(canvas, text=file_path, fg='black')
                        label.pack()
                        canvas.create_window(x, y + 200, window=label)
                        delete_button = Button(canvas, text="Delete", command=lambda path=file_path: delete_image(path))
                        delete_button.pack()
                        canvas.create_window(x + 100, y + 250, window=delete_button)
                        y += 250
                        top.update_idletasks()  # Update display

        display_images()

if __name__ == "__main__":
    root = Tk()
    app = DuplicateImageFinder(root)
    root.mainloop()
