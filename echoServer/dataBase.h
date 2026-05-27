/**
 * @file dataBase.h
 * @brief Описание класса DataBase для работы с SQLite-базой данных сервера.
 *
 * Файл содержит статический класс-помощник, который управляет подключением к базе данных,
 * регистрацией и авторизацией пользователей, сохранением игрового прогресса,
 * достижениями, магазином и административными функциями.
 */
#ifndef DATABASE_H
#define DATABASE_H

#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QDebug>
#include <QByteArray>
#include <QString>
#include <QCoreApplication>
#include <QDir>

/**
 * @class DataBase
 * @brief Статический класс для доступа к базе данных сервера.
 *
 * Класс инкапсулирует работу с таблицами пользователей, достижений, купленных скинов
 * и фонов. Все методы являются статическими, поэтому объект DataBase создавать не нужно.
 */
class DataBase
{
public:
    /**
     * @brief Подключается к SQLite-базе данных и создаёт необходимые таблицы.
     *
     * Метод открывает соединение с именем \c main_connection. Если базы или таблиц ещё нет,
     * они создаются автоматически в каталоге \c db_data рядом с исполняемым файлом.
     *
     * @return \c true, если соединение открыто и основная таблица создана успешно;
     *         \c false при ошибке открытия базы или создания таблицы пользователей.
     */
    static bool connect()
    {
        if (!QSqlDatabase::contains("main_connection"))
        {
            db = QSqlDatabase::addDatabase("QSQLITE", "main_connection");
            // РАБОЧИЙ ПУТЬ - как было раньше
            QString dbDir = QCoreApplication::applicationDirPath() + "/db_data";
            QDir().mkpath(dbDir);

            QString dbPath = dbDir + "/server_database.db";
            qDebug() << "DB path:" << dbPath;

            db.setDatabaseName(dbPath);        }
        else
        {
            db = QSqlDatabase::database("main_connection");
        }

        if (!db.open())
        {
            qDebug() << "Database open error:" << db.lastError().text();
            return false;
        }

        QSqlQuery query(db);

        QString createTable =
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "login TEXT UNIQUE NOT NULL,"
            "display_name TEXT,"
            "password TEXT NOT NULL,"
            "role TEXT DEFAULT 'player',"
            "banned INTEGER DEFAULT 0,"
            "score INTEGER DEFAULT 0,"
            "coins INTEGER DEFAULT 0,"
            "level INTEGER DEFAULT 1,"
            "xp INTEGER DEFAULT 0,"
            "skin INTEGER DEFAULT 0,"
            "background INTEGER DEFAULT 100,"
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")";

        if (!query.exec(createTable))
        {
            qDebug() << "Create table error:" << query.lastError().text();
            return false;
        }

        QSqlQuery alterRole(db);
        alterRole.exec("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'player'");

        QSqlQuery alterDisplayName(db);
        alterDisplayName.exec("ALTER TABLE users ADD COLUMN display_name TEXT");

        QSqlQuery alterBanned(db);
        alterBanned.exec("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0");


        QString createAchievementsTable =
            "CREATE TABLE IF NOT EXISTS achievements ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_id INTEGER NOT NULL,"
            "achievement_id INTEGER NOT NULL,"
            "unlocked BOOLEAN DEFAULT 0,"
            "progress INTEGER DEFAULT 0,"
            "unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "FOREIGN KEY(user_id) REFERENCES users(id),"
            "UNIQUE(user_id, achievement_id)"
            ")";

        if (!query.exec(createAchievementsTable))
        {
            qDebug() << "Create achievements table error:" << query.lastError().text();
        }

        QString createUserSkinsTable =
            "CREATE TABLE IF NOT EXISTS user_skins ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_id INTEGER NOT NULL,"
            "skin_id INTEGER NOT NULL,"
            "FOREIGN KEY(user_id) REFERENCES users(id),"
            "UNIQUE(user_id, skin_id)"
            ")";

        if (!query.exec(createUserSkinsTable))
        {
            qDebug() << "Create user skins table error:" << query.lastError().text();
        }

        QString createUserBackgroundsTable =
            "CREATE TABLE IF NOT EXISTS user_backgrounds ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "user_id INTEGER NOT NULL,"
            "bg_id INTEGER NOT NULL,"
            "FOREIGN KEY(user_id) REFERENCES users(id),"
            "UNIQUE(user_id, bg_id)"
            ")";

        if (!query.exec(createUserBackgroundsTable))
        {
            qDebug() << "Create user backgrounds table error:" << query.lastError().text();
        }

        qDebug() << "Database connected successfully";
        return true;
    }

