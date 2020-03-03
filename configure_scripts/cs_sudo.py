import subprocess

class System:
    @staticmethod
    def _set_nopasswd_sudo(username):
        SUDOER_ENTRY = '{} ALL=(ALL:ALL) NOPASSWD:ALL\n'.format(username)
        sudoer_file = '/etc/sudoers'
        # Check if we are already in sudoers
        with open(sudoer_file, 'r') as sudoers:
            for line in sudoers.readlines():
                if line.strip() == SUDOER_ENTRY:
                    print("Already in sudoer's file!")
                    return
        with open(sudoer_file, 'a') as sudoers:
            sudoers.write(SUDOER_ENTRY)

    @staticmethod
    def module_name():
        if __name__ == '__main__':
            return 'setup'
        else:
            raise NotImplemented


    @staticmethod
    def set_nopasswd_sudo():
        script = ('from %s import System; System._set_nopasswd_sudo(\'%s\')'
            % (System.module_name(), USERNAME))
        subprocess.check_call('sudo python -c "%s"' % script)
