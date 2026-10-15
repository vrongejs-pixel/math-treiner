import streamlit as st
import random
from datetime import datetime, timedelta

st.set_page_config(page_title="Академия Юного Инженера — Имрон", page_icon="🚀", layout="centered")

# Функция голосовой озвучки в браузере
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

# Инициализация глобального состояния и копилки
if "state" not in st.session_state:
    st.session_state.state = {
        "earned_money": 0,
        "solved_total": 0,
        "correct_total": 0,
        "marathon_last_success": None,
        "timed_mode_last_use": None
    }

st.title("🚀 Академия юного инженера: ИМРОН")
st.write("Привет, Имрон! Выбирай любой раздел, тренируй ум, решай задачи и зарабатывай сумы!")

# Боковое меню: возвращаем все простые разделы + марафон и таймер
mode = st.sidebar.selectbox("Выбери раздел тренировки:", [
    "✖️ Таблица умножения", 
    "➕ Простая арифметика", 
    "📖 Текстовые задачи", 
    "🧠 Задачи для развития мышления",
    "🏆 Марафон 50 вопросов (Награда 5000 сум)", 
    "⏱️ Режим с таймером (Награда 10000 сум, раз в 2 часа)", 
    "📊 Статистика и Копилка"
])

now = datetime.now()

# --- РЕЖИМ: Таблица умножения ---
if mode == "✖️ Таблица умножения":
    st.header("✖️ Тренировка таблицы умножения")
    st.write("Свободный режим для оттачивания навыков умножения.")
    
    if 'mult_q' not in st.session_state:
        st.session_state.mult_q = None
        st.session_state.mult_ans = None

    if st.button("Следующий пример") or st.session_state.mult_q is None:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        st.session_state.mult_q = f"{a} × {b}"
        st.session_state.mult_ans = a * b

    st.markdown(f"### Сколько будет: **{st.session_state.mult_q}**?")
    user_ans = st.number_input("Твой ответ:", value=0, step=1, key="m_ans")

    if st.button("Проверить ответ", key="check_mult"):
        st.session_state.state["solved_total"] += 1
        if user_ans == st.session_state.mult_ans:
            st.session_state.state["correct_total"] += 1
            st.success("Молодец, Имрон! Верно! 🌟")
            speak_voice("Правильно, умница!")
            st.session_state.mult_q = None
        else:
            st.error(f"Ошибка! Правильный ответ: {st.session_state.mult_ans}. Попробуй еще раз!")

# --- РЕЖИМ: Простая арифметика ---
elif mode == "➕ Простая арифметика":
    st.header("➕ Простая арифметика (Сложение и вычитание)")
    
    if 'arith_q' not in st.session_state:
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
    user_ans_a = st.number_input("Твой ответ:", value=0, step=1, key="a_ans")

    if st.button("Проверить арифметику", key="check_arith"):
        st.session_state.state["solved_total"] += 1
        if user_ans_a == st.session_state.arith_ans:
            st.session_state.state["correct_total"] += 1
            st.success("Отлично, Имрон! Правильно! 👍")
            speak_voice("Отлично!")
            st.session_state.arith_q = None
        else:
            st.error(f"Неверно. Правильный ответ: {st.session_state.arith_ans}")

# --- РЕЖИМ: Текстовые задачи ---
elif mode == "📖 Текстовые задачи":
    st.header("📖 Текстовые задачи")
    
    tasks_list = [
        ("У Ирины было 4 коробки с карандашами, в каждой по 6 карандашей. Сколько всего карандашей у Ирины?", 24),
        ("В гараже стояло 15 машин. Уехали 7 машин. Сколько машин осталось в гараже?", 8),
        ("На трех полках стояло по 9 книг. Сколько всего книг на полках?", 27),
        ("У Саши было 50 сумов. Он купил тетрадь за 18 сумов. Сколько денег осталось?", 32),
        ("В автобусе ехало 28 пассажиров. На остановке зашло еще 14 человек. Сколько стало пассажиров?", 42)
    ]
    
    if 'task_idx' not in st.session_state:
        st.session_state.task_idx = random.randint(0, len(tasks_list) - 1)

    current_task, current_answer = tasks_list[st.session_state.task_idx]
    
    st.markdown(f"**Задача:** {current_task}")
    user_ans_t = st.number_input("Введите числовой ответ:", value=0, step=1, key="t_ans")

    if st.button("Проверить задачу", key="check_task"):
        st.session_state.state["solved_total"] += 1
        if user_ans_t == current_answer:
            st.session_state.state["correct_total"] += 1
            st.success("Верно, Имрон! Отличная логика! 🧠")
            speak_voice("Верно!")
            st.session_state.task_idx = random.randint(0, len(tasks_list) - 1)
        else:
            st.error("Подумай еще раз! Внимательно перечитай условие.")

