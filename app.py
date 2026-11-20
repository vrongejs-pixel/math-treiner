# -*- coding: utf-8 -*-
# АКАДЕМИЯ ИМРОНА
# Запуск: streamlit run app.py
# Установка: pip install streamlit

import streamlit as st
import sqlite3
import json
import os
import random
import calendar
from pathlib import Path
from datetime import datetime, date, timedelta
from contextlib import contextmanager

# =========================================================
# 1. НАСТРОЙКИ
# =========================================================

st.set_page_config(
    page_title="Академия Имрона",
    page_icon="🚀",
    layout="wide"
)

PARENT_PASSWORD = "198907"

MARATHON_SIZE = 50
MARATHON_REWARD = 200
REST_MINUTES = 30

NORMAL_REWARD = 100

DATA_DIR = Path(os.environ.get("IMRON_DATA_DIR", ".")).expanduser()
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "imron_data.sqlite3"
OLD_JSON = DATA_DIR / "imron_data.json"


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def money(value):
    return f"{int(value):,}".replace(",", " ") + " сум"


@contextmanager
def database():
    con = sqlite3.connect(DB_PATH, timeout=30)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=30000")

    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


# =========================================================
# 2. СОЗДАНИЕ БАЗЫ ДАННЫХ
# =========================================================

def init_database():
    with database() as con:
        con.execute("PRAGMA journal_mode=WAL")

        con.executescript("""
        CREATE TABLE IF NOT EXISTS earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            amount INTEGER NOT NULL CHECK(amount > 0),
            source TEXT NOT NULL,
            note TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            amount INTEGER NOT NULL CHECK(amount > 0),
            note TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS stats (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_activity (
            day TEXT PRIMARY KEY,
            solved INTEGER NOT NULL DEFAULT 0,
            correct INTEGER NOT NULL DEFAULT 0,
            earned INTEGER NOT NULL DEFAULT 0
        );
        """)

    migrate_old_json()


def get_stat(key, default=None):
    with database() as con:
        row = con.execute(
            "SELECT value FROM stats WHERE key=?",
            (key,)
        ).fetchone()

    if row is None:
        return default

    try:
        return json.loads(row["value"])
    except Exception:
        return default


def set_stat(key, value):
    with database() as con:
        con.execute("""
            INSERT INTO stats(key, value)
            VALUES(?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value=excluded.value
        """, (key, json.dumps(value, ensure_ascii=False)))


def migrate_old_json():
    """
    Переносит старые накопления из imron_data.json.
    Старый файл не удаляется и не изменяется.
    """

    if not OLD_JSON.exists():
        return

    if get_stat("legacy_migrated", False):
        return

    try:
        old = json.loads(OLD_JSON.read_text(encoding="utf-8"))

        if not isinstance(old, dict):
            return

        history = old.get("earnings_history", [])

        with database() as con:
            existing = con.execute(
                "SELECT COUNT(*) AS n FROM earnings"
            ).fetchone()["n"]

            if existing == 0:

                if isinstance(history, list) and history:
                    for item in history:
                        try:
                            amount = int(item.get("amount", 0))

                            if amount > 0:
                                con.execute("""
                                    INSERT INTO earnings(
                                        created_at, amount, source, note
                                    )
                                    VALUES(?, ?, ?, ?)
                                """, (
                                    str(item.get("date") or now_text()),
                                    amount,
                                    str(item.get("source") or "Старый прогресс"),
                                    "Перенесено из старой копилки"
                                ))
                        except Exception:
                            continue

                else:
                    old_keys = [
                        "mult_money",
                        "arith_money",
                        "text_money",
                        "logic_money",
                        "marathon_money",
                        "sprint_money",
                        "robot_money"
                    ]

                    total = sum(
                        max(0, int(old.get(k, 0) or 0))
                        for k in old_keys
                    )

                    if total > 0:
                        con.execute("""
                            INSERT INTO earnings(
                                created_at, amount, source, note
                            )
                            VALUES(?, ?, ?, ?)
                        """, (
                            now_text(),
                            total,
                            "Старый баланс",
                            "Однократный перенос старой копилки"
                        ))

            # Перенос старой статистики
            for key in [
                "solved_total",
                "correct_total",
                "errors_total",
                "marathon_best",
                "skill"
            ]:
                if key in old:
                    con.execute("""
                        INSERT OR IGNORE INTO stats(key, value)
                        VALUES(?, ?)
                    """, (
                        key,
                        json.dumps(old[key], ensure_ascii=False)
                    ))

            con.execute("""
                INSERT OR IGNORE INTO stats(key, value)
                VALUES('marathon_rest_until', 'null')
            """)

            con.execute("""
                INSERT OR REPLACE INTO stats(key, value)
                VALUES('legacy_migrated', 'true')
            """)

    except Exception as exc:
        st.error("Не удалось перенести старые данные.")
        st.write("Старый файл не удалён и не изменён.")
        st.code(str(exc))
        st.stop()


