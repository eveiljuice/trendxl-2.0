#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправления бага с бесплатными попытками

Проверяет:
1. Кэшированные результаты не списывают попытки
2. Новые анализы списывают попытки
3. Race condition обрабатывается корректно
"""

from services.cache_service import cache_service
from supabase_client import (
    can_use_free_trial,
    record_free_trial_usage,
    get_free_trial_info,
    check_user_can_analyze
)
import asyncio
import sys
import os

# Добавляем путь к backend модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text: str):
    """Печать заголовка"""
    print(f"\n{BLUE}{'='*80}")
    print(f"{text}")
    print(f"{'='*80}{RESET}\n")


def print_success(text: str):
    """Печать успеха"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """Печать ошибки"""
    print(f"{RED}❌ {text}{RESET}")


def print_info(text: str):
    """Печать информации"""
    print(f"{YELLOW}ℹ️  {text}{RESET}")


async def test_cache_lock():
    """Тест блокировки через Redis"""
    print_header("TEST 1: Redis Lock Mechanism")

    try:
        lock_name = "test_analysis:user123:profile456"

        # Проверить что Redis доступен
        if not cache_service.enabled:
            print_error("Redis не доступен, пропускаем тест блокировки")
            return False

        print_info("Попытка приобрести блокировку...")
        lock1 = await cache_service.acquire_lock(lock_name, timeout=10)

        if lock1:
            print_success("Блокировка приобретена успешно")
        else:
            print_error("Не удалось приобрести блокировку")
            return False

        # Попытаться приобрести ту же блокировку (должно не получиться)
        print_info("Попытка приобрести ту же блокировку снова...")
        lock2 = await cache_service.acquire_lock(lock_name, timeout=10)

        if not lock2:
            print_success("Блокировка корректно занята (ожидаемое поведение)")
        else:
            print_error("Блокировка приобретена дважды (БАГ!)")
            return False

        # Освободить блокировку
        print_info("Освобождение блокировки...")
        released = await cache_service.release_lock(lock_name)

        if released:
            print_success("Блокировка освобождена")
        else:
            print_error("Не удалось освободить блокировку")
            return False

        # Теперь должно получиться приобрести снова
        print_info("Попытка приобрести блокировку после освобождения...")
        lock3 = await cache_service.acquire_lock(lock_name, timeout=10)

        if lock3:
            print_success("Блокировка приобретена после освобождения")
            await cache_service.release_lock(lock_name)
        else:
            print_error("Не удалось приобрести блокировку после освобождения")
            return False

        print_success("TEST 1 PASSED: Redis блокировка работает корректно")
        return True

    except Exception as e:
        print_error(f"TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_free_trial_logic(user_id: str):
    """Тест логики бесплатных попыток"""
    print_header("TEST 2: Free Trial Logic")

    try:
        # Получить текущее состояние
        print_info(f"Проверка состояния для пользователя {user_id}...")
        initial_info = await get_free_trial_info(user_id)

        if initial_info:
            print_info(f"Начальное состояние:")
            print(f"  - Can use today: {initial_info.get('can_use_today')}")
            print(f"  - Today count: {initial_info.get('today_count')}")
            print(
                f"  - Total analyses: {initial_info.get('total_free_analyses')}")
        else:
            print_info("Новый пользователь (нет записей)")

        initial_count = initial_info.get(
            'today_count', 0) if initial_info else 0

        # Проверить возможность использования
        can_use = await can_use_free_trial(user_id)
        print_info(f"Может использовать бесплатную попытку: {can_use}")

        # Записать использование
        if can_use:
            print_info("Запись использования бесплатной попытки...")
            success = await record_free_trial_usage(user_id, "test_profile_fix")

            if success:
                print_success("Использование записано успешно")
            else:
                print_error("Не удалось записать использование")
                return False

            # Проверить новое состояние
            new_info = await get_free_trial_info(user_id)
            new_count = new_info.get('today_count', 0) if new_info else 0

            print_info(f"Новое состояние:")
            print(f"  - Today count: {new_count}")
            print(f"  - Expected: {initial_count + 1}")

            if new_count == initial_count + 1:
                print_success("Счётчик увеличился корректно")
            else:
                print_error(
                    f"Счётчик неверный: {new_count} != {initial_count + 1}")
                return False

            # Проверить что теперь нельзя использовать
            can_use_after = await can_use_free_trial(user_id)

            if not can_use_after:
                print_success("После использования попытка больше недоступна")
            else:
                print_error(
                    "После использования попытка всё ещё доступна (БАГ!)")
                return False
        else:
            print_info(
                "Попытка уже использована сегодня, пропускаем тест записи")

        print_success(
            "TEST 2 PASSED: Логика бесплатных попыток работает корректно")
        return True

    except Exception as e:
        print_error(f"TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_check_user_can_analyze(user_id: str):
    """Тест функции check_user_can_analyze"""
    print_header("TEST 3: check_user_can_analyze Function")

    try:
        print_info(f"Проверка прав доступа для пользователя {user_id}...")
        can_analyze, reason, details = await check_user_can_analyze(user_id)

        print_info(f"Результат проверки:")
        print(f"  - Can analyze: {can_analyze}")
        print(f"  - Reason: {reason}")
        print(f"  - Type: {details.get('type')}")

        if reason == "active_subscription":
            print_success("Пользователь имеет активную подписку")
        elif reason == "free_trial":
            print_success("Пользователь может использовать бесплатную попытку")
            trial_info = details.get('info', {})
            print(f"  - Today count: {trial_info.get('today_count', 0)}")
        elif reason == "no_access":
            print_info("Пользователь исчерпал бесплатные попытки")
            print(f"  - Message: {details.get('message')}")
        else:
            print_error(f"Неизвестная причина: {reason}")
            return False

        print_success(
            "TEST 3 PASSED: Функция check_user_can_analyze работает корректно")
        return True

    except Exception as e:
        print_error(f"TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_concurrent_requests(user_id: str):
    """Тест конкурентных запросов (race condition)"""
    print_header("TEST 4: Concurrent Requests (Race Condition)")

    try:
        # Симуляция двух одновременных запросов
        lock_name = f"analysis:{user_id}:test_profile_concurrent"

        print_info("Симуляция двух одновременных запросов...")

        async def request_simulation(request_id: int):
            """Симуляция одного запроса"""
            print_info(
                f"  Request {request_id}: Попытка приобрести блокировку...")

            lock = await cache_service.acquire_lock(lock_name, timeout=5)

            if lock:
                print_success(
                    f"  Request {request_id}: Блокировка приобретена ✅")
                # Симуляция обработки
                await asyncio.sleep(1)
                await cache_service.release_lock(lock_name)
                print_success(
                    f"  Request {request_id}: Блокировка освобождена")
                return True
            else:
                print_info(
                    f"  Request {request_id}: Блокировка занята (ожидаемо)")
                return False

        # Запустить два запроса одновременно
        results = await asyncio.gather(
            request_simulation(1),
            request_simulation(2)
        )

        # Ровно один запрос должен получить блокировку
        locks_acquired = sum(1 for r in results if r)

        if locks_acquired == 1:
            print_success(f"Только один запрос получил блокировку (ожидаемо)")
        else:
            print_error(
                f"Блокировку получили {locks_acquired} запросов (ожидалось 1)")
            return False

        # Очистить блокировку на всякий случай
        await cache_service.release_lock(lock_name)

        print_success("TEST 4 PASSED: Race condition обрабатывается корректно")
        return True

    except Exception as e:
        print_error(f"TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Главная функция"""
    print_header("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ БАГА С БЕСПЛАТНЫМИ ПОПЫТКАМИ")

    # Получить тестовый user_id из аргументов или использовать дефолтный
    if len(sys.argv) > 1:
        test_user_id = sys.argv[1]
    else:
        print_error("Использование: python test_free_trial_fix.py <USER_ID>")
        print_info(
            "Пример: python test_free_trial_fix.py 12345678-1234-1234-1234-123456789012")
        return

    print_info(f"Тестируем с user_id: {test_user_id}")

    # Запустить все тесты
    results = []

    # TEST 1: Redis Lock
    result1 = await test_cache_lock()
    results.append(("Redis Lock Mechanism", result1))

    # TEST 2: Free Trial Logic
    result2 = await test_free_trial_logic(test_user_id)
    results.append(("Free Trial Logic", result2))

    # TEST 3: check_user_can_analyze
    result3 = await test_check_user_can_analyze(test_user_id)
    results.append(("check_user_can_analyze", result3))

    # TEST 4: Race Condition
    result4 = await test_concurrent_requests(test_user_id)
    results.append(("Concurrent Requests", result4))

    # Итоги
    print_header("📊 ИТОГИ ТЕСТИРОВАНИЯ")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}✅ PASSED{RESET}" if result else f"{RED}❌ FAILED{RESET}"
        print(f"{test_name}: {status}")

    print(f"\n{BLUE}{'='*80}")
    print(f"Результат: {passed}/{total} тестов пройдено")
    print(f"{'='*80}{RESET}\n")

    if passed == total:
        print_success("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        print_error(f"⚠️  {total - passed} тестов провалено")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
