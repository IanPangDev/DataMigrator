from app.factory.Migrador import Migrador
import pyodbc
from customtkinter import CTkTextbox
from datetime import datetime
from decimal import Decimal
from app.factory.utilities import create_table

class SQLserver_to_SQLserver(Migrador):

    def __init__(self) -> None:
        """
        Contructor de la clase
        """
        # mapa de credenciales
        self.credenciales = None

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
            'dns_orig': dns_orig,
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

            with pyodbc.connect(
                f"DRIVER={{SQL Server}};"
                f"SERVER={self.credenciales['dns_orig']};"
                f"DATABASE={self.credenciales['db_orig']};"
                f"UID={self.credenciales['usr_orig']};"
                f"PWD={self.credenciales['pwd_orig']}"
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

                if create_tabla:
                    cursor_orig.execute(f"EXEC sp_describe_first_result_set N'{query_select.replace('\'', '\'\'')}'")
                    description = []
                    for i in cursor_orig.fetchall():
                        description.append([i[2], i[5], i[5], None, i[7], i[8], i[3]])
                    cursor_dst.execute(create_table(tabla_dst, description))
                    cursor_dst.commit()
                
                    logs.insert('end', f"[{datetime.now()}] Tabla creada exitosamente\n")  # Añadir texto al final del widget Text.
                    logs.yview('end')
                
                cursor_orig.execute(query_select)
                
                # Obtienes los nombres de las columnas directamente desde la query
                columnas_destino = [f"[{desc[0]}]" for desc in cursor_orig.description]
                
                columnas_str = ",".join(columnas_destino)
                placeholders = ",".join(["?"] * len(columnas_destino))
                insert_query = f"INSERT INTO {tabla_dst} ({columnas_str}) VALUES ({placeholders})"

                while True:
                    rows = cursor_orig.fetchmany(10_000)
                    if not rows:
                        break
                    cursor_dst.executemany(insert_query, rows)
                    dst.commit()
                    logs.insert('end', f"[{datetime.now()}] Chunk de {len(rows):,} insertado\n")  # Añadir texto al final del widget Text.
                    logs.yview('end')# Desplaza la vista del Text hacia el final para mostrar el nuevo texto.

                logs.insert("end", f"[{datetime.now()}] MIGRACIÓN FINALIZADA\n")
                logs.configure(fg_color="#26af00")
                return

        except Exception as e:
            # Captura cualquier error y lo devuelve como parte del diccionario
            logs.insert('end', f'[{datetime.now()}] Migración fallida\n\n{e}\n\n')
            logs.configure(fg_color="#831616")
            return

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
            pyodbc.connect(
                f'DRIVER={{SQL Server}};'
                f'SERVER={self.credenciales['dns_orig']};'
                f'DATABASE={self.credenciales['db_orig']};'
                f'UID={self.credenciales['usr_orig']};'
                f'PWD={self.credenciales['pwd_orig']}',
                timeout=1
            )
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