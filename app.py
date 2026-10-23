from datetime import datetime, timedelta
import json
import os
import random
import time
import streamlit as st
from github import Github

st.set_page_config(
    page_title="Академия Юного Инженера — Имрон", page_icon="🚀", layout="centered"
)

# ==========================================
# --- СИСТЕМА ВЕЧНОГО СОХРАНЕНИЯ НА GITHUB ---
# ==========================================
DATA_FILE = "imron_data.json"

def get_repo():
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["GITHUB_REPO"]
    g = Github(token)
    return g.get_repo(repo_name)

def load_data():
    defaults = {
        "solved_total": 0,
        "correct_total": 0,
        "mult_correct_count": 0,
        "arith_correct_count": 0,
        "text_correct_count": 0,
        "mult_money": 0,
        "arith_money": 0,
        "text_money": 0,
        "logic_money": 0,
        "marathon_money": 0,
        "sprint_money": 0,
        "logic_solved_ids": [],
        "text_solved_ids": [],
        "marathon_last_success": None,
        "timed_mode_last_use": None,
        "earnings_history": [],
    }
    try:
        repo = get_repo()
        file_content = repo.get_contents(DATA_FILE)
        decoded_content = file_content.decoded_content.decode('utf-8')
        data = json.loads(decoded_content)
        
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        
        if "earnings_history" in data:
            for item in data.get("earnings_history", []):
                if isinstance(item.get("date"), str):
                    item["date"] = datetime.fromisoformat(item["date"])
        if data.get("marathon_last_success") and isinstance(data["marathon_last_success"], str):
            data["marathon_last_success"] = datetime.fromisoformat(data["marathon_last_success"])
        if data.get("timed_mode_last_use") and isinstance(data["timed_mode_last_use"], str):
            data["timed_mode_last_use"] = datetime.fromisoformat(data["timed_mode_last_use"])
            
        return data
    except Exception as e:
        return defaults

def save_data():
    try:
        data_to_save = st.session_state.state.copy()
        
        formatted_history = []
        for item in data_to_save["earnings_history"]:
            formatted_history.append({
                "date": item["date"].isoformat() if isinstance(item["date"], datetime) else item["date"],
                "amount": item["amount"],
                "source": item["source"],
            })
        data_to_save["earnings_history"] = formatted_history

        if isinstance(data_to_save.get("marathon_last_success"), datetime):
            data_to_save["marathon_last_success"] = data_to_save["marathon_last_success"].isoformat()
        if isinstance(data_to_save.get("timed_mode_last_use"), datetime):
            data_to_save["timed_mode_last_use"] = data_to_save["timed_mode_last_use"].isoformat()

        repo = get_repo()
        new_content = json.dumps(data_to_save, ensure_ascii=False, indent=4)
        try:
            file_content = repo.get_contents(DATA_FILE)
            repo.update_file(file_content.path, "Автосохранение Академии Имрона", new_content, file_content.sha)
        except:
            repo.create_file(DATA_FILE, "Создание базы Академии", new_content)
    except Exception as e:
        st.error("⚠️ Ошибка сохранения базы данных на GitHub. Проверьте Secrets.")

if "state" not in st.session_state:
    st.session_state.state = load_data()


def speak_voice(text):
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{text}");
        msg.lang = 'ru-RU';
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)


st.title("🚀 Академия юного инженера: ИМРОН")
st.write(
    "Привет, Имрон! Выбирай любой раздел, тренируй ум, решай задачи и зарабатывай"
    " сумы!"
)

# Боковое меню: все разделы
mode = st.sidebar.selectbox(
    "Выбери раздел тренировки:",
    [
        "📚 Школа юного инженера (Уроки и лайфхаки счета)",
        "✖️ Таблица умножения",
        "➕ Простая арифметика",
        "📖 Текстовые задачи",
        "🧠 Задачи для развития мышления",
        "🏆 Марафон 50 вопросов (Награда 5000 сум)",
        "⏱️ Спринт с таймером (7 примеров, Награда 10000 сум)",
        "📊 Статистика и Отчет для родителя",
    ],
)

now = datetime.now()


def add_earnings(amount, source_name):
    st.session_state.state["earnings_history"].append(
        {"date": datetime.now(), "amount": amount, "source": source_name}
    )
    save_data()


