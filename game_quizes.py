import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox

from print_questions import generate_part1_ui_questions, generate_part2_ui_questions


def draw_dialog_box(
    surface,
    rect,
    fill_color=(0, 0, 0),
    alpha=200,
    border_color=(255, 255, 255),
    border=3,
    radius=18,
):
    box = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(box, (*fill_color, alpha), box.get_rect(), border_radius=radius)
    surface.blit(box, (rect.x, rect.y))
    pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


quiz_i = 0
quiz_done = False
text_widget = None
text_widget_active_for_i = None


quiz_questions_home = []
quiz_questions_wiseman = []
last_part1_payload = {}
last_part2_payload = {}


def ensure_text_widget(screen, box_rect):
    global text_widget
    if text_widget is None:
        text_widget = TextBox(
            screen,
            box_rect.x + 20,
            box_rect.y + 190,
            box_rect.width - 40,
            45,
            fontSize=28,
            borderColour=(255, 255, 255),
            textColour=(0, 0, 0),
            boxColour=(255, 255, 255),
            radius=6,
            borderThickness=2,
        )
        text_widget.active = True
    return text_widget


def draw_quiz_screen(screen, font, bg, quiz, npc_name="NPC"):
    screen.blit(bg, (0, 0))

    box_rect = pygame.Rect(40, 50, 720, 330)
    draw_dialog_box(screen, box_rect, fill_color=(10, 10, 10), alpha=210, border_color=(255, 255, 255))

    name_surf = font.render(npc_name + ":", True, (255, 255, 255))
    screen.blit(name_surf, (box_rect.x + 20, box_rect.y + 15))

    prompt_font = pygame.font.SysFont("Arial", 28)
    lines = wrap_text(quiz.get("question", ""), prompt_font, box_rect.width - 40)
    y = box_rect.y + 60
    for line in lines[:2]:
        screen.blit(prompt_font.render(line, True, (230, 230, 230)), (box_rect.x + 20, y))
        y += 32

    qtype = quiz.get("type")
    hint_font = pygame.font.SysFont("Arial", 24)

    if qtype == "multiple_choice":
        draw_multiple_choice(screen, box_rect, quiz)
        hint = hint_font.render("Up/Down choose | Enter confirm | 1-9 quick | Q exit", True, (180, 180, 180))
        screen.blit(hint, (box_rect.x + 20, box_rect.bottom + 170))
        return

    if qtype == "slider":
        draw_slider(screen, box_rect, quiz)
        hint = hint_font.render("Left/Right change | Enter confirm | Q exit", True, (180, 180, 180))
        screen.blit(hint, (box_rect.x + 20, box_rect.bottom + 170))
        return

    if qtype == "rating":
        draw_rating(screen, box_rect, quiz)
        hint = hint_font.render("Left/Right change | 1-5 quick | Enter confirm | Q exit", True, (180, 180, 180))
        screen.blit(hint, (box_rect.x + 20, box_rect.bottom + 170))
        return

    if qtype == "textinput":
        draw_textinput(screen, box_rect, quiz)
        hint = hint_font.render("Type answer | Enter confirm | Q exit", True, (180, 180, 180))
        screen.blit(hint, (box_rect.x + 20, box_rect.bottom + 170))
        return

    err = pygame.font.SysFont("Arial", 26).render(f"Unknown quiz type: {qtype}", True, (255, 100, 100))
    screen.blit(err, (box_rect.x + 20, box_rect.y + 150))


def draw_multiple_choice(screen, box_rect, quiz):
    opt_font = pygame.font.SysFont("Arial", 26)
    options = quiz.get("answers", [])
    selected_idx = int(quiz.get("user_choice_index", 0))
    opt_y = box_rect.y + 120

    for i, opt in enumerate(options):
        opt_rect = pygame.Rect(box_rect.x + 20, opt_y, box_rect.width - 40, 34)
        is_sel = i == selected_idx
        fill = (60, 60, 60) if is_sel else (30, 30, 30)
        pygame.draw.rect(screen, fill, opt_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), opt_rect, 2, border_radius=10)

        label = f"{i + 1}. {opt}"
        color = (255, 255, 0) if is_sel else (255, 255, 255)
        screen.blit(opt_font.render(label, True, color), (opt_rect.x + 10, opt_rect.y + 5))
        opt_y += 50


def draw_slider(screen, box_rect, quiz):
    max_val = int(quiz.get("select_count", 10))
    val = int(quiz.get("user_choice_index", 0))
    val = max(0, min(max_val, val))

    bar_x = box_rect.x + 60
    bar_y = box_rect.y + 190
    bar_w = box_rect.width - 120
    bar_h = 10

    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), border_radius=6)

    t = 0 if max_val == 0 else (val / max_val)
    knob_x = int(bar_x + t * bar_w)
    knob_y = bar_y + bar_h // 2
    pygame.draw.circle(screen, (255, 255, 0), (knob_x, knob_y), 12)
    pygame.draw.circle(screen, (255, 255, 255), (knob_x, knob_y), 12, 2)

    num_font = pygame.font.SysFont("Arial", 28)
    label = num_font.render(f"{val}/{max_val}", True, (230, 230, 230))
    screen.blit(label, (box_rect.x + 20, box_rect.y + 230))


