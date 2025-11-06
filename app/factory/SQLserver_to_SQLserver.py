from app.factory.Migrador import Migrador
import pyodbc

class SQLserver_to_SQLserver(Migrador):

    def __init__(self) -> None:
        """
        Contructor de la clase
        """
        # # mapa de conversiones
        # self.conversiones = {
        #     DB_TYPE_CHAR: lambda data: f"CHAR({data['data_length']})",
        #     DB_TYPE_VARCHAR: lambda data: f"VARCHAR({data['data_length']})",
        #     DB_TYPE_NUMBER: lambda data: (
        #         f"NUMERIC({data['data_precision']},{data['data_scale']})"
        #         if data['data_precision'] is not None and data['data_scale'] is not None
        #         else "INT"
        #     ),
        #     DB_TYPE_DATE: lambda data: "DATETIME2",
        #     DB_TYPE_CLOB: lambda data: "TEXT",
        #     DB_TYPE_BOOLEAN: lambda data: "BOOL",
        #     DB_TYPE_NVARCHAR: lambda data: lambda data: f"VARCHAR({data['data_length']})"
        # }
        # mapa de credenciales
        self.credenciales = None
        # conectores
        self.conn_orig = None
        self.conn_dst = None
        # tablas
        self.tablas = None
        # definicion catalogos o deltas
        self.catalogo_delta = None

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
    
    def define_tablas(self, tablas: dict, excluye: list = []):
        """
        Metodo que define las tablas a migrar
        Args:
            # tablas: diccionario con estructura
                    [
                        { 
                        'nombre tabla': [
                                            "query Oracle",
                                            "query SQL Server"
                                        ] 
                        },
                        ...
                    ]
            # excluye: lista de tipos de datos excluidos
        """
        pass

    def conecta(self, driver_oracle: str) -> None:
        """
        Metodo que realiza la conexion a ambas bases de datos
        Args:
            # driver_oracle: path del driver para oracle
        """
        pass

    def crea_tablas(self):
        """
        Metodo que crea las tablas en SQL Server
        """
        pass

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

                cursor_orig.execute(query_select)
                
                # Obtienes los nombres de las columnas directamente desde la query
                columnas_destino = [desc[0] for desc in cursor_orig.description]

                columnas_str = ", ".join(columnas_destino)
                placeholders = ", ".join(["?"] * len(columnas_destino))
                insert_query = f"INSERT INTO {tabla_dst} ({columnas_str}) VALUES ({placeholders})"

                while True:
                    rows = cursor_orig.fetchmany(10_000)
                    if not rows:
                        break

                    cursor_dst.executemany(insert_query, rows)
                    dst.commit()

                return {"key": 0, "error": None}

        except Exception as e:
            # Captura cualquier error y lo devuelve como parte del diccionario
            return {"key": 3, "error": e}

    def revisa_integridad(self) -> None:
        """
        Metodo que revisa la integridad de los datos migrados
        """
        pass           

    def desconecta(self) -> None:
        """
        Metodo que desconecta las conexiones a ambas bases de datos
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