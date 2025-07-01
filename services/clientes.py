from models.clientes import Cliente as ClienteModel
from schemas.cliente import ClienteCreate, Cliente

class ClienteService:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        result = self.db.query(ClienteModel).all()
        return [Cliente.model_validate(c) for c in result]

    def create(self, cliente: ClienteCreate):
        new_cliente = ClienteModel(**cliente.dict())
        self.db.add(new_cliente)
        self.db.commit()
        self.db.refresh(new_cliente)
        return new_cliente

    def get(self, id: int):
        result = self.db.query(ClienteModel).filter(ClienteModel.id == id).first()
        return Cliente.model_validate(result)

    def update(self, id: int, cliente: ClienteCreate):
        result = self.db.query(ClienteModel).filter(ClienteModel.id == id).first()
        if not result:
            return None
        for key, value in cliente.dict().items():
            setattr(result, key, value)
        self.db.commit()
        self.db.refresh(result)
        return result

    def delete(self, id: int):
        self.db.query(ClienteModel).filter(ClienteModel.id == id).delete()
        self.db.commit()
