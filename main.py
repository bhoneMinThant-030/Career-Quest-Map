import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox

from game_classes import *
import game_quizes as gq
from print_questions import generate_analysis, generate_gate_scene


GATE_SCENE_STATE = "gate_scene"
DRAGON_SCENE_STATE = "dragon_scene"
INFO_SCENE_STATE = "info_scene"

can_enter_home = False
can_enter_wiseman = False
can_enter_exit_gate = False
can_enter_portal1 = False
can_enter_portal2 = False
can_enter_portal3 = False
can_enter_dragon_warrior = False
can_enter_info_hub = False

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
path_committed = False
committed_path_option = None
dragon_scene_lines = []
dragon_scene_i = 0
dragon_met = False
info_pages = []
info_page_i = 0

pygame.init()

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Career Quest Map")
font = pygame.font.SysFont("Arial", 32)

bg_img = pygame.image.load("images/background.png")
bg_img = pygame.transform.scale(bg_img, (GAME_WIDTH, GAME_HEIGHT))
chapter2_bg = pygame.image.load("images/chapter2_bg.png")
chapter2_bg = pygame.transform.scale(chapter2_bg, (GAME_WIDTH, GAME_HEIGHT))

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

main_player = Player(x=GAME_WIDTH // 2, y=GAME_HEIGHT // 2, width=100, height=100, img_path="images/warrior/", speed=800)
fedora = Player(x=GAME_WIDTH - 400, y=GAME_HEIGHT - 200, width=100, height=100, img_path="images/fedora/", speed=80)
wiseman = Player(x=GAME_WIDTH - 400, y=GAME_HEIGHT - 200, width=100, height=100, img_path="images/wiseman/", speed=80)
dragon_warrior = Player(x=GAME_WIDTH - 500, y=GAME_HEIGHT - 280, width=100, height=100, img_path="images/wiseman/", speed=0)

home = Structure(GAME_WIDTH - 650, GAME_HEIGHT - 450, 200, 200, "images/house.png", "images/home_bg.png")
wiseman_tent = Structure(GAME_WIDTH - 400, GAME_HEIGHT - 200, 100, 100, "images/wiseman/west.png", "images/TreeScene.png")
exit_gate1 = Structure(GAME_WIDTH - 260, GAME_HEIGHT - 250, 100, 100, "images/gate.png", "images/home_bg.png")
portal1 = Structure(GAME_WIDTH - 660, GAME_HEIGHT - 500, 100, 100, "images/1stGate.png", "images/G1Interior.png")
portal2 = Structure(GAME_WIDTH - 540, GAME_HEIGHT - 500, 100, 100, "images/2ndGate.png", "images/G2Interior.png")
portal3 = Structure(GAME_WIDTH - 420, GAME_HEIGHT - 500, 100, 100, "images/3rdGate.png", "images/G3Interior.png")
info_hub = Structure(GAME_WIDTH - 300, GAME_HEIGHT - 420, 100, 100, "images/home.png", "images/home_bg.png")

WISEMAN_RETURN_SPAWN = (430, 320)


def loading_screen(title):
    screen.fill(BLACK)
    text = font.render(title, True, WHITE)
    screen.blit(text, (120, 280))
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


def set_state(new_state, spawn_pos=None, title=None):
    global state, show_analysis_overlay
    state = new_state
    if new_state == CHAPTER2 and analysis_payload and not analysis_overlay_seen:
        show_analysis_overlay = True
    if spawn_pos is not None:
        main_player.rect.topleft = spawn_pos
    if title:
        loading_screen(title)


def get_portal_option(index):
    if index < len(suggested_options):
        return str(suggested_options[index])
    return f"Option {index + 1}"


def draw_chapter2_labels():
    label_font = pygame.font.SysFont("Arial", 20)
    if path_committed:
        t1 = label_font.render(f"Chosen Path: {committed_path_option or 'Unknown'}", True, WHITE)
        t2 = label_font.render("Dragon Warrior has appeared.", True, WHITE)
        t3 = label_font.render("Approach the warrior and press E for your quest.", True, WHITE)
        screen.blit(t1, (40, 24))
        screen.blit(t2, (40, 48))
        screen.blit(t3, (40, 72))
        if dragon_met:
            t4 = label_font.render("Enter the house icon to review your path.", True, WHITE)
            screen.blit(t4, (40, 96))
        return

    options = [get_portal_option(0), get_portal_option(1), get_portal_option(2)]
    portals = [portal1, portal2, portal3]
    for i, option in enumerate(options):
        p = portals[i]
        y = p.rect.y - 45
        for line in wrap_text(option, 160, label_font)[:2]:
            txt = label_font.render(line, True, WHITE)
            screen.blit(txt, (p.rect.centerx - txt.get_width() // 2, y))
            y += 22

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
    lines = [f"Wise Man: You chose {option_name}. Listen closely."]
    info_lines = payload.get("info_dialog_lines", [])
    if isinstance(info_lines, list):
        for ln in info_lines:
            lines.append(f"Wise Man: {str(ln)}")
    work_style = payload.get("work_style_line")
    if isinstance(work_style, str) and work_style.strip():
        lines.append(f"Wise Man: Work style in this path is {work_style}")
    salary = payload.get("salary_outlook_line")
    if isinstance(salary, str) and salary.strip():
        lines.append(f"Wise Man: Salary outlook: {salary}")
    lines.append("Wise Man: Do you want to proceed with the Dragon Path?")
    return lines


def build_dragon_scene_lines(option_name, dragon_payload):
    lines = [f"Dragon Warrior: You chose {option_name}. Your training begins now."]
    if isinstance(dragon_payload, dict):
        mq = dragon_payload.get("micro_quest_1_week")
        mp = dragon_payload.get("mini_project_1_month")
        if isinstance(mq, str) and mq.strip():
            lines.append("Dragon Warrior: Your one-week micro quest:")
            lines.append(f"Dragon Warrior: {mq}")
        if isinstance(mp, str) and mp.strip():
            lines.append("Dragon Warrior: Your one-month mini project:")
            lines.append(f"Dragon Warrior: {mp}")
        resources = dragon_payload.get("resources", [])
        if isinstance(resources, list) and resources:
            lines.append("Dragon Warrior: Gather these resources:")
            for r in resources:
                lines.append(f"Dragon Warrior: - {str(r)}")
    lines.append("Dragon Warrior: Return to the map and keep training.")
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


def render_gate_scene():
    screen.blit(home.bg, (0, 0))
    box_rect = pygame.Rect(40, 50, 720, 330)
    gq.draw_dialog_box(screen, box_rect, fill_color=(10, 10, 10), alpha=210, border_color=(255, 255, 255))

    title_font = pygame.font.SysFont("Arial", 28)
    prompt_font = pygame.font.SysFont("Arial", 28)
    hint_font = pygame.font.SysFont("Arial", 24)
    screen.blit(title_font.render("The Wise Man:", True, WHITE), (box_rect.x + 20, box_rect.y + 15))

    y = box_rect.y + 60
    at_last = gate_scene_i >= max(0, len(gate_scene_lines) - 1)
    if at_last:
        current = gate_scene_lines[min(gate_scene_i, len(gate_scene_lines) - 1)] if gate_scene_lines else "Wise Man: Proceed?"
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
        current = gate_scene_lines[min(gate_scene_i, len(gate_scene_lines) - 1)] if gate_scene_lines else "Wise Man: I have no guidance for this gate yet."
        for ln in wrap_text(current, box_rect.width - 40, prompt_font)[:6]:
            screen.blit(prompt_font.render(ln, True, (230, 230, 230)), (box_rect.x + 20, y))
            y += 32

    screen.blit(pygame.transform.scale(main_player.img_down, (250, 250)), (100, 360))
    screen.blit(pygame.transform.scale(wiseman.img_down, (200, 200)), (500, 380))

    if at_last:
        hint_text = "Left/Right choose Yes/No | Enter confirm | Q back to gates"
    elif gate_scene_i < max(0, len(gate_scene_lines) - 1):
        hint_text = "Left/Right back/next line | Q back to gates"
    else:
        hint_text = "Left/Right review lines | Q back to gates"
    screen.blit(hint_font.render(hint_text, True, (180, 180, 180)), (box_rect.x + 20, box_rect.bottom + 170))


def render_dragon_scene():
    screen.blit(home.bg, (0, 0))
    box_rect = pygame.Rect(40, 50, 720, 330)
    gq.draw_dialog_box(screen, box_rect, fill_color=(10, 10, 10), alpha=210, border_color=(255, 255, 255))

    title_font = pygame.font.SysFont("Arial", 28)
    prompt_font = pygame.font.SysFont("Arial", 28)
    hint_font = pygame.font.SysFont("Arial", 24)
    screen.blit(title_font.render("Dragon Warrior:", True, WHITE), (box_rect.x + 20, box_rect.y + 15))

    current = dragon_scene_lines[min(dragon_scene_i, len(dragon_scene_lines) - 1)] if dragon_scene_lines else "Dragon Warrior: I await your chosen path."
    y = box_rect.y + 60
    for ln in wrap_text(current, box_rect.width - 40, prompt_font)[:6]:
        screen.blit(prompt_font.render(ln, True, (230, 230, 230)), (box_rect.x + 20, y))
        y += 32

    screen.blit(pygame.transform.scale(main_player.img_down, (250, 250)), (100, 360))
    screen.blit(pygame.transform.scale(dragon_warrior.img_down, (200, 200)), (500, 380))

    hint_text = "Left/Right back/next line | Q back to map" if dragon_scene_i < max(0, len(dragon_scene_lines) - 1) else "Left/Right review lines | Q back to map"
    screen.blit(hint_font.render(hint_text, True, (180, 180, 180)), (box_rect.x + 20, box_rect.bottom + 170))


def render_info_scene():
    screen.blit(home.bg, (0, 0))
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

    screen.blit(pygame.transform.scale(main_player.img_down, (250, 250)), (100, 360))
    screen.blit(pygame.transform.scale(dragon_warrior.img_down, (200, 200)), (500, 380))

    screen.blit(hint_font.render(f"Page {info_page_i + 1}/{len(info_pages)}", True, (200, 200, 200)), (box_rect.x + 20, box_rect.bottom + 140))
    screen.blit(hint_font.render("Left/Right change section | Q back to map", True, (180, 180, 180)), (box_rect.x + 20, box_rect.bottom + 170))

def render_outside_quest_hint():
    hint_font = pygame.font.SysFont("Arial", 24)
    if not part1_done:
        msg = "Quest: Complete House questions"
    elif not chapter2_unlocked:
        msg = "Quest: Visit Wise Man"
    else:
        msg = "Quest: Go to the Gate"
    screen.blit(hint_font.render(msg, True, (255, 245, 170)), (24, 24))


def render_state():
    if state == OUTSIDE:
        screen.blit(bg_img, (0, 0))
        home.draw(screen)
        if part1_done:
            wiseman_tent.draw(screen)
        if chapter2_unlocked:
            exit_gate1.draw(screen)
        render_outside_quest_hint()
        main_player.draw(screen)
        return

    if state == HOME:
        if gq.quiz_i < len(gq.quiz_questions_home):
            gq.draw_quiz_screen(screen, font, home.bg, gq.quiz_questions_home[gq.quiz_i], npc_name="Fedora")
            screen.blit(pygame.transform.scale(main_player.img_down, (250, 250)), (100, 360))
            screen.blit(pygame.transform.scale(fedora.img_down, (200, 200)), (500, 380))
        return

    if state == WISEMAN:
        if gq.quiz_i < len(gq.quiz_questions_wiseman):
            gq.draw_quiz_screen(screen, font, home.bg, gq.quiz_questions_wiseman[gq.quiz_i], npc_name="The Wise Man")
            screen.blit(pygame.transform.scale(main_player.img_down, (250, 250)), (100, 360))
            screen.blit(pygame.transform.scale(wiseman.img_down, (200, 200)), (500, 380))
        return

    if state == CHAPTER2:
        screen.blit(chapter2_bg, (0, 0))
        if not path_committed:
            portal1.draw(screen)
            portal2.draw(screen)
            portal3.draw(screen)
        else:
            dragon_warrior.draw(screen)
            if dragon_met:
                info_hub.draw(screen)
        draw_chapter2_labels()
        main_player.draw(screen)
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

    if state == PROFILE:
        screen.fill((20, 20, 20))
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
    can_enter_home = main_player.rect.colliderect(home.rect)
    can_enter_wiseman = part1_done and main_player.rect.colliderect(wiseman_tent.rect)
    can_enter_exit_gate = chapter2_unlocked and main_player.rect.colliderect(exit_gate1.rect)


def update_chapter2_interactions():
    global can_enter_portal1, can_enter_portal2, can_enter_portal3, can_enter_dragon_warrior, can_enter_info_hub
    if path_committed:
        can_enter_portal1 = False
        can_enter_portal2 = False
        can_enter_portal3 = False
        can_enter_dragon_warrior = main_player.rect.colliderect(dragon_warrior.rect)
        can_enter_info_hub = dragon_met and main_player.rect.colliderect(info_hub.rect)
        return
    can_enter_portal1 = main_player.rect.colliderect(portal1.rect)
    can_enter_portal2 = main_player.rect.colliderect(portal2.rect)
    can_enter_portal3 = main_player.rect.colliderect(portal3.rect)
    can_enter_dragon_warrior = False
    can_enter_info_hub = False


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
        set_state(CHAPTER2, (100, 300), "Chapter 2: The Portals")


def handle_chapter2_enter():
    global selected_gate_option, gate_scene_lines, gate_scene_i, gate_yes_no_idx
    if can_enter_portal1:
        selected_gate_option = get_portal_option(0)
    elif can_enter_portal2:
        selected_gate_option = get_portal_option(1)
    elif can_enter_portal3:
        selected_gate_option = get_portal_option(2)
    else:
        return

    if selected_gate_option not in gate_payload_cache:
        loading_screen("Generating gate scene...")
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

        loading_screen("Generating Part 1 questions...")
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
                        state = OUTSIDE
                        gq.reset_quiz_progress()
                    elif action == "next":
                        gq.quiz_next(active)
                        if gq.quiz_done:
                            if state == HOME:
                                part1_answers = gq.collect_answers_for_engine(gq.quiz_questions_home)
                                loading_screen("Generating Part 2 questions...")
                                try:
                                    gq.load_part2_dynamic_quizzes(education_status=player_education_status, part1_answers=part1_answers)
                                    part1_done = True
                                    part2_ready = True
                                except Exception as e:
                                    print(f"Failed to generate Part 2: {e}")
                                state = OUTSIDE
                                gq.reset_quiz_progress()
                            else:
                                part2_answers = gq.collect_answers_for_engine(gq.quiz_questions_wiseman)
                                inferred_fields = gq.last_part2_payload.get("inferred_fields", [])
                                if not isinstance(inferred_fields, list):
                                    inferred_fields = []
                                player_poly_path_choice = get_poly_path_choice(part2_answers)

                                loading_screen("Generating analysis...")
                                try:
                                    analysis_payload = generate_analysis(
                                        education_status=player_education_status,
                                        poly_path_choice=player_poly_path_choice,
                                        inferred_fields=[str(x) for x in inferred_fields],
                                        part2_answers=part2_answers,
                                    )
                                    suggested_options = normalize_suggested_options(analysis_payload.get("suggested_options", []))
                                    gate_payload_cache = {}
                                    gate_dragon_saved = {}
                                    path_committed = False
                                    committed_path_option = None
                                    dragon_met = False
                                    chapter2_unlocked = True
                                    analysis_overlay_seen = False
                                    show_analysis_overlay = False
                                    set_state(OUTSIDE, WISEMAN_RETURN_SPAWN, "Return to Training Ground")
                                except Exception as e:
                                    print(f"Failed to generate analysis: {e}")
                                    state = OUTSIDE
                                gq.reset_quiz_progress()
            else:
                state = OUTSIDE
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
                        if can_enter_info_hub:
                            handle_info_hub_enter()
                        else:
                            handle_dragon_warrior_enter()
                    else:
                        handle_chapter2_enter()
                elif event.key == pygame.K_q:
                    set_state(OUTSIDE, OUTSIDE_SPAWN, "Returning Outside")
            elif state == GATE_SCENE_STATE:
                if event.key == pygame.K_q:
                    set_state(CHAPTER2, (120, 300))
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
                                set_state(CHAPTER2, (120, 300), "Path Chosen: Meet Dragon Warrior")
                            else:
                                set_state(CHAPTER2, (120, 300))
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
                    set_state(CHAPTER2, (120, 300))
                elif event.key == pygame.K_LEFT:
                    dragon_scene_i = max(0, dragon_scene_i - 1)
                elif event.key == pygame.K_RIGHT:
                    dragon_scene_i = min(max(0, len(dragon_scene_lines) - 1), dragon_scene_i + 1)
            elif state == INFO_SCENE_STATE:
                if event.key == pygame.K_q:
                    set_state(CHAPTER2, (120, 300))
                elif event.key == pygame.K_LEFT:
                    info_page_i = max(0, info_page_i - 1)
                elif event.key == pygame.K_RIGHT:
                    info_page_i = min(max(0, len(info_pages) - 1), info_page_i + 1)

    if state != PROFILE and state not in (HOME, WISEMAN):
        pygame_widgets.update(events)

    if state == OUTSIDE:
        main_player.move(dt, GAME_WIDTH, GAME_HEIGHT)
        update_outside_interactions()
    elif state == CHAPTER2:
        if not show_analysis_overlay:
            main_player.move(dt, GAME_WIDTH, GAME_HEIGHT)
            update_chapter2_interactions()

    render_state()
    pygame.display.flip()

pygame.quit()
