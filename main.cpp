//Первые две строчки подключают сам класс mytcpserver и ядро приложения QT
#include <QCoreApplication> 
#include "mytcpserver.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv); //создает терминал, в котором будет все отображатьсяя
    MyTcpServer myserv; //объявляем переменную
    return a.exec(); //запускаем наше консольное приложение для исполнения
}
