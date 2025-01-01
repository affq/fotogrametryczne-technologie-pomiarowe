import Metashape
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog
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

def assign_coordinates():
    chunk = doc.chunk
    if not chunk:
        raise Exception("No chunk selected")
    
    crs = chunk.crs
    for marker in chunk.markers:
        marker.reference.location = crs.project(chunk.transform.matrix.mulp(marker.position))

    chunk.updateTransform()
    chunk.op


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


def assign_marker_coordinates_window():
    chunk = doc.chunk
    if not chunk:
        raise Exception("No chunk with detected markers")

    markers = chunk.markers

    if not markers:
        raise Exception("No markers found in the chunk")

    window = tk.Tk()
    window.title("Assign Marker Coordinates")
    window.geometry("250x400")

    canvas = tk.Canvas(window, width=200, height=400)
    scroll_y = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    def on_mouse_wheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    entries = {} 

    for marker in markers:
        labelframe = tk.LabelFrame(scroll_frame, text=f"{marker.label}")
        labelframe.pack(padx=10, pady=10)

        x_frame = tk.Frame(labelframe)
        x_frame.pack()

        x_label = tk.Label(x_frame, text="X:")
        x_label.pack(side="left", padx=5, pady=5)

        x_entry = tk.Entry(x_frame)
        x_entry.pack(side="left", padx=5, pady=5)

        y_frame = tk.Frame(labelframe)
        y_frame.pack()

        y_label = tk.Label(y_frame, text="Y:")
        y_label.pack(side="left", padx=5, pady=5)

        y_entry = tk.Entry(y_frame)
        y_entry.pack(side="left", padx=5, pady=5)

        z_frame = tk.Frame(labelframe)
        z_frame.pack()

        z_label = tk.Label(z_frame, text="Z:")
        z_label.pack(side="left", padx=5, pady=5)

        z_entry = tk.Entry(z_frame)
        z_entry.pack(side="left", padx=5, pady=5)
    
        entries[marker.label] = (x_entry, y_entry, z_entry)
