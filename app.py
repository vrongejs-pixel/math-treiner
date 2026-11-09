from datetime import datetime, date
import json
import os
import random
import streamlit as st

st.set_page_config(page_title="Академия юного инженера — Имрон", page_icon="🚀", layout="wide")

DATA_FILE = "imron_data.json"

DEFAULTS = {
    "solved_total": 0, "correct_total": 0,
    "mult_correct_count": 0, "arith_correct_count": 0, "text_correct_count": 0,
    "mult_money": 0, "arith_money": 0, "text_money": 0, "logic_money": 0,
    "marathon_money": 0, "sprint_money": 0, "logic_solved_ids": [],
    "text_solved_ids": [], "marathon_last_success": None, "timed_mode_last_use": None,
    "earnings_history": [], "robot_money": 0, "robot_solved_ids": [],
    "skill": {}, "daily_activity": {}, "marathon_attempts": {}, "marathon_best": 0,
    "errors_total": 0, "help_used": 0
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return DEFAULTS.copy()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            raise ValueError("Файл данных должен содержать объект JSON")
        data = DEFAULTS.copy()
        data.update(raw)
        if not isinstance(data.get("earnings_history"), list):
            data["earnings_history"] = []
        return data
    except Exception as exc:
        st.error("Не удалось прочитать файл накоплений. Исходный файл не изменён. Сделай резервную копию и проверь JSON.")
        st.code(str(exc))
        st.stop()

def save_data():
    data = st.session_state.academy
    temp = DATA_FILE + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp, DATA_FILE)

if "academy" not in st.session_state:
    st.session_state.academy = load_data()
if "current" not in st.session_state:
    st.session_state.current = None
if "marathon" not in st.session_state:
    st.session_state.marathon = None

D = st.session_state.academy

def award(amount, source):
    D["earnings_history"].append({"date": datetime.now().isoformat(), "amount": amount, "source": source})
    key = {"Математика": "mult_money", "Логика": "logic_money", "Текстовые задачи": "text_money",
           "Марафон": "marathon_money", "Спринт": "sprint_money"}.get(source, "arith_money")
    D[key] = D.get(key, 0) + amount
    save_data()

def level(section):
    return max(1, min(5, int(D.get("skill", {}).get(section, 1))))

def adjust_level(section, correct):
    skills = D.setdefault("skill", {})
    old = level(section)
    record = skills.setdefault(section, {"right": 0, "wrong": 0, "streak": 0})
    if correct:
        record["right"] += 1
        record["streak"] += 1
        if record["streak"] >= 3 and old < 5:
            skills[section] = {"right": record["right"], "wrong": record["wrong"], "streak": 0}
            skills[section]["level"] = old + 1
            st.success("Ты уверенно справляешься! Сложность повышена.")
        else:
            skills[section]["level"] = old
    else:
        record["wrong"] += 1
        record["streak"] = 0
        skills[section]["level"] = max(1, old - 1) if record["wrong"] % 3 == 0 else old
    save_data()

