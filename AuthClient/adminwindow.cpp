/**
 * @file adminwindow.cpp
 * @brief Реализация окна панели администратора.
 */

#include "adminwindow.h"

#include <QVBoxLayout>
#include <QHeaderView>
#include <QMessageBox>
#include <QTableWidgetItem>
#include <QFile>
#include <QCoreApplication>
#include "singletonclient.h"
#include <QInputDialog>
#include <QMap>

AdminWindow::AdminWindow(const QString& adminLogin, QWidget *parent)
    : QMainWindow(parent), adminLogin(adminLogin)
{
    setupUI();
    applyPinkTheme();

    connect(SingletonClient::getInstance(), &SingletonClient::messageFromServer, this, &AdminWindow::onReadyRead);
    connect(SingletonClient::getInstance(), &SingletonClient::connected, this, [this]() {
        loadStats();
        loadOnlineUsers();
        loadUsers();
    });
    connect(SingletonClient::getInstance(), &SingletonClient::errorOccurred, this, [this](const QString& error) {
        statusLabel->setText("Server connection error");
        QMessageBox::warning(this, "Connection error", error);
    });

    statusLabel->setText("Connected to server");
    loadStats();
    loadOnlineUsers();
    loadUsers();
}

QString AdminWindow::readServerIp() const
{
    QString ip = "127.0.0.1";

    QStringList paths;
    paths << QCoreApplication::applicationDirPath() + "/server_config.txt";
    paths << "server_config.txt";

    for (const QString& path : paths)
    {
        QFile file(path);
        if (file.open(QIODevice::ReadOnly | QIODevice::Text))
        {
            QString value = QString::fromUtf8(file.readAll()).trimmed();
            file.close();

            if (!value.isEmpty())
                return value;
        }
    }

    return ip;
}

void AdminWindow::setupUI()
{
    setWindowTitle("Edinobogic Admin Panel");
    setFixedSize(1050, 760);

    QWidget* central = new QWidget(this);
    QVBoxLayout* layout = new QVBoxLayout(central);
    layout->setContentsMargins(20, 20, 20, 20);
    layout->setSpacing(15);

    QLabel* title = new QLabel("ADMIN PANEL");
    title->setAlignment(Qt::AlignCenter);
    title->setStyleSheet("font-size: 26px; font-weight: bold; color: #8B0045;");
    layout->addWidget(title);

    statusLabel = new QLabel("Loading database...");
    statusLabel->setAlignment(Qt::AlignCenter);
    statusLabel->setStyleSheet("font-size: 13px; color: #8B0045;");
    layout->addWidget(statusLabel);
    statsLabel = new QLabel("Game statistics are loading...");
    statsLabel->setAlignment(Qt::AlignCenter);
    statsLabel->setWordWrap(true);
    statsLabel->setStyleSheet(
        "background-color: #FFF7FB;"
        "border: 2px solid #FF8FBD;"
        "border-radius: 12px;"
        "padding: 10px;"
        "font-size: 13px;"
        "color: #5A1738;"
    );
    layout->addWidget(statsLabel);

    onlineUsersLabel = new QLabel("Online users are loading...");
    onlineUsersLabel->setAlignment(Qt::AlignCenter);
    onlineUsersLabel->setWordWrap(true);
    onlineUsersLabel->setStyleSheet(
        "background-color: #FFF7FB;"
        "border: 2px solid #FF8FBD;"
        "border-radius: 12px;"
        "padding: 10px;"
        "font-size: 13px;"
        "color: #5A1738;"
    );
    layout->addWidget(onlineUsersLabel);


    table = new QTableWidget(this);
    table->setColumnCount(11);

    QStringList headers;
    headers << "ID" << "Login" << "Player Name" << "Role" << "Banned"
            << "Score" << "Coins" << "Level" << "XP"
            << "Skin" << "Background";

    table->setHorizontalHeaderLabels(headers);
    table->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    table->verticalHeader()->setVisible(false);
    table->setEditTriggers(QAbstractItemView::NoEditTriggers);
    table->setSelectionBehavior(QAbstractItemView::SelectRows);
    table->setAlternatingRowColors(true);

    layout->addWidget(table);

    refreshBtn = new QPushButton("REFRESH DATABASE");
    refreshBtn->setCursor(Qt::PointingHandCursor);
    layout->addWidget(refreshBtn, 0, Qt::AlignCenter);

    banBtn = new QPushButton("BAN USER");
    banBtn->setCursor(Qt::PointingHandCursor);
    layout->addWidget(banBtn, 0, Qt::AlignCenter);

    unbanBtn = new QPushButton("UNBAN USER");
    unbanBtn->setCursor(Qt::PointingHandCursor);
    layout->addWidget(unbanBtn, 0, Qt::AlignCenter);

    changePassBtn = new QPushButton("CHANGE PASSWORD");
    changePassBtn->setCursor(Qt::PointingHandCursor);
    layout->addWidget(changePassBtn, 0, Qt::AlignCenter);

    connect(refreshBtn, &QPushButton::clicked, this, [this]() {
        loadStats();
        loadOnlineUsers();
        loadUsers();
    });
    connect(banBtn, &QPushButton::clicked, this, &AdminWindow::banSelectedUser);
    connect(unbanBtn, &QPushButton::clicked, this, &AdminWindow::unbanSelectedUser);
    connect(changePassBtn, &QPushButton::clicked, this, &AdminWindow::changeSelectedUserPassword);

    setCentralWidget(central);
}

