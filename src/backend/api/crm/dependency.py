from typing import Callable

from db.schemas import PanelSchema


class PanelParser:
    @staticmethod
    def build_getting_panels(panel_name: str) -> Callable[[], PanelSchema]:
        pass

    @staticmethod
    def build_creating_panel_row(panel_name: str) -> Callable[[dict[str, str]], None]:
        pass

    @staticmethod
    def build_deleting_panel_row(panel_name: str) -> Callable[[int], None]:
        pass

    @staticmethod
    def build_updating_panel_row(
        panel_name: str,
    ) -> Callable[[int, dict[str, str]], None]:
        pass