# --- РЕЖИМ: Задачи для развития математического мышления ---
elif mode == "🧠 Задачи для развития мышления":
    st.header("🧠 Развитие математического мышления и логики")
    st.write("Интересные нестандартные задачи для тренировки сообразительности.")
    
    logic_list = [
        ("У отца 5 сыновей, и у каждого есть одна сестра. Сколько всего детей в семье?", 6),
        ("Росли 3 березы. На каждой березе по 4 больших ветки. На каждой ветке по 2 яблока. Сколько всего яблок?", 0),
        ("Два отца и два сына поймали 3 рыбы, и каждому досталось по одной рыбе. Как такое могло быть?", 3),
        ("Патрульная машина проехала 20 км на север, потом 20 км на восток, потом 20 км на юг. Сколько километров до участка, если ехать напрямую? (Напишите число)", 20),
        ("У бабушки жили внук Федя, кот Пушок, собака Дружок. Сколько всего ног у этих обитателей в доме?", 10) # 2+4+4 = 10
    ]
    
    if 'logic_idx' not in st.session_state:
        st.session_state.logic_idx = random.randint(0, len(logic_list) - 1)

    c_task, c_ans = logic_list[st.session_state.logic_idx]
    
    st.markdown(f"**Логическая задачка:** {c_task}")
    user_logic_ans = st.number_input("Ваш ответ (число):", value=0, step=1, key="logic_ans_val")

    if st.button("Проверить логику", key="check_logic_btn"):
        st.session_state.state["solved_total"] += 1
        if user_logic_ans == c_ans:
            st.session_state.state["correct_total"] += 1
            st.success("Гениально! Ты отлично мыслишь логически! 🏆")
            speak_voice("Ты умница, Имрон!")
            st.session_state.logic_idx = random.randint(0, len(logic_list) - 1)
        else:
            st.error("Неправильно. Попробуй порассуждать по-другому!")

