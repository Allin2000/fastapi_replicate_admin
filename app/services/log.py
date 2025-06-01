from app.services.crud import CRUDBase
from app.sqlmodel.admin import Log
from app.schemas.logs import LogCreate, LogUpdate


class LogController(CRUDBase[Log, LogCreate, LogUpdate]):
    def __init__(self):
        super().__init__(model=Log)


log_controller = LogController()