QT -= gui

QT += core network sql #Для работы с сетью



CONFIG += c++11 console
CONFIG -= app_bundle


DEFINES += QT_DEPRECATED_WARNINGS


SOURCES += \
    main.cpp \
    mytcpserver.cpp \
    databasemanager.cpp


qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

HEADERS += \
    mytcpserver.h \
    databasemanager.h
