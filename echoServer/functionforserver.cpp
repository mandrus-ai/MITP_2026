/**
 * @file functionforserver.cpp
 * @brief Реализация обработки команд клиента и функций авторизации/регистрации.
 */
#include "functionforserver.h"
#include "dataBase.h"
#include <QDebug>
#include <QMap>

/**
 * @brief Логин последнего успешно авторизованного пользователя.
 */
static QString currentUser;

/**
 * @brief Идентификатор последнего успешно авторизованного пользователя.
 */
static int currentUserId = -1;

/**
 * @brief Список пользователей, которые сейчас находятся онлайн.
 *
 * Ключ — дескриптор сокета клиента, значение — логин пользователя.
 */
static QMap<qintptr, QString> onlineUsers;

/**
 * @brief Удаляет отключившегося пользователя из списка онлайн.
 *
 * @param socketId Дескриптор сокета отключённого клиента.
 */
void removeOnlineUser(qintptr socketId)
{
    onlineUsers.remove(socketId);
}


/**
 * @brief Обрабатывает строковую команду клиента.
 *
 * Функция очищает входные данные, извлекает имя команды и параметры,
 * затем вызывает методы DataBase или вспомогательные функции auth()/reg().
 *
 * @param data_from_client Команда от клиента.
 * @param socketId Дескриптор сокета клиента.
 * @return Ответ сервера в виде QByteArray.
 */
