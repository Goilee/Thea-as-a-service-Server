# Theia application server

Этот проект предназначен для запуска сред разработки, основанных на [Theia](https://theia-ide.org/), как application-as-a-service. В теории, должно работать с произвольным приложем, упакованным в докер-контейнер, и публикующим единственный порт.

Принцип работы состоит в том, что на каждое входящее соединение создаётся и запускается новый контейнер, а клиент перенаправляется на него. Фоновый процесс регулярно проверяет логи контейнеров, и если видит, что клиент покинул контейнер (закрыл вкладку), то контейнер останавливается.

Клиентам предоставится страница их проектов, каждый проект представляет собой докер контейнер. Клиенты могут создавать, удалять и запускать проекты (контейнеры), а также делиться ссылкой на конетйнер с другими пользователями.

# Необходимое ПО

- Python 3
- [Docker](https://docs.docker.com/engine/install/)

Необходимые модули Python можно установить с помощью утилиты pip из корневой директории проекта:

    sudo apt install pip
    pip install -r requirements.txt

Однако, отдельно нужно установить:

   sudo pip install apscheduler
   sudo pip install flask

# Настройка Google

В интерфейсе есть элементы авторизации Google. Для их работы необходимо настроить проект в [console.cloud.google.com](console.cloud.google.com).

1. Создаём проект, имя и прочие параметры настраиваем по желанию.
2. В меню навигации (левый край экрана) заходим в APIs & Services --> Credentials.
3. Нажимаем вверху на CREATE CREDENTIALS --> OAuth CLient ID. Нажимаем CONFIGURE CONSENT SCREEN.
4. Указываем User Type = External. Нажимаем Create.
5. Настраиваем поля на усмотрение. Нажимаем SAVE AND CONTINUE.
6. На экранах Scopes и Test users можно ничего не настраивать, сразу нажав на SAVE AND CONTINUE.
7. Нажимаем BACK TO DASHBOARD. Возвращаемся на страницу Credentials и нажимаем CREATE CREDENTIALS -> OAuth Client ID.
8. Указываем Application type = Web application.
9. Добавляем в Authorized redirect URIs адрес "http://\<host\>/callback", заменив \<host\> на адрес своего хоста.
10. Скачиваем сгенерированные данные в формате JSON. Добавляем в корневую директорию под названием, указанным в config.ini (по умолчанию client_secret.json).

# Настройка параметров сервера

Файл [config.ini](https://github.com/Goilee/RIDE-server/blob/4a31a5c23972b775c0237a7334b9b3bdfded33a8/config.ini) содержит все настраиваемые параметры сервера.

# Запуск

Сервер запускается командой

    sudo python3 run_project.py [--debug]
    
Опция --debug запускает сервер в отладочном режиме. Рекомендуется использоваться при тестировании, но не в релизе, поскольку с этой опцией в случае необработанного исключения клиенты увидят его подробности.
