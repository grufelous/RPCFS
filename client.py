from xmlrpc.client import ServerProxy

proxy = ServerProxy('http://localhost:3000')

def cli():
    print('client> ')

if __name__ == '__main__':
    cli()