import Metashape
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import os
from part_4 import detect_markers, export_camera_orientations, assign_marker_coordinates_from_file

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document
chunk: Metashape.Chunk = doc.chunk

supported_formats = [".jpg", ".jpeg", ".jp2", ".j2k", ".jxl", ".tif", ".tiff", ".png", ".bmp", ".exr", ".tga", ".pgm", ".ppm", ".dng", ".mpo", ".seq", ".ara"]

photos_directory = None

def wizard():
    root = tk.Tk()
    root.title("Wizard")
    root.geometry("780x580")

    def find_photos(directory):
        return [f"{directory}/{filename}" for filename in os.listdir(directory) if filename.lower().endswith(tuple(supported_formats))]

    def open_directory():
        directory = filedialog.askdirectory(title="Select directory with photos")
        global photos_directory
        photos_directory = directory
        
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

    open_directory_button = tk.Button(root, text="Select directory with photos", command=open_directory, bg="pink")
    open_directory_button.pack(padx=10, pady=10, fill=tk.X)

    options = tk.Frame(root)
    options.pack()

    # frame
    first_vertical_frame = tk.Frame(options)
    first_vertical_frame.pack(side=tk.LEFT, fill=tk.BOTH)

    second_vertical_frame = tk.Frame(options)
    second_vertical_frame.pack(side=tk.LEFT, fill=tk.BOTH)

    third_vertical_frame = tk.Frame(options)
    third_vertical_frame.pack(side=tk.LEFT, fill=tk.BOTH)

    align_photos_lf = tk.LabelFrame(first_vertical_frame, text="Align photos", padx=10, pady=10)
    align_photos_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

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

    point_cloud_lf = tk.LabelFrame(third_vertical_frame, text="Point cloud", padx=10, pady=10)
    point_cloud_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

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

    def build_point_cloud(path):
        chunk = doc.chunk
        if not chunk:
            raise Exception("No chunk with aligned photos selected")

        quality = quality_options[quality_combo.get()]
        reuse_depth_maps = reuse_depth_maps_bool.get()
        depth_filtering = depth_filtering_options[depth_filtering_combo.get()]
        calculate_point_colors = calculate_point_colors_bool.get()
        calculate_point_confidence = calculate_point_confidence_bool.get()
        point_cloud_path = photos_directory + "/point_cloud.las"
        
        if path:
            point_cloud_path = path + "/point_cloud.las"
        else:
            point_cloud_path = filedialog.asksaveasfilename(defaultextension=".las", filetypes=[("LAS files", "*.las")])

        print(f"{quality=}, {reuse_depth_maps=}, {depth_filtering=}, {calculate_point_colors=}, {calculate_point_confidence=}, {point_cloud_path=}")

        chunk.buildDepthMaps(downscale=quality, filter_mode=depth_filtering, reuse_depth=reuse_depth_maps)
        chunk.buildPointCloud(point_colors=calculate_point_colors, point_confidence=calculate_point_confidence)
        chunk.exportPointCloud(point_cloud_path)
    
    build_point_cloud_button = tk.Button(point_cloud_lf, text="Build point cloud", command=build_point_cloud)
    build_point_cloud_button.pack(side=tk.BOTTOM)

    three_d_model_lf = tk.LabelFrame(third_vertical_frame, text="Model", padx=10, pady=10)
    three_d_model_lf.pack(side=tk.TOP, padx=10, pady=10) 

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

    def build_model(path):
        chunk = doc.chunk
        if not chunk:
            raise Exception("No chunk with point cloud selected")

        face_count = face_count_options[face_count_combo.get()]
        model_path = photos_directory + "/model.obj"
        if path:
            model_path = path + "/model.obj"
        else:
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

    markers_lf = tk.LabelFrame(first_vertical_frame, text="Markers", padx=10, pady=10)
    markers_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

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

        def save_coordinates():
            try:
                for marker in markers:
                    x, y, z = (
                        float(entries[marker.label][0].get()),
                        float(entries[marker.label][1].get()),
                        float(entries[marker.label][2].get()),
                    )
                    marker.reference.location = Metashape.Vector([x, y, z])
                messagebox.showinfo("Success", "Coordinates assigned successfully")
                window.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")

        save_button = tk.Button(scroll_frame, text="Save Coordinates", command=save_coordinates)
        save_button.pack(pady=10)

        window.mainloop()


    detect_markers_button = tk.Button(markers_lf, text="Detect markers", command=detect_markers)
    detect_markers_button.pack(padx=10, pady=10, fill=tk.X)

    assign_frame = tk.LabelFrame(markers_lf)
    assign_frame.pack()

    assign_label = tk.Label(assign_frame, text="Assign marker coordinates:")
    assign_label.pack(padx=10, pady=10, fill=tk.X)

    assign_marker_coordinates_button = tk.Button(assign_frame, text="Manually", command=assign_marker_coordinates_window)
    assign_marker_coordinates_button.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X)

    assign_marker_coordinates_from_file_button = tk.Button(assign_frame, text="From file", command=assign_marker_coordinates_from_file)
    assign_marker_coordinates_from_file_button.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.X)

    coordinate_system_lf = tk.LabelFrame(second_vertical_frame, text="Coordinate system", padx=10, pady=10)
    coordinate_system_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

    coordinate_system_label = tk.Label(coordinate_system_lf, text="Coordinate system: ")
    coordinate_system_label.pack(side=tk.TOP, anchor='w')

    coordinate_system_options = ["WGS 84", "EPSG:2180", "EPSG:2178", "Other"]
    coordinate_system_combo = ttk.Combobox(coordinate_system_lf, values=coordinate_system_options, state="readonly", width=15)
    coordinate_system_combo.current(0)
    coordinate_system_combo.pack(side=tk.TOP, padx=10, pady=10)

    references_frame = tk.Frame(coordinate_system_lf)
    references_frame.pack(side=tk.TOP, fill=tk.BOTH)

    camera_bool = tk.BooleanVar(value=True)
    camera_checkbox = tk.Checkbutton(references_frame, text="Camera", variable=camera_bool)
    camera_checkbox.pack(side=tk.LEFT, anchor='w')

    markers_bool = tk.BooleanVar(value=True)
    markers_checkbox = tk.Checkbutton(references_frame, text="Markers", variable=markers_bool)
    markers_checkbox.pack(side=tk.RIGHT, anchor='w')

    def convert_coordinates():
        chunk = doc.chunk
        if not chunk:
            raise Exception("No chunk selected")
        
        selected_cs = coordinate_system_combo.get()
        camera = camera_bool.get()
        markers = markers_bool.get()

        epsg_codes = {
            "WGS 84": 4326,
            "EPSG:2180": 2180,
            "EPSG:2178": 2178
        }

        if selected_cs == "Other":
            selected_cs = Metashape.app.getCoordinateSystem()
            if not selected_cs:
                return
        else:
            selected_cs = Metashape.CoordinateSystem(f"EPSG::{epsg_codes[selected_cs]}")

        if camera:
            for camera in chunk.cameras:
                camera.reference.location = Metashape.CoordinateSystem.transform(camera.reference.location, chunk.crs, selected_cs)

        if markers:
            for marker in chunk.markers:
                marker.reference.location = Metashape.CoordinateSystem.transform(marker.reference.location, chunk.crs, selected_cs)
        
        chunk.crs = selected_cs
        chunk.updateTransform()

        messagebox.showinfo("Success", "Coordinates converted")
        

    convert_button = tk.Button(coordinate_system_lf, text="Convert", command=convert_coordinates)
    convert_button.pack()

    export_lf = tk.LabelFrame(second_vertical_frame, text="Camera", padx=10, pady=10)
    export_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

    export_camera_orientations_button = tk.Button(export_lf, text="Export camera orientations", command=export_camera_orientations)
    export_camera_orientations_button.pack(padx=10, pady=10, fill=tk.X)

    def do_everything():
        try:
            open_directory()
            align_photos()
            detect_markers()
            assign_marker_coordinates_from_file()
            convert_coordinates()
            build_point_cloud(photos_directory)
            build_model(photos_directory)
            export_camera_orientations(photos_directory)
        except Exception as e:
            messagebox.showerror("Error", e)
            return
        
        messagebox.showinfo("Success", "All steps completed successfully")

    do_everything_button = tk.Button(root, text="Do everything", command=do_everything)
    do_everything_button.pack(padx=10, pady=10, fill=tk.X)

    root.mainloop()

app.removeMenuItem("Wizard")
app.addMenuItem("Wizard", wizard)
