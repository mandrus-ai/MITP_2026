/**
 * @file authwindow.cpp
 * @brief Реализация окна авторизации и регистрации пользователя.
 */

#include "authwindow.h"
#include "adminwindow.h"
#include <QVBoxLayout>
#include <QFormLayout>
#include <QMessageBox>
#include <QDebug>
#include <QProcess>
#include <QCoreApplication>
#include <QFileInfo>
#include <QTimer>
#include "singletonclient.h"
#include <QFile>


AuthWindow::AuthWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setupUI();
    applyPinkTheme();

    connect(SingletonClient::getInstance(), &SingletonClient::messageFromServer, this, &AuthWindow::onReadyRead);
    connect(SingletonClient::getInstance(), &SingletonClient::connected, this, &AuthWindow::onConnected);
    connect(SingletonClient::getInstance(), &SingletonClient::disconnected, this, &AuthWindow::onDisconnected);
    connect(SingletonClient::getInstance(), &SingletonClient::errorOccurred, this, &AuthWindow::onError);

    QString ip = "127.0.0.1";

    QFile file("server_config.txt");

    if (file.open(QIODevice::ReadOnly | QIODevice::Text))
    {
        ip = QString(file.readAll()).trimmed();
        file.close();
    }

    SingletonClient::getInstance()->connectToServer(ip, 33334);
}

AuthWindow::~AuthWindow() {}

void AuthWindow::applyPinkTheme()
{
    this->setStyleSheet(
        "QMainWindow {"
        "   background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
        "                               stop:0 #FFB6C1, stop:1 #FF69B4);"
        "}"

        "QLabel {"
        "   color: #8B0045;"
        "   font-weight: bold;"
        "   font-size: 12px;"
        "}"

        "QLineEdit {"
        "   background-color: #FFF0F5;"
        "   border: 2px solid #FF69B4;"
        "   border-radius: 8px;"
        "   padding: 6px;"
        "   color: #8B0045;"
        "   font-size: 11px;"
        "}"

        "QLineEdit:focus {"
        "   border: 2px solid #FF1493;"
        "   background-color: #FFFFFF;"
        "}"

        "QPushButton {"
        "   background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
        "                               stop:0 #FF69B4, stop:1 #FF1493);"
        "   color: white;"
        "   border: none;"
        "   border-radius: 10px;"
        "   padding: 8px 16px;"
        "   font-weight: bold;"
        "   font-size: 12px;"
        "   min-width: 120px;"
        "}"

        "QPushButton:hover {"
        "   background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
        "                               stop:0 #FF1493, stop:1 #C71585);"
        "}"

        "QPushButton:pressed {"
        "   background: #C71585;"
        "}"

        "QPushButton:disabled {"
        "   background: #DDA0DD;"
        "   color: #FFE4E1;"
        "}"

        "QTabWidget::pane {"
        "   background-color: #FFF0F5;"
        "   border: 2px solid #FF69B4;"
        "   border-radius: 10px;"
        "}"

        "QTabBar::tab {"
        "   background: #FFB6C1;"
        "   color: #8B0045;"
        "   padding: 8px 20px;"
        "   margin: 2px;"
        "   border-top-left-radius: 8px;"
        "   border-top-right-radius: 8px;"
        "   font-weight: bold;"
        "}"

        "QTabBar::tab:selected {"
        "   background: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
        "                               stop:0 #FF69B4, stop:1 #FF1493);"
        "   color: white;"
        "}"

        "QTabBar::tab:hover:!selected {"
        "   background: #FFC0CB;"
        "}"
        );
}

