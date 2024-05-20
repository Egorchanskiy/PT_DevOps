# Для регулярок
import re

# Для вывода
import subprocess

# Для подключения по SSH
import paramiko

# Для .env
import os
from dotenv import load_dotenv

# Реализация API Python DB
import psycopg2
from psycopg2 import Error

# .env
load_dotenv()
host = os.getenv('RM_HOST')
port = os.getenv('RM_PORT')
username = os.getenv('RM_USER')
password = os.getenv('RM_PASSWORD')
# Токен бота
TOKEN = os.getenv('TOKEN')

# Для подключения к БД
POSTGRES_HOST = os.getenv('DB_HOST')
POSTGRES_PORT = os.getenv('DB_PORT')
POSTGRES_USER = os.getenv('DB_USER')
POSTGRES_PASSWORD = os.getenv('DB_PASSWORD')
POSTGRES_DB = os.getenv('DB_DATABASE')

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Подключаем логирование
import logging
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Для DB подключения
import psycopg2
from psycopg2 import Error

connection = None

#-----------------------/GET_EMAILS-----------------------#

def get_emailsCommand(update: Update, context):
    try:
        connection = psycopg2.connect(user=POSTGRES_USER,
                                      password=POSTGRES_PASSWORD,
                                      host=POSTGRES_HOST,
                                      port=POSTGRES_PORT,
                                      database=POSTGRES_DB)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        for row in data:
            update.message.reply_text(row)
        logging.info("Команда успешно выполнена")
        return
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        return
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            return

#-----------------------/GET_PHONE_NUMBERS-----------------------#

def get_phone_numbersCommand(update: Update, context):
    try:
        connection = psycopg2.connect(user=POSTGRES_USER,
                                      password=POSTGRES_PASSWORD,
                                      host=POSTGRES_HOST,
                                      port=POSTGRES_PORT,
                                      database=POSTGRES_DB)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phones;")
        data = cursor.fetchall()
        for row in data:
            update.message.reply_text(row)
        logging.info("Команда успешно выполнена")
        return
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        return
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            return

#-----------------------/FIND_EMAIL-----------------------#

# /find_email
def find_emailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email-адресов: ')

    return 'find_email'

