import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import requests
import socketio
import threading
from plyer import notification
import json

class CalendarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📅 Calendario Organizador")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")
        
        # Variables
        self.servidor_url = "http://localhost:5000"
        self.dispositivo_id = "desktop_001"
        self.sesiones = []
        
        # Socket.io cliente
        self.sio = socketio.Client()
        self.configurar_socket_eventos()
        
        # Interfaz gráfica
        self.crear_interfaz()
        
        # Conectar al servidor
        self.conectar_servidor()
    
    def configurar_socket_eventos(self):
        """Configura los eventos del WebSocket"""
        @self.sio.on('dispositivo_conectado')
        def en_dispositivo_conectado(datos):
            print(f"✅ {datos['mensaje']}")
            self.mostrar_notificacion(
                "Conectado",
                f"Total de dispositivos: {datos['dispositivos_activos']}"
            )
        
        @self.sio.on('nueva_sesion')
        def en_nueva_sesion(datos):
            print(f"📝 Nueva sesión: {datos['titulo']}")
            self.actualizar_calendario()
            self.mostrar_notificacion(
                "Nueva Sesión",
                f"{datos['titulo']} - {datos['dispositivo'].upper()}"
            )
        
        @self.sio.on('sesion_actualizada')
        def en_sesion_actualizada(datos):
            print(f"✏️ Sesión actualizada: {datos['titulo']}")
            self.actualizar_calendario()
            self.mostrar_notificacion(
                "Sesión Actualizada",
                datos['titulo']
            )
        
        @self.sio.on('sesion_eliminada')
        def en_sesion_eliminada(datos):
            print(f"🗑️ Sesión eliminada: {datos['id']}")
            self.actualizar_calendario()
            self.mostrar_notificacion(
                "Sesión Eliminada",
                f"ID: {datos['id']}"
            )
        
        @self.sio.on('notificacion_recibida')
        def en_notificacion_recibida(datos):
            self.mostrar_notificacion(
                datos['titulo'],
                datos['mensaje']
            )
    
    def conectar_servidor(self):
        """Conecta al servidor en un thread separado"""
        def conectar():
            try:
                self.sio.connect(self.servidor_url)
                self.sio.emit('conectar_dispositivo', {
                    'dispositivo_id': self.dispositivo_id,
                    'tipo': 'desktop'
                })
                self.cargar_sesiones()
            except Exception as e:
                print(f"❌ Error al conectar: {e}")
                self.mostrar_notificacion("Error", f"No se pudo conectar: {e}")
        
        thread = threading.Thread(target=conectar, daemon=True)
        thread.start()
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica"""
        # Frame superior con botones
        frame_superior = ttk.Frame(self.root)
        frame_superior.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            frame_superior,
            text="➕ Agregar Sesión",
            command=self.agregar_sesion
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_superior,
            text="🔄 Actualizar",
            command=self.actualizar_calendario
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            frame_superior,
            text="📢 Enviar Notificación",
            command=self.abrir_formulario_notificacion
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame principal con Treeview
        frame_principal = ttk.Frame(self.root)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_principal)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview para mostrar sesiones
        self.tree = ttk.Treeview(
            frame_principal,
            columns=("Título", "Inicio", "Fin", "Dispositivo"),
            height=15,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading("#0", text="ID")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Inicio", text="Fecha Inicio")
        self.tree.heading("Fin", text="Fecha Fin")
        self.tree.heading("Dispositivo", text="Dispositivo")
        
        self.tree.column("#0", width=30)
        self.tree.column("Título", width=200)
        self.tree.column("Inicio", width=150)
        self.tree.column("Fin", width=150)
        self.tree.column("Dispositivo", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind para doble clic (editar/eliminar)
        self.tree.bind("<Double-1>", self.en_doble_clic)
    
    def cargar_sesiones(self):
        """Carga las sesiones del servidor"""
        try:
            response = requests.get(f"{self.servidor_url}/api/sesiones")
            if response.status_code == 200:
                self.sesiones = response.json()
                self.actualizar_calendario()
        except Exception as e:
            print(f"❌ Error al cargar sesiones: {e}")
    
    def actualizar_calendario(self):
        """Actualiza la visualización del calendario"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar sesiones
        self.cargar_sesiones()
        
        # Agregar sesiones a la tabla
        for sesion in sorted(
            self.sesiones,
            key=lambda x: x['fecha_inicio']
        ):
            inicio = datetime.fromisoformat(sesion['fecha_inicio'])
            fin = datetime.fromisoformat(sesion['fecha_fin'])
            
            self.tree.insert("", tk.END, text=str(sesion['id']), values=(
                sesion['titulo'],
                inicio.strftime("%d/%m/%Y %H:%M"),
                fin.strftime("%d/%m/%Y %H:%M"),
                sesion['dispositivo']
            ))
    
    def agregar_sesion(self):
        """Abre ventana para agregar una nueva sesión"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar Sesión")
        ventana.geometry("400x300")
        ventana.grab_set()
        
        # Campos
        ttk.Label(ventana, text="Título:").pack(pady=5)
        titulo_entry = ttk.Entry(ventana, width=40)
        titulo_entry.pack()
        
        ttk.Label(ventana, text="Descripción:").pack(pady=5)
        descripcion_entry = ttk.Entry(ventana, width=40)
        descripcion_entry.pack()
        
        ttk.Label(ventana, text="Fecha/Hora inicio (YYYY-MM-DD HH:MM):").pack(pady=5)
        inicio_entry = ttk.Entry(ventana, width=40)
        inicio_entry.pack()
        
        ttk.Label(ventana, text="Fecha/Hora fin (YYYY-MM-DD HH:MM):").pack(pady=5)
        fin_entry = ttk.Entry(ventana, width=40)
        fin_entry.pack()
        
        def guardar():
            try:
                datos = {
                    'titulo': titulo_entry.get(),
                    'descripcion': descripcion_entry.get(),
                    'fecha_inicio': datetime.strptime(
                        inicio_entry.get(),
                        "%Y-%m-%d %H:%M"
                    ).isoformat(),
                    'fecha_fin': datetime.strptime(
                        fin_entry.get(),
                        "%Y-%m-%d %H:%M"
                    ).isoformat(),
                    'dispositivo': 'desktop'
                }
                
                response = requests.post(
                    f"{self.servidor_url}/api/sesiones",
                    json=datos
                )
                
                if response.status_code == 201:
                    messagebox.showinfo("Éxito", "Sesión creada")
                    ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo crear la sesión")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto")
        
        ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    
    def en_doble_clic(self, event):
        """Maneja el doble clic en una sesión"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = seleccion[0]
        sesion_id = self.tree.item(item)['text']
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(
            label="✏️ Editar",
            command=lambda: self.editar_sesion(int(sesion_id))
        )
        menu.add_command(
            label="🗑️ Eliminar",
            command=lambda: self.eliminar_sesion(int(sesion_id))
        )
        menu.post(event.x_root, event.y_root)
    
    def editar_sesion(self, sesion_id):
        """Abre ventana para editar una sesión"""
        sesion = next((s for s in self.sesiones if s['id'] == sesion_id), None)
        if not sesion:
            return
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Editar Sesión")
        ventana.geometry("400x300")
        ventana.grab_set()
        
        ttk.Label(ventana, text="Título:").pack(pady=5)
        titulo_entry = ttk.Entry(ventana, width=40)
        titulo_entry.insert(0, sesion['titulo'])
        titulo_entry.pack()
        
        ttk.Label(ventana, text="Descripción:").pack(pady=5)
        descripcion_entry = ttk.Entry(ventana, width=40)
        descripcion_entry.insert(0, sesion['descripcion'])
        descripcion_entry.pack()
        
        inicio_dt = datetime.fromisoformat(sesion['fecha_inicio'])
        ttk.Label(ventana, text="Fecha/Hora inicio:").pack(pady=5)
        inicio_entry = ttk.Entry(ventana, width=40)
        inicio_entry.insert(0, inicio_dt.strftime("%Y-%m-%d %H:%M"))
        inicio_entry.pack()
        
        fin_dt = datetime.fromisoformat(sesion['fecha_fin'])
        ttk.Label(ventana, text="Fecha/Hora fin:").pack(pady=5)
        fin_entry = ttk.Entry(ventana, width=40)
        fin_entry.insert(0, fin_dt.strftime("%Y-%m-%d %H:%M"))
        fin_entry.pack()
        
        def guardar():
            try:
                datos = {
                    'titulo': titulo_entry.get(),
                    'descripcion': descripcion_entry.get(),
                    'fecha_inicio': datetime.strptime(
                        inicio_entry.get(),
                        "%Y-%m-%d %H:%M"
                    ).isoformat(),
                    'fecha_fin': datetime.strptime(
                        fin_entry.get(),
                        "%Y-%m-%d %H:%M"
                    ).isoformat()
                }
                
                response = requests.put(
                    f"{self.servidor_url}/api/sesiones/{sesion_id}",
                    json=datos
                )
                
                if response.status_code == 200:
                    messagebox.showinfo("Éxito", "Sesión actualizada")
                    ventana.destroy()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha incorrecto")
        
        ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=10)
    
    def eliminar_sesion(self, sesion_id):
        """Elimina una sesión"""
        if messagebox.askyesno("Confirmar", "¿Deseas eliminar esta sesión?"):
            try:
                response = requests.delete(
                    f"{self.servidor_url}/api/sesiones/{sesion_id}"
                )
                if response.status_code == 200:
                    messagebox.showinfo("Éxito", "Sesión eliminada")
                    self.actualizar_calendario()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {e}")
    
    def abrir_formulario_notificacion(self):
        """Abre formulario para enviar notificaciones"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Enviar Notificación")
        ventana.geometry("400x250")
        ventana.grab_set()
        
        ttk.Label(ventana, text="Título:").pack(pady=5)
        titulo_entry = ttk.Entry(ventana, width=40)
        titulo_entry.pack()
        
        ttk.Label(ventana, text="Mensaje:").pack(pady=5)
        mensaje_entry = ttk.Entry(ventana, width=40)
        mensaje_entry.pack()
        
        ttk.Label(ventana, text="Tipo:").pack(pady=5)
        tipo_var = tk.StringVar(value="info")
        ttk.Combobox(
            ventana,
            textvariable=tipo_var,
            values=["info", "alerta", "recordatorio"],
            state="readonly"
        ).pack()
        
        def enviar():
            if self.sio.connected:
                self.sio.emit('enviar_notificacion', {
                    'titulo': titulo_entry.get(),
                    'mensaje': mensaje_entry.get(),
                    'tipo': tipo_var.get()
                })
                messagebox.showinfo("Éxito", "Notificación enviada")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No estás conectado al servidor")
        
        ttk.Button(ventana, text="Enviar", command=enviar).pack(pady=10)
    
    def mostrar_notificacion(self, titulo, mensaje):
        """Muestra notificación del sistema"""
        try:
            notification.notify(
                title=titulo,
                message=mensaje,
                timeout=5
            )
        except Exception as e:
            print(f"Error al mostrar notificación: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarioApp(root)
    root.mainloop()
