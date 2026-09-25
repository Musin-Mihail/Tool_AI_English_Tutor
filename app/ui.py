import os
import random

import gradio as gr
from app.services.grader_factory import create_grader_agent
from app.data.database import DatabaseManager
from app.services.tts import (
    pad_audio_slots,
    remount_audio_paths,
    synthesize_correct_variants,
    synthesize_en_variants,
)

agent = create_grader_agent()
db = DatabaseManager()
_EMPTY_TTS = pad_audio_slots([])


def _apply_token_usage(token_state, tokens):
    token_state["input"] += tokens["input"]
    token_state["output"] += tokens["output"]
    return token_state


def format_token_display(state):
    return (
        f"**📊 Токены за сессию (Cursor):** "
        f"Вход: {state['input']} | Выход: {state['output']} | "
        f"Стоимость — в [дашборде Cursor](https://cursor.com/dashboard/usage)"
    )


def generate_feedback_markdown(result, score, topic):
    feedback = f"### Оценка: {score}/10\n"
    feedback += f"**Тема:** {topic}\n\n"

    sentences = result.get("sentences_feedback", [])
    if sentences:
        for s in sentences:
            feedback += f"#### Предложение {s.get('sentence_number', '?')}\n"
            if s.get("student_transcription"):
                feedback += f"🗣 **Вы сказали:** {s.get('student_transcription')}\n"
            feedback += f"✅ **Правильный вариант:** {s.get('correct_variant', '')}\n"

            alts = s.get("alternatives", [])
            if alts:
                feedback += f"🔄 **Альтернативы:** {', '.join(alts)}\n"

            errors = s.get("errors", [])
            if errors:
                feedback += "**Ошибки:**\n"
                for err in errors:
                    feedback += f"- *{err.get('type', 'Error')}*: {err.get('explanation', '')}\n"
            else:
                feedback += "✨ **Ошибок нет!**\n"
            feedback += "\n---\n"
    else:
        # Fallback для старых записей из журнала
        feedback += f"**Правильный вариант:**\n{result.get('correct_variant', '')}\n\n"
        if result.get("errors"):
            feedback += "**Ошибки:**\n"
            for err in result.get("errors", []):
                feedback += (
                    f"- *{err.get('type', 'Error')}*: {err.get('explanation', '')}\n"
                )

    feedback += f"\n**Рекомендация:** {result.get('recommendation', '')}\n"
    return feedback


_EMPTY_TASK_HINT = "Нажмите «Получить задание», чтобы сгенерировать 5 предложений."


async def init_task(token_state):
    table_context, journal_context = db.get_context()
    task_response = await agent.generate_new_task(table_context, journal_context)
    task_text = task_response["result"]

    _apply_token_usage(token_state, task_response["tokens"])

    task_id = db.add_task(task_text)
    return task_text, task_id, token_state, format_token_display(token_state)


async def process_submission(
    task_id, task_text, token_state, audio1, audio2, audio3, audio4, audio5
):
    audios = [a for a in [audio1, audio2, audio3, audio4, audio5] if a is not None]
    if not audios:
        return (
            "⚠️ Пожалуйста, запишите хотя бы один аудиофайл.",
            gr.update(),
            gr.update(),
            token_state,
            format_token_display(token_state),
            audio1,
            audio2,
            audio3,
            audio4,
            audio5,
            gr.update(),
            *_EMPTY_TTS,
        )

    if not task_id or not (task_text or "").strip() or task_text.strip() == _EMPTY_TASK_HINT:
        return (
            "⚠️ Сначала нажмите «Получить задание».",
            gr.update(),
            gr.update(),
            token_state,
            format_token_display(token_state),
            audio1,
            audio2,
            audio3,
            audio4,
            audio5,
            gr.update(),
            *_EMPTY_TTS,
        )

    table_context, journal_context = db.get_context()
    eval_response = await agent.grade_translation(
        audios, task_text, table_context, journal_context
    )
    result = eval_response["result"]

    _apply_token_usage(token_state, eval_response["tokens"])

    score = result.get("score", 0)
    topic = result.get("main_topic", "General")

    db.add_journal_entry(task_id, audios, result, score)
    db.update_performance(topic, score)

    feedback = generate_feedback_markdown(result, score, topic)
    feedback += "\n\n---\nДля нового набора предложений нажмите **«Получить задание»**."
    tts_paths = pad_audio_slots(synthesize_correct_variants(result))
    new_perf_ui = update_performance_ui()

    return (
        feedback,
        _EMPTY_TASK_HINT,
        0,
        token_state,
        format_token_display(token_state),
        None,
        None,
        None,
        None,
        None,
        new_perf_ui,
        *tts_paths,
    )


