import json
import os
import random
import shutil
from datetime import datetime

from app.paths import AUDIO_DIR, DB_PATH
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class UserPerformance(Base):
    __tablename__ = "user_performance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_name = Column(String, unique=True, nullable=False)
    scores_list = Column(Text, default="[ ]")
    average_score = Column(Float, default=0.0)
    active_vocabulary = Column(Text, default="[ ]")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    russian_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    journals = relationship("Journal", back_populates="task")


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    student_audio_paths = Column(Text, default="[ ]")
    ai_feedback = Column(Text, default="{}")
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="journals")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ru_text = Column(Text, nullable=False)
    en_text = Column(Text, nullable=False)
    en_variants = Column(Text, default="[]")
    nuances = Column(Text, default="")
    card_type = Column(String, default="phrase")
    show_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


def normalize_en_variants(raw: Any, en_text: str = "") -> List[str]:
    """Normalize en_variants list or legacy en_text with ' / ' separators."""
    variants: List[str] = []
    if isinstance(raw, list):
        variants = [str(v).strip() for v in raw if str(v).strip()]
    elif isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                variants = [str(v).strip() for v in parsed if str(v).strip()]
        except json.JSONDecodeError:
            variants = []
    if not variants and en_text:
        variants = [p.strip() for p in en_text.split(" / ") if p.strip()]
    # de-dupe preserving order
    seen = set()
    out: List[str] = []
    for v in variants:
        key = v.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
    return out[:4]


