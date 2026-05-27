/**
 * @file singletonclient.cpp
 * @brief Реализация singleton-клиента для обмена данными с сервером.
 */

#include "singletonclient.h"

SingletonClient * SingletonClient::p_instance = nullptr;
SingletonClientDestroyer SingletonClient::destroyer;

SingletonClient::SingletonClient(QObject *parent) : QObject(parent)
{
    m_pSocket = new QTcpSocket(this);
    m_buffer = "";

    connect(m_pSocket, &QTcpSocket::readyRead, this, &SingletonClient::slotReadyRead);
    connect(m_pSocket, &QTcpSocket::connected, this, &SingletonClient::slotConnected);
    connect(m_pSocket, &QTcpSocket::disconnected, this, &SingletonClient::slotDisconnected);
    connect(m_pSocket, &QTcpSocket::errorOccurred, this, &SingletonClient::slotErrorOccurred);

    qDebug() << "SingletonClient создан";
}

SingletonClient::~SingletonClient()
{
    if (m_pSocket && m_pSocket->isOpen())
        m_pSocket->close();
    qDebug() << "SingletonClient уничтожен";
}

SingletonClient* SingletonClient::getInstance()
{
    if (!p_instance)
    {
        p_instance = new SingletonClient();
        destroyer.initialize(p_instance);
    }
    return p_instance;
}

void SingletonClient::connectToServer(const QString& host, quint16 port)
{
    if (m_pSocket->isOpen())
    {
        qDebug() << "Уже подключен к серверу";
        return;
    }

    m_pSocket->connectToHost(host, port);
    qDebug() << "Подключение к" << host << ":" << port;
}

void SingletonClient::disconnectFromServer()
{
    if (m_pSocket->isOpen())
    {
        m_pSocket->disconnectFromHost();
    }
}

void SingletonClient::sendMessageToServer(const QString& query)
{
    if (!m_pSocket->isOpen())
    {
        qDebug() << "Ошибка: нет подключения к серверу";
        emit errorOccurred("Not connected to server");
        return;
    }

    m_pSocket->write(query.toUtf8());
    m_pSocket->write("\x01");
    m_pSocket->flush();
    qDebug() << "Отправлено:" << query;
}

bool SingletonClient::isConnected() const
{
    return m_pSocket->isOpen() && m_pSocket->state() == QAbstractSocket::ConnectedState;
}

/**
 * @brief Читает данные от сервера и обрабатывает сообщения по разделителю.
 *
 * Сервер может прислать большой ответ частями или несколько ответов сразу.
 * Поэтому данные сначала накапливаются в буфере, а затем извлекаются
 * только полностью полученные сообщения, разделённые символом QChar(1).
 */
void SingletonClient::slotReadyRead()
{
    while (m_pSocket->bytesAvailable() > 0)
    {
        QByteArray array = m_pSocket->readAll();
        m_buffer.append(QString::fromUtf8(array));
    }

    qDebug() << "Буфер от сервера:" << m_buffer;

    while (m_buffer.contains(QChar(1)))
    {
        int separatorIndex = m_buffer.indexOf(QChar(1));

        QString message = m_buffer.left(separatorIndex).trimmed();
        m_buffer.remove(0, separatorIndex + 1);

        if (!message.isEmpty())
            emit messageFromServer(message);
    }
}

void SingletonClient::slotConnected()
{
    qDebug() << "Подключен к серверу!";
    emit connected();
}

void SingletonClient::slotDisconnected()
{
    qDebug() << "Отключен от сервера!";
    emit disconnected();
}

void SingletonClient::slotErrorOccurred(QAbstractSocket::SocketError error)
{
    QString errStr = QString("Ошибка сокета: %1").arg(m_pSocket->errorString());
    qDebug() << errStr;
    emit errorOccurred(errStr);
}