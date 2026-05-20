#include "mytcpserver.h"
#include <QDebug>
#include <QDateTime>

MyTcpServer::~MyTcpServer()
{
    mTcpServer->close();
}

MyTcpServer::MyTcpServer(QObject* parent) : QObject(parent)
{
    dbManager = DatabaseManager::getInstance();
    if (!dbManager->openDatabase("GameDB.db")) {
        qDebug() << "Failed to open database. Server will continue but database commands may fail.";
    }

    mTcpServer = new QTcpServer(this);

    connect(mTcpServer, &QTcpServer::newConnection,
        this, &MyTcpServer::slotNewConnection);

    if (!mTcpServer->listen(QHostAddress::Any, 33333)) {
        qDebug() << "Server is not started";
    }
    else {
        qDebug() << "Server is started on port 33333";
    }
}

void MyTcpServer::slotNewConnection()
{
    QTcpSocket* clientSocket = mTcpServer->nextPendingConnection();
    m_buffers.insert(clientSocket, QByteArray());
    // Инициализация сессии: не аутентифицирован
    m_sessions[clientSocket] = { "", "user", false };

    connect(clientSocket, &QTcpSocket::readyRead,
        this, &MyTcpServer::slotServerRead);
    connect(clientSocket, &QTcpSocket::disconnected,
        this, &MyTcpServer::slotClientDisconnected);

    clientSocket->write("Hello! I am game server. Please login or register.\r\n");
    qDebug() << "New client connected:" << clientSocket->peerAddress().toString();
}

void MyTcpServer::slotServerRead()
{
    QTcpSocket* socket = qobject_cast<QTcpSocket*>(sender());
    if (!socket) return;

    QByteArray data = socket->readAll();
    m_buffers[socket].append(data);

    QByteArray& buffer = m_buffers[socket];
    int index;
    while ((index = buffer.indexOf('\n')) != -1) {
        QByteArray command = buffer.left(index).trimmed();
        buffer.remove(0, index + 1);
        if (!command.isEmpty()) {
            qDebug() << "Received command:" << command;
            QByteArray response = parseCommand(command, socket);
            socket->write(response + "\r\n");
        }
    }
}

void MyTcpServer::slotClientDisconnected()
{
    QTcpSocket* socket = qobject_cast<QTcpSocket*>(sender());
    if (!socket) return;

    qDebug() << "Client disconnected:" << socket->peerAddress().toString();
    m_buffers.remove(socket);
    m_sessions.remove(socket);
    socket->deleteLater();
}