# --- РЕЖИМ: Марафон 50 вопросов ---
elif mode == "🏆 Марафон 50 вопросов (Награда 5000 сум)":
    st.header("🏆 Марафон: 50 вопросов без права на ошибку")
    st.write("Пройди все 50 вопросов без единого промаха и получи 5000 сум! Каждые 10 вопросов — голосовая поддержка.")
    
    can_play_marathon = True
    if st.session_state.state["marathon_last_success"] is not None:
        time_passed = now - st.session_state.state["marathon_last_success"]
        if time_passed < timedelta(hours=2):
            remaining = timedelta(hours=2) - time_passed
            mins_left = int(remaining.total_seconds() // 60)
            can_play_marathon = False
            st.warning(f"⏳ Следующая попытка марафона откроется через {mins_left} минут (доступно раз в 2 часа после победы).")

    if can_play_marathon:
        if 'm_active' not in st.session_state:
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
            
            user_m_ans = st.number_input("Твой ответ:", value=0, step=1, key="m_input_val")
            
            if st.button("Ответить"):
                st.session_state.state["solved_total"] += 1
                if user_m_ans == st.session_state.m_ans:
                    st.session_state.state["correct_total"] += 1
                    
                    if st.session_state.m_step in [10, 20, 30, 40]:
                        speak_voice("Ты заработал 1000 сум, так держать!")
                        st.info("💡 Напоминание: Ты заработал 1000 сум за каждые 10 вопросов!")

                    if st.session_state.m_step >= 50:
                        st.session_state.state["earned_money"] += 5000
                        st.session_state.state["marathon_last_success"] = now
                        speak_voice("Ты умница, Имрон! Марафон успешно пройден!")
                        st.success("🎉 ПОЗДРАВЛЯЕМ! Ты прошел весь марафон без промахов и заработал 5000 сум!")
                        st.session_state.m_active = False
                    else:
                        st.session_state.m_step += 1
                        if random.choice([True, False]):
                            a = random.randint(2, 9)
                            b = random.randint(2, 9)
                            st.session_state.m_q = f"{a} × {b}"
                            st.session_state.m_ans = a * b
                        else:
                            a = random.randint(15, 50)
                            b = random.randint(10, 40)
                            if random.choice([True, False]):
                                st.session_state.m_q = f"{a} + {b}"
                                st.session_state.m_ans = a + b
                            else:
                                st.session_state.m_q = f"{a} - {b}"
                                st.session_state.m_ans = a - b
                        st.rerun()
                else:
                    st.error(f"❌ Ошибка на вопросе №{st.session_state.m_step}! Правильный ответ: {st.session_state.m_ans}. Марафон сброшен.")
                    speak_voice("Ничего страшного, попробуй еще раз.")
                    st.session_state.m_active = False

# --- РЕЖИМ: Таймер-режим (1 раз в 2 часа) ---
elif mode == "⏱️ Режим с таймером (Награда 10000 сум, раз в 2 часа)":
    st.header("⏱️ Интеллектуальный этап с защитой от перегрева")
    st.info("💡 Доступно **1 раз в 2 часа**. Награда за прохождение — **10 000 сум**!")

    can_play_timed = True
    if st.session_state.state["timed_mode_last_use"] is not None:
        elapsed = now - st.session_state.state["timed_mode_last_use"]
        if elapsed < timedelta(hours=2):
            left_time = timedelta(hours=2) - elapsed
            h_l = int(left_time.total_seconds() // 3600)
            m_l = int((left_time.total_seconds() % 3600) // 60)
            can_play_timed = False
            st.warning(f"⏳ Мозг отдыхает! Этот режим будет доступен через {h_l} ч. {m_l} мин.")

    if can_play_timed:
        if 't_started' not in st.session_state:
            st.session_state.t_started = False
            st.session_state.t_step = 1
            st.session_state.t_q = None
            st.session_state.t_ans = None

        if not st.session_state.t_started:
            if st.button("🚀 Начать сеанс (10 000 сум)"):
                st.session_state.t_started = True
                st.session_state.t_step = 1
                a = random.randint(10, 50)
                b = random.randint(10, 50)
                st.session_state.t_q = f"{a} + {b}"
                st.session_state.t_ans = a + b
                st.rerun()
        else:
            st.markdown(f"### Этап с таймером: Вопрос {st.session_state.t_step} из 10")
            st.markdown(f"**Сколько будет: {st.session_state.t_q}**?")
            
            user_t_ans = st.number_input("Твой ответ:", value=0, step=1, key="timed_input_val")
            
            if st.button("Проверить таймер-вопрос"):
                st.session_state.state["solved_total"] += 1
                if user_t_ans == st.session_state.t_ans:
                    st.session_state.state["correct_total"] += 1
                    
                    if st.session_state.t_step >= 10:
                        st.session_state.state["earned_money"] += 10000
                        st.session_state.state["timed_mode_last_use"] = now
                        speak_voice("Ты умница, Имрон! Сеанс с таймером пройден, ты заработал 10 тысяч сум!")
                        st.success("🏆 Великолепно! Ты успешно завершил этап с таймером и заработал 10 000 сум!")
                        st.session_state.t_started = False
                    else:
                        st.session_state.t_step += 1
                        a = random.randint(20, 99)
                        b = random.randint(10, 50)
                        if random.choice([True, False]):
                            st.session_state.t_q = f"{a} + {b}"
                            st.session_state.t_ans = a + b
                        else:
                            st.session_state.t_q = f"{a} - {b}"
                            st.session_state.t_ans = a - b
                        st.rerun()
                else:
                    st.error("❌ Ошибка! Таймер-режим прерван.")
                    st.session_state.t_started = False

# --- РЕЖИМ: Статистика и Копилка ---
elif mode == "📊 Статистика и Копилка":
    st.header("📊 Статистика успехов Имрона")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Всего решено", value=st.session_state.state["solved_total"])
    with col2:
        st.metric(label="Правильных", value=st.session_state.state["correct_total"])
    with col3:
        st.metric(label="💰 Общая копилка", value=f"{st.session_state.state['earned_money']} сум")
        
    st.info("💡 В приложении доступны как свободные тренировочные разделы (умножение, арифметика, задачи, мышление), так и премиум-марафоны с наградами!")
