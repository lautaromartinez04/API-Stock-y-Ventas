from models.categorias import Categoria as CategoriaModel
from schemas.categoria import CategoriaCreate, Categoria

class CategoriaService:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        result = self.db.query(CategoriaModel).all()
        return [Categoria.model_validate(c) for c in result]

    def create(self, categoria: CategoriaCreate):
        new_categoria = CategoriaModel(**categoria.dict())
        self.db.add(new_categoria)
        self.db.commit()
        self.db.refresh(new_categoria)
        return new_categoria

    def get(self, id: int):
        result = self.db.query(CategoriaModel).filter(CategoriaModel.id == id).first()
        return Categoria.model_validate(result)

    def update(self, id: int, categoria: CategoriaCreate):
        result = self.db.query(CategoriaModel).filter(CategoriaModel.id == id).first()
        if not result:
            return None
        for key, value in categoria.dict().items():
            setattr(result, key, value)
        self.db.commit()
        self.db.refresh(result)
        return result

    def delete(self, id: int):
        self.db.query(CategoriaModel).filter(CategoriaModel.id == id).delete()
        self.db.commit()