class DatabaseManager:
    def __init__(self, db_url: Optional[str] = None):
        DATA_DIR = DB_PATH.parent
        os.makedirs(DATA_DIR, exist_ok=True)
        self.audio_dir = str(AUDIO_DIR)
        os.makedirs(self.audio_dir, exist_ok=True)
        if db_url is None:
            db_url = f"sqlite:///{DB_PATH.as_posix()}"
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self._ensure_flashcard_en_variants_column()
        self._init_default_topics()
        from app.data.flashcard_seed import FLASHCARD_SEED

        self.seed_flashcards_if_empty(FLASHCARD_SEED)
        self.sync_flashcards_from_seed(FLASHCARD_SEED)
        self._migrate_flashcard_en_variants()

    def _ensure_flashcard_en_variants_column(self) -> None:
        with self.engine.connect() as conn:
            rows = conn.exec_driver_sql("PRAGMA table_info(flashcards)").fetchall()
            colnames = {row[1] for row in rows}
            if "en_variants" not in colnames:
                conn.exec_driver_sql(
                    "ALTER TABLE flashcards ADD COLUMN en_variants TEXT DEFAULT '[]'"
                )
                conn.commit()

    def _migrate_flashcard_en_variants(self) -> None:
        with self.SessionLocal() as session:
            cards = session.query(Flashcard).all()
            changed = False
            for card in cards:
                current = normalize_en_variants(card.en_variants, card.en_text or "")
                if not current:
                    continue
                encoded = json.dumps(current, ensure_ascii=False)
                joined = " / ".join(current)
                if (card.en_variants or "").strip() in ("", "[]") or card.en_text != joined:
                    card.en_variants = encoded
                    card.en_text = joined
                    changed = True
            if changed:
                session.commit()

    def _init_default_topics(self):
        default_topics = [
            "Артикли (a/an, the)",
            "Предлоги (in, on, at, for)",
            "Времена Present (Simple vs. Cont.)",
            "Времена Past (Simple vs. Cont. vs. Perf.)",
            "Неправильные глаголы",
            "Порядок слов в предложении",
            "Модальные глаголы",
            "Условные предложения (Conditionals)",
            "Фразовые глаголы",
            "Косвенная речь (Reported Speech)",
        ]
        with self.SessionLocal() as session:
            for topic in default_topics:
                exists = (
                    session.query(UserPerformance).filter_by(topic_name=topic).first()
                )
                if not exists:
                    new_topic = UserPerformance(topic_name=topic)
                    session.add(new_topic)
            session.commit()

    def _flashcard_to_dict(self, card: Flashcard) -> Dict[str, Any]:
        variants = normalize_en_variants(card.en_variants, card.en_text or "")
        return {
            "id": card.id,
            "ru_text": card.ru_text,
            "en_text": " / ".join(variants) if variants else (card.en_text or ""),
            "en_variants": variants,
            "nuances": card.nuances or "",
            "card_type": card.card_type or "phrase",
            "show_count": card.show_count or 0,
            "correct_count": card.correct_count or 0,
            "incorrect_count": card.incorrect_count or 0,
        }

    def seed_flashcards_if_empty(self, cards: List[Dict[str, Any]]) -> int:
        with self.SessionLocal() as session:
            if session.query(Flashcard).count() > 0:
                return 0
            return self._insert_flashcards(session, cards)

    def sync_flashcards_from_seed(self, cards: List[Dict[str, Any]]) -> Dict[str, int]:
        """Update seed cards by ru_text; keep show/correct/incorrect counts.

        Cards present in DB but not in seed (e.g. generated) are left untouched.
        Seed cards missing from DB are inserted.
        """
        updated = 0
        inserted = 0
        with self.SessionLocal() as session:
            existing = session.query(Flashcard).all()
            by_ru: Dict[str, Flashcard] = {}
            for card in existing:
                key = (card.ru_text or "").strip()
                if key and key not in by_ru:
                    by_ru[key] = card

            to_insert: List[Dict[str, Any]] = []
            for raw in cards:
                ru = (raw.get("ru_text") or "").strip()
                variants = normalize_en_variants(
                    raw.get("en_variants"), raw.get("en_text") or ""
                )
                if not ru or not variants:
                    continue
                nuances = (raw.get("nuances") or "").strip()
                card_type = (raw.get("card_type") or "phrase").strip() or "phrase"
                encoded = json.dumps(variants, ensure_ascii=False)
                joined = " / ".join(variants)
                matched = by_ru.get(ru)
                if matched is None:
                    to_insert.append(
                        {
                            "ru_text": ru,
                            "en_variants": variants,
                            "en_text": joined,
                            "nuances": nuances,
                            "card_type": card_type,
                        }
                    )
                    continue
                if (
                    matched.nuances != nuances
                    or (matched.en_variants or "") != encoded
                    or (matched.en_text or "") != joined
                    or (matched.card_type or "") != card_type
                ):
                    matched.nuances = nuances
                    matched.en_variants = encoded
                    matched.en_text = joined
                    matched.card_type = card_type
                    updated += 1

            if to_insert:
                inserted = self._insert_flashcards(session, to_insert)
            elif updated:
                session.commit()
        return {"updated": updated, "inserted": inserted}

    def add_flashcards(self, cards: List[Dict[str, Any]]) -> int:
        with self.SessionLocal() as session:
            return self._insert_flashcards(session, cards)

    def _insert_flashcards(self, session, cards: List[Dict[str, Any]]) -> int:
        added = 0
        for raw in cards:
            ru = (raw.get("ru_text") or "").strip()
            variants = normalize_en_variants(
                raw.get("en_variants"), raw.get("en_text") or ""
            )
            if not ru or not variants:
                continue
            card = Flashcard(
                ru_text=ru,
                en_text=" / ".join(variants),
                en_variants=json.dumps(variants, ensure_ascii=False),
                nuances=(raw.get("nuances") or "").strip(),
                card_type=(raw.get("card_type") or "phrase").strip() or "phrase",
            )
            session.add(card)
            added += 1
        session.commit()
        return added

    def _flashcard_priority(self, card: Flashcard) -> int:
        """Lower priority = show sooner.
        priority = show_count + 3 * correct_count - incorrect_count
        """
        return (
            (card.show_count or 0)
            + 3 * (card.correct_count or 0)
            - (card.incorrect_count or 0)
        )

    def get_least_shown_flashcard(
        self, exclude_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        with self.SessionLocal() as session:
            query = session.query(Flashcard)
            if exclude_id is not None:
                query = query.filter(Flashcard.id != exclude_id)
            cards = query.all()
            if not cards:
                if exclude_id is not None:
                    card = session.query(Flashcard).filter_by(id=exclude_id).first()
                    return self._flashcard_to_dict(card) if card else None
                return None
            min_priority = min(self._flashcard_priority(c) for c in cards)
            candidates = [
                c for c in cards if self._flashcard_priority(c) == min_priority
            ]
            return self._flashcard_to_dict(random.choice(candidates))

    def get_flashcard_by_id(self, card_id: int) -> Optional[Dict[str, Any]]:
        with self.SessionLocal() as session:
            card = session.query(Flashcard).filter_by(id=card_id).first()
            return self._flashcard_to_dict(card) if card else None

    def get_all_flashcards_for_context(self) -> str:
        with self.SessionLocal() as session:
            cards = session.query(Flashcard).order_by(Flashcard.id.asc()).all()
            if not cards:
                return "Existing flashcards: (empty)"
            lines = ["Existing flashcards:"]
            for c in cards:
                lines.append(
                    f"- [{c.card_type}] RU: {c.ru_text} | EN: {c.en_text}"
                )
                nuances = (c.nuances or "").strip()
                if nuances:
                    for nuance_line in nuances.splitlines():
                        nuance_line = nuance_line.strip()
                        if nuance_line:
                            lines.append(f"  nuance: {nuance_line}")
            return "\n".join(lines)

    def count_flashcards(self) -> int:
        with self.SessionLocal() as session:
            return session.query(Flashcard).count()

    def record_flashcard_result(self, card_id: int, is_correct: bool) -> None:
        with self.SessionLocal() as session:
            card = session.query(Flashcard).filter_by(id=card_id).first()
            if not card:
                return
            card.show_count = (card.show_count or 0) + 1
            if is_correct:
                card.correct_count = (card.correct_count or 0) + 1
            else:
                card.incorrect_count = (card.incorrect_count or 0) + 1
            session.commit()

    def get_context(self):
        with self.SessionLocal() as session:
            topics = session.query(UserPerformance).all()
            table_content = "Context Table:\n"
            for t in topics:
                table_content += (
                    f"- Topic: {t.topic_name} | Avg Score: {t.average_score}\n"
                )

            journals = (
                session.query(Journal)
                .order_by(Journal.created_at.desc())
                .limit(5)
                .all()
            )
            journal_content = "Journal History:\n"
            for j in reversed(journals):
                task_text = j.task.russian_text if j.task else "Unknown"
                journal_content += f"**Задание (Русский):**\n{task_text}\n"

            return table_content, journal_content

    def add_task(self, russian_text: str) -> int:
        with self.SessionLocal() as session:
            task = Task(russian_text=russian_text)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task.id

    def add_journal_entry(
        self, task_id: int, audio_paths: List[str], ai_feedback: Dict, score: float
    ):
        saved_audio_paths = []
        for path in audio_paths:
            if os.path.exists(path):
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{os.path.basename(path)}"
                dest_path = os.path.join(self.audio_dir, filename)
                shutil.copy2(path, dest_path)
                saved_audio_paths.append(dest_path)

        with self.SessionLocal() as session:
            journal = Journal(
                task_id=task_id,
                student_audio_paths=json.dumps(saved_audio_paths, ensure_ascii=False),
                ai_feedback=json.dumps(ai_feedback, ensure_ascii=False),
                score=score,
            )
            session.add(journal)
            session.commit()

    def update_performance(self, topic_name: str, score: float):
        if not topic_name:
            return
        with self.SessionLocal() as session:
            topic = (
                session.query(UserPerformance).filter_by(topic_name=topic_name).first()
            )
            if not topic:
                topic = UserPerformance(topic_name=topic_name)
                session.add(topic)

            scores = json.loads(topic.scores_list) if topic.scores_list else []
            scores.append(score)
            topic.scores_list = json.dumps(scores)
            topic.average_score = round(sum(scores) / len(scores), 1)

            # Логика обновления словаря удалена по запросу
            session.commit()

    def get_all_performance(self):
        with self.SessionLocal() as session:
            topics = session.query(UserPerformance).all()
            result = []
            for t in topics:
                # Возвращаем только 2 колонки
                result.append([t.topic_name, t.average_score])
            return result

    def get_journal_history_full(self):
        with self.SessionLocal() as session:
            journals = session.query(Journal).order_by(Journal.created_at.desc()).all()
            result = []
            for j in journals:
                task_text = j.task.russian_text if j.task else "Unknown"
                audio_paths = (
                    json.loads(j.student_audio_paths) if j.student_audio_paths else []
                )
                ai_feedback = json.loads(j.ai_feedback) if j.ai_feedback else {}
                result.append(
                    {
                        "id": j.id,
                        "task_text": task_text,
                        "created_at": j.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "audio_paths": audio_paths,
                        "ai_feedback": ai_feedback,
                        "score": j.score,
                    }
                )
            return result
