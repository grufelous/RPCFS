from xmlrpc.client import ServerProxy

proxy = ServerProxy('http://localhost:7000')



def cli():
    print('client> ')
    # print(proxy.do_stuff(10))
    print(proxy.present_working_directory('lol'))

if __name__ == '__main__':
    cli()
