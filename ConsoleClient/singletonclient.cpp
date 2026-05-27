/**
 * @file singletonclient.cpp
 * @brief Реализация SingletonClient для TCP-соединения с сервером.
 */

#include "singletonclient.h"

SingletonClient * SingletonClient::p_instance = nullptr;
SingletonClientDestroyer SingletonClient::destroyer;

/**
 * @brief Создаёт TCP-сокет и подключает его сигналы к слотам клиента.
 *
 * @param parent Родительский QObject.
 */
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

/**
 * @brief Закрывает активное соединение перед удалением клиента.
 */
SingletonClient::~SingletonClient()
{
    if (m_pSocket && m_pSocket->isOpen())
        m_pSocket->close();
    qDebug() << "SingletonClient уничтожен";
}

/**
 * @brief Возвращает единственный экземпляр SingletonClient.
 *
 * @return Указатель на объект SingletonClient.
 */
SingletonClient* SingletonClient::getInstance()
{
    if (!p_instance)
    {
        p_instance = new SingletonClient();
        destroyer.initialize(p_instance);
    }
    return p_instance;
}

/**
 * @brief Подключает клиента к серверу.
 *
 * Если соединение уже открыто, повторное подключение не выполняется.
 *
 * @param host IP-адрес или имя хоста сервера.
 * @param port Порт сервера.
 */
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

/**
 * @brief Отключает клиента от сервера.
 */
void SingletonClient::disconnectFromServer()
{
    if (m_pSocket->isOpen())
    {
        m_pSocket->disconnectFromHost();
    }
}

/**
 * @brief Отправляет сообщение серверу.
 *
 * Если соединение отсутствует, генерируется сигнал errorOccurred().
 *
 * @param query Текст сообщения или команды.
 */
void SingletonClient::sendMessageToServer(const QString& query)
{
    if (!m_pSocket->isOpen())
    {
        qDebug() << "Ошибка: нет подключения к серверу";
        emit errorOccurred("Not connected to server");
        return;
    }

    m_pSocket->write(query.toUtf8());
    m_pSocket->flush();
    qDebug() << "Отправлено:" << query;
}

/**
 * @brief Проверяет, находится ли сокет в состоянии активного подключения.
 *
 * @return true, если клиент подключён, иначе false.
 */
bool SingletonClient::isConnected() const
{
    return m_pSocket->isOpen() && m_pSocket->state() == QAbstractSocket::ConnectedState;
}

/**
 * @brief Читает входящие данные от сервера.
 *
 * Метод считывает все доступные байты, добавляет их в буфер
 * и отправляет сигнал messageFromServer().
 */
void SingletonClient::slotReadyRead()
{
    QString res = "";
    while (m_pSocket->bytesAvailable() > 0)
    {
        QByteArray array = m_pSocket->readAll();
        res.append(QString::fromUtf8(array));
        m_buffer.append(QString::fromUtf8(array));
    }

    qDebug() << "Получено от сервера:" << res;

    if (res.contains('\x01'))
    {
        emit messageFromServer(m_buffer);
        m_buffer.clear();
    }
    else
    {
        emit messageFromServer(res);
    }
}

/**
 * @brief Генерирует сигнал connected() после успешного подключения.
 */
void SingletonClient::slotConnected()
{
    qDebug() << "Подключен к серверу!";
    emit connected();
}

/**
 * @brief Генерирует сигнал disconnected() после отключения.
 */
void SingletonClient::slotDisconnected()
{
    qDebug() << "Отключен от сервера!";
    emit disconnected();
}

/**
 * @brief Генерирует сигнал errorOccurred() при ошибке сокета.
 *
 * @param error Код ошибки сокета.
 */
void SingletonClient::slotErrorOccurred(QAbstractSocket::SocketError error)
{
    Q_UNUSED(error);

    QString errStr = QString("Ошибка сокета: %1").arg(m_pSocket->errorString());
    qDebug() << errStr;
    emit errorOccurred(errStr);
}
