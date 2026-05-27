/**
 * @file main.cpp
 * @brief Консольный тестовый клиент для проверки соединения с сервером.
 */

#include <QCoreApplication>
#include <QTimer>
#include <iostream>
#include "singletonclient.h"

/**
 * @brief Точка входа в консольное клиентское приложение.
 *
 * Создаёт объект QCoreApplication, получает экземпляр SingletonClient,
 * подключает обработчики сигналов клиента, устанавливает соединение
 * с сервером и отправляет введённое пользователем сообщение.
 *
 * @param argc Количество аргументов командной строки.
 * @param argv Массив аргументов командной строки.
 * @return Код завершения приложения.
 */
int main(int argc, char* argv[])
{
    QCoreApplication a(argc, argv);

    SingletonClient* client = SingletonClient::getInstance();

    QObject::connect(client, &SingletonClient::messageFromServer, [](const QString& msg){
        std::cout << "Ответ от сервера: " << msg.toStdString() << std::endl;
    });

    // ИСПРАВЛЕНО: добавлен захват &a или [&a]
    QObject::connect(client, &SingletonClient::connected, [client, &a](){
        std::cout << "Подключено к серверу!" << std::endl;
        std::cout << "Введите сообщение для отправки: ";

        std::string msg;
        std::getline(std::cin, msg);

        QString qmsg = QString::fromStdString(msg);
        client->sendMessageToServer(qmsg);

        QTimer::singleShot(2000, client, &SingletonClient::disconnectFromServer);
        QTimer::singleShot(2500, &a, &QCoreApplication::quit);
    });

    QObject::connect(client, &SingletonClient::errorOccurred, [](const QString& err){
        std::cout << "Ошибка: " << err.toStdString() << std::endl;
    });

    client->connectToServer("127.0.0.1", 33334);

    return a.exec();
}
