A script that makes links in your home directory that point to your versioned
dotfiles.

Great for installing your dotfiles on a new machine!


Usage
=====

If your dotfiles repository is located at `~/dotfiles/`, then the command
`./link --src-dir ~/dotfiles/` will mirror your versioned dotfiles into your
home directory by creating a symbolic link for each file.

Linking to Directories (.dotfiles-subdir)
=========================================

By default, `link.py` does not link to directories. Instead, the source
directory's directory tree is mirrored into the destination directory and then
links are created to the contained files.

To force `link.py` to create a link to a directory instead of mirroring it,
create a file inside that directory called `.dotfiles-subdir`.

Example Use Case
----------------

Chris's VIM configuration looks for snippet files in `~/.vim/custom-snippets/`.
He'd like that directory to link to the corresponding directory in his source
directory so that if he creates a new snippets file in
`~/.vim/custom-snippets/`, it'll really be created underneath his git-versioned
source directory and be ready to add to git. To make `link.py` link the entire
directory instead of individually linking its contents, he creates the file
`~/dotfiles/.vim/custom-snippets/.dotfiles-subdir` in his dotfiles repo.
