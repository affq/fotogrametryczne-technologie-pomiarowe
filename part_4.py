import Metashape
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import os

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document
chunk: Metashape.Chunk = doc.chunk

def detect_markers():
    chunk = doc.chunk
    if not chunk:
        raise Exception("No chunk selected")
    
    marker_type = Metashape.TargetType.CrossTarget
    chunk.detectMarkers(marker_type, tolerance=0)

def export_camera_orientations(path):
    chunk = doc.chunk
    if not chunk:
        raise Exception("No chunk selected")
    
    if path:
        output_file = path + "/camera_orientations.txt"
    else:
        output_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    
    with open(output_file, 'w') as f:
        f.write("label x y z yaw[deg] pitch[deg] roll[deg]\n")
        for camera in chunk.cameras:
            if camera.transform:
                position = camera.transform.translation()
                rotation = camera.transform.rotation()

                yaw, pitch, roll = Metashape.utils.mat2ypr(rotation)
                f.write(f"{camera.label} {position.x} {position.y} {position.z} {yaw} {pitch} {roll}\n")
    
    messagebox.showinfo("Success", "Camera orientations exported")

def assign_marker_coordinates_from_file():
    chunk = doc.chunk
    if not chunk:
        raise Exception("No chunk selected")
    
    file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            label, y, x, z = line.split()

            for marker in chunk.markers:
                if marker.label == label:
                    marker.reference.location = Metashape.Vector([float(x), float(y), float(z)])
                    break

    messagebox.showinfo("Success", "Coordinates assigned")