def get_performance_data():
    try:
        data = db.get_all_performance()
        if not data:
            return [["Нет данных", "0.0"]]
        return [[str(row[0]), str(row[1])] for row in data]
    except Exception as e:
        print(f"Ошибка загрузки успеваемости: {e}")
        return [["Ошибка БД", str(e)]]


def update_performance_ui():
    return gr.update(value=get_performance_data())


def load_journal_choices():
    history = db.get_journal_history_full()
    choices = [
        f"{item['id']}: {item['task_text']} ({item['created_at']})" for item in history
    ]
    return gr.update(choices=choices)


def load_journal_entry(choice):
    if not choice:
        return "Выберите запись", None, None, None, None, None, *_EMPTY_TTS
    try:
        entry_id = int(choice.split(":")[0])
        history = db.get_journal_history_full()
        entry = next((item for item in history if item["id"] == entry_id), None)
        if not entry:
            return "Запись не найдена", None, None, None, None, None, *_EMPTY_TTS

        result = entry["ai_feedback"]
        score = entry.get("score", 0)
        topic = result.get("main_topic", "General")

        feedback = generate_feedback_markdown(result, score, topic)
        tts_paths = pad_audio_slots(synthesize_correct_variants(result))

        audios = entry.get("audio_paths", [])
        audios_out = []
        for i in range(5):
            if i < len(audios) and os.path.exists(audios[i]):
                audios_out.append(audios[i])
            else:
                audios_out.append(None)

        return feedback, *audios_out, *tts_paths
    except Exception as e:
        return f"Ошибка загрузки: {e}", None, None, None, None, None, *_EMPTY_TTS


_EMPTY_CARD_AUDIOS = [None, None, None, None]


def _flashcard_status(extra: str = ""):
    total = db.count_flashcards()
    base = f"**Всего карточек:** {total}"
    return f"{base}\n\n{extra}" if extra else base


def _btn_reveal(active: bool):
    return gr.update(interactive=active)


def _btn_grade(active: bool):
    return gr.update(interactive=active)


def _card_variants(card: dict) -> list:
    variants = card.get("en_variants") or []
    if variants:
        return [str(v).strip() for v in variants if str(v).strip()][:4]
    from app.data.database import normalize_en_variants

    return normalize_en_variants(None, card.get("en_text") or "")


def _format_en_variants_md(variants: list) -> str:
    if not variants:
        return "—"
    if len(variants) == 1:
        return f"## {variants[0]}"
    lines = [f"{i}. **{v}**" for i, v in enumerate(variants, 1)]
    return "## Варианты\n\n" + "\n\n".join(lines)


def _card_en_audios(card: dict, prompt_side: str, revealed: bool):
    if not (revealed or prompt_side == "en"):
        return list(_EMPTY_CARD_AUDIOS)
    # Unique paths each time → Gradio player resets to 0:00
    return remount_audio_paths(synthesize_en_variants(_card_variants(card)))


def _empty_flashcard_ui(status_extra: str = ""):
    return (
        0,
        "ru",
        False,
        "### Что перевести\n\nНет карточек.\n\nДобавьте карточки кнопкой «Добавить 20 карточек».",
        "### Перевод\n\n*Здесь появится перевод*",
        _btn_reveal(False),
        _btn_grade(False),
        _btn_grade(False),
        _flashcard_status(status_extra or "Добавьте карточки, чтобы начать."),
        *remount_audio_paths(_EMPTY_CARD_AUDIOS),
    )


