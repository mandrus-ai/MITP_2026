/**
 * @file main.cpp
 * @brief Точка входа серверного приложения.
 */
#include <QCoreApplication>
#include "mytcpserver.h"

/**
 * @brief Создаёт Qt-приложение и запускает TCP-сервер.
 * @param argc Количество аргументов командной строки.
 * @param argv Массив аргументов командной строки.
 * @return Код завершения приложения.
 */
int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);
    MyTcpServer myserv;
    return a.exec();
}
