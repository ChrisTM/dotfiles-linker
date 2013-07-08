#! /bin/env python

import argparse

import os
from os.path import abspath, dirname, join, expanduser


def link_dotfiles(src_dir, dst_dir):
    """
    Populate `dst_dir` with links for the the dotfiles contained in `src_dir`.
    """
    src_dir = abspath(src_dir)
    dst_dir = abspath(dst_dir)

    for dotfile_name in os.listdir(src_dir):
        dotfile_path = join(src_dir, dotfile_name)
        link_path = join(dst_dir, dotfile_name)

        try:
            os.symlink(dotfile_path, link_path)
        except Exception as e:
            print "{}: Not linked. ({})".format(dotfile_name, e)
        else:
            print "{}: Linked.".format(dotfile_name)


# TODO: Support a new use case. Example: a user already has a .ssh dir with
# their keyfiles. The /contents/ of dotfiles/.ssh should be linked; not the
# directory itself. I'd like `link_dotfiles` to call this function (instead of
# doing the linking itself). This function will look to see if directories in
# dotfiles/ contain a file named '.dotfiles_subdir'. If it does, instead of
# linking the directory, it'll recursively call link_contents on that
# directory.
def link_contents(src_dir, dst_dir):
    """Create links in dst_dir that point to the contents in src_dir."""
    pass


if __name__ == "__main__":
    script_dir = abspath(dirname(__file__))
    default_dotfiles_dir = join(script_dir, 'dotfiles')

    parser = argparse.ArgumentParser(
        description='Link your dotfiles into your home directory.',
    )
    parser.add_argument(
        '--dotfiles-dir',
        metavar='DIR',
        help='the directory containing the dotfiles that you want to install',
        default=default_dotfiles_dir,
    )

    args = parser.parse_args()

    src_dir = abspath(args.dotfiles_dir)
    dst_dir = abspath(expanduser('~'))

    link_dotfiles(src_dir, dst_dir)
