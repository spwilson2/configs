#!/usr/bin/python


def main():
    ME_SUDOER = '%{} ALL=(ALL:ALL) NOPASSWD:ALL'.format('swilson')
    with open('/etc/sudoers', 'r') as sudoers:
        lines = sudoers.readlines()
    for line in lines:
        if line.strip() == ME_SUDOER:
            print("Already in sudoer's file!")
            return

    with open('/etc/sudoers', 'a') as sudoers:
        sudoers.write(ME_SUDOER)


if __name__ == '__main__':
    main()
