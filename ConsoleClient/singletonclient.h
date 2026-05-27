/**
 * @file singletonclient.h
 * @brief Объявление SingletonClient для работы с TCP-сервером.
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
 * Класс хранит указатель на единственный экземпляр SingletonClient
 * и освобождает память при завершении работы приложения.
 */
class SingletonClientDestroyer
{
private:
    /**
     * @brief Указатель на единственный экземпляр SingletonClient.
     */
    SingletonClient* p_instance;

public:
    /**
     * @brief Удаляет экземпляр SingletonClient.
     */
    ~SingletonClientDestroyer() { delete p_instance; }

    /**
     * @brief Инициализирует указатель на экземпляр SingletonClient.
     *
     * @param p Указатель на объект SingletonClient.
     */
    void initialize(SingletonClient* p) { p_instance = p; }
};

/**
 * @class SingletonClient
 * @brief Singleton-класс TCP-клиента.
 *
 * Класс создаёт и хранит единственное TCP-соединение с сервером,
 * отправляет сообщения, принимает ответы и сообщает о событиях
 * через сигналы Qt.
 */
class SingletonClient : public QObject
{
    Q_OBJECT

private:
    /**
     * @brief Единственный экземпляр SingletonClient.
     */
    static SingletonClient* p_instance;

    /**
     * @brief Объект, отвечающий за удаление SingletonClient.
     */
    static SingletonClientDestroyer destroyer;

    /**
     * @brief TCP-сокет для соединения с сервером.
     */
    QTcpSocket* m_pSocket;

    /**
     * @brief Буфер для накопления данных, полученных от сервера.
     */
    QString m_buffer;

    /**
     * @brief Создаёт TCP-клиент.
     *
     * Конструктор закрыт, так как объект создаётся только
     * через getInstance().
     *
     * @param parent Родительский QObject.
     */
    SingletonClient(QObject* parent = nullptr);

    /**
     * @brief Запрещённый конструктор копирования.
     */
    SingletonClient(const SingletonClient&);

    /**
     * @brief Запрещённый оператор присваивания.
     */
    SingletonClient& operator = (SingletonClient&);

    /**
     * @brief Закрывает соединение и уничтожает клиент.
     */
    ~SingletonClient();

    friend class SingletonClientDestroyer;

public:
    /**
     * @brief Возвращает единственный экземпляр клиента.
     *
     * Если экземпляр ещё не создан, метод создаёт его
     * и передаёт указатель объекту SingletonClientDestroyer.
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
     * @param query Текст сообщения или команды для отправки.
     */
    void sendMessageToServer(const QString& query);

    /**
     * @brief Проверяет состояние соединения с сервером.
     *
     * @return true, если клиент подключён к серверу, иначе false.
     */
    bool isConnected() const;

public slots:
    /**
     * @brief Читает данные, полученные от сервера.
     *
     * Данные добавляются в буфер. Если получен символ конца сообщения,
     * отправляется сигнал messageFromServer().
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
     * @brief Обрабатывает ошибку TCP-сокета.
     *
     * @param error Код ошибки сокета.
     */
    void slotErrorOccurred(QAbstractSocket::SocketError error);

signals:
    /**
     * @brief Сигнал о получении сообщения от сервера.
     *
     * @param msg Текст полученного сообщения.
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
