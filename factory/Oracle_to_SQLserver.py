from factory.Migrador import Migrador
import oracledb
import pyodbc
from oracledb import DB_TYPE_CHAR, DB_TYPE_CLOB, DB_TYPE_DATE, \
    DB_TYPE_BOOLEAN, DB_TYPE_NUMBER, DB_TYPE_NVARCHAR, DB_TYPE_VARCHAR

class Oracle_to_SQLserver(Migrador):

    def __init__(self) -> None:
        """
        Contructor de la clase
        """
        # mapa de conversiones
        self.conversiones = {
            DB_TYPE_CHAR: lambda data: f"CHAR({data['data_length']})",
            DB_TYPE_VARCHAR: lambda data: f"VARCHAR({data['data_length']})",
            DB_TYPE_NUMBER: lambda data: (
                f"NUMERIC({data['data_precision']},{data['data_scale']})"
                if data['data_precision'] is not None and data['data_scale'] is not None
                else "INT"
            ),
            DB_TYPE_DATE: lambda data: "DATETIME2",
            DB_TYPE_CLOB: lambda data: "TEXT",
            DB_TYPE_BOOLEAN: lambda data: "BOOL",
            DB_TYPE_NVARCHAR: lambda data: lambda data: f"VARCHAR({data['data_length']})"
        }
        # mapa de credenciales
        self.credenciales = None
        # conectores
        self.conn_oracle = None
        self.conn_sql_server = None
        # tablas
        self.tablas = None
        # definicion catalogos o deltas
        self.catalogo_delta = None

    def define_credenciales(self, env_path: str) -> None:
        """
        Metodo que registra las credenciales
        Args:
            # env_path: path donde esta el .env con las credenciales
        """
        # Carga las variables de entorno para la conexion
        if not load_dotenv(env_path):
            print('No se cargaron las credenciales')
            return
        # Creacion de diccionario con credenciales para conexion
        self.credenciales = {
            'user_oracle': getenv('USER_ORACLE'),
            'password_oracle': getenv('PASS_ORACLE'),
            'dns_oracle': getenv('DNS_ORACLE'),
            'user_sql_server': getenv('USER_SQL_SERVER'),
            'password_sql_server': getenv('PASS_SQL_SERVER'),
            'dns_sql_server': getenv('DNS_SQL_SERVER'),
            'database_sql_server': getenv('DATABASE_SQL_SERVER')
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
        # verifica si existe la conexion
        if not self.verifica_conexion():
            print('No se han establecido conexiones')
            return
        # definicion de catalogos o deltas
        self.catalogo_delta = tablas
        # definicion de nuevas tablas a destino
        self.tablas = {}
        # conexion al servidor oracle
        cursor = self.conn_oracle.cursor()
        # recorrido a las tablas que migraran
        for tabla in tablas.keys():
            try:
                # consulta a la tabla
                cursor.execute(f"""
                    SELECT * FROM {tabla}
                """)
                # arreglo de columnas
                columnas = []
                # recorrido a las columnas descritas
                for col in cursor.description:
                    # diccionario de la columna discreta
                    dict_row = {c: data for c, data in zip(['column_name', 'data_type', 'data_length', 'display_size', 'data_precision', 'data_scale', 'nullable'], col)}
                    # si es tipo de datos excluido lo saltamos
                    if dict_row['data_type'] in excluye:
                        continue
                    # conversion de las columnas
                    dict_row['new_data_type'] = self.conversiones[dict_row['data_type']](dict_row)
                    columnas.append({dict_row['column_name']:[dict_row['new_data_type'], dict_row['nullable']]})
                # guardamos la tabla con sus columnas convertidas
                self.tablas[tabla] = columnas
            except Exception as e:
                print('Fallo en la tabla: ',tabla, e)

        # cerrar cursor
        cursor.close()

    def conecta(self, driver_oracle: str) -> None:
        """
        Metodo que realiza la conexion a ambas bases de datos
        Args:
            # driver_oracle: path del driver para oracle
        """
        # verificacion de credenciales
        if self.credenciales == None:
            print('No has definido las credenciales')
            return
        try:
            # carga de driver para oracle
            oracledb.init_oracle_client(lib_dir=driver_oracle)
            # conexion a oracle
            self.conn_oracle = oracledb.connect(
                user=self.credenciales['user_oracle'],
                password=self.credenciales['password_oracle'],
                dsn=self.credenciales['dns_oracle']
            )
            print('Conexion exitosa a Oracle')
        except Exception as e:
            print("Fallo la conexion a Oracle\n", e)
        try:
            # conexion a sql server
            self.conn_sql_server = pyodbc.connect(
                f'DRIVER={{SQL Server}};SERVER={self.credenciales['dns_sql_server']};DATABASE={self.credenciales['database_sql_server']};UID={self.credenciales['user_sql_server']};PWD={self.credenciales['password_sql_server']}'
            )
            print('Conexion exitosa a SQL Server')
        except Exception as e:
            print("Fallo la conexion a SQL Server\n", e)

    def crea_tablas(self):
        """
        Metodo que crea las tablas en SQL Server
        """
        # verifica si existe la conexion
        if not self.verifica_conexion():
            print('No se han establecido conexiones')
            return
        # conexion al servidor SQL Server
        cursor = self.conn_sql_server.cursor()
        for tabla, columnas in tqdm(self.tablas.items(), desc="Creando tablas"):
            # Query para la creacion de la tabla en sql server
            query = f"CREATE TABLE {tabla} ("
            # recorrido de columnas
            for col in columnas:
                # extraccion de nombre y datos por columna
                for nombre, datos in col.items():
                    # datos [0]: tipo de dato
                    # datos[1]: nulleable
                    if not datos[1]:
                        query += f"{nombre} {datos[0]} NOT NULL,"
                    else:
                        query += f"{nombre} {datos[0]},"
            query = query[:-1]+")"
            try:
                pass
                # cursor.execute(query)
                # cursor.commit()
            except Exception as e:
                print(f"Falo en la tabla: {tabla}", e)

        # cerrar cursor
        cursor.close()

    def actualiza_conversiones(self, conversiones: dict):
        """
        Metodo que define las conversiones de tipos de dato
        Args:
            # conversiones: diccionario de conversiones
        """
        self.conversiones = conversiones

    def migrar(self) -> None:
        """
        Metodo que realiza la migracion
        """
        # verifica si existe la conexion
        if not self.verifica_conexion():
            print('No se han establecido conexiones')
            return
        if self.tablas == None or self.catalogo_delta == None:
            print("No has definido las tablas")
            return
        # cursor sql
        cursor_sql_server = self.conn_sql_server.cursor()
        # cursor oracle 
        cursor_oracle = self.conn_oracle.cursor()
        # variable de pyodbc para usar bucket en la insercion (velocidad de inserciones)
        cursor_sql_server.fast_executemany = True
        # extraccion de registros
        for tabla in tqdm(self.tablas.keys(), desc='Migrando tablas'):
            # columnas formateadas
            columnas = ",".join([list(columnas.keys())[0] for columnas in self.tablas[tabla]])
            # aplicacion de filtro si no es catalogo
            if self.catalogo_delta[tabla] == 'catalogo':
                query = f"SELECT {columnas} FROM {tabla}"
            else:
                query = f"SELECT {columnas} FROM {tabla} {self.catalogo_delta[tabla][0]}"
            # ejecucion de la query
            try:
                cursor_oracle.execute(query)
                # inserts = cursor_oracle.fetchall()
            except Exception as e:
                print(f'{tabla} -> Fallo la extraccion de datos', e)

            # columnas para la insercion
            interroga = "("+",".join(["?" for _ in self.tablas[tabla]])+")"
            try:
                pass
                # cursor_sql_server.executemany(f"INSERT INTO {tabla} ({columnas}) VALUES {interroga}", inserts)
                # cursor_sql_server.commit()
            except Exception as e:
                print(f"{tabla} -> Fallo en la insercion", e)
        cursor_sql_server.close()
        cursor_oracle.close()

    def revisa_integridad(self) -> None:
        """
        Metodo que revisa la integridad de los datos migrados
        """
        # verifica si existe la conexion
        if not self.verifica_conexion():
            print('No se han establecido conexiones')
            return
        if self.tablas == None or self.catalogo_delta == None:
            print("No has definido las tablas")
            return
        # cursor sql
        cursor_sql_server = self.conn_sql_server.cursor()
        # cursor oracle 
        cursor_oracle = self.conn_oracle.cursor()
        # extraccion de registros
        for tabla in self.tablas.keys():
            # aplicacion de filtro si no es catalogo
            if self.catalogo_delta[tabla] == 'catalogo':
                query = f"SELECT count(1) FROM {tabla}"
                query_sql_server = query
            else:
                query = f"SELECT count(1) FROM {tabla} {self.catalogo_delta[tabla][0]}"
                query_sql_server = f"SELECT count(1) FROM {tabla} {self.catalogo_delta[tabla][1]}"
            # ejecucion de la query
            try:
                cursor_oracle.execute(query)
                o = cursor_oracle.fetchone()[0]
                cursor_sql_server.execute(query_sql_server)
                s = cursor_sql_server.fetchone()[0]
                print(f"{tabla} oracle:{o} sql server:{s} ✅" if o==s else f"{tabla} oracle:{o} sql server:{s} ❌")
            except Exception as e:
                print(f'{tabla} -> Fallo la extraccion de datos', e)            

    def desconecta(self) -> None:
        """
        Metodo que desconecta las conexiones a ambas bases de datos
        """
        # verifica si hay conexiones por desconectar
        if self.verifica_conexion():
            self.conn_oracle.close()
            self.conn_sql_server.close()
        else:
            print('No se han establecido conexiones')

    def verifica_conexion(self):
        """
        Metodo privado para verificar las conexiones a ambas bases de datos
        """
        if self.conn_oracle != None and self.conn_sql_server != None:
            return True
        else:
            return False