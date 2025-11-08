from abc import ABC, abstractmethod

class Migrador(ABC):

    @abstractmethod
    def define_credenciales(self, **kwargs):
        """
        Metodo que registra las credenciales
        """
        pass

    @abstractmethod
    def migrar(self, **kwargs):
        """
        Metodo que realiza la migracion
        """
        pass

    @abstractmethod
    def revisa_integridad(self, **kwargs):
        """
        Metodo que revisa la integridad de los datos migrados
        """
        pass
    
    @abstractmethod
    def verifica_conexion(self, **kwargs):
        """
        Metodo que verifica las conexiones a ambas bases de datos
        """
        pass