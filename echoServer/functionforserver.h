/**
 * @file functionforserver.h
 * @brief Объявления функций обработки текстовых команд клиента.
 *
 * Сервер принимает команды от клиента в строковом формате, разбирает их
 * и возвращает ответ в виде QByteArray.
 */
#ifndef FUNCTIONFORSERVER_H
#define FUNCTIONFORSERVER_H

#include <QByteArray>
#include <QString>
#include <QStringList>

/**
 * @brief Разбирает входящую команду клиента и вызывает нужную серверную операцию.
 *
 * Входная строка содержит имя команды и параметры, разделённые символом \c &.
 * Например: \c auth&login&password.
 *
 * @param data_from_client Исходная строка, полученная от клиента.
 * @param socketId Дескриптор сокета клиента, используется в ответе авторизации.
 * @return Ответ сервера в формате QByteArray.
 */
QByteArray parsing(const QString& data_from_client, qintptr socketId);

/**
 * @brief Выполняет авторизацию пользователя.
 * @param log Логин пользователя.
 * @param pass Пароль пользователя.
 * @param socketId Дескриптор клиентского сокета.
 * @return Строковый ответ об успешной или неуспешной авторизации.
 */
QByteArray auth(const QString& log, const QString& pass, qintptr socketId);
/**
 * @brief Регистрирует нового пользователя.
 * @param log Логин пользователя.
 * @param pass Пароль пользователя.
 * @param displayName Отображаемое имя игрока.
 * @return Строковый ответ о результате регистрации.
 */
QByteArray reg(const QString& log, const QString& pass, const QString& displayName);

/**
 * @brief Удаляет пользователя из списка онлайн по дескриптору отключённого сокета.
 *
 * Вызывается TCP-сервером при отключении клиента.
 *
 * @param socketId Дескриптор сокета, который отключился.
 */
void removeOnlineUser(qintptr socketId);

#endif // FUNCTIONFORSERVER_H
