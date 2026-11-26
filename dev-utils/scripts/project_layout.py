from select_repository import read_prompt


LAYOUTS = {
    "board": "BOARD_LAYOUT",
    "table": "TABLE_LAYOUT",
    "roadmap": "ROADMAP_LAYOUT",
}


def prompt_view_layout() -> str:
    while True:
        layout = (read_prompt("View layout (board/table/roadmap) [board]: ") or "board").lower()
        if layout in LAYOUTS:
            return layout
        print("Choose board, table, or roadmap.")