def _flashcard_view(card: dict, prompt_side: str, revealed: bool, status_extra: str = ""):
    card_type = card.get("card_type", "phrase")
    variants = _card_variants(card)
    en_display = _format_en_variants_md(variants)

    if prompt_side == "ru":
        left = (
            f"### Что перевести\n"
            f"**Русский** · _{card_type}_\n\n"
            f"## {card['ru_text']}"
        )
        answer_block = en_display
        answer_lang = "Английский"
    else:
        left = (
            f"### Что перевести\n"
            f"**English** · _{card_type}_\n\n"
            f"{en_display}"
        )
        answer_block = f"## {card['ru_text']}"
        answer_lang = "Русский"

    if revealed:
        nuances = (card.get("nuances") or "").strip()
        if nuances:
            nuance_items = "\n".join(
                f"- {line.strip()}"
                for line in nuances.splitlines()
                if line.strip()
            )
            nuances_block = f"**Нюансы:**\n{nuance_items}"
        else:
            nuances_block = "**Нюансы:** —"
        right = (
            f"### Перевод\n"
            f"**{answer_lang}**\n\n"
            f"{answer_block}\n\n"
            f"{nuances_block}"
        )
    else:
        right = (
            "### Перевод\n\n"
            "*Подумайте перевод, затем нажмите «Показать перевод»*"
        )

    audios = _card_en_audios(card, prompt_side, revealed)

    return (
        card["id"],
        prompt_side,
        revealed,
        left,
        right,
        _btn_reveal(not revealed),
        _btn_grade(revealed),
        _btn_grade(revealed),
        _flashcard_status(
            status_extra
            or (
                f"Показов: {card.get('show_count', 0)} · "
                f"правильно: {card.get('correct_count', 0)} · "
                f"неправильно: {card.get('incorrect_count', 0)}"
            )
        ),
        *audios,
    )


def pick_flashcard(
    exclude_id=None, status_extra: str = "", prompt_side: str | None = None
):
    try:
        card = db.get_least_shown_flashcard(exclude_id=exclude_id)
        if not card:
            return _empty_flashcard_ui(status_extra)
        side = prompt_side or random.choice(["ru", "en"])
        return _flashcard_view(card, side, False, status_extra)
    except Exception as e:
        print(f"!!! Flashcard pick error: {e}")
        return _empty_flashcard_ui(f"Ошибка загрузки карточки: {e}")


def load_flashcard_tab(*_args):
    """Tab.select may pass SelectData — ignore extra args."""
    return pick_flashcard()


def reveal_flashcard(card_id, prompt_side):
    if not card_id:
        return _empty_flashcard_ui()
    try:
        card = db.get_flashcard_by_id(int(card_id))
    except Exception as e:
        print(f"!!! Flashcard reveal error: {e}")
        return _empty_flashcard_ui(str(e))
    if not card:
        return pick_flashcard()
    return _flashcard_view(card, prompt_side or "ru", True)


def grade_flashcard(card_id, is_correct):
    try:
        if card_id:
            db.record_flashcard_result(int(card_id), bool(is_correct))
        return pick_flashcard(exclude_id=int(card_id) if card_id else None)
    except Exception as e:
        print(f"!!! Flashcard grade error: {e}")
        return _empty_flashcard_ui(str(e))


def grade_flashcard_correct(card_id):
    return grade_flashcard(card_id, True)


def grade_flashcard_incorrect(card_id):
    return grade_flashcard(card_id, False)


async def generate_flashcards_ui(token_state, card_id):
    existing = db.get_all_flashcards_for_context()
    response = await agent.generate_flashcards(existing)
    cards = response.get("result") or []
    _apply_token_usage(
        token_state, response.get("tokens") or {"input": 0, "output": 0}
    )
    added = db.add_flashcards(cards) if cards else 0
    status = (
        f"Добавлено новых карточек: **{added}**."
        if added
        else "Не удалось добавить карточки. Попробуйте ещё раз."
    )
    view = pick_flashcard(
        exclude_id=int(card_id) if card_id else None,
        status_extra=status,
    )
    return (*view, token_state, format_token_display(token_state))


_FLASHCARD_CSS = """
.flash-card {
  background: #2d333b !important;
  border: 2px solid #f97316 !important;
  border-radius: 16px !important;
  padding: 20px 22px !important;
  min-height: 220px !important;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35) !important;
}
.flash-card-prompt {
  border-color: #38bdf8 !important;
}
.btn-correct button {
  background: #16a34a !important;
  border-color: #15803d !important;
  color: #ffffff !important;
}
.btn-correct button:hover {
  background: #15803d !important;
  border-color: #166534 !important;
}
"""

