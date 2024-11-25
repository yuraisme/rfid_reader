import threading
from pirc522 import RFID
import time
import queue
import RPi.GPIO as GPIO

# Очередь для обмена данными
data_queue = queue.Queue()

# Событие для завершения потоков
exit_event = threading.Event()

def card_reading():
    rdr = RFID()
    prev_id = 0
    while not exit_event.is_set():
        rdr.wait_for_tag()
        # print('tag detected!')
        uid = rdr.read_id(as_number = True)
        if uid is not None and isinstance(uid, int):
            # if prev_id == uid:
            #     time.sleep(2)
            #     prev_id = 0
            #     # print(prev_id)

            if data_queue.empty():
                data_queue.put(uid)  # Кладем UID в очередь
            time.sleep(2)
            # print(f'UID: {uid:X}')
            prev_id = uid
    print('Exit from card_reading')


def get_uid():
    while not exit_event.is_set():  # Проверяем, не нужно ли завершаться
        try:
            # Извлекаем данные из очереди
            uid = data_queue.get(timeout=0.1)  # Ожидаем данные максимум 1 секунду
            print(f"[do_smt] Processing card: {uid}")
            data_queue.task_done()  # Уведомляем, что задача обработана
        except queue.Empty:
            pass  # Если данных нет, продолжаем цикл
    print('Exit from get_uid')

if __name__ == '__main__':
    # card_reading()
    thread1 = threading.Thread(target=card_reading)
    thread2 = threading.Thread(target=get_uid)
    # Запускаем потоки
    thread1.start()
    thread2.start()
    try:
        while True:  # Основной цикл программы
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[Main] Exiting program...")
        exit_event.set()  # Устанавливаем флаг завершения
        thread1.join()  # Дожидаемся завершения потока card_reading
        thread2.join()  # Дожидаемся завершения потока do_smt

    print("[Main] Program has exited.")