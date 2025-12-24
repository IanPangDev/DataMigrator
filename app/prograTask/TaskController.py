import threading
from subprocess import run

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from Registro import Base, Registro


class TaskController:
    def __init__(self, view):
        self.view = view

        self.engine = create_engine("sqlite:///registros.db")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def create_task(self, name):
        threading.Thread(
            target=self._create_worker,
            args=(name,),
            daemon=True
        ).start()

    def delete_task(self, name):
        threading.Thread(
            target=self._delete_worker,
            args=(name,),
            daemon=True
        ).start()

    def _create_worker(self, name):
        self.view.log("Creando tarea...")

        result = run(
            [
                "schtasks", "/create",
                "/tn", name,
                "/tr", r"C:\Users\Ian\Desktop\DataMigrator\app\prograTask\task.bat",
                "/sc", "daily",
                "/st", "18:13"
            ],
            capture_output=True,
            text=True
        )

        self.view.log(result.stdout or result.stderr)

        self.session.add(Registro(name=name))
        self.session.commit()

        self.view.log(f"Tarea registrada: {name}")
    
    def _delete_worker(self, name):
        self.view.log("Borrando tarea...")

        result = run(
            [
                "schtasks", 
                "/delete",
                "/tn",
                "MyTESTApp", 
                "/f"
            ],
            capture_output=True,
            text=True
        )

        self.view.log(result.stdout or result.stderr)

        self.session.execute(
            text("DELETE FROM registros WHERE name = :name"),
            {"name": name}
        )
        self.session.commit()

        self.view.log(f"Tarea eliminada: {name}")