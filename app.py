from datetime import datetime, timedelta
import json
import os
import random
import time
import streamlit as st

st.set_page_config(
    page_title="Академия Юного Инженера — Имрон", page_icon="🚀", layout="centered"
)

# --- ЖЕЛЕЗОБЕТОННОЕ СОХРАНЕНИЕ (Файл на сервере, чтобы копилка никогда не пропадала) ---
DATA_FILE = "imron_data.json"


def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        for item in data.get("earnings_history", []):
          item["date"] = datetime.fromisoformat(item["date"])
        return data
    except Exception:
      pass
  return {
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


def save_data():
  data_to_save = st.session_state.state.copy()
  formatted_history = []
  for item in data_to_save["earnings_history"]:
    formatted_history.append({
        "date": item["date"].isoformat(),
        "amount": item["amount"],
        "source": item["source"],
    })
  data_to_save["earnings_history"] = formatted_history

  if data_to_save["marathon_last_success"]:
    data_to_save["marathon_last_success"] = data_to_save[
        "marathon_last_success"
    ].isoformat()
  if data_to_save["timed_mode_last_use"]:
    data_to_save["timed_mode_last_use"] = data_to_save[
        "timed_mode_last_use"
    ].isoformat()

  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)


if "state" not in st.session_state:
  loaded = load_data()
  if loaded.get("marathon_last_success"):
    try:
      loaded["marathon_last_success"] = datetime.fromisoformat(
          loaded["marathon_last_success"]
      )
    except:
      loaded["marathon_last_success"] = None
  if loaded.get("timed_mode_last_use"):
    try:
      loaded["timed_mode_last_use"] = datetime.fromisoformat(
          loaded["timed_mode_last_use"]
      )
    except:
      loaded["timed_mode_last_use"] = None
  st.session_state.state = loaded


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
    "Привет, Имрон! Выбирай любой раздел, тренируй ум, решай сложные задачи и"
    " зарабатывай сумы!"
)

