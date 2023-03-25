
import os
import pydicom
import datetime
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
from pydicom.dataset import FileDataset, FileMetaDataset

def read_pixel_data(img_path, xdim, ydim, zdim):
    binary_data = np.fromfile(img_path, dtype = np.short)
    pixel_data = []
    for i in range(0, zdim):
        frame_data = np.array(binary_data[i*xdim*ydim:(i+1)*xdim*ydim]).reshape(xdim, ydim)
        pixel_data.append(frame_data)
    return np.array(pixel_data[::-1])

def read_header(header_path):
    with open(header_path) as header:
        lines = header.readlines()
    header = {}
    for line in lines:
        if "=" in line:
            key, value = (_:=line.split("="))[0].strip(), _[1].strip()[:-1]
            try: 
                if float(value) == int(value):
                    header[key] = int(value)
                else:
                    header[key] = float(value)
            except ValueError: header[key.strip()] = value
            
        elif ":" in line:
            key, value = (_:=line.split(":"))[0].strip(), _[1].strip()
            try: 
                if float(value) == int(value):
                    header[key] = int(value)
                else:
                    header[key] = float(value)
            except ValueError: header[key.strip()] = value
    return header   

def read_image_set(image_set_path):
    with open(image_set_path) as image_set:
        lines = image_set.readlines()
    image_set = {}
    for line in lines:
        if "=" in line:
            key, value = str((_:=line.split("="))[0].strip()), str(_[1].strip()[:-1])
            if key.strip() == "ScanTimeFromScanner":
                date=  value[1:-1].split("/")[2]+value[1:-1].split("/")[1]
                if len((d:=value[1:-1].split("/")[0])) == 1:
                    d = "0"+d
                    
                date += d
                image_set[key] = date
                continue
            try: 
                if float(value) == int(value):
                    image_set[key] = int(value)
                else:
                    image_set[key] = float(value)
            except ValueError: image_set[key.strip()] = value
    return image_set 
    

def read_image_info(image_info_path):
    with open(image_info_path) as image_info:
        lines = image_info.readlines()
    image_info = {}
    for i, line in enumerate(lines):
        if "ImageInfo" in line:
            slice_info = {}
            for line in lines[i+1:]:
                if "ImageInfo" in line:
                    break
                if "=" in line:
                    key, value = str((_:=line.split("="))[0].strip()), str(_[1].strip()[:-1])
                    try: 
                        if float(value) == int(value):
                            slice_info[key] = int(value)
                        else:
                            slice_info[key] = float(value)
                    except ValueError: slice_info[key.strip()] = value
            image_info[slice_info["SliceNumber"]] = slice_info
            
    return image_info


def create_ct_slices(header, image_set, image_info, pixel_data):

    file_meta = FileMetaDataset()
    filename = "temp.dcm"
    ds = FileDataset(filename, {},
                 file_meta=file_meta, preamble=b"\0" * 128)
    ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
    ds.is_little_endian = False
    ds.is_implicit_VR = False

    ds.SOPClassUID         = "1.2.840.10008.5.1.4.1.1.2"    
    ds.Modality            = 'CT'
    ds.ImageType           = ['ORIGINAL', 'PRIMARY', 'AXIAL']
    ds.FrameOfReferenceUID = pydicom.uid.generate_uid()
    
    ds.PixelSpacing = [round(float(header["x_pixdim"])*10,3), round(float(header["y_pixdim"])*10,3)]
    ds.SliceThickness = round(float(header["z_pixdim"])*10,3)
    ds.Rows = header["y_dim"]
    ds.Columns = header["x_dim"]
    ds.PatientPosition = header["patient_position"]
    ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
    ds.PositionReferenceIndicator = "SN"
    
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = header["bitpix"]
    ds.BitsStored = header["bitpix"]
    ds.HighBit = header["bitpix"] - 1
    ds.PixelRepresentation = 1
    
    ds.RescaleIntercept = "0.0"
    ds.RescaleSlope = "1.0"
    ds.RescaleType = "HU"
    
    if header["series_UID"] == "":
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    else:
        ds.SeriesInstanceUID = header["series_UID"]
        
    ds.SeriesDescription = header["Series_Description"]
    ds.SeriesNumber = str(np.random.randint(0, 1000))
    
    ds.PatientName = str(header["db_name"])
    ds.PatientID = str(image_set["PatientID"])
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
    ds.ContentTime = timeStr
    ds.StudyTime = ds.ContentTime
    ds.StudyDate = ds.ContentDate
    ds.StudyID = str(np.random.randint(0, 1000))

    ds.Manufacturer = header["scanner_id"]    
    return ds