def process_reward(section_key_correct, section_key_money, section_name):
    st.session_state.state[section_key_correct] += 1
    current_count = st.session_state.state[section_key_correct]
    remainder = current_count % 25
    left_to_reward = 25 - remainder if remainder != 0 else 0

    if remainder == 0:
        st.session_state.state[section_key_money] += 1000
        add_earnings(1000, f"Награда 25 ответов ({section_name})")
        msg = f"Ура! Ты собрал 25 правильных ответов в разделе {section_name} и заработал 1000 сум!"
        st.success(f"🎉 {msg}")
        speak_voice(msg)
    else:
        save_data()
        msg = f"Ты в пути к заработку 1000 сум. Тебе осталось решить еще {left_to_reward} правильных примеров в разделе {section_name}!"
        st.info(f"💡 {msg}")
        speak_voice(f"Тебе осталось решить еще {left_to_reward} примеров до награды!")


# --- РЕЖИМ: Школа юного инженера (Уроки счета в уме) ---
if mode == "📚 Школа юного инженера (Уроки и лайфхаки счета)":
    st.header("📚 Школа юного инженера: Секреты быстрого счета в уме")
    st.write(
        "Привет, Имрон! Здесь собраны самые крутые и легкие методы, которые"
        " помогут тебе считать быстрее компьютера и без ошибок!"
    )

    st.markdown("---")
    st.subheader("💡 Урок 1: Как легко складывать двузначные числа в уме")
    st.write(
        "**Метод поразрядного сложения:** Сначала складывай десятки, а потом"
        " единицы!"
    )
    st.info(
        "**Пример:** `47 + 32`\n"
        "1. Складываем десятки: `40 + 30 = 70`\n"
        "2. Складываем единицы: `7 + 2 = 9`\n"
        "3. Складываем результаты: `70 + 9 = 79`.\n"
        "Ответ: **79**."
    )

    st.markdown("---")
    st.subheader("💡 Урок 2: Самый простой способ вычитания в уме")
    st.write(
        "**Метод округления:** Если вычитаемое близко к круглому числу"
        " (например, 28), вычти круглое (30), а потом верни лишнее (прибавь 2)!"
    )
    st.info(
        "**Пример:** `64 - 28`\n"
        "1. Округляем до 30: `64 - 30 = 34`.\n"
        "2. Возвращаем 2 (так как отняли больше): `34 + 2 = 36`.\n"
        "Ответ: **36**."
    )

    st.markdown("---")
    st.subheader("💡 Урок 3: Как быстро умножать на 9")
    st.write(
        "**Правило девятки:** Умножь число на 10, а затем вычти само число."
    )
    st.info(
        "**Пример:** `7 × 9`\n"
        "1. Умножаем на 10: `7 × 10 = 70`.\n"
        "2. Вычитаем само число: `70 - 7 = 63`.\n"
        "Ответ: **63**."
    )


# --- РЕЖИМ: Таблица умножения ---
elif mode == "✖️ Таблица умножения":
    st.header("✖️ Тренировка таблицы умножения")
    st.markdown(
        "> **📝 Инструкция:** Вспомни таблицу умножения. Введи правильный ответ"
        " цифрой. Накопи **25 правильных ответов**, чтобы заработать **1000 сум**"
        " в копилку умножения!"
    )

    if "mult_q" not in st.session_state:
        st.session_state.mult_q = None
        st.session_state.mult_ans = None

    if st.button("Следующий пример") or st.session_state.mult_q is None:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        st.session_state.mult_q = f"{a} × {b}"
        st.session_state.mult_ans = a * b

    st.markdown(f"### Сколько будет: **{st.session_state.mult_q}**?")
    user_ans_str = st.text_input("Твой ответ:", value="", key="m_ans_clean")

    if st.button("Проверить ответ", key="check_mult"):
        if user_ans_str.strip().isdigit():
            user_ans = int(user_ans_str.strip())
            st.session_state.state["solved_total"] += 1
            if user_ans == st.session_state.mult_ans:
                st.session_state.state["correct_total"] += 1
                save_data()
                process_reward("mult_correct_count", "mult_money", "Таблица умножения")
                st.session_state.mult_q = None
                st.rerun()
            else:
                save_data()
                st.error(
                    f"Ошибка! Правильный ответ: {st.session_state.mult_ans}. Попробуй"
                    " еще раз!"
                )
        else:
            st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Простая арифметика ---
