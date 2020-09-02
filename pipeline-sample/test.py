import app


def test_answer():
    assert app.func(3) == 4


def test_hello():
    ret = app.func(2)
    assert app.hello() == "Hello World!: " + str(ret)
