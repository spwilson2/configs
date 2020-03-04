#!/usr/bin/python
import configure_scripts.confsys as confsys

if __name__ == '__main__':
    print('Warning! Setup will overwrite existing .rc files.')
    input('Press enter to continue: ')
    args = ['setup', '-f']
    confsys.main(args)
