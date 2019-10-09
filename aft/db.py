import pymysql.cursors
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(host=current_app.config['DB_HOST'],
                             user=current_app.config['DB_USER'],
                             password=current_app.config['DB_PASS'],
                             db=current_app.config['DB'],
                             cursorclass=current_app.config['CURSOR'])
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    with current_app.open_resource('./schema.sql') as f:
        queries = f.read().decode('utf-8').replace('\n', ' ').replace('/t', ' ').split(';')
        for num, query in enumerate(queries[:len(queries)-1]):
            db.execute(query)
            # print(num, query, '\n')


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
