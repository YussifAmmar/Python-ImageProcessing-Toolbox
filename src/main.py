import struct
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk ,ImageDraw, ImageFont  # We're using PIL for handling image display
import math
class CustomGUI:
    def __init__(self, master, image_processor):
        self.master = master
        self.master.geometry("400x500")
        self.image_processor = image_processor
        self.master.title("Custom Image Processing GUI")
        
        # Set up customtkinter theme
        ctk.set_appearance_mode("System")  # You can set to "Dark" or "Light"
        ctk.set_default_color_theme("blue")  # You can choose other themes
        
        # Main Frame
        self.frame = ctk.CTkFrame(self.master,width=400,height=500)
        self.frame.pack(fill=ctk.BOTH, expand=True)
        
        # Title Label
        title_label = ctk.CTkLabel(self.frame, text="Home-Made MATLAB Image Processor", font=("Arial", 16))
        title_label.pack(pady=10)
        
        # Function Buttons
        self.create_button("Lighten Image", self.lighten)
        self.create_button("Darken Image", self.darken)
        self.create_button("Negative Image", self.negative)
        self.create_button("Power-Law Transformation", self.powerlaw)
        self.create_button("Histogram Stretch", self.histogram_stretch)
        self.create_button("Histogram Equalization", self.histogram_equalization)
        self.create_button("Blur Image", self.blur)
        self.create_button("Show Original",self.display_original)
        self.create_button("Save and Display Image", self.save_and_display)

        # Exit Button
        exit_button = ctk.CTkButton(self.frame, text="Exit", command=self.master.quit, fg_color="red", hover_color="darkred")
        exit_button.pack(fill=ctk.X, padx=5, pady=20)

    def display_original(self):
        self.image_processor.display_original()

    def create_button(self, text, command):
        button = ctk.CTkButton(self.frame, text=text, command=command)
        button.pack(fill=ctk.X, padx=5, pady=5)
    
    def lighten(self):
        self.open_input_window("Lighten Image", ["Value", "Start Range", "End Range"],
                               lambda vals: self.image_processor.lighten(int(vals[0]), int(vals[1]), int(vals[2])))

    def darken(self):
        self.open_input_window("Darken Image", ["Value", "Start Range", "End Range"],
                               lambda vals: self.image_processor.darken(int(vals[0]), int(vals[1]), int(vals[2])))

    def powerlaw(self):
        self.open_input_window("Power-Law Transformation", ["Gamma"],
                               lambda vals: self.image_processor.powerlaw(float(vals[0])))

    def blur(self):
        self.open_input_window("Blur Image", ["Blur Level (Odd Number)"],
                               lambda vals: self.image_processor.blur(int(vals[0])))

    def histogram_stretch(self):
        self.image_processor.histogram_stretch()
        messagebox.showinfo("Action Complete", "Histogram stretching applied.")

    def histogram_equalization(self):
        self.image_processor.histogram_equalization()
        messagebox.showinfo("Action Complete", "Histogram equalization applied.")

    def negative(self):
        self.image_processor.negative()
        messagebox.showinfo("Action Complete", "Negative transformation applied.")

    def save_and_display(self):
        self.open_input_window("Save and Display", ["Name of the output img"],
                               lambda vals: self.image_processor.display(str(vals[0])))


    def open_input_window(self, title, labels, process_function):
        # Create a new top-level window using customtkinter
        input_window = ctk.CTkToplevel(self.master)
        input_window.title(title)
        input_window.geometry("200x400")
        input_window.grab_set()

        # Store input fields
        input_fields = []

        # Create labels and entry fields for each required input
        for label in labels:
            ctk.CTkLabel(input_window, text=label).pack(pady=5)
            entry = ctk.CTkEntry(input_window)
            entry.pack(pady=5)
            input_fields.append(entry)

        def apply_action():
            try:
                # Collect values from input fields
                values = [field.get() for field in input_fields]
                # Apply the processing function with these values
                process_function(values)
                messagebox.showinfo("Success", f"{title} applied successfully!")
                input_window.destroy()  # Close the input window
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply {title}: {e}")

        # Apply Button
        apply_button = ctk.CTkButton(input_window, text="Apply", command=apply_action)
        apply_button.pack(pady=10)

        # Cancel Button
        cancel_button = ctk.CTkButton(input_window, text="Cancel", command=input_window.destroy)
        cancel_button.pack(pady=10)



