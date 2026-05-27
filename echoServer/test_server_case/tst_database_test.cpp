#include <QtTest>
#include <QCoreApplication>
#include <QDateTime>
#include <QDir>
#include <QFile>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QStringList>

#include "../dataBase.h"
#include "../functionforserver.h"

class ServerDatabaseTest : public QObject
{
    Q_OBJECT

private:
    QCoreApplication* app = nullptr;

    QString databasePath() const
    {
        return QCoreApplication::applicationDirPath() + "/db_data/server_database.db";
    }

    QString uniqueLogin(const QString& prefix) const
    {
        return prefix + "_" + QString::number(QDateTime::currentMSecsSinceEpoch());
    }

    void clearTables()
    {
        QSqlDatabase db = DataBase::getDatabase();
        QVERIFY2(db.isOpen(), "База данных должна быть открыта перед очисткой таблиц");

        QSqlQuery query(db);
        QVERIFY2(query.exec("DELETE FROM achievements"), "Не удалось очистить таблицу achievements");
        QVERIFY2(query.exec("DELETE FROM user_skins"), "Не удалось очистить таблицу user_skins");
        QVERIFY2(query.exec("DELETE FROM user_backgrounds"), "Не удалось очистить таблицу user_backgrounds");
        QVERIFY2(query.exec("DELETE FROM users"), "Не удалось очистить таблицу users");

        query.exec("DELETE FROM sqlite_sequence WHERE name IN ('users', 'achievements', 'user_skins', 'user_backgrounds')");
    }

private slots:
    void initTestCase()
    {
        if (!QCoreApplication::instance()) {
            static int argc = 1;
            static char appName[] = "test_server_new";
            static char* argv[] = { appName, nullptr };
            app = new QCoreApplication(argc, argv);
        }

        DataBase::disconnect();

        QDir dbDir(QCoreApplication::applicationDirPath() + "/db_data");
        if (dbDir.exists()) {
            QFile::remove(databasePath());
        }

        QVERIFY2(DataBase::connect(), "DataBase::connect() должен успешно открыть SQLite-базу");
        clearTables();
    }

    void cleanupTestCase()
    {
        clearTables();
        DataBase::disconnect();
        QFile::remove(databasePath());
    }

    void init()
    {
        clearTables();
    }

    void test_database_connection_and_tables()
    {
        QVERIFY2(DataBase::connect(), "Повторный вызов DataBase::connect() не должен ломать подключение");

        QSqlDatabase db = DataBase::getDatabase();
        QVERIFY2(db.isValid(), "Объект QSqlDatabase должен быть валидным");
        QVERIFY2(db.isOpen(), "Соединение с базой должно быть открыто");

        QStringList tables = db.tables();
        QVERIFY2(tables.contains("users"), "После подключения должна существовать таблица users");
        QVERIFY2(tables.contains("achievements"), "После подключения должна существовать таблица achievements");
        QVERIFY2(tables.contains("user_skins"), "После подключения должна существовать таблица user_skins");
        QVERIFY2(tables.contains("user_backgrounds"), "После подключения должна существовать таблица user_backgrounds");
    }

    void test_registration_authorization_and_duplicates()
    {
        QString login = uniqueLogin("reg_user");
        QString password = "pass123";
        QString displayName = "Test Player";

        QString regRequest = QString("reg&%1&%2&%3").arg(login, password, displayName);
        QString regResponse = QString::fromUtf8(parsing(regRequest));
        QCOMPARE(regResponse, QString("reg_success&%1").arg(login));

        QVERIFY2(DataBase::userExists(login), "После регистрации пользователь должен существовать в БД");

        int userId = DataBase::getUserId(login);
        QVERIFY2(userId > 0, "После регистрации должен возвращаться корректный id пользователя");
        QCOMPARE(DataBase::getUserDisplayName(userId), displayName);
        QCOMPARE(DataBase::getUserScore(userId), 0);
        QCOMPARE(DataBase::getUserCoins(userId), 0);
        QCOMPARE(DataBase::getUserLevel(userId), 1);
        QCOMPARE(DataBase::getUserSkin(userId), 0);
        QCOMPARE(DataBase::getUserBackground(userId), 100);

        QString authResponse = QString::fromUtf8(parsing(QString("auth&%1&%2").arg(login, password)));
        QVERIFY2(authResponse.startsWith("auth_success&"), "Авторизация с корректным паролем должна завершиться успешно");

        QStringList authParts = authResponse.split('&');
        QCOMPARE(authParts.size(), 2);

        QStringList payload = authParts.at(1).split('|');
        QCOMPARE(payload.size(), 9);
        QCOMPARE(payload.at(0), displayName);
        QCOMPARE(payload.at(1).toInt(), userId);
        QCOMPARE(payload.at(2).toInt(), 0);
        QCOMPARE(payload.at(3).toInt(), 0);
        QCOMPARE(payload.at(4).toInt(), 1);
        QCOMPARE(payload.at(5).toInt(), 0);
        QCOMPARE(payload.at(6).toInt(), 100);
        QCOMPARE(payload.at(7).toInt(), 0);
        QCOMPARE(payload.at(8), QString("player"));

        QString duplicateResponse = QString::fromUtf8(parsing(regRequest));
        QCOMPARE(duplicateResponse, QString("reg_failed&user_exists"));

        QString wrongPasswordResponse = QString::fromUtf8(parsing(QString("auth&%1&wrong_password").arg(login)));
        QCOMPARE(wrongPasswordResponse, QString("auth_failed&invalid_login_or_password"));
    }

