#include <QApplication>
#include <QWidget>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QMessageBox>
#include <QTcpSocket>
#include <QProcess>
#include <QFile>
#include <QTextStream>

class AuthWindow : public QWidget
{
    Q_OBJECT

public:
    AuthWindow(QWidget *parent = nullptr) : QWidget(parent)
    {
        setWindowTitle("Единобожик - Авторизация");
        setFixedSize(400, 350);
        setStyleSheet("background-color: #ffe4ec;");

        // Создаем виджеты
        QLabel *titleLabel = new QLabel("Единобожик");
        titleLabel->setStyleSheet("font-size: 28px; font-weight: bold; color: #ff69b4;");
        titleLabel->setAlignment(Qt::AlignCenter);

        QLabel *loginLabel = new QLabel("Логин:");
        loginLabel->setStyleSheet("font-size: 16px; color: #d44c7a;");
        loginEdit = new QLineEdit;
        loginEdit->setStyleSheet("padding: 8px; border: 2px solid #ff69b4; border-radius: 10px;");
        loginEdit->setPlaceholderText("Введите логин");

        QLabel *passwordLabel = new QLabel("Пароль:");
        passwordLabel->setStyleSheet("font-size: 16px; color: #d44c7a;");
        passwordEdit = new QLineEdit;
        passwordEdit->setStyleSheet("padding: 8px; border: 2px solid #ff69b4; border-radius: 10px;");
        passwordEdit->setEchoMode(QLineEdit::Password);
        passwordEdit->setPlaceholderText("Введите пароль");

        QPushButton *loginButton = new QPushButton("Вход");
        loginButton->setStyleSheet("background-color: #ff69b4; color: white; padding: 10px; border-radius: 15px; font-size: 16px;");
        loginButton->setCursor(Qt::PointingHandCursor);

        QPushButton *registerButton = new QPushButton("Регистрация");
        registerButton->setStyleSheet("background-color: #ff85b8; color: white; padding: 10px; border-radius: 15px; font-size: 16px;");
        registerButton->setCursor(Qt::PointingHandCursor);

        // Layout
        QVBoxLayout *mainLayout = new QVBoxLayout(this);
        mainLayout->addSpacing(20);
        mainLayout->addWidget(titleLabel);
        mainLayout->addSpacing(20);
        mainLayout->addWidget(loginLabel);
        mainLayout->addWidget(loginEdit);
        mainLayout->addWidget(passwordLabel);
        mainLayout->addWidget(passwordEdit);
        mainLayout->addSpacing(20);

        QHBoxLayout *buttonLayout = new QHBoxLayout;
        buttonLayout->addWidget(loginButton);
        buttonLayout->addWidget(registerButton);
        mainLayout->addLayout(buttonLayout);
        mainLayout->addSpacing(20);

        // Подключаем сигналы
        connect(loginButton, &QPushButton::clicked, this, &AuthWindow::onLoginClicked);
        connect(registerButton, &QPushButton::clicked, this, &AuthWindow::onRegisterClicked);

        socket = new QTcpSocket(this);
    }

private slots:
    void onLoginClicked()
    {
        QString login = loginEdit->text().trimmed();
        QString password = passwordEdit->text().trimmed();

        if (login.isEmpty() || password.isEmpty()) {
            QMessageBox::warning(this, "Ошибка", "Введите логин и пароль!");
            return;
        }

        // Отправляем запрос на сервер
        socket->connectToHost("127.0.0.1", 33333);
        
        if (!socket->waitForConnected(3000)) {
            QMessageBox::critical(this, "Ошибка", "Не удалось подключиться к серверу!");
            return;
        }

        QString command = QString("login %1 %2\n").arg(login).arg(password);
        socket->write(command.toUtf8());
        
        if (!socket->waitForReadyRead(3000)) {
            QMessageBox::critical(this, "Ошибка", "Нет ответа от сервера!");
            socket->close();
            return;
        }

        QByteArray response = socket->readLine().trimmed();
        socket->close();

        QString responseStr = QString::fromUtf8(response);
        
        if (responseStr.startsWith("Login successful")) {
            // Сохраняем данные в файл
            QFile file("game_data.txt");
            if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
                QTextStream out(&file);
                out << login << "\n";
                out << responseStr << "\n";
                file.close();
            }
            
            // Запускаем Python игру
            QProcess::startDetached("python", QStringList() << "alien_invasion.py");
            
            // Закрываем окно авторизации
            QApplication::quit();
        } else {
            QMessageBox::warning(this, "Ошибка", "Неверный логин или пароль!");
        }
    }

    void onRegisterClicked()
    {
        QString login = loginEdit->text().trimmed();
        QString password = passwordEdit->text().trimmed();

        if (login.isEmpty() || password.isEmpty()) {
            QMessageBox::warning(this, "Ошибка", "Введите логин и пароль!");
            return;
        }

        if (password.length() < 3) {
            QMessageBox::warning(this, "Ошибка", "Пароль должен быть не менее 3 символов!");
            return;
        }

        socket->connectToHost("127.0.0.1", 33333);
        
        if (!socket->waitForConnected(3000)) {
            QMessageBox::critical(this, "Ошибка", "Не удалось подключиться к серверу!");
            return;
        }

        QString command = QString("register %1 %2\n").arg(login).arg(password);
        socket->write(command.toUtf8());
        
        if (!socket->waitForReadyRead(3000)) {
            QMessageBox::critical(this, "Ошибка", "Нет ответа от сервера!");
            socket->close();
            return;
        }

        QByteArray response = socket->readLine().trimmed();
        socket->close();

        if (response.contains("successful")) {
            QMessageBox::information(this, "Успех", "Регистрация прошла успешно! Теперь войдите.");
        } else {
            QMessageBox::warning(this, "Ошибка", "Пользователь с таким логином уже существует!");
        }
    }

private:
    QLineEdit *loginEdit;
    QLineEdit *passwordEdit;
    QTcpSocket *socket;
};

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    AuthWindow window;
    window.show();
    return app.exec();
}