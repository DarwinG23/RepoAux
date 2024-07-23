from models.persona import Persona
from models.rol import Rol
from controls.tda.linked.linkedList import Linked_List

class Docente(Persona):
    def __init__(self):
        super().__init__()
        self.__titulo = ""
        self.__cubiculo = ""
        self.__idiomas = ""
        self.__tipoContrato = ""
        self.__idPersona = 0

    @property
    def _idPersona(self):
        return self.__idPersona

    @_idPersona.setter
    def _idPersona(self, value):
        self.__idPersona = value


    @property
    def _titulo(self):
        return self.__titulo

    @_titulo.setter
    def _titulo(self, value):
        self.__titulo = value

    @property
    def _cubiculo(self):
        return self.__cubiculo

    @_cubiculo.setter
    def _cubiculo(self, value):
        self.__cubiculo = value

    @property
    def _idiomas(self):
        return self.__idiomas

    @_idiomas.setter
    def _idiomas(self, value):
        self.__idiomas = value

    @property
    def _tipoContrato(self):
        return self.__tipoContrato

    @_tipoContrato.setter
    def _tipoContrato(self, value):
        self.__tipoContrato = value

    @property
    def serializable(self):
        data = super().serializable
        
        data.update({
            "titulo": self.__titulo,
            "cubiculo": self.__cubiculo,
            "idiomas": self.__idiomas,
            "tipoContrato": self.__tipoContrato,
            "idPersona": self.__idPersona
        })
        return data
    
    def deserializar(data):
        docente = Docente()
        docente._id = data["id"]
        docente._dni = data["dni"]
        docente._nombre = data["nombre"]
        docente._apellido = data["apellido"]
        docente._fechaNacimiento = data["fechaNacimiento"]
        docente._numTelefono = data["numTelefono"]
        docente._idCuenta = data["idCuenta"]
        clase = Rol()
        docente._roles = Linked_List().deserializar(data["roles"], clase)
        docente._titulo = data["titulo"]
        docente._cubiculo = data["cubiculo"]
        docente._idiomas = data["idiomas"]
        docente._tipoContrato = data["tipoContrato"]
        docente._idPersona = data["idPersona"]
        return docente
    
    def __str__(self) -> str:
        return f'{self.__titulo} {self.__cubiculo} {self.__idiomas} {self.__tipoContrato}'



