#!/usr/bin/env python
import atexit
import os
import signal
import sys
import time

from loguru import logger

from .config import CHECK_INTERVAL, EMAIL_RECIPIENT, NAME_PID
from .exceptions import PageNotExistsError, ParsingError, WikiServiceError
from .init_repository import WikiDataInitializer
from .parser import (
    get_full_url,
    get_list_href,
    get_name,
    get_paragraph,
    get_ru_url,
    get_text_response,
)
from .repository import JsonRepository
from .send import compose_msg, send_wiki_email


class Daemon:
    def __init__(self, pidfile: str):
        self.pidfile = pidfile

    def daemonize(self):
        """UNIX double fork mechanism"""

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"fork #1: {err}\n")
            sys.exit(1)

        os.chdir("/")
        os.setsid()  # независимо от управляющего терминала
        os.umask(0)

        # второй fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"fork #2: {err}\n")
            sys.exit(1)

        # сброс
        sys.stdout.flush()
        sys.stderr.flush()
        # перенаправить потоки
        with open(os.devnull) as si, open(os.devnull, "a+") as so, open(os.devnull, "a+") as se:
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())

        # регистрация удаления
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile, "w+") as f:
            f.write(pid + "\n")

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """Запуск"""
        # Проверка pid-файла, чтобы узнать, запущен ли демон
        try:
            with open(self.pidfile) as pf:
                pid = int(pf.read().strip())
        except OSError:
            pid = None

        if pid:
            message = f"pidfile {self.pidfile} существует. Deamon уже запущен.\n"
            sys.stderr.write(message)
            sys.exit(1)

        self.daemonize()
        self.run()

    def stop(self):
        """Остановка PID"""
        # Получение номера запущенного PID
        try:
            with open(self.pidfile) as pf:
                pid = int(pf.read().strip())
        except OSError:
            pid = None

        if not pid:
            message = f"pidfile {self.pidfile} не существует. Daemon не запущен.\n"
            sys.stderr.write(message)
            return

        self.kill_pid(pid)

    def kill_pid(self, pid: int):
        """Убиваем процесс"""
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err.args))
                sys.exit()

    def run(self):
        """Данный метод следует переопределить"""
        ...


class WikiMonitorDaemon(Daemon):
    def __init__(self, pidfile: str, filename: str, is_init: bool = True):
        super().__init__(pidfile)
        json_path = os.path.expanduser(f"~/.wiki_info/{filename}")  # сохранение в домашнем катологе пользователя
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        self.repo = WikiDataInitializer(JsonRepository(json_path))
        if is_init:
            self._save_all_people()

    def _save_all_people(self):
        try:
            self.repo.save_info()
        except Exception as err:
            logger.error(f"{err}")

    def check_new_people(self):
        logger.info("Проверка...")
        try:
            current_hrefs = get_list_href()
            logger.info("Список ссылок получен")
        except (ParsingError, WikiServiceError):
            logger.error("Ошибка при сохранении ссылок")
            return
        for href in current_hrefs:
            time.sleep(2)
            if self.repo.check_person_exists(href):
                continue  # переходим к следующему человеку
            logger.info(f"Новый: {href}")
            try:
                # Получаем url
                original_url = get_full_url(href)
                logger.info(f"Получили {original_url=}")
            except PageNotExistsError:
                logger.error("Переход к следующему человеку")
                continue  # пропускаем человека без ссылки
            try:
                name, paragraph, final_url = self._get_info_about_person(original_url)
                success = self._has_sent_msg(final_url, paragraph)
                self._save_to_json(success, name, href)
            except ParsingError as err:
                logger.error(f"{err=}")
            # except HTTPSConnectionPool as err:
            #     logger.error(f"{err}")
            #     continue
        logger.info("Проверка списка завершена")

    def _get_info_about_person(self, original_url: str) -> tuple[str, str, str]:
        """Получает информацию о человеке"""
        try:
            original_page = get_text_response(original_url)
            final_url = get_ru_url(original_page, original_url)
            logger.info(f"{final_url=}")

            final_page = get_text_response(final_url)
            paragraph = get_paragraph(final_page)
            name = get_name(final_url)

            logger.info("Имя и параграф получены")
            return name, paragraph, final_url

        except (WikiServiceError, AttributeError) as err:
            raise ParsingError(f"Ошибка парсинга HTML: {err}") from err


    def _save_to_json(self, success: bool, name: str, href: str):
        """Сохраняет нового человека в список при условии, что письмо на почту было отправлено"""
        if success:
            logger.info("Подготовка сохранения в json")
            try:
                self.repo.add_new_person(href, {"name": name})
                logger.info("Человек сохранен в json")
            except Exception as err:
                logger.error(f"{err=}")
        else:
            logger.info("Сообщение не доставлено")

    def _has_sent_msg(self, final_url: str, paragraph: str) -> bool:
        """Возвращает True, если письмо отправлено, иначе False"""
        msg = compose_msg(final_url, paragraph)
        success = send_wiki_email(recipient_email=EMAIL_RECIPIENT, mg_text=msg)
        return success

    def run(self):
        logger.info("Демон запущен")
        while True:
            self.check_new_people()
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    daemon = WikiMonitorDaemon(NAME_PID, filename="text.json")
    daemon.start()