# Функция для поиска и вывода ответа
def find_email(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий (или нет) email адреса
    logging.info("Получен текст для поиска")

    emailRegex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', re. I) # Регулярное выражение для email

    emailList = emailRegex.findall(user_input) # Ищем email 

    if not emailList: # Обрабатываем случай, когда email нет
        update.message.reply_text('Email-адреса не найдены') # Вывод сообщения в случае отсутствия email-адресов
        logging.info("Выход из функции")

        return ConversationHandler.END # Завершаем работу обработчика диалога
    
    emailNumbers = '' # Создаем строку, в которую будем записывать email-адреса

    for i in range(len(emailList)):
        emailNumbers += f'{i+1}. {emailList[i]}\n' # Записываем email на итерации
        
    update.message.reply_text(emailNumbers) # Отправляем сообщение пользователю
    logging.info("Успешно отправлен результат")
    update.message.reply_text('Хотите записать найденные данные? (да/нет)') # Спрашиваем о записи
    logging.info("Отправлен запрос о записи")
    
    context.user_data['emailList'] = emailList # Сохраняем emailList и в случае записи запишем на БД

    return 'find_emailDB'

# Функция для записи найденных адресов в БД
def find_emailDB(update: Update, context):
    user_response = update.message.text # Пользователь отвечает
    logging.info("Получен ответ")

    if user_response == 'да' or user_response == 'Да' or user_response == 'ДА': # В данном случае можно и без регулярок
        emailList = context.user_data.get('emailList') # Сохраненный emailList с адресами передаем
        if emailList: # Подключаемся к БД
            connection = None

            try:
                connection = psycopg2.connect(user=POSTGRES_USER,
                                            password=POSTGRES_PASSWORD,
                                            host=POSTGRES_HOST,
                                            port=POSTGRES_PORT,
                                            database=POSTGRES_DB)

                cursor = connection.cursor()
                for i in range(len(emailList)):
                    cursor.execute("INSERT INTO Emails (email) VALUES ('" + emailList[i] + "');") # В цикле добавляем каждый найденныцй адрес в таблицу emails
                connection.commit()
                update.message.reply_text('Данные успешно записаны') # Сообщаем об успехе
                logging.info("Команда успешно выполнена")

            except (Exception, Error) as error:
                update.message.reply_text('При записи данных произошла непредвиденная ошибка')
                logging.error("Ошибка при работе с PostgreSQL: %s", error)

            finally:
                if connection is not None:
                    cursor.close()
                    connection.close()
                    logging.info("Соединение с PostgreSQL закрыто")
    elif user_response == 'нет' or user_response == 'Нет' or user_response == 'НЕТ':
        update.message.reply_text('Запись в базу данных отменена')
        logging.info("Отмена записи")
    else:
        update.message.reply_text('Пожалуйста, ответьте "Да" или "Нет"')
        user_response = update.message.text
        logging.info("Некорректный ввод ответа о записи")
        return

    logging.info("Выход из функции")
    return ConversationHandler.END

#-----------------------/FIND_PHONE_NUMBER-----------------------#

# /find_phone_number
def find_phone_numberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

# Функция для поиска и вывода ответа
def find_phone_number(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    logging.info("Получен текст для поиска")

    phoneNumRegex = re.compile(r'(?:(?:\+7|8)[\- ]?)?[\( ]?\d{3}[\) ]?[\- ]?\d{3}[\- ]?\d{2}[\- ]?\d{2}') # Регулярное выражение дял номеров 

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены') # Вывод сообщения в случае отсутствия номеров
        logging.info("Выход из функции")

        return ConversationHandler.END # Завершаем работу обработчика диалога
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов

    for i in range(len(phoneNumberList)):  # Массив для записи найденных номеров
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    logging.info("Успешно отправлен результат")
    update.message.reply_text('Хотите записать найденные данные? (да/нет)') # Спрашиваем о записи
    logging.info("Отправлен запрос о записи")
      
    context.user_data['phoneNumberList'] = phoneNumberList # Сохраняем phoneNumberList и в случае записи запишем на БД

    return 'find_phone_numberDB'

# Функция для записи найденных адресов в БД
def find_phone_numberDB(update: Update, context):
    user_response = update.message.text # Пользователь отвечает
    logging.info("Получен ответ") 
      
    if user_response == 'да' or user_response == 'Да' or user_response == 'ДА': # В данном случае можно и без регулярок
        phoneNumberList = context.user_data.get('phoneNumberList') # Сохраненный phoneNumberList с телефонами передаем
        if phoneNumberList: # Подключаемся к БД
            connection = None

            try:
                connection = psycopg2.connect(user=POSTGRES_USER,
                                            password=POSTGRES_PASSWORD,
                                            host=POSTGRES_HOST,
                                            port=POSTGRES_PORT,
                                            database=POSTGRES_DB)

                cursor = connection.cursor()
                for i in range(len(phoneNumberList)):
                    cursor.execute("INSERT INTO Phones (phone) VALUES ('" + phoneNumberList[i] + "');") # В цикле добавляем каждый найденныцй номер в таблицу phones
                connection.commit()
                update.message.reply_text('Данные успешно записаны') # Сообщаем об успехе
                logging.info("Команда успешно выполнена")

            except (Exception, Error) as error:
                update.message.reply_text('При записи данных произошла непредвиденная ошибка')
                logging.error("Ошибка при работе с PostgreSQL: %s", error)

            finally:
                if connection is not None:
                    cursor.close()
                    connection.close()
                    logging.info("Соединение с PostgreSQL закрыто")
    elif user_response == 'нет' or user_response == 'Нет' or user_response == 'НЕТ':
        update.message.reply_text('Запись в базу данных отменена')
        logging.info("Отмена записи")
    else:
        update.message.reply_text('Пожалуйста, ответьте "Да" или "Нет"')
        user_response = update.message.text
        logging.info("Некорректный ввод ответа о записи")
        return

    logging.info("Выход из функции")   
    return ConversationHandler.END

#-----------------------/VERIFY_PASSWORD-----------------------#

# /verify_password
def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки на сложность: ')

    return 'verify_password'

# Функция для вывода информации о сложности
def verify_password(update: Update, context):
    user_input = update.message.text # Получаем пароль на вход
    logging.info("Получен ответ")

    passwordRegex = re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}') # Регулярное выражение для проверки сложности

    passwordList = passwordRegex.findall(user_input) 

    if passwordList: # Обрабатываем случай, когда пароль сложный
        update.message.reply_text('Пароль сложный')
        logging.info("Успешно отправлен результат")

        return ConversationHandler.END # Завершаем работу обработчика диалога  
    else:
        update.message.reply_text('Пароль простой')
        logging.info("Успешно отправлен результат")

        return # Завершаем выполнение функции 

#-----------------------/GET_COMMAND-----------------------#

# /get_*
def getCommand(update: Update, context):
    
    command = update.message.text.split()[0][1:]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info("Открытие сессии")

    if command == 'get_release':
        stdin, stdout, stderr = client.exec_command('lsb_release -a')
    elif command == 'get_uname':
        stdin, stdout, stderr = client.exec_command('uname -a')
    elif command == 'get_uptime':
        stdin, stdout, stderr = client.exec_command('uptime')
    elif command == 'get_df':
        stdin, stdout, stderr = client.exec_command('df -h')
    elif command == 'get_free':
        stdin, stdout, stderr = client.exec_command('free -h')
    elif command == 'get_mpstat':
        stdin, stdout, stderr = client.exec_command('mpstat')
    elif command == 'get_w':
        stdin, stdout, stderr = client.exec_command('w')
    elif command == 'get_auths':
        stdin, stdout, stderr = client.exec_command('last -10')
    elif command == 'get_critical':
        stdin, stdout, stderr = client.exec_command('journalctl -p err -n 5')
    elif command == 'get_ps':
        stdin, stdout, stderr = client.exec_command('ps -A u | head -n 30')
    elif command == 'get_ss':
        stdin, stdout, stderr = client.exec_command('ss -tulpn')
    elif command == 'get_services':
        stdin, stdout, stderr = client.exec_command('systemctl list-units --type service --state running')

    data = stdout.read() + stderr.read()
    client.close()
    logging.info("Закрытие сессии")

    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    return update.message.reply_text(data)

#-----------------------/GET_APT_LIST-----------------------#

# /get_apt_list
def get_apt_listCommand(update: Update, context):
    update.message.reply_text('Введите название пакета для отображения информации (all - вывод всех установленных пакетов): ')

    return 'get_apt_list'

# Функция для вывода информации о пакетах
def get_apt_list(update: Update, context):
    user_input = update.message.text # Получаем название пакета на вход (или all)
    logging.info("Получен ответ")

    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    logging.info("Открытие сессии")

    if user_input == "all":
        stdin, stdout, stderr = client.exec_command('apt list --installed | head -n 30')
        logging.info("Успешное выполнение команды на удаленном хосте")
    else:
        stdin, stdout, stderr = client.exec_command('apt show ' + user_input)
        logging.info("Успешное выполнение команды на удаленном хосте")

    data = stdout.read() + stderr.read()
    client.close()
    logging.info("Закрытие сессии")

    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    update.message.reply_text(data)

    return ConversationHandler.END # Завершаем работу обработчика диалога  

#-----------------------/GET_REPL_LOGS-----------------------#

# /get_repl_logs
def get_repl_logsCommand(update: Update, context):

    command = "cat /var/log/postgresql/postgresql.log | grep repl"
    res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or res.stderr.decode() != "":
        update.message.reply_text("Невозможно открыть логи репликации")
    else:
        update.message.reply_text(res.stdout.decode().strip('\n'))

#-----------------------MAIN-----------------------#

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога find_phone_number
    convHandlerFind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'find_phone_numberDB': [MessageHandler(Filters.text & ~Filters.command, find_phone_numberDB)],
        },
        fallbacks=[]
    )

   # Обработчик диалога verify_password
    convHandlerVerify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

   # Обработчик диалога get_apt_list
    convHandlerGet_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    # Обработчик диалога find_email
    convHandlerFind_email = ConversationHandler(
    entry_points=[CommandHandler('find_email', find_emailCommand)],
    states={
        'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
        'find_emailDB': [MessageHandler(Filters.text & ~Filters.command, find_emailDB)],
    },
    fallbacks=[]
    )

	# Регистрируем обработчики диалога
    dp.add_handler(convHandlerFind_phone_number)
    dp.add_handler(convHandlerFind_email)
    dp.add_handler(convHandlerVerify_password)
    dp.add_handler(convHandlerGet_apt_list)

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("get_release", getCommand))
    dp.add_handler(CommandHandler("get_uname", getCommand))
    dp.add_handler(CommandHandler("get_uptime", getCommand))
    dp.add_handler(CommandHandler("get_df", getCommand))
    dp.add_handler(CommandHandler("get_free", getCommand))
    dp.add_handler(CommandHandler("get_mpstat", getCommand))
    dp.add_handler(CommandHandler("get_w", getCommand))
    dp.add_handler(CommandHandler("get_auths", getCommand))
    dp.add_handler(CommandHandler("get_critical", getCommand))
    dp.add_handler(CommandHandler("get_ps", getCommand))
    dp.add_handler(CommandHandler("get_ss", getCommand))
    dp.add_handler(CommandHandler("get_services", getCommand))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_listCommand))

    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logsCommand))

    dp.add_handler(CommandHandler("get_emails", get_emailsCommand))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbersCommand))

	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
