import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup as BS

token = "5813059906:AAF5yFnSp8G3A2ctwo151yx7nDb0BVSM4vI"
bot = telebot.TeleBot(token)

url = "https://kaktus.media/?lable=8"

source = requests.get(url).text
soup = BS(source, "lxml")


def process_info(soup):
    links = []
    titles = []
    info = soup.find_all("div", class_="Tag--articles")
    for i in info:
        pre_links = i.find_all("a", class_="ArticleItem--name")
        for x in pre_links:
            link = x.get("href")
            title = x.text
            links.append(link)
            titles.append(title)

    return links[:20], titles[:20]  # Возвращаем только первые 20 ссылок и заголовков


def get_titles_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)  # Используем инлайн-клавиатуру
    links, titles = process_info(soup)
    for index, title in enumerate(titles, start=1):
        callback_data = f"news_{index}"  # Уникальный идентификатор для каждой кнопки
        button_text = f"{index}. {title}"  # Добавляем нумерацию к тексту кнопки
        button = types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
        markup.add(button)

    quit_button = types.InlineKeyboardButton(text="Quit", callback_data="quit")
    markup.add(quit_button)

    return markup


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Ассалоум Алейкум бращке ✌️ ")


@bot.message_handler(commands=["button"])
def button_message(message):
    markup = get_titles_markup()
    bot.send_message(
        message.chat.id, "Вот 20 заголовков с кактуса", reply_markup=markup
    )


@bot.message_handler(content_types="text")
def message_reply(message):
    if message.text == "Вот 20 заголовков с кактуса":
        markup = get_titles_markup()
        bot.send_message(
            message.chat.id, "Вот 20 заголовков с кактуса", reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("news_"))
def callback_news(call):
    index = int(call.data.split("_")[1])  # Получаем индекс новости
    links, _ = process_info(soup)
    news_link = links[index - 1]  # Используем индекс для получения ссылки
    bot.send_message(call.message.chat.id, news_link)


@bot.callback_query_handler(func=lambda call: call.data == "quit")
def callback_quit(call):
    bot.send_message(call.message.chat.id, "До свидания!")


bot.polling()