# =========================================================
# 3. ЗАРАБОТОК И СТАТИСТИКА
# =========================================================

def record_result(correct, reward=0, source="Задание", note=""):
    """
    Записывает ответ, статистику и заработок одной операцией.
    Если ответ правильный, деньги сразу попадают в копилку.
    """

    today = date.today().isoformat()
    amount = int(reward) if correct else 0

    with database() as con:

        con.execute("""
            INSERT INTO stats(key, value)
            VALUES('solved_total', '1')
            ON CONFLICT(key)
            DO UPDATE SET value=CAST(value AS INTEGER)+1
        """)

        if correct:
            con.execute("""
                INSERT INTO stats(key, value)
                VALUES('correct_total', '1')
                ON CONFLICT(key)
                DO UPDATE SET value=CAST(value AS INTEGER)+1
            """)
        else:
            con.execute("""
                INSERT INTO stats(key, value)
                VALUES('errors_total', '1')
                ON CONFLICT(key)
                DO UPDATE SET value=CAST(value AS INTEGER)+1
            """)

        con.execute("""
            INSERT INTO daily_activity(day, solved, correct, earned)
            VALUES(?, 1, ?, ?)
            ON CONFLICT(day)
            DO UPDATE SET
                solved=solved+1,
                correct=correct+excluded.correct,
                earned=earned+excluded.earned
        """, (today, 1 if correct else 0, amount))

        if amount > 0:
            con.execute("""
                INSERT INTO earnings(created_at, amount, source, note)
                VALUES(?, ?, ?, ?)
            """, (now_text(), amount, source, note))


def balances():
    with database() as con:
        earned = con.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM earnings"
        ).fetchone()[0]

        paid = con.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM payments"
        ).fetchone()[0]

    earned = int(earned)
    paid = int(paid)

    return earned, paid, earned - paid


def add_payment(amount, note=""):
    """
    Записывает фактическую выплату.
    Нельзя выплатить больше, чем Имрон заработал.
    """

    amount = int(amount)

    if amount <= 0:
        raise ValueError("Введи сумму больше нуля.")

    with database() as con:

        earned = con.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM earnings"
        ).fetchone()[0]

        paid = con.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM payments"
        ).fetchone()[0]

        remaining = int(earned) - int(paid)

        if amount > remaining:
            raise ValueError(
                f"Можно отметить максимум {money(remaining)}."
            )

        con.execute("""
            INSERT INTO payments(created_at, amount, note)
            VALUES(?, ?, ?)
        """, (now_text(), amount, note))


def get_history():
    with database() as con:
        earnings = con.execute("""
            SELECT * FROM earnings
            ORDER BY id DESC
        """).fetchall()

        payments = con.execute("""
            SELECT * FROM payments
            ORDER BY id DESC
        """).fetchall()

    return [dict(x) for x in earnings], [dict(x) for x in payments]


# =========================================================
# 4. ГЕНЕРАТОРЫ ЗАДАНИЙ
# =========================================================

