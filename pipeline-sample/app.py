from flask import Flask
app = Flask(__name__)


def func(x):
    return x + 1


def func(x):
    return x + 1


@app.route('/')
def hello():
    ret = func(2)
    return "Hello World!: " + str(ret)


if __name__ == '__main__':
    app.run()
