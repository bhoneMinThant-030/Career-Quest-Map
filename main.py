import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
import os

from game_classes import *
import game_quizes as gq
from print_questions import generate_analysis, generate_gate_scene


GATE_SCENE_STATE = "gate_scene"
DRAGON_SCENE_STATE = "dragon_scene"
INFO_SCENE_STATE = "info_scene"
FINAL_SCENE_STATE = "final_scene"

can_enter_home = False
can_enter_wiseman = False
can_enter_exit_gate = False
can_enter_portal1 = False
can_enter_portal2 = False
can_enter_portal3 = False
can_enter_dragon_warrior = False
can_enter_info_hub = False
can_enter_post_info_gate = False

player_name = ""
player_education_status = "Secondary School"
player_poly_course = None
player_poly_path_choice = None

state = PROFILE
part1_ready = False
part1_done = False
part2_ready = False
chapter2_unlocked = False
show_analysis_overlay = False
analysis_overlay_seen = False

analysis_payload = {}
suggested_options = []
gate_payload_cache = {}
selected_gate_option = None
gate_scene_lines = []
gate_scene_i = 0
gate_yes_no_idx = 0
gate_dragon_saved = {}
active_portal_bg = None
gates_prefetched = False
path_committed = False
committed_path_option = None
dragon_scene_lines = []
dragon_scene_i = 0
dragon_met = False
info_pages = []
info_page_i = 0
info_hub_exited_once = False

DIALOG_PLAYER_POS = (130, 400)
DIALOG_PLAYER_SIZE = (150, 150)
audio_enabled = False
opening_audio_path = None
house_audio_path = None
wiseman_audio_path = None
chapter2_audio_path = None
portal_interior_audio_path = None
no_portal_audio_path = None
dw_audio_path = None
booth_audio_path = None
final_scene_audio_path = None
active_music_key = None

pygame.init()
try:
    pygame.mixer.init()
except Exception as audio_init_err:
    print(f"Audio disabled: {audio_init_err}")

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Career Quest Map")
font = pygame.font.SysFont("Arial", 32)

bg_img = pygame.image.load("images/background.png")
bg_img = pygame.transform.scale(bg_img, (GAME_WIDTH, GAME_HEIGHT))
chapter2_bg = pygame.image.load("images/chapter2_bg.png")
chapter2_bg = pygame.transform.scale(chapter2_bg, (GAME_WIDTH, GAME_HEIGHT))
chapter2_bg_removed_portal = pygame.image.load("images/chapter2_bg_removed_portal.png")
chapter2_bg_removed_portal = pygame.transform.scale(chapter2_bg_removed_portal, (GAME_WIDTH, GAME_HEIGHT))
first_scene_bg = pygame.image.load("images/FirstScene.png")
first_scene_bg = pygame.transform.scale(first_scene_bg, (GAME_WIDTH, GAME_HEIGHT))
dw_scene_bg = pygame.image.load("images/dwScene.png")
dw_scene_bg = pygame.transform.scale(dw_scene_bg, (GAME_WIDTH, GAME_HEIGHT))
quest_booth_interior_bg = pygame.image.load("images/questBoothInterior.png")
quest_booth_interior_bg = pygame.transform.scale(quest_booth_interior_bg, (GAME_WIDTH, GAME_HEIGHT))
final_scene_bg = pygame.image.load("images/FinalScene.png")
final_scene_bg = pygame.transform.scale(final_scene_bg, (GAME_WIDTH, GAME_HEIGHT))


