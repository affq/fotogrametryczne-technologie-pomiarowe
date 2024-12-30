import Metashape
import cv2
import numpy as np
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import os

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document
chunk: Metashape.Chunk = doc.chunk

def export_internal_orientation():
    chunk = doc.chunk
    if not chunk:
        raise Exception("No chunk selected")
    
    camera = chunk.sensors[0]
    f = camera.calibration.f
    cx, cy = camera.calibration.cx, camera.calibration.cy
    k1, k2, k3 = camera.calibration.k1, camera.calibration.k2, camera.calibration.k3
    p1, p2 = camera.calibration.p1, camera.calibration.p2
    
    np.savetxt("camera_params.txt", [f, cx, cy, k1, k2, p1, p2, k3])

def detect_control_points(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    fast = cv2.FastFeatureDetector_create()
    keypoints = fast.detect(img, None)
    return keypoints

def select_point(image):
    pass

def measure_points(chunk, num_points=3, num_images=3):
    measured_points = []
    for i in range(num_points):
        point_3d = Metashape.Vector([0, 0, 0])
        for j in range(num_images):
            camera = chunk.cameras[j]
            image = cv2.imread(camera.photo.path)
            # kod do automatycznego lub półautomatycznego wyboru punktu
            # point_2d = select_point(image)
            # point_3d += camera.transform.mulp(camera.sensor.calibration.unproject(point_2d))
        measured_points.append(point_3d / num_images)
    return measured_points

def reproject_points(chunk, points_3d):
    camera_matrix = np.array([[chunk.sensors[0].calibration.f, 0, chunk.sensors[0].calibration.cx],
                              [0, chunk.sensors[0].calibration.f, chunk.sensors[0].calibration.cy],
                              [0, 0, 1]])
    dist_coeffs = np.array([chunk.sensors[0].calibration.k1, chunk.sensors[0].calibration.k2,
                            chunk.sensors[0].calibration.p1, chunk.sensors[0].calibration.p2,
                            chunk.sensors[0].calibration.k3])
    
    for camera in chunk.cameras:
        R = camera.transform.rotation().matrix()
        t = camera.transform.translation()
        points_2d, _ = cv2.projectPoints(np.array(points_3d), R, t, camera_matrix, dist_coeffs)
    
    return points_2d
