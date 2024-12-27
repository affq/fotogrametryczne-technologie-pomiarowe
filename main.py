import Metashape
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document
chunk: Metashape.Chunk = doc.chunk

supported_formats = [".jpg",
                      ".jpeg",
                      ".jp2",
                      ".j2k",
                      ".jxl",
                      ".tif",
                      ".tiff",
                      ".png",
                      ".bmp",
                      ".exr",
                      ".tga",
                      ".pgm",
                      ".ppm",
                      ".dng",
                      ".mpo",
                      ".seq",
                      ".ara"
                      ]

def wizard():
    root = tk.Tk()
    root.title("Wizard")
    root.geometry("500x700")

    def find_photos(directory):
        return [f"{directory}/{filename}" for filename in os.listdir(directory) if filename.lower().endswith(tuple(supported_formats))]

    def open_directory():
        directory = filedialog.askdirectory()
        
        if directory:
            photos = find_photos(directory)
            chunk.addPhotos(photos)

    open_directory_button = tk.Button(root, text="Wybierz folder ze zdjęciami", command=open_directory)
    open_directory_button.pack(anchor='w', padx=10, pady=10)

    align_photos_lf = tk.LabelFrame(root, text="Orientacja zdjęć", padx=10, pady=10)
    align_photos_lf.pack(anchor='w', padx=10, pady=10)

    accuracy_options = {
        "Highest": 0,
        "High": 1,
        "Medium": 2,
        "Low": 4,
        "Lowest": 8
    }

    accuracy_label = tk.Label(align_photos_lf, text="Accuracy:")
    accuracy_label.pack(anchor='w')

    accuracy_combo = ttk.Combobox(align_photos_lf, values=list(accuracy_options.keys()), state="readonly")
    accuracy_combo.current(2)
    accuracy_combo.pack(anchor='w', padx=10, pady=10)

    generic_preselection_bool = tk.BooleanVar()
    generic_preselection_checkbox = tk.Checkbutton(align_photos_lf, text="Generic preselection", variable=generic_preselection_bool)
    generic_preselection_checkbox.pack(anchor='w')

    reference_preselection_bool = tk.BooleanVar()
    reference_preselection_checkbox = tk.Checkbutton(align_photos_lf, text="Reference preselection", variable=reference_preselection_bool)
    reference_preselection_checkbox.pack(anchor='w')

    reset_current_alignment_bool = tk.BooleanVar()
    reset_current_alignment_checkbox = tk.Checkbutton(align_photos_lf, text="Reset current alignment", variable=reset_current_alignment_bool)
    reset_current_alignment_checkbox.pack(anchor='w')

    def align_photos():
        accuracy = accuracy_options[accuracy_combo.get()]
        generic_preselection = generic_preselection_bool.get()
        reference_preselection = reference_preselection_bool.get()
        reset_current_alignment = reset_current_alignment_bool.get()

        print(f"{accuracy=}, {generic_preselection=}, {reference_preselection=}")

        chunk.matchPhotos(downscale=accuracy, generic_preselection=generic_preselection, reference_preselection=reference_preselection)
        chunk.alignCameras(reset_alignment=reset_current_alignment)

    align_photos_button = tk.Button(align_photos_lf, text="Align photos", command=align_photos)
    align_photos_button.pack()

    point_cloud_lf = tk.LabelFrame(root, text="Chmura punktów", padx=10, pady=10)
    point_cloud_lf.pack(anchor='w', padx=10, pady=10)

    quality_options = {
        "Ultra high": 1,
        "High": 2,
        "Medium": 4,
        "Low": 8,
        "Lowest": 16
    }

    quality_label = tk.Label(point_cloud_lf, text="Quality:")
    quality_label.pack(anchor='w')

    quality_combo = ttk.Combobox(point_cloud_lf, values=list(quality_options.keys()), state="readonly")
    quality_combo.current(2)
    quality_combo.pack(anchor='w', padx=10, pady=10)

    calculate_point_colors_bool = tk.BooleanVar()
    calculate_point_colors_checkbox = tk.Checkbutton(point_cloud_lf, text="Calculate point colors", variable=calculate_point_colors_bool)
    calculate_point_colors_checkbox.pack(anchor='w')

    calculate_point_confidence_bool = tk.BooleanVar()
    calculate_point_confidence_checkbox = tk.Checkbutton(point_cloud_lf, text="Calculate point confidence", variable=calculate_point_confidence_bool)
    calculate_point_confidence_checkbox.pack(anchor='w')

    depth_filtering_options = {
        "Disabled": Metashape.FilterMode.NoFiltering,
        "Mild": Metashape.FilterMode.MildFiltering,
        "Moderate": Metashape.FilterMode.ModerateFiltering,
        "Aggressive": Metashape.FilterMode.AggressiveFiltering
    }

    depth_filtering_label = tk.Label(point_cloud_lf, text="Depth filtering:")
    depth_filtering_label.pack(anchor='w')

    depth_filtering_combo = ttk.Combobox(point_cloud_lf, values=list(depth_filtering_options.keys()), state="readonly")
    depth_filtering_combo.current(1)
    depth_filtering_combo.pack(padx=10, pady=10, anchor='w')

    def build_point_cloud():
        quality = quality_options[quality_combo.get()]
        depth_filtering = depth_filtering_options[depth_filtering_combo.get()]
        calculate_point_colors = calculate_point_colors_bool.get()
        calculate_point_confidence = calculate_point_confidence_bool.get()
        point_cloud_path = filedialog.asksaveasfilename(defaultextension=".las", filetypes=[("LAS files", "*.las")])

        print(f"{quality=}, {depth_filtering=}, {calculate_point_colors=}, {calculate_point_confidence=}, {point_cloud_path=}")

        chunk.buildDepthMaps(downscale=quality, filter_mode=depth_filtering)
        chunk.buildPointCloud(calculate_point_colors, calculate_point_confidence)
        chunk.exportPointCloud(point_cloud_path)
    
    build_point_cloud_button = tk.Button(point_cloud_lf, text="Build point cloud", command=build_point_cloud, padx=10, pady=10)
    build_point_cloud_button.pack()

    three_d_model_lf = tk.LabelFrame(root, text="Model 3D", padx=10, pady=10)
    three_d_model_lf.pack(anchor='w', padx=10, pady=10)

    root.mainloop()

app.removeMenuItem("Wizard")
app.addMenuItem("Wizard", wizard)