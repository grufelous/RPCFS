from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer


server = SimpleXMLRPCServer(('localhost', 3000), logRequests=True)

file_servers = set()


def add_fs(fs_port):
    if fs_port in file_servers:
        return 'Port occupied'
    file_servers.add(fs_port)
    print('Active fs: ', file_servers)
    return f'Started fs at port {fs_port}'


def remove_fs(fs_port):
    if fs_port not in file_servers:
        return 'Port already removed'
    file_servers.remove(fs_port)
    print('Active fs: ', file_servers)
    return f'Closed fs at port {fs_port}'


def get_fs():
    return file_servers.__str__()


if __name__ == '__main__':
    server.register_function(add_fs)
    server.register_function(remove_fs)
    server.register_function(get_fs)
    try:
        print('Central coordinator started at port 3000')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Coordinator terminated')
