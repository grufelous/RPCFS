from xmlrpc.client import ServerProxy

proxy = ServerProxy('http://localhost:3000')

def cli():
    print('client> ')
    proxy.do_stuff(10)

if __name__ == '__main__':
    cli()