/**
 * @file singletonclient.h
 * @brief Объявление singleton-клиента для сетевого обмена с сервером.
 */

#ifndef SINGLETONCLIENT_H
#define SINGLETONCLIENT_H

#include <QObject>
#include <QTcpSocket>
#include <QString>
#include <QDebug>

class SingletonClient;

/**
 * @class SingletonClientDestroyer
 * @brief Вспомогательный класс для удаления SingletonClient.
 *
 * Класс отвечает за корректное освобождение памяти,
 * выделенной под единственный экземпляр SingletonClient.
 */
class SingletonClientDestroyer
{
private:
    SingletonClient* p_instance;
public:
    /**
     * @brief Удаляет экземпляр SingletonClient.
     */
    ~SingletonClientDestroyer() { delete p_instance; }

    /**
     * @brief Сохраняет указатель на экземпляр SingletonClient.
     *
     * @param p Указатель на объект SingletonClient.
     */
    void initialize(SingletonClient* p) { p_instance = p; }
};

/**
 * @class SingletonClient
 * @brief Singleton-класс сетевого клиента.
 *
 * Класс обеспечивает единственное подключение к TCP-серверу,
 * отправку сообщений, получение ответов и передачу событий
 * через сигналы Qt.
 */
class SingletonClient : public QObject
{
    Q_OBJECT

private:
    static SingletonClient* p_instance;
    static SingletonClientDestroyer destroyer;

    QTcpSocket* m_pSocket;
    QString m_buffer;

    SingletonClient(QObject* parent = nullptr);
    SingletonClient(const SingletonClient&);
    SingletonClient& operator = (SingletonClient&);
    ~SingletonClient();

    friend class SingletonClientDestroyer;

public:
    /**
     * @brief Возвращает единственный экземпляр клиента.
     *
     * Если объект ещё не создан, создаёт его и инициализирует destroyer.
     *
     * @return Указатель на SingletonClient.
     */
    static SingletonClient* getInstance();

    /**
     * @brief Подключается к TCP-серверу.
     *
     * @param host IP-адрес или имя хоста сервера.
     * @param port Порт сервера.
     */
    void connectToServer(const QString& host, quint16 port);

    /**
     * @brief Отключается от сервера.
     */
    void disconnectFromServer();

    /**
     * @brief Отправляет сообщение серверу.
     *
     * К сообщению добавляется специальный символ-разделитель,
     * по которому сервер определяет конец сообщения.
     *
     * @param query Строка запроса для отправки.
     */
    void sendMessageToServer(const QString& query);

    /**
     * @brief Проверяет, подключён ли клиент к серверу.
     *
     * @return true, если соединение активно, иначе false.
     */
    bool isConnected() const;

public slots:
    /**
     * @brief Читает данные, пришедшие от сервера.
     *
     * Накапливает данные в буфере и отправляет сигнал messageFromServer().
     */
    void slotReadyRead();

    /**
     * @brief Обрабатывает успешное подключение к серверу.
     */
    void slotConnected();

    /**
     * @brief Обрабатывает отключение от сервера.
     */
    void slotDisconnected();

    /**
     * @brief Обрабатывает ошибку сокета.
     *
     * @param error Тип ошибки сокета.
     */
    void slotErrorOccurred(QAbstractSocket::SocketError error);

signals:
    /**
     * @brief Сигнал о получении сообщения от сервера.
     *
     * @param msg Полученное сообщение.
     */
    void messageFromServer(const QString& msg);

    /**
     * @brief Сигнал об успешном подключении к серверу.
     */
    void connected();

    /**
     * @brief Сигнал об отключении от сервера.
     */
    void disconnected();

    /**
     * @brief Сигнал об ошибке соединения.
     *
     * @param err Текст ошибки.
     */
    void errorOccurred(const QString& err);
};

#endif // SINGLETONCLIENT_H
