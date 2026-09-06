from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from generated.database import get_db
from generated import repository as repo
from generated.schema import KlijentCreate, PaketCreate, RadnikCreate, TerminCreate, UslugaCreate, KlijentRead, PaketRead, RadnikRead, TerminRead, UslugaRead, KlijentUpdate, PaketUpdate, RadnikUpdate, TerminUpdate, UslugaUpdate
from generated import validation

router = APIRouter()
@router.post("/klijent/", response_model=KlijentRead)
def create_klijent(data: KlijentCreate, db: Session = Depends(get_db)):
    return repo.create_klijent(db, data.model_dump())

@router.get("/klijent/", response_model=list[KlijentRead])
def list_klijent(db: Session = Depends(get_db)):
    return repo.get_all_klijent(db)

@router.get("/klijent/{item_id}", response_model=KlijentRead)
def get_klijent(item_id: int, db: Session = Depends(get_db)):
    obj = repo.get_klijent(db, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Klijent not found")
    return obj

@router.put("/klijent/{item_id}", response_model=KlijentRead)
def update_klijent(item_id: int, data: KlijentUpdate, db: Session = Depends(get_db)):
    obj = repo.update_klijent(db, item_id, data.model_dump(exclude_none=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Klijent not found")
    return obj

@router.delete("/klijent/{item_id}")
def delete_klijent(item_id: int, db: Session = Depends(get_db)):
    ok = repo.delete_klijent(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Klijent not found")
    return {"deleted": True}
@router.post("/paket/", response_model=PaketRead)
def create_paket(data: PaketCreate, db: Session = Depends(get_db)):
    try:
        validation.validiraj_Paket(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return repo.create_paket(db, data.model_dump())

@router.get("/paket/", response_model=list[PaketRead])
def list_paket(db: Session = Depends(get_db)):
    return repo.get_all_paket(db)

@router.get("/paket/{item_id}", response_model=PaketRead)
def get_paket(item_id: int, db: Session = Depends(get_db)):
    obj = repo.get_paket(db, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Paket not found")
    return obj

@router.put("/paket/{item_id}", response_model=PaketRead)
def update_paket(item_id: int, data: PaketUpdate, db: Session = Depends(get_db)):
    obj = repo.update_paket(db, item_id, data.model_dump(exclude_none=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Paket not found")
    return obj

@router.delete("/paket/{item_id}")
def delete_paket(item_id: int, db: Session = Depends(get_db)):
    ok = repo.delete_paket(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Paket not found")
    return {"deleted": True}
@router.post("/radnik/", response_model=RadnikRead)
def create_radnik(data: RadnikCreate, db: Session = Depends(get_db)):
    return repo.create_radnik(db, data.model_dump())

@router.get("/radnik/", response_model=list[RadnikRead])
def list_radnik(db: Session = Depends(get_db)):
    return repo.get_all_radnik(db)

@router.get("/radnik/{item_id}", response_model=RadnikRead)
def get_radnik(item_id: int, db: Session = Depends(get_db)):
    obj = repo.get_radnik(db, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Radnik not found")
    return obj

@router.put("/radnik/{item_id}", response_model=RadnikRead)
def update_radnik(item_id: int, data: RadnikUpdate, db: Session = Depends(get_db)):
    obj = repo.update_radnik(db, item_id, data.model_dump(exclude_none=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Radnik not found")
    return obj

@router.delete("/radnik/{item_id}")
def delete_radnik(item_id: int, db: Session = Depends(get_db)):
    ok = repo.delete_radnik(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Radnik not found")
    return {"deleted": True}
@router.post("/termin/", response_model=TerminRead)
def create_termin(data: TerminCreate, db: Session = Depends(get_db)):
    try:
        validation.validiraj_Termin(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return repo.create_termin(db, data.model_dump())

@router.get("/termin/", response_model=list[TerminRead])
def list_termin(db: Session = Depends(get_db)):
    return repo.get_all_termin(db)

@router.get("/termin/{item_id}", response_model=TerminRead)
def get_termin(item_id: int, db: Session = Depends(get_db)):
    obj = repo.get_termin(db, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Termin not found")
    return obj

@router.put("/termin/{item_id}", response_model=TerminRead)
def update_termin(item_id: int, data: TerminUpdate, db: Session = Depends(get_db)):
    obj = repo.update_termin(db, item_id, data.model_dump(exclude_none=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Termin not found")
    return obj

@router.delete("/termin/{item_id}")
def delete_termin(item_id: int, db: Session = Depends(get_db)):
    ok = repo.delete_termin(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Termin not found")
    return {"deleted": True}
@router.post("/usluga/", response_model=UslugaRead)
def create_usluga(data: UslugaCreate, db: Session = Depends(get_db)):
    return repo.create_usluga(db, data.model_dump())

@router.get("/usluga/", response_model=list[UslugaRead])
def list_usluga(db: Session = Depends(get_db)):
    return repo.get_all_usluga(db)

@router.get("/usluga/{item_id}", response_model=UslugaRead)
def get_usluga(item_id: int, db: Session = Depends(get_db)):
    obj = repo.get_usluga(db, item_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Usluga not found")
    return obj

@router.put("/usluga/{item_id}", response_model=UslugaRead)
def update_usluga(item_id: int, data: UslugaUpdate, db: Session = Depends(get_db)):
    obj = repo.update_usluga(db, item_id, data.model_dump(exclude_none=True))
    if obj is None:
        raise HTTPException(status_code=404, detail="Usluga not found")
    return obj

@router.delete("/usluga/{item_id}")
def delete_usluga(item_id: int, db: Session = Depends(get_db)):
    ok = repo.delete_usluga(db, item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usluga not found")
    return {"deleted": True}