QByteArray parsing(const QString& data_from_client, qintptr socketId)
{
    qDebug() << "=== PARSING FUNCTION CALLED ===";

    QString cleanData = data_from_client;
    cleanData.remove(QChar(1));
    cleanData = cleanData.trimmed();

    qDebug() << "Input data:" << cleanData;
    qDebug() << "HEX:" << cleanData.toUtf8().toHex();

    QStringList data_from_client_list = cleanData.split('&');

    if (data_from_client_list.isEmpty())
    {
        qDebug() << "Empty request!";
        return "error&empty_request";
    }

    QString nameofFunc = data_from_client_list.first().trimmed();
    data_from_client_list.removeFirst();

    qDebug() << "Function:" << nameofFunc;
    qDebug() << "Params:" << data_from_client_list;

    if (nameofFunc == "auth")
    {
        if (data_from_client_list.size() < 2)
        {
            return "error&auth_params";
        }

        QString login = data_from_client_list.at(0).trimmed();
        QString password = data_from_client_list.at(1).trimmed();

        if (DataBase::authenticateUser(login, password))
        {
            currentUser = login;
            currentUserId = DataBase::getUserId(login);
            onlineUsers[socketId] = login;
        }

        return auth(login, password, socketId);
    }
    else if (nameofFunc == "reg")
    {
        if (data_from_client_list.size() < 3)
        {
            return "error&reg_params";
        }

        QString login = data_from_client_list.at(0).trimmed();
        QString password = data_from_client_list.at(1).trimmed();
        QString displayName = data_from_client_list.at(2).trimmed();

        return reg(login, password, displayName);
    }
    else if (nameofFunc == "update_score")
    {
        if (data_from_client_list.size() < 2)
            return "error&missing_params";

        int userId = data_from_client_list.at(0).toInt();
        int newScore = data_from_client_list.at(1).toInt();

        if (DataBase::updateUserScore(userId, newScore))
            return "success";
        return "error";
    }
    else if (nameofFunc == "add_coins")
    {
        if (data_from_client_list.size() < 2)
            return "error&missing_params";

        int userId = data_from_client_list.at(0).toInt();
        int amount = data_from_client_list.at(1).toInt();

        if (DataBase::addUserCoins(userId, amount))
            return "success";
        return "error";
    }
    else if (nameofFunc == "update_coins")
    {
        if (data_from_client_list.size() < 2)
            return "error&missing_params";

        int userId = data_from_client_list.at(0).toInt();
        int newCoins = data_from_client_list.at(1).toInt();

        if (DataBase::updateUserCoins(userId, newCoins))
            return "success";
        return "error";
    }
    else if (nameofFunc == "update_level")
    {
        if (data_from_client_list.size() < 3)
            return "error&missing_params";

        int userId = data_from_client_list.at(0).toInt();
        int level = data_from_client_list.at(1).toInt();
        int xp = data_from_client_list.at(2).toInt();

        if (DataBase::updateUserLevel(userId, level, xp))
            return "success";
        return "error";
    }
    else if (nameofFunc == "save_all")
    {
        if (data_from_client_list.size() < 5)
            return "error&missing_params";

        int userId = data_from_client_list.at(0).toInt();
        int score = data_from_client_list.at(1).toInt();
        int coins = data_from_client_list.at(2).toInt();
        int level = data_from_client_list.at(3).toInt();
        int xp = data_from_client_list.at(4).toInt();

        if (DataBase::savePlayerData(userId, score, coins, level, xp))
            return "success";
        return "error";
    }
    else if (nameofFunc == "get_achievements")
    {
        if (data_from_client_list.size() < 1)
            return "error&missing_user_id";

        int userId = data_from_client_list.at(0).toInt();
        QString result = DataBase::getUserAchievements(userId);
        return result.toUtf8();
    }
    else if (nameofFunc == "update_achievement")
    {
        if (data_from_client_list.size() < 4)
            return "error&missing_params";

        int userId = data_from_client_list.at(0).toInt();
        int achId = data_from_client_list.at(1).toInt();
        int progress = data_from_client_list.at(2).toInt();
        bool unlocked = data_from_client_list.at(3).toInt() == 1;

        if (DataBase::updateAchievementProgress(userId, achId, progress, unlocked))
            return "success";
        return "error";
    }
    else if (nameofFunc == "get_shop_data")
    {
        if (data_from_client_list.size() < 1)
            return "error&missing_user_id";

        int userId = data_from_client_list.at(0).toInt();
        return DataBase::getShopData(userId).toUtf8();
    }
    else if (nameofFunc == "get_leaderboard")
    {
        return DataBase::getLeaderboard().toUtf8();
    }
    else if (nameofFunc == "get_admin_users")
    {
        if (data_from_client_list.size() < 1)
            return "error&missing_login";

        QString login = data_from_client_list.at(0).trimmed();

        if (DataBase::getUserRole(login) != "admin")
            return "error&access_denied";

        return DataBase::getAllUsersForAdmin().toUtf8();
    }
    /**
     * @brief Обрабатывает запрос администратора на получение общей статистики игры.
     */
    else if (nameofFunc == "get_admin_stats")
    {
        if (data_from_client_list.size() < 1)
            return "error&missing_login";

        QString login = data_from_client_list.at(0).trimmed();

        if (DataBase::getUserRole(login) != "admin")
            return "error&access_denied";

        return DataBase::getAdminGameStats().toUtf8();
    }
    /*
 * @brief Возвращает список пользователей, которые сейчас онлайн.
 *
 * Команда используется админ-панелью для отображения текущих
 * подключённых пользователей.
 *
 * @return Ответ формата online_users|login1|login2.
 */
    else if (nameofFunc == "get_online_users")
    {
        QStringList users = onlineUsers.values();
        users.removeDuplicates();
        users.sort();

        QString result = "online_users";

        for (const QString& user : users)
            result += "|" + user;

        return result.toUtf8();
    }

    else if (nameofFunc == "set_user_role")
    {
        if (data_from_client_list.size() < 3)
            return "error&missing_params";

        QString adminLogin = data_from_client_list.at(0).trimmed();
        QString targetLogin = data_from_client_list.at(1).trimmed();
        QString role = data_from_client_list.at(2).trimmed();

        if (DataBase::getUserRole(adminLogin) != "admin")
            return "error&access_denied";

        if (DataBase::setUserRole(targetLogin, role))
            return "success";

        return "error";
    }
    else if (nameofFunc == "ban_user")
    {
        if (data_from_client_list.size() < 2)
            return "error&missing_params";

        QString adminLogin = data_from_client_list.at(0).trimmed();
        QString targetLogin = data_from_client_list.at(1).trimmed();

        if (DataBase::getUserRole(adminLogin) != "admin")
            return "error&access_denied";

        if (DataBase::banUser(targetLogin))
            return "ban_success";

        return "ban_failed";
    }

    else if (nameofFunc == "unban_user")
    {
        if (data_from_client_list.size() < 2)
            return "error&missing_params";

        QString adminLogin = data_from_client_list.at(0).trimmed();
        QString targetLogin = data_from_client_list.at(1).trimmed();

        if (DataBase::getUserRole(adminLogin) != "admin")
            return "error&access_denied";

        if (DataBase::unbanUser(targetLogin))
            return "unban_success";

        return "unban_failed";
    }

    else if (nameofFunc == "buy_item")
    {
        if (data_from_client_list.size() < 3)
            return "error&missing_params";

        int userId = data_from_client_list.at(0).toInt();
        int itemId = data_from_client_list.at(1).toInt();
        QString itemType = data_from_client_list.at(2);

        if (DataBase::buyItem(userId, itemId, itemType))
            return "success";
        return "error";
    }
    else if (nameofFunc == "equip_item")
    {
        if (data_from_client_list.size() < 3)
            return "error&missing_params";

        int userId = data_from_client_list.at(0).toInt();
        int itemId = data_from_client_list.at(1).toInt();
        QString itemType = data_from_client_list.at(2);

        if (DataBase::equipItem(userId, itemId, itemType))
            return "success";
        return "error";
    }
    else if (nameofFunc == "get_user_data")
    {
        if (data_from_client_list.size() < 1)
            return "error&missing_user_id";

        int userId = data_from_client_list.at(0).toInt();

        int score = DataBase::getUserScore(userId);
        int coins = DataBase::getUserCoins(userId);
        int level = DataBase::getUserLevel(userId);
        int skin = DataBase::getUserSkin(userId);
        int background = DataBase::getUserBackground(userId);
        int xp = DataBase::getUserXP(userId);
        QString displayName = DataBase::getUserDisplayName(userId);

        return QString("user_data|%1|%2|%3|%4|%5|%6|%7")
            .arg(score)
            .arg(coins)
            .arg(level)
            .arg(skin)
            .arg(background)
            .arg(xp)
            .arg(displayName)
            .toUtf8();
    }

    else if (nameofFunc == "set_user_password")
    {
        if (data_from_client_list.size() < 3)
            return "error&missing_params";

        QString adminLogin = data_from_client_list.at(0).trimmed();
        QString targetLogin = data_from_client_list.at(1).trimmed();
        QString newPassword = data_from_client_list.at(2).trimmed();

        if (DataBase::getUserRole(adminLogin) != "admin")
            return "error&access_denied";

        if (newPassword.isEmpty())
            return "password_failed";

        if (DataBase::setUserPassword(targetLogin, newPassword))
            return "password_success";

        return "password_failed";
    }

    return "error&unknown_function";
}

