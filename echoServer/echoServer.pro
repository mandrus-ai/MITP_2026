QT += core network sql

CONFIG += c++17 console

CONFIG -= app_bundle

TEMPLATE = app

SOURCES += \
    main.cpp \
    mytcpserver.cpp \
    functionforserver.cpp \
    dataBase.cpp

HEADERS += \
    mytcpserver.h \
    functionforserver.h \
    dataBase.h