def create_DICOM_CT(pinn_dir, save_dir):
    
    for file in os.listdir(pinn_dir):
        if file.endswith(".img"):
            img_path = os.path.join(pinn_dir, file)
        elif file.endswith(".header"):
            header_path = os.path.join(pinn_dir, file)
        elif file.endswith(".ImageSet"):
            image_set_path = os.path.join(pinn_dir, file)
        elif file.endswith(".ImageInfo"):
            image_info_path = os.path.join(pinn_dir, file)
            
    header = read_header(header_path)
    image_set = read_image_set(image_set_path)
    image_info = read_image_info(image_info_path)
    pixel_data = read_pixel_data(img_path, header["x_dim"], header["y_dim"], header["z_dim"])
    ds = create_ct_slices(header, image_set, image_info, pixel_data)
    for slice_id in range(header["z_dim"]):
    
        ds.file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        filename = "CT." + ds.SeriesInstanceUID +f".{slice_id}" + ".dcm"
        ds.file_meta.filename = filename
        ds.SOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID
        ds.InstanceNumber = slice_id+1
        
        ds.ImagePositionPatient = [round(float(header["x_start"])*10,3), round(float(header["y_start"])*10,3), round(float(image_info[slice_id+1]["TablePosition"])*10,3)]
        ds.PixelData = pixel_data[slice_id,:,:].tobytes()
        ds.save_as(os.path.join(save_dir, filename), write_like_original=False)


class Pinn2DCM(tk.Tk):
    
    def __init__(self):
        
        super().__init__()
        
        self.title("PinnacleCT to DICOM Converter")
        self.geometry("406x300")
        self.resizable(False, False)
        self.frame = self.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.mainloop()
        
    class Frame(ttk.Frame):
        def __init__(self, master):
            self.master = master
            super().__init__(master)
            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)
            self.rowconfigure(2, weight=2)
            self.columnconfigure(0, weight=1, minsize=198)
            self.columnconfigure(1, weight=1, minsize=198)
            self.load_pinnacle_directory_button = ttk.Button(self, text="Load Pinnacle Directory", command=self.load_pinnacle_directory)
            self.load_pinnacle_directory_button.grid(row=0, column=0)
            self.load_output_directory_button = ttk.Button(self, text="Load Output Directory", command=self.load_output_directory)
            self.load_output_directory_button.grid(row=0, column=1)
            self.convert_button = ttk.Button(self, text="Convert", command=self.convert, state="disabled")
            self.convert_button.grid(row=1, column=0, columnspan=2)
            self.log = tk.Text(self, height=10, width=50, state="disabled", font=("Arial", 10))
            self.log.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
            
            
            self.pinnacle_directory = tk.StringVar()
            self.output_directory = tk.StringVar()
            self.valid = tk.BooleanVar(value=False)
            
        def convert(self):
            self.log.config(state="normal")
            self.log.insert(tk.END, "Converting...\n")

            create_DICOM_CT(self.pinnacle_directory.get(), self.output_directory.get())
            self.log.insert(tk.END, f"Conversion finished! Created DICOM files for {len(os.listdir(self.output_directory.get()))} CT slices!\n")
            self.log.config(state="disabled")
            self.reset()
            
        def reset(self):
            self.pinnacle_directory.set("")
            self.output_directory.set("")
            self.valid.set(False)
            self.log.config(state="normal")
            self.log.insert(tk.END, "________________________________________________________\n\n")
            self.log.config(state="disabled")
            self.convert_button.config(state="disabled")
            
        def load_pinnacle_directory(self):
            dir = askdirectory()
            if dir != "":
                self.pinnacle_directory.set(dir)
                self.log.config(state="normal")
                self.log.insert(tk.END, f"Pinnacle Directory: {self.pinnacle_directory.get()}\n")
                self.log.config(state="disabled")
                self.check_validity()
            
        def load_output_directory(self):
            dir = askdirectory()
            if dir != "":
                self.output_directory.set(dir)
                self.log.config(state="normal")
                self.log.insert(tk.END, f"Output Directory: {self.output_directory.get()}\n")
                self.log.config(state="disabled")
                self.check_validity()
            
        def check_validity(self):
            if self.valid.get()== False:
                valid = 0
                try:
                    for file in os.listdir(self.pinnacle_directory.get()):
                        if file.endswith(".header"):
                            valid += 1
                        elif file.endswith(".img"):
                            valid += 1
                        elif file.endswith(".ImageSet"):
                            valid += 1
                        elif file.endswith(".ImageInfo"):
                            valid += 1
                except Exception:
                    pass
                
                if self.pinnacle_directory.get() != "" and self.output_directory.get() != "":
                    if valid == 4: 
                        self.valid.set(True)
                        self.log.config(state="normal")
                        self.log.insert(tk.END, "Valid Pinnacle Directory!\n")
                        self.log.insert(tk.END, "Press Convert to start conversion!\n")
                        self.log.config(state="disabled")
                        self.convert_button.config(state="normal")
                    else:
                        self.log.config(state="normal")
                        self.log.insert(tk.END, "Invalid Pinnacle Directory!\n")
                        self.log.config(state="disabled")