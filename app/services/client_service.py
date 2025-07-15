from sqlalchemy.orm import Session
from app.models.client import Client,ClientCreate
# from app.schemas import ClientCreate, Client

def get_client(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Client).offset(skip).limit(limit).all()

def create_client(db: Session, client: ClientCreate):
    # client_data = client.dict(exclude_unset=True)
    try:
        db_client = Client.from_orm(client)
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    except Exception as e:
        print(f"Error creating client: {e}")
        return None

def update_client(db: Session, client_id: int, client_update: dict):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client:
        for key, value in client_update.items():
            setattr(db_client, key, value)
        db.commit()
        db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: int):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client:
        db.delete(db_client)
        db.commit()
    return db_client