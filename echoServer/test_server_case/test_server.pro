QT += testlib sql network
QT -= gui

CONFIG += qt console warn_on depend_includepath testcase c++17
CONFIG -= app_bundle

TEMPLATE = app
TARGET = test_server

SOURCES += \
    tst_database_test.cpp \
    ../dataBase.cpp \
    ../functionforserver.cpp

HEADERS += \
    ../dataBase.h \
    ../functionforserver.h
