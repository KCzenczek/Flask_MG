import os
import sys
from app import create_app, db
from app.models import User, Role
import unittest
import click


app = create_app(os.getenv('FLASK_CONFIG') or 'default')


COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='uruchom testy z pomiarem pokrycia kodu')
@click.argument('test_names', nargs=-1)
def test(coverage, test_names):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('info o pokryciu kodu:')
        COV.report()
        COV.erase()


# @app.cli.command()
# @click.argument('test_names', nargs=-1)
# def test(test_names):
#     """Run the unit tests."""
#     if test_names:
#         tests = unittest.TestLoader().loadTestsFromNames(test_names)
#     else:
#         tests = unittest.TestLoader().discover('tests')
#     unittest.TextTestRunner(verbosity=2).run(tests)


# @app.cli.command()
# def test():
#     """
#     run unittest
#     """
#     import unittest
#     tests = unittest.TestLoader().discover('tests')
#     unittest.TextTestRunner(verbosity=2).run(tests)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)
