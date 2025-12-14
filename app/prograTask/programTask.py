import argparse
from subprocess import run
from os.path import exists
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from Registro import Base, Registro


def main():
    # Definir los argumentos que el script aceptará
    parser = argparse.ArgumentParser(description="Script de ejemplo que recibe argumentos")
    parser.add_argument("--mode", type=int, help="Elimina o crea")
    parser.add_argument("--name", type=str, help="nombre de la tarea")
    parser.add_argument("--periodo", type=str, help="periodo de ejecucion")
    parser.add_argument("--db_orig", type=str, help="base de datos origen") 
    parser.add_argument("--db_dst", type=str, help="base de datos destino") 
    parser.add_argument("--usr_orig", type=str, help="usuario del origen")
    parser.add_argument("--usr_dst", type=str, help="usuario del destino")
    parser.add_argument("--pwd_orig", type=str, help="password del origen")
    parser.add_argument("--pwd_dst", type=str, help="password del destino")
    parser.add_argument("--dns_orig", type=str, help="dns del origen")
    parser.add_argument("--dns_dst", type=str, help="dns del destino")
    parser.add_argument("--query_path", type=str, help="path de la query")
    parser.add_argument("--tabla_dst", type=str, help="Tabla destino")

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
    engine = create_engine(f"sqlite:///{db_path}", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    if not exists(db_path):
        # Crear la BD
        Base.metadata.create_all(engine)

        print("Base de datos creada y registro insertado.")

    # Crear o eliminar tarea programada
    if args.mode == 0:
        output = run(
            [
                "schtasks", "/create",
                "/tn", "MyTESTApp",
                "/tr", "C:\\Users\\imss\\Desktop\\DataMigrator\\app\\prograTask\\task.bat",
                "/sc", "daily", "/st", "11:45"
            ],
            capture_output=True, text=True
        )
        print(output.stdout)

        # Crear registro con ORM (correcto)
        nuevo = Registro(name=args.name)
        session.add(nuevo)
        session.commit()
        # SELECT seguro
        result = session.execute(
            text("SELECT * FROM registros WHERE name = :name"),
            {"name": args.name}
        ).fetchall()
        
        print("Insertado:", result)
    else:
        output = run(["schtasks", "/delete", "/tn", "MyTESTApp", "/f"], capture_output=True, text=True)
        print(output.stdout)

        # SELECT seguro
        result = session.execute(
            text("SELECT * FROM registros WHERE name = :name"),
            {"name": args.name}
        ).fetchall()

        print("ANTES DE BORRAR:", result)

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

        print("DESPUÉS DE BORRAR:", result)


if __name__ == "__main__":
    main()