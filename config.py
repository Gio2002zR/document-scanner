"""
Archivo de configuración para el escáner de documentos
"""

import os

class Config:
    """Configuración general de la aplicación"""
    
    # Rutas
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')
    
    # Configuración de cámara
    CAMERA_DEFAULT_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Configuración de procesamiento
    GAUSSIAN_BLUR_KERNEL = (5, 5)
    CANNY_THRESHOLD_1 = 50
    CANNY_THRESHOLD_2 = 150
    DILATE_KERNEL_SIZE = (3, 3)
    DILATE_ITERATIONS = 1
    
    # Configuración de OCR
    TESSERACT_CMD = None  # Auto-detectar
    OCR_LANGUAGE = 'spa'  # Español
    OCR_CONFIG = '--oem 3 --psm 6'
    
    # Configuración de PDF
    PDF_PAGE_SIZE = 'A4'
    PDF_MARGIN = 0.5  # pulgadas
    PDF_QUALITY = 95  # 0-100
    
    # Configuración de imagen
    MAX_IMAGE_DIMENSION = 2480
    JPEG_QUALITY = 95
    
    # Formatos soportados
    SUPPORTED_IMAGE_FORMATS = [
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
    ]
    
    # Configuración de interfaz
    WINDOW_TITLE = "Escáner de Documentos Profesional"
    WINDOW_SIZE = "1200x800"
    PREVIEW_MAX_WIDTH = 580
    PREVIEW_MAX_HEIGHT = 480
    
    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        
    @classmethod
    def get_tesseract_path(cls):
        """Detectar automáticamente la ruta de Tesseract"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return None
