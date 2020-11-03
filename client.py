# Call by client
# from jsonrpclib import Server
# def main():
#     conn = Server('http://localhost:1006')
#     print(conn.findlen(('a','x','d','z'), 11, {'Mt. Abu': 1602, 'Mt. Nanda': 3001,'Mt. Kirubu': 102, 'Mt.Nish': 5710}))
# if __name__ == '__main__':
#     main()

from xmlrpc.client import ServerProxy

proxy = ServerProxy('http://localhost:3000')

if __name__ == '__main__':
    # print(proxy.list_directory())
    print(proxy.do_stuff(5))
    print(proxy.do_stuff('hello'))
    print(proxy.list_directory('/'))