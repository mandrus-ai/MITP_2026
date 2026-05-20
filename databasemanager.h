#ifndef DATABASEMANAGER_H
#define DATABASEMANAGER_H

#include <QSqlDatabase>
#include <QSqlQuery>
#include <QString>
#include <QMap>
#include <QList>
#include <QThread>
#include <QMutex>

class DatabaseManager;

class DatabaseDestroyer
{
public:
    ~DatabaseDestroyer();
    void initialize(DatabaseManager* p);
private:
    DatabaseManager* p_instance = nullptr;
};

class DatabaseManager
{
public:
    static DatabaseManager* getInstance();

    bool openDatabase(const QString& dbName = "GameDB");
    void closeDatabase();

    // Методы работы с пользователями
    bool registerUser(const QString& login, const QString& password);
    bool loginUser(const QString& login, const QString& password);
    bool isAdmin(const QString& login);
    int getUserCount();
    QList<QStringList> getAllUsers();

    // Статистика
    bool getUserStats(const QString& login, int& score, int& currency, int& skinId);
    bool updateScore(const QString& login, int score);
    bool updateCurrency(const QString& login, int delta);
    bool purchaseSkin(const QString& login, int skinId);
    bool setUserSkin(const QString& login, int skinId);
    QList<QStringList> getAllSkins();
    QList<QStringList> getLeaderboard(int limit = 10);

private:
    DatabaseManager();
    ~DatabaseManager();
    DatabaseManager(const DatabaseManager&) = delete;
    DatabaseManager& operator=(const DatabaseManager&) = delete;

    static DatabaseManager* p_instance;
    static DatabaseDestroyer destroyer;
    QSqlDatabase db;
    QMutex dbMutex;  // Для потокобезопасности

    friend class DatabaseDestroyer;
};

#endif // DATABASEMANAGER_H