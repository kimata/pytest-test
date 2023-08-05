#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys
import pathlib
from unittest import mock

sys.path.append(str(pathlib.Path(__file__).parent.parent / "myproject"))


# テストを実行する際に，環境変数をセットする．
@pytest.fixture(scope="session", autouse=True)
def env_mock():
    with mock.patch.dict(
        "os.environ",
        {
            "TEST": "true",
        },
    ) as fixture:
        yield fixture


# NOTE: 環境変数のセット
def test_env(mocker):
    import os

    assert os.environ.get("TEST", "NONE") == "true"


# NOTE: 返値の置き換え(固定値)
def test_mock_return_value_1(mocker):
    import a

    # 置き換え前
    assert a.a_func() == "called a_func"

    # 「TEST」を返すように置き換え
    mocker.patch("a.a_func", return_value="T")

    # 置き換え後
    assert a.a_func() == "T"
    assert a.a_func() == "T"
    assert a.a_func() == "T"


# NOTE: 返値の置き換え(呼び出しの度に変化)
def test_mock_return_value_2(mocker):
    import a

    # 置き換え前
    assert a.a_func() == "called a_func"

    # 「T1」～「T3」を順次返すように置き換え
    mocker.patch("a.a_func", side_effect=["T0", "T1", "T2"])

    # 置き換え後
    assert a.a_func() == "T0"
    assert a.a_func() == "T1"
    assert a.a_func() == "T2"
    # もう1回追加で呼び出すとエラーになる


# NOTE: 返値の置き換え(呼び出し回数で変化)
def test_mock_return_value_3(mocker):
    import a

    # 置き換え前
    assert a.a_func() == "called a_func"

    # 「T1」～「T3」を順次返すように置き換え
    def a_mock():
        a_mock.i += 1
        return "T{i}".format(i=a_mock.i % 3)

    a_mock.i = 2

    mocker.patch("a.a_func", side_effect=a_mock)

    # 置き換え後
    assert a.a_func() == "T0"
    assert a.a_func() == "T1"
    assert a.a_func() == "T2"
    assert a.a_func() == "T0"


# NOTE: 返値の置き換え(特定の関数から呼び出されたときのみ変化)
def test_mock_return_value_4(mocker):
    import a
    import b

    # 置き換え前
    assert a.a_func() == "called a_func"
    assert b.b_func() == "called a_func"

    import inspect
    from a import a_func  # オリジナルを import

    def a_mock():
        caller = inspect.stack()[4].function
        if caller == "b_func":
            return "T0"
        else:
            return a_func()

    mocker.patch("a.a_func", side_effect=a_mock)

    # 置き換え後
    assert a.a_func() == "called a_func"
    assert b.b_func() == "T0"


# NOTE: 返値の置き換え(from x import y の場合)
def test_mock_return_value_5(mocker):
    import a
    import b

    # 置き換え前
    assert a.a_func() == "called a_func"
    assert b.b_func() == "called a_func"
    assert b.b_func2() == "called a_func"

    mocker.patch("a.a_func", return_value="T")

    # 置き換え後
    assert a.a_func() == "T"
    assert b.b_func() == "T"
    assert b.b_func2() == "called a_func"  # 置き換わらない

    mocker.patch("b.a_func", return_value="T2")

    assert a.a_func() == "T"
    assert b.b_func() == "T"
    assert b.b_func2() == "T2"


# NOTE: 返値の置き換え (例外)
def test_mock_return_value_6(mocker):
    import a

    # 置き換え前
    assert a.a_func() == "called a_func"

    mocker.patch("a.a_func", side_effect=RuntimeError)

    with pytest.raises(RuntimeError):
        a.a_func()


# NOTE: オブジェクトの置き換え (メソッド及びプロパティを置き換え)
def test_mock_object_1(mocker):
    import c

    c_obj = c.C()

    assert c_obj.c_func() == "called C.c_func"
    assert c_obj.prop == "prop C"

    mocker.patch.object(c.C, "c_func", return_value="T")
    mocker.patch.object(c.C, "prop", new_callable=mocker.PropertyMock, return_value="prop T")

    c_obj = c.C()

    assert c_obj.c_func() == "T"
    assert c_obj.prop == "prop T"


# NOTE: 応用編 (open の置き換え)
def test_mock_open_1(mocker):
    import builtins
    import string
    import random

    # このファイル名が指定されたときに置き換えることにする
    target_file = "".join(random.sample(string.ascii_lowercase, 10))

    open_orig = builtins.open  # オリジナルの関数を保存する

    file_mock = mocker.MagicMock()
    file_mock.read.return_value = "T"

    def open_mock(
        file,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True,
        opener=None,
    ):
        # ファイル名が一致する場合のみ置換
        if file == target_file:
            return file_mock
        else:
            return open_orig(file, mode, buffering, encoding, errors, newline, closefd, opener)

    mocker.patch("builtins.open", side_effect=open_mock)

    # 存在しないファイルを読み書き
    f = open(target_file)
    f.write("T")
    assert f.read() == "T"

    # ファイル名がターゲットと異なる場合はエラーが出る
    with pytest.raises(FileNotFoundError):
        f = open(target_file + "_")


# NOTE: 応用編 (open の置き換え)
def test_mock_open_2(mocker):
    import builtins
    import string
    import random

    # このファイル名が指定されたときに置き換えることにする
    target_file = "".join(random.sample(string.ascii_lowercase, 10))

    file_mock = mocker.MagicMock()
    file_mock.__enter__.return_value.read.return_value = "T"

    open_orig = builtins.open

    def open_mock(
        file,
        mode="r",
        buffering=-1,
        encoding=None,
        errors=None,
        newline=None,
        closefd=True,
        opener=None,
    ):
        if file == target_file:
            return file_mock
        else:
            return open_orig(file, mode, buffering, encoding, errors, newline, closefd, opener)

    mocker.patch("builtins.open", side_effect=open_mock)

    # NOTE: 存在しないファイルを読み書き

    with open(target_file) as f:
        f.write("T")
        assert f.read() == "T"


# NOTE: 応用編 (requests.get の置き換え)
def test_mock_request(mocker):
    import requests

    res = requests.models.Response()
    res._content_consumed = True
    res._content = b'{"T": true}'
    res.encoding = "utf-8"
    res.status_code = 200

    mocker.patch("requests.get", return_value=res)

    assert requests.get("DUMMY").status_code == 200
    assert requests.get("DUMMY").text == '{"T": true}'
    assert requests.get("DUMMY").json() == {"T": True}


# NOTE: 応用編 (Slack 通知の置き換え)
@pytest.fixture(scope="session", autouse=True)
def slack_mock():
    with mock.patch(
        "slack_sdk.web.client.WebClient.chat_postMessage",
        retunr_value=True,
    ) as fixture:
        yield fixture


def test_mock_slack(mocker):
    import slack_sdk

    client = slack_sdk.WebClient(token="DUMMY")
    client.chat_postMessage(channel="DUMMY", text="DUMMY")


# NOTE: 時間の操作
def test_create_sensor_graph_1(freezer):
    import schedule