def new_question(section):
    L = level(section)
    if section == "Математика":
        if L == 1:
            a, b = random.randint(12, 40), random.randint(2, 9)
            op = random.choice(["×", "+", "-"])
        elif L == 2:
            a, b = random.randint(20, 99), random.randint(2, 12)
            op = random.choice(["×", "÷", "+", "-"])
        elif L == 3:
            a, b = random.randint(100, 999), random.randint(2, 12)
            op = random.choice(["×", "÷", "+", "-"])
        elif L == 4:
            a, b = random.randint(20, 99), random.randint(10, 30)
            op = random.choice(["×", "+", "-"])
        else:
            a, b = random.randint(100, 999), random.randint(10, 25)
            op = random.choice(["×", "+", "-"])
        if op == "÷":
            b = random.randint(2, 12); ans = random.randint(3, 20); a = b * ans
        else:
            ans = a*b if op == "×" else a+b if op == "+" else a-b
        return {"q": f"{a} {op} {b} = ?", "answer": ans,
                "hint": "Определи действие. Разложи большое число на удобные части и считай по разрядам.",
                "solution": f"Выполни действие {a} {op} {b}. Получается {ans}. Проверь обратным действием."}
    if section == "Логика":
        bank = [
            ("Продолжи ряд: 2, 4, 8, 16, ...", 32, "Каждое следующее число в 2 раза больше.", "16 × 2 = 32."),
            ("У пяти братьев одна общая сестра. Сколько всего детей?", 6, "Сестра у всех братьев одна и та же.", "5 братьев + 1 сестра = 6 детей."),
            ("На столе 4 яблока. Ты взял 2. Сколько яблок у тебя?", 2, "Считай только те яблоки, которые ты взял.", "Ты взял 2 яблока, значит у тебя 2."),
            ("Продолжи ряд: 3, 6, 12, 24, ...", 48, "Каждый раз число удваивается.", "24 × 2 = 48."),
            ("У квадрата отрезали один угол прямой линией. Сколько углов стало?", 5, "Представь, что один угол срезали, а на его месте появился новый отрезок.", "Было 4 угла; после среза стало 5.")
        ]
        item = random.choice(bank)
        return {"q": item[0], "answer": item[1],
                "hint": item[2], "solution": item[3]}
    if section == "Текстовые задачи":
        a = random.randint(3, 12) + L
        b = random.randint(2, 8)
        return {"q": f"В {a} коробках лежит по {b} деталей. 3 детали использовали. Сколько деталей осталось?",
                "answer": a*b-3, "hint": "Сначала найди общее количество деталей во всех коробках, затем вычти использованные.",
                "solution": f"Сначала умножаем: {a} × {b} = {a*b}. Затем вычитаем 3: {a*b} − 3 = {a*b-3}."}
    if section == "Физика и инженерия":
        bank = [
            ("Почему длинная ручка легче открывает тугую крышку?", 1, "Подумай, что меняется, когда точка приложения силы дальше от оси.", "Длинная ручка увеличивает плечо силы. Вариант ответа: 1 — увеличивается плечо силы."),
            ("Что быстрее нагреется на солнце: чёрная или белая поверхность?", 1, "Тёмные поверхности обычно поглощают больше солнечного излучения.", "Чёрная поверхность обычно нагревается быстрее. Вариант ответа: 1."),
            ("Какой простой механизм помогает поднять тяжёлый груз с меньшей силой: блок или гладкая доска?", 1, "Вспомни колесо с верёвкой, которое меняет направление силы.", "Блок помогает поднимать груз. Вариант ответа: 1.")
        ]
        q = random.choice(bank)
        return {"q": q[0] + " (введи 1)", "answer": 1, "hint": q[2], "solution": q[3]}
    if section == "Память и внимание":
        n = random.randint(2, 8) + L
        return {"q": f"Вычисли в уме и запомни результат: {n} × 3 + 2. Какой ответ?",
                "answer": n*3+2, "hint": "Сначала умножь, затем прибавь 2. Не торопись.",
                "solution": f"{n} × 3 = {n*3}; {n*3} + 2 = {n*3+2}."}
    if section == "Стратегия":
        n = random.choice([12, 15, 18, 21, 24]) + (L-1)*3
        return {"q": f"В игре нужно набрать {n} очков. За ход можно получить 3 или 5 очков. Можно ли набрать ровно {n}? Введи 1 — да, 0 — нет.",
                "answer": 1 if any((n-5*k) >= 0 and (n-5*k) % 3 == 0 for k in range(n//5+1)) else 0,
                "hint": "Попробуй вычитать по 5, а остаток проверить делением на 3.",
                "solution": "Перебери возможное число ходов по 5 очков. Остаток должен делиться на 3."}
    return {"q": "Придумай число, которое при умножении на 4 и прибавлении 6 даёт 30. Введи число.",
            "answer": 6, "hint": "Сначала убери прибавленные 6, затем раздели результат на 4.",
            "solution": "30 − 6 = 24; 24 ÷ 4 = 6. Значит, исходное число — 6."}

LESSONS = {
"Математика": ("Математическая лаборатория", "Изучаем вычисления, умножение и деление столбиком, дроби, измерения, периметр и площадь. Главное — понимать смысл действий, а не только запоминать ответы."),
"Логика": ("Лаборатория логики", "Ищем закономерности, учимся проверять гипотезы, замечать ловушки в формулировках и объяснять, почему ответ верен."),
"Физика и инженерия": ("Мир инженера", "Разбираем силу, рычаги, блоки, трение, тепло, электрические цепи и устройство простых механизмов. Любое объяснение связываем с реальными предметами."),
"Память и внимание": ("Тренировка памяти", "Развиваем концентрацию, рабочую память, последовательность действий и внимательность к деталям."),
"Стратегия": ("Стратегическое мышление", "Учимся планировать несколько ходов вперёд, сравнивать варианты и выбирать решение с учётом последствий."),
"Творчество": ("Мастерская изобретателя", "Учимся ставить задачу, придумывать несколько вариантов, выбирать лучший и объяснять свою идею."),
"Текстовые задачи": ("Школа рассуждений", "Учимся читать условие, выделять известное и неизвестное, составлять план решения и проверять результат.")
}

st.title("🚀 Академия юного инженера — Имрон")
st.caption("Учись понимать, рассуждать, создавать и проверять свои идеи.")
sections = ["Математика", "Логика", "Физика и инженерия", "Память и внимание", "Текстовые задачи", "Стратегия", "Творчество", "Марафон 50 вопросов", "Инженерный спринт", "Статистика и копилка"]
mode = st.sidebar.selectbox("Выбери направление", sections)

if mode in LESSONS:
    title, theory = LESSONS[mode]
    st.header(title)
    st.info(theory)
    st.subheader("Как работаем")
    st.write("1. Прочитай объяснение. 2. Реши задание самостоятельно. 3. Если трудно — нажми «Помоги понять». 4. После попытки изучи разбор.")
    st.write(f"Текущий уровень: **{level(mode)} из 5**. Три уверенных правильных ответа подряд повышают сложность.")
    if mode == "Математика":
        with st.expander("Урок: умножение по разрядам"):
            st.write("Пример: 23 × 4. Разложи 23 на 20 и 3. Умножь каждую часть: 20 × 4 = 80, 3 × 4 = 12. Сложи: 80 + 12 = 92.")
        with st.expander("Урок: проверка деления"):
            st.write("Если 84 ÷ 4 = 21, проверь обратным действием: 21 × 4 = 84. Если получилось исходное число, деление проверено.")
        with st.expander("Следующие темы курса"):
            st.write("Деление с остатком → скобки и порядок действий → дроби как части целого → периметр и площадь → задачи на время, скорость и расстояние → проценты и олимпиадные задачи.")
    elif mode == "Физика и инженерия":
        with st.expander("Урок: рычаг"):
            st.write("Рычаг — твёрдая планка, которая поворачивается вокруг опоры. Чем дальше от опоры приложить силу, тем легче повернуть предмет. Пример: длинный ключ помогает открутить тугую гайку.")
        with st.expander("Безопасный опыт"):
            st.write("Положи линейку на круглый карандаш и слегка надави на один конец. Понаблюдай, как меняется усилие при перемещении точки опоры. Не используй тяжёлые или острые предметы.")
    elif mode == "Логика":
        with st.expander("Метод исследователя"):
            st.write("1. Найди, что меняется. 2. Предложи правило. 3. Проверь его на нескольких шагах. 4. Попробуй найти контрпример.")
    if mode == "Творчество":
        idea = st.text_area("Мастерская: опиши своё изобретение и какую проблему оно решает")
        if st.button("Сохранить идею"):
            D.setdefault("ideas", []).append({"date": datetime.now().isoformat(), "text": idea})
            save_data()
            st.success("Идея сохранена в журнале изобретателя.")
    if st.button("🎯 Получить задание", key="new_"+mode):
        st.session_state.current = {"section": mode, **new_question(mode)}
    task = st.session_state.current
    if task and task.get("section") == mode:
        st.markdown("---")
        st.subheader("Задание")
        st.markdown("### " + task["q"])
        with st.expander("💡 Помоги понять"):
            st.write(task["hint"])
            D["help_used"] = D.get("help_used", 0) + 1
            save_data()
        with st.expander("📘 Показать решение"):
            st.write(task["solution"])
        answer = st.text_input("Твой ответ (число)", key="answer_"+mode)
        if st.button("Проверить", key="check_"+mode):
            if answer.strip().lstrip("-").isdigit():
                D["solved_total"] += 1
                if int(answer.strip()) == task["answer"]:
                    D["correct_total"] += 1
                    adjust_level(mode, True)
                    reward = 100 if level(mode) <= 2 else 200 if level(mode) <= 4 else 300
                    award(reward, mode)
                    st.success(f"Верно! Ты заработал {reward} сум. Отличная работа!")
                    st.session_state.current = None
                else:
                    D["errors_total"] = D.get("errors_total", 0) + 1
                    adjust_level(mode, False)
                    save_data()
                    st.error("Ошибка — это не поражение, а возможность научиться чему-то новому.")
                    st.write("Попробуй ещё раз. Используй подсказку и проверь каждый шаг.")
                    st.write("Правильный ответ:", task["answer"])
                    st.write("Разбор:", task["solution"])
            else:
                st.warning("Введи ответ числом.")

elif mode == "Марафон 50 вопросов":
    st.header("🏆 Большой марафон — 50 заданий")
    today = date.today().isoformat()
    attempts = D.setdefault("marathon_attempts", {})
    used = attempts.get(today, 0)
    st.write(f"Попыток сегодня: {used} из 2. Для награды нужно набрать минимум 40 правильных ответов из 50.")
    if st.session_state.marathon is None:
        if used >= 2:
            st.warning("Сегодня обе попытки использованы. Завтра можно будет попробовать снова.")
        elif st.button("Начать марафон"):
            attempts[today] = used + 1
            st.session_state.marathon = {"step": 1, "right": 0, "wrong": 0, "question": new_question("Математика")}
            save_data()
            st.rerun()
    else:
        m = st.session_state.marathon
        st.progress(m["step"]/50)
        st.subheader(f"Вопрос {m['step']} из 50")
        st.markdown("### "+m["question"]["q"])
        with st.expander("💡 Помоги понять"):
            st.write(m["question"]["hint"])
        with st.expander("📘 Показать решение"):
            st.write(m["question"]["solution"])
        ans = st.text_input("Ответ", key=f"marathon_{m['step']}")
        if st.button("Проверить ответ", key="marathon_check"):
            if ans.strip().lstrip("-").isdigit():
                D["solved_total"] += 1
                if int(ans) == m["question"]["answer"]:
                    m["right"] += 1
                    D["correct_total"] += 1
                    st.success("Верно!")
                    m["step"] += 1
                    if m["step"] <= 50:
                        m["question"] = new_question("Математика")
                else:
                    m["wrong"] += 1
                    D["errors_total"] = D.get("errors_total", 0) + 1
                    st.error("Ошибка — это не поражение, а возможность научиться чему-то новому.")
                    st.write("Правильный ответ:", m["question"]["answer"])
                    st.write(m["question"]["solution"])
                    st.info("Марафон продолжается. Ошибка не сбрасывает твой результат.")
                if m["step"] > 50:
                    D["marathon_best"] = max(D.get("marathon_best", 0), m["right"])
                    if m["right"] >= 40:
                        award(15000, "Марафон")
                        D["marathon_last_success"] = datetime.now().isoformat()
                        st.balloons()
                        st.success(f"Марафон пройден: {m['right']} из 50! Награда — 15 000 сум.")
                    else:
                        st.info(f"Финиш! Результат: {m['right']} из 50. Нужно 40. Изучи ошибки и попробуй в следующий раз.")
                    st.session_state.marathon = None
                save_data()
                st.rerun()
            else:
                st.warning("Введи число.")
        if st.button("Завершить марафон"):
            st.session_state.marathon = None
            save_data()
            st.rerun()

elif mode == "Инженерный спринт":
    st.header("⏱️ Инженерный спринт")
    st.write("Семь заданий на математику и логику. Здесь тренируем точность и скорость, но ошибки разбираем спокойно.")
    if st.button("Начать тренировку"):
        st.session_state.current = {"section": "Математика", **new_question("Математика")}
        st.session_state.sprint_step = 1
    if st.session_state.get("sprint_step"):
        st.write(f"Задание {st.session_state.sprint_step} из 7")
        t = st.session_state.current
        if t:
            st.markdown("### "+t["q"])
            with st.expander("💡 Помоги понять"): st.write(t["hint"])
            with st.expander("📘 Показать решение"): st.write(t["solution"])
            a = st.text_input("Ответ", key=f"sprint_{st.session_state.sprint_step}")
            if st.button("Проверить задание"):
                if a.strip().lstrip("-").isdigit() and int(a) == t["answer"]:
                    D["correct_total"] += 1
                    st.session_state.sprint_step += 1
                    if st.session_state.sprint_step > 7:
                        award(10000, "Спринт")
                        st.success("Спринт завершён! Награда — 10 000 сум.")
                        del st.session_state["sprint_step"]
                        st.session_state.current = None
                    else:
                        st.session_state.current = {"section": "Математика", **new_question("Математика")}
                    save_data()
                    st.rerun()
                else:
                    D["errors_total"] = D.get("errors_total", 0) + 1
                    save_data()
                    st.error("Ошибка — это не поражение, а возможность научиться чему-то новому.")
                    st.write("Ответ:", t["answer"], "Разбор:", t["solution"])

else:
    st.header("📊 Статистика и копилка Имрона")
    total = sum(D.get(k, 0) for k in ["mult_money","arith_money","text_money","logic_money","marathon_money","sprint_money","robot_money"])
    c1,c2,c3 = st.columns(3)
    c1.metric("Решено заданий", D.get("solved_total",0))
    c2.metric("Правильных ответов", D.get("correct_total",0))
    c3.metric("Копилка", f"{total:,} сум".replace(",", " "))
    st.metric("Ошибки — опыт для роста", D.get("errors_total",0))
    st.metric("Лучший результат марафона", f"{D.get('marathon_best',0)} / 50")
    st.subheader("История наград")
    for item in reversed(D.get("earnings_history", [])):
        st.write(f"{item.get('date','')} — +{item.get('amount',0)} сум ({item.get('source','')})")
    st.download_button("Скачать резервную копию накоплений", json.dumps(D, ensure_ascii=False, indent=2), file_name="imron_data_backup.json", mime="application/json")
    st.caption("Совет: периодически скачивай резервную копию. Локальный JSON на Streamlit Cloud не является гарантированным постоянным хранилищем.")