/**
 * @brief Проверяет данные пользователя и формирует ответ авторизации.
 *
 * При успешной авторизации возвращает данные профиля: отображаемое имя,
 * идентификатор пользователя, очки, монеты, уровень, выбранные предметы,
 * опыт, роль и дескриптор сокета.
 *
 * @param log Логин пользователя.
 * @param pass Пароль пользователя.
 * @param socketId Дескриптор клиентского сокета.
 * @return Ответ \c auth_success или \c auth_failed с причиной ошибки.
 */
QByteArray auth(const QString& log, const QString& pass, qintptr socketId)
{
    qDebug() << "AUTH:" << log << pass;

    if (DataBase::authenticateUser(log, pass))
    {
        if (DataBase::isUserBanned(log))
        {
            return  "auth_failed&user_banned";
        }

        qDebug() << "Auth success";

        int userId = DataBase::getUserId(log);
        int score = DataBase::getUserScore(userId);
        int coins = DataBase::getUserCoins(userId);
        int level = DataBase::getUserLevel(userId);
        int skin = DataBase::getUserSkin(userId);
        int background = DataBase::getUserBackground(userId);
        int xp = DataBase::getUserXP(userId);
        QString displayName = DataBase::getUserDisplayName(userId);
        QString role = DataBase::getUserRole(log);

        return QString("auth_success&%1|%2|%3|%4|%5|%6|%7|%8|%9|%10")
            .arg(displayName)
            .arg(userId)
            .arg(score)
            .arg(coins)
            .arg(level)
            .arg(skin)
            .arg(background)
            .arg(xp)
            .arg(role)
            .arg(socketId)
            .toUtf8();
    }

    qDebug() << "Auth failed";
    return "auth_failed&invalid_login_or_password";

    qDebug() << "Auth failed";
    return "auth_failed&invalid_login_or_password";
}

/**
 * @brief Создаёт нового пользователя в базе данных.
 * @param log Логин пользователя.
 * @param pass Пароль пользователя.
 * @param displayName Отображаемое имя игрока.
 * @return Ответ \c reg_success или \c reg_failed с причиной ошибки.
 */
QByteArray reg(const QString& log, const QString& pass, const QString& displayName)
{
    qDebug() << "REG:" << log << pass << displayName;

    if (DataBase::userExists(log))
    {
        return "reg_failed&user_exists";
    }

    if (DataBase::registerUser(log, pass, displayName))
    {
        return QString("reg_success&%1").arg(log).toUtf8();
    }

    return "reg_failed&database_error";
}