elif mode == "➕ Простая арифметика":
    st.header("➕ Простая арифметика (Сложение и вычитание)")
    st.markdown(
        "> **📝 Инструкция:** Используй методы быстрого счета из Школы инженера."
        " Накопи **25 правильных ответов**, чтобы получить **1000 сум** в"
        " копилку арифметики!"
    )

    if "arith_q" not in st.session_state:
        st.session_state.arith_q = None
        st.session_state.arith_ans = None

    if st.button("Новый пример") or st.session_state.arith_q is None:
        op = random.choice(["+", "-"])
        if op == "+":
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            st.session_state.arith_ans = a + b
        else:
            a = random.randint(20, 99)
            b = random.randint(10, a)
            st.session_state.arith_ans = a - b
        st.session_state.arith_q = f"{a} {op} {b}"

    st.markdown(f"### Сколько будет: **{st.session_state.arith_q}**?")
    user_ans_a_str = st.text_input("Твой ответ:", value="", key="a_ans_clean")

    if st.button("Проверить арифметику", key="check_arith"):
        val_clean = user_ans_a_str.strip().replace(" ", "")
        if val_clean.lstrip("-").isdigit():
            user_ans_a = int(val_clean)
            st.session_state.state["solved_total"] += 1
            if user_ans_a == st.session_state.arith_ans:
                st.session_state.state["correct_total"] += 1
                save_data()
                process_reward("arith_correct_count", "arith_money", "Простая арифметика")
                st.session_state.arith_q = None
                st.rerun()
            else:
                save_data()
                st.error(f"Неверно. Правильный ответ: {st.session_state.arith_ans}")
        else:
            st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Текстовые задачи (Без повторов) ---
elif mode == "📖 Текстовые задачи":
    st.header("📖 Текстовые задачи")
    st.markdown(
        "> **📝 Инструкция:** Внимательно прочитай условие, найди главные числа"
        " и вопрос. Введи ответ цифрой. Накопи **25 правильных ответов**, чтобы"
        " получить **1000 сум** в копилку текстовых задач!"
    )

    tasks_list = [
        {"id": 1, "q": "У Ирины было 4 коробки с карандашами, в каждой по 6 карандашей. Сколько всего карандашей у Ирины?", "ans": 24},
        {"id": 2, "q": "В гараже стояло 15 машин. Уехали 7 машин. Сколько машин осталось в гараже?", "ans": 8},
        {"id": 3, "q": "На трех полках стояло по 9 книг. Сколько всего книг на полках?", "ans": 27},
        {"id": 4, "q": "У Саши было 50 сумов. Он купил тетрадь за 18 сумов. Сколько денег осталось?", "ans": 32},
        {"id": 5, "q": "В автобусе ехало 28 пассажиров. На остановке зашло еще 14 человек. Сколько стало пассажиров?", "ans": 42},
        {"id": 6, "q": "В мастерской отремонтировали 12 велосипедов, а самокатов на 4 больше, чем велосипедов. Сколько всего самокатов отремонтировали?", "ans": 16},
        {"id": 7, "q": "У бабушки в саду росло 18 кустов белых роз, а красных на 5 кустов меньше. Сколько всего кустов роз росло в саду?", "ans": 31},
    ]

    if "current_text_task" not in st.session_state or st.session_state.current_text_task is None:
        available_text = [t for t in tasks_list if t["id"] not in st.session_state.state["text_solved_ids"]]
        if not available_text:
            st.success("🎉 Ты решил все текстовые задачи! Начинаем заново по кругу.")
            st.session_state.state["text_solved_ids"] = []
            available_text = tasks_list
        st.session_state.current_text_task = random.choice(available_text)

    curr_t = st.session_state.current_text_task
    st.markdown(f"**Задача:** {curr_t['q']}")
    user_ans_t_str = st.text_input("Введите числовой ответ:", value="", key="t_ans_clean")

    if st.button("Проверить задачу", key="check_task"):
        val_clean = user_ans_t_str.strip()
        if val_clean.lstrip("-").isdigit():
            user_ans_t = int(val_clean)
            st.session_state.state["solved_total"] += 1
            if user_ans_t == curr_t["ans"]:
                st.session_state.state["correct_total"] += 1
                if curr_t["id"] not in st.session_state.state["text_solved_ids"]:
                    st.session_state.state["text_solved_ids"].append(curr_t["id"])
                save_data()
                process_reward("text_correct_count", "text_money", "Текстовые задачи")
                st.session_state.current_text_task = None
                st.rerun()
            else:
                save_data()
                st.error("Подумай еще раз! Внимательно перечитай условие.")
        else:
            st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Задачи для развития математического мышления ---
