/**
 * @file mytcpserver.h
 * @brief Объявление TCP-сервера на базе QTcpServer.
 */
#ifndef MYTCPSERVER_H
#define MYTCPSERVER_H

#include <QObject>
#include <QTcpServer>
#include <QTcpSocket>
#include <QList>

/**
 * @class MyTcpServer
 * @brief TCP-сервер, принимающий подключения клиентов и обрабатывающий команды.
 *
 * Класс создаёт QTcpServer, слушает входящие подключения, читает данные из сокетов
 * и отправляет ответы, полученные от функции parsing().
 */
class MyTcpServer : public QObject
{
    Q_OBJECT

public:
    /**
     * @brief Создаёт сервер, запускает прослушивание порта и подключает базу данных.
     * @param parent Родительский QObject.
     */
    explicit MyTcpServer(QObject *parent = nullptr);
    /**
     * @brief Останавливает сервер и закрывает соединение с базой данных.
     */
    ~MyTcpServer();

public slots:
    /**
     * @brief Обрабатывает новое входящее клиентское подключение.
     */
    void slotNewConnection();
    /**
     * @brief Читает данные от клиента, вызывает обработчик команд и отправляет ответ.
     */
    void slotServerRead();
    /**
     * @brief Обрабатывает отключение клиента и освобождает сокет.
     */
    void slotClientDisconnected();

private:
    /**
     * @brief Объект TCP-сервера, который слушает входящие подключения.
     */
    QTcpServer *mTcpServer;

    /**
     * @brief Список всех подключённых клиентских сокетов.
     */
    QList<QTcpSocket*> sockets;
};

#endif // MYTCPSERVER_H
