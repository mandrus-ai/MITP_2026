#include <QtTest>
#include <QFile>
#include "../databasemanager.h"

class GameDatabaseTest : public QObject
{
    Q_OBJECT

private:
    QString dbName(const QString& suffix) const
    {
        return QString("test_%1_%2.db")
            .arg(suffix)
            .arg(QDateTime::currentMSecsSinceEpoch());
    }

    void closeAndRemove(DatabaseManager* db, const QString& name)
    {
        db->closeDatabase();
        QFile::remove(name);
    }

private slots:
    void test_registration_creates_user_and_default_stats()
    {
        DatabaseManager* db = DatabaseManager::getInstance();
        QString name = dbName("registration");

        QVERIFY2(db->openDatabase(name), "Не удалось открыть тестовую SQLite БД");

        QVERIFY2(db->registerUser("test_user", "12345"),
                 "Регистрация нового пользователя должна быть успешной");

        QVERIFY2(db->loginUser("test_user", "12345"),
                 "Пользователь должен авторизоваться после успешной регистрации");

        int score = -1;
        int currency = -1;
        int skinId = -1;

        QVERIFY2(db->getUserStats("test_user", score, currency, skinId),
                 "После регистрации должна автоматически создаваться запись UserStats");

        QCOMPARE(score, 0);
        QCOMPARE(currency, 0);
        QCOMPARE(skinId, 0);

        closeAndRemove(db, name);
    }

    void test_duplicate_registration_is_rejected()
    {
        DatabaseManager* db = DatabaseManager::getInstance();
        QString name = dbName("duplicate");

        QVERIFY2(db->openDatabase(name), "Не удалось открыть тестовую SQLite БД");

        QVERIFY2(db->registerUser("same_login", "111"),
                 "Первая регистрация пользователя должна быть успешной");

        QVERIFY2(!db->registerUser("same_login", "222"),
                 "Повторная регистрация с тем же логином должна быть отклонена");

        QCOMPARE(db->getUserCount(), 1);

        closeAndRemove(db, name);
    }

    void test_auth_wrong_password_is_rejected()
    {
        DatabaseManager* db = DatabaseManager::getInstance();
        QString name = dbName("auth");

        QVERIFY2(db->openDatabase(name), "Не удалось открыть тестовую SQLite БД");

        QVERIFY2(db->registerUser("auth_user", "correct_pass"),
                 "Не удалось создать пользователя для проверки авторизации");

        QVERIFY2(!db->loginUser("auth_user", "wrong_pass"),
                 "Авторизация с неверным паролем должна быть отклонена");

        QVERIFY2(!db->loginUser("unknown_user", "correct_pass"),
                 "Авторизация несуществующего пользователя должна быть отклонена");

        closeAndRemove(db, name);
    }

    void test_score_currency_and_leaderboard_update()
    {
        DatabaseManager* db = DatabaseManager::getInstance();
        QString name = dbName("stats");

        QVERIFY2(db->openDatabase(name), "Не удалось открыть тестовую SQLite БД");

        QVERIFY2(db->registerUser("player_one", "111"), "Не удалось создать player_one");
        QVERIFY2(db->registerUser("player_two", "222"), "Не удалось создать player_two");

        QVERIFY2(db->updateScore("player_one", 250),
                 "Обновление счета player_one должно быть успешным");
        QVERIFY2(db->updateScore("player_two", 100),
                 "Обновление счета player_two должно быть успешным");

        QVERIFY2(db->updateCurrency("player_one", 300),
                 "Начисление валюты player_one должно быть успешным");

        int score = 0;
        int currency = 0;
        int skinId = 0;

        QVERIFY2(db->getUserStats("player_one", score, currency, skinId),
                 "Не удалось получить статистику player_one");

        QCOMPARE(score, 250);
        QCOMPARE(currency, 300);

        QList<QStringList> leaderboard = db->getLeaderboard();
        QVERIFY2(!leaderboard.isEmpty(), "Лидерборд не должен быть пустым");
        QCOMPARE(leaderboard.first().at(0), QString("player_one"));
        QCOMPARE(leaderboard.first().at(1), QString("250"));

        closeAndRemove(db, name);
    }

    void test_skin_purchase_and_set()
    {
        DatabaseManager* db = DatabaseManager::getInstance();
        QString name = dbName("skin");

        QVERIFY2(db->openDatabase(name), "Не удалось открыть тестовую SQLite БД");

        QVERIFY2(db->registerUser("skin_user", "123"),
                 "Не удалось создать пользователя для проверки магазина");

        QList<QStringList> skins = db->getAllSkins();
        QVERIFY2(!skins.isEmpty(), "В таблице Skins должен быть хотя бы стандартный скин");

        int selectedSkinId = -1;
        int selectedSkinPrice = 0;

        for (const QStringList& skin : skins) {
            if (skin.size() >= 3 && skin.at(0).toInt() != 0) {
                selectedSkinId = skin.at(0).toInt();
                selectedSkinPrice = skin.at(2).toInt();
                break;
            }
        }

        if (selectedSkinId == -1) {
            QSKIP("Платные скины не найдены. Проверьте заполнение таблицы Skins в openDatabase().");
        }

        QVERIFY2(!db->purchaseSkin("skin_user", selectedSkinId),
                 "Покупка скина без достаточного количества валюты должна быть отклонена");

        QVERIFY2(db->updateCurrency("skin_user", selectedSkinPrice),
                 "Не удалось начислить валюту для покупки скина");

        QVERIFY2(db->purchaseSkin("skin_user", selectedSkinId),
                 "Покупка доступного скина должна быть успешной");

        QVERIFY2(!db->purchaseSkin("skin_user", selectedSkinId),
                 "Повторная покупка уже купленного скина должна быть отклонена");

        QVERIFY2(db->setUserSkin("skin_user", selectedSkinId),
                 "Купленный скин должен устанавливаться пользователю");

        int score = 0;
        int currency = 0;
        int skinId = 0;

        QVERIFY2(db->getUserStats("skin_user", score, currency, skinId),
                 "Не удалось получить статистику после установки скина");

        QCOMPARE(currency, 0);
        QCOMPARE(skinId, selectedSkinId);

        closeAndRemove(db, name);
    }
};

QTEST_GUILESS_MAIN(GameDatabaseTest)

#include "tst_gamedatabase_test.moc"
