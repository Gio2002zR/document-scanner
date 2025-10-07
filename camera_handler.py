"""
Módulo para manejo de cámara web
Incluye captura, configuración y optimización de calidad
"""

import cv2
import numpy as np
import threading
import time

class CameraHandler:
    def __init__(self):
        """Inicializar manejador de cámara"""
        self.camera = None
        self.is_active = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
        # Configuraciones de cámara
        self.camera_index = 0
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
        
    def start_camera(self, camera_index=0):
        """Iniciar cámara"""
        try:
            self.camera_index = camera_index
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                return False
                
            # Configurar resolución y FPS
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Configuraciones adicionales para mejor calidad
            self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Exposición manual
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Autofocus
            
            # Probar captura
            ret, frame = self.camera.read()
            if not ret:
                self.camera.release()
                return False
                
            self.is_active = True
            
            # Iniciar hilo de captura
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error iniciando cámara: {e}")
            return False
            
    def stop_camera(self):
        """Detener cámara"""
        self.is_active = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
            
        if self.camera:
            self.camera.release()
            self.camera = None
            
        with self.frame_lock:
            self.current_frame = None
            
    def _capture_loop(self):
        """Loop de captura en hilo separado"""
        while self.is_active and self.camera and self.camera.isOpened():
            try:
                ret, frame = self.camera.read()
                if ret:
                    # Mejorar calidad del frame
                    enhanced_frame = self._enhance_frame(frame)
                    
                    with self.frame_lock:
                        self.current_frame = enhanced_frame.copy()
                else:
                    time.sleep(0.01)  # Breve pausa si no hay frame
                    
            except Exception as e:
                print(f"Error en loop de captura: {e}")
                break
                
        self.is_active = False
        
    def get_frame(self):
        """Obtener frame actual"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None
            
    def _enhance_frame(self, frame):
        """Mejorar calidad del frame"""
        try:
            # Aplicar filtro para reducir ruido
            denoised = cv2.bilateralFilter(frame, 9, 75, 75)
            
            # Mejorar nitidez
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            # Ajustar brillo y contraste automáticamente
            lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception as e:
            print(f"Error mejorando frame: {e}")
            return frame
            
    def capture_high_quality(self):
        """Capturar imagen de alta calidad"""
        if not self.is_active or not self.camera:
            return None
            
        try:
            # Tomar múltiples frames y seleccionar el mejor
            frames = []
            for _ in range(5):
                ret, frame = self.camera.read()
                if ret:
                    frames.append(frame)
                time.sleep(0.1)
                
            if not frames:
                return None
                
            # Seleccionar frame con mejor nitidez
            best_frame = self._select_sharpest_frame(frames)
            
            # Aplicar mejoras adicionales
            enhanced = self._enhance_for_document(best_frame)
            
            return enhanced
            
        except Exception as e:
            print(f"Error capturando imagen de alta calidad: {e}")
            return self.get_frame()
            
    def _select_sharpest_frame(self, frames):
        """Seleccionar el frame más nítido"""
        max_variance = 0
        best_frame = frames[0]
        
        for frame in frames:
            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calcular varianza del Laplaciano (medida de nitidez)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if variance > max_variance:
                max_variance = variance
                best_frame = frame
                
        return best_frame
        
    def _enhance_for_document(self, frame):
        """Mejorar frame específicamente para documentos"""
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Aplicar filtro gaussiano
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Umbralización adaptativa
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Convertir de vuelta a BGR
            result = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            
            return result
            
        except Exception as e:
            print(f"Error mejorando para documento: {e}")
            return frame
            
    def set_camera_properties(self, brightness=None, contrast=None, saturation=None):
        """Configurar propiedades de la cámara"""
        if not self.camera or not self.camera.isOpened():
            return False
            
        try:
            if brightness is not None:
                self.camera.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
                
            if contrast is not None:
                self.camera.set(cv2.CAP_PROP_CONTRAST, contrast)
                
            if saturation is not None:
                self.camera.set(cv2.CAP_PROP_SATURATION, saturation)
                
            return True
            
        except Exception as e:
            print(f"Error configurando propiedades: {e}")
            return False
            
    def get_camera_info(self):
        """Obtener información de la cámara"""
        if not self.camera or not self.camera.isOpened():
            return None
            
        try:
            info = {
                'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.camera.get(cv2.CAP_PROP_FPS),
                'brightness': self.camera.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': self.camera.get(cv2.CAP_PROP_CONTRAST),
                'saturation': self.camera.get(cv2.CAP_PROP_SATURATION),
                'auto_exposure': self.camera.get(cv2.CAP_PROP_AUTO_EXPOSURE)
            }
            return info
            
        except Exception as e:
            print(f"Error obteniendo información: {e}")
            return None
            
    def list_available_cameras(self):
        """Listar cámaras disponibles"""
        available_cameras = []
        
        for i in range(5):  # Probar primeros 5 índices
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(i)
                cap.release()
            except:
                continue
                
        return available_cameras
        
    def switch_camera(self, camera_index):
        """Cambiar a otra cámara"""
        if self.is_active:
            self.stop_camera()
            
        return self.start_camera(camera_index)
        
    def save_frame(self, filename=None):
        """Guardar frame actual"""
        frame = self.get_frame()
        if frame is None:
            return False
            
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            
        try:
            cv2.imwrite(filename, frame)
            return True
        except Exception as e:
            print(f"Error guardando frame: {e}")
            return False