    void test_player_data_save_and_reading()
    {
        QString login = uniqueLogin("progress_user");
        QVERIFY2(DataBase::registerUser(login, "progress_pass", "Progress Player"), "Пользователь должен регистрироваться напрямую через DataBase");

        int userId = DataBase::getUserId(login);
        QVERIFY2(userId > 0, "Для сохранения прогресса нужен корректный id пользователя");

        QString saveRequest = QString("save_all&%1&1250&320&5&80").arg(userId);
        QCOMPARE(QString::fromUtf8(parsing(saveRequest)), QString("success"));

        QCOMPARE(DataBase::getUserScore(userId), 1250);
        QCOMPARE(DataBase::getUserCoins(userId), 320);
        QCOMPARE(DataBase::getUserLevel(userId), 5);
        QCOMPARE(DataBase::getUserXP(userId), 80);

        QString userDataResponse = QString::fromUtf8(parsing(QString("get_user_data&%1").arg(userId)));
        QStringList data = userDataResponse.split('|');

        QCOMPARE(data.size(), 8);
        QCOMPARE(data.at(0), QString("user_data"));
        QCOMPARE(data.at(1).toInt(), 1250);
        QCOMPARE(data.at(2).toInt(), 320);
        QCOMPARE(data.at(3).toInt(), 5);
        QCOMPARE(data.at(4).toInt(), 0);
        QCOMPARE(data.at(5).toInt(), 100);
        QCOMPARE(data.at(6).toInt(), 80);
        QCOMPARE(data.at(7), QString("Progress Player"));
    }

    void test_shop_and_achievements()
    {
        QString login = uniqueLogin("shop_user");
        QVERIFY2(DataBase::registerUser(login, "shop_pass", "Shop Player"), "Пользователь должен быть создан для проверки магазина");

        int userId = DataBase::getUserId(login);
        QVERIFY2(userId > 0, "Для покупки предмета нужен корректный id пользователя");

        QVERIFY2(DataBase::updateUserCoins(userId, 300), "Перед покупкой пользователю должны быть начислены монеты");

        QString shopBefore = QString::fromUtf8(parsing(QString("get_shop_data&%1").arg(userId)));
        QVERIFY2(shopBefore.startsWith("shop_data|300|0|100|"), "До покупки магазин должен вернуть баланс 300, стандартный скин 0 и фон 100");

        QCOMPARE(QString::fromUtf8(parsing(QString("buy_item&%1&1&skin").arg(userId))), QString("success"));
        QCOMPARE(DataBase::getUserCoins(userId), 200);

        QCOMPARE(QString::fromUtf8(parsing(QString("equip_item&%1&1&skin").arg(userId))), QString("success"));
        QCOMPARE(DataBase::getUserSkin(userId), 1);

        QString shopAfter = QString::fromUtf8(parsing(QString("get_shop_data&%1").arg(userId)));
        QVERIFY2(shopAfter.startsWith("shop_data|200|1|100|"), "После покупки и выбора скина магазин должен вернуть обновленные данные");
        QVERIFY2(shopAfter.contains("1"), "После покупки id скина должен присутствовать среди купленных предметов");

        QCOMPARE(QString::fromUtf8(parsing(QString("update_achievement&%1&7&100&1").arg(userId))), QString("success"));

        QString achievements = QString::fromUtf8(parsing(QString("get_achievements&%1").arg(userId)));
        QVERIFY2(achievements.startsWith("achievements"), "Ответ по достижениям должен начинаться с achievements");
        QVERIFY2(achievements.contains("|7:1:100"), "Достижение 7 должно быть сохранено как открытое с прогрессом 100");
    }
};

QTEST_APPLESS_MAIN(ServerDatabaseTest)

#include "tst_database_test.moc"
