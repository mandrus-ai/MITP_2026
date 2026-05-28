QT += testlib sql network
QT -= gui

CONFIG += qt console warn_on depend_includepath testcase
CONFIG -= app_bundle

TEMPLATE = app
TARGET = test_gamedatabase

SOURCES += \
    tst_gamedatabase_test.cpp \
    ../databasemanager.cpp

HEADERS += \
    ../databasemanager.h