void AuthWindow::setupUI()
{
    setWindowTitle("Authorization");
    setMinimumSize(400, 380);
    setFixedSize(450, 420);

    QWidget* centralWidget = new QWidget(this);
    QVBoxLayout* mainLayout = new QVBoxLayout(centralWidget);
    mainLayout->setSpacing(15);
    mainLayout->setContentsMargins(20, 20, 20, 20);

    // Title
    QLabel* titleLabel = new QLabel("WELCOME");
    titleLabel->setAlignment(Qt::AlignCenter);
    titleLabel->setStyleSheet("font-size: 18px; font-weight: bold; color: #FF1493; margin: 10px;");
    mainLayout->addWidget(titleLabel);

    // Connection status
    connectionStatus = new QLabel("Connecting to server...");
    connectionStatus->setAlignment(Qt::AlignCenter);
    connectionStatus->setStyleSheet("color: #FF69B4; font-size: 11px;");
    mainLayout->addWidget(connectionStatus);

    // Tabs
    tabWidget = new QTabWidget();

    // === Login Tab ===
    QWidget* authTab = new QWidget();
    QVBoxLayout* authLayout = new QVBoxLayout(authTab);
    authLayout->setSpacing(15);

    QFormLayout* authForm = new QFormLayout();
    authForm->setSpacing(10);
    authForm->setLabelAlignment(Qt::AlignRight);

    QLabel* loginLabel = new QLabel("Username:");
    authLogin = new QLineEdit();
    authLogin->setPlaceholderText("Enter your username");

    QLabel* passLabel = new QLabel("Password:");
    authPass = new QLineEdit();
    authPass->setEchoMode(QLineEdit::Password);
    authPass->setPlaceholderText("Enter your password");

    authForm->addRow(loginLabel, authLogin);
    authForm->addRow(passLabel, authPass);
    authLayout->addLayout(authForm);

    authBtn = new QPushButton("LOGIN");
    authBtn->setCursor(Qt::PointingHandCursor);
    authLayout->addWidget(authBtn, 0, Qt::AlignCenter);

    authStatus = new QLabel();
    authStatus->setAlignment(Qt::AlignCenter);
    authStatus->setStyleSheet("color: #FF69B4; font-size: 11px;");
    authLayout->addWidget(authStatus);
    authLayout->addStretch();

    // === Register Tab ===
    QWidget* regTab = new QWidget();
    QVBoxLayout* regLayout = new QVBoxLayout(regTab);
    regLayout->setSpacing(15);

    QFormLayout* regForm = new QFormLayout();
    regForm->setSpacing(10);
    regForm->setLabelAlignment(Qt::AlignRight);

    QLabel* regNameLabel = new QLabel("Player Name:");
    regDisplayName = new QLineEdit();
    regDisplayName->setPlaceholderText("Your beautiful in-game name");

    QLabel* regLoginLabel = new QLabel("Login:");
    regLogin = new QLineEdit();
    regLogin->setPlaceholderText("Choose a login");

    QLabel* regPassLabel = new QLabel("Password:");
    regPass = new QLineEdit();
    regPass->setEchoMode(QLineEdit::Password);
    regPass->setPlaceholderText("Choose a password");

    QLabel* regConfirmLabel = new QLabel("Confirm Password:");
    regConfirmPass = new QLineEdit();
    regConfirmPass->setEchoMode(QLineEdit::Password);
    regConfirmPass->setPlaceholderText("Confirm your password");

    regForm->addRow(regNameLabel, regDisplayName);
    regForm->addRow(regLoginLabel, regLogin);
    regForm->addRow(regPassLabel, regPass);
    regForm->addRow(regConfirmLabel, regConfirmPass);
    regLayout->addLayout(regForm);

    regBtn = new QPushButton("REGISTER");
    regBtn->setCursor(Qt::PointingHandCursor);
    regLayout->addWidget(regBtn, 0, Qt::AlignCenter);

    regStatus = new QLabel();
    regStatus->setAlignment(Qt::AlignCenter);
    regStatus->setStyleSheet("color: #FF69B4; font-size: 11px;");
    regLayout->addWidget(regStatus);
    regLayout->addStretch();

    tabWidget->addTab(authTab, "Login");
    tabWidget->addTab(regTab, "Register");
    mainLayout->addWidget(tabWidget);

    setCentralWidget(centralWidget);

    connect(authBtn, &QPushButton::clicked, this, &AuthWindow::onAuth);
    connect(regBtn, &QPushButton::clicked, this, &AuthWindow::onReg);
}

void AuthWindow::sendToServer(const QString& data)
{
    SingletonClient::getInstance()->sendMessageToServer(data);
    qDebug() << "Sent:" << data;
}

void AuthWindow::onAuth()
{
    QString login = authLogin->text().trimmed();
    QString pass = authPass->text().trimmed();

    if(login.isEmpty() || pass.isEmpty()) {
        authStatus->setText("Please fill in all fields!");
        authStatus->setStyleSheet("color: red; font-size: 11px;");
        return;
    }

    authStatus->setText("Checking...");
    authStatus->setStyleSheet("color: orange; font-size: 11px;");
    authBtn->setEnabled(false);

    sendToServer(QString("auth&%1&%2").arg(login).arg(pass));
}

