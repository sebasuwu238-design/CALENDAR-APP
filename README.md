# 📅 CALENDAR-APP

Aplicación de calendario para organizar tu tiempo con sincronización en tiempo real entre dispositivos móviles y de escritorio.

## 🎯 Características

✅ **Backend en Python (Flask)**
- API REST para gestionar sesiones/eventos
- WebSocket para sincronización en tiempo real
- Base de datos SQLite (fácil de escalar a PostgreSQL)
- Notificaciones automáticas

✅ **Aplicación Desktop (Tkinter)**
- Interfaz gráfica intuitiva
- Ver, agregar, editar y eliminar sesiones
- Notificaciones del sistema
- Sincronización en tiempo real

✅ **Conectividad**
- Comunicación por WiFi
- Múltiples dispositivos simultáneos
- Sincronización automática

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/sebasuwu238-design/CALENDAR-APP.git
cd CALENDAR-APP
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 📋 Uso

### Iniciar el servidor backend
```bash
cd backend
python app.py
```

El servidor estará disponible en `http://localhost:5000`

### Iniciar la aplicación desktop
```bash
cd desktop
python desktop_app.py
```

## 📁 Estructura del Proyecto

```
CALENDAR-APP/
├── backend/
│   └── app.py              # Servidor Flask + WebSocket
├── desktop/
│   └── desktop_app.py      # App Desktop Tkinter
├── requirements.txt        # Dependencias Python
├── .env                    # Variables de entorno
└── README.md              # Este archivo
```

---

**GitHub:** [@sebasuwu238-design](https://github.com/sebasuwu238-design)
