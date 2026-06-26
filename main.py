"""
Проєкт: Трекер звичок (Консольна утиліта)
Автор: Марк Гапяк, група ІПЗ-22
"""

import json
import os
from datetime import date, timedelta

DATA_FILE = "habits.json"

# ── Збереження даних ────────────────────────────────────────────────────────

def load_data():
    """Завантажує записи з JSON-файлу. Якщо файл не існує — повертає порожній список."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(records):
    """Записує список записів у JSON-файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

# ── Допоміжні функції ───────────────────────────────────────────────────────

def next_id(records):
    """Генерує наступний унікальний ідентифікатор."""
    if not records:
        return 1
    return max(r["id"] for r in records) + 1

def get_current_week_dates():
    """Повертає список дат (у форматі рядка) для поточного тижня (Пн-Нд)."""
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    return [str(start_of_week + timedelta(days=i)) for i in range(7)]

# ── Основна логіка ──────────────────────────────────────────────────────────

def add_habit():
    """Додає нову звичку для відстеження."""
    name = input("\n Назва звички: ").strip()
    if not name:
        print(" Помилка: назва не може бути порожньою.")
        return
    
    category = input(" Категорія (наприклад, Спорт, Розваги): ").strip()
    if not category:
        category = "Загальне"

    records = load_data()
    records.append({
        "id": next_id(records),
        "name": name,
        "category": category,
        "checkins": [] # Список дат, коли звичка була виконана
    })
    save_data(records)
    print(" ✓ Звичку успішно додано.")

def daily_checkin():
    """Щоденна відмітка виконання звички."""
    records = load_data()
    if not records:
        print(" Немає жодної звички. Спочатку додайте звичку.")
        return

    print("\n Доступні звички:")
    for r in records:
        print(f" [{r['id']}] {r['name']} ({r['category']})")
        
    try:
        habit_id = int(input(" Введіть ID звички для відмітки: ").strip())
    except ValueError:
        print(" Помилка: введіть ціле число.")
        return

    target_habit = next((r for r in records if r["id"] == habit_id), None)
    if not target_habit:
        print(" Звичку з таким ID не знайдено.")
        return

    today_str = str(date.today())
    if today_str in target_habit["checkins"]:
        print(" Ви вже відмітили цю звичку сьогодні! Молодці!")
    else:
        target_habit["checkins"].append(today_str)
        target_habit["checkins"].sort()
        save_data(records)
        print(" ✓ Відмітку додано!")

def weekly_status():
    """Перегляд статусу за поточний тиждень та відсоток виконання."""
    records = load_data()
    if not records:
        print(" Записів немає.")
        return

    week_dates = get_current_week_dates()
    
    # Вирівнюємо шапку по 5 символів на день для ідеальної таблиці
    days_header = " ".join(f"{day:^5}" for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"])
    
    print("\n Статус за поточний тиждень:")
    print("-" * 75)
    print(f" {'ID':<3} {'Назва':<15} | {days_header} | Прогрес")
    print("-" * 75)

    for r in records:
        week_checks = 0
        status_cells = []
        for d in week_dates:
            if d in r["checkins"]:
                status_cells.append(f"{'[x]':^5}")
                week_checks += 1
            else:
                status_cells.append(f"{'[ ]':^5}")
        
        status_line = " ".join(status_cells)
        percent = (week_checks / 7) * 100
        print(f" {r['id']:<3} {r['name']:<15} | {status_line} | {percent:>5.1f}%")
    print("-" * 75)

def calculate_streak():
    """Додаткова функція: підраховує поточний стрік (дні підряд) для звичок."""
    records = load_data()
    if not records:
        print(" Записів немає.")
        return

    print("\n Поточний стрік (дні підряд):")
    today = date.today()
    
    for r in records:
        streak = 0
        current_date = today
        # Якщо сьогодні ще не відмічено, перевіряємо з учорашнього дня
        if str(today) not in r["checkins"]:
            current_