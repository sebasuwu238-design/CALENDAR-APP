# 🎯 Flutter - App Móvil Alternativa

Alternativa más rápida y performante usando Flutter.

## 🚀 Instalación

```bash
# Crear proyecto
flutter create calendario_app
cd calendario_app

# Agregar dependencias
flutter pub add socket_io_client
flutter pub add http
flutter pub add flutter_local_notifications
flutter pub add intl
```

## 📝 Estructura básica

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Calendario',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const CalendarioPage(),
    );
  }
}

class CalendarioPage extends StatefulWidget {
  const CalendarioPage({Key? key}) : super(key: key);

  @override
  State<CalendarioPage> createState() => _CalendarioPageState();
}

class _CalendarioPageState extends State<CalendarioPage> {
  late IO.Socket socket;
  List<dynamic> sesiones = [];
  final String apiUrl = 'http://<TU_IP>:5000';

  @override
  void initState() {
    super.initState();
    conectarServidor();
    cargarSesiones();
  }

  void conectarServidor() {
    socket = IO.io(apiUrl, IO.OptionBuilder()
        .setTransports(['websocket'])
        .disableAutoConnect()
        .build());

    socket.connect();

    socket.on('connect', (_) {
      print('✅ Conectado al servidor');
      socket.emit('conectar_dispositivo', {
        'dispositivo_id': 'flutter_001',
        'tipo': 'movil'
      });
    });

    socket.on('nueva_sesion', (_) {
      cargarSesiones();
    });

    socket.on('disconnect', (_) {
      print('❌ Desconectado del servidor');
    });
  }

  void cargarSesiones() async {
    try {
      final response = await http.get(
        Uri.parse('$apiUrl/api/sesiones'),
      );

      if (response.statusCode == 200) {
        setState(() {
          sesiones = jsonDecode(response.body);
        });
      }
    } catch (e) {
      print('Error al cargar sesiones: $e');
    }
  }

  void agregarSesion() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Nueva Sesión'),
        content: const Text('Implementar formulario'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cerrar'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    socket.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📅 Calendario'),
        elevation: 0,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: ElevatedButton.icon(
              onPressed: agregarSesion,
              icon: const Icon(Icons.add),
              label: const Text('Agregar Sesión'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 12,
                ),
              ),
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: sesiones.length,
              itemBuilder: (context, index) {
                final sesion = sesiones[index];
                return Card(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  child: ListTile(
                    title: Text(sesion['titulo']),
                    subtitle: Text(
                      DateTime.parse(sesion['fecha_inicio'])
                          .toString()
                          .split(' ')[0],
                    ),
                    leading: const Icon(Icons.event),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
```

## 📱 Ejecutar

```bash
# iOS
flutter run -d ios

# Android
flutter run -d android

# Lista de dispositivos disponibles
flutter devices
```

## 🔌 Configurar IP

Reemplaza `<TU_IP>` con tu dirección IP.

---

**Flutter es más rápido y produce apps nativas de mejor rendimiento.**
