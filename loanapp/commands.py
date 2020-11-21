import click

from werkzeug.security import generate_password_hash

def create_admin():
    name = click.prompt('Admin name')
    password = click.prompt('Choose password')

    hashed_passwd = generate_password_hash(password, method="sha256")
    from loanapp.users.models import User
    new_user = User(name=name, password=hashed_passwd)
    new_user.setAdmin()

    from loanapp import db

    try:
        db.session.add(new_user)
        db.session.commit()
        click.echo('New admin created: ' + name)
    except Exception as e:
        print(e)
        click.echo('Admin with that name already exists.')

@click.command('create-admin')
def create_admin_command():
    """ Create an admin. """

    create_admin()


@click.command('init-db')
def init_database():
    """ Clear the existing data and create new tables. """

    from loanapp import db
    db.create_all()
    click.echo("Initialized the database.")
