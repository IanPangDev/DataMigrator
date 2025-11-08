from app.factory.Migrador import Migrador
import jaydebeapi
import pyodbc

class Hive_to_SQLserver(Migrador):

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
            'dns_orig': 'jdbc:hive2://'+dns_orig,
            'db_orig': db_orig,
            'usr_dst': usr_dst,
            'pwd_dst': pwd_dst,
            'dns_dst': dns_dst,
            'db_dst': db_dst
        }

    def actualiza_conversiones(self, conversiones: dict):
        """
        Metodo que define las conversiones de tipos de dato
        Args:
            # conversiones: diccionario de conversiones
        """
        pass

    def migrar(self, query_select: str, tabla_dst: str) -> dict:
        """
        Realiza la migración por lotes (batch) de 10,000 registros.
        Devuelve un diccionario con el estado:
            {'key': 0, 'error': None} en caso de éxito
            {'key': 1, 'error': <mensaje>} en caso de error
        """
        try:
            verifica = self.verifica_conexion()
            if verifica['key'] != 0:
                return {"key": verifica['key'], "error": verifica['error']}

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
                
                # Obtienes los nombres de las columnas directamente desde la query
                columnas_destino = [desc[0].split('.')[-1] for desc in cursor_orig.description]

                columnas_str = ", ".join(columnas_destino)
                placeholders = ", ".join(["?"] * len(columnas_destino))
                insert_query = f"INSERT INTO {tabla_dst} ({columnas_str}) VALUES ({placeholders})"
                while True:
                    rows = cursor_orig.fetchmany(10_000)
                    if not rows:
                        break

                    # rows = [[str(i) for i in list(row)] for row in rows]
                    cursor_dst.executemany(insert_query, rows)
                    dst.commit()

                return {"key": 0, "error": None}

        except Exception as e:
            # Captura cualquier error y lo devuelve como parte del diccionario
            return {"key": 3, "error": e}

    def verifica_conexion(self) -> dict:
        """
        Metodo privado para verificar las conexiones a ambas bases de datos
        Devuelve un diccionario con el estado:
            {'key': 0, 'error': None} en caso de éxito
            {'key': 1 o 2, 'error': <mensaje>} en caso de error
        """
        try: 
            jaydebeapi.connect(
                "org.apache.hive.jdbc.HiveDriver",
                self.credenciales['dns_orig'],
                [
                    self.credenciales['usr_orig'],
                    self.credenciales['pwd_orig']
                ],
                "app\\factory\\drivers\\hive-jdbc-uber-2.6.5.0-292.jar"
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