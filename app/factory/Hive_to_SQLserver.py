from app.factory.Migrador import Migrador
import jaydebeapi
import pyodbc
from customtkinter import CTkTextbox
from datetime import datetime
from app.factory.utilities import create_table
import jpype

class Hive_to_SQLserver(Migrador):

    def __init__(self) -> None:
        """
        Contructor de la clase
        """
        # mapa de credenciales
        self.credenciales = None
        
        self.mapper = {
            # ======================
            # NUMÉRICOS
            # ======================
            "tinyint":   lambda d: "tinyint",
            "smallint":  lambda d: "smallint",
            "int":       lambda d: "int",
            "integer":   lambda d: "int",
            "bigint":    lambda d: "bigint",

            "decimal": lambda d: (
                f"decimal({d['data_precision']},{d['data_scale']})"
                if d['data_precision'] else "decimal"
            ),
            "numeric": lambda d: (
                f"numeric({d['data_precision']},{d['data_scale']})"
                if d['data_precision'] else "numeric"
            ),

            "float":  lambda d: "float",
            "double": lambda d: "float",
            "real":   lambda d: "real",

            # ======================
            # BOOLEANOS
            # ======================
            "boolean": lambda d: "bit",

            # ======================
            # FECHAS
            # ======================
            "date": lambda d: "datetime2",

            "timestamp": lambda d: "datetime2",

            # ======================
            # STRING
            # ======================
            "string": lambda d: "nvarchar(4000)",
            "varchar": lambda d: (
                f"varchar({d['data_length']})"
                if d['data_length'] and d['data_length'] <= 8000
                else "varchar(4000)"
            ),
            "char": lambda d: (
                f"char({d['data_length']})"
                if d['data_length'] else "char(1)"
            )
        }

    def define_credenciales(self,
                            usr_orig: str,
                            pwd_orig: str,
                            dns_orig: str,
                            db_orig: str,
                            usr_dst: str,
                            pwd_dst: str,
                            dns_dst: str,
                            db_dst: str
                            ) -> None:
        """
        Metodo que registra las credenciales
        Args:
            # env_path: path donde esta el .env con las credenciales
        """
        # Creacion de diccionario con credenciales para conexion
        self.credenciales = {
            'usr_orig': usr_orig,
            'pwd_orig': pwd_orig,
            'dns_orig': 'jdbc:hive2://'+dns_orig,
            'db_orig': db_orig,
            'usr_dst': usr_dst,
            'pwd_dst': pwd_dst,
            'dns_dst': dns_dst,
            'db_dst': db_dst
        }

    def migrar(self, query_select: str, tabla_dst: str, logs: CTkTextbox, create_tabla: bool) -> None:
        """
        Realiza la migración por lotes (batch) de 10,000 registros.
        """
        try:
            verifica = self.verifica_conexion()
            if verifica['key'] != 0:
                match verifica.get('key'):
                    case 1:
                        logs.insert('end', f'[{datetime.now()}] Conexion fallida en origen\n\n{verifica['error']}')
                        logs.configure(fg_color="#831616")
                    case 2:
                        logs.insert('end', f'[{datetime.now()}] Conexion fallida en destino\n\n{verifica['error']}')
                        logs.configure(fg_color="#831616")
                    case _:
                        pass
                logs.yview('end')
                return

            with jaydebeapi.connect(
                "org.apache.hive.jdbc.HiveDriver",
                self.credenciales['dns_orig'],
                [
                    self.credenciales['usr_orig'],
                    self.credenciales['pwd_orig']
                ],
                "factory\\drivers\\hive-jdbc-uber-2.6.5.0-292.jar"
            ) as orig, pyodbc.connect(
                f"DRIVER={{SQL Server}};"
                f"SERVER={self.credenciales['dns_dst']};"
                f"DATABASE={self.credenciales['db_dst']};"
                f"UID={self.credenciales['usr_dst']};"
                f"PWD={self.credenciales['pwd_dst']}"
            ) as dst:

                cursor_orig = orig.cursor()
                cursor_dst = dst.cursor()
                cursor_dst.fast_executemany = True

                cursor_orig.execute(query_select)
                
                if create_tabla:
                    # crear tabla
                    # =========================
                    # Obtener metadata JDBC
                    # =========================
                    meta = cursor_orig._rs.getMetaData()
                    num_cols = meta.getColumnCount()

                    jdbc_types = {}
                    for i in range(1, num_cols + 1):  # JDBC empieza en 1
                        col_name = meta.getColumnName(i).lower()
                        jdbc_types[col_name] = meta.getColumnTypeName(i)

                    # =========================
                    # Reemplazar tipos en cursor.description
                    # =========================
                    new_description = []

                    for col in cursor_orig.description:
                        name, type_code, display_size, internal_size, precision, scale, null_ok = col

                        true_type = jdbc_types.get(name.lower(), type_code)

                        new_description.append((
                            name.split('.')[-1],          # nombre columna
                            true_type,     # tipo REAL (JDBC/Hive)
                            display_size,
                            internal_size,
                            precision,
                            scale,
                            null_ok
                        ))

                    cursor_dst.execute(create_table(tabla_dst, new_description, self.mapper))
                    cursor_dst.commit()
                    
                    logs.insert('end', f"[{datetime.now()}] Tabla creada exitosamente\n")  # Añadir texto al final del widget Text.
                    logs.yview('end')
                
                # Obtienes los nombres de las columnas directamente desde la query
                columnas_destino = [desc[0].split('.')[-1] for desc in cursor_orig.description]

                columnas_str = ",".join(columnas_destino)
                placeholders = ",".join(["?"] * len(columnas_destino))
                insert_query = f"INSERT INTO {tabla_dst} ({columnas_str}) VALUES ({placeholders})"
                while True:
                    rows = cursor_orig.fetchmany(10_000)
                    if not rows:
                        break

                    # rows = [[str(i) for i in list(row)] for row in rows]
                    cursor_dst.executemany(insert_query, rows)
                    dst.commit()
                    logs.insert('end', f"[{datetime.now()}] Chunk de {len(rows):,} insertado\n")  # Añadir texto al final del widget Text.
                    logs.yview('end')# Desplaza la vista del Text hacia el final para mostrar el nuevo texto.

                logs.insert("end", f"[{datetime.now()}] MIGRACIÓN FINALIZADA\n")
                logs.configure(fg_color="#26af00")
                

        except Exception as e:
            # Captura cualquier error y lo devuelve como parte del diccionario
            logs.insert('end', f'[{datetime.now()}] Migración fallida\n\n{e}\n\n')
            logs.configure(fg_color="#831616")
            
        finally:
                
            try:
                cursor_orig.close()
            except:
                pass

            try:
                cursor_dst.close()
            except:
                pass

            try:
                orig.close()
            except:
                pass

            try:
                dst.close()
            except:
                pass
        
    def revisa_integridad(self) -> None:
        """
        Metodo que revisa la integridad de los datos migrados
        """
        pass

    def verifica_conexion(self) -> dict:
        """
        Metodo privado para verificar las conexiones a ambas bases de datos
        Devuelve un diccionario con el estado:
            {'key': 0, 'error': None} en caso de éxito
            {'key': 1 o 2, 'error': <mensaje>} en caso de error
        """
        try: 
            conn_orig = jaydebeapi.connect(
                "org.apache.hive.jdbc.HiveDriver",
                self.credenciales['dns_orig'],
                [
                    self.credenciales['usr_orig'],
                    self.credenciales['pwd_orig']
                ],
                "app\\factory\\drivers\\hive-jdbc-uber-2.6.5.0-292.jar"
            )
            conn_orig.close()
        except Exception as e:
            return {
                'key':1,
                'error':e
            }
        
        try: 
            pyodbc.connect(
                f'DRIVER={{SQL Server}};'
                f'SERVER={self.credenciales['dns_dst']};'
                f'DATABASE={self.credenciales['db_dst']};'
                f'UID={self.credenciales['usr_dst']};'
                f'PWD={self.credenciales['pwd_dst']}',
                timeout=1
            )
        except Exception as e:
            return {
                'key':2,
                'error':e
            }
        
        return {
            'key':0,
            'error':None
        }