def make_question(section):

    if section == "Математика":

        a = random.randint(24, 89)
        b = random.randint(2, 12)
        operation = random.choice(["+", "-", "×", "÷"])

        if operation == "+":
            answer = a + b
            question = f"{a} + {b} = ?"

        elif operation == "-":
            if b > a:
                a, b = b, a

            answer = a - b
            question = f"{a} − {b} = ?"

        elif operation == "×":
            answer = a * b
            question = f"{a} × {b} = ?"

        else:
            answer = random.randint(2, 20)
            a = answer * b
            question = f"{a} ÷ {b} = ?"

        return {
            "q": question,
            "answer": answer,
            "hint": "Внимательно определи действие и проверь вычисление.",
            "solution": f"Правильный ответ: {answer}. Проверь обратным действием."
        }

    if section == "Уравнения":

        x = random.randint(3, 30)
        a = random.randint(2, 9)
        mode = random.choice([1, 2, 3])

        if mode == 1:
            b = random.randint(5, 40)

            return {
                "q": f"x + {b} = {x+b}. Найди x.",
                "answer": x,
                "hint": "Чтобы найти неизвестное слагаемое, из суммы вычти известное.",
                "solution": f"x = {x+b} − {b} = {x}."
            }

        if mode == 2:
            return {
                "q": f"x − {a} = {x-a}. Найди x.",
                "answer": x,
                "hint": "Чтобы найти уменьшаемое, к разности прибавь вычитаемое.",
                "solution": f"x = {x-a} + {a} = {x}."
            }

        return {
            "q": f"{a} × x = {a*x}. Найди x.",
            "answer": x,
            "hint": "Чтобы найти неизвестный множитель, раздели произведение на известный множитель.",
            "solution": f"x = {a*x} ÷ {a} = {x}."
        }

    if section == "Периметр":

        a = random.randint(4, 25)
        b = random.randint(3, 18)

        answer = 2 * (a + b)

        return {
            "q": f"Длина прямоугольника {a} см, ширина {b} см. Найди периметр.",
            "answer": answer,
            "hint": "Периметр — сумма длин всех сторон.",
            "solution": f"P = {a} + {b} + {a} + {b} = {answer} см."
        }

    if section == "Текстовые задачи":

        a = random.randint(4, 15)
        b = random.randint(3, 12)
        c = random.randint(2, 20)

        answer = a * b - c

        return {
            "q": f"В {a} коробках лежало по {b} карандашей. "
                 f"{c} карандашей раздали. Сколько осталось?",
            "answer": answer,
            "hint": "Сначала найди общее количество карандашей, потом вычти розданные.",
            "solution": f"{a} × {b} = {a*b}; {a*b} − {c} = {answer}."
        }

    if section == "Логика":

        bank = [
            (
                "Продолжи ряд: 2, 4, 8, 16, ...",
                32,
                "Каждое число удваивается.",
                "16 × 2 = 32."
            ),
            (
                "У пяти братьев одна общая сестра. Сколько всего детей?",
                6,
                "Сестра у всех братьев одна и та же.",
                "5 + 1 = 6 детей."
            ),
            (
                "На столе 5 яблок. Ты взял 2. Сколько яблок у тебя?",
                2,
                "Считай только те яблоки, которые ты взял.",
                "У тебя 2 яблока."
            ),
            (
                "Продолжи ряд: 3, 6, 12, 24, ...",
                48,
                "Каждый раз число удваивается.",
                "24 × 2 = 48."
            ),
            (
                "Два отца и два сына получили по одной конфете. "
                "Всего было 3 человека. Сколько было людей?",
                3,
                "Один человек может одновременно быть отцом и сыном.",
                "Это дедушка, отец и сын."
            ),
            (
                "В комнате 4 угла. В каждом углу сидит кошка. "
                "Сколько кошек, если каждая видит трёх остальных?",
                4,
                "Представь кошку в каждом углу.",
                "Всего 4 кошки."
            )
        ]

        q = random.choice(bank)

        return {
            "q": q[0],
            "answer": q[1],
            "hint": q[2],
            "solution": q[3]
        }

    return make_question("Логика")