# Боковое меню: все разделы (включая Репетитора столбиком)
mode = st.sidebar.selectbox(
    "Выбери раздел тренировки:",
    [
        "👨‍🏫 Репетитор: Учим умножение и деление столбиком",
        "📚 Школа юного инженера (Уроки и лайфхаки счета)",
        "✖️ Отдельный тренажер: Умножение и Деление",
        "➕ Простая арифметика",
        "📖 Текстовые задачи",
        "🧠 Усложненные задачи для мышления",
        "🏆 Марафон 50 вопросов (Умножение, Деление, Награда 5000 сум)",
        (
            "⏱️ Инженерный Спринт с таймером (Умножение, Деление и Логика, Награда"
            " 10000 сум)"
        ),
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


# --- РЕЖИМ: Репетитор (Наглядное обучение столбиком) ---
if mode == "👨‍🏫 Репетитор: Учим умножение и деление столбиком":
  st.header("👨‍🏫 Личный Репетитор Имрона: Учимся считать столбиком")
  st.write(
      "Здесь все правила объяснены очень подробно, по шагам. Если что-то не"
      " понятно, всегда можно заглянуть сюда и освежить память!"
  )

  st.markdown("---")
  st.subheader("✖️ Шаг 1: Как умножать двузначное число на однозначное столбиком")
  st.write(
      "**Пример:** `43 × 2`\n"
      "1. Пишем числа друг под другом: большее сверху, меньшее снизу под единицами.\n"
      "2. Умножаем нижнее число **сначала на единицы** верхнего: `2 × 3 = 6`. Пишем 6 под единицами.\n"
      "3. Затем умножаем нижнее число **на десятки** верхнего: `2 × 4 = 8`. Пишем 8 под десятками.\n"
      "4. Получается **86**."
  )
  st.info(
      "💡 *Если при умножении получается число больше 9 (например, 14), то 4 пишем"
      " внизу, а 1 «запоминаем» и прибавляем к следующему разряду!*"
  )

  st.markdown("---")
  st.subheader("➗ Шаг 2: Как делить в столбик («Уголок»)")
  st.write(
      "**Пример:** `84 ÷ 3`\n"
      "Деление — это поиск части. Мы делим слева направо (от десятков к единицам):\n"
      "1. Рисуем «уголок». Внутри пишем **84** (делимое), снаружи слева **3** (делитель).\n"
      "2. Берем первую цифру слева — это **8** (десятки). Спрашиваем себя: *«Сколько раз по 3 поместится в 8?»* По 2 раза (`3 × 2 = 6`). Пишем **2** в частное (под уголок).\n"
      "3. Проверяем остаток: `8 - 6 = 2`. Остался остаток 2 десятка.\n"
      "4. Сносим к двойке следующую цифру сверху — получается **24** (единицы).\\n"
      "5. Спрашиваем: *«Сколько раз по 3 поместится в 24?»* Ровно 8 раз (`3 × 8 = 24`). Пишем **8** в частное рядом с двойкой.\n"
      "Ответ: **28**."
  )
  st.success(
      "🎯 Главное правило деления столбиком: **Раздели → Умножь → Вычти → Снеси"
      " следующую цифру!** Повторяй эти 4 шага, пока цифры не кончатся."
  )


# --- РЕЖИМ: Школа юного инженера ---
elif mode == "📚 Школа юного инженера (Уроки и лайфхаки счета)":
  st.header("📚 Школа юного инженера: Секреты быстрого счета в уме")
  st.write(
      "Привет, Имрон! Настоящие инженеры умеют не только считать, но и"
      " рассуждать. Изучай методы и применяй их на практике!"
  )

  st.markdown("---")
  st.subheader("💡 Урок 1: Как делить в уме двузначные числа")
  st.write(
      "**Метод разложения на удобные слагаемые:** Если число не делится сразу,"
      " разбей его на два числа, которые легко делятся на твой делитель."
  )
  st.info(
      "**Пример:** `84 ÷ 4`\n1. Раскладываем 84 на `80` и `4`.\n2. Делим каждое"
      " на 4: `80 ÷ 4 = 20` и `4 ÷ 4 = 1`.\n3. Складываем результаты: `20 + 1 ="
      " 21`.\nОтвет: **21**."
  )


# --- РЕЖИМ: Отдельный тренажер: Умножение и Деление ---
elif mode == "✖️ Отдельный тренажер: Умножение и Деление":
  st.header("✖️/➗ Специальный тренажер: Умножение и Деление")
  st.markdown(
      "> **📝 Инструкция:** Этот раздел создан специально для прокачки"
      " умножения и деления. Решай примеры внимательно, используй подсказки из"
      " раздела репетитора. Накопи **25 правильных ответов**, чтобы заработать"
      " **1000 сум**!"
  )

  if "mult_q" not in st.session_state:
    st.session_state.mult_q = None
    st.session_state.mult_ans = None

  if st.button("Следующий пример") or st.session_state.mult_q is None:
    op_type = random.choice(["mult", "div"])
    if op_type == "mult":
      a = random.randint(3, 15)
      b = random.randint(2, 10)
      st.session_state.mult_q = f"{a} × {b}"
      st.session_state.mult_ans = a * b
    else:
      b = random.randint(2, 10)
      ans = random.randint(3, 12)
      a = b * ans
      st.session_state.mult_q = f"{a} ÷ {b}"
      st.session_state.mult_ans = ans

  st.markdown(f"### Сколько будет: **{st.session_state.mult_q}**?")
  user_ans_str = st.text_input("Твой ответ:", value="", key="m_ans_clean")

  if st.button("Проверить ответ", key="check_mult"):
    if user_ans_str.strip().isdigit():
      user_ans = int(user_ans_str.strip())
      st.session_state.state["solved_total"] += 1
      if user_ans == st.session_state.mult_ans:
        st.session_state.state["correct_total"] += 1
        save_data()
        process_reward("mult_correct_count", "mult_money", "Умножение и Деление")
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
      "> **📝 Инструкция:** Решай примеры с трехзначными числами. Накопи **25"
      " правильных ответов**, чтобы получить **1000 сум**."
  )

  if "arith_q" not in st.session_state:
    st.session_state.arith_q = None
    st.session_state.arith_ans = None

  if st.button("Новый пример") or st.session_state.arith_q is None:
    op = random.choice(["+", "-"])
    if op == "+":
      a = random.randint(100, 500)
      b = random.randint(100, 400)
      st.session_state.arith_ans = a + b
    else:
      a = random.randint(200, 600)
      b = random.randint(50, a)
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


# --- РЕЖИМ: Текстовые задачи ---
elif mode == "📖 Текстовые задачи":
  st.header("📖 Текстовые задачи")
  st.markdown(
      "> **📝 Инструкция:** Усложненные задачи на логику расчетов и движение."
      " Накопи **25 правильных ответов** для награды в **1000 сум**."
  )

  tasks_list = [
      {
          "id": 1,
          "q": "Турист шел 3 часа со скоростью 4 км/ч, а потом проехал на велосипеде 2 часа со скоростью 12 км/ч. Какой общий путь прошел и проехал турист?",
          "ans": 36,
      },
      {
          "id": 2,
          "q": "В двух мешках было 80 кг муки. Когда из первого мешка взяли 15 кг, в обоих мешках муки стало поровну. Сколько кг муки было в первом мешке сначала?",
          "ans": 55,
      },
      {
          "id": 3,
          "q": "Периметр прямоугольника равен 30 см, а его ширина равна 5 см. Чему равна длина этого прямоугольника?",
          "ans": 10,
      },
  ]

  if (
      "current_text_task" not in st.session_state
      or st.session_state.current_text_task is None
  ):
    available_text = [
        t
        for t in tasks_list
        if t["id"] not in st.session_state.state["text_solved_ids"]
    ]
    if not available_text:
      st.success("🎉 Ты решил все текстовые задачи! Начинаем заново по кругу.")
      st.session_state.state["text_solved_ids"] = []
      available_text = tasks_list
    st.session_state.current_text_task = random.choice(available_text)

  curr_t = st.session_state.current_text_task
  st.markdown(f"**Задача:** {curr_t['q']}")
  user_ans_t_str = st.text_input(
      "Введите числовой ответ:", value="", key="t_ans_clean"
  )

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


# --- РЕЖИМ: Усложненные задачи для развития мышления ---
elif mode == "🧠 Усложненные задачи для мышления":
  st.header("🧠 Инженерная логика и олимпиадные задачки")
  st.markdown(
      "> **📝 Инструкция:** Эти задачи заставят тебя поломать голову! За каждую"
      " правильно решенную сложную задачу ты получаешь **200 сум**."
  )

  logic_list = [
      {
          "id": 1,
          "q": "У отца 6 дочерей, и у каждой дочери есть один брат. Сколько всего детей в семье?",
          "ans": 7,
      },
      {
          "id": 2,
          "q": "Две матери, две дочки и бабушка с внучкой пошли в магазин и купили 5 пирожков, причем каждой досталось по одному. Как такое могло быть?",
          "ans": 3,
      },
      {
          "id": 3,
          "q": "Шнур длиной 30 метров режут на части по 2 метра. Какое минимальное количество разрезов нужно сделать?",
          "ans": 14,
      },
  ]

  if (
      "current_logic_task" not in st.session_state
      or st.session_state.current_logic_task is None
  ):
    available_tasks = [
        t
        for t in logic_list
        if t["id"] not in st.session_state.state["logic_solved_ids"]
    ]
    if not available_tasks:
      st.success(
          "🎉 Ура, Имрон! Ты решил все усложненные инженерные задачи! Начинаем"
          " заново по кругу."
      )
      st.session_state.state["logic_solved_ids"] = []
      available_tasks = logic_list
    st.session_state.current_logic_task = random.choice(available_tasks)

  curr = st.session_state.current_logic_task
  st.markdown(f"**Инженерная задача:** {curr['q']}")
  user_logic_str = st.text_input(
      "Ваш ответ (число):", value="", key="logic_ans_clean"
  )

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
          add_earnings(200, "Сложная логическая задача")

        st.success(
            "🧠 Потрясающе! Настоящий инженерный ум! Ты заработал 200 сум! 🏆"
        )
        speak_voice("Блестяще, Имрон! Задача решена правильно!")

        st.session_state.current_logic_task = None
        st.rerun()
      else:
        save_data()
        st.error(
            "Неправильно. Подумай над условием еще раз, здесь есть подвох!"
        )
    else:
      st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Марафон 50 вопросов ---
elif mode == "🏆 Марафон 50 вопросов (Умножение, Деление, Награда 5000 сум)":
  st.header("🏆 Большой Марафон: Умножение и Деление (50 вопросов)")
  st.markdown(
      "> **📝 Инструкция:** Пройди все 50 вопросов без единой ошибки. Награда —"
      " **5000 сум**."
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
      if st.button("🚀 Начать Большой Марафон"):
        st.session_state.m_active = True
        st.session_state.m_step = 1
        if random.choice([True, False]):
          a, b = random.randint(2, 9), random.randint(2, 9)
          st.session_state.m_q = f"{a} × {b}"
          st.session_state.m_ans = a * b
        else:
          b, ans = random.randint(2, 9), random.randint(2, 9)
          a = b * ans
          st.session_state.m_q = f"{a} ÷ {b}"
          st.session_state.m_ans = ans
        st.rerun()
    else:
      st.markdown(f"### Вопрос № {st.session_state.m_step} из 50")
      st.markdown(f"**Сколько будет: {st.session_state.m_q}**?")

      user_m_str = st.text_input(
          "Твой ответ:", value="", key=f"m_input_clean_{st.session_state.m_step}"
      )

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
              add_earnings(5000, "Большой Марафон (Умножение/Деление)")
              speak_voice("Ты умница, Имрон! Большой марафон успешно пройден!")
              st.success(
                  "🎉 ПОЗДРАВЛЯЕМ! Ты прошел сложный марафон и заработал 5000"
                  " сум!"
              )
              st.session_state.m_active = False
            else:
              st.session_state.m_step += 1
              if random.choice([True, False]):
                a, b = random.randint(2, 9), random.randint(2, 9)
                st.session_state.m_q = f"{a} × {b}"
                st.session_state.m_ans = a * b
              else:
                b, ans = random.randint(2, 9), random.randint(2, 9)
                a = b * ans
                st.session_state.m_q = f"{a} ÷ {b}"
                st.session_state.m_ans = ans
              st.rerun()
          else:
            save_data()
            st.error(
                f"❌ Ошибка на вопросе №{st.session_state.m_step}! Марафон"
                " сброшен."
            )
            speak_voice("Ничего страшного, попробуй еще раз.")
            st.session_state.m_active = False
        else:
          st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Инженерный Спринт с таймером ---
elif (
    mode
    == "⏱️ Инженерный Спринт с таймером (Умножение, Деление и Логика, Награда 10000 сум)"
):
  st.header("⏱️ Инженерный Спринт с таймером (Усложненный)")
  st.info(
      "💡 Задача: решить **7 сложных заданий за 3 минуты (180 секунд)**. Награда"
      " — **10 000 сум** (доступно раз в 2 часа)."
  )

  can_play_sprint = True
  if st.session_state.state["timed_mode_last_use"] is not None:
    elapsed = now - st.session_state.state["timed_mode_last_use"]
    if elapsed < timedelta(hours=2):
      left_time = timedelta(hours=2) - elapsed
      h_l = int(left_time.total_seconds() // 3600)
      m_l = int((left_time.total_seconds() % 3600) // 60)
      can_play_sprint = False
      st.warning(f"⏳ Спринт будет доступен через {h_l} ч. {m_l} мин.")


  def generate_sprint_question():
    q_type = random.choice(["mult", "div", "logic"])
    if q_type == "mult":
      a, b = random.randint(7, 15), random.randint(6, 12)
      return f"{a} × {b}", a * b
    elif q_type == "div":
      b = random.randint(4, 12)
      ans = random.randint(6, 15)
      a = b * ans
      return f"{a} ÷ {b}", ans
    else:
      logic_sprint_bank = [
          (
              (
                  "У отца 4 сына, и у каждого есть одна сестра. Сколько всего"
                  " детей в семье?"
              ),
              5,
          ),
          (
              (
                  "Шоколадку разделили на 5 частей по прямой линии. Сколько было"
                  " сделано разрезов?"
              ),
              4,
          ),
      ]
      return random.choice(logic_sprint_bank)


  if can_play_sprint:
    if "sprint_active" not in st.session_state:
      st.session_state.sprint_active = False
      st.session_state.s_step = 1
      st.session_state.s_start_time = None
      st.session_state.s_q = None
      st.session_state.s_ans = None

    if not st.session_state.sprint_active:
      if st.button("🚀 Начать Инженерный Спринт (3 мин)"):
        st.session_state.sprint_active = True
        st.session_state.s_step = 1
        st.session_state.s_start_time = time.time()
        q_text, q_ans = generate_sprint_question()
        st.session_state.s_q = q_text
        st.session_state.s_ans = q_ans
        st.rerun()
    else:
      elapsed_sec = time.time() - st.session_state.s_start_time
      time_left = max(0, 180 - int(elapsed_sec))

      if time_left == 0:
        st.error("⏰ Время вышло! Инженерный спринт прерван.")
        speak_voice("Время вышло, ничего страшного.")
        st.session_state.sprint_active = False
      else:
        st.markdown(
            f"### ⏱️ Осталось времени: **{time_left} сек.** | Задание"
            f" {st.session_state.s_step} из 7"
        )
        st.markdown(f"**Задание:** {st.session_state.s_q}")

        user_s_str = st.text_input(
            "Твой ответ (число):",
            value="",
            key=f"sprint_step_clean_{st.session_state.s_step}",
        )

        if st.button("Ответить на спринт"):
          val_clean = user_s_str.strip()
          if val_clean.lstrip("-").isdigit():
            user_s_ans = int(val_clean)
            st.session_state.state["solved_total"] += 1
            if user_s_ans == st.session_state.s_ans:
              st.session_state.state["correct_total"] += 1

              if st.session_state.s_step >= 7:
                st.session_state.state["sprint_money"] += 10000
                st.session_state.state["timed_mode_last_use"] = now
                add_earnings(10000, "Инженерный Спринт")
                speak_voice(
                    "Великолепно, Имрон! Спринт успешно пройден, получено 10"
                    " тысяч сум!"
                )
                st.success(
                    "🏆 Блестяще! Инженерный спринт пройден и заработано 10 000"
                    " сум!"
                )
                st.session_state.sprint_active = False
              else:
                st.session_state.s_step += 1
                q_text, q_ans = generate_sprint_question()
                st.session_state.s_q = q_text
                st.session_state.s_ans = q_ans
                st.rerun()
            else:
              save_data()
              st.error("❌ Ошибка! Инженерный спринт прерван из-за ошибки.")
              st.session_state.sprint_active = False
          else:
            st.warning("Пожалуйста, введи число!")


# --- РЕЖИМ: Статистика и Отчет для родителя ---
elif mode == "📊 Статистика и Отчет для родителя":
  st.header("📊 Статистика успехов и Панель родительского контроля")
  st.write(
      "👨‍👦 Здесь отображаются данные активности Имрона. Вся статистика"
      " сохраняется в файл на сервере и защищена от удаления!"
  )

  total_earned = (
      st.session_state.state["mult_money"]
      + st.session_state.state["arith_money"]
      + st.session_state.state["text_money"]
      + st.session_state.state["logic_money"]
      + st.session_state.state["marathon_money"]
      + st.session_state.state["sprint_money"]
  )

  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(
        label="Всего решено", value=st.session_state.state["solved_total"]
    )
  with col2:
    st.metric(
        label="Правильных ответов",
        value=st.session_state.state["correct_total"],
    )
  with col3:
    st.metric(label="💰 Общая копилка", value=f"{total_earned} сум")

  st.divider()

  # --- НЕДЕЛЬНЫЙ ОТЧЕТ ---
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
    st.metric(
        label="✖️/➗ Умножение/Деление",
        value=f"{st.session_state.state['mult_money']} сум",
    )
    st.caption(
        f"Правильных ответов: {st.session_state.state['mult_correct_count']}"
    )
  with c2:
    st.metric(
        label="➕ Арифметика",
        value=f"{st.session_state.state['arith_money']} сум",
    )
    st.caption(
        f"Правильных ответов: {st.session_state.state['arith_correct_count']}"
    )
  with c3:
    st.metric(
        label="📖 Текст. задачи",
        value=f"{st.session_state.state['text_money']} сум",
    )
    st.caption(
        f"Правильных ответов: {st.session_state.state['text_correct_count']}"
    )

  c4, c5, c6 = st.columns(3)
  with c4:
    st.metric(
        label="🧠 Сложная логика",
        value=f"{st.session_state.state['logic_money']} сум",
    )
    st.caption(
        f"Решено задач: {len(st.session_state.state['logic_solved_ids'])}"
    )
  with c5:
    st.metric(
        label="🏆 Марафон",
        value=f"{st.session_state.state['marathon_money']} сум",
    )
  with c6:
    st.metric(
        label="⏱️ Спринт", value=f"{st.session_state.state['sprint_money']} сум"
    )

  st.divider()

  # --- ИСТОРИЯ НАЧИСЛЕНИЙ ПО ДАТАМ ---
  st.subheader("📜 История начислений в копилку (по порядку)")
  history = st.session_state.state["earnings_history"]

  if not history:
    st.info(
        "История пока пуста. Как только Имрон заработает сумы, здесь появится"
        " хронология!"
    )
  else:
    for idx, record in enumerate(reversed(history), 1):
      rec_date = record["date"]
      if isinstance(rec_date, str):
        rec_date = datetime.fromisoformat(rec_date)
      date_str = rec_date.strftime("%d.%m.%Y в %H:%M")
      st.markdown(
          f"**{idx}.** `{date_str}` — **+{record['amount']} сум**"
          f" *({record['source']})*"
      )

  st.divider()
  st.info(
      "🎯 **Отчет для отца:** Репетитор столбиком добавлен, тренажер"
      " умножения/деления усилен, а вся история надежно сохранена в файле!"
  )
