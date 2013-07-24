#! /bin/env python

import argparse

from collections import defaultdict, OrderedDict
import errno
import filecmp
import os
from os import path

# Directories containing a file with this name will be linked to directly
# instead of having its contents linked individually.
SUBDIR_ANNOTATION = '.dotfiles-subdir'


def files_differ(path_a, path_b):
    """
    True if the files at `path_a` and `path_b` have different content.
    """
    return not filecmp.cmp(path_a, path_b)


class Linker(object):
    RESULT_DESCRIPTIONS = OrderedDict([
        ('subdir.created', 'Subdirs created'),
        ('subdir.exists', 'Subdirs already created'),
        ('subdir.not-created', 'Subdirs not created'),

        ('link.created', 'Links created'),
        ('link.exists', 'Links already created'),
        ('link.not-created', 'Links not created'),
    ])
    RESULT_TYPES = RESULT_DESCRIPTIONS.keys()

    # used for pretty-printing
    _max_type_width = max(map(len, RESULT_TYPES))

    def __init__(self, src_dir, dst_dir, show_progress=False):
        self.src_dir = path.abspath(src_dir)
        self.dst_dir = path.abspath(dst_dir)
        self.show_progress = show_progress

        self.results = []  # tuples of form (result, path, reason)

    def run(self):
        self._link_contents(self.src_dir, self.dst_dir)

    def _link(self, target, link):
        """
        Create a symbolic link named `link` that points to `target`.
        """
        if path.islink(link) and path.realpath(link) == path.realpath(target):
            self._add_result('link.exists', link)
            return

        try:
            os.symlink(target, link)
        except Exception as e:
            if e.errno == errno.EEXIST:
                if files_differ(target, link):
                    reason = 'a different file already exists'
                else:
                    reason = 'an identical file already exists'

                self._add_result('link.not-created', link, reason=reason)
            else:
                self._add_result('link.not-created', link, reason=e)
        else:
            self._add_result('link.created', link)

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
        if path.exists(dst_dir):
            if path.isdir(dst_dir):
                self._add_result('subdir.exists', dst_dir)
            else:
                self._add_result(
                    'subdir.not-created', dst_dir,
                    reason='something already exists here'
                )
        else:
            os.mkdir(dst_dir)
            self._add_result('subdir.created', dst_dir)

        for name in os.listdir(src_dir):
            if name == SUBDIR_ANNOTATION:
                continue

            src_path = path.join(src_dir, name)
            dst_path = path.join(dst_dir, name)

            if (path.isdir(src_path) and
                    SUBDIR_ANNOTATION not in os.listdir(src_path)):
                self._link_contents(src_path, dst_path)
            else:
                self._link(src_path, dst_path)

    def _add_result(self, type, path, reason=None):
        """
        Remember that `result` happened while trying to create the link or
        subdir at `path`.
        """
        assert type in self.RESULT_TYPES

        self.results.append({'type': type, 'path': path, 'reason': reason})

        if self.show_progress:
            if reason:
                template = '{type:<{type_width}} {path} ({reason})'
            else:
                template = '{type:<{type_width}} {path}'

            print template.format(
                type=type, path=path, reason=reason,
                type_width=self._max_type_width)

    def summary(self):
        """
        Return a string summarizing the results of a linking run.
        """
        lines_by_type = defaultdict(list)
        for result in self.results:
            if result['reason']:
                line_template = '  {path} ({reason})'
            else:
                line_template = '  {path}'
            lines_by_type[result['type']].append(
                line_template.format(**result)
            )

        lines = []
        for type in self.RESULT_TYPES:
            # only output if we have lines for this result type and if the
            # result type is one that affects the filesystem (*.exists do not).
            if type in lines_by_type and not type.endswith('.exists'):
                lines.append(self.RESULT_DESCRIPTIONS[type])
                lines.extend(lines_by_type[type])

        summary = '\n'.join(lines)

        return summary or 'Everything is linked. No changes made.'


if __name__ == '__main__':
    script_dir = path.abspath(path.dirname(__file__))

    default_dst_dir = path.abspath(path.expanduser('~'))
    # we guess their username from their home directory and assume they've got
    # a folder in the dotfiles repo with that name
    username = path.basename(default_dst_dir)
    default_src_dir = path.join(script_dir, username)

    parser = argparse.ArgumentParser(
        description='Link your dotfiles into your home directory.',
    )
    parser.add_argument(
        '--src-dir',
        metavar='DIR',
        help='The directory containing the dotfiles you want to link. (default: %(default)s)',
        default=default_src_dir,
    )
    parser.add_argument(
        '--dst-dir',
        metavar='DIR',
        help='The directory where you want to link the dotfiles. (default: %(default)s)',
        default=default_dst_dir,
    )
    parser.add_argument(
        '-v', '--progress',
        help='Print status messages while linking.',
        action='store_true',
        default=False,
    )

    args = parser.parse_args()

    # verify that --src-dir and --dst-dir exist
    some_dirs_do_not_exist = False
    for dir_type, dir_path in [('--src-dir', args.src_dir),
                               ('--dst-dir', args.dst_dir)]:
        if not path.isdir(dir_path):
            some_dirs_do_not_exist = True
            print "Error: The {} directory {} does not exist.".format(
                dir_type, dir_path)
    if some_dirs_do_not_exist:
        exit(1)

    linker = Linker(
        src_dir=args.src_dir,
        dst_dir=args.dst_dir,
        show_progress=args.progress,
    )
    linker.run()

    # print a blank line to differentiate progress messages from the summary
    if args.progress:
        print

    print linker.summary()