# Gradio 6: css передаётся в launch(), не в Blocks()
FLASHCARD_CSS = _FLASHCARD_CSS


def build_ui():
    with gr.Blocks(title="English Tutor AI") as demo:
        gr.Markdown("# 🎓 English Tutor AI (Voice Edition)")

        token_state = gr.State(value={"input": 0, "output": 0, "cost": 0.0})
        token_display = gr.Markdown("**📊 Токены за сессию:** Вход: 0 | Выход: 0")

        with gr.Tabs():
            # Первая вкладка: Практика
            with gr.Tab("📝 Практика"):
                task_id_state = gr.State(value=0)

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📝 Текущее задание:")
                        task_display = gr.Textbox(
                            label="Переведите эти 5 предложений",
                            value=_EMPTY_TASK_HINT,
                            interactive=False,
                            lines=7,
                        )
                        get_task_btn = gr.Button(
                            "Получить задание", variant="secondary"
                        )

                        gr.Markdown("### 🎙️ Запись ответов (по одному на предложение):")
                        # WAV — без ffmpeg; mp3 требует установленный ffmpeg в PATH
                        audio1 = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            format="wav",
                            label="Предложение 1",
                        )
                        audio2 = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            format="wav",
                            label="Предложение 2",
                        )
                        audio3 = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            format="wav",
                            label="Предложение 3",
                        )
                        audio4 = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            format="wav",
                            label="Предложение 4",
                        )
                        audio5 = gr.Audio(
                            sources=["microphone"],
                            type="filepath",
                            format="wav",
                            label="Предложение 5",
                        )

                        submit_btn = gr.Button(
                            "Отправить на проверку", variant="primary"
                        )

                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 Результат проверки:")
                        feedback_display = gr.Markdown(
                            "Здесь появится разбор ваших ошибок и оценка."
                        )
                        gr.Markdown("### 🔊 Правильный вариант (озвучка):")
                        tts1 = gr.Audio(label="Правильный вариант 1", interactive=False)
                        tts2 = gr.Audio(label="Правильный вариант 2", interactive=False)
                        tts3 = gr.Audio(label="Правильный вариант 3", interactive=False)
                        tts4 = gr.Audio(label="Правильный вариант 4", interactive=False)
                        tts5 = gr.Audio(label="Правильный вариант 5", interactive=False)

            with gr.Tab("🃏 Карточки"):
                # RU-промпт при сборке UI — без TTS на старте сервера
                _initial = pick_flashcard(prompt_side="ru")
                card_id_state = gr.State(value=_initial[0])
                prompt_side_state = gr.State(value=_initial[1])
                revealed_state = gr.State(value=_initial[2])

                gr.Markdown(
                    "Слева — **что перевести**. Справа — перевод после кнопки. "
                    "Озвучка Kokoro для английского текста."
                )
                cards_status = gr.Markdown(_initial[8])

                with gr.Row(equal_height=True):
                    with gr.Column(
                        scale=1, elem_classes=["flash-card", "flash-card-prompt"]
                    ):
                        left_card = gr.Markdown(_initial[3])
                    with gr.Column(scale=1, elem_classes=["flash-card"]):
                        right_card = gr.Markdown(_initial[4])
                        reveal_btn = gr.Button(
                            "Показать перевод",
                            variant="secondary",
                            interactive=True,
                        )

                gr.Markdown("### 🔊 Озвучка (English) — каждый вариант отдельно")
                with gr.Row():
                    card_audio1 = gr.Audio(
                        label="Вариант 1",
                        value=_initial[9],
                        interactive=False,
                        autoplay=False,
                    )
                    card_audio2 = gr.Audio(
                        label="Вариант 2",
                        value=_initial[10],
                        interactive=False,
                        autoplay=False,
                    )
                with gr.Row():
                    card_audio3 = gr.Audio(
                        label="Вариант 3",
                        value=_initial[11],
                        interactive=False,
                        autoplay=False,
                    )
                    card_audio4 = gr.Audio(
                        label="Вариант 4",
                        value=_initial[12],
                        interactive=False,
                        autoplay=False,
                    )

                with gr.Row():
                    correct_btn = gr.Button(
                        "Правильно",
                        variant="primary",
                        interactive=False,
                        elem_classes=["btn-correct"],
                    )
                    incorrect_btn = gr.Button(
                        "Неправильно", variant="stop", interactive=False
                    )

                generate_cards_btn = gr.Button(
                    "Добавить 20 карточек (нейросеть)", variant="primary"
                )

            with gr.Tab("📈 Успеваемость") as perf_tab:
                perf_table = gr.Dataframe(
                    value=get_performance_data(),
                    headers=["Тема", "Средний балл"],
                    datatype=["str", "str"],
                    type="array",
                    column_count=(2, "fixed"),
                    interactive=False,
                )
                refresh_perf_btn = gr.Button("Обновить данные")

            with gr.Tab("📓 Журнал занятий") as journal_tab:
                with gr.Row():
                    with gr.Column():
                        journal_dropdown = gr.Dropdown(
                            label="Выберите занятие", choices=[]
                        )
                        journal_refresh_btn = gr.Button("Обновить список")
                        j_a1 = gr.Audio(label="Ответ 1", interactive=False)
                        j_a2 = gr.Audio(label="Ответ 2", interactive=False)
                        j_a3 = gr.Audio(label="Ответ 3", interactive=False)
                        j_a4 = gr.Audio(label="Ответ 4", interactive=False)
                        j_a5 = gr.Audio(label="Ответ 5", interactive=False)
                    with gr.Column():
                        journal_feedback = gr.Markdown("Здесь появится разбор.")
                        gr.Markdown("### 🔊 Правильный вариант (озвучка):")
                        j_tts1 = gr.Audio(
                            label="Правильный вариант 1", interactive=False
                        )
                        j_tts2 = gr.Audio(
                            label="Правильный вариант 2", interactive=False
                        )
                        j_tts3 = gr.Audio(
                            label="Правильный вариант 3", interactive=False
                        )
                        j_tts4 = gr.Audio(
                            label="Правильный вариант 4", interactive=False
                        )
                        j_tts5 = gr.Audio(
                            label="Правильный вариант 5", interactive=False
                        )

        flashcard_outputs = [
            card_id_state,
            prompt_side_state,
            revealed_state,
            left_card,
            right_card,
            reveal_btn,
            correct_btn,
            incorrect_btn,
            cards_status,
            card_audio1,
            card_audio2,
            card_audio3,
            card_audio4,
        ]

        # Карточка уже инициализирована при сборке UI; demo.load не нужен для вкладки

        get_task_btn.click(
            fn=init_task,
            inputs=[token_state],
            outputs=[task_display, task_id_state, token_state, token_display],
        )

        reveal_btn.click(
            fn=reveal_flashcard,
            inputs=[card_id_state, prompt_side_state],
            outputs=flashcard_outputs,
        )
        correct_btn.click(
            fn=grade_flashcard_correct,
            inputs=[card_id_state],
            outputs=flashcard_outputs,
        )
        incorrect_btn.click(
            fn=grade_flashcard_incorrect,
            inputs=[card_id_state],
            outputs=flashcard_outputs,
        )
        generate_cards_btn.click(
            fn=generate_flashcards_ui,
            inputs=[token_state, card_id_state],
            outputs=[*flashcard_outputs, token_state, token_display],
        )

        journal_tab.select(fn=load_journal_choices, outputs=[journal_dropdown])

        refresh_perf_btn.click(fn=update_performance_ui, outputs=[perf_table])
        journal_refresh_btn.click(fn=load_journal_choices, outputs=[journal_dropdown])

        journal_dropdown.change(
            fn=load_journal_entry,
            inputs=[journal_dropdown],
            outputs=[
                journal_feedback,
                j_a1,
                j_a2,
                j_a3,
                j_a4,
                j_a5,
                j_tts1,
                j_tts2,
                j_tts3,
                j_tts4,
                j_tts5,
            ],
        )

        submit_btn.click(
            fn=process_submission,
            inputs=[
                task_id_state,
                task_display,
                token_state,
                audio1,
                audio2,
                audio3,
                audio4,
                audio5,
            ],
            outputs=[
                feedback_display,
                task_display,
                task_id_state,
                token_state,
                token_display,
                audio1,
                audio2,
                audio3,
                audio4,
                audio5,
                perf_table,
                tts1,
                tts2,
                tts3,
                tts4,
                tts5,
            ],
        )

    return demo
