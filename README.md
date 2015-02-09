dotfiles
========

Some dotfiles and a script that links them into your environment.

Usage
=====

If you already have your dotfiles versioned in this repository, getting your
dotfiles set up in a new environment is simple:

1. Clone this repo: `git clone git@github.com:CloudBoltSoftware/dotfiles.git`
2. Run the symlinking script: `./dotfiles/link.py` (`--help` for more options)

Getting Started
===============

If you want to begin versioning your dotfiles in this repository, follow these
steps:

1. Create a directory in this repository with the same name as your username.
   We'll call this your dotfiles directory.
2. Move your dotfiles into your dotfiles directory.
3. Run `link.py` --- links will be created in your home directory that point to
   the dotfiles in your dotfiles directory.

Now when you edit ~/.vimrc, you'll actually be editing the file that exists in
your copy of the dotfiles repo, allowing it to be versioned by git.

Linking to Directories (.dotfiles-subdir)
=========================================
By default, `link.py` does not link to directories. Instead, the source
directory's directory tree is mirrored into the destination directory and then
links are created to the contained files.

To force `link.py` to create a link to a directory instead of mirroring it,
create a file inside that directory called `.dotfiles-subdir`.

Example Use Case
----------------
Chris's VIM configuration looks for filetype-specific snippet files in a
directory called `~/.vim/custom-snippets/`. He'd like that directory to link to
the corresponding directory in his source directory so that if he creates a new
snippets file in `~/.vim/custom-snippets/`, it'll really be created underneath
his git-versioned source directory and be ready to add to git. To make
`link.py` link the entire directory instead of individually linking its
contents, he runs
`touch ~/dotfiles/chris/.vim/custom-snippets/.dotfiles-subdir`.