QByteArray MyTcpServer::parseCommand(const QByteArray& cmd, QTcpSocket* clientSocket)
{
    QList<QByteArray> parts = cmd.split(' ');
    if (parts.isEmpty()) return "Empty command";

    QByteArray command = parts[0].toLower();

    // Команды, доступные без аутентификации
    if (command == "register") {
        if (parts.size() < 3) return "Usage: register <login> <password>";
        QString login = parts[1];
        QString password = parts[2];
        if (dbManager->registerUser(login, password)) {
            return "Registration successful";
        }
        else {
            return "Registration failed: user already exists or DB error";
        }
    }
    else if (command == "login") {
        if (parts.size() < 3) return "Usage: login <login> <password>";
        QString login = parts[1];
        QString password = parts[2];
        if (dbManager->loginUser(login, password)) {
            ClientSession& session = m_sessions[clientSocket];
            session.login = login;
            session.authenticated = true;
            session.role = dbManager->isAdmin(login) ? "admin" : "user";

            int score, currency, skinId;
            dbManager->getUserStats(login, score, currency, skinId);
            return QString("Login successful|%1|%2|%3|%4")
                .arg(session.role).arg(score).arg(currency).arg(skinId).toUtf8();
        }
        else {
            return "Login failed: invalid credentials";
        }
    }

    // Далее требуем аутентификации
    if (!m_sessions[clientSocket].authenticated) {
        return "Please login or register first.";
    }

    ClientSession& session = m_sessions[clientSocket];

    if (command == "help" || command == "menu") {
        return "Available commands:\r\n"
            "  help, menu        - show this help\r\n"
            "  echo <text>       - echo the text\r\n"
            "  time              - show current time\r\n"
            "  status            - show number of connected clients\r\n"
            "  calc <a> <op> <b> - arithmetic (op: +, -, *, /)\r\n"
            "  users             - show total registered users\r\n"
            "  score <value>     - update your score\r\n"
            "  addcurrency <delta> - add currency\r\n"
            "  getstats          - get your stats (score, currency, skin)\r\n"
            "  skins             - list all skins\r\n"
            "  buyskin <id>      - purchase a skin\r\n"
            "  setskin <id>      - equip a skin you own\r\n"
            "  leaderboard       - top 10 players by score\r\n"
            "  admin ...         - admin commands (if admin)\r\n"
            "  quit              - close connection";
    }
    else if (command == "echo") {
        QByteArray text = (parts.size() > 1) ? cmd.mid(command.size()).trimmed() : QByteArray();
        return "ECHO: " + text;
    }
    else if (command == "time") {
        return QDateTime::currentDateTime().toString().toUtf8();
    }
    else if (command == "status") {
        return "Connected clients: " + QByteArray::number(m_buffers.size());
    }
    else if (command == "calc") {
        if (parts.size() < 4) {
            return "Usage: calc <a> <op> <b> (e.g., calc 5 + 3)";
        }
        bool ok1, ok2;
        double a = parts[1].toDouble(&ok1);
        double b = parts[3].toDouble(&ok2);
        if (!ok1 || !ok2) return "Invalid number format";
        QByteArray op = parts[2];
        double result;
        if (op == "+") result = a + b;
        else if (op == "-") result = a - b;
        else if (op == "*") result = a * b;
        else if (op == "/") {
            if (b == 0) return "Division by zero";
            result = a / b;
        }
        else return "Unknown operator. Use +, -, *, /";
        return QByteArray::number(result);
    }
    else if (command == "users") {
        int count = dbManager->getUserCount();
        if (count >= 0) return "Total users: " + QByteArray::number(count);
        else return "Error getting user count";
    }
    else if (command == "score") {
        if (parts.size() < 2) return "Usage: score <value>";
        bool ok;
        int newScore = parts[1].toInt(&ok);
        if (!ok) return "Invalid number";
        if (dbManager->updateScore(session.login, newScore))
            return "Score updated";
        else
            return "Failed to update score";
    }
    else if (command == "addcurrency") {
        if (parts.size() < 2) return "Usage: addcurrency <delta>";
        int delta = parts[1].toInt();
        if (dbManager->updateCurrency(session.login, delta))
            return "Currency updated";
        else
            return "Failed to update currency";
    }
    else if (command == "getstats") {
        int score, currency, skinId;
        if (dbManager->getUserStats(session.login, score, currency, skinId)) {
            return QString("Stats|%1|%2|%3").arg(score).arg(currency).arg(skinId).toUtf8();
        }
        else {
            return "Failed to get stats";
        }
    }
    else if (command == "skins") {
        QList<QStringList> skins = dbManager->getAllSkins();
        QByteArray response;
        for (const auto& skin : skins) {
            response += skin.join('|').toUtf8() + "\n";
        }
        return response;
    }
    else if (command == "buyskin") {
        if (parts.size() < 2) return "Usage: buyskin <skin_id>";
        int skinId = parts[1].toInt();
        if (dbManager->purchaseSkin(session.login, skinId))
            return "Skin purchased";
        else
            return "Purchase failed (not enough currency or already owned)";
    }
    else if (command == "setskin") {
        if (parts.size() < 2) return "Usage: setskin <skin_id>";
        int skinId = parts[1].toInt();
        if (dbManager->setUserSkin(session.login, skinId))
            return "Skin set";
        else
            return "You don't own this skin";
    }
    else if (command == "leaderboard") {
        QList<QStringList> leaders = dbManager->getLeaderboard();
        QByteArray response = "Leaderboard:\n";
        for (int i = 0; i < leaders.size(); ++i) {
            response += QString("%1. %2 - %3\n")
                .arg(i + 1).arg(leaders[i][0]).arg(leaders[i][1]).toUtf8();
        }
        return response;
    }
    // Админские команды
    else if (command == "admin" && session.role == "admin") {
        if (parts.size() < 2) return "Admin commands: allusers, setrole, ban";
        QByteArray subcmd = parts[1].toLower();
        if (subcmd == "allusers") {
            QList<QStringList> users = dbManager->getAllUsers();
            QByteArray response;
            for (const auto& u : users) {
                response += u.join('|').toUtf8() + "\n";
            }
            return response;
        }
        else if (subcmd == "setrole") {
            if (parts.size() < 4) return "Usage: admin setrole <login> <role>";
            QString login = parts[2];
            QString role = parts[3];
            QSqlQuery query;
            query.prepare("UPDATE Users SET role = :role WHERE login = :login");
            query.bindValue(":role", role);
            query.bindValue(":login", login);
            if (query.exec())
                return "Role updated";
            else
                return "Failed to update role";
        }
        else if (subcmd == "ban") {
            if (parts.size() < 3) return "Usage: admin ban <login>";
            QString login = parts[2];
            QSqlQuery query;
            query.prepare("DELETE FROM Users WHERE login = :login");
            query.bindValue(":login", login);
            if (query.exec())
                return "User banned";
            else
                return "Failed to ban user";
        }
        else {
            return "Unknown admin command";
        }
    }
    else if (command == "quit") {
        return "Goodbye!";
    }
    else {
        return "Unknown command. Type 'help' for available commands.";
    }
}