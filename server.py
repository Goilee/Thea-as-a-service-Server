from argparse import ArgumentParser
from subprocess import Popen, PIPE
from flask import Flask, Blueprint, render_template
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from os import _exit


parser = ArgumentParser(description='Docker application server.')
parser.add_argument('-a', '--address', dest='HOST', help='host ip address', default='localhost')
parser.add_argument('-p', '--port', dest='PORT', help='port to listen', type=int, default=3000)
parser.add_argument('-d', '--debug', dest='DEBUG', help='run in debug mode', action='store_const', const=True, default=False)
args = parser.parse_args()


# запускает команду в shell и возвращает вывод
def run_cmd(cmd):
    process = Popen(cmd, stdout=PIPE, shell=True)
    return process.communicate()[0].decode('utf-8')


# запускает контейнер на случайном порту и возвращает кортеж (ip, port)
def run_container():
    host = args.HOST
    result = run_cmd(f'sh runContainer.sh {host}').splitlines()
    port = result[0]
    container = result[1]
    print(f'Started container (id={container}) on ({host},{port})')
    return (host, port)


# удаляет контейнер и возвращает вывод команды
def force_remove_container(container):
    result = run_cmd(f'sh removeContainer.sh {container}')[:-1]
    print(f'Force removed: {result}')
    return result


# возвращает номер последней строки, содержащей подстроку line (-1 при отсутствии)
def find_last_line_in_logs(container, substr):
    result = run_cmd(f'''docker logs {container} 2>&1 | grep -n "{substr}" | tail --lines=1''')
    try:
        lineNumber = int(result[0:result.index(':')])
        return lineNumber
    except ValueError:
        return -1


# возвращает список айднишников запущенных контейнеров
def get_running_containers():
    with open('image') as f:
        image = f.read()
    result = run_cmd(f'docker ps -q --filter "ancestor={image}"')
    return result.splitlines()


# удаляет запущенные контейнеры, из которых вышел юзер (или все, если параметр True)
def clean_containers(cleanAll = False):
    for container in get_running_containers():
        clientEnter = find_last_line_in_logs(container, "Set client")
        clientExit = find_last_line_in_logs(container, "All contributions have been stopped")
        print (f'Container {container}: entered {clientEnter}, exited {clientExit}')
        if clientExit > clientEnter or cleanAll:
            force_remove_container(container)


main = Blueprint('main', __name__)

@main.route('/')
def index():
    (host, port) = run_container()
    return render_template('loader.html'), { "Refresh": f"10; url=http://{host}:{port}" }


INTERVAL_IN_SECONDS = 300
scheduler = BlockingScheduler()
scheduler.add_job(clean_containers, 'interval', seconds=INTERVAL_IN_SECONDS)
cleaner_thread = Thread(target=scheduler.start, args=())
cleaner_thread.start()

try:
    app = Flask(__name__)
    app.register_blueprint(main)
    app.run(host = args.HOST, port = args.PORT, debug = args.DEBUG)
finally:
    print('Clean all containers...')
    clean_containers(True)
    _exit(0)