elif mode == "🧠 Задачи для развития мышления":
    st.header("🧠 Развитие математического мышления и логики (10 лет)")
    st.markdown(
        "> **📝 Инструкция:** Эти задачи на логику и смекалку. За каждую"
        " правильно решенную задачу ты получаешь **200 сум** в копилку."
    )

    logic_list = [
        {"id": 1, "q": "Лестница состоит из 15 ступенек. На какую ступеньку нужно встать, чтобы оказаться ровно посередине лестницы? (введи номер ступеньки)", "ans": 8},
        {"id": 2, "q": "У мальчика столько же сестер, сколько и братьев, а у его сестры вдвое меньше сестер, чем братьев. Сколько всего детей в семье?", "ans": 4},
        {"id": 3, "q": "Блокнот с карандашом вместе стоят 1100 сумов. Блокнот дороже карандаша на 1000 сумов. Сколько стоит карандаш?", "ans": 50},
        {"id": 4, "q": "Трое друзей делили яблоки. Каждому досталось по 4 яблока, и еще 2 яблока осталось в пакете. Сколько всего было яблок?", "ans": 14},
        {"id": 5, "q": "Шоколадку разделили на 6 частей по прямой линии. Сколько было сделано разрезов?", "ans": 5},
        {"id": 6, "q": "В комнате горело 5 свечей, 2 свечи потухли. Сколько свечей осталось?", "ans": 2},
        {"id": 7, "q": "Два года назад Малик был вдвое младше своей сестры. Сейчас Малику 12 лет. Сколько лет его сестре сейчас?", "ans": 22},
        {"id": 8, "q": "У отца 5 сыновей, и у каждого есть одна сестра. Сколько всего детей в семье?", "ans": 6},
        {"id": 9, "q": "Росли 3 березы. На каждой березе по 4 больших ветки. На каждой ветке по 2 яблока. Сколько всего яблок выросло на березах?", "ans": 0},
        {"id": 10, "q": "У бабушки жили внук Федя, кот Пушок и собака Дружок. Сколько всего ног у этих обитателей в доме?", "ans": 10},
    ]

    if "current_logic_task" not in st.session_state or st.session_state.current_logic_task is None:
        available_tasks = [t for t in logic_list if t["id"] not in st.session_state.state["logic_solved_ids"]]
        if not available_tasks:
            st.success("🎉 Ура, Имрон! Ты решил все логические задачи! Начинаем заново по кругу.")
            st.session_state.state["logic_solved_ids"] = []
            available_tasks = logic_list
        st.session_state.current_logic_task = random.choice(available_tasks)

    curr = st.session_state.current_logic_task
    st.markdown(f"**Логическая задачка:** {curr['q']}")
    user_logic_str = st.text_input("Ваш ответ (число):", value="", key="logic_ans_clean")

    if st.button("Проверить логику", key="check_logic_btn"):
        val_clean = user_logic_str.strip()
        if val_clean.lstrip("-").isdigit():
            user_logic_ans = int(val_clean)
            st.session_state.state["solved_total"] += 1
            if user_logic_ans == curr["ans"]:
                st.session_state.state["correct_total"] += 1

                if curr["id"] not in st.session_state.state["logic_solved_ids"]:
                    st.session_state.state["logic_solved_ids"].append(curr["id"])
                    st.session_state.state["logic_money"] += 200
                    add_earnings(200, "Логическая задача")

                st.success("🧠 Гениально! Ты отлично мыслишь логически и заработал 200 сум! 🏆")
                speak_voice("Ты умница, Имрон! Логическая задача решена правильно!")

                st.session_state.current_logic_task = None
                st.rerun()
            else:
                save_data()
                st.error("Неправильно. Попробуй порассуждать по-другому!")
        else:
            st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Марафон 50 вопросов ---