void AdminWindow::applyPinkTheme()
{
    setStyleSheet(
        "QMainWindow {"
        " background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        " stop:0 #FFEAF2, stop:1 #FFD1E3);"
        "}"

        "QLabel {"
        " color: #8B0045;"
        " font-weight: bold;"
        "}"

        "QTableWidget {"
        " background-color: #FFF7FB;"
        " alternate-background-color: #FFEAF2;"
        " border: 2px solid #FF8FBD;"
        " border-radius: 12px;"
        " gridline-color: #FFD1E3;"
        " color: #5A1738;"
        " selection-background-color: #FFB6D5;"
        " selection-color: #5A1738;"
        " font-size: 12px;"
        "}"

        "QHeaderView::section {"
        " background-color: #FF7DB8;"
        " color: white;"
        " padding: 7px;"
        " border: none;"
        " font-weight: bold;"
        "}"

        "QPushButton {"
        " background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        " stop:0 #FF69B4, stop:1 #FF1493);"
        " color: white;"
        " border: none;"
        " border-radius: 12px;"
        " padding: 10px 28px;"
        " font-weight: bold;"
        " font-size: 13px;"
        " min-width: 180px;"
        "}"

        "QPushButton:hover {"
        " background: #FF1493;"
        "}"
    );
}

void AdminWindow::sendToServer(const QString& data)
{
    SingletonClient::getInstance()->sendMessageToServer(data);
}

void AdminWindow::loadUsers()
{
    if (!SingletonClient::getInstance()->isConnected())
    {
        statusLabel->setText("Not connected to server");
        return;
    }

    statusLabel->setText("Loading users from database...");
    sendToServer("get_admin_users&" + adminLogin);
}


/**
 * @brief Отправляет серверу запрос на получение общей статистики игры.
 */
void AdminWindow::loadStats()
{
    if (!SingletonClient::getInstance()->isConnected())
    {
        statusLabel->setText("Not connected to server");
        return;
    }

    sendToServer("get_admin_stats&" + adminLogin);
}

/**
 * @brief Отправляет серверу запрос на получение списка онлайн-пользователей.
 */
void AdminWindow::loadOnlineUsers()
{
    if (!SingletonClient::getInstance()->isConnected())
    {
        statusLabel->setText("Not connected to server");
        return;
    }

    sendToServer("get_online_users&" + adminLogin);
}

/**
 * @brief Обрабатывает сообщения, полученные от сервера.
 *
 * Сервер может прислать несколько ответов одним пакетом. Ответы разделяются
 * управляющим символом QChar(1), поэтому метод сначала разделяет пакет
 * на отдельные сообщения, а затем обрабатывает каждое сообщение отдельно.
 *
 * Это важно для панели администратора: admin_users, admin_stats и online_users
 * не должны попадать в одну таблицу.
 *
 * @param msg Пакет данных, полученный от сервера.
 */
void AdminWindow::onReadyRead(QString msg)
{
    QStringList messages = msg.split(QChar(1), Qt::SkipEmptyParts);

    if (messages.isEmpty())
        messages << msg;

    for (QString currentMsg : messages)
    {
        currentMsg = currentMsg.trimmed();

        if (currentMsg.isEmpty())
            continue;

        qDebug() << "Received:" << currentMsg;

        if (currentMsg.startsWith("admin_stats"))
        {
            showStats(currentMsg);
            continue;
        }

        if (currentMsg.startsWith("online_users"))
        {
            showOnlineUsers(currentMsg);
            continue;
        }

        if (currentMsg == "ban_success")
        {
            statusLabel->setText("User banned successfully");
            loadStats();
            loadOnlineUsers();
            loadUsers();
            continue;
        }

        if (currentMsg == "unban_success")
        {
            statusLabel->setText("User unbanned successfully");
            loadStats();
            loadOnlineUsers();
            loadUsers();
            continue;
        }

        if (currentMsg == "password_success")
        {
            statusLabel->setText("Password changed successfully");
            QMessageBox::information(this, "Change password", "Password changed successfully.");
            loadStats();
            loadOnlineUsers();
            loadUsers();
            continue;
        }

        if (currentMsg == "password_failed")
        {
            QMessageBox::warning(this, "Change password", "Failed to change password.");
            continue;
        }

        if (currentMsg == "ban_failed" || currentMsg == "unban_failed")
        {
            QMessageBox::warning(this, "Error", currentMsg);
            continue;
        }

        if (currentMsg.startsWith("error"))
        {
            statusLabel->setText("Access denied or server error");
            QMessageBox::warning(this, "Admin error", currentMsg);
            continue;
        }

        if (!currentMsg.startsWith("admin_users"))
            continue;

        QStringList rows = currentMsg.split("|");
        rows.removeFirst();

        table->setRowCount(rows.size());

        for (int r = 0; r < rows.size(); r++)
        {
            QStringList cols = rows[r].split(":");

            for (int c = 0; c < table->columnCount(); c++)
            {
                QString value = c < cols.size() ? cols[c] : "";

                if (c == 4)
                    value = value == "1" ? "+" : "-";

                QTableWidgetItem* item = new QTableWidgetItem(value);
                item->setTextAlignment(Qt::AlignCenter);
                table->setItem(r, c, item);
            }
        }

        statusLabel->setText(QString("Database loaded. Users: %1").arg(rows.size()));
    }
}