    /**
     * @brief Закрывает активное соединение с базой данных.
     */
    static void disconnect()
    {
        if (db.isOpen())
        {
            db.close();
            qDebug() << "Database disconnected";
        }
    }

    /**
     * @brief Возвращает текущее соединение с базой данных.
     * @return Объект QSqlDatabase, используемый классом DataBase.
     */
    static QSqlDatabase getDatabase()
    {
        return db;
    }

    /**
     * @brief Проверяет существование пользователя по логину.
     * @param login Логин пользователя.
     * @return \c true, если пользователь найден; иначе \c false.
     */
    static bool userExists(const QString& login)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("SELECT id FROM users WHERE login = :login");
        query.bindValue(":login", login.trimmed());

        if (!query.exec()) return false;
        return query.next();
    }

    /**
     * @brief Регистрирует нового пользователя.
     *
     * После создания записи пользователю автоматически добавляются стартовый скин
     * и стартовый фон.
     *
     * @param login Логин пользователя.
     * @param password Пароль пользователя.
     * @param displayName Отображаемое имя игрока.
     * @return \c true при успешной регистрации; иначе \c false.
     */
    static bool registerUser(const QString& login, const QString& password, const QString& displayName)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("INSERT INTO users (login, display_name, password) VALUES (:login, :display_name, :password)");
        query.bindValue(":login", login.trimmed());
        query.bindValue(":display_name", displayName.trimmed());
        query.bindValue(":password", password.trimmed());

        if (!query.exec())
        {
            qDebug() << "Register error:" << query.lastError().text();
            return false;
        }

        int userId = getUserId(login);

        QSqlQuery insertSkin(db);
        insertSkin.prepare("INSERT INTO user_skins (user_id, skin_id) VALUES (:user_id, 0)");
        insertSkin.bindValue(":user_id", userId);
        insertSkin.exec();

        QSqlQuery insertBg(db);
        insertBg.prepare("INSERT INTO user_backgrounds (user_id, bg_id) VALUES (:user_id, 100)");
        insertBg.bindValue(":user_id", userId);
        insertBg.exec();

        return true;
    }

    /**
     * @brief Проверяет логин и пароль пользователя.
     * @param login Логин пользователя.
     * @param password Пароль пользователя.
     * @return \c true, если пара логин/пароль найдена в базе; иначе \c false.
     */
    static bool authenticateUser(const QString& login, const QString& password)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("SELECT id FROM users WHERE login = :login AND password = :password");
        query.bindValue(":login", login.trimmed());
        query.bindValue(":password", password.trimmed());

        if (!query.exec()) return false;
        return query.next();
    }

    /**
     * @brief Возвращает идентификатор пользователя по логину.
     * @param login Логин пользователя.
     * @return Идентификатор пользователя или \c -1, если пользователь не найден.
     */
    static int getUserId(const QString& login)
    {
        if (!db.isOpen()) return -1;

        QSqlQuery query(db);
        query.prepare("SELECT id FROM users WHERE login = :login");
        query.bindValue(":login", login);

        if (query.exec() && query.next())
        {
            return query.value(0).toInt();
        }
        return -1;
    }

    /**
     * @brief Возвращает количество очков пользователя.
     * @param userId Идентификатор пользователя.
     * @return Значение поля \c score или \c 0 при ошибке.
     */
    static int getUserScore(int userId)
    {
        if (!db.isOpen()) return 0;

        QSqlQuery query(db);
        query.prepare("SELECT score FROM users WHERE id = :id");
        query.bindValue(":id", userId);

        if (query.exec() && query.next())
        {
            return query.value(0).toInt();
        }
        return 0;
    }

    /**
     * @brief Возвращает количество монет пользователя.
     * @param userId Идентификатор пользователя.
     * @return Значение поля \c coins или \c 0 при ошибке.
     */
    static int getUserCoins(int userId)
    {
        if (!db.isOpen()) return 0;

        QSqlQuery query(db);
        query.prepare("SELECT coins FROM users WHERE id = :id");
        query.bindValue(":id", userId);

        if (query.exec() && query.next())
        {
            return query.value(0).toInt();
        }
        return 0;
    }

    /**
     * @brief Возвращает уровень пользователя.
     * @param userId Идентификатор пользователя.
     * @return Значение поля \c level или \c 1 при ошибке.
     */
    static int getUserLevel(int userId)
    {
        if (!db.isOpen()) return 1;

        QSqlQuery query(db);
        query.prepare("SELECT level FROM users WHERE id = :id");
        query.bindValue(":id", userId);

        if (query.exec() && query.next())
        {
            return query.value(0).toInt();
        }
        return 1;
    }

    /**
     * @brief Возвращает количество опыта пользователя.
     * @param userId Идентификатор пользователя.
     * @return Значение поля \c xp или \c 0 при ошибке.
     */
    static int getUserXP(int userId)
    {
        if (!db.isOpen()) return 0;

        QSqlQuery query(db);
        query.prepare("SELECT xp FROM users WHERE id = :id");
        query.bindValue(":id", userId);

        if (query.exec() && query.next())
        {
            return query.value(0).toInt();
        }
        return 0;
    }

    /**
     * @brief Возвращает идентификатор выбранного скина пользователя.
     * @param userId Идентификатор пользователя.
     * @return Идентификатор скина или \c 0 при ошибке.
     */
    static int getUserSkin(int userId)
    {
        if (!db.isOpen()) return 0;

        QSqlQuery query(db);
        query.prepare("SELECT skin FROM users WHERE id = :id");
        query.bindValue(":id", userId);

        if (query.exec() && query.next())
        {
            return query.value(0).toInt();
        }
        return 0;
    }

    /**
     * @brief Возвращает идентификатор выбранного фона пользователя.
     * @param userId Идентификатор пользователя.
     * @return Идентификатор фона или \c 100 при ошибке.
     */
    static int getUserBackground(int userId)
    {
        if (!db.isOpen()) return 100;

        QSqlQuery query(db);
        query.prepare("SELECT background FROM users WHERE id = :id");
        query.bindValue(":id", userId);

        if (query.exec() && query.next())
        {
            return query.value(0).toInt();
        }
        return 100;
    }

    /**
     * @brief Обновляет количество очков пользователя.
     * @param userId Идентификатор пользователя.
     * @param newScore Новое количество очков.
     * @return \c true при успешном обновлении; иначе \c false.
     */
    static bool updateUserScore(int userId, int newScore)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET score = :score WHERE id = :id");
        query.bindValue(":score", newScore);
        query.bindValue(":id", userId);

        return query.exec();
    }

    /**
     * @brief Добавляет монеты пользователю.
     * @param userId Идентификатор пользователя.
     * @param amount Количество монет, которое нужно прибавить.
     * @return \c true при успешном обновлении; иначе \c false.
     */
    static bool addUserCoins(int userId, int amount)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET coins = coins + :amount WHERE id = :id");
        query.bindValue(":amount", amount);
        query.bindValue(":id", userId);

        return query.exec();
    }

    /**
     * @brief Устанавливает новое количество монет пользователя.
     * @param userId Идентификатор пользователя.
     * @param newCoins Новое количество монет.
     * @return \c true при успешном обновлении; иначе \c false.
     */
    static bool updateUserCoins(int userId, int newCoins)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET coins = :coins WHERE id = :id");
        query.bindValue(":coins", newCoins);
        query.bindValue(":id", userId);

        return query.exec();
    }

    /**
     * @brief Обновляет уровень и опыт пользователя.
     * @param userId Идентификатор пользователя.
     * @param level Новый уровень.
     * @param xp Новое количество опыта.
     * @return \c true при успешном обновлении; иначе \c false.
     */
    static bool updateUserLevel(int userId, int level, int xp)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET level = :level, xp = :xp WHERE id = :id");
        query.bindValue(":level", level);
        query.bindValue(":xp", xp);
        query.bindValue(":id", userId);

        return query.exec();
    }

    /**
     * @brief Сохраняет основные игровые данные пользователя одним запросом.
     * @param userId Идентификатор пользователя.
     * @param score Количество очков.
     * @param coins Количество монет.
     * @param level Уровень игрока.
     * @param xp Количество опыта.
     * @return \c true при успешном сохранении; иначе \c false.
     */
    static bool savePlayerData(int userId, int score, int coins, int level, int xp)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET score = :score, coins = :coins, level = :level, xp = :xp WHERE id = :id");
        query.bindValue(":score", score);
        query.bindValue(":coins", coins);
        query.bindValue(":level", level);
        query.bindValue(":xp", xp);
        query.bindValue(":id", userId);

        return query.exec();
    }

    /** @name Достижения */
    /// @{

    /**
     * @brief Возвращает список достижений пользователя в строковом формате.
     *
     * Формат ответа: \c achievements|achievement_id:unlocked:progress...
     *
     * @param userId Идентификатор пользователя.
     * @return Строка с данными достижений или \c error при недоступной базе данных.
     */
    static QString getUserAchievements(int userId)
    {
        if (!db.isOpen()) return "error";

        QSqlQuery query(db);
        query.prepare("SELECT achievement_id, unlocked, progress FROM achievements WHERE user_id = :user_id");
        query.bindValue(":user_id", userId);

        QString result = "achievements";
        if (query.exec())
        {
            while (query.next())
            {
                result += QString("|%1:%2:%3")
                .arg(query.value(0).toInt())
                    .arg(query.value(1).toInt())
                    .arg(query.value(2).toInt());
            }
        }
        return result;
    }

    /**
     * @brief Создаёт или обновляет прогресс достижения пользователя.
     * @param userId Идентификатор пользователя.
     * @param achId Идентификатор достижения.
     * @param progress Текущий прогресс достижения.
     * @param unlocked Флаг получения достижения.
     * @return \c true при успешном сохранении; иначе \c false.
     */
    static bool updateAchievementProgress(int userId, int achId, int progress, bool unlocked)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare(
            "INSERT INTO achievements (user_id, achievement_id, progress, unlocked) "
            "VALUES (:user_id, :ach_id, :progress, :unlocked) "
            "ON CONFLICT(user_id, achievement_id) DO UPDATE SET "
            "progress = excluded.progress, "
            "unlocked = excluded.unlocked"
            );
        query.bindValue(":user_id", userId);
        query.bindValue(":ach_id", achId);
        query.bindValue(":progress", progress);
        query.bindValue(":unlocked", unlocked ? 1 : 0);

        return query.exec();
    }

    /// @}

    /** @name Магазин и таблица лидеров */
    /// @{

    /**
     * @brief Возвращает данные магазина и инвентаря пользователя.
     *
     * Формат ответа: \c shop_data|coins|skin|background|ownedSkins|ownedBackgrounds
     *
     * @param userId Идентификатор пользователя.
     * @return Строка с данными магазина или \c error при ошибке.
     */
    static QString getShopData(int userId)
    {
        if (!db.isOpen()) return "error";

        QSqlQuery query(db);
        query.prepare("SELECT coins, skin, background FROM users WHERE id = :id");
        query.bindValue(":id", userId);

        if (query.exec() && query.next())
        {
            int coins = query.value(0).toInt();
            int skin = query.value(1).toInt();
            int bg = query.value(2).toInt();

            QSqlQuery skinQuery(db);
            skinQuery.prepare("SELECT skin_id FROM user_skins WHERE user_id = :id");
            skinQuery.bindValue(":id", userId);
            QStringList ownedSkins;
            if (skinQuery.exec())
            {
                while (skinQuery.next())
                    ownedSkins << skinQuery.value(0).toString();
            }

            QSqlQuery bgQuery(db);
            bgQuery.prepare("SELECT bg_id FROM user_backgrounds WHERE user_id = :id");
            bgQuery.bindValue(":id", userId);
            QStringList ownedBgs;
            if (bgQuery.exec())
            {
                while (bgQuery.next())
                    ownedBgs << bgQuery.value(0).toString();
            }

            return QString("shop_data|%1|%2|%3|%4|%5")
                .arg(coins).arg(skin).arg(bg)
                .arg(ownedSkins.join(","))
                .arg(ownedBgs.join(","));
        }
        return "error";
    }

    /**
     * @brief Покупает предмет магазина для пользователя.
     *
     * Метод проверяет тип предмета, цену и баланс пользователя. После покупки
     * списывает монеты и добавляет предмет в таблицу владения.
     *
     * @param userId Идентификатор пользователя.
     * @param itemId Идентификатор предмета.
     * @param itemType Тип предмета: \c skin или \c bg.
     * @return \c true при успешной покупке; иначе \c false.
     */
    static bool buyItem(int userId, int itemId, QString itemType)
    {
        if (!db.isOpen()) return false;

        int price = 0;
        if (itemType == "skin")
        {
            if (itemId == 1) price = 100;
            else if (itemId == 2) price = 250;
            else return false;
        }
        else if (itemType == "bg")
        {
            if (itemId == 101) price = 50;
            else if (itemId == 102) price = 100;
            else return false;
        }
        else return false;

        QSqlQuery check(db);
        check.prepare("SELECT coins FROM users WHERE id = :id");
        check.bindValue(":id", userId);
        if (!check.exec() || !check.next()) return false;

        int coins = check.value(0).toInt();
        if (coins < price) return false;

        QSqlQuery update(db);
        update.prepare("UPDATE users SET coins = coins - :price WHERE id = :id");
        update.bindValue(":price", price);
        update.bindValue(":id", userId);
        if (!update.exec()) return false;

        QString table = (itemType == "skin") ? "user_skins" : "user_backgrounds";
        QString column = (itemType == "skin") ? "skin_id" : "bg_id";

        QSqlQuery insert(db);
        insert.prepare(QString("INSERT INTO %1 (user_id, %2) VALUES (:user_id, :item_id)")
                           .arg(table).arg(column));
        insert.bindValue(":user_id", userId);
        insert.bindValue(":item_id", itemId);

        return insert.exec();
    }

    /**
     * @brief Выбирает купленный предмет как активный.
     * @param userId Идентификатор пользователя.
     * @param itemId Идентификатор предмета.
     * @param itemType Тип предмета: \c skin или \c bg.
     * @return \c true, если предмет принадлежит пользователю и был выбран; иначе \c false.
     */
    static bool equipItem(int userId, int itemId, QString itemType)
    {
        if (!db.isOpen()) return false;

        QString table = (itemType == "skin") ? "user_skins" : "user_backgrounds";
        QString column = (itemType == "skin") ? "skin_id" : "bg_id";

        QSqlQuery check(db);
        check.prepare(QString("SELECT id FROM %1 WHERE user_id = :user_id AND %2 = :item_id")
                          .arg(table).arg(column));
        check.bindValue(":user_id", userId);
        check.bindValue(":item_id", itemId);

        if (!check.exec() || !check.next()) return false;

        QString userColumn = (itemType == "skin") ? "skin" : "background";
        QSqlQuery update(db);
        update.prepare(QString("UPDATE users SET %1 = :item_id WHERE id = :id").arg(userColumn));
        update.bindValue(":item_id", itemId);
        update.bindValue(":id", userId);

        return update.exec();
    }

    /**
     * @brief Формирует таблицу лидеров по очкам.
     *
     * Возвращает до десяти пользователей, отсортированных по убыванию очков.
     * Формат ответа: \c leaderboard|place:name:score:level...
     *
     * @return Строка с таблицей лидеров или \c error при недоступной базе данных.
     */
    static QString getLeaderboard()
    {
        if (!db.isOpen()) return "error";

        QSqlQuery query(db);
        query.prepare(
            "SELECT COALESCE(NULLIF(display_name, ''), login), score, level "
            "FROM users "
            "ORDER BY score DESC "
            "LIMIT 10"
            );

        QString result = "leaderboard";

        if (query.exec())
        {
            int place = 1;

            while (query.next())
            {
                QString login = query.value(0).toString();
                int score = query.value(1).toInt();
                int level = query.value(2).toInt();

                result += QString("|%1:%2:%3:%4")
                              .arg(place)
                              .arg(login)
                              .arg(score)
                              .arg(level);

                place++;
            }
        }

        return result;
    }

    /**
     * @brief Возвращает отображаемое имя пользователя.
     *
     * Если display_name пустой, возвращается логин. Если пользователь не найден,
     * возвращается строка \c Игрок.
     *
     * @param userId Идентификатор пользователя.
     * @return Отображаемое имя пользователя.
     */
    static QString getUserDisplayName(int userId)
    {
        if (!db.isOpen()) return "Игрок";

        QSqlQuery query(db);
        query.prepare("SELECT display_name, login FROM users WHERE id = :id");
        query.bindValue(":id", userId);

        if (query.exec() && query.next())
        {
            QString displayName = query.value(0).toString().trimmed();
            QString login = query.value(1).toString().trimmed();

            if (!displayName.isEmpty())
                return displayName;

            return login;
        }

        return "Игрок";
    }


    /// @}

    /** @name Административная панель */
    /// @{

    /**
     * @brief Возвращает роль пользователя.
     * @param login Логин пользователя.
     * @return Роль пользователя: обычно \c player или \c admin.
     */
    static QString getUserRole(const QString& login)
    {
        if (!db.isOpen()) return "player";

        QSqlQuery query(db);
        query.prepare("SELECT role FROM users WHERE login = :login");
        query.bindValue(":login", login.trimmed());

        if (query.exec() && query.next())
            return query.value(0).toString().trimmed();

        return "player";
    }

    /**
     * @brief Назначает пользователю роль администратора.
     * @param login Логин пользователя.
     * @return \c true при успешном обновлении; иначе \c false.
     */
    static bool makeAdmin(const QString& login)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET role = 'admin' WHERE login = :login");
        query.bindValue(":login", login.trimmed());

        return query.exec();
    }

    /**
     * @brief Возвращает список всех пользователей для административной панели.
     *
     * Формат ответа начинается с \c admin_users, далее данные пользователей передаются
     * через разделители \c | и \c :.
     *
     * @return Строка со списком пользователей или \c error при недоступной базе данных.
     */
    static QString getAllUsersForAdmin()
    {
        if (!db.isOpen()) return "error";

        QSqlQuery query(db);
        query.prepare(
            "SELECT id, login, COALESCE(display_name, ''), role, banned, score, coins, level, xp, skin, background "
            "FROM users "
            "ORDER BY id ASC"
        );

        QString result = "admin_users";

        if (query.exec())
        {
            while (query.next())
            {
                QString id = query.value(0).toString();
                QString login = query.value(1).toString();
                QString displayName = query.value(2).toString();
                QString role = query.value(3).toString();
                QString banned = query.value(4).toString();
                QString score = query.value(5).toString();
                QString coins = query.value(6).toString();
                QString level = query.value(7).toString();
                QString xp = query.value(8).toString();
                QString skin = query.value(9).toString();
                QString background = query.value(10).toString();

                if (displayName.trimmed().isEmpty())
                    displayName = login;

                QStringList values;
                values << id << login << displayName << role << banned
                       << score << coins << level << xp << skin << background;

                for (QString& value : values)
                {
                    value.remove(QChar(1));
                    value.replace("|", " ");
                    value.replace(":", " ");
                }

                result += "|" + values.join(":");
            }
        }
        else
        {
            qDebug() << "Admin users query error:" << query.lastError().text();
        }

        return result;
    }

    /**
     * @brief Возвращает общую статистику всей игры для панели администратора.
     *
     * Метод собирает количество пользователей, активных и заблокированных игроков,
     * число администраторов, общий и лучший счёт, монеты, средний уровень,
     * открытые достижения, купленные скины и фоны.
     *
     * @return Строка формата admin_stats|key:value|key:value или error.
     */
    static QString getAdminGameStats()
    {
        if (!db.isOpen())
            return "error";

        auto scalarInt = [](const QString& sql) -> int
        {
            QSqlQuery query(DataBase::db);

            if (query.exec(sql) && query.next())
                return query.value(0).toInt();

            qDebug() << "Stats int query error:" << query.lastError().text();
            return 0;
        };

        auto scalarDouble = [](const QString& sql) -> double
        {
            QSqlQuery query(DataBase::db);

            if (query.exec(sql) && query.next())
                return query.value(0).toDouble();

            qDebug() << "Stats double query error:" << query.lastError().text();
            return 0.0;
        };

        return QString(
            "admin_stats|total_users:%1|active_users:%2|banned_users:%3|admins:%4|"
            "total_score:%5|best_score:%6|total_coins:%7|avg_level:%8|"
            "unlocked_achievements:%9|bought_skins:%10|bought_backgrounds:%11"
        )
            .arg(scalarInt("SELECT COUNT(*) FROM users"))
            .arg(scalarInt("SELECT COUNT(*) FROM users WHERE banned = 0"))
            .arg(scalarInt("SELECT COUNT(*) FROM users WHERE banned = 1"))
            .arg(scalarInt("SELECT COUNT(*) FROM users WHERE role = 'admin'"))
            .arg(scalarInt("SELECT COALESCE(SUM(score), 0) FROM users"))
            .arg(scalarInt("SELECT COALESCE(MAX(score), 0) FROM users"))
            .arg(scalarInt("SELECT COALESCE(SUM(coins), 0) FROM users"))
            .arg(scalarDouble("SELECT COALESCE(AVG(level), 0) FROM users"), 0, 'f', 2)
            .arg(scalarInt("SELECT COUNT(*) FROM achievements WHERE unlocked = 1"))
            .arg(scalarInt("SELECT COUNT(*) FROM user_skins"))
            .arg(scalarInt("SELECT COUNT(*) FROM user_backgrounds"));
    }

    /**
     * @brief Изменяет роль пользователя.
     * @param login Логин пользователя.
     * @param role Новая роль. Допустимые значения: \c admin и \c player.
     * @return \c true при успешном обновлении; иначе \c false.
     */
    static bool setUserRole(const QString& login, const QString& role)
    {
        if (!db.isOpen()) return false;

        if (role != "admin" && role != "player") return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET role = :role WHERE login = :login");
        query.bindValue(":role", role);
        query.bindValue(":login", login.trimmed());

        return query.exec();
    }

    /**
 * @brief Изменяет пароль пользователя.
 *
 * Используется администратором для смены пароля выбранного пользователя.
 *
 * @param login Логин пользователя.
 * @param password Новый пароль пользователя.
 * @return true, если пароль успешно изменён, иначе false.
 */
    static bool setUserPassword(const QString& login, const QString& password)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET password = :password WHERE login = :login");
        query.bindValue(":login", login.trimmed());
        query.bindValue(":password", password.trimmed());

        return query.exec();
    }

    /**
     * @brief Проверяет, заблокирован ли пользователь.
     * @param login Логин пользователя.
     * @return \c true, если пользователь заблокирован; иначе \c false.
     */
    static bool isUserBanned(const QString& login)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("SELECT banned FROM users WHERE login = :login");
        query.bindValue(":login", login.trimmed());

        if (query.exec() && query.next())
            return query.value(0).toInt() == 1;

        return false;
    }

    /**
     * @brief Блокирует пользователя.
     * @param login Логин пользователя.
     * @return \c true при успешной блокировке; иначе \c false.
     */
    static bool banUser(const QString& login)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET banned = 1 WHERE login = :login");
        query.bindValue(":login", login.trimmed());

        return query.exec();
    }

    /**
     * @brief Снимает блокировку с пользователя.
     * @param login Логин пользователя.
     * @return \c true при успешной разблокировке; иначе \c false.
     */
    static bool unbanUser(const QString& login)
    {
        if (!db.isOpen()) return false;

        QSqlQuery query(db);
        query.prepare("UPDATE users SET banned = 0 WHERE login = :login");
        query.bindValue(":login", login.trimmed());

        return query.exec();
    }

    /// @}

private:

    /**
     * @brief Общее соединение с базой данных, используемое всеми статическими методами.
     */
    static QSqlDatabase db;
};

#endif // DATABASE_H
