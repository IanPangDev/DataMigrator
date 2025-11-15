
---

# 🧩 DataMigrator Desktop (Python)

DataMigrator es una aplicación de escritorio desarrollada en Python que permite migrar datos entre diferentes motores de base de datos:

* Oracle → SQL Server

* SQL Server ↔ SQL Server

* Hive → SQL Server

La aplicación implementa el patrón Factory para la creación dinámica de conectores y el patrón MVC para estructurar la lógica de negocio, control y vista de la interfaz gráfica (GUI).

---

## 🚀 Características

* 🔄 Migración entre diferentes motores (Oracle, SQL Server, Hive).

* 🏗️ Arquitectura basada en patrones de diseño:

    * Factory Pattern para la creación de conectores de base de datos.

    * MVC Pattern para separar la lógica de negocio, control y presentación.

* 🖥️ Interfaz gráfica en CustomTkinter:

    * Configuración visual de orígenes y destinos.

    * Vista para logs.

* 🧩 Extensible: fácilmente ampliable a nuevos motores de base de datos.

---

## ⚙️ Requisitos

Para ejecutar correctamente DataMigrator, asegúrate de tener instalados los siguientes componentes:

* Python 3.13.5+

* Java 8 o superior (requerido para conectores basados en JDBC, como Oracle o Hive)

* Driver de conexión para Oracle (instantclient_23_9)

* Librerías listadas en requirements.txt

Variable de entorno JAVA_HOME correctamente configurada, apuntando al directorio de instalación de Java

---

## 🧱 Estructura del proyecto

```
DataMigrator/
│
├── app/                    # Carpeta de la app
│   ├── controlador.py
│   ├── vista.py
│   └── factory/            # Modelos para las migraciones
│        ├── ....py          
│        └── drivers/       # Carpeta de drivers (Oracle y Hive)
│
├── script/                 # Carpeta con scripts sql de prueba
├── containers/             # Carpeta con los contenedores para pruebas
│    ├── hive 
│    └── sql_server 
│
├── requirements.txt        # Librerias a usar
├── init.bat                # Script para iniciar contenedores
├── README.md               
└── main.py                 # Ejecutable principal
```