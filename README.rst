Mymusic
=======

Just a minimalist console (ncurses) for listen my music 

Do you need of vlc.

Installation
------------

::

    git clone https://github.com/fraoustin/mymusic.git
    cd mymusic
    python setup.py install

Usage
-----

::

    mymusic /home/user/Music

shortcuts:

- q : quit
- + : more sound
- - : less sound
- enter : selected element
- p : play
- s : stop
- space : pause

You can listen a stream by m3u file.

Sample myradio.m3u

::

    #EXTM3U

    #EXTINF:-1,TSF Jazz
    http://broadcast.infomaniak.net:80/tsfjazz-high.mp3

Library
-------

I use python Library

- npyscreen
- vlc