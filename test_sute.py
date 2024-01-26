#!/usr/bin/env python3
__author__ = 'igorsia'
__licence__ = 'GPL2'

import sys
import os
import subprocess
import time
import zipfile
from shutil import rmtree
import tempfile


def exec_prg(prg_name, test_file):
    args = ['python3', prg_name] if prg_name.endswith('.py') else [prg_name]
    rez = subprocess.run(['python3', prg_name],
                         capture_output=True,
                         stdin=test_file)
    out = rez.stdout.decode()
    err = rez.stderr.decode()
    return_code = rez.returncode
    return return_code, out, err


def main(prg_name, zip_name):
    def open_zip_file(zipname):
        # zipname = sys.argv[1]
        if zipfile.is_zipfile(zipname):
            zipp = zipfile.ZipFile(zipname, 'r')
        else:
            print(f"Файл {zipname} не является zip архивом")
            quit()

        tmp_dir = tempfile.gettempdir()
        tmp_dir = os.path.join(tmp_dir, f"{os.path.basename(zipname)}.tmp")

        if os.path.exists(tmp_dir) and os.path.isdir(tmp_dir):
            rmdir(tmp_dir)
        os.mkdir(tmp_dir)
        zipp.extractall(tmp_dir)
        os.chdir(tmp_dir)
        return tmp_dir

    def rmdir(tmpdir):
        if os.path.isdir(tmpdir):
            rmtree(tmpdir, ignore_errors=False, onerror=None)

    cur_path = os.path.dirname(os.path.realpath(__file__))
    tmp_dir = open_zip_file(zip_name)

    for test in sorted([int(x.split('.')[0]) for x in filter(lambda a: a.endswith('.a'), os.listdir())]):
        print(f'Тестируем {prg_name} {test}', end=' ')
        with open(f'{test}') as fl, open(f'{test}.a') as ft:
            start = time.time_ns()
            rc, out, err = exec_prg(os.path.join(cur_path, prg_name), fl)
            end = time.time_ns()
            print(f"{'С ошибкой' if rc else 'Успешно.'}", end=' ')
            test_out = '\n'.join([x.rstrip() for x in ft.readlines()]) + '\n'
            rez = out == test_out
            print(f'Тест {"пройден" if rez else "не пройден"}', end=' ')
            print(f'за {(end - start)/1_000_000:.0f} ms')
            if not rez:
                print(f'|{test_out.encode()}|{out.encode()}|')
            if rc:
                print(err)

    rmdir(tmp_dir)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: \n{sys.argv[0]} program.py tests.zip')
        quit(1)
    main(sys.argv[1], sys.argv[2])

