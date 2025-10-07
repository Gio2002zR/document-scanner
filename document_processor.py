"""
Módulo de procesamiento de documentos
Incluye detección de bordes, corrección de perspectiva, mejoras de calidad y OCR
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from skimage import filters
from imutils import contours
import imutils

class DocumentProcessor:
    def __init__(self):
        """Inicializar procesador de documentos"""
        # Configurar Tesseract (ajustar ruta si es necesario)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def process_document(self, image):
        """
        Procesar documento completo: detección, corrección de perspectiva y mejoras
        """
        try:
            # 1. Preprocesamiento
            preprocessed = self.preprocess_image(image)
            
            # 2. Detectar contorno del documento
            document_contour = self.detect_document_contour(preprocessed)
            
            if document_contour is not None:
                # 3. Corregir perspectiva
                corrected = self.correct_perspective(image, document_contour)
                
                # 4. Mejorar calidad
                enhanced = self.enhance_image(corrected)
                
                return enhanced
            else:
                # Si no se detecta documento, aplicar mejoras básicas
                return self.enhance_image(image)
                
        except Exception as e:
            print(f"Error procesando documento: {e}")
            return None
            
    def preprocess_image(self, image):
        """Preprocesar imagen para detección de contornos"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro gaussiano para reducir ruido
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detectar bordes usando Canny
        edges = cv2.Canny(blurred, 50, 150)
        
        # Dilatar para cerrar espacios
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        return dilated
        
    def detect_document_contour(self, processed_image):
        """Detectar contorno del documento"""
        # Encontrar contornos
        cnts = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        
        if not cnts:
            return None
            
        # Ordenar contornos por área (el más grande primero)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        
        # Buscar contorno rectangular
        for cnt in cnts[:5]:  # Revisar los 5 contornos más grandes
            # Aproximar contorno
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            # Si tiene 4 puntos, es probable que sea un documento
            if len(approx) == 4:
                return approx
                
        return None
        
    def correct_perspective(self, image, contour):
        """Corregir perspectiva del documento"""
        # Obtener los 4 puntos del contorno
        pts = contour.reshape(4, 2)
        
        # Ordenar puntos: top-left, top-right, bottom-right, bottom-left
        rect = self.order_points(pts)
        
        # Calcular dimensiones del documento corregido
        (tl, tr, br, bl) = rect
        
        # Calcular ancho
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        # Calcular altura
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        # Definir puntos de destino
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")
        
        # Calcular matriz de transformación perspectiva
        M = cv2.getPerspectiveTransform(rect, dst)
        
        # Aplicar transformación
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
        
    def order_points(self, pts):
        """Ordenar puntos en orden: top-left, top-right, bottom-right, bottom-left"""
        rect = np.zeros((4, 2), dtype="float32")
        
        # Top-left: suma mínima
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        
        # Bottom-right: suma máxima
        rect[2] = pts[np.argmax(s)]
        
        # Top-right: diferencia mínima
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        
        # Bottom-left: diferencia máxima
        rect[3] = pts[np.argmax(diff)]
        
        return rect
        
    def enhance_image(self, image):
        """Mejorar calidad de la imagen"""
        # Convertir a escala de grises si es necesario
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Aplicar umbralización adaptativa para mejorar contraste
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Aplicar filtro de mediana para reducir ruido
        denoised = cv2.medianBlur(adaptive_thresh, 3)
        
        # Convertir de vuelta a BGR si la imagen original era en color
        if len(image.shape) == 3:
            result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
        else:
            result = denoised
            
        return result
        
    def apply_adjustments(self, image, brightness=1.0, contrast=1.0, sharpness=1.0):
        """Aplicar ajustes de brillo, contraste y nitidez"""
        try:
            # Convertir de OpenCV a PIL
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                
            pil_image = Image.fromarray(image_rgb)
            
            # Aplicar brillo
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(pil_image)
                pil_image = enhancer.enhance(brightness)
                
            # Aplicar contraste
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(pil_image)
                pil_image = enhancer.enhance(contrast)
                
            # Aplicar nitidez
            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(pil_image)
                pil_image = enhancer.enhance(sharpness)
                
            # Convertir de vuelta a OpenCV
            result_array = np.array(pil_image)
            result_bgr = cv2.cvtColor(result_array, cv2.COLOR_RGB2BGR)
            
            return result_bgr
            
        except Exception as e:
            print(f"Error aplicando ajustes: {e}")
            return image
            
    def extract_text(self, image):
        """Extraer texto usando OCR"""
        try:
            # Preprocesar imagen para OCR
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
                
            # Mejorar imagen para OCR
            # Redimensionar si es muy pequeña
            height, width = gray.shape
            if height < 300 or width < 300:
                scale = max(300/height, 300/width)
                new_height = int(height * scale)
                new_width = int(width * scale)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
                
            # Aplicar umbralización
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Reducir ruido
            denoised = cv2.medianBlur(thresh, 3)
            
            # Configuración de Tesseract para español
            config = '--oem 3 --psm 6 -l spa'
            
            # Extraer texto
            text = pytesseract.image_to_string(denoised, config=config)
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error en OCR: {e}")
            
    def improve_for_ocr(self, image):
        """Mejorar imagen específicamente para OCR"""
        # Convertir a escala de grises
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Redimensionar si es necesario
        height, width = gray.shape
        if height < 500:
            scale = 500 / height
            new_height = int(height * scale)
            new_width = int(width * scale)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
        # Aplicar filtro bilateral para reducir ruido manteniendo bordes
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Umbralización adaptativa
        thresh = cv2.adaptiveThreshold(
            bilateral, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Operaciones morfológicas para limpiar
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    def detect_text_regions(self, image):
        """Detectar regiones de texto en la imagen"""
        try:
            # Convertir a escala de grises
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
                
            # Aplicar morfología para conectar texto
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filtrar por tamaño (probable texto)
                if w > 20 and h > 10 and w < gray.shape[1] * 0.8:
                    text_regions.append((x, y, w, h))
                    
            return text_regions
            
        except Exception as e:
            print(f"Error detectando regiones de texto: {e}")
            return []
