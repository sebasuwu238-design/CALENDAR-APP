from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///calendario.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Sesión/Evento
class Sesion(Base):
    __tablename__ = "sesiones"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descripcion = Column(String)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    dispositivo = Column(String)  # 'movil', 'desktop'
    creado_en = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Diccionario para rastrear usuarios conectados
usuarios_conectados = {}

# ==================== RUTAS HTTP ====================

@app.route('/api/sesiones', methods=['GET'])
def obtener_sesiones():
    """Obtiene todas las sesiones del calendario"""
    db: Session = SessionLocal()
    sesiones = db.query(Sesion).all()
    db.close()
    
    return jsonify([{
        'id': s.id,
        'titulo': s.titulo,
        'descripcion': s.descripcion,
        'fecha_inicio': s.fecha_inicio.isoformat(),
        'fecha_fin': s.fecha_fin.isoformat(),
        'dispositivo': s.dispositivo
    } for s in sesiones])

@app.route('/api/sesiones', methods=['POST'])
def crear_sesion():
    """Crea una nueva sesión"""
    datos = request.json
    db: Session = SessionLocal()
    
    nueva_sesion = Sesion(
        titulo=datos['titulo'],
        descripcion=datos.get('descripcion', ''),
        fecha_inicio=datetime.fromisoformat(datos['fecha_inicio']),
        fecha_fin=datetime.fromisoformat(datos['fecha_fin']),
        dispositivo=datos.get('dispositivo', 'desconocido')
    )
    
    db.add(nueva_sesion)
    db.commit()
    db.refresh(nueva_sesion)
    db.close()
    
    # Notificar a todos los usuarios conectados
    socketio.emit('nueva_sesion', {
        'id': nueva_sesion.id,
        'titulo': nueva_sesion.titulo,
        'fecha_inicio': nueva_sesion.fecha_inicio.isoformat(),
        'dispositivo': nueva_sesion.dispositivo
    }, broadcast=True)
    
    return jsonify({'id': nueva_sesion.id, 'mensaje': 'Sesión creada'}), 201

@app.route('/api/sesiones/<int:sesion_id>', methods=['PUT'])
def actualizar_sesion(sesion_id):
    """Actualiza una sesión existente"""
    datos = request.json
    db: Session = SessionLocal()
    
    sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
    if not sesion:
        db.close()
        return jsonify({'error': 'Sesión no encontrada'}), 404
    
    sesion.titulo = datos.get('titulo', sesion.titulo)
    sesion.descripcion = datos.get('descripcion', sesion.descripcion)
    sesion.fecha_inicio = datetime.fromisoformat(datos['fecha_inicio'])
    sesion.fecha_fin = datetime.fromisoformat(datos['fecha_fin'])
    
    db.commit()
    db.close()
    
    # Notificar actualización
    socketio.emit('sesion_actualizada', {
        'id': sesion_id,
        'titulo': sesion.titulo,
        'fecha_inicio': sesion.fecha_inicio.isoformat()
    }, broadcast=True)
    
    return jsonify({'mensaje': 'Sesión actualizada'})

@app.route('/api/sesiones/<int:sesion_id>', methods=['DELETE'])
def eliminar_sesion(sesion_id):
    """Elimina una sesión"""
    db: Session = SessionLocal()
    sesion = db.query(Sesion).filter(Sesion.id == sesion_id).first()
    
    if not sesion:
        db.close()
        return jsonify({'error': 'Sesión no encontrada'}), 404
    
    db.delete(sesion)
    db.commit()
    db.close()
    
    # Notificar eliminación
    socketio.emit('sesion_eliminada', {'id': sesion_id}, broadcast=True)
    
    return jsonify({'mensaje': 'Sesión eliminada'})

# ==================== WEBSOCKET ====================

@socketio.on('conectar_dispositivo')
def manejar_conexion(datos):
    """Maneja la conexión de un dispositivo"""
    dispositivo_id = datos['dispositivo_id']
    tipo_dispositivo = datos['tipo']  # 'movil', 'desktop'
    
    usuarios_conectados[dispositivo_id] = {
        'tipo': tipo_dispositivo,
        'conectado_en': datetime.utcnow().isoformat()
    }
    
    print(f"✅ {tipo_dispositivo.upper()} conectado: {dispositivo_id}")
    
    emit('dispositivo_conectado', {
        'mensaje': f'Bienvenido {tipo_dispositivo}',
        'dispositivos_activos': len(usuarios_conectados)
    }, broadcast=True)

@socketio.on('desconectar')
def manejar_desconexion():
    """Maneja la desconexión de un dispositivo"""
    print("❌ Dispositivo desconectado")
    emit('dispositivo_desconectado', {
        'dispositivos_activos': len(usuarios_conectados)
    }, broadcast=True)

@socketio.on('enviar_notificacion')
def enviar_notificacion(datos):
    """Envía notificaciones a todos los dispositivos"""
    notificacion = {
        'titulo': datos['titulo'],
        'mensaje': datos['mensaje'],
        'tipo': datos.get('tipo', 'info'),  # 'info', 'alerta', 'recordatorio'
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Emitir a todos los clientes excepto al emisor
    emit('notificacion_recibida', notificacion, broadcast=True, skip_sid=True)
    print(f"📢 Notificación enviada: {datos['titulo']}")

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def no_encontrado(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def error_interno(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
