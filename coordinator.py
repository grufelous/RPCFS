from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer


SERVER = SimpleXMLRPCServer(('localhost', 3000), logRequests=True)

FILESERVERS = list()


def add_fs(fs_port):
    if fs_port in FILESERVERS:
        return 'Port occupied'
    FILESERVERS.append(fs_port)
    print('Active fs: ', FILESERVERS)
    return f'Started fs at port {fs_port}'


def remove_fs(fs_port):
    if fs_port not in FILESERVERS:
        return 'Port already removed'
    FILESERVERS.remove(fs_port)
    print('Active fs: ', FILESERVERS)
    return f'Closed fs at port {fs_port}'


def get_fs():
    return FILESERVERS


if __name__ == '__main__':
    SERVER.register_function(add_fs)
    SERVER.register_function(remove_fs)
    SERVER.register_function(get_fs)
    try:
        print('Central coordinator started at port 3000')
        SERVER.serve_forever()
    except KeyboardInterrupt:
        print('Coordinator terminated')
