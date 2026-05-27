/**
 * @file main.cpp
 * @brief Точка входа в клиентское приложение.
 */

#include <QApplication>
#include "authwindow.h"

/**
 * @brief Точка входа в клиентское приложение.
 *
 * Создаёт QApplication, открывает окно авторизации
 * и запускает главный цикл обработки событий Qt.
 *
 * @param argc Количество аргументов командной строки.
 * @param argv Массив аргументов командной строки.
 * @return Код завершения приложения.
 */
int main(int argc, char* argv[])
{
    QApplication a(argc, argv);
    AuthWindow w;
    w.show();
    return a.exec();
}