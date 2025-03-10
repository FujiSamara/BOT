from common.contracts.uow import BaseUnitOfWork

from app.contracts.repositories import FileRepository


class FileUnitOfWork(BaseUnitOfWork):
    file: FileRepository
