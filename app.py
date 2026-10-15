import streamlit as st
import random
import time
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

# Инициализация глобального состояния и таймеров блокировки (каждые 2 часа)
if "state" not in st.session_state:
    st.session_state.state = {
        "earned_money": 0,
        "solved_total": 0,
        "correct_total": 0,
        "marathon_last_success": None,  # Время последнего успешного марафона
        "timed_mode_last_use": None    # Время последнего использования таймер-режима
    }

st.title("🚀 Академия юного инженера: ИМРОН")
st.write("Привет, Имрон! Выбирай режим, зарабатывай сумы и прокачивай свой ум!")

# Боковое меню
mode = st.sidebar.selectbox("Выбери режим:", [
    "🏆 Марафон 50 вопросов (Награда 5000 сум)", 
    "⏱️ Умный режим с таймером (Награда 10000 сум, раз в 2 часа)", 
    "📊 Статистика и Копилка"
])

# Текущее время для проверки 2-часовых интервалов
now = datetime.now()

# --- РЕЖИМ 1: МАРАФОН 50 ВОПРОСОВ ---
if mode == "🏆 Марафон 50 вопросов (Награда 5000 сум)":
    st.header("🏆 Марафон: 50 вопросов без права на ошибку")
    st.write("Пройди все 50 вопросов без единого промаха и получи 5000 сум в копилку! Каждые 10 правильных ответов тебя ждет голосовая поддержка.")
    
    # Проверка таймера для успешного марафона (раз в 2 часа после успеха)
    can_play_marathon = True
    marathon_wait_msg = ""
    if st.session_state.state["marathon_last_success"] is not None:
        time_passed = now - st.session_state.state["marathon_last_success"]
        if time_passed < timedelta(hours=2):
            remaining = timedelta(hours=2) - time_passed
            mins_left = int(remaining.total_seconds() // 60)
            can_play_marathon = False
            marathon_wait_msg = f"⏳ Ты уже успешно прошел марафон! Следующая попытка откроется через {mins_left} минут (доступно раз в 2 часа)."

    if not can_play_marathon:
        st.warning(marathon_wait_msg)
    else:
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
                    
                    # Каждые 10 правильных ответов — напоминание голосом
                    if st.session_state.m_step in [10, 20, 30, 40]:
                        speak_voice("Ты заработал 1000 сум, так держать!")
                        st.info(f"💡 Напоминание: Ты заработал 1000 сум за каждые 10 вопросов!")

                    if st.session_state.m_step >= 50:
                        # Успешное завершение всего марафона
                        st.session_state.state["earned_money"] += 5000
                        st.session_state.state["marathon_last_success"] = now
                        speak_voice("Ты умница, Имрон! Марафон успешно пройден!")
                        st.success("🎉 ПОЗДРАВЛЯЕМ! Ты прошел весь марафон без промахов и заработал 5000 сум! Запись добавлена в статистику.")
                        st.session_state.m_active = False
                    else:
                        st.session_state.m_step += 1
                        # Генерация следующего вопроса (микс умножения и арифметики)
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
                    st.error(f"❌ Ошибка на вопросе №{st.session_state.m_step}! Правильный ответ: {st.session_state.m_ans}. Марафон сброшен, но ты можешь начать его заново прямо сейчас!")
                    speak_voice("Ничего страшного, Имрон, попробуй еще раз.")
                    st.session_state.m_active = False

# --- РЕЖИМ 2: ТАЙМЕР-РЕЖИМ (1 РАЗ В 2 ЧАСА, НАГРАДА 10000 СУМ) ---
elif mode == "⏱️ Умный режим с таймером (Награда 10000 сум, раз в 2 часа)":
    st.header("⏱️ Интеллектуальный этап с защитой от перегрева")
    st.info("💡 Этот режим можно запускать **только 1 раз в 2 часа**, чтобы мозг отдыхал. За успешное прохождение — награда **10 000 сум**!")

    can_play_timed = True
    wait_msg = ""
    if st.session_state.state["timed_mode_last_use"] is not None:
        elapsed = now - st.session_state.state["timed_mode_last_use"]
        if elapsed < timedelta(hours=2):
            left_time = timedelta(hours=2) - elapsed
            h_l = int(left_time.total_seconds() // 3600)
            m_l = int((left_time.total_seconds() % 3600) // 60)
            can_play_timed = False
            wait_msg = f"⏳ Мозг отдыхает! Этот режим будет доступен через {h_l} ч. {m_l} мин."

    if not can_play_timed:
        st.warning(wait_msg)
    else:
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
                        # Успешно пройден таймер-режим
                        st.session_state.state["earned_money"] += 10000
                        st.session_state.state["timed_mode_last_use"] = now
                        speak_voice("Ты умница, Имрон! Сеанс с таймером пройден, ты заработал 10 тысяч сум!")
                        st.success("🏆 Великолепно! Ты успешно завершил этап с таймером и заработал 10 000 сум в копилку! Следующий сеанс откроется через 2 часа.")
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
                    st.error("❌ Ошибка! Таймер-режим прерван. Попробуй еще раз, когда отдохнешь.")
                    st.session_state.t_started = False

# --- РЕЖИМ 3: СТАТИСТИКА И КОПИЛКА ---
elif mode == "📊 Статистика и Копилка":
    st.header("📊 Статистика успехов Имрона")
    st.write("Здесь отображается общая копилка и результаты выполненных заданий.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Всего решено", value=st.session_state.state["solved_total"])
    with col2:
        st.metric(label="Правильных", value=st.session_state.state["correct_total"])
    with col3:
        st.metric(label="💰 Общая копилка", value=f"{st.session_state.state['earned_money']} сум")
        
    st.info("💡 **Как устроены стимулы:**\n- Марафон (50 вопросов): приносит **5000 сум** при успешном прохождении. При ошибке можно повторять бесконечно, а при успехе — повторять каждые 2 часа. Каждые 10 вопросов озвучивается бонус 1000 сум.\n- Режим с таймером: приносит **10 000 сум**, защищает мозг от перегрузки и доступен ровно 1 раз в 2 часа!")
   
                     
                   
           
