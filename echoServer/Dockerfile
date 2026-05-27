FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    qt5-qmake \
    qtbase5-dev \
    g++ \
    make \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p /app/data

COPY . .

RUN qmake echoServer.pro
RUN make

EXPOSE 33333

CMD ["./echoServer"]