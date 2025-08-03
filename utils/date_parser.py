import datetime
import re
from dateutil import parser
import pytz

TIMEZONE = pytz.timezone("Asia/Dushanbe")


def parse_strict_date(user_message: str) -> datetime.datetime:
    """
    Парсинг строго формата ДД-ММ-ГГГГ и т.п.
    Возвращает datetime.datetime (без времени).
    """
    cleaned_input = re.sub(r'[^\d\s/.\-]', '', user_message.strip())
    parts = re.split(r'[\s/.\-]+', cleaned_input)
    parts = [part for part in parts if part]

    if len(parts) != 3:
        raise ValueError("Неверный формат даты. Укажите день, месяц и год.")

    day, month, year = parts

    if len(year) == 2:
        year = f"20{year}" if int(year) < 50 else f"19{year}"

    try:
        return datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        raise ValueError("Неверная дата. Проверьте правильность дня, месяца и года.")


def parse_strict_time(user_message: str) -> str:
    """
    Парсинг времени: "03:25", "3 вечера", "4.15 утра", и т.д.
    Возвращает строку времени: HH:MM
    """
    cleaned_input = user_message.strip().lower()
    is_am = any(marker in cleaned_input for marker in ['am', 'утра', 'утро', 'дня'])
    is_pm = any(marker in cleaned_input for marker in ['pm', 'вечера', 'вечер', 'ночи', 'ночь'])
    cleaned_input = re.sub(r'[^\d\s:.\-]', '', cleaned_input)
    parts = re.split(r'[\s:.\-]+', cleaned_input)
    parts = [part for part in parts if part]

    if len(parts) == 1:
        hours = int(parts[0])
        minutes = 0
    elif len(parts) >= 2:
        hours = int(parts[0])
        minutes = int(parts[1])
    else:
        raise ValueError("Неверный формат времени.")

    if is_pm and hours < 12:
        hours += 12
    elif is_am and hours == 12:
        hours = 0

    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError("Неверное значение времени.")

    return f"{hours:02d}:{minutes:02d}"


def parse_user_datetime(user_input: str) -> datetime.datetime | None:
    """
    Объединённый парсер. Сначала пробует строгий разбор, затем гибкий.
    Возвращает datetime с учётом часового пояса.
    """
    try:
        # Пробуем разбить вручную
        date_part, time_part = split_date_time(user_input)
        date_obj = parse_strict_date(date_part)
        time_str = parse_strict_time(time_part)
        time_obj = datetime.datetime.strptime(time_str, "%H:%M").time()
        combined = datetime.datetime.combine(date_obj.date(), time_obj)
        return TIMEZONE.localize(combined)
    except Exception:
        try:
            # Гибкий разбор
            dt = parser.parse(user_input, fuzzy=True)
            return TIMEZONE.localize(dt)
        except Exception:
            return None


def split_date_time(text: str) -> tuple[str, str]:
    """
    Делит ввод на две части: дату и время
    (например: "31.07.2025 03:20" -> ("31.07.2025", "03:20"))
    """
    match = re.search(r"(\d{1,2}[\s/.\-]\d{1,2}[\s/.\-]\d{2,4})", text)
    if match:
        date_part = match.group(1)
        time_part = text.replace(date_part, "")
        return date_part, time_part.strip()
    else:
        raise ValueError("Не удалось найти дату.")


def format_datetime_for_csv(dt: datetime.datetime) -> str:
    """
    Возвращает строку вида YYYY-MM-DD HH:MM
    """
    return dt.strftime("%Y-%m-%d %H:%M")


#
# def test_date_parser():
#     print("=== Testing parse_strict_date ===")
#     date_examples = [
#         "25 12 2023",     # Spaces
#         "25/12/2023",     # Slashes
#         "25.12.2023",     # Dots
#         "25-12-2023",     # Dashes
#         "25/12/23",       # 2-digit year
#         "25.12-2023",     # Mixed separators
#     ]
#
#     for example in date_examples:
#         try:
#             result = parse_strict_date(example)
#             print(f"Input: '{example}' → Output: '{result}'")
#         except ValueError as e:
#             print(f"Input: '{example}' → Error: {e}")
#
#     print("\n=== Testing parse_strict_time ===")
#     time_examples = [
#         "14:30",          # 24-hour format with colon
#         "14.30",          # 24-hour format with dot
#         "14 30",          # 24-hour format with space
#         "2:30 pm",        # 12-hour format with PM
#         "2:30 вечера",    # 12-hour format with Russian time of day
#         "2:30PM",         # 12-hour without space
#         "12 дня",         # 12-hour with only hours
#         "7 утра",         # Morning time in Russian
#         "23:05",          # Late evening
#         "9",              # Only hours
#     ]
#
#     for example in time_examples:
#         try:
#             result = parse_strict_time(example)
#             print(f"Input: '{example}' → Output: '{result}'")
#         except ValueError as e:
#             print(f"Input: '{example}' → Error: {e}")
#
#     print("\n=== Testing split_date_time ===")
#     split_examples = [
#         "25.12.2023 14:30",
#         "25/12/2023 в 14.30",
#         "25-12-2023 примерно 2:30 вечера",
#         "25.12.23 7 утра"
#     ]
#
#     for example in split_examples:
#         try:
#             date_part, time_part = split_date_time(example)
#             print(f"Input: '{example}' → Date: '{date_part}', Time: '{time_part}'")
#         except ValueError as e:
#             print(f"Input: '{example}' → Error: {e}")
#
#     print("\n=== Testing parse_user_datetime ===")
#     datetime_examples = [
#         "25.12.2023 14:30",
#         "25/12/2023 в 2 часа дня",
#         "25-12-2023 примерно 2:30 вечера",
#         "25.12.23 7 утра",
#         "неправильный формат",  # Should handle errors
#     ]
#
#     for example in datetime_examples:
#         result = parse_user_datetime(example)
#         if result:
#             formatted = format_datetime_for_csv(result)
#             print(f"Input: '{example}' → Parsed: '{result}' → CSV format: '{formatted}'")
#         else:
#             print(f"Input: '{example}' → Could not parse")
#
# if __name__ == "__main__":
#     test_date_parser()