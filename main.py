import Metashape
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import os

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document
chunk: Metashape.Chunk = doc.chunk

supported_formats = [".jpg", ".jpeg", ".jp2", ".j2k", ".jxl", ".tif", ".tiff", ".png", ".bmp", ".exr", ".tga", ".pgm", ".ppm", ".dng", ".mpo", ".seq", ".ara"]

def wizard():
    root = tk.Tk()
    root.title("Wizard")
    root.geometry("750x450")

    def find_photos(directory):
        return [f"{directory}/{filename}" for filename in os.listdir(directory) if filename.lower().endswith(tuple(supported_formats))]

    def open_directory():
        directory = filedialog.askdirectory(title="Select directory with photos")
        
        if directory:
            photos = find_photos(directory)
            
            if not photos:
                raise Exception("No photos found in the selected directory")
            
            chunk = doc.chunk
            if not chunk:
                chunk = doc.addChunk()
            
            chunk.addPhotos(photos)
        else:
            raise Exception("No directory selected")

    open_directory_button = tk.Button(root, text="Select directory with photos", command=open_directory)
    open_directory_button.pack(padx=10, pady=10)

    options = tk.Frame(root)
    options.pack(padx=10, pady=10)

    align_photos_lf = tk.LabelFrame(options, text="Align photos", padx=10, pady=10)
    align_photos_lf.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)

    accuracy_options = {
        "Highest": 0,
        "High": 1,
        "Medium": 2,
        "Low": 4,
        "Lowest": 8
    }

    accuracy_frame = tk.Frame(align_photos_lf)
    accuracy_frame.pack(anchor='w')

    accuracy_label = tk.Label(accuracy_frame, text="Accuracy:")
    accuracy_label.pack(side=tk.LEFT, anchor='w')

    accuracy_combo = ttk.Combobox(accuracy_frame, values=list(accuracy_options.keys()), state="readonly", width=8)
    accuracy_combo.current(2)
    accuracy_combo.pack(side=tk.LEFT, anchor='w', padx=10, pady=10)

    generic_preselection_bool = tk.BooleanVar(value=True)
    generic_preselection_checkbox = tk.Checkbutton(align_photos_lf, text="Generic preselection", variable=generic_preselection_bool)
    generic_preselection_checkbox.pack(anchor='w')

    reference_preselection_bool = tk.BooleanVar(value=True)
    reference_preselection_checkbox = tk.Checkbutton(align_photos_lf, text="Reference preselection", variable=reference_preselection_bool)
    reference_preselection_checkbox.pack(anchor='w')

    reset_current_alignment_bool = tk.BooleanVar()
    reset_current_alignment_checkbox = tk.Checkbutton(align_photos_lf, text="Reset current alignment", variable=reset_current_alignment_bool)
    reset_current_alignment_checkbox.pack(anchor='w')

    def align_photos():
        chunk = doc.chunk
        if not chunk:
            raise Exception("No chunk with photos selected")

        accuracy = accuracy_options[accuracy_combo.get()]
        generic_preselection = generic_preselection_bool.get()
        reference_preselection = reference_preselection_bool.get()
        reset_current_alignment = reset_current_alignment_bool.get()

        print(f"{accuracy=}, {generic_preselection=}, {reference_preselection=}")

        chunk.matchPhotos(downscale=accuracy, generic_preselection=generic_preselection, reference_preselection=reference_preselection)
        chunk.alignCameras(reset_alignment=reset_current_alignment)

    align_photos_button = tk.Button(align_photos_lf, text="Align photos", command=align_photos)
    align_photos_button.pack(side=tk.BOTTOM)

    point_cloud_lf = tk.LabelFrame(options, text="Point cloud", padx=10, pady=10)
    point_cloud_lf.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH)

    quality_options = {
        "Ultra high": 1,
        "High": 2,
        "Medium": 4,
        "Low": 8,
        "Lowest": 16
    }

    quality_frame = tk.Frame(point_cloud_lf)
    quality_frame.pack(anchor='w')

    quality_label = tk.Label(quality_frame, text="Quality:")
    quality_label.pack(side=tk.LEFT, anchor='w')

    quality_combo = ttk.Combobox(quality_frame, values=list(quality_options.keys()), state="readonly", width=8)
    quality_combo.current(2)
    quality_combo.pack(side=tk.LEFT, anchor='w', padx=10, pady=10)

    reuse_depth_maps_bool = tk.BooleanVar(value=True)
    reuse_depth_maps_checkbox = tk.Checkbutton(point_cloud_lf, text="Reuse depth maps", variable=reuse_depth_maps_bool)
    reuse_depth_maps_checkbox.pack(anchor='w')

    calculate_point_colors_bool = tk.BooleanVar(value=True)
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

    depth_filtering_frame = tk.Frame(point_cloud_lf)
    depth_filtering_frame.pack(anchor='w')

    depth_filtering_label = tk.Label(depth_filtering_frame, text="Depth filtering:")
    depth_filtering_label.pack(side=tk.LEFT, anchor='w')

    depth_filtering_combo = ttk.Combobox(depth_filtering_frame, values=list(depth_filtering_options.keys()), state="readonly", width=9)
    depth_filtering_combo.current(1)
    depth_filtering_combo.pack(padx=10, pady=10, side=tk.LEFT, anchor='w')

    def build_point_cloud():
        chunk = doc.chunk
        if not chunk:
            raise Exception("No chunk with aligned photos selected")

        quality = quality_options[quality_combo.get()]
        reuse_depth_maps = reuse_depth_maps_bool.get()
        depth_filtering = depth_filtering_options[depth_filtering_combo.get()]
        calculate_point_colors = calculate_point_colors_bool.get()
        calculate_point_confidence = calculate_point_confidence_bool.get()
        point_cloud_path = filedialog.asksaveasfilename(defaultextension=".las", filetypes=[("LAS files", "*.las")])

        print(f"{quality=}, {reuse_depth_maps=}, {depth_filtering=}, {calculate_point_colors=}, {calculate_point_confidence=}, {point_cloud_path=}")

        chunk.buildDepthMaps(downscale=quality, filter_mode=depth_filtering, reuse_depth=reuse_depth_maps)
        chunk.buildPointCloud(point_colors=calculate_point_colors, point_confidence=calculate_point_confidence)
        chunk.exportPointCloud(point_cloud_path)
    
    build_point_cloud_button = tk.Button(point_cloud_lf, text="Build point cloud", command=build_point_cloud)
    build_point_cloud_button.pack()

    three_d_model_lf = tk.LabelFrame(options, text="Model", padx=10, pady=10)
    three_d_model_lf.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH) 

    face_count_options = {
        "Low": Metashape.FaceCount.LowFaceCount,
        "Medium": Metashape.FaceCount.MediumFaceCount,
        "High": Metashape.FaceCount.HighFaceCount,
        "Custom": None
    }

    face_count_frame = tk.Frame(three_d_model_lf)
    face_count_frame.pack(anchor='w')

    face_count_label = tk.Label(face_count_frame, text="Face count:")
    face_count_label.pack(side=tk.LEFT, anchor='w')

    face_count_combo = ttk.Combobox(face_count_frame, values=list(face_count_options.keys()), state="readonly")
    face_count_combo.current(1)
    face_count_combo.pack(side=tk.LEFT, anchor='w', padx=10, pady=10)

    def build_model():
        chunk = doc.chunk
        if not chunk:
            raise Exception("No chunk with point cloud selected")

        face_count = face_count_options[face_count_combo.get()]
        model_path = filedialog.asksaveasfilename(defaultextension=".obj", filetypes=[("OBJ files", "*.obj")])

        if face_count:
            chunk.buildModel(face_count=face_count)
        else:
            face_count = simpledialog.askinteger("Custom face count", "Enter custom face count:")
            if not face_count:
                return
            if face_count < 0:
                raise Exception("Face count must be a positive integer")
            chunk.buildModel(face_count=Metashape.FaceCount.CustomFaceCount, face_count_custom=face_count)
            
        chunk.exportModel(model_path)

    build_model_button = tk.Button(three_d_model_lf, text="Build model", command=build_model)
    build_model_button.pack(side=tk.BOTTOM)

    def do_everything():
        try:
            open_directory()
            align_photos()
            build_point_cloud()
            build_model()
        except Exception as e:
            messagebox.showerror("Error", e)
            return

    do_everything_button = tk.Button(root, text="Do everything", command=do_everything)
    do_everything_button.pack(padx=10, pady=10, fill=tk.X)

    root.mainloop()

app.removeMenuItem("Wizard")
app.addMenuItem("Wizard", wizard)
