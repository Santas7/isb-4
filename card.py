import multiprocessing
import hashlib
import logging
import main


class Card:
    def __init__(self) -> None:
        self.cores = multiprocessing.cpu_count()

    @staticmethod
    def check_card_number(card_number_, options) -> str:
        """
            проверка номера карты на соответствие хешу и бину карты
        :return: str
        """
        for card_bin in options['BINS']:
            card_number = f'{card_bin}{card_number_:06d}{options["LATER_NUM"]}'
            if hashlib.sha1(card_number.encode()).hexdigest() == options["HASH"]:
                return card_number
        main.logger.info(f'Номер карты: {card_number_} - не соответствует хешу')
        return ""

    def luna(self, card_number) -> bool:
        """
            проверка номера карты по алгоритму Луна
        :param self:
        :return: bool
        """
        try:
            card_numbers = list(map(int, card_number))
            card_numbers = card_numbers[::-1]
            for i in range(1, len(card_numbers), 2):
                card_numbers[i] *= 2
                if card_numbers[i] > 9:
                    card_numbers[i] = card_numbers[i] % 10 + card_numbers[i] // 10
            main.logger.info(f'Номер карты: {card_number} - {sum(card_numbers) % 10 == 0}')
            return sum(card_numbers) % 10 == 0
        except Exception as e:
            main.logger.warning(f'Ошибка в функции luna: {e}')