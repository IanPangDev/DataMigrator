import argparse
from subprocess import run
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from Registro import Base, Registro
from datetime import datetime

def main():
    # Definir los argumentos que el script aceptará
    parser = argparse.ArgumentParser(description="Script de ejemplo que recibe argumentos")
    parser.add_argument("--mode", type=int, help="Elimina o crea", required=True)
    parser.add_argument("--name", type=str, help="nombre de la tarea", required=True)
    parser.add_argument("--periodo", type=str, help="periodo de ejecucion", required=True)
    parser.add_argument("--db_orig", type=str, help="base de datos origen", required=True) 
    parser.add_argument("--db_dst", type=str, help="base de datos destino", required=True) 
    parser.add_argument("--usr_orig", type=str, help="usuario del origen", required=True)
    parser.add_argument("--usr_dst", type=str, help="usuario del destino", required=True)
    parser.add_argument("--pwd_orig", type=str, help="password del origen", required=True)
    parser.add_argument("--pwd_dst", type=str, help="password del destino", required=True)
    parser.add_argument("--dns_orig", type=str, help="dns del origen", required=True)
    parser.add_argument("--dns_dst", type=str, help="dns del destino", required=True)
    parser.add_argument("--query_path", type=str, help="path de la query", required=True)
    parser.add_argument("--tabla_dst", type=str, help="Tabla destino", required=True)

    # Parsear
    args = parser.parse_args()

    # Mostrar parámetros
    print(
        "\n"
        f"periodo de ejecucion: {args.periodo}\n"
        f"base de datos origen: {args.db_orig}\n"
        f"base de datos destino: {args.db_dst}\n"
        f"usuario del origen: {args.usr_orig}\n"
        f"usuario del destino: {args.usr_dst}\n"
        f"password del origen: {args.pwd_orig}\n"
        f"password del destino: {args.pwd_dst}\n"
        f"dns del origen: {args.dns_orig}\n"
        f"dns del destino: {args.dns_dst}\n"
        f"path de la query: {args.query_path}\n"
        f"Tabla destino: {args.tabla_dst}\n"
    )

    # Base de datos
    db_path = "registros.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    logs = create_window_logs()

    # CREA LAS TABLAS SI NO EXISTEN
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    logs = create_window_logs()

    logs.insert('end', f'[{datetime.now()}] Base de datos creada y registro insertado.')
    # print("Base de datos creada y registro insertado.")

    # Crear o eliminar tarea programada
    if args.mode == 0:
        output = run(
            [
                "schtasks", "/create",
                "/tn", "MyTESTApp",
                "/tr", "C:\\Users\\imss\\Desktop\\DataMigrator\\app\\prograTask\\task.bat",
                "/sc", "daily", "/st", "10:42"
            ],
            capture_output=True, text=True
        )
        logs.insert('end', f'[{datetime.now()}] {output.stdout}')
        # print(output.stdout)

        # Crear registro con ORM (correcto)
        nuevo = Registro(name=args.name)
        session.add(nuevo)
        session.commit()
        # SELECT seguro
        result = session.execute(
            text("SELECT * FROM registros WHERE name = :name"),
            {"name": args.name}
        ).fetchall()
        
        logs.insert('end', f'[{datetime.now()}] Insertado: {result}')
        # print("Insertado:", result)
    else:
        output = run(["schtasks", "/delete", "/tn", "MyTESTApp", "/f"], capture_output=True, text=True)
        logs.insert('end', f'[{datetime.now()}] {output.stdout}')
        # print(output.stdout)

        # SELECT seguro
        result = session.execute(
            text("SELECT * FROM registros WHERE name = :name"),
            {"name": args.name}
        ).fetchall()

        logs.insert('end', f'[{datetime.now()}] ANTES DE BORRAR: {result}')
        # print("ANTES DE BORRAR:", result)

        # DELETE seguro
        session.execute(
            text("DELETE FROM registros WHERE name = :name"),
            {"name": args.name}
        )
        session.commit()

        # Verificar borrado
        result = session.execute(
            text("SELECT * FROM registros WHERE name = :name"),
            {"name": args.name}
        ).fetchall()

        logs.insert('end', f'[{datetime.now()}] DESPUÉS DE BORRAR: {result}')
        # print("DESPUÉS DE BORRAR:", result)


if __name__ == "__main__":
    main()