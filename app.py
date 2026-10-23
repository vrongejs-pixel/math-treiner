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
        "robot_money": 0,
        "marathon_money": 0,
        "sprint_money": 0,
        "logic_solved_ids": [],
        "text_solved_ids": [],
        "robot_solved_ids": [],
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
    "Привет, Имрон! Изучай робототехнику, тренируй счет, решай задачи и пополняй свою копилку!"
)

# Боковое меню: все разделы
mode = st.sidebar.selectbox(
    "Выбери раздел тренировки:",
    [
        "👨‍🏫 Репетитор (Учимся и разбираем правила с примерами)",
        "🤖 Робототехника и LEGO (Машины и механика)",
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


# --- РЕЖИМ: РЕПЕТИТОР ---
if mode == "👨‍🏫 Репетитор (Учимся и разбираем правила с примерами)":
    st.header("👨‍🏫 Персональный Репетитор Имрона")
    st.write("Здесь собраны подробные объяснения всех тем за 4 класс с множеством понятных примеров. Сначала изучи теорию, а потом переходи к тренировкам!")

    st.markdown("---")
    st.subheader("📌 Тема 1: Поразрядное сложение и вычитание в уме")
    st.write("Когда нужно сложить большие двузначные числа, считай по шагам: сначала десятки, потом единицы.")
    st.info(
        "**Примеры для тренировки:**\n"
        "- `47 + 32` ➡️ 40+30=70, 7+2=9, вместе **79**\n"
        "- `54 + 23` ➡️ 50+20=70, 4+3=7, вместе **77**\n"
        "- `86 - 34` ➡️ 80-30=50, 6-4=2, вместе **52**\n"
        "- `68 - 25` ➡️ 60-20=40, 8-5=3, вместе **43**"
    )

    st.markdown("---")
    st.subheader("📌 Тема 2: Метод округления при вычитании")
    st.write("Если вычитаемое число близко к круглому (например, 28), проще отнять круглое число, а потом вернуть лишнее.")
    st.info(
        "**Примеры для тренировки:**\n"
        "- `64 - 28` ➡️ Отнимаем 30 (получилось 34), возвращаем 2 ➡️ **36**\n"
        "- `83 - 39` ➡️ Отнимаем 40 (получилось 43), возвращаем 1 ➡️ **44**"
    )

    st.markdown("---")
    st.subheader("📌 Тема 3: Правило быстрого умножения на 9")
    st.write("Умножь число на 10 (припиши ноль), а затем вычти само число.")
    st.info(
        "**Примеры для тренировки:**\n"
        "- `7 × 9` ➡️ 7 × 10 = 70, отнимаем 7 ➡️ **63**\n"
        "- `8 × 9` ➡️ 8 × 10 = 80, отнимаем 8 ➡️ **72**"
    )

    st.markdown("---")
    st.subheader("📌 Тема 4: Задачи на движение (Скорость, Время, Расстояние)")
    st.write("Главная формула инженера: **Расстояние = Скорость × Время** ($S = v \times t$).")
    st.info(
        "**Примеры для тренировки:**\n"
        "- Поезд едет со скоростью 60 км/ч 3 часа. Расстояние = 60 × 3 = **180 км**.\n"
        "- Турист шел 4 часа со скоростью 5 км/ч. Расстояние = 5 × 4 = **20 км**."
    )


# --- РЕЖИМ: РОБОТОТЕХНИКА И LEGO (С ТЕОРИЕЙ И СХЕМАМИ) ---
elif mode == "🤖 Робототехника и LEGO (Машины и механика)":
    st.header("🤖 Лаборатория Робототехники и LEGO")
    st.write("Привет, юный инженер! В этом разделе ты найдешь секреты механики, чертежи и схемы сборки машин из LEGO Technic. Изучи теорию и решай инженерные задачи по **300 сум**!")

    st.markdown("---")
    st.subheader("⚙️ Урок механики №1: Зубчатые колеса (Шестеренки)")
    st.write("В конструкторах LEGO шестеренки передают вращение от мотора на колеса. Если маленькое колесо крутит большое, то скорость уменьшается, но машина получает **большую силу тяги** (чтобы заехать в гору!). А если большое крутит маленькое — машина едет быстрее.")
    st.info(
        "**Схема расчета передаточного числа:**\n"
        "Если на ведущем колесе **8 зубьев**, а на ведомом **24 зуба**, то маленькое колесо должно сделать ровно **3 оборота**, чтобы большое сделало 1 полный оборот ($24 \div 8 = 3$)."
    )

    st.markdown("---")
    st.subheader("🏎️ Урок механики №2: Прочность кузова и балки")
    st.write("Чтобы машинка из LEGO не развалилась при столкновении или быстрой езде, инженеры используют **перекрестное соединение балок** (соединение пинами минимум в двух точках). Это создает жесткий каркас.")

    st.markdown("---")
    st.subheader("🧠 Практикум: Инженерные задачи по робототехнике")

    robot_tasks = [
        {"id": 1, "q": "У тебя в конструкторе есть маленькое зубчатое колесо на 8 зубьев и большое колесо на 24 зуба. Во сколько раз большое колесо больше маленького?", "ans": 3},
        {"id": 2, "q": "Электромотор LEGO делает 60 оборотов в минуту. Сколько оборотов он сделает за 4 минуты?", "ans": 240},
        {"id": 3, "q": "Для постройки гоночной машины LEGO Technic понадобилось 4 колеса и по 12 деталей на каждое колесо. Сколько деталей ушло только на колеса?", "ans": 48},
        {"id": 4, "q": "Робот-исследователь проехал вперед 15 метров, а затем задним ходом 7 метров. На каком расстоянии от старта он оказался?", "ans": 8},
        {"id": 5, "q": "У робота есть 2 ультразвуковых датчика расстояния и 3 датчика касания. Сколько всего датчиков установлено на роботе?", "ans": 5},
        {"id": 6, "q": "Машина из LEGO проехала 50 см за 2 секунды. С какой скоростью (в см в секунду) она двигалась?", "ans": 25},
        {"id": 7, "q": "На сборку одного робота у Имрона уходит 45 минут. Сколько минут уйдет на сборку 3 таких роботов?", "ans": 135},
        {"id": 8, "q": "В наборе LEGO было 300 деталей. Для модели багги использовали 185 деталей. Сколько деталей осталось в коробке?", "ans": 115},
        {"id": 9, "q": "Чтобы шасси машины держалось прочно, инженер установил 4 балки по 12 соединительных штифтов на каждой. Сколько всего штифтов было использовано?", "ans": 48},
        {"id": 10, "q": "Скорость первой модели робота 10 см/с, а вторая модель едет вдвое быстрее. Какая скорость у второй модели (см/с)?", "ans": 20}
    ]

    if "current_robot_task" not in st.session_state or st.session_state.current_robot_task is None:
        available_robot = [t for t in robot_tasks if t["id"] not in st.session_state.state["robot_solved_ids"]]
        if not available_robot:
            st.success("🎉 Ура, Имрон! Ты решил все задачи по робототехнике! Начинаем заново по кругу.")
            st.session_state.state["robot_solved_ids"] = []
            available_robot = robot_tasks
        st.session_state.current_robot_task = random.choice(available_robot)

    curr_r = st.session_state.current_robot_task
    st.markdown(f"**Инженерная задача:** {curr_r['q']}")
    user_robot_str = st.text_input("Твой ответ (число):", value="", key="robot_ans_clean")

    if st.button("Проверить решение инженера", key="check_robot_btn"):
        val_clean = user_robot_str.strip()
        if val_clean.lstrip("-").isdigit():
            user_robot_ans = int(val_clean)
            st.session_state.state["solved_total"] += 1
            if user_robot_ans == curr_r["ans"]:
                st.session_state.state["correct_total"] += 1

                if curr_r["id"] not in st.session_state.state["robot_solved_ids"]:
                    st.session_state.state["robot_solved_ids"].append(curr_r["id"])
                    st.session_state.state["robot_money"] += 300
                    add_earnings(300, "Задача по робототехнике")

                st.success("🤖 Браво, главный инженер! Задача решена верно, в копилку добавлено 300 сум! 🏆")
                speak_voice("Отличная работа, Имрон! Робот собран правильно!")

                st.session_state.current_robot_task = None
                st.rerun()
            else:
                save_data()
                st.error("❌ Ошибка! Проверь механику и посчитай еще раз.")
        else:
            st.warning("Пожалуйста, введи число!")


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
        "> **📝 Инструкция:** Используй методы из раздела **Репетитор**. Накопи **25 правильных ответов**, чтобы получить **1000 сум** в копилку арифметики!"
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


# --- РЕЖИМ: Задачи для развития мышления ---
elif mode == "🧠 Задачи для развития мышления":
    st.header("🧠 Развитие математического мышления (4 класс)")
    st.markdown(
        "> **📝 Инструкция:** Полезные задачи по программе 4 класса (скорость, периметр, работа). За каждую правильно решенную задачу ты получаешь **200 сум** в копилку."
    )

    logic_list_4class = [
        {"id": 1, "q": "Поезд идет со скоростью 60 км/ч. Какое расстояние он пройдет за 3 часа?", "ans": 180},
        {"id": 2, "q": "Периметр квадрата равен 36 см. Чему равна длина одной стороны квадрата?", "ans": 9},
        {"id": 3, "q": "Мастер делает 12 деталей в час, а ученик — 8 деталей в час. Сколько деталей они изготовят вместе за 2 часа?", "ans": 40},
        {"id": 4, "q": "В мешке было 50 кг муки. Из него брали 3 раза по 8 кг. Сколько кг муки осталось в мешке?", "ans": 26},
        {"id": 5, "q": "В бочку налили 60 литров воды, а из крана вылили в 3 раза меньше. Сколько литров воды осталось в бочке?", "ans": 40},
        {"id": 6, "q": "Турист шел пешком 4 часа со скоростью 5 км/ч. Какое расстояние он прошел?", "ans": 20},
        {"id": 7, "q": "У прямоугольника длина 10 см, а ширина 4 см. Чему равен периметр этого прямоугольника?", "ans": 28},
        {"id": 8, "q": "У прямоугольника длина 10 см, а ширина 4 см. Чему равна площадь этого прямоугольника (в кв. см)?", "ans": 40},
        {"id": 9, "q": "В трех одинаковых коробках лежит 36 карандашей. Сколько карандашей в 5 таких коробках?", "ans": 60},
        {"id": 10, "q": "Садовник посадил 5 рядов яблонь, по 8 деревьев в каждом ряду, и еще 15 груш. Сколько всего деревьев он посадил?", "ans": 55},
        {"id": 11, "q": "Автомобиль проехал 240 км за 4 часа. С какой средней скоростью он ехал (км/ч)?", "ans": 60},
        {"id": 12, "q": "У мальчика было несколько марок. После того как он подарил другу 12 марок, у него осталось 18. Сколько марок было сначала?", "ans": 30},
        {"id": 13, "q": "В классе 28 учеников. Девочек на 4 больше, чем мальчиков. Сколько мальчиков в классе?", "ans": 12},
        {"id": 14, "q": "Длина прыжка кузнечика 30 см. Сколько прыжков ему нужно сделать, чтобы преодолеть 3 метра (300 см)?", "ans": 10},
        {"id": 15, "q": "Купили 4 кг яблок по 5000 сумов и 2 кг груш по 8000 сумов. Сколько всего сумов заплатили?", "ans": 36000},
        {"id": 16, "q": "В спортзале занималось 36 детей. Из них четверо ушли в раздевалку, а остальные построились в 4 одинаковых ряда. Сколько детей в одном ряду?", "ans": 8},
        {"id": 17, "q": "У брата 48 тетрадей, а у сестры в 4 раза меньше. Сколько всего тетрадей у них вместе?", "ans": 60},
        {"id": 18, "q": "Периметр равностороннего треугольника равен 27 см. Чему равна длина одной его стороны?", "ans": 9},
        {"id": 19, "q": "Велосипедист ехал 3 часа со скоростью 14 км/ч. Какое расстояние он преодолел?", "ans": 42},
        {"id": 20, "q": "Книга стоит 18000 сумов, а альбом на 6000 сумов дешевле. Сколько стоит покупка книги и альбома вместе?", "ans": 30000}
    ]

    if "current_logic_task" not in st.session_state or st.session_state.current_logic_task is None:
        available_tasks = [t for t in logic_list_4class if t["id"] not in st.session_state.state["logic_solved_ids"]]
        if not available_tasks:
            st.success("🎉 Ура, Имрон! Ты решил все задачи! Начинаем заново по кругу.")
            st.session_state.state["logic_solved_ids"] = []
            available_tasks = logic_list_4class
        st.session_state.current_logic_task = random.choice(available_tasks)

    curr = st.session_state.current_logic_task
    st.markdown(f"**Задание:** {curr['q']}")
    user_logic_str = st.text_input("Ваш ответ (число):", value="", key="logic_ans_clean")

    if st.button("Проверить решение", key="check_logic_btn"):
        val_clean = user_logic_str.strip()
        if val_clean.lstrip("-").isdigit():
            user_logic_ans = int(val_clean)
            st.session_state.state["solved_total"] += 1
            if user_logic_ans == curr["ans"]:
                st.session_state.state["correct_total"] += 1

                if curr["id"] not in st.session_state.state["logic_solved_ids"]:
                    st.session_state.state["logic_solved_ids"].append(curr["id"])
                    st.session_state.state["logic_money"] += 200
                    add_earnings(200, "Задача на мышление")

                st.success("🧠 Отлично! Задача решена правильно, ты заработал 200 сум! 🏆")
                speak_voice("Ты молодец, Имрон! Задача решена верно!")

                st.session_state.current_logic_task = None
                st.rerun()
            else:
                save_data()
                st.error("Неправильно. Подумай еще раз над условием!")
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


# --- РЕЖИМ: Спринт с таймером ---
elif mode == "⏱️ Спринт с таймером (7 примеров, Награда 10000 сум)":
    st.header("⏱️ Супер-Спринт с таймером (Смешанные задачи для 4 класса)")
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
                
                pool = []
                for _ in range(4):
                    a = random.randint(15, 60)
                    b = random.randint(10, 40)
                    if random.choice([True, False]):
                        pool.append({"q": f"{a} + {b}", "ans": a + b})
                    else:
                        pool.append({"q": f"{a} - {b}", "ans": a - b})
                
                text_tasks = [
                    {"q": "У Ирины было 4 коробки с карандашами, в каждой по 6 карандашей. Сколько всего карандашей у Ирины?", "ans": 24},
                    {"q": "В гараже стояло 15 машин. Уехали 7 машин. Сколько машин осталось в гараже?", "ans": 8},
                    {"q": "На трех полках стояло по 9 книг. Сколько всего книг на полках?", "ans": 27},
                    {"q": "У Саши было 50 сумов. Он купил тетрадь за 18 сумов. Сколько денег осталось?", "ans": 32},
                    {"q": "В автобусе ехало 28 пассажиров. На остановке зашло еще 14 человек. Сколько стало пассажиров?", "ans": 42},
                    {"q": "В мастерской отремонтировали 12 велосипедов, а самокатов на 4 больше. Сколько всего самокатов?", "ans": 16},
                    {"q": "У бабушки в саду росло 18 кустов белых роз, а красных на 5 меньше. Сколько всего роз в саду?", "ans": 31}
                ]
                pool.extend(random.sample(text_tasks, min(2, len(text_tasks))))
                
                sprint_logic_tasks = [
                    {"q": "Поезд идет со скоростью 60 км/ч. Какое расстояние он пройдет за 3 часа?", "ans": 180},
                    {"q": "Периметр квадрата равен 36 см. Чему равна длина одной стороны квадрата?", "ans": 9},
                    {"q": "Мастер делает 12 деталей в час, а ученик — 8. Сколько деталей они сделают вместе за 2 часа?", "ans": 40},
                    {"q": "У прямоугольника длина 10 см, а ширина 4 см. Чему равен периметр этого прямоугольника?", "ans": 28}
                ]
                pool.extend(random.sample(sprint_logic_tasks, min(1, len(sprint_logic_tasks))))
                
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
                                st.success("🏆 Блестяще! Ты решил все 7 задач и заработал 10 000 сум!")
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
        st.session_state.state.get("robot_money", 0) +
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
    with c2:
        st.metric(label="➕ Арифметика", value=f"{st.session_state.state['arith_money']} сум")
    with c3:
        st.metric(label="📖 Текст. задачи", value=f"{st.session_state.state['text_money']} сум")

    c4, c5, c6 = st.columns(3)
    with c4:
        st.metric(label="🧠 Мышление", value=f"{st.session_state.state['logic_money']} сум")
    with c5:
        st.metric(label="🤖 Робототехника", value=f"{st.session_state.state.get('robot_money', 0)} сум")
    with c6:
        st.metric(label="⏱️ Спринт / Марафон", value=f"{st.session_state.state['marathon_money'] + st.session_state.state['sprint_money']} сум")

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
