# Загружаем переменные из .env
ifneq (,$(wildcard ./.env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

DC = docker compose
RUN_VENV = poetry run
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP_FILE = docker/app.yaml
STORAGES_FILE = docker/storages.yaml
APP_CONTAINER = ${DOCKER_CONFIG__APP_CONTAINER}
STORAGE_CONTAINER = ${DOCKER_CONFIG__STORAGE_CONTAINER}
PROJECT_NAME = ${DOCKER_CONFIG__PROJECT_NAME}


.PHONY: app
app:
	${DC} -p ${PROJECT_NAME} -f ${APP_FILE} ${ENV} up --build -d
	${MAKE} app-logs

app-down:
	${DC} -p ${PROJECT_NAME} -f ${APP_FILE} ${ENV} down

app-shell:
	${EXEC} ${APP_CONTAINER} bash

app-logs:
	${LOGS} ${APP_CONTAINER} -f

app-restart:
	git pull
	${DC} -p ${PROJECT_NAME} -f ${APP_FILE} ${ENV} down
	${DC} -p ${PROJECT_NAME} -f ${APP_FILE} ${ENV} up --build -d
	${LOGS} ${APP_CONTAINER} -f


.PHONY: storages
storages:
	${DC} -p ${PROJECT_NAME} -f ${STORAGES_FILE} ${ENV} up --build -d

storages-down:
	${DC} -p ${PROJECT_NAME} -f ${STORAGES_FILE} ${ENV} down

.PHONY: main
main:
	cd app && ${RUN_VENV} python main.py
