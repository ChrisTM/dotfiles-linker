#! /bin/env python

import argparse

import errno
import filecmp
import os
from os import path

# Directories containing a file with this name will not be linked; their
# contents will be linked instead
SUBDIR_ANNOTATION = ".dotfiles_subdir"


def files_differ(path_a, path_b):
    """
    Return True if the files at `path_a` and `path_b` have different
    content.
    """
    return not filecmp.cmp(path_a, path_b)


class Linker(object):
    def __init__(self, src_dir, dst_dir):
        self.src_dir = path.abspath(src_dir)
        self.dst_dir = path.abspath(dst_dir)

    def run(self):
        self._link_contents(self.src_dir, self.dst_dir)

    def _link(self, target, link):
        """
        Create a symbolic link named `link` that points to `target`.
        """
        # Name of the current dotfile, as relative to the dotfiles dir. We use this
        # instead of `target` in output because it's shorter.
        display_name = path.relpath(target, self.src_dir)

        if path.islink(link) and path.realpath(link) == path.realpath(target):
            print "{}:\tAlready linked.".format(display_name)
            return

        try:
            os.symlink(target, link)
        except Exception as e:
            if e.errno == errno.EEXIST:
                if files_differ(target, link):
                    diff_msg = 'a different'
                else:
                    diff_msg = 'an identical'

                print "{}:\tNot linked --- {} file already exists.".format(
                    display_name, diff_msg)
            else:
                print "{}:\tNot linked ({})".format(display_name, e)
        else:
            print "{}:\tLinked.".format(display_name)


    def _link_contents(self, src_dir, dst_dir):
        """
        Create links in dst_dir that point to the contents in src_dir.

        If `src_dir` contains a file called `.dotfiles_subdir`, instead of
        creating a link to `src_dir`, a dir named `src_dir` will be created
        inside `dst_dir` and links for `src_dir`'s contents will be created in
        that new dir.

        This `.dotfiles_subdir` behavior is useful in cases like the following:
        a user's ~/.ssh dir is meant to contain both versioned and unversioned
        files (like their private keys). We cannot replace their ~/.ssh dir
        with a link to ~/dotfiles/dotfiles/.ssh becaue then their keys would
        not be accessible.  A file called
        ~/dotfiles/dotfiles/.ssh/.dotfiles_subdir indicates that the contents
        and not the directory itself should be linked. Now the user's private
        keys can exist as siblings of any linked config files.
        """
        if not path.exists(dst_dir):
            display_name = path.relpath(src_dir, self.src_dir)
            os.mkdir(dst_dir)
            print "{}:\tSubdir created.".format(display_name)

        for name in os.listdir(src_dir):
            if name == SUBDIR_ANNOTATION:
                continue

            src_path = path.join(src_dir, name)
            dst_path = path.join(dst_dir, name)

            if (path.isdir(src_path) and
                    SUBDIR_ANNOTATION in os.listdir(src_path)):
                self._link_contents(src_path, dst_path)
            else:
                self._link(src_path, dst_path)

if __name__ == "__main__":
    script_dir = path.abspath(path.dirname(__file__))
    default_dotfiles_dir = path.join(script_dir, 'dotfiles')

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

    src_dir = path.abspath(args.dotfiles_dir)
    dst_dir = path.abspath(path.expanduser('~'))

    linker = Linker(src_dir, dst_dir)
    linker.run()
