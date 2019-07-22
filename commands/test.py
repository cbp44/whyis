# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask

import os


class Test(Command):
    """
    Run tests
    """

    ci = False
    verbosity = 2
    failfast = False
    tests = 'test*'

    def get_options(self):
        return [
            Option('--verbosity', '-v', dest='verbosity',
                   type=int, default=self.verbosity),
            Option('--failfast', dest='failfast',
                   default=self.failfast, action='store_false'),
            Option('--test', dest='tests',
                   default=self.tests, type=str),
            Option('--ci', dest='ci', default=self.ci, action='store_true')
        ]

    def run(self, verbosity, failfast, tests, ci):
        import sys
        import glob
        import unittest

        exists = os.path.exists
        isdir = os.path.isdir
        join = os.path.join

        project_path = os.path.abspath(os.path.dirname('.'))
        sys.path.insert(0, project_path)

        # our special folder for blueprints
        if exists('apps'):
            sys.path.insert(0, join('apps'))

        loader = unittest.TestLoader()
        all_tests = []

        if exists('apps'):
            for path in glob.glob('apps/*'):
                if isdir(path):
                    tests_dir = join(path, 'tests')

                    if exists(join(path, 'tests.py')):
                        all_tests.append(loader.discover(path, 'tests.py'))
                    elif exists(tests_dir):
                        all_tests.append(loader.discover(tests_dir, pattern=tests + '.py'))

        if exists('tests') and isdir('tests'):
            all_tests.append(loader.discover('tests', pattern=tests + '.py'))
        elif exists('tests.py'):
            all_tests.append(loader.discover('.', pattern='tests.py'))

        if 'app_path' in flask.current_app.config:
            print('Adding tests from', flask.current_app.config['app_path'])
            sys.path.insert(0, flask.current_app.config['app_path'])
            all_tests.append(loader.discover(join(flask.current_app.config['app_path'], 'tests'),
                                             pattern=tests + '.py',
                                             top_level_dir=flask.current_app.config['app_path']))

        test_suite = unittest.TestSuite(all_tests)

        if ci:
            import xmlrunner
            test_results_dir_path = os.path.join("test-results", "py")
            if not os.path.isdir(test_results_dir_path):
                os.makedirs(test_results_dir_path)
            with open(os.path.join(test_results_dir_path, "results.xml"), "wb") as output:
                xmlrunner.XMLTestRunner(output=output,
                                        verbosity=verbosity, failfast=failfast).run(test_suite)
                print("Wrote test results to", os.path.abspath(test_results_dir_path))
        else:
            unittest.TextTestRunner(
                verbosity=verbosity, failfast=failfast).run(test_suite)