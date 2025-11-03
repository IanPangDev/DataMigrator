import customtkinter as ctk
from tkinter import filedialog

class Vista(ctk.CTk):
    def __init__(self, controlador):
        super().__init__()
        self.controlador = controlador
        self.title("Migración mutimotor")
        self.resizable(False, False)
        self.after(1, self.wm_state, 'zoomed')

        # Configuración de columnas y filas
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Barra lateral
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar.grid(row=0, column=0, pady=20, sticky="nswe")

        self.titulo_sidebar = ctk.CTkLabel(
            self.sidebar,
            text='TIPOS DE MIGRACIÓN',
            justify='center',
            font=('Segoe UI', 14, 'bold')
        )
        self.titulo_sidebar.pack(pady=10, padx=10)

        self.slqServer_sqlServer = ctk.CTkButton(
            self.sidebar,
            text="SQL Server a SQL Server",
            command=lambda: self.controlador.cambiar_vista("sql_serverxsql_server")
        )
        self.slqServer_sqlServer.pack(pady=10, padx=15, fill='x')

        self.hadoop_sqlServer = ctk.CTkButton(
            self.sidebar,
            text="Hadoop a SQL Server",
            command=lambda: self.controlador.cambiar_vista("hadoopxsql_server")
        )
        self.hadoop_sqlServer.pack(pady=10, padx=15, fill='x')

        self.oracle_sqlServer = ctk.CTkButton(
            self.sidebar,
            text="Oracle a SQL Server",
            command=lambda: self.controlador.cambiar_vista("oraclexsql_server")
        )
        self.oracle_sqlServer.pack(pady=10, padx=15, fill='x')

        # Área de contenido
        self.contenedor_contenido = ctk.CTkFrame(self)
        self.contenedor_contenido.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Configurar 4 columnas y 8 filas en el grid del contenedor
        for i in range(8):
            self.contenedor_contenido.rowconfigure(i, weight=1)
        for j in range(4):
            self.contenedor_contenido.columnconfigure(j, weight=1)

        self.label_contenido = ctk.CTkLabel(
            self.contenedor_contenido,
            text="BIENVENIDO A LA APP DE MIGRACIÓN MULTIMOTOR",
            font=('Segoe UI', 30, 'bold'),
            justify="center"
        )
        self.label_contenido.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

    def mostrar_sql_server_to_sql_server(self):
        self.color = "#23518C"
        self.label_contenido.configure(text='Migración de SQL Server a SQL Server', 
                                    font=('Segoe UI', 16, 'bold'),
                                    bg_color=self.color)
        self.__plantilla_form()
        # Etiqueta y campo para dns origen
        label_dns_orig = self.__label_form("DNS:", 12)
        label_dns_orig.grid(row=5, column=0, padx=10, pady=10, sticky='e')
        self.dns_orig = self.__textbox_form('localhost:1433')
        self.dns_orig.grid(row=5, column=1, padx=10, pady=10)
        # Etiqueta y campo para dns destino
        label_dns_dst = self.__label_form('DNS:', 12)
        label_dns_dst.grid(row=5, column=2, padx=10, pady=10, sticky='e')
        self.dns_dst = self.__textbox_form('localhost:1433')
        self.dns_dst.grid(row=5, column=3, padx=10, pady=10)
        # Etiqueta y campo para tabla destino
        label_table_dst = self.__label_form('Tabla:', 12)
        label_table_dst.grid(row=6, column=2, padx=10, pady=10, sticky='e')
        self.table_dst = self.__textbox_form('Test')
        self.table_dst.grid(row=6, column=3, padx=10, pady=10)
        # Etiqueta para mostrar el nombre del archivo
        self.label_archivo = ctk.CTkLabel(
            self.contenedor_contenido,
            text="Ningún archivo seleccionado"
        )
        self.label_archivo.grid(row=6, column=0, padx=10, pady=10, sticky='e')
        # Botón para seleccionar archivo .sql
        self.query = None
        self.boton_archivo = ctk.CTkButton(
            self.contenedor_contenido,
            text="Seleccionar archivo .sql",
            command=self.pedir_archivo,
            height=30,
            width=300
        )
        self.boton_archivo.grid(row=6, column=1, padx=10, pady=10)
        # Boton verificador de conexion
        self.boton_verificador = self.__button_form_conexion('sql_serverxsql_server')
        self.boton_verificador.grid(row=7, column=0, columnspan=2, padx=40, pady=40, sticky='nsew')
        # Boton migrador
        self.boton_migrador = ctk.CTkButton(
            self.contenedor_contenido,
            bg_color=self.color,
            text="Migrar",
            command=lambda: self.__button_migrador()
        )
        self.boton_migrador.grid(row=7, column=2, columnspan=2, padx=40, pady=40, sticky='nsew')

    def mostrar_hadoop_to_sql_server(self):
        self.color = "#E07E29"
        self.label_contenido.configure(text='Migracion de Hadoop a SQL Server',
                                    font=('Segoe UI', 16, 'bold'),
                                    bg_color=self.color)
        self.__plantilla_form()

    def mostrar_oracle_to_sql_server(self):
        self.color = "#203359"
        self.label_contenido.configure(text='Migracion de Oracle a SQL Server',
                                    font=('Segoe UI', 16, 'bold'),
                                    bg_color=self.color)
        self.__plantilla_form()
    
    def pedir_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo .sql",
            filetypes=[("Archivos SQL", "*.sql"), ("Todos los archivos", "*.*")]
        )

        if ruta:
            self.label_archivo.configure(text=f"Archivo seleccionado:\n{ruta}")

            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                self.query = f.read()
    
    def __button_migrador(self):
        salida = self.controlador.migrar(self.query, self.table_dst.get("1.0", "end-1c").strip())
        match salida.get('key'):
            case 1:
                self.mostrar_aviso(f'Conexion fallida en origen\n\n{salida['error']}', 1)
            case 2:
                self.mostrar_aviso(f'Conexion fallida en destino\n\n{salida['error']}', 1)
            case 3:
                self.mostrar_aviso(f'Migración fallida\n\n{salida['error']}', 1)
            case _:
                self.mostrar_aviso('Migración exitosa', 0)
    
    def __button_form_conexion(self, clave):
        return ctk.CTkButton(
            self.contenedor_contenido,
            text="Verifica conexion de ambos",
            command=lambda: self.__full_credentials(clave)
        )
    
    def __full_credentials(self, clave: str):
        datos_form = {
            self.usr_orig: 'Usuario origen', 
            self.pwd_orig: 'Contraseña origen',
            self.db_orig: 'Base de datos origen',
            self.dns_orig: 'DNS origen',
            self.usr_dst: 'Usuario destino',
            self.pwd_dst: 'Contraseña destino',
            self.db_dst: 'Base de datos destino',
            self.dns_dst: 'DNS destino',
            self.table_dst: 'Tabla destino'
        }
        errores = [text for v, text in datos_form.items() if v.get("1.0", "end-1c").strip() == '']
        if not self.query:
            errores.append('Query')
        if errores:
            self.mostrar_aviso("Campos vacíos: " + ", ".join(errores), 1)
            return
        self.controlador.define_motores(clave)
        datos_form = {
            'usr_orig': self.usr_orig, 
            'pwd_orig': self.pwd_orig,
            'db_orig': self.db_orig,
            'dns_orig': self.dns_orig,
            'usr_dst': self.usr_dst,
            'pwd_dst': self.pwd_dst,
            'db_dst': self.db_dst,
            'dns_dst': self.dns_dst
        }
        # Extraer los valores y asignar el nombre real de la variable
        valores = {
            nombre: (
                campo.get("1.0", "end-1c").strip().replace(':', ',')
                if 'dns' in nombre
                else campo.get("1.0", "end-1c").strip()
            )
            for nombre, campo in datos_form.items()
        }

        # Llamar a verifica_conexion con los nombres reales como parámetros
        salida = self.controlador.verifica_conexion(**valores)
        match salida.get('key'):
            case 1:
                self.mostrar_aviso(f'Conexion fallida en origen\n\n{salida['error']}', 1)
            case 2:
                self.mostrar_aviso(f'Conexion fallida en destino\n\n{salida['error']}', 1)
            case _:
                self.mostrar_aviso('Conexion exitosa', 0)

    def mostrar_aviso(self, mensaje: str, type: int):
        popup = ctk.CTkToplevel(self)
        color = None
        match type:
            case 1:
                popup.title("Error")
                color = "#831616"
            case 2:
                popup.title("Aviso")
                color = "#d0cc0d"
            case _:
                popup.title("Exito")
                color = "#26af00"
                
        popup.resizable(False, False)
        popup.update_idletasks()
        
        max_width = 500  # ancho máximo permitido
        base_width = 300
        base_height = 400
        
        # Crear label temporal para medir texto
        temp_label = ctk.CTkLabel(popup, text=f"{mensaje}", wraplength=max_width - 60)
        temp_label.update_idletasks()
        text_width = min(max(temp_label.winfo_reqwidth() + 60, base_width), max_width)
        text_height = max(temp_label.winfo_reqheight() + 100, base_height)
        temp_label.destroy()

        # Centrar popup en pantalla
        pantalla_ancho = popup.winfo_screenwidth()
        pantalla_alto = popup.winfo_screenheight()
        x = (pantalla_ancho // 2) - (text_width // 2)
        y = (pantalla_alto // 2) - (text_height // 2)
        popup.geometry(f"{text_width}x{text_height}+{x}+{y}")

        popup.grab_set()  # bloquea la ventana principal

        # --- Fondo de error ---
        frame = ctk.CTkFrame(popup, fg_color=color, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Etiqueta de mensaje ---
        label = ctk.CTkLabel(
            frame,
            text=f"{mensaje}",
            text_color="white",
            wraplength=text_width - 40,  # para que el texto se ajuste automáticamente
            justify="center",
            font=('Segoe UI', 13, 'bold')
        )
        label.pack(pady=15, padx=10, expand=True)

        # --- Botón de cierre ---
        boton_ok = ctk.CTkButton(
            frame,
            text="Aceptar",
            fg_color="white",
            text_color="black",
            command=popup.destroy,
            width=100,
        )
        boton_ok.pack(pady=(5, 15))

    def __label_form(self, text: str, size: int) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            self.contenedor_contenido,
            text=text,
            justify="center",
            font=('Segoe UI', size, 'bold')
        )
    
    def __textbox_form(self, text: str = '') -> ctk.CTkTextbox:
        textbox = ctk.CTkTextbox(
            self.contenedor_contenido,
            width=300,
            height=30
        )
        textbox.insert("1.0", text)
        return textbox

    def __plantilla_form(self):
        # Label de origen
        self.label_datos_orig = self.__label_form("Datos origen", 14)
        self.label_datos_orig.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Etiqueta y campo para Usuario origen
        label_usr_orig = self.__label_form('Usuario:', 12)
        label_usr_orig.grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.usr_orig = self.__textbox_form('sa')
        self.usr_orig.grid(row=2, column=1, padx=10, pady=10)

        # Etiqueta y campo para Contraseña origen
        label_pwd_orig = self.__label_form('Contraseña:', 12)
        label_pwd_orig.grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.pwd_orig = self.__textbox_form()
        self.pwd_orig.grid(row=3, column=1, padx=10, pady=10)

        # Etiqueta y campo para Base de Datos de Origen
        label_bd_orig = self.__label_form('Base de Datos:',12)
        label_bd_orig.grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.db_orig = self.__textbox_form('master')
        self.db_orig.grid(row=4, column=1, padx=10, pady=10)
    
                # Label de destino
        self.label_datos_dst = self.__label_form("Datos destino", 14)
        self.label_datos_dst.grid(row=1, column=3, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Etiqueta y campo para Usuario destino
        label_usr_dst = self.__label_form("Usuario:", 12)
        label_usr_dst.grid(row=2, column=2, padx=10, pady=10, sticky='e')
        self.usr_dst = self.__textbox_form('sa')
        self.usr_dst.grid(row=2, column=3, padx=10, pady=10)

        # Etiqueta y campo para Contraseña destino
        label_pwd_dst = self.__label_form('Contraseña:', 12)
        label_pwd_dst.grid(row=3, column=2, padx=10, pady=10, sticky='e')
        self.pwd_dst = self.__textbox_form()
        self.pwd_dst.grid(row=3, column=3, padx=10, pady=10)

        # Etiqueta y campo para Base de Datos de destino
        label_bd_dst = self.__label_form('Base de Datos:', 12)
        label_bd_dst.grid(row=4, column=2, padx=10, pady=10, sticky='e')
        self.db_dst = self.__textbox_form('master')
        self.db_dst.grid(row=4, column=3, padx=10, pady=10)