def make_marathon():
    kinds = (
        ["Математика"] * 15
        + ["Уравнения"] * 10
        + ["Периметр"] * 5
        + ["Текстовые задачи"] * 10
        + ["Логика"] * 10
    )

    random.shuffle(kinds)

    return [
        {"section": section, **make_question(section)}
        for section in kinds
    ]


# =========================================================
# 5. СОХРАНЕНИЕ МАРАФОНА И ОТДЫХА
# =========================================================

def save_active_marathon(marathon):
    set_stat("active_marathon", marathon)


def load_active_marathon():
    return get_stat("active_marathon", None)


def finish_marathon(marathon):
    result = {
        "right": int(marathon["right"]),
        "wrong": int(marathon["wrong"]),
        "finished_at": now_text()
    }

    set_stat("last_marathon", result)
    set_stat("active_marathon", None)

    rest_until = datetime.now() + timedelta(minutes=REST_MINUTES)

    set_stat("marathon_rest_until", rest_until.isoformat())


# =========================================================
# 6. ИНИЦИАЛИЗАЦИЯ
# =========================================================

init_database()

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "parent_logged_in" not in st.session_state:
    st.session_state.parent_logged_in = False

if "marathon" not in st.session_state:
    st.session_state.marathon = load_active_marathon()


# =========================================================
# 7. ГЛАВНЫЙ ЭКРАН
# =========================================================

st.title("🚀 Академия Имрона")
st.caption("Учись, рассуждай, решай задачи и собирай свои достижения.")

earned, paid, remaining = balances()

col1, col2, col3 = st.columns(3)

col1.metric("Всего заработано", money(earned))
col2.metric("Уже выплачено", money(paid))
col3.metric("Осталось получить", money(remaining))

sections = [
    "Главная",
    "Математика",
    "Уравнения",
    "Периметр",
    "Текстовые задачи",
    "Логика",
    "Марафон 50",
    "Статистика",
    "Копилка"
]

mode = st.sidebar.radio("Выбери раздел", sections)


# =========================================================
# 8. ГЛАВНАЯ
# =========================================================

if mode == "Главная":

    st.subheader("Добро пожаловать, Имрон! 👋")

    st.write(
        "Выбирай учебный раздел, решай задания, "
        "учись на ошибках и зарабатывай за правильные ответы."
    )

    st.info(
        "За правильный ответ в обычных заданиях начисляется "
        f"{money(NORMAL_REWARD)}. "
        f"В марафоне — {money(MARATHON_REWARD)} за каждый правильный ответ."
    )

    st.subheader("Твои достижения")

    a, b, c = st.columns(3)

    a.metric("Решено заданий", get_stat("solved_total", 0))
    b.metric("Правильных ответов", get_stat("correct_total", 0))
    c.metric("Ошибок", get_stat("errors_total", 0))

    st.subheader("Выбери направление")

    for section in [
        "Математика",
        "Уравнения",
        "Периметр",
        "Текстовые задачи",
        "Логика"
    ]:
        st.write("📘 " + section)


# =========================================================
# 9. УЧЕБНЫЕ РАЗДЕЛЫ
# =========================================================

