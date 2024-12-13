import struct
import tkinter as tk
from tkinter import Canvas
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk ,ImageDraw, ImageFont  # We're using PIL for handling image display
import math
class CustomGUI:
    def __init__(self, master, image_processor):
        self.master = master
        self.image_processor = image_processor
        self.master.title("Custom Image Processing GUI")

        # Main Frame
        self.frame = tk.Frame(self.master, bg="lightgray", padx=10, pady=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        title_label = tk.Label(self.frame, text="Home-Made MATLAB Image Processor",
                               font=("Arial", 16), bg="lightgray", fg="black")
        title_label.pack(pady=10)

        # Function Buttons
        tk.Button(self.frame, text="Lighten Image", command=self.lighten).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.frame, text="Darken Image", command=self.darken).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.frame, text="Negative Image", command=self.negative).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.frame, text="Power-Law Transformation", command=self.powerlaw).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.frame, text="Histogram Stretch", command=self.histogram_stretch).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.frame, text="Histogram Equalization", command=self.histogram_equalization).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.frame, text="Blur Image", command=self.blur).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(self.frame, text="Save and Display Image", command=self.save_and_display).pack(fill=tk.X, padx=5, pady=5)

        # Exit Button
        tk.Button(self.frame, text="Exit", command=self.master.quit, bg="red", fg="white").pack(fill=tk.X, padx=5, pady=20)

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

        #***Currently only displaying the result, dehash the code below for saving***#
        self.image_processor.display(image_type='Processed_IMG')


        # # Create a new window asking the user for the filename
        # input_window = tk.Toplevel(self.master)
        # input_window.title("Enter Filename")
        # input_window.geometry("300x150")
        # input_window.grab_set()  # Make this window modal (blocks interaction with the main window)

        # # Create label and entry field for the filename input
        # tk.Label(input_window, text="Enter the filename (without extension):").pack(pady=10)
        # filename_entry = tk.Entry(input_window)
        # filename_entry.pack(pady=10)

        # def save_action():
        #     # Get the filename entered by the user
        #     filename = filename_entry.get()

        #     # Check if the filename is not empty
        #     if filename:
        #         # Save the image with the entered filename
        #         self.image_processor.display(image_type=filename)  # This will save and display the image
        #         messagebox.showinfo("Action Complete", f"Image saved as {filename}_output_image.png")
        #         input_window.destroy()  # Close the window after saving
        #     else:
        #         # Show an error message if the filename is empty
        #         messagebox.showerror("Error", "Please enter a valid filename.")

        # # "Save" button to apply the action
        # tk.Button(input_window, text="Save", command=save_action).pack(pady=10)

        # # "Cancel" button to close the input window without saving
        # tk.Button(input_window, text="Cancel", command=input_window.destroy).pack(pady=10)


    def open_input_window(self, title, labels, process_function):
        # Create a new top-level window
        input_window = tk.Toplevel(self.master)
        input_window.title(title)
        input_window.geometry("300x300")
        input_window.grab_set()

        # Store input fields
        input_fields = []

        # Create labels and entry fields for each required input
        for label in labels:
            tk.Label(input_window, text=label).pack(pady=5)
            entry = tk.Entry(input_window)
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
        tk.Button(input_window, text="Apply", command=apply_action).pack(pady=10)

        # Cancel Button
        tk.Button(input_window, text="Cancel", command=input_window.destroy).pack(pady=10)



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





    def display_image(self):
        root = tk.Tk()
        root.title("Image Display")

        # Create a canvas to display the image
        canvas = Canvas(root, width=self.width, height=self.height)
        canvas.pack()

        # Convert the image data into a format that can be displayed
        img_data = []
        for row in self.image_data:
            for pixel in row:
                img_data.append((pixel, pixel, pixel))  
                
        # Convert the list of pixel data into a PIL Image
        img = Image.new('RGB', (self.width, self.height))
        img.putdata(img_data)

        
        tk_img = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        root.mainloop()

    def display(self, image_type="Original"):
        # Convert the image data into a flat list (from 2D to 1D)
        img_data = [pixel for row in self.image_data for pixel in row]

        # Create a new grayscale image using PIL
        img = Image.new("L", (self.width, self.height))  # "L" mode is for grayscale
        img.putdata(img_data)  # Add pixel data to the image

        # Save the image with a custom name (ensure the file extension is valid)
        filename = f"{image_type}_output_image.png"  # Custom filename with .png extension
        img.save(filename)  # Save the image with the given name

        # Open the saved image (This will display it with the custom filename in the viewer)
        img.show()


if __name__ == "__main__":
    
    file_path = filedialog.askopenfilename(title="Select a TIFF Image", filetypes=[("TIFF files", "*.tif")])
    if not file_path:
        messagebox.showerror("Error !","No file selected. Exiting.")



    else:
        #image = Home_Made_Matlab(r'C:\Users\Yussif\OneDrive\Desktop\level_3\DIP\project\samples\Ein1.tif')
        image = Home_Made_Matlab(file_path)
        image.origin_data = [row[:] for row in image.image_data]

        root = tk.Tk()
        gui = CustomGUI(root, image)
        root.mainloop()


