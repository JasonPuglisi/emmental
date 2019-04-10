"""Searches the filesystem for videos."""

import subprocess


def search_ls(directory, query):
    """Use ls to search the video directory."""
    cmd = f'ls {directory} | grep {query}'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = process.stdout.read()
    return output.decode('utf-8')