elif mode in [
    "Математика",
    "Уравнения",
    "Периметр",
    "Текстовые задачи",
    "Логика"
]:

    st.header(mode)

    if st.button("🎯 Получить новое задание", use_container_width=True):
        st.session_state.current_question = {
            "section": mode,
            **make_question(mode)
        }

    task = st.session_state.current_question

    if task and task["section"] == mode:

        st.subheader(task["q"])

        with st.expander("💡 Учитель: помоги мне понять"):
            st.write(task["hint"])

            st.write("**Попробуй рассуждать самостоятельно.**")

            if st.button("Показать объяснение", key=f"explain_{mode}"):
                st.session_state[f"show_solution_{mode}"] = True

            if st.session_state.get(f"show_solution_{mode}", False):
                st.info(task["solution"])

        answer = st.text_input(
            "Введи свой ответ",
            key=f"answer_{mode}"
        )

        if st.button("Проверить ответ", key=f"check_{mode}"):

            if answer.strip().lstrip("-").isdigit():

                correct = int(answer.strip()) == int(task["answer"])

                record_result(
                    correct,
                    NORMAL_REWARD,
                    mode,
                    "Обычное задание"
                )

                if correct:
                    st.success(
                        f"Верно! +{money(NORMAL_REWARD)} записаны в копилку."
                    )

                    st.session_state.current_question = None
                    st.session_state[f"show_solution_{mode}"] = False

                else:
                    st.error(
                        "Ошибка — это не поражение, "
                        "а возможность научиться."
                    )

                    st.write("Правильный ответ:", task["answer"])
                    st.write("**Разбор:**", task["solution"])

            else:
                st.warning("Введи ответ целым числом.")


# =========================================================
# 10. МАРАФОН 50 ЗАДАНИЙ
# =========================================================

elif mode == "Марафон 50":

    st.header("🏆 Марафон — 50 заданий")

    marathon = st.session_state.marathon

    rest_until = get_stat("marathon_rest_until", None)

    seconds_left = 0

    if rest_until:
        try:
            end_time = datetime.fromisoformat(rest_until)
            seconds_left = int(
                (end_time - datetime.now()).total_seconds()
            )
        except Exception:
            seconds_left = 0

    if seconds_left > 0 and marathon is None:

        minutes = seconds_left // 60
        seconds = seconds_left % 60

        st.warning(
            f"Время отдыха ещё не закончилось. "
            f"Осталось: {minutes} мин. {seconds} сек."
        )

    elif marathon is None:

        last = get_stat("last_marathon", None)

        if last:
            st.info(
                f"Последний результат: {last['right']} из 50. "
                f"Ошибок: {last['wrong']}."
            )

        st.write("За каждый правильный ответ начисляется 200 сум.")
        st.write("Максимум за идеальный проход — 10 000 сум.")

        if st.button(
            "Начать марафон",
            disabled=(seconds_left > 0),
            use_container_width=True
        ):

            marathon = {
                "questions": make_marathon(),
                "step": 0,
                "right": 0,
                "wrong": 0,
                "feedback": None
            }

            st.session_state.marathon = marathon
            save_active_marathon(marathon)
            st.rerun()

    else:

        m = marathon

        if m["step"] < MARATHON_SIZE:

            q = m["questions"][m["step"]]

            st.progress(m["step"] / MARATHON_SIZE)

            st.caption(
                f"Задание {m['step'] + 1} из 50 · {q['section']}"
            )

            st.subheader(q["q"])

            if m["feedback"] is None:

                with st.expander("💡 Подсказка учителя"):
                    st.write(q["hint"])

                answer = st.text_input(
                    "Твой ответ",
                    key=f"marathon_answer_{m['step']}"
                )

                if st.button(
                    "Проверить",
                    key=f"marathon_check_{m['step']}"
                ):

                    if answer.strip().lstrip("-").isdigit():

                        correct = int(answer.strip()) == int(q["answer"])

                        if correct:
                            m["right"] += 1

                            record_result(
                                True,
                                MARATHON_REWARD,
                                "Марафон",
                                f"Задание {m['step'] + 1} из 50"
                            )

                            st.success(
                                "+200 сум! Деньги уже сохранены в копилке."
                            )

                            m["feedback"] = "correct"

                        else:
                            m["wrong"] += 1

                            record_result(
                                False,
                                0,
                                "Марафон",
                                f"Задание {m['step'] + 1} из 50"
                            )

                            m["feedback"] = "wrong"

                        save_active_marathon(m)
                        st.session_state.marathon = m
                        st.rerun()

                    else:
                        st.warning("Введи ответ числом.")

            else:

                if m["feedback"] == "correct":

                    st.success("Правильно! Молодец!")

                else:

                    st.error(
                        "Пока неверно. Ошибка помогает научиться."
                    )

                    st.write("Правильный ответ:", q["answer"])
                    st.write("**Объяснение:**", q["solution"])

                if st.button(
                    "Следующее задание",
                    key=f"marathon_next_{m['step']}"
                ):

                    m["step"] += 1
                    m["feedback"] = None

                    if m["step"] >= MARATHON_SIZE:

                        finish_marathon(m)

                        st.session_state.marathon = None

                        st.success("Марафон завершён!")

                        st.rerun()

                    else:

                        save_active_marathon(m)
                        st.session_state.marathon = m

                        st.rerun()

        else:

            finish_marathon(m)

            st.session_state.marathon = None

            st.rerun()


