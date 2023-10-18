from flask import Flask
from kubernetes import client, config

app = Flask(__name__)


@app.route('/pods')
def index():
    ### Для подключения к кластеру изнутри пода используем сервис аккаунт.
    ### По умолчанию используется serviceAccount с именем default
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    res = v1.list_namespaced_pod("default")

    pods = []
    for pod in res.items:
        pods.append(pod.metadata.name)

    return {"pods": pods}


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='8080')
