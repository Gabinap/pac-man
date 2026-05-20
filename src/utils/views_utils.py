from panda3d.core import TransparencyAttrib
from ursina import Button, Text, color, Entity, Quad
import src.config.constants as C

GLASS = color.rgba32(150, 180, 160, 105)
GLASS_HOVER = color.rgba32(180, 205, 220, 140)
GLASS_SELECTED = color.rgba32(220, 175, 80, 170)
GLASS_EXIT_SELECTED = color.rgba32(165, 70, 75, 180)
BORDER = color.rgba32(240, 220, 185, 130)
TEXT_COLOR = color.rgba32(250, 240, 220, 255)

TITLE_COLOR = color.rgba32(230, 150, 170, 255)
TITLE_OUTLINE = color.rgba32(95, 35, 60, 255)
SUBTITLE_COLOR = color.rgba32(180, 205, 220, 255)
SCORES_TITLE_COLOR = color.rgba32(225, 180, 80, 255)
SCORE_ENTRY_COLOR = color.rgba32(245, 235, 215, 255)
EMPTY_SCORE_COLOR = color.rgba32(150, 160, 145, 255)

PANEL_COLOR = color.rgba32(30, 45, 50, 150)
PANEL_BORDER = color.rgba32(225, 200, 160, 120)

BTN_W, BTN_H = 0.42, 0.085
BTN_SCALE = (BTN_W, BTN_H)
BTN_ASPECT = BTN_W / BTN_H
BORDER_PAD = 0.006
CORNER_RADIUS = 0.20
CORNER_SEGMENTS = 16
PANEL_RADIUS = 0.15
PANEL_BORDER_PAD = 0.008

DIFFICULTIES = [C.EDifficulty.EASY, C.EDifficulty.MEDIUM, C.EDifficulty.HARD]


def make_button(
    parent: Entity,
    text: str,
    y: float,
    x: float = 0,
    w: float | None = None,
    h: float | None = None,
    **kwargs,
) -> Button:
    bw = w if w is not None else BTN_W
    bh = h if h is not None else BTN_H
    btn_aspect = bw / bh
    brd_aspect = (bw + BORDER_PAD) / (bh + BORDER_PAD)
    border = Entity(
        model=Quad(
            radius=CORNER_RADIUS, segments=CORNER_SEGMENTS, aspect=brd_aspect
        ),
        color=BORDER,
        scale=(bw + BORDER_PAD, bh + BORDER_PAD),
        position=(x, y, 0.001),
        parent=parent,
    )
    border.setTransparency(TransparencyAttrib.MAlpha)

    btn_args = {
        "text": text,
        "model": Quad(
            radius=CORNER_RADIUS, segments=CORNER_SEGMENTS, aspect=btn_aspect
        ),
        "color": GLASS,
        "highlight_color": GLASS_HOVER,
        "pressed_color": GLASS_HOVER,
        "scale": (bw, bh),
        "x": x,
        "y": y,
        "parent": parent,
    }
    btn_args.update(kwargs)

    btn = Button(**btn_args)
    btn.setTransparency(TransparencyAttrib.MAlpha)
    btn.text_entity.color = TEXT_COLOR
    return btn


def make_panel(
    parent: Entity, x: float, y: float, w: float, h: float
) -> tuple:
    pnl_aspect = w / h if h > 0 else 1.0
    brd_aspect = (
        (w + PANEL_BORDER_PAD) / (h + PANEL_BORDER_PAD) if h > 0 else 1.0
    )
    border = Entity(
        model=Quad(radius=PANEL_RADIUS, segments=16, aspect=brd_aspect),
        color=PANEL_BORDER,
        scale=(w + PANEL_BORDER_PAD, h + PANEL_BORDER_PAD),
        position=(x, y, 0.02),
        parent=parent,
    )
    border.setTransparency(TransparencyAttrib.MAlpha)
    panel = Entity(
        model=Quad(radius=PANEL_RADIUS, segments=16, aspect=pnl_aspect),
        color=PANEL_COLOR,
        scale=(w, h),
        position=(x, y, 0.019),
        parent=parent,
    )
    panel.setTransparency(TransparencyAttrib.MAlpha)
    return border, panel


def make_section_divider(parent: Entity, y: float, label: str) -> None:
    """Centered label flanked by a horizontal rule and diamond accents."""
    Text(
        label,
        origin=(0, 0),
        x=0,
        y=y,
        scale=1.5,
        color=SCORES_TITLE_COLOR,
        parent=parent,
    )
    _INNER = 0.095
    _OUTER = 0.275
    _LINE_W = _OUTER - _INNER
    _LINE_CX = (_INNER + _OUTER) / 2
    _D_X = _OUTER + 0.014
    _D_SIZE = 0.013
    for sign in (-1, 1):
        line = Entity(
            model="quad",
            color=PANEL_BORDER,
            scale=(_LINE_W, 0.003),
            position=(sign * _LINE_CX, y, 0.001),
            parent=parent,
        )
        line.setTransparency(TransparencyAttrib.MAlpha)
        Entity(
            model="quad",
            color=SCORES_TITLE_COLOR,
            scale=(_D_SIZE, _D_SIZE),
            rotation_z=45,
            position=(sign * _D_X, y, 0.001),
            parent=parent,
        )


def make_outlined_text(
    parent: Entity,
    text: str,
    y: float,
    scale: float,
    fill: object,
    outline: object,
    thickness: float = 0.004,
    **kwargs,
) -> Text:
    offsets = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-0.7, -0.7),
        (0.7, -0.7),
        (-0.7, 0.7),
        (0.7, 0.7),
    ]

    text_args = {"origin": (0, 0), "parent": parent}
    text_args.update(kwargs)

    for dx, dy in offsets:
        Text(
            text,
            x=text_args.get("x", 0) + dx * thickness,
            y=y + dy * thickness,
            z=text_args.get("z", 0) - 0.001,
            scale=scale,
            color=outline,
            **{k: v for k, v in text_args.items() if k not in ["x", "z"]},
        )
    return Text(text, y=y, scale=scale, color=fill, **text_args)


def update_menu_highlight(elements: list, selected_index: int) -> None:
    from ursina import InputField

    for i, current in enumerate(elements):
        if hasattr(current, "text") and current.text == "Exit":
            current.color = (
                GLASS_EXIT_SELECTED if i == selected_index else GLASS
            )
        elif isinstance(current, InputField):
            if i == selected_index:
                current.color = color.black
                current.active = True
            else:
                current.active = False
                current.color = color.black
        elif hasattr(current, "color"):
            current.color = GLASS_SELECTED if i == selected_index else GLASS


def handle_menu_input(key: str, elements: list, selected_index: int) -> int:

    if key in ("down arrow", "tab"):
        selected_index = (selected_index + 1) % len(elements)
    elif key in ("up arrow", "shift+tab"):
        selected_index = (selected_index - 1) % len(elements)
    elif key == "enter":
        current = elements[selected_index]
        if hasattr(current, "on_click") and current.on_click:
            current.on_click()
    return selected_index
