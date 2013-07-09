#! /bin/env python

import argparse

import os
from os import path
from os.path import abspath, dirname, join, expanduser

# Directories containing a file with this name will not be linked; their
# contents will be linked instead
SUBDIR_ANNOTATION = ".dotfiles_subdir"


def link(target, link, root_dir='.'):
    """
    Create a symbolic link named `link` that points to `target`.
    """
    # Name of the current dotfile, as relative to the dotfiles dir. We use this
    # instead of `target` in output because it's shorter.
    rel_name = path.relpath(target, root_dir)
    try:
        os.symlink(target, link)
    except Exception as e:
        print "{}:\tNot linked. ({})".format(rel_name, e)
    else:
        print "{}:\tLinked.".format(rel_name)


def link_contents(src_dir, dst_dir, root_dir='.'):
    """
    Create links in dst_dir that point to the contents in src_dir.

    If `src_dir` contains a file called `.dotfiles_subdir`, instead of creating
    a link to `src_dir`, a dir named `src_dir` will be created inside `dst_dir`
    and links for `src_dir`'s contents will be created in that new dir.

    This `.dotfiles_subdir` behavior is useful in cases like the following: a
    user's ~/.ssh dir is meant to contain both versioned and unversioned files
    (like their private keys). We cannot replace their ~/.ssh dir with a link
    to ~/dotfiles/dotfiles/.ssh becaue then their keys would not be accessible.
    A file called ~/dotfiles/dotfiles/.ssh/.dotfiles_subdir indicates that the
    contents and not the directory itself should be linked. Now the user's
    private keys can exist as siblings of any linked config files.
    """
    src_dir = abspath(src_dir)
    dst_dir = abspath(dst_dir)
    root_dir = abspath(root_dir)

    if not path.exists(dst_dir):
        print "{}:\tDotfiles subdir created."
        os.mkdir(dst_dir)

    for name in os.listdir(src_dir):
        if name == SUBDIR_ANNOTATION:
            continue

        src_path = join(src_dir, name)
        dst_path = join(dst_dir, name)

        if path.isdir(src_path) and SUBDIR_ANNOTATION in os.listdir(src_path):
            link_contents(src_path, dst_path, root_dir=root_dir)
        else:
            link(src_path, dst_path, root_dir=root_dir)


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

    link_contents(src_dir, dst_dir, root_dir=src_dir)
