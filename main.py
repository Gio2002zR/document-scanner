#!/usr/bin/env python3
"""
Escáner de Documentos Completo
Autor: Asistente IA
Fecha: Septiembre 2025

Este escáner de documentos incluye:
- Interfaz gráfica intuitiva
- Captura desde cámara web o archivos
- Procesamiento automático de imágenes
- Detección y corrección de perspectiva
- Mejoras de calidad (brillo, contraste, nitidez)
- Exportación a PDF y otros formatos
- OCR para reconocimiento de texto
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageEnhance
import os
import sys
import threading
from datetime import datetime
from document_processor import DocumentProcessor
from camera_handler import CameraHandler
from pdf_generator import PDFGenerator

class DocumentScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Escáner de Documentos Profesional")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar componentes
        self.document_processor = DocumentProcessor()
        self.camera_handler = CameraHandler()
        self.pdf_generator = PDFGenerator()
        
        # Variables
        self.current_image = None
        self.processed_image = None
        self.scanned_pages = []  # Lista de diccionarios con imagen y nombre
        self.is_camera_active = False
        self.page_counter = 0
        self.selected_page_index = None  # Índice de la página seleccionada para edición
        
        # Configurar interfaz
        self.setup_ui()
        
        # Configurar eventos
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Panel de controles (izquierda)
        self.setup_control_panel(main_frame)
        
        # Panel de vista previa (centro)
        self.setup_preview_panel(main_frame)
        
        # Panel de páginas escaneadas (derecha)
        self.setup_pages_panel(main_frame)
        
        # Barra de estado
        self.setup_status_bar(main_frame)
        
    def setup_control_panel(self, parent):
        """Panel de controles"""
        control_frame = ttk.LabelFrame(parent, text="Controles", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Información de edición
        self.edit_info_label = ttk.Label(control_frame, text="Modo: Nueva imagen", 
                                        font=("Arial", 9, "italic"), 
                                        foreground="blue")
        self.edit_info_label.pack(pady=(0, 10))
        
        # Botones de captura
        capture_frame = ttk.LabelFrame(control_frame, text="Captura", padding="5")
        capture_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.camera_btn = ttk.Button(capture_frame, text="📷 Abrir Cámara", 
                                   command=self.toggle_camera, width=20)
        self.camera_btn.pack(pady=2)
        
        self.file_btn = ttk.Button(capture_frame, text="📁 Seleccionar Archivo", 
                                 command=self.open_file, width=20)
        self.file_btn.pack(pady=2)
        
        self.capture_btn = ttk.Button(capture_frame, text="📸 Capturar", 
                                    command=self.capture_image, width=20, 
                                    state=tk.DISABLED)
        self.capture_btn.pack(pady=2)
        
        # Controles de procesamiento
        process_frame = ttk.LabelFrame(control_frame, text="Procesamiento", padding="5")
        process_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_process_btn = ttk.Button(process_frame, text="🔄 Auto Procesar", 
                                         command=self.auto_process, width=20)
        self.auto_process_btn.pack(pady=2)
        
        # Controles de ajuste
        adjust_frame = ttk.LabelFrame(control_frame, text="Ajustes", padding="5")
        adjust_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Información de imagen siendo editada
        self.edit_info_label = ttk.Label(adjust_frame, text="Editando: Nueva imagen", 
                                       font=("Arial", 8), foreground="blue")
        self.edit_info_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Brillo
        ttk.Label(adjust_frame, text="Brillo:").pack(anchor=tk.W)
        self.brightness_var = tk.DoubleVar(value=1.0)
        self.brightness_scale = ttk.Scale(adjust_frame, from_=0.5, to=2.0, 
                                        variable=self.brightness_var, 
                                        command=self.apply_adjustments)
        self.brightness_scale.pack(fill=tk.X, pady=2)
        
        # Contraste
        ttk.Label(adjust_frame, text="Contraste:").pack(anchor=tk.W)
        self.contrast_var = tk.DoubleVar(value=1.0)
        self.contrast_scale = ttk.Scale(adjust_frame, from_=0.5, to=2.0, 
                                      variable=self.contrast_var, 
                                      command=self.apply_adjustments)
        self.contrast_scale.pack(fill=tk.X, pady=2)
        
        # Nitidez
        ttk.Label(adjust_frame, text="Nitidez:").pack(anchor=tk.W)
        self.sharpness_var = tk.DoubleVar(value=1.0)
        self.sharpness_scale = ttk.Scale(adjust_frame, from_=0.0, to=3.0, 
                                       variable=self.sharpness_var, 
                                       command=self.apply_adjustments)
        self.sharpness_scale.pack(fill=tk.X, pady=2)
        
        # Botón de reset
        ttk.Button(adjust_frame, text="↺ Reset", command=self.reset_adjustments).pack(pady=5)
        
        # Controles de salida
        output_frame = ttk.LabelFrame(control_frame, text="Salida", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.add_page_btn = ttk.Button(output_frame, text="➕ Añadir Página", 
                                     command=self.add_page, width=20)
        self.add_page_btn.pack(pady=2)
        
        self.save_image_btn = ttk.Button(output_frame, text="💾 Guardar Imagen", 
                                       command=self.save_image, width=20)
        self.save_image_btn.pack(pady=2)
        
        self.generate_pdf_btn = ttk.Button(output_frame, text="📄 Generar PDF", 
                                         command=self.generate_pdf, width=20)
        self.generate_pdf_btn.pack(pady=2)
        
        self.ocr_btn = ttk.Button(output_frame, text="🔍 Extraer Texto (OCR)", 
                                command=self.extract_text, width=20)
        self.ocr_btn.pack(pady=2)
        
    def setup_preview_panel(self, parent):
        """Panel de vista previa"""
        preview_frame = ttk.LabelFrame(parent, text="Vista Previa", padding="10")
        preview_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Canvas para mostrar imagen
        self.preview_canvas = tk.Canvas(preview_frame, bg='white', width=600, height=500)
        self.preview_canvas.pack(expand=True, fill=tk.BOTH)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        h_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        self.preview_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
    def setup_pages_panel(self, parent):
        """Panel de páginas escaneadas"""
        pages_frame = ttk.LabelFrame(parent, text="Páginas Escaneadas", padding="10")
        pages_frame.grid(row=0, column=2, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Lista de páginas
        self.pages_listbox = tk.Listbox(pages_frame, width=20, height=20)
        self.pages_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Botones de gestión de páginas
        pages_buttons_frame = ttk.Frame(pages_frame)
        pages_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(pages_buttons_frame, text="Ver", command=self.view_page, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(pages_buttons_frame, text="Renombrar", command=self.rename_page, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(pages_buttons_frame, text="Eliminar", command=self.delete_page, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(pages_buttons_frame, text="Subir", command=self.move_page_up, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(pages_buttons_frame, text="Bajar", command=self.move_page_down, width=8).pack(side=tk.LEFT, padx=2)
        
        pages_buttons_frame2 = ttk.Frame(pages_frame)
        pages_buttons_frame2.pack(fill=tk.X, pady=(2, 0))
        
        ttk.Button(pages_buttons_frame2, text="Actualizar", command=self.update_selected_page, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(pages_buttons_frame2, text="Nueva Imagen", command=self.new_image_mode, width=12).pack(side=tk.LEFT, padx=2)
        
        pages_buttons_frame3 = ttk.Frame(pages_frame)
        pages_buttons_frame3.pack(fill=tk.X, pady=(2, 0))
        
        ttk.Button(pages_buttons_frame3, text="Limpiar Todo", command=self.clear_pages, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(pages_buttons_frame3, text="Duplicar", command=self.duplicate_page, width=12).pack(side=tk.LEFT, padx=2)
        
    def setup_status_bar(self, parent):
        """Barra de estado"""
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def toggle_camera(self):
        """Activar/desactivar cámara"""
        if not self.is_camera_active:
            if self.camera_handler.start_camera():
                self.is_camera_active = True
                self.camera_btn.config(text="📷 Cerrar Cámara")
                self.capture_btn.config(state=tk.NORMAL)
                self.update_camera_feed()
                self.status_var.set("Cámara activa")
            else:
                messagebox.showerror("Error", "No se pudo acceder a la cámara")
        else:
            self.camera_handler.stop_camera()
            self.is_camera_active = False
            self.camera_btn.config(text="📷 Abrir Cámara")
            self.capture_btn.config(state=tk.DISABLED)
            
            # Limpiar el canvas cuando se cierra la cámara
            self.preview_canvas.delete("all")
            
            self.status_var.set("Cámara cerrada")
            
    def update_camera_feed(self):
        """Actualizar feed de la cámara"""
        if self.is_camera_active:
            frame = self.camera_handler.get_frame()
            if frame is not None:
                self.display_image(frame)
            self.root.after(30, self.update_camera_feed)
            
    def open_file(self):
        """Abrir archivo de imagen"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                # Cambiar a modo nueva imagen
                self.selected_page_index = None
                self.current_image = image.copy()
                self.processed_image = None
                
                # Reset ajustes
                self.reset_adjustments()
                
                # Actualizar información
                self.edit_info_label.config(text="Editando: Nueva imagen")
                
                # Mostrar imagen
                self.display_image(image)
                self.status_var.set(f"Archivo cargado: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", "No se pudo cargar la imagen")
                
    def capture_image(self):
        """Capturar imagen desde cámara"""
        if self.is_camera_active:
            frame = self.camera_handler.get_frame()
            if frame is not None:
                # Detener la cámara primero
                self.camera_handler.stop_camera()
                self.is_camera_active = False
                self.camera_btn.config(text="📷 Abrir Cámara")
                self.capture_btn.config(state=tk.DISABLED)
                
                # Cambiar a modo nueva imagen
                self.selected_page_index = None
                self.current_image = frame.copy()
                self.processed_image = None
                
                # Reset ajustes
                self.reset_adjustments()
                
                # Actualizar información
                self.edit_info_label.config(text="Editando: Nueva imagen")
                
                # Mostrar la imagen capturada
                self.display_image(self.current_image)
                
                self.status_var.set("Imagen capturada - Cámara cerrada")
            else:
                messagebox.showerror("Error", "No se pudo capturar la imagen")
                
    def display_image(self, image):
        """Mostrar imagen en el canvas"""
        # Convertir de BGR a RGB
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image
            
        # Redimensionar para el canvas
        height, width = image_rgb.shape[:2]
        max_width, max_height = 580, 480
        
        scale = min(max_width/width, max_height/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        image_resized = cv2.resize(image_rgb, (new_width, new_height))
        
        # Convertir a PhotoImage
        image_pil = Image.fromarray(image_resized)
        self.photo = ImageTk.PhotoImage(image_pil)
        
        # Mostrar en canvas
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(
            max_width//2, max_height//2, 
            image=self.photo, anchor=tk.CENTER
        )
        
    def auto_process(self):
        """Procesamiento automático del documento"""
        if self.current_image is None:
            messagebox.showwarning("Advertencia", "No hay imagen para procesar")
            return
            
        self.status_var.set("Procesando imagen...")
        
        # Ejecutar en hilo separado para no bloquear UI
        threading.Thread(target=self._process_image, daemon=True).start()
        
    def _process_image(self):
        """Procesar imagen en hilo separado"""
        try:
            processed = self.document_processor.process_document(self.current_image)
            if processed is not None:
                self.processed_image = processed
                self.root.after(0, lambda: self.display_image(processed))
                self.root.after(0, lambda: self.status_var.set("Imagen procesada exitosamente"))
            else:
                self.root.after(0, lambda: self.status_var.set("No se pudo procesar la imagen"))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error procesando imagen: {error_msg}"))
            
    def apply_adjustments(self, *args):
        """Aplicar ajustes de brillo, contraste y nitidez"""
        # Determinar qué imagen usar como base
        base_image = None
        editing_info = ""
        
        if self.selected_page_index is not None and self.selected_page_index < len(self.scanned_pages):
            # Editando una página existente
            base_image = self.scanned_pages[self.selected_page_index]['image']
            editing_info = f"Editando: {self.scanned_pages[self.selected_page_index]['name']}"
        elif self.current_image is not None:
            # Editando imagen nueva
            base_image = self.current_image
            editing_info = "Editando: Nueva imagen"
        else:
            return
            
        try:
            # Obtener valores de los sliders
            brightness = self.brightness_var.get()
            contrast = self.contrast_var.get()
            sharpness = self.sharpness_var.get()
            
            # Aplicar ajustes
            adjusted = self.document_processor.apply_adjustments(
                base_image, brightness, contrast, sharpness
            )
            
            if adjusted is not None:
                self.processed_image = adjusted
                self.display_image(adjusted)
                
                # Actualizar información
                self.edit_info_label.config(text=editing_info + " (Modificada)")
                
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Error", f"Error aplicando ajustes: {error_msg}")
            
    def reset_adjustments(self):
        """Resetear ajustes a valores por defecto"""
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.sharpness_var.set(1.0)
        
        # Resetear imagen procesada
        self.processed_image = None
        
        # Mostrar imagen original
        if self.selected_page_index is not None and self.selected_page_index < len(self.scanned_pages):
            # Mostrando página seleccionada
            page_data = self.scanned_pages[self.selected_page_index]
            self.display_image(page_data['image'])
            self.edit_info_label.config(text=f"Editando: {page_data['name']}")
        elif self.current_image is not None:
            # Mostrando imagen nueva
            self.display_image(self.current_image)
            self.edit_info_label.config(text="Editando: Nueva imagen")
            
    def add_page(self):
        """Añadir página actual a la lista"""
        image_to_add = self.processed_image if self.processed_image is not None else self.current_image
        
        if image_to_add is None:
            messagebox.showwarning("Advertencia", "No hay imagen para añadir")
            return
        
        # Crear ventana para nombrar la página
        dialog = tk.Toplevel(self.root)
        dialog.title("Nombrar Página")
        dialog.geometry("350x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Variables
        page_name = tk.StringVar()
        self.page_counter += 1
        default_name = f"Página {self.page_counter}"
        page_name.set(default_name)
        
        # Contenido de la ventana
        ttk.Label(dialog, text="Nombre de la página:").pack(pady=10)
        
        entry_frame = ttk.Frame(dialog)
        entry_frame.pack(pady=5, padx=20, fill=tk.X)
        
        name_entry = ttk.Entry(entry_frame, textvariable=page_name, font=("Arial", 10))
        name_entry.pack(fill=tk.X)
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        # Botones
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def add_with_name():
            name = page_name.get().strip()
            if not name:
                name = default_name
            
            # Crear copia profunda de la imagen para evitar referencias
            page_image = image_to_add.copy()
            
            # Añadir página con nombre
            page_data = {
                'name': name,
                'image': page_image,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            self.scanned_pages.append(page_data)
            self.update_pages_list()
            
            self.status_var.set(f"Página '{name}' añadida")
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Añadir", command=add_with_name, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Permitir añadir con Enter
        name_entry.bind('<Return>', lambda e: add_with_name())
        dialog.bind('<Escape>', lambda e: cancel())
        
    def update_pages_list(self):
        """Actualizar la lista de páginas en la interfaz"""
        self.pages_listbox.delete(0, tk.END)
        for i, page_data in enumerate(self.scanned_pages):
            display_text = f"{i+1}. {page_data['name']} ({page_data['timestamp']})"
            self.pages_listbox.insert(tk.END, display_text)
        
    def view_page(self):
        """Ver página seleccionada"""
        selection = self.pages_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.scanned_pages):
                page_data = self.scanned_pages[index]
                
                # Establecer como página seleccionada para edición
                self.selected_page_index = index
                self.current_image = page_data['image'].copy()
                self.processed_image = None
                
                # Actualizar información de edición
                self.edit_info_label.config(text=f"Editando: {page_data['name']}")
                
                # Reset de ajustes
                self.reset_adjustments()
                
                # Mostrar imagen
                self.display_image(page_data['image'])
                self.status_var.set(f"Editando: {page_data['name']}")
        else:
            messagebox.showwarning("Advertencia", "Selecciona una página para ver")
                
    def rename_page(self):
        """Renombrar página seleccionada"""
        selection = self.pages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una página para renombrar")
            return
            
        index = selection[0]
        if index >= len(self.scanned_pages):
            return
            
        current_name = self.scanned_pages[index]['name']
        
        # Crear ventana de diálogo
        dialog = tk.Toplevel(self.root)
        dialog.title("Renombrar Página")
        dialog.geometry("350x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Variables
        new_name = tk.StringVar(value=current_name)
        
        # Contenido
        ttk.Label(dialog, text="Nuevo nombre:").pack(pady=10)
        
        entry_frame = ttk.Frame(dialog)
        entry_frame.pack(pady=5, padx=20, fill=tk.X)
        
        name_entry = ttk.Entry(entry_frame, textvariable=new_name, font=("Arial", 10))
        name_entry.pack(fill=tk.X)
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        # Botones
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def rename():
            name = new_name.get().strip()
            if name:
                self.scanned_pages[index]['name'] = name
                self.update_pages_list()
                self.status_var.set(f"Página renombrada a '{name}'")
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Renombrar", command=rename, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Eventos
        name_entry.bind('<Return>', lambda e: rename())
        dialog.bind('<Escape>', lambda e: cancel())
                
    def delete_page(self):
        """Eliminar página seleccionada"""
        selection = self.pages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una página para eliminar")
            return
            
        index = selection[0]
        if index >= len(self.scanned_pages):
            return
            
        page_name = self.scanned_pages[index]['name']
        
        # Confirmar eliminación
        result = messagebox.askyesno("Confirmar", f"¿Eliminar la página '{page_name}'?")
        if result:
            self.scanned_pages.pop(index)
            self.update_pages_list()
            self.status_var.set(f"Página '{page_name}' eliminada")
            
    def move_page_up(self):
        """Mover página hacia arriba en la lista"""
        selection = self.pages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una página para mover")
            return
            
        index = selection[0]
        if index > 0 and index < len(self.scanned_pages):
            # Intercambiar páginas
            self.scanned_pages[index], self.scanned_pages[index-1] = \
                self.scanned_pages[index-1], self.scanned_pages[index]
            
            self.update_pages_list()
            self.pages_listbox.selection_set(index-1)
            self.status_var.set("Página movida hacia arriba")
            
    def move_page_down(self):
        """Mover página hacia abajo en la lista"""
        selection = self.pages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una página para mover")
            return
            
        index = selection[0]
        if index < len(self.scanned_pages) - 1:
            # Intercambiar páginas
            self.scanned_pages[index], self.scanned_pages[index+1] = \
                self.scanned_pages[index+1], self.scanned_pages[index]
            
            self.update_pages_list()
            self.pages_listbox.selection_set(index+1)
            self.status_var.set("Página movida hacia abajo")
            
    def duplicate_page(self):
        """Duplicar página seleccionada"""
        selection = self.pages_listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una página para duplicar")
            return
            
        index = selection[0]
        if index < len(self.scanned_pages):
            original_page = self.scanned_pages[index]
            
            # Crear copia
            duplicate_page = {
                'name': f"{original_page['name']} (Copia)",
                'image': original_page['image'].copy(),
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            self.scanned_pages.insert(index + 1, duplicate_page)
            self.update_pages_list()
            self.status_var.set(f"Página '{original_page['name']}' duplicada")
                
    def clear_pages(self):
        """Limpiar todas las páginas"""
        if self.scanned_pages:
            result = messagebox.askyesno("Confirmar", "¿Eliminar todas las páginas?")
            if result:
                self.scanned_pages.clear()
                self.pages_listbox.delete(0, tk.END)
                self.page_counter = 0
                self.status_var.set("Todas las páginas eliminadas")
                
    def update_selected_page(self):
        """Actualizar página seleccionada con cambios realizados"""
        if self.selected_page_index is None or self.selected_page_index >= len(self.scanned_pages):
            messagebox.showwarning("Advertencia", "No hay página seleccionada para actualizar")
            return
            
        if self.processed_image is None:
            messagebox.showinfo("Información", "No hay cambios para aplicar")
            return
            
        page_name = self.scanned_pages[self.selected_page_index]['name']
        
        # Confirmar actualización
        result = messagebox.askyesno("Confirmar", 
                                   f"¿Actualizar la página '{page_name}' con los cambios realizados?")
        
        if result:
            # Actualizar la imagen en la página
            self.scanned_pages[self.selected_page_index]['image'] = self.processed_image.copy()
            self.scanned_pages[self.selected_page_index]['timestamp'] = datetime.now().strftime("%H:%M:%S")
            
            # Actualizar lista visual
            self.update_pages_list()
            
            # Resetear estado
            self.processed_image = None
            self.edit_info_label.config(text=f"Editando: {page_name} (Actualizada)")
            
            self.status_var.set(f"Página '{page_name}' actualizada exitosamente")
            
    def new_image_mode(self):
        """Cambiar a modo de imagen nueva (salir del modo edición de página)"""
        self.selected_page_index = None
        self.current_image = None
        self.processed_image = None
        
        # Reset de ajustes
        self.reset_adjustments()
        
        # Actualizar información
        self.edit_info_label.config(text="Modo: Nueva imagen")
        
        # Limpiar vista previa
        self.preview_canvas.delete("all")
        
        # Deseleccionar en lista
        self.pages_listbox.selection_clear(0, tk.END)
        
        self.status_var.set("Modo nueva imagen - Cargar o capturar imagen")
                
    def save_image(self):
        """Guardar imagen actual"""
        image_to_save = self.processed_image if self.processed_image is not None else self.current_image
        
        if image_to_save is None:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("TIFF", "*.tiff"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            cv2.imwrite(file_path, image_to_save)
            self.status_var.set(f"Imagen guardada: {os.path.basename(file_path)}")
            
    def generate_pdf(self):
        """Generar PDF con todas las páginas"""
        if not self.scanned_pages:
            messagebox.showwarning("Advertencia", "No hay páginas para generar PDF")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Guardar PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        
        if file_path:
            try:
                # Extraer solo las imágenes de las páginas
                page_images = [page_data['image'] for page_data in self.scanned_pages]
                self.pdf_generator.create_pdf(page_images, file_path)
                self.status_var.set(f"PDF generado: {os.path.basename(file_path)}")
                messagebox.showinfo("Éxito", "PDF generado exitosamente")
            except Exception as e:
                error_msg = str(e)
                messagebox.showerror("Error", f"Error generando PDF: {error_msg}")
                
    def extract_text(self):
        """Extraer texto usando OCR"""
        image_for_ocr = self.processed_image if self.processed_image is not None else self.current_image
        
        if image_for_ocr is None:
            messagebox.showwarning("Advertencia", "No hay imagen para procesar")
            return
        
        # Verificar si Tesseract está disponible
        if not self._check_tesseract_available():
            self._show_tesseract_install_dialog()
            return
            
        self.status_var.set("Extrayendo texto...")
        
        # Ejecutar OCR en hilo separado
        threading.Thread(target=self._extract_text_thread, args=(image_for_ocr,), daemon=True).start()
        
    def _check_tesseract_available(self):
        """Verificar si Tesseract está disponible"""
        try:
            import pytesseract
            # Intentar una prueba simple
            pytesseract.get_tesseract_version()
            return True
        except:
            return False
            
    def _show_tesseract_install_dialog(self):
        """Mostrar diálogo de instalación de Tesseract"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Tesseract OCR no encontrado")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # Contenido
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icono y título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(title_frame, text="🔍", font=("Arial", 24)).pack(side=tk.LEFT)
        ttk.Label(title_frame, text="Tesseract OCR Requerido", 
                 font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # Mensaje
        message = """Para usar la función de reconocimiento de texto (OCR), necesitas instalar Tesseract OCR.

Tesseract es un motor de OCR gratuito y de código abierto desarrollado por Google.

¿Qué hacer?
1. Descargar e instalar Tesseract OCR
2. Asegurarse de incluir el idioma español
3. Reiniciar la aplicación

¿Quieres abrir la página de descarga?"""
        
        text_widget = tk.Text(main_frame, wrap=tk.WORD, height=8, width=50, 
                             font=("Arial", 10), bg="#f8f8f8", relief=tk.FLAT)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def open_download_page():
            import webbrowser
            webbrowser.open("https://github.com/UB-Mannheim/tesseract/wiki")
            dialog.destroy()
        
        def run_installer():
            import subprocess
            import os
            installer_path = os.path.join(os.path.dirname(__file__), "install_tesseract.py")
            subprocess.Popen([sys.executable, installer_path])
            dialog.destroy()
        
        def close_dialog():
            dialog.destroy()
        
        ttk.Button(button_frame, text="📥 Abrir Página de Descarga", 
                  command=open_download_page).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🔧 Ejecutar Instalador", 
                  command=run_installer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cerrar", 
                  command=close_dialog).pack(side=tk.RIGHT)
        
    def _extract_text_thread(self, image):
        """Extraer texto en hilo separado"""
        try:
            text = self.document_processor.extract_text(image)
            if text.strip():
                self.root.after(0, lambda: self._show_extracted_text(text))
            else:
                self.root.after(0, lambda: messagebox.showinfo("OCR", "No se encontró texto en la imagen"))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error en OCR: {error_msg}"))
        finally:
            self.root.after(0, lambda: self.status_var.set("Listo"))
            
    def _show_extracted_text(self, text):
        """Mostrar texto extraído en ventana nueva"""
        text_window = tk.Toplevel(self.root)
        text_window.title("Texto Extraído")
        text_window.geometry("600x400")
        
        text_widget = tk.Text(text_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_window, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, text)
        
        # Botón para guardar texto
        save_btn = ttk.Button(text_window, text="Guardar Texto", 
                            command=lambda: self._save_text(text))
        save_btn.pack(pady=10)
        
    def _save_text(self, text):
        """Guardar texto extraído"""
        file_path = filedialog.asksaveasfilename(
            title="Guardar texto",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            messagebox.showinfo("Éxito", "Texto guardado exitosamente")
            
    def on_closing(self):
        """Manejar cierre de aplicación"""
        if self.is_camera_active:
            self.camera_handler.stop_camera()
        self.root.destroy()

def main():
    """Función principal"""
    root = tk.Tk()
    app = DocumentScannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
