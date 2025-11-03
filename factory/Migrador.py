from abc import ABC, abstractmethod

class Migrador(ABC):

    @abstractmethod
    def define_credenciales(self, **kwargs):
        """
        Metodo que registra las credenciales
        """
        pass

    @abstractmethod
    def actualiza_conversiones(self, **kwargs):
        """
        Metodo que define las conversiones de tipos de dato
        """
        pass
    
    @abstractmethod
    def define_tablas(self, **kwargs):
        """
        Metodo que define las tablas a migrar
        """
        pass

    @abstractmethod
    def conecta(self, **kwargs):
        """
        Metodo que realiza la conexion a ambas bases de datos
        """
        pass


    @abstractmethod
    def crea_tablas(self, **kwargs):
        """
        Metodo que crea las tablas en SQL Server
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
    def desconecta(self, **kwargs):
        """
        Metodo que desconecta las conexiones a ambas bases de datos
        """
        pass
    
    @abstractmethod
    def verifica_conexion(self, **kwargs):
        """
        Metodo que verifica las conexiones a ambas bases de datos
        """
        pass