# =========================================================
# 11. СТАТИСТИКА — ТОЛЬКО ДЛЯ РОДИТЕЛЯ
# =========================================================

elif mode == "Статистика":

    st.header("📊 Статистика Имрона")

    if not st.session_state.parent_logged_in:

        st.info("Этот раздел доступен только родителю.")

        password = st.text_input(
            "Введи пароль родителя",
            type="password"
        )

        if st.button("🔐 Войти"):

            if password == PARENT_PASSWORD:

                st.session_state.parent_logged_in = True
                st.rerun()

            else:
                st.error("Неверный пароль.")

    else:

        st.success("Родительский доступ открыт.")

        if st.button("Выйти из родительского раздела"):

            st.session_state.parent_logged_in = False
            st.rerun()

        solved = int(get_stat("solved_total", 0) or 0)
        correct = int(get_stat("correct_total", 0) or 0)
        errors = int(get_stat("errors_total", 0) or 0)

        accuracy = round(correct / solved * 100) if solved else 0

        a, b, c, d = st.columns(4)

        a.metric("Решено заданий", solved)
        b.metric("Правильных ответов", correct)
        c.metric("Ошибок", errors)
        d.metric("Точность", f"{accuracy}%")

        # ---------------------------------------------
        # КАЛЕНДАРЬ
        # ---------------------------------------------

        st.divider()
        st.subheader("📅 Календарь занятий и заработка")

        selected_month = st.date_input(
            "Выбери месяц",
            value=date.today().replace(day=1)
        )

        year = selected_month.year
        month = selected_month.month

        with database() as con:
            rows = con.execute("""
                SELECT * FROM daily_activity
                WHERE substr(day, 1, 7)=?
                ORDER BY day
            """, (f"{year:04d}-{month:02d}",)).fetchall()

        activity = {
            row["day"]: dict(row)
            for row in rows
        }

        month_name = calendar.month_name[month]

        st.write(f"**{month_name} {year}**")

        cal = calendar.monthcalendar(year, month)

        headers = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        cols = st.columns(7)

        for i, h in enumerate(headers):
            cols[i].markdown(f"**{h}**")

        for week in cal:

            cols = st.columns(7)

            for i, day_number in enumerate(week):

                if day_number == 0:
                    cols[i].write(" ")
                    continue

                day_key = date(year, month, day_number).isoformat()
                info = activity.get(day_key)

                if info:

                    cols[i].markdown(
                        f"**{day_number}**\n\n"
                        f"Задач: {info['solved']}\n\n"
                        f"+{info['earned']} сум"
                    )

                else:
                    cols[i].write(str(day_number))

        st.subheader("Заработок по дням")

        if rows:

            for row in reversed(rows):

                st.write(
                    f"**{row['day']}** — "
                    f"решено: {row['solved']}, "
                    f"правильно: {row['correct']}, "
                    f"заработано: {money(row['earned'])}"
                )

        else:
            st.info("За этот месяц записей пока нет.")

        # ---------------------------------------------
        # ЗАРАБОТОК ПО РАЗДЕЛАМ
        # ---------------------------------------------

        st.divider()
        st.subheader("💰 Заработок по разделам")

        earnings, payments = get_history()

        by_source = {}

        for item in earnings:

            source = item["source"]

            by_source[source] = (
                by_source.get(source, 0) + int(item["amount"])
            )

        if by_source:

            for source, amount in sorted(by_source.items()):

                st.write(f"**{source}:** {money(amount)}")

        else:
            st.info("Пока нет начислений.")

        # ---------------------------------------------
        # УЧЁТ ВЫПЛАТ
        # ---------------------------------------------

        st.divider()
        st.subheader("💵 Учёт денег, выплаченных Имрону")

        earned, paid, remaining = balances()

        x, y, z = st.columns(3)

        x.metric("Всего заработано", money(earned))
        y.metric("Уже оплачено", money(paid))
        z.metric("Осталось выплатить", money(remaining))

        st.markdown("### Записать новую выплату")

        amount = st.number_input(
            "Сколько денег ты фактически выдал Имрону?",
            min_value=0,
            max_value=max(0, remaining),
            step=1000,
            value=0
        )

        note = st.text_input(
            "Примечание",
            placeholder="Например: выплата за неделю"
        )

        if st.button(
            "✅ Отметить как оплаченное",
            disabled=(amount <= 0 or remaining <= 0),
            use_container_width=True
        ):

            try:

                add_payment(int(amount), note)

                st.success(
                    f"Выплата {money(amount)} записана. "
                    "Остаток пересчитан."
                )

                st.rerun()

            except ValueError as exc:

                st.error(str(exc))

        st.subheader("История выплат")

        if payments:

            for p in payments:

                st.write(
                    f"{p['created_at']} — "
                    f"**−{money(p['amount'])}** — "
                    f"{p.get('note') or 'Оплачено'}"
                )

        else:

            st.info("Пока выплат не было.")

        # ---------------------------------------------
        # РЕЗЕРВНЫЕ КОПИИ
        # ---------------------------------------------

        st.divider()
        st.subheader("Резервная копия")

        backup_earnings, backup_payments = get_history()

        backup = {
            "created_at": now_text(),
            "earned": earned,
            "paid": paid,
            "remaining": remaining,
            "earnings": backup_earnings,
            "payments": backup_payments,
            "stats": {
                "solved_total": solved,
                "correct_total": correct,
                "errors_total": errors
            }
        }

        st.download_button(
            "⬇️ Скачать резервную копию всех денег и статистики",
            data=json.dumps(
                backup,
                ensure_ascii=False,
                indent=2
            ),
            file_name="imron_full_backup.json",
            mime="application/json",
            use_container_width=True
        )


