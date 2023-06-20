import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import win32clipboard
from io import BytesIO
from Scanner import Scanner


class ScannerGUI(tk.Frame):
    a4_size = (210 * 1, 297 * 1)

    def __init__(self, master=None):
        super().__init__(master)

        self.master = master

        self.down_icon = ImageTk.PhotoImage(
            Image.open(os.path.join("icons", "down_icon.png")).resize(
                (32, 32), Image.Resampling.LANCZOS
            )
        )
        self.right_icon = ImageTk.PhotoImage(
            Image.open(os.path.join("icons", "right_icon.png")).resize(
                (32, 32), Image.Resampling.LANCZOS
            )
        )

        self.create_widgets()

        self.pack()

    def create_widgets(self):
        self.generate_main_frame()
        self.generate_additional_frame()

        self.set_styles()

    # ----------------------------------------------------------------
    def set_styles(self):
        self.master.resizable(0, 0)

        for child in self.winfo_children():
            self.apply_paddings(child)
            self.set_colors(child)
            self.set_fonts(child)

    def apply_paddings(self, widget, padx=5, pady=5):
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                self.apply_paddings(child, padx, pady)
        else:
            widget.pack_configure(padx=padx, pady=pady)

    def set_colors(self, widget, bg_color="#303030", fg_color="#00A36C"):
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                widget.configure(bg=bg_color)
                self.set_colors(child, bg_color, fg_color)
        else:
            try:
                widget.configure(bg=bg_color)
                widget.configure(fg=fg_color)
            except:
                pass

    def set_fonts(self, widget, family="Comic Sans MS"):
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                self.set_fonts(child)

        elif isinstance(widget, tk.Label):
            widget.configure(font=(family, 14))

        elif isinstance(widget, tk.Button):
            widget.configure(font=(family, 12))

        elif isinstance(widget, tk.Scale):
            widget.configure(font=(family, 12))

    # ----------------------------------------------------------------
    def generate_main_frame(self):
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side="top")

        input_frame = self.generate_input_frame(self.main_frame)
        template_frame = self.generate_template_frame(self.main_frame)
        output_frame = self.generate_output_frame(self.main_frame)

        input_frame.pack(side="left")
        template_frame.pack(side="left")
        output_frame.pack(side="left")

    def generate_input_frame(self, parent_frame):
        input_frame = tk.Frame(parent_frame)

        input_frame_label = tk.Label(input_frame, text="Input image")
        input_frame_label.pack()

        self.input_image = ScannerGUI.create_dummy_image(ScannerGUI.a4_size)
        input_photo = ImageTk.PhotoImage(self.input_image)

        self.input_image_view = tk.Label(input_frame, image=input_photo)
        self.input_image_view.image = input_photo
        self.input_image_view.pack()
        self.input_image_view.bind(
            "<Double-Button-1>",
            lambda event: self.select_input_image(),
        )

        self.add_context_menu(self.input_image_view)

        input_button = tk.Button(
            input_frame,
            text="Select image",
            command=lambda: self.select_input_image(),
        )
        input_button.pack(fill="x")

        return input_frame

    def generate_template_frame(self, parent_frame):
        template_frame = tk.Frame(parent_frame)

        template_frame_label = tk.Label(template_frame, text="Template")
        template_frame_label.pack()

        self.template_image = ScannerGUI.create_dummy_image(ScannerGUI.a4_size)
        template_photo = ImageTk.PhotoImage(self.template_image)

        self.template_image_view = tk.Label(template_frame, image=template_photo)
        self.template_image_view.image = template_photo
        self.template_image_view.pack()
        self.template_image_view.bind(
            "<Double-Button-1>",
            lambda event: self.select_template_image(),
        )

        self.add_context_menu(self.template_image_view)

        template_button = tk.Button(
            template_frame,
            text="Set template",
            command=lambda: self.select_template_image(),
        )
        template_button.pack(fill="x")

        return template_frame

    def generate_output_frame(self, parent_frame):
        output_frame = tk.Frame(parent_frame)

        output_frame_label = tk.Label(output_frame, text="Result")
        output_frame_label.pack()

        self.output_image = ScannerGUI.create_dummy_image(ScannerGUI.a4_size)
        output_photo = ImageTk.PhotoImage(self.output_image)

        self.output_image_view = tk.Label(output_frame, image=output_photo)
        self.output_image_view.image = output_photo
        self.output_image_view.pack()

        self.add_context_menu(self.output_image_view)

        output_button = tk.Button(
            output_frame,
            text="Scan image",
            command=self.scan_image,
        )
        output_button.pack(fill="x")

        return output_frame

    # ----------------------------------------------------------------
    def generate_additional_frame(self):
        self.additional_frame = tk.Frame(self)
        self.additional_frame.pack(side="top", fill="x")

        self.additional_frame_label_frame = tk.Frame(self.additional_frame)
        self.additional_frame_label_frame.pack(side="top", fill="x")
        self.additional_frame_label_frame.bind(
            "<Button-1>", self.toggle_additional_frame
        )

        self.additional_frame_label = tk.Label(
            self.additional_frame_label_frame,
            text="Advanced",
            image=self.right_icon,
            compound="left",
        )
        self.additional_frame_label.configure(image=self.right_icon)
        self.additional_frame_label.pack(side="left")
        self.additional_frame_label.bind("<Button-1>", self.toggle_additional_frame)

        self.additional_frame_content_frame = tk.Frame(self.additional_frame)
        self.additional_frame_content_frame.pack(side="top", fill="x")
        self.additional_frame_content_frame.pack_forget()

        self.orb_features_number = tk.IntVar(value=500)
        self.orb_features_number_scale = tk.Scale(
            self.additional_frame_content_frame,
            from_=0,
            to=1500,
            orient="horizontal",
            label="ORB features",
            variable=self.orb_features_number,
            resolution=1,
            command=None,
        )
        self.orb_features_number_scale.pack(side="top", fill="x")

        self.matches_percentage = tk.IntVar(value=5)
        self.matches_percentage_scale = tk.Scale(
            self.additional_frame_content_frame,
            from_=0,
            to=100,
            orient="horizontal",
            label="Percentage",
            variable=self.matches_percentage,
            resolution=1,
            command=None,
        )
        self.matches_percentage_scale.pack(side="top", fill="x")

        dummy_advanced_image = ScannerGUI.create_dummy_image(
            (ScannerGUI.a4_size[0] * 2, ScannerGUI.a4_size[1])
        )
        self.advanced_output_image = dummy_advanced_image
        dummy_advanced_photo = ImageTk.PhotoImage(dummy_advanced_image)
        self.advanced_output_image_view = tk.Label(
            self.additional_frame_content_frame,
            image=dummy_advanced_photo,
        )
        self.advanced_output_image_view.image = dummy_advanced_photo
        self.advanced_output_image_view.pack(side="top", fill="x")

        self.add_context_menu(self.advanced_output_image_view)

    def toggle_additional_frame(self, event):
        if self.additional_frame_content_frame.winfo_ismapped():
            self.additional_frame_content_frame.pack_forget()
            self.additional_frame_label.configure(image=self.right_icon)
        else:
            self.additional_frame_content_frame.pack(side="top", fill="x")
            self.additional_frame_label.configure(image=self.down_icon)

        self.master.update()

    # ----------------------------------------------------------------
    def add_context_menu(self, image_view):
        context_menu = tk.Menu(image_view, tearoff=0)

        context_menu.add_command(
            label="Reset Image", command=lambda: self.clear_image(image_view)
        )
        context_menu.add_command(
            label="Copy Image",
            command=lambda: self.copy_to_clipboard(image_view),
        )
        context_menu.add_command(
            label="Save Image", command=lambda: self.save_image(image_view)
        )

        image_view.bind(
            "<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root)
        )

    def clear_image(self, image_view):
        image = None

        if image_view == self.input_image_view:
            image = ScannerGUI.create_dummy_image(ScannerGUI.a4_size)
            self.input_image = image
        elif image_view == self.template_image_view:
            image = ScannerGUI.create_dummy_image(ScannerGUI.a4_size)
            self.template_image = image
        elif image_view == self.output_image_view:
            image = ScannerGUI.create_dummy_image(ScannerGUI.a4_size)
            self.output_image = image
        elif image_view == self.advanced_output_image_view:
            image = ScannerGUI.create_dummy_image(
                (
                    ScannerGUI.a4_size[0] * 2,
                    ScannerGUI.a4_size[1],
                )
            )
            self.advanced_output_image = image

        if image:
            photo = ImageTk.PhotoImage(image)
            image_view.configure(image=photo)
            image_view.image = photo

    def copy_to_clipboard(self, image_view):
        image = None

        if image_view == self.input_image_view:
            image = self.input_image
        elif image_view == self.template_image_view:
            image = self.template_image
        elif image_view == self.output_image_view:
            image = self.output_image
        elif image_view == self.advanced_output_image_view:
            image = self.advanced_output_image

        if image:
            output = BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

    def save_image(self, image_view):
        image = None

        if image_view == self.input_image_view:
            image = self.input_image
        elif image_view == self.template_image_view:
            image = self.template_image
        elif image_view == self.output_image_view:
            image = self.output_image
        elif image_view == self.advanced_output_image_view:
            image = self.advanced_output_image

        if image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("JPEG", "*.jpeg")],
            )
            if file_path:
                image.save(file_path)

    # ----------------------------------------------------------------
    # size: (width, height)
    # color: (r, g, b), from 0 to 255
    @staticmethod
    def create_dummy_image(size, color=(178, 255, 223)):
        image = Image.new("RGB", size, color)
        return image

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )

        if file_path:
            image = Image.open(file_path)
            return image

        return None

    def select_input_image(self):
        image = self.open_image()

        if image:
            self.input_image = image

            resized_image = image.resize(ScannerGUI.a4_size)
            photo = ImageTk.PhotoImage(resized_image)
            self.input_image_view.configure(image=photo)
            self.input_image_view.image = photo

    def select_template_image(self):
        image = self.open_image()

        if image:
            self.template_image = image

            resized_image = image.resize(ScannerGUI.a4_size)
            photo = ImageTk.PhotoImage(resized_image)
            self.template_image_view.configure(image=photo)
            self.template_image_view.image = photo

    def scan_image(self):
        try:
            scanned_image, matches_image, error = Scanner.scan(
                self.input_image,
                self.template_image,
                orb_features_number=self.orb_features_number.get(),
                matches_percentage=self.matches_percentage.get(),
            )

            if not error:
                self.output_image = scanned_image

                resized_image = self.output_image.resize(ScannerGUI.a4_size)
                photo = ImageTk.PhotoImage(resized_image)

                self.output_image_view.configure(image=photo)
                self.output_image_view.image = photo

            else:
                messagebox.showwarning("Error while scanning", error)

            if matches_image:
                self.advanced_output_image = matches_image

                original_width, original_height = self.advanced_output_image.size

                target_height = ScannerGUI.a4_size[1]
                target_width = target_height * original_width // original_height

                resized_image = self.advanced_output_image.resize(
                    (target_width, target_height)
                )
                photo = ImageTk.PhotoImage(resized_image)

                self.advanced_output_image_view.configure(image=photo)
                self.advanced_output_image_view.image = photo

        except Exception as error:
            messagebox.showwarning("An error occurred", error)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Document scanner")

    app = ScannerGUI(master=root)

    root.mainloop()
