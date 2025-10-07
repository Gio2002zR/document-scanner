"""
Módulo para generación de PDFs
Convierte imágenes escaneadas en documentos PDF de alta calidad
"""

import cv2
import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import io
import os
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        """Inicializar generador de PDF"""
        self.page_size = A4
        self.margin = 0.5 * inch
        self.quality = 95  # Calidad JPEG (0-100)
        
    def create_pdf(self, images, output_path, title="Documento Escaneado"):
        """
        Crear PDF a partir de lista de imágenes
        
        Args:
            images: Lista de imágenes (arrays de OpenCV)
            output_path: Ruta del archivo PDF de salida
            title: Título del documento
        """
        try:
            # Crear documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin
            )
            
            # Contenido del PDF
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = styles['Title']
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Procesar cada imagen
            for i, image in enumerate(images):
                # Convertir imagen de OpenCV a PIL
                pil_image = self._opencv_to_pil(image)
                
                # Optimizar imagen para PDF
                optimized_image = self._optimize_for_pdf(pil_image)
                
                # Crear objeto imagen temporal
                img_buffer = io.BytesIO()
                optimized_image.save(img_buffer, format='JPEG', quality=self.quality)
                img_buffer.seek(0)
                
                # Calcular dimensiones para ajustar a página
                img_width, img_height = optimized_image.size
                page_width = self.page_size[0] - 2 * self.margin
                page_height = self.page_size[1] - 2 * self.margin
                
                # Calcular escala manteniendo proporción
                scale = min(page_width / img_width, page_height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Agregar imagen al PDF
                rl_image = RLImage(img_buffer, width=new_width, height=new_height)
                story.append(rl_image)
                
                # Agregar espacio entre páginas (excepto la última)
                if i < len(images) - 1:
                    story.append(Spacer(1, 20))
                    
            # Construir PDF
            doc.build(story)
            
            return True
            
        except Exception as e:
            print(f"Error creando PDF: {e}")
            return False
            
    def create_pdf_with_metadata(self, images, output_path, metadata=None):
        """
        Crear PDF con metadatos personalizados
        
        Args:
            images: Lista de imágenes
            output_path: Ruta de salida
            metadata: Dict con metadatos (title, author, subject, etc.)
        """
        try:
            # Metadatos por defecto
            if metadata is None:
                metadata = {}
                
            default_metadata = {
                'title': 'Documento Escaneado',
                'author': 'Escáner de Documentos',
                'subject': 'Documento digitalizado',
                'creator': 'Document Scanner App',
                'producer': 'Document Scanner PDF Generator',
                'creationDate': datetime.now(),
                'modDate': datetime.now()
            }
            
            # Combinar metadatos
            final_metadata = {**default_metadata, **metadata}
            
            # Crear PDF con canvas para más control
            c = canvas.Canvas(output_path, pagesize=self.page_size)
            
            # Establecer metadatos
            c.setTitle(final_metadata['title'])
            c.setAuthor(final_metadata['author'])
            c.setSubject(final_metadata['subject'])
            c.setCreator(final_metadata['creator'])
            c.setProducer(final_metadata['producer'])
            
            # Procesar cada imagen
            for image in images:
                # Convertir y optimizar imagen
                pil_image = self._opencv_to_pil(image)
                optimized_image = self._optimize_for_pdf(pil_image)
                
                # Guardar imagen temporal
                temp_path = f"temp_page_{id(image)}.jpg"
                optimized_image.save(temp_path, 'JPEG', quality=self.quality)
                
                # Calcular posición y tamaño
                img_width, img_height = optimized_image.size
                page_width = self.page_size[0] - 2 * self.margin
                page_height = self.page_size[1] - 2 * self.margin
                
                scale = min(page_width / img_width, page_height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Centrar imagen en página
                x = (self.page_size[0] - new_width) / 2
                y = (self.page_size[1] - new_height) / 2
                
                # Dibujar imagen
                c.drawImage(temp_path, x, y, width=new_width, height=new_height)
                
                # Nueva página (excepto para la última imagen)
                if image is not images[-1]:
                    c.showPage()
                    
                # Limpiar archivo temporal
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
            # Guardar PDF
            c.save()
            
            return True
            
        except Exception as e:
            print(f"Error creando PDF con metadatos: {e}")
            return False
            
    def create_searchable_pdf(self, images, output_path, ocr_texts=None):
        """
        Crear PDF con texto searchable (requiere texto OCR)
        
        Args:
            images: Lista de imágenes
            output_path: Ruta de salida
            ocr_texts: Lista de textos extraídos por OCR (opcional)
        """
        try:
            c = canvas.Canvas(output_path, pagesize=self.page_size)
            
            for i, image in enumerate(images):
                # Procesar imagen
                pil_image = self._opencv_to_pil(image)
                optimized_image = self._optimize_for_pdf(pil_image)
                
                # Guardar imagen temporal
                temp_path = f"temp_searchable_{i}.jpg"
                optimized_image.save(temp_path, 'JPEG', quality=self.quality)
                
                # Calcular dimensiones
                img_width, img_height = optimized_image.size
                page_width = self.page_size[0] - 2 * self.margin
                page_height = self.page_size[1] - 2 * self.margin
                
                scale = min(page_width / img_width, page_height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                x = (self.page_size[0] - new_width) / 2
                y = (self.page_size[1] - new_height) / 2
                
                # Dibujar imagen
                c.drawImage(temp_path, x, y, width=new_width, height=new_height)
                
                # Agregar texto invisible si hay OCR
                if ocr_texts and i < len(ocr_texts):
                    self._add_invisible_text(c, ocr_texts[i], x, y, new_width, new_height)
                    
                # Nueva página
                if i < len(images) - 1:
                    c.showPage()
                    
                # Limpiar temporal
                try:
                    os.remove(temp_path)
                except:
                    pass
                    
            c.save()
            return True
            
        except Exception as e:
            print(f"Error creando PDF searchable: {e}")
            return False
            
    def _opencv_to_pil(self, opencv_image):
        """Convertir imagen de OpenCV a PIL"""
        if len(opencv_image.shape) == 3:
            # BGR a RGB
            rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
        else:
            # Escala de grises a RGB
            rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_GRAY2RGB)
            
        return Image.fromarray(rgb_image)
        
    def _optimize_for_pdf(self, pil_image):
        """Optimizar imagen PIL para PDF"""
        # Convertir a RGB si es necesario
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
            
        # Redimensionar si es muy grande
        max_dimension = 2480  # Máximo para buena calidad
        width, height = pil_image.size
        
        if max(width, height) > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
                
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
        return pil_image
        
    def _add_invisible_text(self, canvas, text, x, y, width, height):
        """Agregar texto invisible para búsquedas"""
        try:
            # Configurar texto invisible
            canvas.setFillColorRGB(1, 1, 1, alpha=0)  # Texto transparente
            canvas.setFont("Helvetica", 8)
            
            # Dividir texto en líneas
            lines = text.split('\n')
            line_height = 10
            
            for i, line in enumerate(lines[:50]):  # Máximo 50 líneas
                text_y = y + height - (i + 1) * line_height
                if text_y > y:  # Solo si está dentro del área de imagen
                    canvas.drawString(x, text_y, line.strip())
                    
        except Exception as e:
            print(f"Error agregando texto invisible: {e}")
            
    def merge_pdfs(self, pdf_paths, output_path):
        """Combinar múltiples PDFs en uno solo"""
        try:
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    merger.append(pdf_path)
                    
            merger.write(output_path)
            merger.close()
            
            return True
            
        except ImportError:
            print("PyPDF2 no está instalado. Instalar con: pip install PyPDF2")
            return False
        except Exception as e:
            print(f"Error combinando PDFs: {e}")
            return False
            
    def compress_pdf(self, input_path, output_path, quality='medium'):
        """Comprimir PDF existente"""
        try:
            # Configuraciones de calidad
            quality_settings = {
                'low': 50,
                'medium': 75,
                'high': 90
            }
            
            jpeg_quality = quality_settings.get(quality, 75)
            
            # Leer PDF y re-comprimir imágenes
            # Nota: Esto requeriría una implementación más compleja
            # Por ahora, copiamos el archivo
            import shutil
            shutil.copy2(input_path, output_path)
            
            return True
            
        except Exception as e:
            print(f"Error comprimiendo PDF: {e}")
            return False
            
    def set_page_size(self, size='A4'):
        """Configurar tamaño de página"""
        sizes = {
            'A4': A4,
            'Letter': letter,
            'Legal': (612, 1008)
        }
        
        if size in sizes:
            self.page_size = sizes[size]
            return True
        return False
        
    def set_quality(self, quality):
        """Configurar calidad JPEG (0-100)"""
        if 0 <= quality <= 100:
            self.quality = quality
            return True
        return False
