/**
 * @file authwindow.h
 * @brief Объявление класса окна авторизации и регистрации.
 */

#ifndef AUTHWINDOW_H
#define AUTHWINDOW_H

#include <QMainWindow>
#include <QTcpSocket>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QTabWidget>
#include <QProcess>
#include <QCoreApplication>

/**
 * @class AuthWindow
 * @brief Окно авторизации и регистрации пользователя.
 *
 * Класс отвечает за подключение к серверу, вход пользователя,
 * регистрацию нового аккаунта и запуск игры после успешной авторизации.
 */
class AuthWindow : public QMainWindow
{
    Q_OBJECT

public:
    /**
     * @brief Создаёт окно авторизации.
     *
     * Настраивает интерфейс, применяет тему оформления,
     * подключает сигналы сетевого клиента и выполняет подключение к серверу.
     *
     * @param parent Родительский виджет.
     */
    AuthWindow(QWidget *parent = nullptr);

    /**
     * @brief Уничтожает окно авторизации.
     */
    ~AuthWindow();

private slots:
    /**
     * @brief Обрабатывает нажатие кнопки входа.
     *
     * Проверяет заполненность полей логина и пароля,
     * после чего отправляет команду авторизации на сервер.
     */
    void onAuth();

    /**
     * @brief Обрабатывает нажатие кнопки регистрации.
     *
     * Проверяет заполненность полей и совпадение паролей,
     * после чего отправляет команду регистрации на сервер.
     */
    void onReg();

    /**
     * @brief Обрабатывает сообщение, полученное от сервера.
     *
     * Разбирает ответы авторизации и регистрации.
     * При успешном входе открывает админ-панель для администратора
     * или запускает игру для обычного пользователя.
     *
     * @param msg Сообщение от сервера.
     */
    void onReadyRead(QString msg);

    /**
     * @brief Обрабатывает успешное подключение к серверу.
     */
    void onConnected();

    /**
     * @brief Обрабатывает отключение от сервера.
     */
    void onDisconnected();

    /**
     * @brief Обрабатывает ошибку сетевого подключения.
     *
     * @param error Текст ошибки.
     */
    void onError(const QString& error);

private:
    /**
     * @brief Создаёт элементы интерфейса окна авторизации и регистрации.
     */
    void setupUI();

    /**
     * @brief Применяет розовую тему оформления к окну.
     */
    void applyPinkTheme();

    /**
     * @brief Отправляет строковую команду на сервер.
     *
     * @param data Команда или данные для отправки.
     */
    void sendToServer(const QString& data);



    QTabWidget* tabWidget;
    QLineEdit* authLogin;
    QLineEdit* authPass;
    QPushButton* authBtn;
    QLabel* authStatus;

    QLineEdit* regLogin;
    QLineEdit* regDisplayName;
    QLineEdit* regPass;
    QLineEdit* regConfirmPass;
    QPushButton* regBtn;
    QLabel* regStatus;

    QLabel* connectionStatus;
    QString buffer;
};

#endif // AUTHWINDOW_H
