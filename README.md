
---

# 🧩 DataMigrator Desktop (Python)

DataMigrator es una aplicación de escritorio desarrollada en Python que permite migrar datos entre diferentes motores de base de datos:

* Oracle → SQL Server

* SQL Server ↔ SQL Server

* Hadoop → SQL Server

La aplicación implementa el patrón Factory para la creación dinámica de conectores y el patrón MVC para estructurar la lógica de negocio, control y vista de la interfaz gráfica (GUI).

---

## 🚀 Características

* 🔄 Migración entre diferentes motores (Oracle, SQL Server, Hadoop).

* 🏗️ Arquitectura basada en patrones de diseño:

    * Factory Pattern para la creación de conectores de base de datos.

    * MVC Pattern para separar la lógica de negocio, control y presentación.

* 🖥️ Interfaz gráfica en CustomTkinter:

    * Configuración visual de orígenes y destinos.

    * Vista para logs.

* 🧩 Extensible: fácilmente ampliable a nuevos motores de base de datos.

---

## 🧱 Estructura del proyecto

```
DataMigrator/
│
├── factory             # Carpeta con modelos factory
├── script              # Carpeta con scripts sql de prueba
├── sql_server          # Carpeta con docker compose para BD de prueba
├── controlador.py      # Clase controlador
├── vista.py            # Clase vista
├── requirements.txt    # Librerias a usar
├── README.md           
└── main.py             # Ejecutable principal
```