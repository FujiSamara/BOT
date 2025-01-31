from app.infra.config import settings
from typing import Callable, Any
from datetime import datetime
import os


def delete_old_files(
    get_old_paths_func: Callable, update_old_paths_func: Callable, dt_now: datetime
) -> bool:
    old_paths, id_list = get_old_paths_func(dt_now, settings.stubname)
    for old_path in old_paths:
        if os.path.exists(os.path.abspath(old_path)):
            os.remove(old_path)
    return update_old_paths_func(id_list, settings.stubname)


def delete_files_for_model_by_id(model: Any, row_id: int, id_column: str) -> bool:
    from app import services

    paths = services.get_file_paths_model(model, row_id, id_column=id_column)
    for path in paths:
        if os.path.exists(os.path.abspath(path)):
            os.remove(path)
    return True
