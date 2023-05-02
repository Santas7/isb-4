import multiprocessing
import hashlib
import logging


logger = logging.getLogger()
logger.setLevel('INFO')


BINS = (
519998, 529025, 516451, 522327, 522329, 523760, 527652, 528528, 529158, 529460, 529856, 530176, 530429, 531452, 531456,
531855, 531866, 531963, 532465, 534133, 534135, 534299, 510144, 518591, 518640, 540989, 526589, 528154)
HASH = "754a917a9c82f5247412006a5abe1c0eb76e1007"
LATER_NUM = "0758"


class Card:
    def __init__(self) -> None:
        self.pools = 0
        self.cores = multiprocessing.cpu_count()

    def set_cores(self, cores: int) -> None:
        """
                    установка количества ядер процессора
                :param cores:
                :return: None
                """
        self.cores = cores

    @staticmethod
    def check_card_number(card_number_) -> str:
        """
                    проверка номера карты на соответствие хешу и бину карты
                :param card_number_:
                :return: str
                """
        global BINS, HASH, LATER_NUM
        for card_bin in BINS:
            card_number = f'{card_bin}{card_number_:06d}{LATER_NUM}'
            if hashlib.sha1(card_number.encode()).hexdigest() == HASH:
                return card_number
        return ""

    def enum_card_number(self) -> dict:
        """
                    перебор номера карты с помощью многопроцессорной обработки данных и возврат номера карты
                :return: dict
                """
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as p:
            for result in p.map(self.check_card_number, range(1000000)):
                if result:
                    p.terminate()
                    return {'card_number': result, 'pools': p._processes}
        return {'card_number': None, 'pools': p._processes}

    def luna(self, card_number) -> bool:
        """
                    проверка номера карты по алгоритму Луна
                :param self:
                :return: bool
                """
        try:
            card_numbers = [int(digit) for digit in card_number][::-1]
            for i in range(1, len(card_numbers), 2):
                card_numbers[i] *= 2
                if card_numbers[i] > 9:
                    card_numbers[i] = card_numbers[i] % 10 + card_numbers[i] // 10
            logger.info(f'card_number: {card_number}, luna: {sum(card_numbers) % 10 == 0}')
            return sum(card_numbers) % 10 == 0
        except Exception as e:
            logger.warning(e)
