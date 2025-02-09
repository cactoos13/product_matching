FROM ubuntu:latest
LABEL authors="treant"

ENTRYPOINT ["top", "-b"]