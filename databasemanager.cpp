#include "databasemanager.h"
#include <QDebug>
#include <QSqlError>
#include <QSqlRecord>

// Инициализация статических членов
DatabaseManager* DatabaseManager::p_instance = nullptr;
DatabaseDestroyer DatabaseManager::destroyer;

DatabaseDestroyer::~DatabaseDestroyer()
{
    delete p_instance;
}

void DatabaseDestroyer::initialize(DatabaseManager* p)
{
    p_instance = p;
}

DatabaseManager::DatabaseManager()
{
    db = QSqlDatabase::addDatabase("QSQLITE");
}

DatabaseManager::~DatabaseManager()
{
    if (db.isOpen())
        db.close();
}

DatabaseManager* DatabaseManager::getInstance()
{
    if (!p_instance) {
        p_instance = new DatabaseManager();
        destroyer.initialize(p_instance);
    }
    return p_instance;
}

bool DatabaseManager::openDatabase(const QString& dbName)
{
    db.setDatabaseName(dbName);
    if (!db.open()) {
        qDebug() << "Cannot open database:" << db.lastError().text();
        return false;
    }

    QSqlQuery query;

    // Создаём таблицу Users
    QString createUsers = "CREATE TABLE IF NOT EXISTS Users ("
        "login VARCHAR(20) PRIMARY KEY NOT NULL,"
        "password VARCHAR(20) NOT NULL,"
        "reg_date DATETIME DEFAULT CURRENT_TIMESTAMP,"
        "role VARCHAR(10) DEFAULT 'user')";

    if (!query.exec(createUsers)) {
        qDebug() << "Failed to create Users table:" << query.lastError().text();
        return false;
    }

    // Таблица статистики
    QString createStats = "CREATE TABLE IF NOT EXISTS UserStats ("
        "login VARCHAR(20) PRIMARY KEY NOT NULL,"
        "score INT DEFAULT 0,"
        "currency INT DEFAULT 0,"
        "skin_id INT DEFAULT 0,"
        "FOREIGN KEY(login) REFERENCES Users(login) ON DELETE CASCADE)";

    if (!query.exec(createStats)) {
        qDebug() << "Failed to create UserStats table:" << query.lastError().text();
        return false;
    }

    // Таблица скинов
    QString createSkins = "CREATE TABLE IF NOT EXISTS Skins ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "name VARCHAR(30) NOT NULL,"
        "price INT NOT NULL,"
        "image_path VARCHAR(100))";

    if (!query.exec(createSkins)) {
        qDebug() << "Failed to create Skins table:" << query.lastError().text();
        return false;
    }

    // Таблица покупок скинов
    QString createPurchases = "CREATE TABLE IF NOT EXISTS Purchases ("
        "login VARCHAR(20) NOT NULL,"
        "skin_id INT NOT NULL,"
        "purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,"
        "PRIMARY KEY (login, skin_id),"
        "FOREIGN KEY(login) REFERENCES Users(login) ON DELETE CASCADE,"
        "FOREIGN KEY(skin_id) REFERENCES Skins(id) ON DELETE CASCADE)";

    if (!query.exec(createPurchases)) {
        qDebug() << "Failed to create Purchases table:" << query.lastError().text();
        return false;
    }

    // Добавляем начальные скины (если их нет)
    QSqlQuery insertSkin;
    insertSkin.prepare("INSERT OR IGNORE INTO Skins (id, name, price, image_path) VALUES (?, ?, ?, ?)");
    insertSkin.addBindValue(0);
    insertSkin.addBindValue("Default");
    insertSkin.addBindValue(0);
    insertSkin.addBindValue("images/ship.png");
    insertSkin.exec();

    insertSkin.addBindValue(1);
    insertSkin.addBindValue("Gold");
    insertSkin.addBindValue(100);
    insertSkin.addBindValue("images/ship_gold.png");
    insertSkin.exec();

    insertSkin.addBindValue(2);
    insertSkin.addBindValue("Stealth");
    insertSkin.addBindValue(200);
    insertSkin.addBindValue("images/ship_stealth.png");
    insertSkin.exec();

    // Триггер для автоматического создания записи в UserStats при регистрации
    QString trigger = "CREATE TRIGGER IF NOT EXISTS init_user_stats AFTER INSERT ON Users "
        "BEGIN INSERT INTO UserStats (login) VALUES (NEW.login); END;";

    if (!query.exec(trigger)) {
        qDebug() << "Failed to create trigger:" << query.lastError().text();
    }

    qDebug() << "Database opened successfully!";
    return true;
}

void DatabaseManager::closeDatabase()
{
    if (db.isOpen())
        db.close();
}

bool DatabaseManager::registerUser(const QString& login, const QString& password)
{
    // Проверка существования пользователя
    QSqlQuery check;
    check.prepare("SELECT login FROM Users WHERE login = :login");
    check.bindValue(":login", login);
    if (!check.exec()) {
        qDebug() << "Check query failed:" << check.lastError().text();
        return false;
    }
    if (check.next()) {
        qDebug() << "User already exists:" << login;
        return false;
    }

    // Вставка нового пользователя
    QSqlQuery insert;
    insert.prepare("INSERT INTO Users (login, password) VALUES (:login, :password)");
    insert.bindValue(":login", login);
    insert.bindValue(":password", password);

    if (!insert.exec()) {
        qDebug() << "Insert failed:" << insert.lastError().text();
        return false;
    }

    qDebug() << "User registered successfully:" << login;
    return true;
}