def draw_rating(screen, box_rect, quiz):
    max_val = 5
    val = int(quiz.get("user_choice_index", 0))
    val = max(1, min(max_val, val if val > 0 else 1))
    quiz["user_choice_index"] = val

    center_y = box_rect.y + 210
    start_x = box_rect.x + 170
    gap = 95
    radius = 28

    for i in range(1, max_val + 1):
        cx = start_x + (i - 1) * gap
        filled = i <= val
        fill_color = (255, 215, 80) if filled else (45, 45, 45)
        border_color = (255, 255, 255)
        pygame.draw.circle(screen, fill_color, (cx, center_y), radius)
        pygame.draw.circle(screen, border_color, (cx, center_y), radius, 3)

        num_font = pygame.font.SysFont("Arial", 24)
        num = num_font.render(str(i), True, (0, 0, 0) if filled else (220, 220, 220))
        screen.blit(num, (cx - num.get_width() // 2, center_y - num.get_height() // 2))

    label_font = pygame.font.SysFont("Arial", 28)
    label = label_font.render(f"Rating: {val}/5", True, (230, 230, 230))
    screen.blit(label, (box_rect.x + 20, box_rect.y + 255))


def draw_textinput(screen, box_rect, quiz):
    global text_widget_active_for_i
    tb = ensure_text_widget(screen, box_rect)

    placeholder = quiz.get("placeholder", "")
    current = quiz.get("user_input", "")

    if text_widget_active_for_i != id(quiz):
        tb.setText(current)
        text_widget_active_for_i = id(quiz)
        tb.active = True

    tb.draw()

    if (tb.getText() or "").strip() == "" and placeholder:
        ph_font = pygame.font.SysFont("Arial", 22)
        ph = ph_font.render(f"Example: {placeholder}", True, (180, 180, 180))
        screen.blit(ph, (box_rect.x + 20, box_rect.y + 160))


def handle_quiz_event(event, quizzes):
    global quiz_i

    quiz = quizzes[quiz_i]
    qtype = quiz.get("type")

    if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
        return "quit"

    if qtype == "multiple_choice":
        if event.type == pygame.KEYDOWN:
            options = quiz.get("answers", [])
            n = len(options)
            if n == 0:
                return None

            if event.key == pygame.K_UP:
                quiz["user_choice_index"] = (quiz.get("user_choice_index", 0) - 1) % n
            elif event.key == pygame.K_DOWN:
                quiz["user_choice_index"] = (quiz.get("user_choice_index", 0) + 1) % n
            elif pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                if idx < n:
                    quiz["user_choice_index"] = idx
            elif event.key == pygame.K_RETURN:
                return "next"
        return None

    if qtype == "slider":
        if event.type == pygame.KEYDOWN:
            max_val = int(quiz.get("select_count", 10))
            v = int(quiz.get("user_choice_index", 0))

            if event.key == pygame.K_LEFT:
                v = max(0, v - 1)
            elif event.key == pygame.K_RIGHT:
                v = min(max_val, v + 1)
            elif event.key == pygame.K_RETURN:
                return "next"

            quiz["user_choice_index"] = v
        return None

    if qtype == "rating":
        if event.type == pygame.KEYDOWN:
            max_val = 5
            v = int(quiz.get("user_choice_index", 1))
            v = max(1, min(max_val, v if v > 0 else 1))

            if event.key == pygame.K_LEFT:
                v = max(1, v - 1)
            elif event.key == pygame.K_RIGHT:
                v = min(max_val, v + 1)
            elif pygame.K_1 <= event.key <= pygame.K_5:
                v = event.key - pygame.K_0
            elif event.key == pygame.K_RETURN:
                return "next"

            quiz["user_choice_index"] = v
        return None

    if qtype == "textinput":
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if text_widget is not None:
                quiz["user_input"] = text_widget.getText()
            return "next"
        return None

    return None


def quiz_next(quizzes):
    global quiz_i, quiz_done, text_widget_active_for_i
    quiz_i += 1
    if quiz_i >= len(quizzes):
        quiz_done = True
        return
    text_widget_active_for_i = None


def reset_quiz_progress():
    global quiz_i, quiz_done, text_widget_active_for_i
    quiz_i = 0
    quiz_done = False
    text_widget_active_for_i = None


def _extract_answer_for_engine(q):
    qtype = q.get("type")
    if qtype == "multiple_choice":
        answers = q.get("answers", [])
        idx = int(q.get("user_choice_index", 0))
        if isinstance(answers, list) and 0 <= idx < len(answers):
            return answers[idx]
        return ""
    if qtype == "slider":
        return int(q.get("user_choice_index", 0))
    if qtype == "rating":
        v = int(q.get("user_choice_index", 1))
        return max(1, min(5, v if v > 0 else 1))
    if qtype == "textinput":
        return str(q.get("user_input", "")).strip()
    return ""


def collect_answers_for_engine(quizzes):
    out = []
    for q in quizzes:
        if not isinstance(q, dict):
            continue
        out.append(
            {
                "id": q.get("qid"),
                "type": q.get("source_type"),
                "prompt": q.get("question"),
                "answer": _extract_answer_for_engine(q),
            }
        )
    return out


def load_part1_dynamic_quizzes(education_status, poly_course=None):
    global quiz_questions_home, last_part1_payload
    part1_ui, payload = generate_part1_ui_questions(
        education_status=education_status,
        poly_course=poly_course,
    )
    quiz_questions_home = part1_ui
    last_part1_payload = payload if isinstance(payload, dict) else {}
    reset_quiz_progress()


def load_part2_dynamic_quizzes(education_status, part1_answers):
    global quiz_questions_wiseman, last_part2_payload
    part2_ui, payload = generate_part2_ui_questions(
        education_status=education_status,
        part1_answers=part1_answers,
    )
    quiz_questions_wiseman = part2_ui
    last_part2_payload = payload if isinstance(payload, dict) else {}
    reset_quiz_progress()
