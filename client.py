from xmlrpc.client import ServerProxy

from utils.reply import Reply

proxy = ServerProxy('http://localhost:7000')

supported_commands = {
    'pwd': 0,
    'ls': 0,
    'cp': 2,
    'cat': 1,
    'help': 0,
    'exit': 0,
}

def help_message():
    print('Supported commands: ')
    print('\tpwd')
    print('\tls <folder_name>')
    print('\tcp <source_file> <destination_file>')
    print('\tcat <file>')
    print('Use full paths as needed')

def cli():
    str_inp = input('client> ')
    tokens = ' '.join(str_inp.split(' ')).split()

    if len(tokens) == 0:
        print('Empty input')
    else:
        cmd = tokens[0]
        if cmd not in supported_commands:
            print('Command not found')
        elif supported_commands[cmd] != len(tokens)-1:
            print('Syntax error: argument mismatch')
        else:
            if cmd == 'help':
                help_message()
            elif cmd == 'pwd':
                print('{} mounted at /'.format(proxy.present_working_directory()))
            elif cmd == 'ls':
                print(proxy.list_directory())
            elif cmd == 'cp':
                print(proxy.copy_file(tokens[1], tokens[2]))
            elif cmd == 'cat':
                print(proxy.cat(tokens[1]))
            elif cmd == 'exit':
                exit()


if __name__ == '__main__':
    try:
        while(True):
            cli()
    except KeyboardInterrupt:
        print('Client terminated')
