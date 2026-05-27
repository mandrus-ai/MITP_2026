QT += core gui network widgets

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++11

SOURCES += \
    main.cpp \
    authwindow.cpp \
    singletonclient.cpp \
    adminwindow.cpp

HEADERS += \
    authwindow.h \
    singletonclient.h \
    adminwindow.h



