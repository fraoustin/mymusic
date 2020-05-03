#!/usr/bin/env python3
from .npyscreen import StandardApp, FormBaseNew, wgtextbox, SimpleGrid
import os
import sys
import datetime
import curses
from .vlc import State, MediaPlayer
import click


def convertMillis(millis):
    dte = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=millis/1000)
    return dte.strftime("%H:%M:%S")


class M3u():

    def __init__(self, data):
        self.uri = None
        self.name = ''
        with open(data) as e:
            for line in e:
                if line.startswith("#EXTINF:-1,"):
                    self.name = line[len("#EXTINF:-1,"):].replace('\n', '')
                if line.startswith("http://"):
                    self.uri = line.replace('\n', '')

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MyMediaPlayer(metaclass=Singleton):
    
    def __init__(self):
        self.uri = ""
        self.ihm = None
        self.vlc = MediaPlayer()
        self._title = ""
        self._album = ""
        self._author = ""

    @property
    def title(self):
        return self._title

    @property
    def album(self):
        return self._album

    @property
    def author(self):
        return self._author
    
    @property
    def timer(self):
        if self.vlc.get_time() > 0:
            return convertMillis(self.vlc.get_time())
        return ''

    @property
    def length(self):
        if self.vlc.get_length() > 0:
            return convertMillis(self.vlc.get_length())
        return ''

    @property
    def volume(self):
        return self.vlc.audio_get_volume()

    @property
    def state(self):
        return self.vlc.get_state()
 
    def change_uri(self, ihm, uri=None):
        self.ihm = ihm
        self.vlc.stop()
        del self.vlc
        if uri.endswith('.m3u'):
            m3u = M3u(uri)
            self.vlc = MediaPlayer(m3u.uri)
            self.uri = m3u.uri
            self._title = m3u.name
            self._album = ""
            self._author = ""
        else:
            self.vlc = MediaPlayer("file://%s" % uri)
            self.uri = "file://%s" % uri
            uri = self.uri[7:]
            self._title = os.path.splitext(os.path.basename(uri))[0]
            self._album = os.path.split(os.path.split(uri)[0])[1]
            self._author = os.path.split(os.path.split(os.path.split(uri)[0])[0])[1]
        self.vlc.play()
    
    def play(self):
        self.vlc.play()
    
    def pause(self):
        self.vlc.pause()
    
    def stop(self):
        self.vlc.stop()
    
    def play(self):
        self.vlc.play()

    def sound_more(self):
        vol = self.vlc.audio_get_volume()
        self.vlc.audio_set_volume(min(vol+5, 100))

    def sound_less(self):
        vol = self.vlc.audio_get_volume()
        self.vlc.audio_set_volume(max(vol-5, 0))

class MyMusic(StandardApp):

    def __init__(self, path):
        StandardApp.__init__(self)
        self.path = path

    def onStart(self):
        self.addForm("MAIN", MainForm, name="My Music", path=self.path)


class MainForm(FormBaseNew):

    ALLOW_RESIZE = True

    def __init__(self, path='.', *args, **keywords):
        self.path = os.path.abspath(path)
        self.root = os.path.abspath(path)
        FormBaseNew.__init__(self, minimum_lines = 8,  minimum_columns = 8,*args, **keywords)

    def create(self):
        y, x = self.useable_space()
        self._create_gd()
        self._update_gd(self._get_listdir(self.path))
        self.gd.add_handlers({
            curses.ascii.NL: self.select_element,
            curses.ascii.SP: self.sound_pause,
            ord('q'): self.exit_application,
            ord('+'): self.sound_more,
            ord('-'): self.sound_less,
            ord('s'): self.sound_stop,
            ord('r'): self.refresh_force,
            ord('p'): self.sound_play
        })
        self.add(wgtextbox.TextfieldBase, value='', editable=False)
        self.infos = [self.add(wgtextbox.TextfieldBase, value='', editable=False, highlight_color='red'),
            self.add(wgtextbox.TextfieldBase, value='', editable=False),
            self.add(wgtextbox.TextfieldBase, value='', editable=False),
            self.add(wgtextbox.TextfieldBase, value='', editable=False)]

    def refresh_force(self, *args, **keywords):
        self.DISPLAY()
        self.DISPLAY()

    def refresh(self, *args, **keywords):
        self.infos[0].value = MyMediaPlayer().author
        self.infos[0].update()
        self.infos[1].value = MyMediaPlayer().album
        self.infos[1].update()
        self.infos[2].value = MyMediaPlayer().title
        self.infos[2].update()
        if MyMediaPlayer().state not in  [State.Stopped, State.NothingSpecial]:
            self.infos[3].value = MyMediaPlayer().timer + " / " + MyMediaPlayer().length + " Volume: " + str(MyMediaPlayer().volume)
        else:
            self.infos[3].value = ""
        if MyMediaPlayer().state in  [State.Paused]:
            self.infos[3].important = True
        if MyMediaPlayer().state in  [State.Stopped]:
            self.infos[0].highlight = True
        self.infos[3].update()
#       del error of vlc
        self.curses_pad.redrawwin()
        FormBaseNew.refresh(self, *args, **keywords)


    def _create_gd(self, val=200):
#       fix to dertmine max width
        while val > 1:
            try:
                self.gd = self.add(SimpleGrid, max_height=-5, column_width=val)
                val = 0
            except Exception:
                val = val-1

    def exit_application(self, *args, **keywords):
        curses.beep()
        self.parentApp.setNextForm(None)
        self.editing = False

    def sound_play(self, *args, **keywords):
        MyMediaPlayer().sound_play()

    def sound_more(self, *args, **keywords):
        MyMediaPlayer().sound_more()

    def sound_less(self, *args, **keywords):
        MyMediaPlayer().sound_less()

    def sound_pause(self, *args, **keywords):
        MyMediaPlayer().pause()

    def sound_stop(self, *args, **keywords):
        MyMediaPlayer().stop()

    def _update_gd(self, lst):
        self.gd.values = []
        for elt in lst:
            self.gd.values.append([elt,])
        self.gd.edit_cell = [0,0]

    def _get_listdir(self, path):
        lstelt = []
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        directorys = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        if os.path.abspath(path) != self.root:
            directorys = ['..',] + directorys
        for lst in [directorys, files]:
            lst.sort()
            for elt in lst:
                lstelt.append(elt)
        return lstelt


    def select_element(self, *args, **keywords):
        selected = self.gd.values[self.gd.edit_cell[0]][0]
        if os.path.isdir(os.path.join(self.path, selected)):
            self.path = os.path.join(self.path, selected)
            self._update_gd(self._get_listdir(self.path))
        else:
            MyMediaPlayer().change_uri(self, os.path.join(self.path, selected))


@click.command()
@click.argument('directory')
def run(directory):
    """DIRECTORY contains your music"""
    MyApp = MyMusic(directory)
    MyApp.run()

if __name__ == '__main__':
    run()