bool DatabaseManager::loginUser(const QString& login, const QString& password)
{
    QSqlQuery query;
    query.prepare("SELECT password FROM Users WHERE login = :login");
    query.bindValue(":login", login);
    if (!query.exec()) {
        qDebug() << "Login query failed:" << query.lastError().text();
        return false;
    }
    if (query.next()) {
        return (query.value(0).toString() == password);
    }
    return false;
}

bool DatabaseManager::isAdmin(const QString& login)
{
    QSqlQuery query;
    query.prepare("SELECT role FROM Users WHERE login = :login");
    query.bindValue(":login", login);
    if (query.exec() && query.next()) {
        return query.value(0).toString() == "admin";
    }
    return false;
}

int DatabaseManager::getUserCount()
{
    QSqlQuery query("SELECT COUNT(*) FROM Users");
    if (query.exec() && query.next()) {
        return query.value(0).toInt();
    }
    return -1;
}

QList<QStringList> DatabaseManager::getAllUsers()
{
    QList<QStringList> result;
    QSqlQuery query("SELECT login, role, reg_date FROM Users");
    if (query.exec()) {
        while (query.next()) {
            QStringList row;
            row << query.value(0).toString()
                << query.value(1).toString()
                << query.value(2).toString();
            result.append(row);
        }
    }
    return result;
}

bool DatabaseManager::getUserStats(const QString& login, int& score, int& currency, int& skinId)
{
    QSqlQuery query;
    query.prepare("SELECT score, currency, skin_id FROM UserStats WHERE login = :login");
    query.bindValue(":login", login);
    if (query.exec() && query.next()) {
        score = query.value(0).toInt();
        currency = query.value(1).toInt();
        skinId = query.value(2).toInt();
        return true;
    }
    return false;
}

bool DatabaseManager::updateScore(const QString& login, int score)
{
    QSqlQuery query;
    query.prepare("UPDATE UserStats SET score = :score WHERE login = :login");
    query.bindValue(":score", score);
    query.bindValue(":login", login);
    return query.exec();
}

bool DatabaseManager::updateCurrency(const QString& login, int delta)
{
    QSqlQuery query;
    query.prepare("UPDATE UserStats SET currency = currency + :delta WHERE login = :login");
    query.bindValue(":delta", delta);
    query.bindValue(":login", login);
    return query.exec();
}

bool DatabaseManager::purchaseSkin(const QString& login, int skinId)
{
    // Проверяем цену
    QSqlQuery priceQuery;
    priceQuery.prepare("SELECT price FROM Skins WHERE id = :id");
    priceQuery.bindValue(":id", skinId);
    if (!priceQuery.exec() || !priceQuery.next())
        return false;
    int price = priceQuery.value(0).toInt();

    // Проверяем баланс
    int curScore, curCurrency, curSkin;
    if (!getUserStats(login, curScore, curCurrency, curSkin))
        return false;
    if (curCurrency < price)
        return false;

    // Проверяем, не куплен ли уже скин
    QSqlQuery checkPurchase;
    checkPurchase.prepare("SELECT 1 FROM Purchases WHERE login = :login AND skin_id = :skin_id");
    checkPurchase.bindValue(":login", login);
    checkPurchase.bindValue(":skin_id", skinId);
    if (checkPurchase.exec() && checkPurchase.next())
        return false;

    // Добавляем покупку
    QSqlQuery purchaseQuery;
    purchaseQuery.prepare("INSERT INTO Purchases (login, skin_id) VALUES (:login, :skin_id)");
    purchaseQuery.bindValue(":login", login);
    purchaseQuery.bindValue(":skin_id", skinId);
    if (!purchaseQuery.exec())
        return false;

    return updateCurrency(login, -price);
}

bool DatabaseManager::setUserSkin(const QString& login, int skinId)
{
    // Проверяем, есть ли у пользователя этот скин
    QSqlQuery check;
    check.prepare("SELECT 1 FROM Purchases WHERE login = :login AND skin_id = :skin_id");
    check.bindValue(":login", login);
    check.bindValue(":skin_id", skinId);
    if (!check.exec() || !check.next())
        return false;

    QSqlQuery update;
    update.prepare("UPDATE UserStats SET skin_id = :skin_id WHERE login = :login");
    update.bindValue(":skin_id", skinId);
    update.bindValue(":login", login);
    return update.exec();
}

QList<QStringList> DatabaseManager::getAllSkins()
{
    QList<QStringList> result;
    QSqlQuery query("SELECT id, name, price, image_path FROM Skins");
    if (query.exec()) {
        while (query.next()) {
            QStringList row;
            row << query.value(0).toString()
                << query.value(1).toString()
                << query.value(2).toString()
                << query.value(3).toString();
            result.append(row);
        }
    }
    return result;
}

QList<QStringList> DatabaseManager::getLeaderboard(int limit)
{
    QList<QStringList> result;
    QSqlQuery query;
    query.prepare("SELECT u.login, s.score FROM Users u "
        "JOIN UserStats s ON u.login = s.login "
        "ORDER BY s.score DESC LIMIT :limit");
    query.bindValue(":limit", limit);
    if (query.exec()) {
        while (query.next()) {
            QStringList row;
            row << query.value(0).toString() << query.value(1).toString();
            result.append(row);
        }
    }
    return result;
}