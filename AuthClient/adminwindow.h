/**
 * @file adminwindow.h
 * @brief Объявление класса окна панели администратора.
 */

#ifndef ADMINWINDOW_H
#define ADMINWINDOW_H

#include <QMainWindow>
#include <QTcpSocket>
#include <QTableWidget>
#include <QPushButton>
#include <QLabel>
#include <QString>

/**
 * @class AdminWindow
 * @brief Окно панели администратора.
 *
 * Класс отвечает за отображение списка пользователей,
 * загрузку данных с сервера, а также за блокировку
 * и разблокировку выбранных пользователей.
 */
class AdminWindow : public QMainWindow
{
    Q_OBJECT

public:
    /**
     * @brief Создаёт окно администратора.
     *
     * Инициализирует интерфейс, подключает сигналы клиента
     * и загружает список пользователей с сервера.
     *
     * @param adminLogin Логин текущего администратора.
     * @param parent Родительский виджет.
     */
    explicit AdminWindow(const QString& adminLogin, QWidget *parent = nullptr);

private slots:
    /**
     * @brief Обрабатывает сообщение, полученное от сервера.
     *
     * Разбирает ответы сервера для админ-панели:
     * список пользователей, результат блокировки,
     * разблокировки или сообщение об ошибке.
     *
     * @param msg Сообщение от сервера.
     */
    void onReadyRead(QString msg);

    /**
     * @brief Запрашивает список пользователей у сервера.
     */
    void loadUsers();

    /**
     * @brief Запрашивает общую статистику игры у сервера.
     */
    void loadStats();

    /**
     * @brief Запрашивает список пользователей, которые сейчас находятся онлайн.
     */
    void loadOnlineUsers();

    /**
     * @brief Блокирует выбранного пользователя.
     *
     * Получает логин выбранного пользователя из таблицы
     * и отправляет серверу команду на блокировку.
     */
    void banSelectedUser();

    /**
     * @brief Разблокирует выбранного пользователя.
     *
     * Получает логин выбранного пользователя из таблицы
     * и отправляет серверу команду на разблокировку.
     */
    void unbanSelectedUser();


    /**
 * @brief Изменяет пароль выбранного пользователя.
 *
 * Открывает диалоговое окно для ввода нового пароля,
 * проверяет корректность введённых данных и отправляет
 * серверу запрос на изменение пароля выбранного пользователя.
 */
    void changeSelectedUserPassword();

private:
    /**
     * @brief Создаёт и настраивает элементы интерфейса админ-панели.
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

    /**
     * @brief Отображает общую статистику игры в панели администратора.
     *
     * @param msg Ответ сервера в формате admin_stats|ключ:значение.
     */
    void showStats(const QString& msg);

    /**
     * @brief Отображает список пользователей, которые находятся онлайн.
     *
     * @param msg Ответ сервера в формате online_users|login1|login2.
     */
    void showOnlineUsers(const QString& msg);

    /**
     * @brief Считывает IP-адрес сервера из конфигурационного файла.
     *
     * @return IP-адрес сервера или 127.0.0.1 по умолчанию.
     */
    QString readServerIp() const;

    QString adminLogin;
    QString buffer;

    QTableWidget* table;
    QPushButton* refreshBtn;
    QPushButton* banBtn;
    QPushButton* unbanBtn;
    QPushButton* changePassBtn;

    /**
     * @brief Текстовая метка состояния админ-панели.
     */
    QLabel* statusLabel;

    /**
     * @brief Текстовый блок для общей статистики игры.
     */
    QLabel* statsLabel;

    /**
     * @brief Текстовый блок со списком игроков онлайн.
     */
    QLabel* onlineUsersLabel;
};

#endif // ADMINWINDOW_H
