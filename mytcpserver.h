/**
 * @file mytcpserver.h
 * @brief TCP server for client connections
 * @author Student
 * @version 1.0
 */

#ifndef MYTCPSERVER_H
#define MYTCPSERVER_H

#include <QObject>
#include <QTcpServer>
#include <QTcpSocket>
#include <QMap>
#include <QByteArray>
#include "databasemanager.h"

 /**
  * @brief Client session information
  */
struct ClientSession {
    QString login;          ///< Username
    QString role;           ///< "user" or "admin"
    bool authenticated;     ///< Login status
};

/**
 * @brief Main TCP server class
 *
 * Handles:
 * - Client connections on port 33333
 * - Text command parsing
 * - Access control
 */
class MyTcpServer : public QObject
{
    Q_OBJECT

public:
    /**
     * @brief Constructor - starts server on port 33333
     * @param parent Qt parent object
     */
    explicit MyTcpServer(QObject* parent = nullptr);

    /**
     * @brief Destructor - closes all connections
     */
    ~MyTcpServer();

private slots:
    /**
     * @brief Handle new client connection
     */
    void slotNewConnection();

    /**
     * @brief Handle incoming data from client
     */
    void slotServerRead();

    /**
     * @brief Handle client disconnection
     */
    void slotClientDisconnected();

private:
    /**
     * @brief Parse client command and return response
     * @param cmd Raw command bytes
     * @param clientSocket Client socket
     * @return Response bytes
     *
     * Supported commands:
     *
     * **Public (no auth):**
     * - `register <login> <password>` - create account
     * - `login <login> <password>` - authenticate
     *
     * **User (requires auth):**
     * - `help` - show commands
     * - `score <value>` - update score
     * - `addcurrency <delta>` - change currency
     * - `getstats` - show stats
     * - `skins` - list skins
     * - `buyskin <id>` - purchase skin
     * - `setskin <id>` - equip skin
     * - `leaderboard` - show top players
     *
     * **Admin only:**
     * - `admin allusers` - list all users
     * - `admin setrole <login> <role>` - change role
     * - `admin ban <login>` - ban user
     *
     * **Utility:**
     * - `echo <text>` - echo back
     * - `time` - current time
     * - `status` - client count
     * - `calc <a> <op> <b>` - calculator
     */
    QByteArray parseCommand(const QByteArray& cmd, QTcpSocket* clientSocket);

    QTcpServer* mTcpServer;
    QMap<QTcpSocket*, QByteArray> m_buffers;
    QMap<QTcpSocket*, ClientSession> m_sessions;
    DatabaseManager* dbManager;
};

#endif