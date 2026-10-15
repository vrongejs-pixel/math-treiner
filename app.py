import streamlit as st
import random
import time

st.title("🚀 Тренажер юного инженера по математике")
st.write("Привет! Прокачай свои навыки счета, чтобы в будущем конструировать ракеты, мосты и роботов!")

# Выбор режима в боковом меню
mode = st.sidebar.selectbox("Выбери режим тренировки:", ["Таблица умножения", "Простая арифметика", "Тест на скорость (Таймер)"])

if mode == "Таблица умножения":
    st.header("✖️ Тренировка таблицы умножения")
    
    if 'mult_score' not in st.session_state:
        st.session_state.mult_score = 0
        st.session_state.mult_q = None
        st.session_state.mult_ans = None

    if st.button("Следующий пример") or st.session_state.mult_q is None:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        st.session_state.mult_q = f"{a} × {b}"
        st.session_state.mult_ans = a * b

    st.markdown(f"### Сколько будет: **{st.session_state.mult_q}**?")
    user_ans = st.number_input("Твой ответ:", value=0, step=1, key="m_ans")
    
    if st.button("Проверить"):
        if user_ans == st.session_state.mult_ans:
            st.success("🎉 Правильно! Отличная работа инженера!")
            st.session_state.mult_score += 1
        else:
            st.error(f"❌ Ошибка. Правильный ответ: {st.session_state.mult_ans}")
        st.write(f"Твой текущий счет: {st.session_state.mult_score}")

elif mode == "Простая арифметика":
    st.header("➕➖ Простые расчеты")
    
    if 'arith_score' not in st.session_state:
        st.session_state.arith_score = 0
        st.session_state.arith_q = None
        st.session_state.arith_ans = None

    if st.button("Новый пример") or st.session_state.arith_q is None:
        op = random.choice(['+', '-', '*'])
        if op == '+':
            a = random.randint(10, 100)
            b = random.randint(10, 100)
            res = a + b
        elif op == '-':
            a = random.randint(20, 100)
            b = random.randint(1, a)
            res = a - b
        else:
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            res = a * b
        
        st.session_state.arith_q = f"{a} {op} {b}"
        st.session_state.arith_ans = res

    st.markdown(f"### Реши пример: **{st.session_state.arith_q}** = ?")
    user_ans = st.number_input("Ответ:", value=0, step=1, key="a_ans")

    if st.button("Проверить ответ"):
        if user_ans == st.session_state.arith_ans:
            st.success("🎯 Верно! Абсолютная точность!")
            st.session_state.arith_score += 1
        else:
            st.error(f"❌ Неверно. Правильно: {st.session_state.arith_ans}")
        st.write(f"Твой текущий счет: {st.session_state.arith_score}")

elif mode == "Тест на скорость (Таймер)":
    st.header("⏱️ Экзамен на скорость счета")
    st.write("Реши 5 примеров как можно быстрее! Секундомер запущен.")
    
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
        st.session_state.test_questions = []
        st.session_state.start_time = 0

    if not st.session_state.test_started:
        if st.button("Начать испытание!"):
            st.session_state.test_started = True
            st.session_state.start_time = time.time()
            st.session_state.test_questions = []
            for _ in range(5):
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                st.session_state.test_questions.append((f"{a} × {b}", a * b))
            st.rerun()
    else:
        user_inputs = []
        for i, (q, ans) in enumerate(st.session_state.test_questions):
            val = st.number_input(f"Пример {i+1}: {q} =", value=0, step=1, key=f"t_{i}")
            user_inputs.append(val)
        
        if st.button("Завершить и проверить время"):
            elapsed_time = round(time.time() - st.session_state.start_time, 1)
            correct = 0
            for (q, ans), user_val in zip(st.session_state.test_questions, user_inputs):
                if user_val == ans:
                    correct += 1
            
            st.success(f"🏆 Тест пройден за {elapsed_time} секунд!")
            st.info(f"Правильных ответов: {correct} из 5")
            
            if correct == 5:
                st.balloons()
                st.write("🌟 Невероятно! Настоящий будущий инженер!")
            
            if st.button("Пройти еще раз"):
                st.session_state.test_started = False
                st.rerun()
