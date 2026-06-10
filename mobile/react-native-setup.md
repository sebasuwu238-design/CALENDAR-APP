# 📱 React Native - App Móvil

Aplicación móvil para CALENDAR-APP usando React Native y Expo.

## 🚀 Instalación

```bash
# Crear proyecto
npx create-expo-app CalendarioApp
cd CalendarioApp

# Instalar dependencias
npm install socket.io-client axios
npm install react-native-local-notification
npm install react-native-datepicker
```

## 📝 Estructura básica

```javascript
// App.js
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert } from 'react-native';
import { io } from 'socket.io-client';
import axios from 'axios';

const API_URL = 'http://<TU_IP>:5000'; // Reemplaza con tu IP

export default function App() {
  const [sesiones, setSesiones] = useState([]);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Conectar al servidor
    const newSocket = io(API_URL, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
    });

    newSocket.on('connect', () => {
      console.log('✅ Conectado al servidor');
      newSocket.emit('conectar_dispositivo', {
        dispositivo_id: 'movil_001',
        tipo: 'movil'
      });
    });

    newSocket.on('nueva_sesion', () => {
      cargarSesiones();
    });

    setSocket(newSocket);
    cargarSesiones();

    return () => newSocket.close();
  }, []);

  const cargarSesiones = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/sesiones`);
      setSesiones(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const agregarSesion = async () => {
    // Aquí iría la lógica para agregar sesión
    Alert.alert('Nueva Sesión', 'Implementar formulario');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>📅 Calendario</Text>
      
      <TouchableOpacity 
        style={styles.boton}
        onPress={agregarSesion}
      >
        <Text style={styles.botonTexto}>➕ Agregar Sesión</Text>
      </TouchableOpacity>

      <FlatList
        data={sesiones}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.sesion}>
            <Text style={styles.sesionTitulo}>{item.titulo}</Text>
            <Text style={styles.sesionFecha}>
              {new Date(item.fecha_inicio).toLocaleDateString('es-ES')}
            </Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    paddingTop: 50,
  },
  titulo: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  boton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    marginHorizontal: 20,
    marginBottom: 20,
  },
  botonTexto: {
    color: 'white',
    textAlign: 'center',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sesion: {
    backgroundColor: 'white',
    padding: 15,
    marginHorizontal: 20,
    marginVertical: 5,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  sesionTitulo: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  sesionFecha: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
  },
});
```

## 📦 Ejecutar en tu dispositivo

```bash
# iOS
npm run ios

# Android
npm run android

# En navegador
npm run web
```

## 🔌 Configurar IP del servidor

Reemplaza `<TU_IP>` con la dirección IP de tu laptop:

**Windows:**
```cmd
ipconfig
```

**macOS/Linux:**
```bash
ifconfig | grep inet
```

Busca la IP que comienza con `192.168.` o `10.0.`

---

¡Listo para desarrollo móvil!
