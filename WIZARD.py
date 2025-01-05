import Metashape
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import os

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document
chunk: Metashape.Chunk = doc.chunk

class Wizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wizard")
        self.geometry("780x640")
        
        self.app = app
        self.doc = doc
        self.chunk = chunk

        self.photos_directory = None

        self.accuracy_options = {"Highest": 0, "High": 1, "Medium": 2, "Low": 4, "Lowest": 8}
        self.quality_options = {"Ultra high": 1, "High": 2, "Medium": 4, "Low": 8, "Lowest": 16}
        self.depth_filtering_options = {"Disabled": Metashape.FilterMode.NoFiltering, "Mild": Metashape.FilterMode.MildFiltering, "Moderate": Metashape.FilterMode.ModerateFiltering, "Aggressive": Metashape.FilterMode.AggressiveFiltering}
        self.face_count_options = { "Low": Metashape.FaceCount.LowFaceCount, "Medium": Metashape.FaceCount.MediumFaceCount, "High": Metashape.FaceCount.HighFaceCount, "Custom": None}
        self.epsg_codes = {"WGS 84": 4326, "EPSG:2180": 2180, "EPSG:2178": 2178}
        self.supported_formats = [".jpg", ".jpeg", ".jp2", ".j2k", ".jxl", ".tif", ".tiff", ".png", ".bmp", ".exr", ".tga", ".pgm", ".ppm", ".dng", ".mpo", ".seq", ".ara"]

        self.MARKER_FILE = None

        self.add_widgets()
        self.mainloop()

    def check_chunk(self):
        if not self.chunk:
            raise Exception("No chunk selected")

    def detect_markers(self):
        self.check_chunk()
        marker_type = Metashape.TargetType.CrossTarget
        self.chunk.detectMarkers(marker_type, tolerance=0)
        for marker in self.chunk.markers:
            if len(marker.projections) < 5:
                self.chunk.remove(marker)
        self.chunk.updateTransform()

    def assign_coordinates(self):
        self.check_chunk()
        for marker in self.chunk.markers:
            marker.reference.location = self.chunk.crs.project(chunk.transform.matrix.mulp(marker.position))
        self.chunk.updateTransform()

    def export_camera_orientations(self, path=None):
        self.check_chunk()
        if path:
            output_file = path + "/camera_orientations.txt"
        else:
            output_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        
        with open(output_file, 'w') as f:
            f.write("label x y z yaw[deg] pitch[deg] roll[deg]\n")
            for camera in self.chunk.cameras:
                if camera.transform:
                    position = camera.transform.translation()
                    rotation = camera.transform.rotation()

                    yaw, pitch, roll = Metashape.utils.mat2ypr(rotation)
                    f.write(f"{camera.label} {position.x} {position.y} {position.z} {yaw} {pitch} {roll}\n")

    def convert_markers(self, selected_cs):
        for marker in self.chunk.markers:
            marker.reference.location = Metashape.CoordinateSystem.transform(marker.reference.location, self.chunk.crs, selected_cs)

        self.chunk.crs = selected_cs
        self.chunk.updateTransform()

    def convert_cameras(self, selected_cs):
        print(f"{self.chunk.crs}")
        print(f"{selected_cs}")
        for camera in self.chunk.cameras:
            camera.reference.location = Metashape.CoordinateSystem.transform(camera.reference.location, self.chunk.crs, selected_cs)

        self.chunk.crs = selected_cs
        self.chunk.updateTransform()

    def load_markers_from_file(self):
        self.check_chunk()
        markers_crs = Metashape.app.getCoordinateSystem()
        
        file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file:
            return
        self.MARKER_FILE = file

        if self.chunk.cameras:
            self.convert_cameras(markers_crs)

        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                label, y, x, z = line.split()
                marker = self.chunk.addMarker()
                marker.label = label
                marker.reference.location = Metashape.Vector([float(x), float(y), float(z)])
        
        self.chunk.crs = markers_crs
        self.chunk.updateTransform()

    def find_photos(self, directory):
        return [f"{directory}/{filename}" for filename in os.listdir(directory) if filename.lower().endswith(tuple(self.supported_formats))]
    
    def open_directory(self):
        cameras_crs = Metashape.app.getCoordinateSystem()
        directory = filedialog.askdirectory(title="Select directory with photos")
        
        if directory:
            self.photos_directory = directory
            photos = self.find_photos(directory)
            
            if not photos:
                raise Exception("No photos found in the selected directory")
            
            if self.chunk is None:
                self.chunk = self.doc.addChunk()

            if self.chunk.markers:
                self.convert_markers(cameras_crs)

            self.chunk.crs = cameras_crs
            self.chunk.addPhotos(photos)
        else:
            raise Exception("No directory selected")
        
    def align_photos(self):
        self.check_chunk()

        accuracy = self.accuracy_options[self.accuracy_combo.get()]
        generic_preselection = self.generic_preselection_bool.get()
        reference_preselection = self.reference_preselection_bool.get()
        reset_current_alignment = self.reset_current_alignment_bool.get()

        self.chunk.matchPhotos(downscale=accuracy, generic_preselection=generic_preselection, reference_preselection=reference_preselection)
        self.chunk.alignCameras(reset_alignment=reset_current_alignment)

    def build_point_cloud(self, path=None):
        self.check_chunk()

        quality = self.quality_options[self.quality_combo.get()]
        reuse_depth_maps = self.reuse_depth_maps_bool.get()
        depth_filtering = self.depth_filtering_options[self.depth_filtering_combo.get()]
        calculate_point_colors = self.calculate_point_colors_bool.get()
        calculate_point_confidence = self.calculate_point_confidence_bool.get()
        point_cloud_path = self.photos_directory + "/point_cloud.las"
        if path:
            point_cloud_path = path + "/point_cloud.las"

        self.chunk.buildDepthMaps(downscale=quality, filter_mode=depth_filtering, reuse_depth=reuse_depth_maps)
        self.chunk.buildPointCloud(point_colors=calculate_point_colors, point_confidence=calculate_point_confidence)
        self.chunk.exportPointCloud(point_cloud_path)

    def build_model(self, path=None):
        self.check_chunk()

        face_count = self.face_count_options[self.face_count_combo.get()]
        model_path = self.photos_directory + "/model.obj"
        if path:
            model_path = path + "/model.obj"

        if face_count:
            self.chunk.buildModel(face_count=face_count)
        else:
            face_count = simpledialog.askinteger("Custom face count", "Enter custom face count:")
            if not face_count:
                return
            if face_count < 0:
                raise Exception("Face count must be a positive integer")
            self.chunk.buildModel(face_count=Metashape.FaceCount.CustomFaceCount, face_count_custom=face_count)
        
        self.chunk.exportModel(model_path)

    def convert_coordinates(self):
        self.check_chunk()
        
        selected_cs = self.coordinate_system_combo.get()
        camera = self.camera_bool.get()
        markers = self.markers_bool.get()

        if selected_cs == "Other":
            selected_cs = Metashape.app.getCoordinateSystem()
            if not selected_cs:
                return
        else:
            selected_cs = Metashape.CoordinateSystem(f"EPSG::{self.epsg_codes[selected_cs]}")

        if camera:
            for camera in self.chunk.cameras:
                camera.reference.location = Metashape.CoordinateSystem.transform(camera.reference.location, self.chunk.crs, selected_cs)

        if markers:
            for marker in self.chunk.markers:
                marker.reference.location = Metashape.CoordinateSystem.transform(marker.reference.location, self.chunk.crs, selected_cs)
        
        self.chunk.crs = selected_cs
        self.chunk.updateTransform()

    def add_open_directory_button(self):
        open_directory_button = tk.Button(self, text="Select directory with photos", command=self.open_directory)
        open_directory_button.pack(padx=10, pady=5, fill=tk.X)

        load_markers_button = tk.Button(self, text="Load markers from file", command=self.load_markers_from_file)
        load_markers_button.pack(padx=10, pady=5, fill=tk.X)
    
    def add_ramki(self):
        self.options = tk.Frame(self)
        self.options.pack()

        self.first_vertical_frame = tk.Frame(self.options)
        self.first_vertical_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        self.second_vertical_frame = tk.Frame(self.options)
        self.second_vertical_frame.pack(side=tk.LEFT, fill=tk.BOTH)

        self.third_vertical_frame = tk.Frame(self.options)
        self.third_vertical_frame.pack(side=tk.LEFT, fill=tk.BOTH)

    def add_align_photos_frame(self):
        align_photos_lf = tk.LabelFrame(self.first_vertical_frame, text="Align photos", padx=10, pady=10)
        align_photos_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

        accuracy_frame = tk.Frame(align_photos_lf)
        accuracy_frame.pack(anchor='w')

        accuracy_label = tk.Label(accuracy_frame, text="Accuracy:")
        accuracy_label.pack(side=tk.LEFT, anchor='w')

        self.accuracy_combo = ttk.Combobox(accuracy_frame, values=list(self.accuracy_options.keys()), state="readonly", width=8)
        self.accuracy_combo.current(2)
        self.accuracy_combo.pack(side=tk.LEFT, anchor='w', padx=10, pady=10)

        self.generic_preselection_bool = tk.BooleanVar(value=True)
        generic_preselection_checkbox = tk.Checkbutton(align_photos_lf, text="Generic preselection", variable=self.generic_preselection_bool)
        generic_preselection_checkbox.pack(anchor='w')

        self.reference_preselection_bool = tk.BooleanVar(value=True)
        reference_preselection_checkbox = tk.Checkbutton(align_photos_lf, text="Reference preselection", variable=self.reference_preselection_bool)
        reference_preselection_checkbox.pack(anchor='w')

        self.reset_current_alignment_bool = tk.BooleanVar()
        reset_current_alignment_checkbox = tk.Checkbutton(align_photos_lf, text="Reset current alignment", variable=self.reset_current_alignment_bool)
        reset_current_alignment_checkbox.pack(anchor='w')

        align_photos_button = tk.Button(align_photos_lf, text="Align photos", command=self.align_photos)
        align_photos_button.pack(side=tk.BOTTOM)

    def add_point_cloud_frame(self):
        point_cloud_lf = tk.LabelFrame(self.third_vertical_frame, text="Point cloud", padx=10, pady=10)
        point_cloud_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

        quality_frame = tk.Frame(point_cloud_lf)
        quality_frame.pack(anchor='w')

        quality_label = tk.Label(quality_frame, text="Quality:")
        quality_label.pack(side=tk.LEFT, anchor='w')

        self.quality_combo = ttk.Combobox(quality_frame, values=list(self.quality_options.keys()), state="readonly", width=8)
        self.quality_combo.current(2)
        self.quality_combo.pack(side=tk.LEFT, anchor='w', padx=10, pady=10)

        self.reuse_depth_maps_bool = tk.BooleanVar(value=True)
        reuse_depth_maps_checkbox = tk.Checkbutton(point_cloud_lf, text="Reuse depth maps", variable=self.reuse_depth_maps_bool)
        reuse_depth_maps_checkbox.pack(anchor='w')

        self.calculate_point_colors_bool = tk.BooleanVar(value=True)
        calculate_point_colors_checkbox = tk.Checkbutton(point_cloud_lf, text="Calculate point colors", variable=self.calculate_point_colors_bool)
        calculate_point_colors_checkbox.pack(anchor='w')

        self.calculate_point_confidence_bool = tk.BooleanVar()
        calculate_point_confidence_checkbox = tk.Checkbutton(point_cloud_lf, text="Calculate point confidence", variable=self.calculate_point_confidence_bool)
        calculate_point_confidence_checkbox.pack(anchor='w')

        depth_filtering_frame = tk.Frame(point_cloud_lf)
        depth_filtering_frame.pack(anchor='w')

        depth_filtering_label = tk.Label(depth_filtering_frame, text="Depth filtering:")
        depth_filtering_label.pack(side=tk.LEFT, anchor='w')

        self.depth_filtering_combo = ttk.Combobox(depth_filtering_frame, values=list(self.depth_filtering_options.keys()), state="readonly", width=9)
        self.depth_filtering_combo.current(1)
        self.depth_filtering_combo.pack(padx=10, pady=10, side=tk.LEFT, anchor='w')

        build_point_cloud_button = tk.Button(point_cloud_lf, text="Build point cloud", command=self.build_point_cloud)
        build_point_cloud_button.pack(side=tk.BOTTOM)

    def add_model_frame(self):
        three_d_model_lf = tk.LabelFrame(self.third_vertical_frame, text="Model", padx=10, pady=10)
        three_d_model_lf.pack(side=tk.TOP, padx=10, pady=10) 

        face_count_frame = tk.Frame(three_d_model_lf)
        face_count_frame.pack(anchor='w')

        face_count_label = tk.Label(face_count_frame, text="Face count:")
        face_count_label.pack(side=tk.LEFT, anchor='w')

        self.face_count_combo = ttk.Combobox(face_count_frame, values=list(self.face_count_options.keys()), state="readonly")
        self.face_count_combo.current(1)
        self.face_count_combo.pack(side=tk.LEFT, anchor='w', padx=10, pady=10)

        build_model_button = tk.Button(three_d_model_lf, text="Build model", command=self.build_model)
        build_model_button.pack(side=tk.BOTTOM)

    def add_markers_frame(self):
        markers_lf = tk.LabelFrame(self.first_vertical_frame, text="Markers", padx=10, pady=10)
        markers_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

        detect_markers_button = tk.Button(markers_lf, text="Detect markers", command=self.detect_markers)
        detect_markers_button.pack(padx=10, pady=10, fill=tk.X)

        assign_marker_coordinates_button = tk.Button(markers_lf, text="Assign marker coordinates", command=self.assign_coordinates)
        assign_marker_coordinates_button.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

        label_markers_button = tk.Button(markers_lf, text="Label markers", command=self.label_markers)
        label_markers_button.pack(side=tk.TOP, padx=10, pady=10, fill=tk.X)

    def add_coordinate_system_frame(self):
        coordinate_system_lf = tk.LabelFrame(self.second_vertical_frame, text="Coordinate system", padx=10, pady=10)
        coordinate_system_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

        coordinate_system_label = tk.Label(coordinate_system_lf, text="Coordinate system: ")
        coordinate_system_label.pack(side=tk.TOP, anchor='w')

        coordinate_system_options = ["WGS 84", "EPSG:2180", "EPSG:2178", "Other"]
        self.coordinate_system_combo = ttk.Combobox(coordinate_system_lf, values=coordinate_system_options, state="readonly", width=15)
        self.coordinate_system_combo.current(0)
        self.coordinate_system_combo.pack(side=tk.TOP, padx=10, pady=10)

        references_frame = tk.Frame(coordinate_system_lf)
        references_frame.pack(side=tk.TOP, fill=tk.BOTH)

        self.camera_bool = tk.BooleanVar(value=True)
        camera_checkbox = tk.Checkbutton(references_frame, text="Camera", variable=self.camera_bool)
        camera_checkbox.pack(side=tk.LEFT, anchor='w')

        self.markers_bool = tk.BooleanVar(value=True)
        markers_checkbox = tk.Checkbutton(references_frame, text="Markers", variable=self.markers_bool)
        markers_checkbox.pack(side=tk.RIGHT, anchor='w')

        convert_button = tk.Button(coordinate_system_lf, text="Convert", command=self.convert_coordinates)
        convert_button.pack()

    def add_export_frame(self):
        export_lf = tk.LabelFrame(self.second_vertical_frame, text="Camera", padx=10, pady=10)
        export_lf.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH)

        export_camera_orientations_button = tk.Button(export_lf, text="Export camera orientations", command=self.export_camera_orientations)
        export_camera_orientations_button.pack(padx=10, pady=10, fill=tk.X)

    def add_do_all_button(self):
        do_everything_button = tk.Button(self, text="Do everything na 3", command=self.do_everything3)
        do_everything_button.pack(padx=10, pady=5, fill=tk.X)

        do_everything_na4_button = tk.Button(self, text="Do everything na 4", command=self.do_everything4)
        do_everything_na4_button.pack(padx=10, fill=tk.X)

    def label_markers(self):
        with open (self.MARKER_FILE, 'r') as f:
            lines = f.readlines()
            for marker in self.chunk.markers:
                smallest_dist = 100000
                for line in lines:
                    label, y, x, z = line.split()
                    dist = (marker.reference.location.x - float(x))**2 + (marker.reference.location.y - float(y))**2 + (marker.reference.location.z - float(z))**2
                    if dist < smallest_dist:
                        smallest_dist = dist
                        marker.label = label                    

    def do_everything4(self):
        try:
            self.chunk.updateTransform()
            self.chunk.optimizeCameras()
            self.detect_markers()
            self.assign_coordinates()
            self.label_markers()
            self.export_camera_orientations(self.photos_directory)
        except Exception as e:
            messagebox.showerror("Error", e)
            return
        messagebox.showinfo("Success", "All steps completed successfully")

    def do_everything3(self):
        try:
            self.align_photos()
            self.detect_markers()
            self.assign_coordinates()
            self.convert_coordinates()
            self.build_point_cloud(self.photos_directory)
            self.build_model(self.photos_directory)
        except Exception as e:
            messagebox.showerror("Error", e)
            return
        messagebox.showinfo("Success", "All steps completed successfully")
    
    def add_widgets(self):
        self.add_open_directory_button()
        self.add_ramki()
        self.add_align_photos_frame()
        self.add_markers_frame()
        self.add_coordinate_system_frame()
        self.add_export_frame()
        self.add_point_cloud_frame()
        self.add_model_frame()
        self.add_do_all_button()

app.removeMenuItem("Wizard")
app.addMenuItem("Wizard", Wizard)