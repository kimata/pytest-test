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


# NOTE: オブジェクトの置き換え (メソッド及びプロパティを置き換え)
def test_mock_object_1(mocker):
    import c

    c_obj = c.C()

    assert c_obj.c_func() == "called C.c_func"
    assert c_obj.prop == "prop C"

    mocker.patch.object(c.C, "c_func", return_value="T")
    mocker.patch.object(
        c.C, "prop", new_callable=mocker.PropertyMock, return_value="prop T"
    )

    c_obj = c.C()

    assert c_obj.c_func() == "T"
    assert c_obj.prop == "prop T"


# NOTE: オブジェクトの置き換え
def test_mock_object_2(mocker):
    import builtins
    import string
    import random

    # このファイル名が指定されたときに置き換えることにする
    target_file = "".join(random.sample(string.ascii_lowercase, 10))

    file_mock = mocker.MagicMock()
    file_mock.read.return_value = "T"

    # mocker.patch.object(open_mock, "write", return_value=None)

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
            return open_orig(
                file, mode, buffering, encoding, errors, newline, closefd, opener
            )

    mocker.patch("builtins.open", side_effect=open_mock)

    # NOTE: 存在しないファイルを読み書き
    f = open(target_file)
    f.write("T")
    assert f.read() == "T"