# =========================================================
# 12. КОПИЛКА
# =========================================================

elif mode == "Копилка":

    st.header("💰 Копилка Имрона")

    earned, paid, remaining = balances()

    a, b, c = st.columns(3)

    a.metric("Всего заработано", money(earned))
    b.metric("Уже выплачено", money(paid))
    c.metric("Осталось получить", money(remaining))

    earnings, payments = get_history()

    st.divider()
    st.subheader("История заработка")

    if earnings:

        for item in earnings:

            st.write(
                f"{item['created_at']} — "
                f"**+{money(item['amount'])}** — "
                f"{item['source']} "
                f"{('· ' + item['note']) if item['note'] else ''}"
            )

    else:

        st.info("Пока нет заработка. Решай задания, чтобы пополнять копилку.")

    st.divider()
    st.subheader("Отмеченные выплаты")

    if payments:

        for p in payments:

            st.write(
                f"{p['created_at']} — "
                f"−{money(p['amount'])} — Оплачено"
            )

    else:

        st.info("Пока выплат не отмечено.")


# =========================================================
# 13. ИНФОРМАЦИЯ О СОХРАНЕНИИ
# =========================================================

st.sidebar.divider()

st.sidebar.caption("Данные хранятся в базе SQLite.")

st.sidebar.caption(
    "Не удаляй файл imron_data.sqlite3 — "
    "в нём находятся заработки, выплаты и статистика."
)

st.sidebar.caption(
    "Для облачного запуска необходимо постоянное хранилище."
)