void AuthWindow::onReg()
{
    QString displayName = regDisplayName->text().trimmed();
    QString login = regLogin->text().trimmed();
    QString pass = regPass->text().trimmed();
    QString confirmPass = regConfirmPass->text().trimmed();

    if(displayName.isEmpty() || login.isEmpty() || pass.isEmpty() || confirmPass.isEmpty()) {
        regStatus->setText("Please fill in all fields!");
        regStatus->setStyleSheet("color: red; font-size: 11px;");
        return;
    }

    if(pass != confirmPass) {
        regStatus->setText("Passwords do not match!");
        regStatus->setStyleSheet("color: red; font-size: 11px;");
        return;
    }

    regStatus->setText("Registering...");
    regStatus->setStyleSheet("color: orange; font-size: 11px;");
    regBtn->setEnabled(false);

    sendToServer(
        QString("reg&%1&%2&%3")
            .arg(login)
            .arg(pass)
            .arg(displayName)
        );
}

void AuthWindow::onReadyRead(QString msg)
{
    msg.remove(QChar(1));
    msg = msg.trimmed();
    qDebug() << "Received:" << msg;

        if(msg.startsWith("auth_success"))
        {
            // Формат: auth_success&login|userId|score|coins|level|skin|background|xp
            QStringList parts = msg.split('&');
            if(parts.size() >= 2) {
                QStringList dataParts = parts[1].split('|');
                if(dataParts.size() >= 8) {
                    QString login = dataParts[0];
                    QString userId = dataParts[1];
                    QString score = dataParts[2];
                    QString coins = dataParts[3];
                    QString level = dataParts[4];
                    QString skin = dataParts[5];
                    QString background = dataParts[6];
                    QString xp = dataParts[7];
                    QString role = dataParts.size() > 8 ? dataParts[8] : "player";
                    QString socketId = dataParts.size() > 9 ? dataParts[9] : "";

                    authStatus->setText("Login successful!");
                    authStatus->setStyleSheet("color: green; font-size: 11px;");

                    QMessageBox::information(this, "Success", QString("Welcome, %1!\nYour stats:\nScore: %2\nCoins: %3\nLevel: %4")
                                                                  .arg(login).arg(score).arg(coins).arg(level));
                    authBtn->setEnabled(true);

                    if (role == "admin")
                    {
                        AdminWindow* adminWindow = new AdminWindow(authLogin->text().trimmed());
                        adminWindow->show();

                        QTimer::singleShot(300, this, [this]() {
                            this->close();
                        });

                        return;
                    }

                    // ЗАПУСК ИГРЫ с передачей всех данных
                    QString pythonPath = "python";
                    // ЗАПУСК ГОТОВОЙ ИГРЫ .EXE
                    QString gamePath =
                        QCoreApplication::applicationDirPath()
                        + "/AlienInvasion/game_launcher.exe";

                    QStringList args;
                    args << login;
                    args << "player";
                    args << userId;
                    args << score;
                    args << coins;
                    args << level;
                    args << skin;
                    args << background;
                    args << xp;
                    args << socketId;

                    qDebug() << "Starting game:" << gamePath;
                    qDebug() << "Starting game with args:" << args;

                    bool started = QProcess::startDetached(gamePath, args);

                    if (!started)
                    {
                        QMessageBox::critical(this, "Ошибка", "Не удалось запустить игру.");
                        authBtn->setEnabled(true);
                        return;
                    }

                    QTimer::singleShot(300, this, [this]() {
                        this->close();
                    });
                }
            }
        }
        else if(msg.startsWith("auth_failed"))
        {
            QString error = msg.split('&').value(1);
            authStatus->setText(error);
            authStatus->setStyleSheet("color: red; font-size: 11px;");
            authBtn->setEnabled(true);
        }
        else if(msg.startsWith("reg_success"))
        {
            QString login = msg.split('&').value(1);
            regStatus->setText("Registration successful!");
            regStatus->setStyleSheet("color: green; font-size: 11px;");
            QMessageBox::information(this, "Success", "Registration completed!\nYou can now login.");
            tabWidget->setCurrentIndex(0);
            authLogin->setText(login);
            regBtn->setEnabled(true);
        }
        else if(msg.startsWith("reg_failed"))
        {
            QString error = msg.split('&').value(1);
            regStatus->setText(error);
            regStatus->setStyleSheet("color: red; font-size: 11px;");
            regBtn->setEnabled(true);
        }
    }


void AuthWindow::onConnected()
{
    connectionStatus->setText("✓ Connected to server");
    connectionStatus->setStyleSheet("color: green; font-size: 11px;");
    qDebug() << "Connected to server!";
}

void AuthWindow::onDisconnected()
{
    connectionStatus->setText("✗ Disconnected from server");
    connectionStatus->setStyleSheet("color: red; font-size: 11px;");
    qDebug() << "Disconnected from server!";
}

void AuthWindow::onError(const QString& error)
{
    connectionStatus->setText("Error: " + error);
    connectionStatus->setStyleSheet("color: red; font-size: 11px;");
    qDebug() << "Socket error:" << error;
}
