from app.vista import Vista
from app.factory import SQLserver_to_SQLserver, Hive_to_SQLserver, Oracle_to_SQLserver
from threading import Thread
from datetime import datetime

class Controlador:
    def __init__(self):
        self.vista = Vista(self)

    def cambiar_vista(self, clave: str):
        datos = {
            "sql_serverxsql_server": lambda: self.vista.mostrar_sql_server_to_sql_server(),
            "hivexsql_server": lambda: self.vista.mostrar_hive_to_sql_server(),
            "oraclexsql_server": lambda: self.vista.mostrar_oracle_to_sql_server()
        }
        datos[clave]()
    
    def define_motores(self, clave: str):
        datos = {
            "sql_serverxsql_server": SQLserver_to_SQLserver(),
            "hivexsql_server": Hive_to_SQLserver(),
            "oraclexsql_server": Oracle_to_SQLserver()
        }
        self.factory = datos[clave]

    def migrar(self, query_select: str, tabla_dst: str, create_tabla: bool):
        # Mostrar ventana con logs
        logs = self.vista.mostrar_logs()

        # -------------------------
        #   HILO DE MIGRACIÓN
        # -------------------------
        def migracion_hilo():
            logs.insert("end", f"[{datetime.now()}] MIGRACIÓN EMPEZADA a {tabla_dst}\n")
            self.factory.migrar(query_select, tabla_dst, logs, create_tabla)
            logs.see("end")

        # Lanzar hilo
        hilo_migracion = Thread(target=migracion_hilo, daemon=True)
        hilo_migracion.start()

        return

    def verifica_conexion(self,
                        usr_orig: str,
                        pwd_orig: str,
                        dns_orig: str,
                        db_orig: str,
                        usr_dst: str,
                        pwd_dst: str,
                        dns_dst: str,
                        db_dst: str
                        ) -> dict:
        self.factory.define_credenciales(
            usr_orig,
            pwd_orig,
            dns_orig,
            db_orig,
            usr_dst,
            pwd_dst,
            dns_dst,
            db_dst,
        )
        return self.factory.verifica_conexion()

    def ejecutar(self):
        self.vista.mainloop()