def _resolve_opening_audio():
    candidates = [
        "openingSceneAudio.mp3",
        os.path.join("audio", "openingSceneAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _resolve_house_audio():
    candidates = [
        "houseAudio.mp3",
        os.path.join("audio", "houseAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _resolve_wiseman_audio():
    candidates = [
        "wiseManAudio.mp3",
        os.path.join("audio", "wiseManAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _resolve_chapter2_audio():
    candidates = [
        "seenPortalAudio.mp3",
        os.path.join("audio", "seenPortalAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _resolve_portal_interior_audio():
    candidates = [
        "portalInteriorAudio.mp3",
        os.path.join("audio", "portalInteriorAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _resolve_no_portal_audio():
    candidates = [
        "noPortalAudio.mp3",
        os.path.join("audio", "noPortalAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _resolve_dw_audio():
    candidates = [
        "dwAudio.mp3",
        os.path.join("audio", "dwAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _resolve_booth_audio():
    candidates = [
        "boothAudio.mp3",
        os.path.join("audio", "boothAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _resolve_final_scene_audio():
    candidates = [
        "finalSceneAudio.mp3",
        os.path.join("audio", "finalSceneAudio.mp3"),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def init_audio():
    global audio_enabled, opening_audio_path, house_audio_path, wiseman_audio_path, chapter2_audio_path, portal_interior_audio_path, no_portal_audio_path, dw_audio_path, booth_audio_path, final_scene_audio_path
    opening_audio_path = _resolve_opening_audio()
    house_audio_path = _resolve_house_audio()
    wiseman_audio_path = _resolve_wiseman_audio()
    chapter2_audio_path = _resolve_chapter2_audio()
    portal_interior_audio_path = _resolve_portal_interior_audio()
    no_portal_audio_path = _resolve_no_portal_audio()
    dw_audio_path = _resolve_dw_audio()
    booth_audio_path = _resolve_booth_audio()
    final_scene_audio_path = _resolve_final_scene_audio()
    if opening_audio_path is None:
        print("Audio file not found: openingSceneAudio.mp3")
    if house_audio_path is None:
        print("Audio file not found: houseAudio.mp3")
    if wiseman_audio_path is None:
        print("Audio file not found: wiseManAudio.mp3")
    if chapter2_audio_path is None:
        print("Audio file not found: seenPortalAudio.mp3")
    if portal_interior_audio_path is None:
        print("Audio file not found: portalInteriorAudio.mp3")
    if no_portal_audio_path is None:
        print("Audio file not found: noPortalAudio.mp3")
    if dw_audio_path is None:
        print("Audio file not found: dwAudio.mp3")
    if booth_audio_path is None:
        print("Audio file not found: boothAudio.mp3")
    if final_scene_audio_path is None:
        print("Audio file not found: finalSceneAudio.mp3")
    if opening_audio_path is None and house_audio_path is None and wiseman_audio_path is None and chapter2_audio_path is None and portal_interior_audio_path is None and no_portal_audio_path is None and dw_audio_path is None and booth_audio_path is None and final_scene_audio_path is None:
        audio_enabled = False
        return
    try:
        pygame.mixer.music.set_volume(1.0)
        audio_enabled = True
    except Exception as audio_err:
        print(f"Audio disabled: {audio_err}")
        audio_enabled = False


def set_background_music(music_key):
    global active_music_key
    if not audio_enabled:
        return
    if music_key == active_music_key:
        return
    try:
        if music_key == "opening":
            if opening_audio_path is None:
                return
            pygame.mixer.music.load(opening_audio_path)
            pygame.mixer.music.play(-1)
        elif music_key == "house":
            if house_audio_path is None:
                return
            pygame.mixer.music.load(house_audio_path)
            pygame.mixer.music.play(-1)
        elif music_key == "wiseman":
            if wiseman_audio_path is None:
                return
            pygame.mixer.music.load(wiseman_audio_path)
            pygame.mixer.music.play(-1)
        elif music_key == "chapter2":
            if chapter2_audio_path is None:
                return
            pygame.mixer.music.load(chapter2_audio_path)
            pygame.mixer.music.play(-1)
        elif music_key == "portal_interior":
            if portal_interior_audio_path is None:
                return
            pygame.mixer.music.load(portal_interior_audio_path)
            pygame.mixer.music.play(-1)
        elif music_key == "chapter2_no_portal":
            if no_portal_audio_path is None:
                return
            pygame.mixer.music.load(no_portal_audio_path)
            pygame.mixer.music.play(-1)
        elif music_key == "dw":
            if dw_audio_path is None:
                return
            pygame.mixer.music.load(dw_audio_path)
            pygame.mixer.music.play(-1)
        elif music_key == "booth":
            if booth_audio_path is None:
                return
            pygame.mixer.music.load(booth_audio_path)
            pygame.mixer.music.play(-1)
        elif music_key == "final_scene":
            if final_scene_audio_path is None:
                return
            pygame.mixer.music.load(final_scene_audio_path)
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()
        active_music_key = music_key
    except Exception as music_err:
        print(f"Music playback error: {music_err}")
        active_music_key = None


init_audio()


def _load_preferred_font(candidates, size, italic=False):
    for name in candidates:
        font_path = pygame.font.match_font(name, italic=italic)
        if font_path:
            return pygame.font.Font(font_path, size)
    # Serif fallback if preferred fonts are unavailable.
    fallback = "Times New Roman"
    return pygame.font.SysFont(fallback, size, italic=italic)

profile_name_box = TextBox(
    screen,
    300,
    165,
    420,
    45,
    fontSize=30,
    borderColour=WHITE,
    textColour=BLACK,
    boxColour=WHITE,
    placeholderText="Enter your name...",
    radius=6,
    borderThickness=2,
)
profile_name_box.active = True

profile_poly_course_box = TextBox(
    screen,
    300,
    350,
    420,
    45,
    fontSize=30,
    borderColour=WHITE,
    textColour=BLACK,
    boxColour=WHITE,
    placeholderText="e.g. IT, Engineering, Business",
    radius=6,
    borderThickness=2,
)
profile_poly_course_box.active = False

education_options = ["Secondary", "JC", "Poly"]
education_selected_idx = 0
education_rects = [
    pygame.Rect(300, 245, 20, 20),
    pygame.Rect(300, 285, 20, 20),
    pygame.Rect(300, 325, 20, 20),
]

clock = pygame.time.Clock()

main_player = Player(x=GAME_WIDTH // 2, y=GAME_HEIGHT // 2, width=50, height=50, img_path="images/warrior/", speed=100)
fedora = Player(x=GAME_WIDTH - 400, y=GAME_HEIGHT - 200, width=100, height=100, img_path="images/fedora/", speed=80)
wiseman = Player(x=GAME_WIDTH - 400, y=GAME_HEIGHT - 200, width=100, height=100, img_path="images/wiseman/", speed=80)
dragon_warrior = Player(x=GAME_WIDTH - 500, y=GAME_HEIGHT - 280, width=150, height=150, img_path="images/dragonWarrior/", speed=0)
aung_gyi = Player(x=GAME_WIDTH - 500, y=GAME_HEIGHT - 280, width=100, height=100, img_path="images/aungGyi/", speed=0)

home = Structure(GAME_WIDTH - 300, GAME_HEIGHT - 585, 150, 150, "images/house.png", "images/home_bg.png")
wiseman_tent = Structure(GAME_WIDTH - 220, GAME_HEIGHT - 210, 65, 65, "images/wiseman/west.png", "images/TreeScene.png")
exit_gate1 = Structure(GAME_WIDTH - 388, GAME_HEIGHT - 115, 60, 60, "images/gate.png", "images/home_bg.png")
portal1 = Structure(GAME_WIDTH - 572, GAME_HEIGHT - 480, 65, 80, "images/1stGate.png", "images/innerG1.png")
portal2 = Structure(GAME_WIDTH - 472, GAME_HEIGHT - 480, 30, 80, "images/2ndGate.png", "images/innerG2.png")
portal3 = Structure(GAME_WIDTH - 410, GAME_HEIGHT - 480, 30, 80, "images/3rdGate.png", "images/innerG3.png")
info_hub = Structure(GAME_WIDTH - 220, GAME_HEIGHT - 350, 100, 100, "images/questBooth.png", "images/home_bg.png")
post_info_exit_gate = Structure(GAME_WIDTH - 470, GAME_HEIGHT - 80, 70, 70, "images/gate.png", "images/home_bg.png")

WISEMAN_RETURN_SPAWN = (620, 390)

# Static map blockers (manual rectangles). Add/adjust these over time.
# Example: pygame.Rect(x, y, width, height)
OUTSIDE_BLOCKED_RECTS = [
    pygame.Rect(0, 0, 480, 150),
    pygame.Rect(0, 150, 150, 100),
    pygame.Rect(150, 150, 130, 50),
    pygame.Rect(250, 200, 140, 40),
    pygame.Rect(440, 150, 50, 50),
    pygame.Rect(500, 200, 30, 20),
    pygame.Rect(600, 220, 250, 100),
    pygame.Rect(570, 320, 250, 10),

    pygame.Rect(0, 320, 150, 100),
    pygame.Rect(150, 350, 80, 100),
    pygame.Rect(230, 320, 50, 200),

    pygame.Rect(280, 320, 100, 50),
    #pygame.Rect(375, 300, 30, 10),
    pygame.Rect(410, 340, 10, 20),
    pygame.Rect(280, 460, 220, 200),
    pygame.Rect(480, 320, 5, 5),

    pygame.Rect(280, 460, 220, 200),
    pygame.Rect(600, 480, 50, 100),
    pygame.Rect(650, 510, 180, 50),
    pygame.Rect(750, 310, 80, 200),
]

CHAPTER2_BLOCKED_RECTS = [
    pygame.Rect(0, 0, GAME_WIDTH, 180),
    pygame.Rect(0, 150, 300, 100),
    pygame.Rect(300, 150, 100, 120),
    pygame.Rect(530, 210, 100, 50),
    
    pygame.Rect(0, 330, 410, 300),
    pygame.Rect(490, 330, 380, 250),

    pygame.Rect(780, 180, 50, 150)
]
blocked_rects_by_state = {
    OUTSIDE: OUTSIDE_BLOCKED_RECTS,
    CHAPTER2: CHAPTER2_BLOCKED_RECTS,
}
SHOW_COLLISION_DEBUG = False

def _spawn_near(rect, dx=0, dy=70):
    x = rect.centerx + dx
    y = rect.bottom + dy
    x = max(0, min(GAME_WIDTH - main_player.rect.width, x))
    y = max(0, min(GAME_HEIGHT - main_player.rect.height, y))
    return (x, y)


HOME_EXIT_SPAWN = _spawn_near(home.rect, dx=-180, dy=-50)
WISEMAN_EXIT_SPAWN = _spawn_near(wiseman_tent.rect, dx=-110, dy=-40)
CH1_GATE_EXIT_SPAWN = _spawn_near(exit_gate1.rect, dx=-40, dy=10)
PORTAL_EXIT_SPAWNS = {
    0: _spawn_near(portal1.rect, dx=60, dy=60),
    1: _spawn_near(portal2.rect, dx=-15, dy=60),
    2: _spawn_near(portal3.rect, dx=-70, dy=60),
}
DRAGON_EXIT_SPAWN = _spawn_near(dragon_warrior.rect, dx=-60, dy=20)
INFO_HUB_EXIT_SPAWN = _spawn_near(info_hub.rect, dx=-100, dy=-85)


def loading_screen(title, bg=None):
    if bg is not None:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(BLACK)

    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 110))
    screen.blit(overlay, (0, 0))

    # Chapters use a decorative serif; story quotes use italic serif.
    is_chapter_title = str(title).strip().lower().startswith("chapter")
    loading_font = _load_preferred_font(
        candidates=["Mantinia Regular", "Mantinia", "Cinzel", "Garamond", "Georgia"],
        size=32,
        italic=False,
    ) if is_chapter_title else _load_preferred_font(
        candidates=["Agmena", "Alegreya", "Palatino Linotype", "Georgia", "Garamond"],
        size=32,
        italic=True,
    )

    text_lines = wrap_text(title, GAME_WIDTH - 240, loading_font)
    if not text_lines:
        text_lines = [str(title)]

    start_x = 120
    start_y = 260
    line_gap = 44
    for i, line in enumerate(text_lines):
        txt = loading_font.render(line, True, WHITE)
        screen.blit(txt, (start_x, start_y + i * line_gap))
    pygame.display.flip()


def map_education_for_engine(choice):
    if choice == "Secondary":
        return "Secondary School"
    if choice == "JC":
        return "JC"
    return "Poly"


def wrap_text(text, max_width, local_font):
    words = str(text).split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if local_font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def set_state(new_state, spawn_pos=None, title=None, facing=None, loading_ms=0):
    global state, show_analysis_overlay
    state = new_state
    if new_state == CHAPTER2 and analysis_payload and not analysis_overlay_seen:
        show_analysis_overlay = True
    if spawn_pos is not None:
        main_player.rect.topleft = spawn_pos
    if facing == "up":
        main_player.img = main_player.img_up
    elif facing == "down":
        main_player.img = main_player.img_down
    elif facing == "left":
        main_player.img = main_player.img_left
    elif facing == "right":
        main_player.img = main_player.img_right
    if title:
        bg = None
        if new_state == OUTSIDE:
            bg = bg_img
        elif new_state == HOME:
            bg = home.bg
        elif new_state == WISEMAN:
            bg = wiseman_tent.bg
        elif new_state == CHAPTER2:
            bg = chapter2_bg_removed_portal if path_committed else chapter2_bg
        elif new_state in (GATE_SCENE_STATE, DRAGON_SCENE_STATE, INFO_SCENE_STATE):
            bg = active_portal_bg if active_portal_bg is not None else home.bg
        loading_screen(title, bg=bg)
        if loading_ms and loading_ms > 0:
            pygame.time.delay(int(loading_ms))


def get_portal_option(index):
    if index < len(suggested_options):
        return str(suggested_options[index])
    return f"Option {index + 1}"


def _get_player_label():
    name = str(player_name).strip()
    return name if name else "Player"


def draw_name_tag(surface, text, center_x, top_y, max_width=None, font_size=20):
    tag_font = pygame.font.SysFont("Arial", font_size, bold=True)
    raw_text = str(text)
    lines = wrap_text(raw_text, max_width, tag_font) if max_width else [raw_text]
    if not lines:
        lines = [raw_text]
    rendered = [tag_font.render(line, True, WHITE) for line in lines]
    pad_x, pad_y = 10, 5
    box_w = max(t.get_width() for t in rendered) + pad_x * 2
    box_h = sum(t.get_height() for t in rendered) + (len(rendered) - 1) * 4 + pad_y * 2
    x = int(center_x - box_w // 2)
    y = int(top_y - box_h - 6)
    x = max(8, min(GAME_WIDTH - box_w - 8, x))
    y = max(8, y)
    panel = pygame.Rect(x, y, box_w, box_h)
    pygame.draw.rect(surface, (0, 0, 0, 170), panel, border_radius=8)
    pygame.draw.rect(surface, WHITE, panel, 2, border_radius=8)
    ty = panel.y + pad_y
    for txt in rendered:
        surface.blit(txt, (panel.x + (box_w - txt.get_width()) // 2, ty))
        ty += txt.get_height() + 4


def draw_main_player(surface):
    main_player.draw(surface)
    draw_name_tag(surface, _get_player_label(), main_player.rect.centerx, main_player.rect.y)


def draw_main_player_dialog(surface, pos=DIALOG_PLAYER_POS, size=DIALOG_PLAYER_SIZE):
    sprite = pygame.transform.scale(main_player.img_right, size)
    surface.blit(sprite, pos)


def draw_structure_label(surface, structure, text):
    label_text = str(text)
    max_width = 85 if structure in (portal1, portal2, portal3) else None
    font_size = 15 if structure in (portal1, portal2, portal3) else 20

    cx = structure.rect.centerx
    top_y = structure.rect.y
    if structure == portal1:
        cx -= 58
        top_y -= 8
    elif structure == portal2:
        top_y -= 55
    elif structure == portal3:
        cx += 58
        top_y -= 8

    draw_name_tag(surface, label_text, cx, top_y, max_width=max_width, font_size=font_size)


def draw_enter_prompt(surface, target_rect, text="Press E to Enter"):
    prompt_font = pygame.font.SysFont("Arial", 20, bold=True)
    label = prompt_font.render(text, True, WHITE)
    pad_x, pad_y = 10, 6
    box_w = label.get_width() + pad_x * 2
    box_h = label.get_height() + pad_y * 2
    x = target_rect.centerx - box_w // 2
    y = target_rect.centery - box_h // 2
    x = max(8, min(GAME_WIDTH - box_w - 8, x))
    y = max(8, y)
    panel = pygame.Rect(x, y, box_w, box_h)
    pygame.draw.rect(surface, (0, 0, 0, 185), panel, border_radius=10)
    pygame.draw.rect(surface, WHITE, panel, 2, border_radius=10)
    surface.blit(label, (panel.x + pad_x, panel.y + pad_y))


def draw_chapter2_labels():
    label_font = pygame.font.SysFont("Arial", 20)
    if path_committed:
        t1 = label_font.render(f"Chosen Path: {committed_path_option or 'Unknown'}", True, WHITE)
        t2 = label_font.render("Dragon Warrior has appeared.", True, WHITE)
        t3 = label_font.render("Approach Dragon Warrior and press E for your quest.", True, WHITE)
        screen.blit(t1, (40, 24))
        screen.blit(t2, (40, 48))
        screen.blit(t3, (40, 72))
        if dragon_met:
            t4 = label_font.render("Enter the house icon to review your path.", True, WHITE)
            screen.blit(t4, (40, 96))
        return

    hint_font = pygame.font.SysFont("Arial", 22)
    hint = hint_font.render("Move to a portal and press E to enter | Q to return outside", True, WHITE)
    screen.blit(hint, (40, 560))


def render_analysis_overlay():
    panel = pygame.Rect(55, 45, 790, 510)
    shade = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 140))
    screen.blit(shade, (0, 0))
    pygame.draw.rect(screen, (15, 15, 30), panel, border_radius=16)
    pygame.draw.rect(screen, WHITE, panel, 3, border_radius=16)

    title_font = pygame.font.SysFont("Arial", 30)
    body_font = pygame.font.SysFont("Arial", 22)
    screen.blit(title_font.render("Wise Man Analysis", True, (255, 220, 120)), (panel.x + 20, panel.y + 18))

    y = panel.y + 70
    max_width = panel.width - 40

    def draw_section(label, values):
        nonlocal y
        if y > panel.bottom - 70:
            return
        screen.blit(body_font.render(label, True, (180, 220, 255)), (panel.x + 20, y))
        y += 28
        for item in values:
            for ln in wrap_text(f"- {item}", max_width, body_font):
                if y > panel.bottom - 70:
                    return
                screen.blit(body_font.render(ln, True, WHITE), (panel.x + 26, y))
                y += 24
        y += 6

    draw_section("Strength Tags", [str(x) for x in analysis_payload.get("strength_tags", [])] if isinstance(analysis_payload.get("strength_tags"), list) else [])
    draw_section("Work Style Tags", [str(x) for x in analysis_payload.get("work_style_tags", [])] if isinstance(analysis_payload.get("work_style_tags"), list) else [])
    draw_section("Feedback", [str(x) for x in analysis_payload.get("feedback_lines", [])] if isinstance(analysis_payload.get("feedback_lines"), list) else [])

    hint = body_font.render("Press Enter or Space to continue", True, (210, 210, 210))
    screen.blit(hint, (panel.x + 20, panel.bottom - 36))

def build_gate_scene_lines(option_name, payload):
    lines = [f"You chose {option_name}. Listen closely."]
    info_lines = payload.get("info_dialog_lines", [])
    if isinstance(info_lines, list):
        for ln in info_lines:
            lines.append(str(ln))
    work_style = payload.get("work_style_line")
    if isinstance(work_style, str) and work_style.strip():
        lines.append(f"Work style in this path is {work_style}")
    salary = payload.get("salary_outlook_line")
    if isinstance(salary, str) and salary.strip():
        lines.append(f"Salary outlook: {salary}")
    lines.append("Do you want to proceed with the Dragon Path?")
    return lines


def build_dragon_scene_lines(option_name, dragon_payload):
    lines = [f"You chose {option_name}. Your training begins now."]
    if isinstance(dragon_payload, dict):
        mq = dragon_payload.get("micro_quest_1_week")
        mp = dragon_payload.get("mini_project_1_month")
        if isinstance(mq, str) and mq.strip():
            lines.append("Your one-week micro quest:")
            lines.append(f"{mq}")
        if isinstance(mp, str) and mp.strip():
            lines.append("Your one-month mini project:")
            lines.append(f"{mp}")
        resources = dragon_payload.get("resources", [])
        if isinstance(resources, list) and resources:
            lines.append("Gather these resources:")
            for r in resources:
                lines.append(f"- {str(r)}")
    lines.append("Return to the map and keep training.")
    return lines


def _str_list(value):
    return [str(v) for v in value] if isinstance(value, list) else []


def build_info_pages():
    pages = []
    strength = _str_list(analysis_payload.get("strength_tags", []))
    if strength:
        pages.append(("Strength", strength))
    work_style = _str_list(analysis_payload.get("work_style_tags", []))
    if work_style:
        pages.append(("Work Style", work_style))
    feedback = _str_list(analysis_payload.get("feedback_lines", []))
    if feedback:
        pages.append(("Feedback", feedback))

    dragon_payload = gate_dragon_saved.get(committed_path_option, {})
    if isinstance(dragon_payload, dict):
        quests = []
        mq = dragon_payload.get("micro_quest_1_week")
        mp = dragon_payload.get("mini_project_1_month")
        if isinstance(mq, str) and mq.strip():
            quests.append(f"Micro Quest: {mq}")
        if isinstance(mp, str) and mp.strip():
            quests.append(f"Mini Project: {mp}")
        if quests:
            pages.append(("Quests", quests))
        resources = _str_list(dragon_payload.get("resources", []))
        if resources:
            pages.append(("Resources", resources))

    if not pages:
        pages.append(("Info", ["No data available yet."]))
    return pages


def _strip_speaker_prefix(text):
    s = str(text)
    prefixes = ("Wise Man:", "Dragon Warrior:", "The Sage:", "Player:")
    for p in prefixes:
        if s.strip().startswith(p):
            return s.strip()[len(p):].strip()
    return s


def render_gate_scene():
    bg = active_portal_bg if active_portal_bg is not None else home.bg
    screen.blit(bg, (0, 0))
    box_rect = pygame.Rect(40, 50, 720, 330)
    gq.draw_dialog_box(screen, box_rect, fill_color=(10, 10, 10), alpha=210, border_color=(255, 255, 255))

    title_font = pygame.font.SysFont("Arial", 28)
    prompt_font = pygame.font.SysFont("Arial", 28)
    hint_font = pygame.font.SysFont("Arial", 24)
    screen.blit(title_font.render("The Sage:", True, WHITE), (box_rect.x + 20, box_rect.y + 15))

    y = box_rect.y + 60
    at_last = gate_scene_i >= max(0, len(gate_scene_lines) - 1)
    if at_last:
        current = gate_scene_lines[min(gate_scene_i, len(gate_scene_lines) - 1)] if gate_scene_lines else "Proceed?"
        current = _strip_speaker_prefix(current)
        for ln in wrap_text(current, box_rect.width - 40, prompt_font)[:3]:
            screen.blit(prompt_font.render(ln, True, (230, 230, 230)), (box_rect.x + 20, y))
            y += 36
        yes_rect = pygame.Rect(box_rect.x + 20, y + 8, 140, 48)
        no_rect = pygame.Rect(box_rect.x + 190, y + 8, 140, 48)
        pygame.draw.rect(screen, (70, 90, 70) if gate_yes_no_idx == 0 else (45, 45, 45), yes_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, yes_rect, 2, border_radius=10)
        pygame.draw.rect(screen, (90, 65, 65) if gate_yes_no_idx == 1 else (45, 45, 45), no_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, no_rect, 2, border_radius=10)
        yes_txt = prompt_font.render("Yes", True, WHITE)
        no_txt = prompt_font.render("No", True, WHITE)
        screen.blit(yes_txt, (yes_rect.centerx - yes_txt.get_width() // 2, yes_rect.y + 8))
        screen.blit(no_txt, (no_rect.centerx - no_txt.get_width() // 2, no_rect.y + 8))
    else:
        current = gate_scene_lines[min(gate_scene_i, len(gate_scene_lines) - 1)] if gate_scene_lines else "I have no guidance for this gate yet."
        current = _strip_speaker_prefix(current)
        for ln in wrap_text(current, box_rect.width - 40, prompt_font)[:6]:
            screen.blit(prompt_font.render(ln, True, (230, 230, 230)), (box_rect.x + 20, y))
            y += 32

    draw_main_player_dialog(screen)
    screen.blit(pygame.transform.scale(aung_gyi.img_left, (200, 200)), (500, 380))

    if at_last:
        hint_text = "Left/Right choose Yes/No | Enter confirm | Q back to gates"
    elif gate_scene_i < max(0, len(gate_scene_lines) - 1):
        hint_text = "Left/Right back/next line | Q back to gates"
    else:
        hint_text = "Left/Right review lines | Q back to gates"
    screen.blit(hint_font.render(hint_text, True, (180, 180, 180)), (box_rect.x + 20, box_rect.bottom + 170))


def render_dragon_scene():
    bg = dw_scene_bg
    screen.blit(bg, (0, 0))
    box_rect = pygame.Rect(40, 50, 720, 330)
    gq.draw_dialog_box(screen, box_rect, fill_color=(10, 10, 10), alpha=210, border_color=(255, 255, 255))

    title_font = pygame.font.SysFont("Arial", 28)
    prompt_font = pygame.font.SysFont("Arial", 28)
    hint_font = pygame.font.SysFont("Arial", 24)
    screen.blit(title_font.render("Dragon Warrior:", True, WHITE), (box_rect.x + 20, box_rect.y + 15))

    current = dragon_scene_lines[min(dragon_scene_i, len(dragon_scene_lines) - 1)] if dragon_scene_lines else "I await your chosen path."
    current = _strip_speaker_prefix(current)
    y = box_rect.y + 60
    for ln in wrap_text(current, box_rect.width - 40, prompt_font)[:6]:
        screen.blit(prompt_font.render(ln, True, (230, 230, 230)), (box_rect.x + 20, y))
        y += 32

    draw_main_player_dialog(screen)
    screen.blit(pygame.transform.scale(dragon_warrior.img_left, (300, 300)), (500, 280))

    hint_text = "Left/Right back/next line | Q back to map" if dragon_scene_i < max(0, len(dragon_scene_lines) - 1) else "Left/Right review lines | Q back to map"
    screen.blit(hint_font.render(hint_text, True, (180, 180, 180)), (box_rect.x + 20, box_rect.bottom + 170))


def render_info_scene():
    bg = quest_booth_interior_bg
    screen.blit(bg, (0, 0))
    box_rect = pygame.Rect(40, 50, 720, 330)
    gq.draw_dialog_box(screen, box_rect, fill_color=(10, 10, 10), alpha=210, border_color=(255, 255, 255))

    title_font = pygame.font.SysFont("Arial", 30)
    body_font = pygame.font.SysFont("Arial", 26)
    hint_font = pygame.font.SysFont("Arial", 24)

    page_title, page_lines = info_pages[min(info_page_i, len(info_pages) - 1)]
    screen.blit(title_font.render(page_title, True, (255, 220, 120)), (box_rect.x + 20, box_rect.y + 18))

    y = box_rect.y + 70
    for line in page_lines:
        wrapped = wrap_text(line, box_rect.width - 40, body_font)
        for idx, ln in enumerate(wrapped):
            if y > box_rect.bottom - 25:
                break
            text = f"- {ln}" if idx == 0 else ln
            screen.blit(body_font.render(text, True, (230, 230, 230)), (box_rect.x + 20, y))
            y += 30
        if y > box_rect.bottom - 25:
            break

    draw_main_player_dialog(screen)

    screen.blit(hint_font.render(f"Page {info_page_i + 1}/{len(info_pages)}", True, (200, 200, 200)), (box_rect.x + 20, box_rect.bottom + 140))
    screen.blit(hint_font.render("Left/Right change section | Q back to map", True, (180, 180, 180)), (box_rect.x + 20, box_rect.bottom + 170))

def render_outside_quest_hint():
    hint_font = pygame.font.SysFont("Arial", 24)
    if not part1_done:
        msg = "Quest: Find the House on the Map"
    elif not chapter2_unlocked:
        msg = "Quest: Meet the Wise Man"
    else:
        msg = "Quest: Exit to Chapter II"
    screen.blit(hint_font.render(msg, True, (255, 245, 170)), (24, 24))


def render_state():
    if state == OUTSIDE:
        screen.blit(bg_img, (0, 0))
        home.draw(screen)
        draw_structure_label(screen, home, "The House")
        if part1_done:
            wiseman_tent.draw(screen)
            draw_structure_label(screen, wiseman_tent, "The Wise Man")
        if chapter2_unlocked:
            exit_gate1.draw(screen)
            draw_structure_label(screen, exit_gate1, "Exit Gate")
        if can_enter_home:
            draw_enter_prompt(screen, home.rect)
        elif can_enter_wiseman:
            draw_enter_prompt(screen, wiseman_tent.rect)
        elif can_enter_exit_gate:
            draw_enter_prompt(screen, exit_gate1.rect)
        if SHOW_COLLISION_DEBUG:
            draw_blocked_rects_debug()
        render_outside_quest_hint()
        draw_main_player(screen)
        return

    if state == HOME:
        if gq.quiz_i < len(gq.quiz_questions_home):
            gq.draw_quiz_screen(screen, font, home.bg, gq.quiz_questions_home[gq.quiz_i], npc_name="Fedora")
            draw_main_player_dialog(screen)
            screen.blit(pygame.transform.scale(fedora.img_left, (200, 200)), (500, 380))
        return

    if state == WISEMAN:
        if gq.quiz_i < len(gq.quiz_questions_wiseman):
            gq.draw_quiz_screen(screen, font, wiseman_tent.bg, gq.quiz_questions_wiseman[gq.quiz_i], npc_name="The Wise Man")
            draw_main_player_dialog(screen)
            screen.blit(pygame.transform.scale(wiseman.img_left, (200, 200)), (500, 380))
        return

    if state == CHAPTER2:
        screen.blit(chapter2_bg_removed_portal if path_committed else chapter2_bg, (0, 0))
        if not path_committed:
            portal1.draw(screen)
            portal2.draw(screen)
            portal3.draw(screen)
            draw_structure_label(screen, portal1, get_portal_option(0))
            draw_structure_label(screen, portal2, get_portal_option(1))
            draw_structure_label(screen, portal3, get_portal_option(2))
            if can_enter_portal1:
                draw_enter_prompt(screen, portal1.rect)
            elif can_enter_portal2:
                draw_enter_prompt(screen, portal2.rect)
            elif can_enter_portal3:
                draw_enter_prompt(screen, portal3.rect)
        else:
            dragon_warrior.draw(screen)
            draw_structure_label(screen, dragon_warrior, "Dragon Warrior")
            if dragon_met:
                info_hub.draw(screen)
                draw_structure_label(screen, info_hub, "Info Hub")
            if info_hub_exited_once:
                post_info_exit_gate.draw(screen)
                draw_structure_label(screen, post_info_exit_gate, "Exit Gate")
            if can_enter_post_info_gate:
                draw_enter_prompt(screen, post_info_exit_gate.rect)
            elif can_enter_info_hub:
                draw_enter_prompt(screen, info_hub.rect)
            elif can_enter_dragon_warrior:
                draw_enter_prompt(screen, dragon_warrior.rect)
        if SHOW_COLLISION_DEBUG:
            draw_blocked_rects_debug()
        draw_chapter2_labels()
        draw_main_player(screen)
        if show_analysis_overlay:
            render_analysis_overlay()
        return

    if state == GATE_SCENE_STATE:
        render_gate_scene()
        return

    if state == DRAGON_SCENE_STATE:
        render_dragon_scene()
        return

    if state == INFO_SCENE_STATE:
        render_info_scene()
        return

    if state == FINAL_SCENE_STATE:
        screen.blit(final_scene_bg, (0, 0))
        shade = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 70))
        screen.blit(shade, (0, 0))
        end_font = pygame.font.SysFont("Arial", 30, bold=True)
        hint_font = pygame.font.SysFont("Arial", 24)
        msg = end_font.render("Victory! Your journey is complete.", True, WHITE)
        hint = hint_font.render("Press Q or ESC to quit.", True, WHITE)
        screen.blit(msg, (GAME_WIDTH // 2 - msg.get_width() // 2, 40))
        screen.blit(hint, (GAME_WIDTH // 2 - hint.get_width() // 2, 78))
        return

    if state == PROFILE:
        screen.blit(first_scene_bg, (0, 0))
        shade = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 120))
        screen.blit(shade, (0, 0))
        screen.blit(font.render("Create Your Profile", True, WHITE), (240, 70))
        screen.blit(font.render("Name:", True, WHITE), (140, 170))
        profile_name_box.draw()
        screen.blit(font.render("Education:", True, WHITE), (140, 240))

        small_font = pygame.font.SysFont("Arial", 24)
        for i, opt in enumerate(education_options):
            r = education_rects[i]
            pygame.draw.rect(screen, WHITE, r, 2)
            if i == education_selected_idx:
                pygame.draw.rect(screen, WHITE, r.inflate(-8, -8))
            screen.blit(small_font.render(opt, True, WHITE), (r.x + 35, r.y - 4))

        if education_options[education_selected_idx] == "Poly":
            screen.blit(font.render("Course:", True, WHITE), (140, 350))
            profile_poly_course_box.draw()

        hint = small_font.render("Enter = confirm | Click education | Tab to change textbox focus", True, (180, 180, 180))
        screen.blit(hint, (90, 540))


def update_outside_interactions():
    global can_enter_home, can_enter_wiseman, can_enter_exit_gate
    can_enter_home = main_player.rect.colliderect(home.rect.inflate(40, 40))
    can_enter_wiseman = part1_done and main_player.rect.colliderect(wiseman_tent.rect.inflate(40, 40))
    can_enter_exit_gate = chapter2_unlocked and main_player.rect.colliderect(exit_gate1.rect.inflate(40, 40))


def update_chapter2_interactions():
    global can_enter_portal1, can_enter_portal2, can_enter_portal3, can_enter_dragon_warrior, can_enter_info_hub, can_enter_post_info_gate
    if path_committed:
        can_enter_portal1 = False
        can_enter_portal2 = False
        can_enter_portal3 = False
        can_enter_dragon_warrior = main_player.rect.colliderect(dragon_warrior.rect.inflate(30, 30))
        can_enter_info_hub = dragon_met and main_player.rect.colliderect(info_hub.rect.inflate(40, 40))
        can_enter_post_info_gate = info_hub_exited_once and main_player.rect.colliderect(post_info_exit_gate.rect.inflate(50, 50))
        return
    can_enter_portal1 = main_player.rect.colliderect(portal1.rect.inflate(40, 40))
    can_enter_portal2 = main_player.rect.colliderect(portal2.rect.inflate(40, 40))
    can_enter_portal3 = main_player.rect.colliderect(portal3.rect.inflate(40, 40))
    can_enter_dragon_warrior = False
    can_enter_info_hub = False
    can_enter_post_info_gate = False


def get_blocked_rects_for_state():
    blocked = list(blocked_rects_by_state.get(state, []))

    # Dynamic blockers based on progression/scene.
    if state == OUTSIDE:
        blocked.append(home.rect)
        if part1_done:
            blocked.append(wiseman_tent.rect)
    elif state == CHAPTER2:
        if not path_committed:
            blocked.extend([portal1.rect, portal2.rect, portal3.rect])
        else:
            if dragon_met:
                blocked.append(info_hub.rect)
            if info_hub_exited_once:
                blocked.append(post_info_exit_gate.rect)
    return blocked


def resolve_world_collision(prev_pos):
    for rect in get_blocked_rects_for_state():
        if main_player.rect.colliderect(rect):
            main_player.rect.topleft = prev_pos
            break


def draw_blocked_rects_debug():
    # Static blockers from manual state lists
    for r in blocked_rects_by_state.get(state, []):
        pygame.draw.rect(screen, (255, 80, 80), r, 2)  # red

    # Dynamic blockers added by progression/state
    if state == OUTSIDE:
        pygame.draw.rect(screen, (80, 180, 255), home.rect, 2)  # blue
        if part1_done:
            pygame.draw.rect(screen, (80, 180, 255), wiseman_tent.rect, 2)
        if chapter2_unlocked:
            pygame.draw.rect(screen, (80, 180, 255), exit_gate1.rect, 2)
    elif state == CHAPTER2:
        if not path_committed:
            pygame.draw.rect(screen, (80, 180, 255), portal1.rect, 2)
            pygame.draw.rect(screen, (80, 180, 255), portal2.rect, 2)
            pygame.draw.rect(screen, (80, 180, 255), portal3.rect, 2)
        elif dragon_met:
            pygame.draw.rect(screen, (80, 180, 255), info_hub.rect, 2)
            if info_hub_exited_once:
                pygame.draw.rect(screen, (80, 180, 255), post_info_exit_gate.rect, 2)


def prefetch_all_gate_scenes():
    global gate_payload_cache, gates_prefetched
    if gates_prefetched:
        return
    loading_screen("Chapter II : The Sacred Portals", bg=chapter2_bg)
    work_path = bool(player_education_status == "Poly" and player_poly_path_choice == "Work")
    for option in suggested_options:
        key = str(option)
        if key in gate_payload_cache:
            continue
        try:
            payload = generate_gate_scene(
                option_name=key,
                work_path=work_path,
                education_status=player_education_status,
                poly_path_choice=player_poly_path_choice,
            )
            if isinstance(payload, dict):
                gate_payload_cache[key] = payload
        except Exception as gate_err:
            print(f"Prefetch gate scene failed for '{key}': {gate_err}")
    gates_prefetched = True


def handle_keydown_ch1(event):
    if event.key != pygame.K_e:
        return
    if can_enter_home:
        if not part1_ready:
            print("Part 1 is not ready yet.")
            return
        set_state(HOME, HOME_SPAWN, "Entering Home")
        return
    if can_enter_wiseman:
        if not part1_done:
            print("Complete Part 1 at Home first.")
            return
        if not part2_ready:
            print("Part 2 is not ready yet.")
            return
        set_state(WISEMAN, HOME_SPAWN, "Meeting Wise Man")
        return
    if can_enter_exit_gate:
        if not chapter2_unlocked:
            print("Finish Wise Man path first.")
            return
        set_state(CHAPTER2, (20, 260), "Chapter 2: The Portals", facing="right", loading_ms=3000)


def handle_chapter2_enter():
    global selected_gate_option, gate_scene_lines, gate_scene_i, gate_yes_no_idx, active_portal_bg
    if can_enter_portal1:
        selected_gate_option = get_portal_option(0)
        active_portal_bg = portal1.bg
    elif can_enter_portal2:
        selected_gate_option = get_portal_option(1)
        active_portal_bg = portal2.bg
    elif can_enter_portal3:
        selected_gate_option = get_portal_option(2)
        active_portal_bg = portal3.bg
    else:
        return

    if selected_gate_option not in gate_payload_cache:
        loading_screen("A delayed gate awakens...", bg=active_portal_bg if active_portal_bg is not None else chapter2_bg)
        work_path = bool(player_education_status == "Poly" and player_poly_path_choice == "Work")
        try:
            payload = generate_gate_scene(
                option_name=selected_gate_option,
                work_path=work_path,
                education_status=player_education_status,
                poly_path_choice=player_poly_path_choice,
            )
            gate_payload_cache[selected_gate_option] = payload if isinstance(payload, dict) else {}
        except Exception as e:
            print(f"Failed to generate gate scene: {e}")
            return

    payload = gate_payload_cache.get(selected_gate_option, {})
    gate_scene_lines = build_gate_scene_lines(selected_gate_option, payload if isinstance(payload, dict) else {})
    gate_scene_i = 0
    gate_yes_no_idx = 0
    set_state(GATE_SCENE_STATE)


def handle_dragon_warrior_enter():
    global dragon_scene_lines, dragon_scene_i, dragon_met
    if not path_committed or not can_enter_dragon_warrior:
        return
    dragon_payload = gate_dragon_saved.get(committed_path_option, {})
    dragon_scene_lines = build_dragon_scene_lines(committed_path_option or "Chosen Path", dragon_payload if isinstance(dragon_payload, dict) else {})
    dragon_scene_i = 0
    dragon_met = True
    set_state(DRAGON_SCENE_STATE)


def handle_info_hub_enter():
    global info_pages, info_page_i
    if not path_committed or not dragon_met or not can_enter_info_hub:
        return
    info_pages = build_info_pages()
    info_page_i = 0
    set_state(INFO_SCENE_STATE)


def get_selected_portal_exit_spawn():
    if selected_gate_option == get_portal_option(0):
        return PORTAL_EXIT_SPAWNS.get(0)
    if selected_gate_option == get_portal_option(1):
        return PORTAL_EXIT_SPAWNS.get(1)
    if selected_gate_option == get_portal_option(2):
        return PORTAL_EXIT_SPAWNS.get(2)
    return (120, 300)

def handle_profile_events(event):
    global education_selected_idx
    global player_name, player_education_status, player_poly_course
    global part1_ready

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mx, my = event.pos
        for i, r in enumerate(education_rects):
            if r.collidepoint(mx, my):
                education_selected_idx = i
                profile_poly_course_box.active = education_options[i] == "Poly"

    if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
        if education_options[education_selected_idx] == "Poly":
            if profile_name_box.active:
                profile_name_box.active = False
                profile_poly_course_box.active = True
            else:
                profile_poly_course_box.active = False
                profile_name_box.active = True

    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        name = profile_name_box.getText().strip()
        if not name:
            print("Name is required.")
            return

        selected = education_options[education_selected_idx]
        mapped_edu = map_education_for_engine(selected)
        poly_course = None
        if selected == "Poly":
            poly_course = profile_poly_course_box.getText().strip()
            if not poly_course:
                print("Poly course of study is required.")
                return

        player_name = name
        player_education_status = mapped_edu
        player_poly_course = poly_course

        loading_screen("Chapter I : The Training Ground", bg=bg_img)
        try:
            gq.load_part1_dynamic_quizzes(education_status=player_education_status, poly_course=player_poly_course)
            part1_ready = True
            set_state(OUTSIDE, OUTSIDE_SPAWN, "Chapter I : Finding Yourself")
        except Exception as e:
            print(f"Failed to generate Part 1: {e}")


def get_active_quizzes():
    if state == HOME:
        return gq.quiz_questions_home
    if state == WISEMAN:
        return gq.quiz_questions_wiseman
    return None


def get_poly_path_choice(part2_answers):
    for answer in part2_answers:
        if not isinstance(answer, dict):
            continue
        if answer.get("id") == "poly_path":
            raw = str(answer.get("answer", "")).strip()
            if raw in ("Work", "Go to uni"):
                return raw
    return None


def normalize_suggested_options(values):
    if not isinstance(values, list):
        return ["Option 1", "Option 2", "Option 3"]
    out = [str(v) for v in values if str(v).strip()]
    while len(out) < 3:
        out.append(f"Option {len(out) + 1}")
    return out[:3]


running = True
while running:
    dt = clock.tick(60) / 1000.0
    events = pygame.event.get()

    if state in (PROFILE, OUTSIDE):
        set_background_music("opening")
    elif state == HOME:
        set_background_music("house")
    elif state == WISEMAN:
        set_background_music("wiseman")
    elif state == CHAPTER2:
        set_background_music("chapter2_no_portal" if path_committed else "chapter2")
    elif state == GATE_SCENE_STATE:
        set_background_music("portal_interior")
    elif state == DRAGON_SCENE_STATE:
        set_background_music("dw")
    elif state == INFO_SCENE_STATE:
        set_background_music("booth")
    elif state == FINAL_SCENE_STATE:
        set_background_music("final_scene")
    else:
        set_background_music(None)

    for event in events:
        if event.type == pygame.QUIT:
            running = False
            continue

        if state == PROFILE:
            pygame_widgets.update([event])
            handle_profile_events(event)
            continue

        if state in (HOME, WISEMAN):
            active = get_active_quizzes()
            if active is None:
                continue

            if gq.quiz_i < len(active):
                current_quiz = active[gq.quiz_i]
                if current_quiz.get("type") == "textinput":
                    pygame_widgets.update([event])

                if event.type == pygame.KEYDOWN:
                    action = gq.handle_quiz_event(event, active)
                    if action == "quit":
                        if state == HOME:
                            set_state(OUTSIDE, HOME_EXIT_SPAWN, facing="down")
                        else:
                            set_state(OUTSIDE, WISEMAN_EXIT_SPAWN, facing="left")
                        gq.reset_quiz_progress()
                    elif action == "next":
                        gq.quiz_next(active)
                        if gq.quiz_done:
                            if state == HOME:
                                part1_answers = gq.collect_answers_for_engine(gq.quiz_questions_home)
                                loading_screen("Fedora drew a quiet breath, and the next gate of questions slowly opened...", bg=bg_img)
                                try:
                                    gq.load_part2_dynamic_quizzes(education_status=player_education_status, part1_answers=part1_answers)
                                    part1_done = True
                                    part2_ready = True
                                except Exception as e:
                                    print(f"Failed to generate Part 2: {e}")
                                set_state(OUTSIDE, HOME_EXIT_SPAWN, facing="down")
                                gq.reset_quiz_progress()
                            else:
                                part2_answers = gq.collect_answers_for_engine(gq.quiz_questions_wiseman)
                                inferred_fields = gq.last_part2_payload.get("inferred_fields", [])
                                if not isinstance(inferred_fields, list):
                                    inferred_fields = []
                                player_poly_path_choice = get_poly_path_choice(part2_answers)

                                loading_screen("Beneath the magical tree, the Wise Man weighed your strengths in silence...", bg=wiseman_tent.bg)
                                try:
                                    analysis_payload = generate_analysis(
                                        education_status=player_education_status,
                                        poly_path_choice=player_poly_path_choice,
                                        inferred_fields=[str(x) for x in inferred_fields],
                                        part2_answers=part2_answers,
                                    )
                                    suggested_options = normalize_suggested_options(analysis_payload.get("suggested_options", []))
                                    gate_payload_cache = {}
                                    gates_prefetched = False
                                    gate_dragon_saved = {}
                                    path_committed = False
                                    committed_path_option = None
                                    dragon_met = False
                                    info_hub_exited_once = False
                                    chapter2_unlocked = True
                                    analysis_overlay_seen = False
                                    show_analysis_overlay = False
                                    set_state(OUTSIDE, WISEMAN_RETURN_SPAWN, "Return to Training Ground", facing="left")
                                except Exception as e:
                                    print(f"Failed to generate analysis: {e}")
                                    set_state(OUTSIDE, WISEMAN_EXIT_SPAWN, facing="left")
                                gq.reset_quiz_progress()
            else:
                if state == HOME:
                    set_state(OUTSIDE, HOME_EXIT_SPAWN, facing="down")
                else:
                    set_state(OUTSIDE, WISEMAN_EXIT_SPAWN, facing="left")
                gq.reset_quiz_progress()
            continue

        if event.type == pygame.KEYDOWN:
            if state == OUTSIDE:
                handle_keydown_ch1(event)
            elif state == CHAPTER2:
                if show_analysis_overlay and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    show_analysis_overlay = False
                    analysis_overlay_seen = True
                elif event.key == pygame.K_e and not show_analysis_overlay:
                    if path_committed:
                        if can_enter_post_info_gate:
                            set_state(FINAL_SCENE_STATE, title="Final Chapter: Victory")
                        elif can_enter_info_hub:
                            handle_info_hub_enter()
                        else:
                            handle_dragon_warrior_enter()
                    else:
                        handle_chapter2_enter()
                elif event.key == pygame.K_q:
                    set_state(OUTSIDE, CH1_GATE_EXIT_SPAWN, "Returning Outside", facing="left")
            elif state == GATE_SCENE_STATE:
                if event.key == pygame.K_q:
                    set_state(CHAPTER2, get_selected_portal_exit_spawn(), facing="down")
                else:
                    is_guide_last = gate_scene_i >= max(0, len(gate_scene_lines) - 1)
                    if is_guide_last:
                        if event.key == pygame.K_LEFT:
                            gate_yes_no_idx = 0
                        elif event.key == pygame.K_RIGHT:
                            gate_yes_no_idx = 1
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            payload = gate_payload_cache.get(selected_gate_option, {})
                            if gate_yes_no_idx == 0:
                                if isinstance(payload, dict):
                                    dragon_payload = payload.get("dragon", {})
                                    if isinstance(dragon_payload, dict):
                                        gate_dragon_saved[selected_gate_option] = dragon_payload
                                path_committed = True
                                committed_path_option = selected_gate_option
                                set_state(CHAPTER2, DRAGON_EXIT_SPAWN, "Path Chosen: Meet Dragon Warrior", facing="right")
                            else:
                                set_state(CHAPTER2, get_selected_portal_exit_spawn(), facing="down")
                    else:
                        if event.key == pygame.K_LEFT:
                            gate_scene_i = max(0, gate_scene_i - 1)
                        elif event.key == pygame.K_RIGHT:
                            gate_scene_i = min(max(0, len(gate_scene_lines) - 1), gate_scene_i + 1)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            if gate_scene_i < max(0, len(gate_scene_lines) - 1):
                                gate_scene_i += 1
            elif state == DRAGON_SCENE_STATE:
                if event.key == pygame.K_q:
                    set_state(CHAPTER2, DRAGON_EXIT_SPAWN, facing="right")
                elif event.key == pygame.K_LEFT:
                    dragon_scene_i = max(0, dragon_scene_i - 1)
                elif event.key == pygame.K_RIGHT:
                    dragon_scene_i = min(max(0, len(dragon_scene_lines) - 1), dragon_scene_i + 1)
            elif state == INFO_SCENE_STATE:
                if event.key == pygame.K_q:
                    info_hub_exited_once = True
                    set_state(CHAPTER2, INFO_HUB_EXIT_SPAWN, facing="left")
                elif event.key == pygame.K_LEFT:
                    info_page_i = max(0, info_page_i - 1)
                elif event.key == pygame.K_RIGHT:
                    info_page_i = min(max(0, len(info_pages) - 1), info_page_i + 1)
            elif state == FINAL_SCENE_STATE:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

    if state != PROFILE and state not in (HOME, WISEMAN):
        pygame_widgets.update(events)

    if state == OUTSIDE:
        prev_pos = main_player.rect.topleft
        main_player.move(dt, GAME_WIDTH, GAME_HEIGHT)
        resolve_world_collision(prev_pos)
        update_outside_interactions()
    elif state == CHAPTER2:
        if not show_analysis_overlay:
            prev_pos = main_player.rect.topleft
            main_player.move(dt, GAME_WIDTH, GAME_HEIGHT)
            resolve_world_collision(prev_pos)
            update_chapter2_interactions()

    render_state()
    pygame.display.flip()

pygame.quit()
