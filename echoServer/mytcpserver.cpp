/**
 * @file mytcpserver.cpp
 * @brief Реализация TCP-сервера приложения.
 */
#include "mytcpserver.h"
#include "functionforserver.h"
#include "dataBase.h"

#include <QDebug>
#include <QCoreApplication>
#include <QString>

/**
 * @brief Завершает работу сервера и закрывает базу данных.
 */
MyTcpServer::~MyTcpServer()
{
    DataBase::disconnect();

    if (mTcpServer)
    {
        mTcpServer->close();
    }
}

/**
 * @brief Инициализирует TCP-сервер, слоты и соединение с базой данных.
 * @param parent Родительский объект Qt.
 */
MyTcpServer::MyTcpServer(QObject *parent)
    : QObject(parent)
{
    mTcpServer = new QTcpServer(this);

    connect(mTcpServer,
            &QTcpServer::newConnection,
            this,
            &MyTcpServer::slotNewConnection);

    if(!mTcpServer->listen(QHostAddress::Any, 33334))
    {
        qDebug() << "Server is NOT started";
    }
    else
    {
        qDebug() << "Server is started";
    }

    // Подключаем базу данных
    if(!DataBase::connect())
    {
        qDebug() << "DATABASE CONNECTION FAILED!";
    }

    DataBase::setUserPassword("ksusha2003", "2003");
    DataBase::makeAdmin("ksusha2003");
    qDebug() << "ROLE:" << DataBase::getUserRole("ksusha2003");
}

/**
 * @brief Принимает новое подключение и настраивает сигналы клиентского сокета.
 */
void MyTcpServer::slotNewConnection()
{
    QTcpSocket* clientSocket =
        mTcpServer->nextPendingConnection();

    sockets.append(clientSocket);

    connect(clientSocket,
            &QTcpSocket::readyRead,
            this,
            &MyTcpServer::slotServerRead);

    connect(clientSocket,
            &QTcpSocket::disconnected,
            this,
            &MyTcpServer::slotClientDisconnected);

    qDebug() << "New client connected!";
}

/**
 * @brief Читает запросы клиента и отправляет ответы.
 *
 * Клиент может отправить несколько команд подряд. Команды разделяются
 * символом QChar(1), поэтому сервер должен обработать каждую команду отдельно.
 */
void MyTcpServer::slotServerRead()
{
    QTcpSocket *socket = static_cast<QTcpSocket*>(sender());

    if (!socket)
    {
        qDebug() << "Socket is null!";
        return;
    }

    QByteArray array = socket->readAll();
    QString receivedData = QString::fromUtf8(array);

    qDebug() << "Received raw:" << receivedData;

    QStringList requests = receivedData.split(QChar(1), Qt::SkipEmptyParts);
    qintptr socketId = socket->socketDescriptor();

    for (QString request : requests)
    {
        request = request.trimmed();

        if (request.isEmpty())
            continue;

        qDebug() << "Processing request:" << request;

        QByteArray response = parsing(request, socketId);

        qDebug() << "Sending:" << response;

        socket->write(response);
        socket->write("\x01");
    }

    socket->flush();
}

/**
 * @brief Закрывает и удаляет сокет отключившегося клиента.
 */
void MyTcpServer::slotClientDisconnected()
{
    QTcpSocket *socket =
        qobject_cast<QTcpSocket*>(sender());

    qDebug() << "Client disconnected!";

    if(socket)
    {
        removeOnlineUser(socket->socketDescriptor());
        sockets.removeAll(socket);
        socket->close();
        socket->deleteLater();
    }
}
