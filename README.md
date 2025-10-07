# 📄 Escáner de Documentos

Aplicación de escritorio desarrollada en Python para digitalizar documentos usando cámara web o archivos de imagen, con procesamiento automático y exportación a PDF.

## ✨ Características

- **Captura desde cámara web** o archivos (JPG, PNG, BMP, TIFF)
- **Detección automática de bordes** y corrección de perspectiva
- **Ajustes manuales** de brillo, contraste y nitidez
- **Gestión de múltiples páginas** con nombres personalizables
- **Exportación a PDF** multipágina con metadatos
- **OCR para extracción de texto** en español
- **Interfaz gráfica intuitiva** con tkinter

## 🛠️ Instalación

### Requisitos
- Python 3.8+
- Cámara web (opcional)
- Tesseract OCR (se instala automáticamente)

### Pasos
```bash
# Clonar proyecto
git clone https://github.com/usuario/document-scanner.git
cd document-scanner

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

## 🚀 Uso

1. **Ejecutar**: `python main.py`
2. **Capturar**: Desde cámara o cargar archivo
3. **Procesar**: Auto-procesamiento con detección de bordes
4. **Ajustar**: Brillo, contraste y nitidez si es necesario
5. **Guardar**: Como imagen o PDF multipágina

## 🔧 Tecnologías

- **Python** - Lenguaje principal
- **OpenCV** - Procesamiento de imágenes y detección de bordes
- **tkinter** - Interfaz gráfica nativa
- **PIL/Pillow** - Manipulación de imágenes
- **ReportLab** - Generación de PDFs
- **pytesseract** - OCR para extracción de texto
- **NumPy** - Operaciones numéricas

## 📁 Estructura del Proyecto

```
document_scanner/
├── main.py                 # Aplicación principal con GUI
├── document_processor.py   # Procesamiento de imágenes y OCR
├── camera_handler.py       # Manejo de cámara con threading
├── pdf_generator.py        # Generación de PDFs
├── config.py              # Configuración y detección automática
├── requirements.txt       # Dependencias del proyecto
└── README.md             # Documentación
```

## 🎯 Características Destacadas

- **Detección automática de documentos** usando algoritmos de OpenCV
- **Corrección de perspectiva** para enderezar documentos escaneados
- **Interfaz intuitiva** con controles en tiempo real
- **Gestión avanzada de páginas** con edición individual
- **OCR integrado** con optimización automática para texto
- **Exportación profesional** a múltiples formatos

---

*Proyecto desarrollado como parte de mi portafolio de desarrollo en Python*
