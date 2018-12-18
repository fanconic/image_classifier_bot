# Image Classifier Bot
Multithreaded Telegram Bot that can classify images via a TCP connection or Asynchronous Messaging connection, using Redis.

## TCP Connection
The first implementation exists of two scripts: server.py and bot.py. Both communicate with each other via TCP Socket connection. Additionally the bot is multithreaded with a queue, to speed up processes.

## Asynchronous Communication
Advancement of the TCP Connection. Using the Redis API an asynchronous messagequeue was implemented, that connects three scripts:
bot.py, image_downloader.py and predict.py. The last two can be run multiple times now, to scale up the process for multiple users.