class Home_Made_Matlab:
    def __init__(self, file_path):
        self.file_path = file_path
        self.width = None
        self.height = None
        self.image_data = None
        self.origin_data = None
        self.endian=None
        self.pixel_offset = None
        self.read_tiff(file_path)

    def read_tiff(self, file_path):
        with open(file_path, 'rb') as f:
            # Read the magic number to check file type
            magic_number = f.read(4)
            #messagebox.showinfo("Header",f"Header of TIFF file: {magic_number}")

            if magic_number == b'II*\x00':  # Little-endian TIFF (II)
                endian = '<'
            elif magic_number == b'MM\x00*':  # Big-endian TIFF (MM)
                endian = '>'
            else:
                raise ValueError(f"Invalid TIFF magic number: {magic_number}")
                messagebox.showerror("Error",f"Invalid TIFF magic number: {magic_number}")

            # Read the TIFF header, offset to the first IFD (Image File Directory)
            f.seek(4)  # Skip the magic number
            offset = struct.unpack(endian + 'I', f.read(4))[0]
            self.pixel_offset=offset
            #messagebox.showinfo("IFD Offset",f"IFD offset: {offset}")

            f.seek(offset)
            
            # Read IFD entry count (2 bytes)
            entry_count = struct.unpack(endian + 'H', f.read(2))[0]
            messagebox.showinfo("IMG Info",f"Header of TIFF file: {magic_number}\n\nIFD offset: {offset}\n\nIFD entry count: {entry_count}\n\n")

            # Read the IFD entries (each entry is 12 bytes)
            for _ in range(entry_count):
                tag = struct.unpack(endian + 'H', f.read(2))[0]
                field_type = struct.unpack(endian + 'H', f.read(2))[0]
                count = struct.unpack(endian + 'I', f.read(4))[0]
                value = struct.unpack(endian + 'I', f.read(4))[0]

                # Look for ImageWidth (tag 256) and ImageLength (tag 257)
                if tag == 256:
                    self.width = value
                    messagebox.showinfo("WIDTH",f"Image Width: {self.width}")
                elif tag == 257:
                    self.height = value
                    messagebox.showinfo("HEIGHT",f"Image Height: {self.height}")

            # Assuming that the data is stored in a contiguous array format (8-bit grayscale)
            if self.width and self.height:
                self.read_image_data(f, endian)

    def read_image_data(self, f, endian):
        f.seek(0)

        self.origin_data=[]
        self.image_data = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                pixel_value = struct.unpack(endian + 'B', f.read(1))[0]  # Read each byte (grayscale pixel)
                row.append(pixel_value)
            self.image_data.append(row)
            self.origin_data.append(row)

    def lighten(self, val,start,end):
        # Modify the existing image data to lighten each pixel
        for y in range(self.height):
            for x in range(self.width):
                if start<=self.image_data[y][x]<=end:
                    new_pixel_value = self.image_data[y][x] + int(val)
                    self.image_data[y][x] = min(255, max(0, new_pixel_value))  # Ensure pixel value is between 0 and 255

    def darken(self, val,start,end):
        # Modify the existing image data to lighten each pixel
        min_val = min(min(row) for row in self.image_data)
        max_val = max(max(row) for row in self.image_data)
        
        # Print min and max values for debugging
        messagebox.showinfo("MIN_MAX Values",f"Min pixel value after stretch: {min_val}\nMax pixel value after stretch: {max_val}")


        for y in range(self.height):
            for x in range(self.width):
                if start<=self.image_data[y][x]<=end:
                    new_pixel_value = self.image_data[y][x] - int(val)
                    self.image_data[y][x] = min(255, max(0, new_pixel_value)) 

    def negative(self):
        # Modify the existing image data to lighten each pixel
        for y in range(self.height):
            for x in range(self.width):
                new_pixel_value = 255 - self.image_data[y][x]
                self.image_data[y][x] = min(255, max(0, new_pixel_value))


    def powerlaw(self, gamma):
    # Apply power-law (gamma) transformation to each pixel
        for y in range(self.height):
            for x in range(self.width):
                # Normalize the pixel value (0 to 1 range)
                normalized_pixel = self.image_data[y][x] / 255.0
                
                # Apply the power-law transformation
                transformed_pixel = normalized_pixel ** gamma
                
                # Scale back to 0-255 and round
                new_pixel_value = round(transformed_pixel * 255)
                self.image_data[y][x] = min(255, max(0, new_pixel_value))

    def histogram_stretch(self):
        # Find the minimum and maximum pixel values in the image
        min_val = min(min(row) for row in self.image_data)
        max_val = max(max(row) for row in self.image_data)
        
        # Print min and max values for debugging
        messagebox.showinfo("MIN_MAX Values",f"Min pixel value after stretch: {min_val}\nMax pixel value after stretch: {max_val}")


        # If the image has no contrast (min_val == max_val), do nothing
        if min_val == max_val:
            messagebox.showwarning("Error","No contrast to stretch.")
            return  # No stretching needed if all pixel values are the same

        # Apply the stretching formula to each pixel
        for y in range(self.height):
            for x in range(self.width):
                # Stretch the pixel values to the range [0, 255]
                new_value = int(255 * ((self.image_data[y][x] - min_val) / (max_val - min_val)))
                self.image_data[y][x] = new_value

        # Print min and max values after stretching
        new_min = min(min(row) for row in self.image_data)
        new_max = max(max(row) for row in self.image_data)
        messagebox.showinfo("New Values",f"Min pixel value after stretch: {new_min}\nMax pixel value after stretch: {new_max}")


    def histogram_equalization(self):
        # Flatten the image data into a 1D list for easier histogram computation
        flat_image_data = [pixel for row in self.image_data for pixel in row]

        # Calculate histogram (frequency of each pixel value)
        hist = [0] * 256
        for pixel in flat_image_data:
            hist[pixel] += 1

        # Calculate cumulative distribution function (CDF)
        cdf = [sum(hist[:i+1]) for i in range(256)]
        
        # Normalize the CDF (map values to the range [0, 255])
        cdf_min = min(cdf)
        total_pixels = self.width * self.height
        normalized_cdf = [(cdf[i] - cdf_min) / (total_pixels - cdf_min) * 255 for i in range(256)]

        # Apply the new pixel values based on the normalized CDF
        for y in range(self.height):
            for x in range(self.width):
                self.image_data[y][x] = int(normalized_cdf[self.image_data[y][x]])
 

    def blur(self, level=3):
        if level % 2 == 0:
            raise ValueError("blur: Mask size should be odd.")

        height = self.height
        width = self.width

        gap = (level - 1) // 2
        divisor = 1.0 / (level * level)

        blurred_image = [[0 for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                sum = 0.0
                for mask_y in range(y - gap, y + gap + 1):
                    for mask_x in range(x - gap, x + gap + 1):
                        if mask_x < 0 or mask_x >= width or mask_y < 0 or mask_y >= height:
                            sum += 0  
                        else:
                            sum += self.image_data[mask_y][mask_x]
                
                sum *= divisor
                blurred_image[y][x] = round(sum)

        self.image_data = blurred_image





    # def display_image(self):
    #     root = tk.Tk()
    #     root.title("Image Display")

    #     # Create a canvas to display the image
    #     canvas = Canvas(root, width=self.width, height=self.height)
    #     canvas.pack()

    #     # Convert the image data into a format that can be displayed
    #     img_data = []
    #     for row in self.image_data:
    #         for pixel in row:
    #             img_data.append((pixel, pixel, pixel))  
                
    #     # Convert the list of pixel data into a PIL Image
    #     img = Image.new('RGB', (self.width, self.height))
    #     img.putdata(img_data)

        
    #     tk_img = ImageTk.PhotoImage(img)
    #     canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
    #     root.mainloop()

    def display(self, image_type="Original"):
        # Convert the image data into a flat list (from 2D to 1D)
        img_data = [pixel for row in self.image_data for pixel in row]

        # Create a new grayscale image using PIL
        img = Image.new("L", (self.width, self.height))  # "L" mode is for grayscale
        img.putdata(img_data)  # Add pixel data to the image

        # Save the image with a custom name (ensure the file extension is valid)
        filename = f"{image_type}.png"  # Custom filename with .png extension
        img.save(filename)  # Save the image with the given name

        # Open the saved image (This will display it with the custom filename in the viewer)
        img.show()

    def display_original(self):
        img = Image.open(self.file_path)
        img.show()

if __name__ == "__main__":
    # File dialog to select the TIFF image
    file_path = filedialog.askopenfilename(title="Select a TIFF Image", filetypes=[("TIFF files", "*.tif")])
    if not file_path:
        messagebox.showerror("Error!", "No file selected. Exiting.")

        
    else:
        # Create an instance of Home_Made_Matlab with the selected file path
        image = Home_Made_Matlab(file_path)
        image.origin_data = [row[:] for row in image.image_data]

        # Initialize the main window using customtkinter
        root = ctk.CTk()  # Use CTk instead of Tk to integrate customtkinter
        root.title("Custom Image Processing GUI")
        
        # Set the appearance mode and theme
        ctk.set_appearance_mode("System")  # You can change to "Light" or "Dark"
        ctk.set_default_color_theme("blue")  # You can set a different theme

        # Create the GUI with the custom window and pass the image
        gui = CustomGUI(root, image)
        
        # Start the main loop
        root.mainloop()