/**
 * @brief Разбирает строку статистики от сервера и выводит её в интерфейс.
 *
 * @param msg Строка ответа сервера в формате admin_stats|ключ:значение.
 */
void AdminWindow::showStats(const QString& msg)
{
    QMap<QString, QString> values;
    QStringList parts = msg.split("|");
    parts.removeFirst();

    for (const QString& part : parts)
    {
        int separator = part.indexOf(":");

        if (separator <= 0)
            continue;

        QString key = part.left(separator);
        QString value = part.mid(separator + 1);

        values.insert(key, value);
    }

    statsLabel->setText(
        QString("Users: %1 total / %2 active / %3 banned / %4 admins\n"
                "Score: %5 total / %6 best | Coins: %7 | Avg level: %8\n"
                "Achievements: %9 | Skins: %10 | Backgrounds: %11")
            .arg(values.value("total_users", "0"))
            .arg(values.value("active_users", "0"))
            .arg(values.value("banned_users", "0"))
            .arg(values.value("admins", "0"))
            .arg(values.value("total_score", "0"))
            .arg(values.value("best_score", "0"))
            .arg(values.value("total_coins", "0"))
            .arg(values.value("avg_level", "0.00"))
            .arg(values.value("unlocked_achievements", "0"))
            .arg(values.value("bought_skins", "0"))
            .arg(values.value("bought_backgrounds", "0"))
    );
}

/**
 * @brief Разбирает список онлайн-пользователей от сервера и выводит его в интерфейс.
 *
 * @param msg Строка ответа сервера в формате online_users|login1|login2.
 */
void AdminWindow::showOnlineUsers(const QString& msg)
{
    QStringList users = msg.split("|");
    users.removeFirst();

    users.removeAll("");

    if (users.isEmpty())
    {
        onlineUsersLabel->setText("Online users: none");
        return;
    }

    onlineUsersLabel->setText(
        QString("Online users (%1): %2")
            .arg(users.size())
            .arg(users.join(", "))
    );
}

void AdminWindow::banSelectedUser()
{
    int row = table->currentRow();

    if (row < 0)
    {
        QMessageBox::warning(this, "Ban user", "Select a user first.");
        return;
    }

    QString targetLogin = table->item(row, 1)->text();

    if (targetLogin == adminLogin)
    {
        QMessageBox::warning(this, "Ban user", "You cannot ban yourself.");
        return;
    }

    sendToServer("ban_user&" + adminLogin + "&" + targetLogin);
}

void AdminWindow::unbanSelectedUser()
{
    int row = table->currentRow();

    if (row < 0)
    {
        QMessageBox::warning(this, "Unban user", "Select a user first.");
        return;
    }

    QString targetLogin = table->item(row, 1)->text();

    sendToServer("unban_user&" + adminLogin + "&" + targetLogin);
}


/**
 * @brief Изменяет пароль выбранного пользователя.
 *
 * Функция получает выбранную строку таблицы пользователей,
 * запрашивает новый пароль через диалоговое окно и отправляет
 * серверу команду set_user_password.
 */
void AdminWindow::changeSelectedUserPassword()
{
    int row = table->currentRow();

    if (row < 0)
    {
        QMessageBox::warning(this, "Change password", "Select a user first.");
        return;
    }

    QString targetLogin = table->item(row, 1)->text();

    bool ok = false;
    QString newPassword = QInputDialog::getText(
        this,
        "Change password",
        "Enter new password for user " + targetLogin + ":",
        QLineEdit::Password,
        "",
        &ok
        );

    if (!ok)
        return;

    newPassword = newPassword.trimmed();

    if (newPassword.isEmpty())
    {
        QMessageBox::warning(this, "Change password", "Password cannot be empty.");
        return;
    }

    if (newPassword.contains("&"))
    {
        QMessageBox::warning(this, "Change password", "Password cannot contain symbol '&'.");
        return;
    }

    sendToServer("set_user_password&" + adminLogin + "&" + targetLogin + "&" + newPassword);
}
