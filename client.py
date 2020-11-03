from xmlrpc.client import ServerProxy

proxy = ServerProxy('http://localhost:3000')

if __name__ == '__main__':
    # print(proxy.list_directory())
    print(proxy.do_stuff(5))
    print(proxy.do_stuff('hello'))
    print(proxy.list_directory('/'))