elif mode == "🏆 Марафон 50 вопросов (Награда 5000 сум)":
    st.header("🏆 Марафон: 50 вопросов без права на ошибку")
    st.markdown(
        "> **📝 Инструкция:** Ответь на 50 вопросов подряд без единой ошибки."
        " Награда — **5000 сум** (доступно раз в 2 часа)."
    )

    can_play_marathon = True
    if st.session_state.state["marathon_last_success"] is not None:
        time_passed = now - st.session_state.state["marathon_last_success"]
        if time_passed < timedelta(hours=2):
            remaining = timedelta(hours=2) - time_passed
            mins_left = int(remaining.total_seconds() // 60)
            can_play_marathon = False
            st.warning(f"⏳ Следующая попытка марафона откроется через {mins_left} минут.")

    if can_play_marathon:
        if "m_active" not in st.session_state:
            st.session_state.m_active = False
            st.session_state.m_step = 1
            st.session_state.m_q = None
            st.session_state.m_ans = None

        if not st.session_state.m_active:
            if st.button("🚀 Начать Марафон"):
                st.session_state.m_active = True
                st.session_state.m_step = 1
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                st.session_state.m_q = f"{a} × {b}"
                st.session_state.m_ans = a * b
                st.rerun()
        else:
            st.markdown(f"### Вопрос № {st.session_state.m_step} из 50")
            st.markdown(f"**Сколько будет: {st.session_state.m_q}**?")

            user_m_str = st.text_input("Твой ответ:", value="", key=f"m_input_clean_{st.session_state.m_step}")

            if st.button("Ответить"):
                val_clean = user_m_str.strip()
                if val_clean.lstrip("-").isdigit():
                    user_m_ans = int(val_clean)
                    st.session_state.state["solved_total"] += 1
                    if user_m_ans == st.session_state.m_ans:
                        st.session_state.state["correct_total"] += 1

                        if st.session_state.m_step >= 50:
                            st.session_state.state["marathon_money"] += 5000
                            st.session_state.state["marathon_last_success"] = now
                            add_earnings(5000, "Марафон 50 вопросов")
                            speak_voice("Ты умница, Имрон! Марафон успешно пройден!")
                            st.success("🎉 ПОЗДРАВЛЯЕМ! Ты прошел весь марафон и заработал 5000 сум!")
                            st.session_state.m_active = False
                        else:
                            st.session_state.m_step += 1
                            a = random.randint(2, 9)
                            b = random.randint(2, 9)
                            st.session_state.m_q = f"{a} × {b}"
                            st.session_state.m_ans = a * b
                            st.rerun()
                    else:
                        save_data()
                        st.error(f"❌ Ошибка на вопросе №{st.session_state.m_step}! Марафон сброшен.")
                        speak_voice("Ничего страшного, попробуй еще раз.")
                        st.session_state.m_active = False
                else:
                    st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Спринт с таймером (Усложненный: Уникальные задачи без повторов) ---
elif mode == "⏱️ Спринт с таймером (7 примеров, Награда 10000 сум)":
    st.header("⏱️ Супер-Спринт с таймером (Уникальные задачи)")
    st.info("💡 Задача: решить **7 разных задач без повторений** за 3 минуты (180 секунд). Награда — **10 000 сум** (доступно раз в 2 часа).")

    can_play_sprint = True
    if st.session_state.state["timed_mode_last_use"] is not None:
        elapsed = now - st.session_state.state["timed_mode_last_use"]
        if elapsed < timedelta(hours=2):
            left_time = timedelta(hours=2) - elapsed
            h_l = int(left_time.total_seconds() // 3600)
            m_l = int((left_time.total_seconds() % 3600) // 60)
            can_play_sprint = False
            st.warning(f"⏳ Спринт будет доступен через {h_l} ч. {m_l} мин.")

    if can_play_sprint:
        if "sprint_active" not in st.session_state:
            st.session_state.sprint_active = False

        if not st.session_state.sprint_active:
            if st.button("🚀 Начать Супер-Спринт (7 задач / 3 мин)"):
                st.session_state.sprint_active = True
                st.session_state.s_step = 1
                st.session_state.s_start_time = time.time()
                
                # Создаем пул из всех возможных задач и перемешиваем их, чтобы гарантированно не было повторов
                pool = []
                
                # Добавляем 5 арифметических примеров
                for _ in range(5):
                    a = random.randint(15, 60)
                    b = random.randint(10, 40)
                    if random.choice([True, False]):
                        pool.append({"q": f"{a} + {b}", "ans": a + b})
                    else:
                        pool.append({"q": f"{a} - {b}", "ans": a - b})
                
                # Текстовые задачи
                text_tasks = [
                    {"q": "У Ирины было 4 коробки с карандашами, в каждой по 6 карандашей. Сколько всего карандашей у Ирины?", "ans": 24},
                    {"q": "В гараже стояло 15 машин. Уехали 7 машин. Сколько машин осталось в гараже?", "ans": 8},
                    {"q": "На трех полках стояло по 9 книг. Сколько всего книг на полках?", "ans": 27},
                    {"q": "У Саши было 50 сумов. Он купил тетрадь за 18 сумов. Сколько денег осталось?", "ans": 32},
                    {"q": "В автобусе ехало 28 пассажиров. На остановке зашло еще 14 человек. Сколько стало пассажиров?", "ans": 42},
                    {"q": "В мастерской отремонтировали 12 велосипедов, а самокатов на 4 больше. Сколько всего самокатов?", "ans": 16},
                    {"q": "У бабушки в саду росло 18 кустов белых роз, а красных на 5 меньше. Сколько всего роз в саду?", "ans": 31}
                ]
                pool.extend(random.sample(text_tasks, min(3, len(text_tasks))))
                
                # Логические задачи
                logic_tasks = [
                    {"q": "Лестница состоит из 15 ступенек. На какую ступеньку нужно встать, чтобы оказаться посередине?", "ans": 8},
                    {"q": "У мальчика столько же сестер, сколько и братьев, а у его сестры вдвое меньше сестер, чем братьев. Сколько детей?", "ans": 4},
                    {"q": "Блокнот с карандашом стоят 1100 сумов. Блокнот дороже на 1000 сумов. Сколько стоит карандаш?", "ans": 50},
                    {"q": "Трое друзей делили яблоки. Каждому досталось по 4, и 2 осталось. Сколько было яблок?", "ans": 14},
                    {"q": "Шоколадку разделили на 6 частей по прямой линии. Сколько было сделано разрезов?", "ans": 5},
                    {"q": "В комнате горело 5 свечей, 2 потухли. Сколько свечей осталось?", "ans": 2},
                    {"q": "Два года назад Малик был вдвое младше сестры. Сейчас Малику 12 лет. Сколько лет сестре?", "ans": 22},
                    {"q": "У отца 5 сыновей, и у каждого есть одна сестра. Сколько всего детей в семье?", "ans": 6},
                    {"q": "У бабушки жили внук Федя, кот Пушок и собака Дружок. Сколько всего ног у этих обитателей в доме?", "ans": 10}
                ]
                pool.extend(random.sample(logic_tasks, min(3, len(logic_tasks))))
                
                # Перемешиваем весь пул и берем ровно 7 уникальных задач
                random.shuffle(pool)
                st.session_state.s_questions = pool[:7]
                st.rerun()
        else:
            elapsed_sec = time.time() - st.session_state.s_start_time
            time_left = max(0, 180 - int(elapsed_sec))

            if time_left == 0:
                st.error("⏰ Время вышло! Спринт прерван.")
                speak_voice("Время вышло, ничего страшного.")
                st.session_state.sprint_active = False
            else:
                current_q_idx = st.session_state.s_step - 1
                current_task = st.session_state.s_questions[current_q_idx]

                st.markdown(f"### ⏱️ Осталось времени: **{time_left} сек.** | Задача {st.session_state.s_step} из 7")
                st.markdown(f"**Задание:** {current_task['q']}")

                user_s_str = st.text_input("Твой ответ (только число):", value="", key=f"sprint_step_clean_{st.session_state.s_step}")

                if st.button("Ответить на спринт"):
                    val_clean = user_s_str.strip()
                    if val_clean.lstrip("-").isdigit():
                        user_s_ans = int(val_clean)
                        st.session_state.state["solved_total"] += 1
                        if user_s_ans == current_task["ans"]:
                            st.session_state.state["correct_total"] += 1

                            if st.session_state.s_step >= 7:
                                st.session_state.state["sprint_money"] += 10000
                                st.session_state.state["timed_mode_last_use"] = now
                                add_earnings(10000, "Супер-Спринт с таймером")
                                speak_voice("Ты гений, Имрон! Супер-Спринт пройден, ты заработал 10 тысяч сум!")
                                st.success("🏆 Блестяще! Ты решил все 7 уникальных задач и заработал 10 000 сум!")
                                st.session_state.sprint_active = False
                            else:
                                st.session_state.s_step += 1
                                st.rerun()
                        else:
                            save_data()
                            st.error("❌ Ошибка! Спринт прерван из-за неверного ответа.")
                            st.session_state.sprint_active = False
                    else:
                        st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Статистика и Отчет для родителя ---
elif mode == "📊 Статистика и Отчет для родителя":
    st.header("📊 Статистика успехов и Панель родительского контроля")
    st.write(
        "👨‍👦 Здесь отображаются данные активности Имрона. Вся статистика"
        " надежно сохраняется на GitHub и защищена от удаления!"
    )

    total_earned = (
        st.session_state.state["mult_money"] +
        st.session_state.state["arith_money"] +
        st.session_state.state["text_money"] +
        st.session_state.state["logic_money"] +
        st.session_state.state["marathon_money"] +
        st.session_state.state["sprint_money"]
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Всего решено", value=st.session_state.state["solved_total"])
    with col2:
        st.metric(label="Правильных ответов", value=st.session_state.state["correct_total"])
    with col3:
        st.metric(label="💰 Общая копилка", value=f"{total_earned} сум")

    st.divider()

    st.subheader("📅 Недельный отчет (За последние 7 дней)")
    week_ago = datetime.now() - timedelta(days=7)
    week_earned = 0
    week_operations_count = 0

    for item in st.session_state.state["earnings_history"]:
        item_date = item["date"]
        if isinstance(item_date, str):
            item_date = datetime.fromisoformat(item_date)
        if item_date >= week_ago:
            week_earned += item["amount"]
            week_operations_count += 1

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.metric(label="💵 Заработано за неделю", value=f"{week_earned} сум")
    with col_w2:
        st.metric(label="🎯 Наград за неделю", value=week_operations_count)

    st.divider()
    st.subheader("🏦 Детализация копилок по разделам:")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="✖️ Умножение", value=f"{st.session_state.state['mult_money']} сум")
        st.caption(f"Правильных ответов: {st.session_state.state['mult_correct_count']}")
    with c2:
        st.metric(label="➕ Арифметика", value=f"{st.session_state.state['arith_money']} сум")
        st.caption(f"Правильных ответов: {st.session_state.state['arith_correct_count']}")
    with c3:
        st.metric(label="📖 Текст. задачи", value=f"{st.session_state.state['text_money']} сум")
        st.caption(f"Правильных ответов: {st.session_state.state['text_correct_count']}")

    c4, c5, c6 = st.columns(3)
    with c4:
        st.metric(label="🧠 Логическое мышление", value=f"{st.session_state.state['logic_money']} сум")
        st.caption(f"Решено задач: {len(st.session_state.state['logic_solved_ids'])}")
    with c5:
        st.metric(label="🏆 Марафон", value=f"{st.session_state.state['marathon_money']} сум")
    with c6:
        st.metric(label="⏱️ Спринт", value=f"{st.session_state.state['sprint_money']} сум")

    st.divider()

    st.subheader("📜 История начислений в копилку (по порядку)")
    history = st.session_state.state["earnings_history"]

    if not history:
        st.info("История пока пуста. Как только Имрон заработает сумы, здесь появится хронология!")
    else:
        for idx, record in enumerate(reversed(history), 1):
            rec_date = record["date"]
            if isinstance(rec_date, str):
                rec_date = datetime.fromisoformat(rec_date)
            date_str = rec_date.strftime("%d.%m.%Y в %H:%M")
            st.markdown(f"**{idx}.** `{date_str}` — **+{record['amount']} сум** *({record['source']})*")

    st.divider()
    st.info("🎯 **Отчет для отца:** Данные надежно зафиксированы на GitHub. Копилка и история больше никогда не пропадут!")
    st.divider()
    st.info("🎯 **Отчет для отца:** Данные надежно зафиксированы на GitHub. Копилка и история больше никогда не пропадут!")
