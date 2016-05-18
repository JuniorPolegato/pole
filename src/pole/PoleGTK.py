#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PoleGTK - Operações com GTK em Python

Arquivo: PoleGTK.py
Versão.: 0.2.0
Autor..: Claudio Polegato Junior
Data...: 04 Abr 2011

Copyright © 2011 - Claudio Polegato Junior <junior@juniorpolegato.com.br>
Todos os direitos reservados
"""

# Importing PyGTK modules
import pygtk
import gtk
import gobject
import glib
import datetime
import PoleUtil
from PoleUtil import formatar
import PoleLog
import unicodedata
import sys
import os
import re
from string import strip
import logging
import traceback
import pango
import importlib

pygtk.require("2.0")

# Resolver problema de imagens não exibidas nos botões
gtk.settings_get_default().props.gtk_button_images = True

logger = logging.getLogger('pole')

cf = PoleUtil.convert_and_format

# Translation
_ = PoleUtil._

message_titles = {gtk.MESSAGE_INFO: _('Information'),
                  gtk.MESSAGE_WARNING: _('Warning'),
                  gtk.MESSAGE_QUESTION: _('Question'),
                  gtk.MESSAGE_ERROR: _('Error')}


def message(widget, text, message_type=gtk.MESSAGE_INFO, title=None):
    if message_type == gtk.MESSAGE_QUESTION:
        buttons = gtk.BUTTONS_YES_NO
    else:
        buttons = gtk.BUTTONS_CLOSE
    flags = flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
    dialog = gtk.MessageDialog(widget.get_toplevel(), flags,
                               message_type, buttons)
    dialog.set_markup(text)

    if title is None:
        title = message_titles[message_type]
    dialog.set_title(title)
    result = dialog.run()
    dialog.destroy()
    return result


def destroy(widget, event=None):
    widget.destroy()


def info_bar_ex(widget, message, message_type=gtk.MESSAGE_INFO,
                button_label='Fechar', callback=destroy, timeout=3000):
    bar = gtk.InfoBar()
    bar.set_message_type(message_type)
    bar.add_button(button_label, gtk.RESPONSE_CLOSE)
    bar.get_content_area().pack_start(gtk.Label(message), True, True)
    bar.connect('response', callback)
    bar.connect('close', destroy)

    widget.pack_start(bar, False, False)
    widget.reorder_child(bar, 0)
    bar.show_all()

    glib.timeout_add(timeout, lambda: bar.destroy())


def info_bar(parent, text, **kwargs):
    return info_bar_ex(parent, text, gtk.MESSAGE_INFO, **kwargs)


def warning_bar(parent, text, **kwargs):
    return info_bar_ex(parent, text, gtk.MESSAGE_WARNING, **kwargs)


def error_bar(parent, text, **kwargs):
    return info_bar_ex(parent, text, gtk.MESSAGE_ERROR, **kwargs)


def info(widget, text, title=None):
    return message(widget, text, gtk.MESSAGE_INFO, title)


def error(widget, text, title=None):
    return message(widget, text, gtk.MESSAGE_ERROR, title)


def warning(widget, text, title=None):
    return message(widget, text, gtk.MESSAGE_WARNING, title)


def question(widget, text, title=None):
    return message(widget, text, gtk.MESSAGE_QUESTION, title)


def error_detail(widget, text, detail_info, title=None):
    detail(widget, text, detail_info, title, gtk.MESSAGE_ERROR)


def warning_detail(widget, text, detail_info, title='Warning'):
    detail(widget, text, detail_info, title, gtk.MESSAGE_WARNING)


def detail(widget, text, detail_info, title=None,
           message_type=gtk.MESSAGE_INFO):
    # Get toplevel window
    if isinstance(widget, gtk.Widget):
        window = widget.get_toplevel()
    else:
        window = None
    # Create Message dialog with hidden details
    if title is None:
        title = message_titles[gtk.MESSAGE_ERROR]
    flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
    dialog = gtk.MessageDialog(window, flags, message_type,
                               gtk.BUTTONS_CLOSE, text)
    dialog.format_secondary_text(' ')
    dialog.set_title(title)
    l1 = dialog.get_message_area().children()[0]
    l1.set_line_wrap(False)
    expander = gtk.Expander(_('Details'))
    scroll = gtk.ScrolledWindow()
    text_buffer = gtk.TextBuffer()
    text_view = gtk.TextView(text_buffer)
    scroll.set_shadow_type(gtk.SHADOW_IN)
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    text_buffer.set_text(detail_info)
    text_view.set_editable(False)
    text_view.set_size_request(500, 300)
    dialog.child.pack_start(expander, True, True)
    expander.add(scroll)
    scroll.add(text_view)
    expander.show_all()
    dialog.set_resizable(True)
    result = dialog.run()
    dialog.destroy()
    return result


def show_exception(project, args):
    # Exception message
    exc_message = traceback.format_exc().strip().splitlines()
    pri_text = exc_message[-1][:80] + '…' * (len(exc_message[-1]) > 80)
    title = pri_text.split(':', 1)[0]
    # sec_text = '\n'.join(m[:100] + '…' * (len(m) > 100)
    #                                       for m in exc_message[-3:-1])
    # Get toplevel window
    if len(args) > 1 and isinstance(args[1], gtk.Widget):
        obj = args[1]
    else:
        for obj in project.interface.get_objects():
            if isinstance(obj, gtk.Widget):
                break
    return error_detail(obj, pri_text, '\n'.join(exc_message), title)


def select_file_or_folder(parent=None, title=None, file_or_folder=None,
                          filters=[], select_folder=False, save_file=False):
    if select_folder:
        select_type = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER
        if not title:
            title = _('Select folder')
    elif save_file:
        select_type = gtk.FILE_CHOOSER_ACTION_SAVE
        if not title:
            title = _('Select file to save to')
    else:
        select_type = gtk.FILE_CHOOSER_ACTION_OPEN
        if not title:
            title = _('Select file')

    parent = parent.get_toplevel()

    ok = gtk.STOCK_SAVE if save_file else gtk.STOCK_OPEN

    filechooser = gtk.FileChooserDialog(title,
                                        parent,
                                        select_type,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                         ok, gtk.RESPONSE_OK))

    for f in filters:
        if isinstance(f, (str, unicode)):
            fx = gtk.FileFilter()
            fx.set_name(f)
            fx.add_pattern(f)
            f = fx
        filechooser.add_filter(f)

    if file_or_folder:
        filechooser.set_filename(file_or_folder)
        if select_folder:
            filechooser.set_current_folder(file_or_folder)
        else:
            filechooser.set_current_name(os.path.split(file_or_folder)[-1])

    filechooser.set_default_response(gtk.RESPONSE_OK)

    try:
        if filechooser.run() == gtk.RESPONSE_OK:
            path = filechooser.get_filename()
            if not save_file:
                return path
            if not os.path.exists(path):
                return path
            if question(filechooser, 'Sobrescrever arquivo?') == gtk.RESPONSE_YES:
                return path

    finally:
        filechooser.destroy()


def save_file(parent=None, title=None, file_or_folder=None, filters=[]):
    return select_file_or_folder(parent, title, file_or_folder,
                                 filters, False, True)


def select_file(parent=None, title=None, file_or_folder=None, filters=[]):
    return select_file_or_folder(parent, title, file_or_folder,
                                 filters, False, False)


def select_folder(parent=None, title=None, file_or_folder=None, filters=[]):
    return select_file_or_folder(parent, title, file_or_folder,
                                 filters, True, False)


def show_toolbutton_menu(toolbutton, menu):
    toolbutton.children()[0].children()[1].clicked()
    x, y = toolbutton.get_toplevel().window.get_origin()
    x += toolbutton.allocation.x
    y += toolbutton.allocation.y + toolbutton.allocation.height
    menu.popup(None, None, lambda m: (x, y, True), 0, 0)


def pixbuf_new_from_binary(binary):
    pixloader = gtk.gdk.PixbufLoader()
    pixloader.write(binary)
    pixloader.close()
    return pixloader.get_pixbuf()


def load_images_as_icon(path='.'):
    for file in os.listdir(path):
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(path + os.sep + file)
            factory = gtk.IconFactory()
            iconset = gtk.IconSet(pixbuf)
            name = file[:file.rindex('.')] if '.' in file else file
            factory.add(name, iconset)
            factory.add_default()
        except:
            PoleLog.log_except()
        while gtk.events_pending():
            gtk.main_iteration()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Classe Calendar mostra o Calendário quando executada a função run,
# segurando parado o programa principal naquele ponto de chamada, tal
# como a run do GtkDialog, sendo que Enter emite Ok e Esc emite Cancelar
class PopupWindow(gtk.Window, gtk.Buildable):
    __gtype_name__ = 'PopupWindow'
    __gsignals__ = {
        "focus-out-event": "override",
        "button-press-event": "override",
        "delete-event": "override",
    }

    def __init__(self, *args):
        # print 'init 1 popup', self,args
        super(PopupWindow, self).__init__(*args)
        # print 'init 2 popup', self,args
        self.set_decorated(False)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        # self.connect('focus-out-event', self.quit)
        # self.connect("button-press-event", self.quit)
        # self.connect("delete-event", self.undelete)
        # For new versions of GTK+
        try:
            self.set_property('has_resize_grip', False)
        except:
            pass
        self.__canceled = False

    def do_delete_event(self, event):
        return True

    def run(self, caller, size=None, position=None, center=False, transient_for=None):
        if transient_for:
            toplevel = transient_for.get_toplevel()
        else:
            toplevel = caller.get_toplevel()
        # self.set_transient_for(toplevel)
        self.set_modal(True)
        self.__loop = glib.MainLoop()
        if center:
            if size is not None:
                self.set_size_request(*size)
            self.realize()
            window = caller.get_toplevel()
            x, y = window.window.get_origin()
            x += (window.allocation.width - self.allocation.width) / 2
            y += (window.allocation.height - self.allocation.height) / 2
        else:
            if position is None:
                x, y = caller.get_toplevel().window.get_origin()
                x += caller.allocation.x
                y += caller.allocation.y + caller.allocation.height
            else:
                x, y = position
            if size is None:
                self.resize(caller.allocation.width, 1)
            else:
                self.set_size_request(*size)
        self.move(x, y)
        if isinstance(self, Calendar):
            self.show_all()
        else:
            self.show()
        for i in range(1000):
            status = gtk.gdk.pointer_grab(window=self.window, owner_events=True,
                                          event_mask=gtk.gdk.BUTTON_PRESS_MASK,
                                          cursor=gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
            if status in (gtk.gdk.GRAB_SUCCESS, gtk.gdk.GRAB_ALREADY_GRABBED):
                break
        if status not in (gtk.gdk.GRAB_SUCCESS, gtk.gdk.GRAB_ALREADY_GRABBED):
            toplevel.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.__loop.run()
        gtk.gdk.pointer_ungrab()
        self.hide()
        return not self.__canceled

    def do_focus_out_event(self, event):
        self.__canceled = True
        self.quit(self, event)

    def do_button_press_event(self, event):
        self.quit(self, event)

    def quit(self, *args):
        try:
            popup = args[0]
        except:
            popup = self
        if len(args) == 2 and args[1].type in (gtk.gdk.BUTTON_PRESS, gtk.gdk._2BUTTON_PRESS, gtk.gdk._3BUTTON_PRESS):
            w, h = popup.get_size()
            x, y = popup.get_pointer()
            # print w, h , x, y, self
            if 0 <= x <= w and 0 <= y <= h:
                return
            self.__canceled = True
        # popup.__loop.quit()
        self.__loop.quit()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Classe Calendar mostra o Calendário quando executada a função run,
# segurando parado o programa principal naquele ponto de chamada, tal
# como a run do GtkDialog, sendo que Enter emite Ok e Esc emite Cancelar
class Calendar(PopupWindow):
    def __init__(self, caller, calendar_type=PoleUtil.DATE):
        super(Calendar, self).__init__()
        self.__caller = caller
        self.__type = calendar_type
        if isinstance(caller, gtk.Entry):
            self.__set_new_date = caller.set_text
            self.__old_date = caller.get_text()
        else:
            self.__set_new_date = caller.set_label
            self.__old_date = caller.get_label()
        self.connect("key-press-event", self.__key_press)
        # If date didn't have a z number, use now
        z = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        if not self.__old_date or not sum(map(lambda x: x in z, self.__old_date)):
            date = datetime.datetime.now()
            if self.__type == PoleUtil.HOLLERITH:
                date = PoleUtil.convert_and_format(date, datetime.date, PoleUtil.MONTH)[1]
        elif self.__type == PoleUtil.HOLLERITH:
            date = self.__old_date
        else:
            date = PoleUtil.convert_and_format(self.__old_date, datetime.datetime, self.__type)[0]
        self.__frame = gtk.Frame()
        self.add(self.__frame)
        self.__frame.set_shadow_type(gtk.SHADOW_IN)
        self.__vbox = gtk.VBox(spacing=5)
        self.__frame.add(self.__vbox)
        self.__buttons = gtk.HButtonBox()
        self.__ok = gtk.Button(stock='gtk-ok')
        self.__ok.child.child.get_children()[0].show()
        self.__arrow = gtk.Image()
        self.__arrow.set_from_stock('gtk-jump-to', gtk.ICON_SIZE_BUTTON)
        self.__today = gtk.Button(label=(_('_Today'), _('_Now'))[self.__type in (1, 2)])
        self.__today.set_image(self.__arrow)
        self.__today.child.child.get_children()[0].show()
        self.__cancel = gtk.Button(stock='gtk-cancel')
        self.__cancel.child.child.get_children()[0].show()
        self.__ok.connect('clicked', self.__change_date)
        self.__today.connect('clicked', self.__go_to_now)
        self.__today.connect('button-press-event', self.__double_click)
        self.__cancel.connect('clicked', self.quit)
        self.__buttons.pack_start(self.__ok)
        self.__buttons.pack_start(self.__today)
        self.__buttons.pack_start(self.__cancel)
        if self.__type in (PoleUtil.MONTH, PoleUtil.HOLLERITH):
            self.__table = gtk.Table(homogeneous=True)
            toggle = None
            if self.__type == PoleUtil.HOLLERITH:
                toggle = gtk.RadioButton(toggle, '13 - 13º Pagto')
                toggle.set_mode(False)
                toggle.set_relief(gtk.RELIEF_NONE)
                toggle.get_children()[0].set_alignment(0.0, 0.5)
                toggle.connect('button-press-event', self.__double_click)
                self.__table.attach(toggle, 0, 1, 4, 5)
            for i in range(12, 0, -1):
                toggle = gtk.RadioButton(toggle, '%02i - %s' % (i, datetime.date(1900,  i, 1).strftime('%B').capitalize()))
                toggle.set_mode(False)
                toggle.set_relief(gtk.RELIEF_NONE)
                toggle.get_children()[0].set_alignment(0.0, 0.5)
                toggle.connect('button-press-event', self.__double_click)
                self.__table.attach(toggle, (i - 1) / 4, (i - 1) / 4 + 1, (i - 1) % 4, (i - 1) % 4 + 1)
            month = int(date[:2]) if self.__type == PoleUtil.HOLLERITH else date.month
            year = int(date[3:]) if self.__type == PoleUtil.HOLLERITH else date.year
            self.__table.get_children()[month - 1].set_active(True)
            self.__vbox.set_spacing(15)
            self.__vbox.pack_start(self.__table)
            self.__hbox = gtk.HBox(spacing=5)
            self.__year = gtk.SpinButton()
            self.__year_label = gtk.Label(_('Year:'))
            self.__year_label.set_alignment(1.0, 0.5)
            self.__year.get_adjustment().set_all(value=year,
                                                 lower=1,
                                                 upper=9999,
                                                 step_increment=1,
                                                 page_increment=10)
            self.__hbox.pack_start(self.__year_label, expand=True, fill=True)
            self.__hbox.pack_start(self.__year, expand=False, fill=False)
            self.__table.attach(self.__hbox, 1, 3, 4, 5)
            self.__vbox.pack_start(self.__buttons, expand=False, fill=False)
            self.__year.grab_focus()
        if self.__type in (PoleUtil.DATE, PoleUtil.DATE_TIME):
            self.__calendar = gtk.Calendar()
            self.__calendar.select_day(date.day)
            self.__calendar.select_month(date.month - 1, date.year)
            self.__calendar.connect("day-selected-double-click", self.__change_date)
            self.__vbox.pack_start(self.__calendar, expand=False, fill=False)
        if self.__type == PoleUtil.DATE:
            self.__vbox.pack_start(self.__buttons, expand=False, fill=False)
        if self.__type in (PoleUtil.TIME, PoleUtil.DATE_TIME):
            self.__vbox_time = gtk.VBox(spacing=5)
            self.__hbox = gtk.HBox()
            self.__vbox_time.pack_start(self.__hbox)
            self.__vbox_time.pack_start(self.__buttons)
            self.__vbox.pack_start(self.__vbox_time, expand=False, fill=False)
            self.add(self.__vbox)
            self.__label = gtk.Label(_('Time:'))
            self.__label1 = gtk.Label(':')
            self.__label2 = gtk.Label(':')
            self.__hour = gtk.SpinButton()
            self.__minute = gtk.SpinButton()
            self.__second = gtk.SpinButton()
            self.__label.set_alignment(1.0, 0.5)
            self.__hour.set_width_chars(2)
            self.__minute.set_width_chars(2)
            self.__second.set_width_chars(2)
            self.__hour.set_alignment(1.0)
            self.__minute.set_alignment(1.0)
            self.__second.set_alignment(1.0)
            self.__hbox.pack_start(self.__label, expand=True)
            self.__hbox.pack_start(self.__hour, expand=False)
            self.__hbox.pack_start(self.__label1, expand=False)
            self.__hbox.pack_start(self.__minute, expand=False)
            self.__hbox.pack_start(self.__label2, expand=False)
            self.__hbox.pack_start(self.__second, expand=False)
            self.__hour.get_adjustment().set_all(value=date.hour,
                                                 lower=0,
                                                 upper=23,
                                                 step_increment=1,
                                                 page_increment=5)
            self.__minute.get_adjustment().set_all(value=date.minute,
                                                   lower=0,
                                                   upper=59,
                                                   step_increment=1,
                                                   page_increment=5)
            self.__second.get_adjustment().set_all(value=date.second,
                                                   lower=0,
                                                   upper=59,
                                                   step_increment=1,
                                                   page_increment=5)
        self.__updated = False

    def run(self, position=None, center=False, transient_for=None):
        super(Calendar, self).run(self.__caller, (-1, -1), position, center, transient_for)
        return self.__updated

    def __double_click(self, *args):
        if args[1].type == gtk.gdk._2BUTTON_PRESS:
            self.__change_date()

    def __go_to_now(self, *args):
        date = datetime.datetime.now()
        if self.__type in (PoleUtil.MONTH, PoleUtil.HOLLERITH):
            self.__year.set_value(date.year)
            self.__table.get_children()[date.month].set_active(True)
            return
        if self.__type in (PoleUtil.DATE, PoleUtil.DATE_TIME):
            self.__calendar.select_day(date.day)
            self.__calendar.select_month(date.month - 1, date.year)
        if self.__type in (PoleUtil.TIME, PoleUtil.DATE_TIME):
            self.__hour.get_adjustment().set_value(date.hour)
            self.__minute.get_adjustment().set_value(date.minute)
            self.__second.get_adjustment().set_value(date.second)

    def __change_date(self, *args):
        self.__ok.grab_focus()
        if self.__type in (PoleUtil.DATE, PoleUtil.DATE_TIME):
            date = self.__calendar.get_date()
            date = datetime.datetime(date[0], date[1] + 1, date[2])
        elif self.__type in (PoleUtil.MONTH, PoleUtil.HOLLERITH):
            month = 0
            for child in self.__table.get_children()[1:]:
                month += 1
                if child.get_active():
                    break
            if self.__type == PoleUtil.HOLLERITH:
                self.__set_new_date("%02i/%04i" %
                                    (month, self.__year.get_value()))
                self.quit()
                return
            date = datetime.datetime(int(self.__year.get_value()), month, 1)
        else:
            date = datetime.datetime(1900, 1, 1)
        if self.__type in (PoleUtil.TIME, PoleUtil.DATE_TIME):
            date = date.replace(hour=int(self.__hour.get_value()),
                                minute=int(self.__minute.get_value()),
                                second=int(self.__second.get_value()))
        new_date = PoleUtil.convert_and_format(date, datetime.datetime, self.__type)[1]
        self.__updated = self.__old_date != new_date
        if self.__updated:
            self.__set_new_date(new_date)
        self.quit()

    def __key_press(self, *args):
        if args[0] == self.__cancel:
            key = gtk.keysyms.Escape
        else:
            key = args[1].keyval
        if key == gtk.keysyms.Escape:
            self.quit()
        elif key in (gtk.keysyms.KP_Enter, gtk.keysyms.Return):
            self.__change_date()


class DateButton(gtk.Button, gtk.Buildable):
    __gtype_name__ = 'DateButton'
    __gsignals__ = {
        "clicked": "override",
    }

    def __init__(self, *args):
        super(DateButton, self).__init__(*args)
        self.__type = PoleUtil.DATE
        self.updated = False
        self.__select_then_tab = False

    def do_parser_finished(self, builder):
        configs = self.get_tooltip_text()
        if configs is None or '|' not in configs:
            self.__default_date()
            return
        configs = [c.replace('0x00', '|') for c in configs.replace('\|', '0x00').split('|', 1)]
        self.set_tooltip_text(configs[0])
        self.config(configs[1])

    def config(self, configs):
        types = {'DATE': PoleUtil.DATE, 'TIME': PoleUtil.TIME, 'DATE_TIME': PoleUtil.DATE_TIME, 'MONTH': PoleUtil.MONTH, 'HOURS': PoleUtil.HOURS, 'DAYS_HOURS': PoleUtil.DAYS_HOURS, 'HOLLERITH': PoleUtil.HOLLERITH}
        if configs in types.values():
            self.__default_date()
            return
        configs = [x.strip() for x in configs.split(',')]
        for c in configs:
            if c.upper() in types:
                self.__type = types[c.upper()]
            if c.lower() == 'select_then_tab':
                self.__select_then_tab = True
        self.__default_date()

    def __default_date(self):
        # If date didn't have at least one of z number, use now
        z = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        if not self.get_label() or not sum(map(lambda x: x in z, self.get_label())):
            conv_type = self.__type if self.__type != PoleUtil.HOLLERITH else PoleUtil.MONTH
            self.set_label(PoleUtil.convert_and_format(datetime.datetime.now(), datetime.date, conv_type)[1])

    def do_clicked(self, *args, **kargs):
        old = self.get_label()
        if self.__type != PoleUtil.HOLLERITH:
            try:
                x = PoleUtil.convert_and_format(old, datetime.datetime, self.__type)[1]
            except ValueError:
                x = PoleUtil.convert_and_format(datetime.datetime.now(), datetime.datetime, self.__type)[1]
            self.set_label(x)
        changed = Calendar(self, self.__type).run()
        self.updated = (self.__type != PoleUtil.HOLLERITH and old != x) or changed
        if self.__select_then_tab:
            self.__timer = gobject.timeout_add(500, self.__emit_tab)
        # super(DateButton, self).do_clicked(self, *args, **kargs)

    def __emit_tab(self):
        gobject.source_remove(self.__timer)
        event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
        event.keyval = gtk.keysyms.Tab
        # event.string = ''
        # event.send_event = False
        # event.time = 0
        event.window = self.get_window()
        # Hardware key code
        keymap = gtk.gdk.keymap_get_default()
        keycode, group, level = keymap.get_entries_for_keyval(event.keyval)[0]
        event.hardware_keycode = keycode
        event.group = group
        event.state = level
        # Emit signal key press
        self.get_toplevel().emit('key-press-event', event)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Classe para criar grade e linha de grade
class GridRow(object):
    def __init__(self, grid, path, line, with_colors):
        self.__grid = grid
        self.__path = path
        self.__line = line
        self.__with_colors = with_colors

    def __getattribute__(self, attribute):
        if object.__getattribute__(self, '_GridRow__with_colors'):
            if attribute == 'fg':
                return self.__grid.get_model()[self.__path][-2]
            if attribute == 'bg':
                return self.__grid.get_model()[self.__path][-1]
        return object.__getattribute__(self, attribute)

    def __setattr__(self, attribute, value):
        if attribute == 'fg':
            if self.__with_colors:
                self.__grid.get_model()[self.__path][-2] = value
        elif attribute == 'bg':
            if self.__with_colors:
                self.__grid.get_model()[self.__path][-1] = value
        else:
            object.__setattr__(self, attribute, value)

    def __getitem__(self, index):
        if isinstance(index, slice):
            index = index.indices(len(self.__grid._Grid__titles) + 2 * self.__with_colors)
            return (tuple([self.__line[0][i] for i in range(*index)]), tuple([self.__line[1][i] for i in range(*index)]))
        if type(index) == str:
            if index not in self.__grid._Grid__titles:
                raise ValueError(_('Invalid or not found column name `' + index + '´.'))
            index = self.__grid._Grid__titles.index(index)
        return [self.__line[0][index], self.__line[1][index]]

    def __setitem__(self, index, value):
        model = self.__grid.get_model()
        types = self.__grid._Grid__types
        if type(index) == str:
            if index not in self.__grid._Grid__titles:
                raise ValueError(_('Invalid or not found column name `' + index + '´.'))
            index = self.__grid._Grid__titles.index(index)
        if type(index) in (int, long):
            column = self.__grid._Grid__model_pos[index]
            try:
                formated = PoleUtil.convert_and_format(value, types[index], self.__grid._Grid__decimals[index])
            except ValueError or TypeError:
                PoleLog.log_except()
                message(self.__grid, _("This value could not be converted or formatted.\n\nThis value is ignored and the previous value will not change."))
                return
            line = model[self.__path]
            if types[index] in (datetime.time, datetime.datetime):
                formated[0] = PoleUtil.convert_and_format(formated[0], float)[0]
            elif types[index] == datetime.date:
                formated[0] = PoleUtil.convert_and_format(formated[0], int)[0]
            if types[index] in (int, float, long, datetime.date, datetime.time, datetime.datetime):
                line[column], line[column + 1] = formated
            elif types[index] == bool:
                line[column] = formated[0]
            else:
                line[column] = formated[1]
        else:
            raise TypeError(_('Invalid type of column index or name `' +
                              type(index) + '´.'))

    def path(self):
        return self.__path

    def is_expanded(self):
        return self.__grid.row_expanded(self.__path)


class ComboBoxCompletion(gtk.ComboBox, gtk.Buildable):
    __gtype_name__ = 'ComboBoxCompletion'

    def __init__(self, *args, **kargs):
        super(ComboBoxCompletion, self).__init__(*args, **kargs)
        self.__completion = gtk.EntryCompletion()
        self.__completion.set_model(self.get_model())
        self.__completion.set_minimum_key_length(1)
        self.__completion.set_text_column(0)
        self.__completion.set_match_func(self.match_func)
        self.__completion.connect('match-selected', self.on_match_selected)

    def do_parser_finished(self, builder):
        self.child.set_completion(self.__completion)
        self.__completion.set_model(self.get_model())

    def set_model(self, model):
        super(ComboBoxCompletion, self).set_model(model)
        self.__completion.set_model(model)

    def match_func(self, completion, key, iter, column=0):
        key = PoleUtil.formatar(key, "Livre Mai").replace(' ', '.*')
        model = completion.get_model()
        text = PoleUtil.formatar(model.get_value(iter, column), "Livre Mai")
        return re.search(key, text)

    def on_match_selected(self, completion, model, iter):
        value = model.get_value(iter, 0)
        set_active_text(self, value)


class Editor(gtk.Entry, gtk.Buildable):
    __gtype_name__ = 'Editor'

    __gsignals__ = {
        "key-press-event": "override",
        "changed": "override",
        "focus-out-event": "override",
        "focus-in-event": "override",
    }

    def __init__(self, *args, **kargs):
        super(Editor, self).__init__(*args, **kargs)
        self.__formating = True
        self.__enter_to_tab = False
        self.__upper = False
        self.__lower = False
        self.__normalize = False
        self.__float = False
        self.__decimals = PoleUtil.locale.localeconv()['frac_digits']
        self.__int = False
        self.__num = False
        self.__old_text = ''
        self.__characters = None
        self.__max_length = -1
        self.__pole_type = None
        self.__limits = []

    def do_parser_finished(self, builder):
        configs = self.get_tooltip_text()
        if configs is None or '|' not in configs:
            return
        configs = [c.replace('0x00', '|') for c in configs.replace('\|', '0x00').split('|', 1)]
        self.set_tooltip_text(configs[0])
        self.config(configs[1])

    def config(self, configs):
        configs = [x.strip() for x in configs.split(',')]
        self.__enter_to_tab = "enter_to_tab" in [x.lower() for x in configs]
        pole_type = None
        for config in configs:
            # print config, config in PoleUtil.tipos
            if config in PoleUtil.tipos:
                pole_type = config
                break
        if pole_type:
            type_info = PoleUtil.tipos[config]
            ptype = PoleUtil.python_tipo[type_info[0]]
            mask = [m for m in type_info[5].split(' ') if len(m) > 0]
            if ptype == str:
                self.__upper = "upper" in mask
                self.__lower = "lower" in mask
                self.__normalize = "normalize" in mask
                self.__limits = [(m[0], m[1], int(m[2:])) for m in mask if '>' in m or '<' in m]
            elif ptype in [int, long]:
                self.__int = True
            elif ptype == float:
                self.__float = True
            self.__pole_type = pole_type
            self.__decimals = type_info[2]
            self.__characters = type_info[4]
            self.__max_length = type_info[1]
            if self.get_max_length() == self.__max_length:
                self.set_max_length(0)
            # self.set_width_chars(type_info[1]) # Depends on layout
            self.set_alignment(type_info[8])
        else:
            self.__upper = "upper" in configs
            self.__lower = "lower" in configs
            self.__normalize = "normalize" in configs
            self.__float = "float" in [x[:5] for x in configs]
            if self.__float:
                try:
                    self.__decimals = int([x[5:] for x in configs if x[:5] == "float"][0])
                except Exception:
                    self.__decimals = PoleUtil.locale.localeconv()['frac_digits']
            else:
                self.__decimals = 0
            self.__int = "int" in configs
            self.__num = "num" in configs
        if self.__int or self.__float or self.__num:
            self.set_alignment(1)

    def do_key_press_event(self, event):
        # print self, event
        if self.__enter_to_tab and event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
            event.keyval = gtk.keysyms.Tab
            # Hardware key code
            keymap = gtk.gdk.keymap_get_default()
            keycode, group, level = keymap.get_entries_for_keyval(event.keyval)[0]
            event.hardware_keycode = keycode
            event.group = group
            event.state = level
        else:
            # super(Editor, self).do_key_press_event(self, event)
            gtk.Entry.do_key_press_event(self, event)
            return (event.keyval in (gtk.keysyms.Right, gtk.keysyms.Left))

    def do_changed(self, *args, **kargs):
        # print "do_changed", self, args, kargs
        # print self.__formating, self.get_text(), self.has_focus()
        if self.__formating or self.get_text() == '' or not self.has_focus():
            return
        pos = self.get_position()
        text = self.get_text().decode('utf-8')
        # print text, self.__int, self.__num, self.__float
        size = len(text)
        if self.__int or self.__num:
            text = re.sub('[^0-9]', '', text)
        elif self.__float:
            decimal = PoleUtil.locale.localeconv()['decimal_point']
            text = decimal.join(re.sub('[^0-9]', '', t)
                                for t in text.split(decimal, 1))
        else:
            if self.__normalize:
                text = unicodedata.normalize('NFKD', text).encode('ascii',
                                                                  'ignore')
            if self.__upper:
                text = text.upper()
            elif self.__lower:
                text = text.lower()
            if self.__characters:
                text = ''.join([c for c in text if c in self.__characters])
        self.__formating = True
        self.set_text(text)
        # print pos, size, len(text), text
        self.set_position(pos - (size - len(text)))
        # while gtk.events_pending():
        #    gtk.main_iteration()
        self.__formating = False

    def do_focus_out_event(self, *args, **kargs):
        # print "do_focus_out_event", self, args, kargs
        # print self.get_text(), self.__int, self.__float, self.__pole_type
        if self.get_text() == '':
            # super(Editor, self).do_focus_out_event(self, *args, **kargs)
            gtk.Entry.do_focus_out_event(self, *args, **kargs)
            return
        self.__formating = True
        if self.get_max_length() == self.__max_length:
            self.set_max_length(0)
        if self.__int:
            self.set_text(cf(self.get_text(), int)[1])
        elif self.__float:
            self.set_text(cf(self.get_text(), float, self.__decimals)[1])
        elif self.__pole_type:
            self.set_text(PoleUtil.formatar(self.get_text(), self.__pole_type))
        self.__formating = False
        # super(Editor, self).do_focus_out_event(*args, **kargs)
        gtk.Entry.do_focus_out_event(self, *args, **kargs)
        self.__formating = True

    def do_focus_in_event(self, *args, **kargs):
        self.__formating = False
        self.do_changed()
        # super(Editor, self).do_focus_in_event(self, *args, **kargs)
        if self.get_max_length() == 0:
            self.set_max_length(self.__max_length)
        gtk.Entry.do_focus_in_event(self, *args, **kargs)


class Grid(gtk.TreeView, gtk.Buildable):

    __gtype_name__ = 'Grid'

    def __init__(self, *args):
        super(Grid, self).__init__(*args)
        # self.set_rules_hint(True)
        # self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

        self.__titles = []
        self.__types = []
        self.__decimals = []
        self.__editables = []
        self.__with_colors = False

        self.__structurex = False
        self.__sizes = []
        self.__formats = []
        self.__foreing_data = []

        self.__model_types = []

        self.edit_callback = None
        self.set_search_equal_func(self.search_func)
        self.connect('button-press-event', self.cell_clicked)

        self.__model_pos = []

        self.__wrap_width = 800

    def do_parser_finished(self, builder):
        configs = self.get_tooltip_text()
        if configs is None or '|' not in configs:
            return
        configs = [c.replace('0x00', '|')
                   for c in configs.replace('\|', '0x00').split('|')]
        # self.set_tooltip_text((configs[0], ' ')[configs[0] == ""])
        self.set_tooltip_text(configs[0])
        configs = [[x.strip() for x in i.split(',')] for i in configs[1:]]
        if configs[0][0].strip()[:10] == 'wrap-width':
            self.__wrap_width = int(configs[0][0].split('=')[1].strip())
            configs = configs[1:]
        titles = []
        types = []
        decimals = []
        editables = []
        with_colors = False
        sizes = []
        formats = []
        for column in configs:
            if len(column) > 4:
                raise ValueError(_("Invalid values column format, expected max of 4 values: name, type[, decimal][,edit]."))
            if len(column) == 1 and column[0] == 'color':
                with_colors = True
                continue
            if len(column) < 2 or len(column) > 4:
                raise ValueError(_('Invalid column parameters. Expected color or title,type[,decimals][,edit].'))
            titles.append(column[0])
            if column[1] == 'bool':
                types.append(bool)
            elif column[1] == 'int':
                types.append(int)
            elif column[1] == 'long':
                types.append(long)
            elif column[1] == 'float':
                types.append(float)
            elif column[1] == 'str':
                types.append(str)
            elif column[1] == 'date':
                types.append(datetime.date)
                decimals.append(PoleUtil.DATE)
            elif column[1] == 'time':
                types.append(datetime.time)
                decimals.append(PoleUtil.TIME)
            elif column[1] == 'datetime':
                types.append(datetime.datetime)
                if len(column) > 2:
                    if column[2].isdigit():
                        decimals.append(int(column[2]))
                    elif column[2] == 'DATE':
                        decimals.append(PoleUtil.DATE)
                    elif column[2] == 'TIME':
                        decimals.append(PoleUtil.TIME)
                    elif column[2] == 'MONTH':
                        decimals.append(PoleUtil.MONTH)
                    elif column[2] == 'HOURS':
                        decimals.append(PoleUtil.HOURS)
                    elif column[2] == 'DAYS_HOURS':
                        decimals.append(PoleUtil.DAYS_HOURS)
                    else:
                        decimals.append(PoleUtil.DATE_TIME)
                else:
                    decimals.append(PoleUtil.DATE_TIME)
            elif column[1] == 'month':
                types.append(datetime.date)
                decimals.append(PoleUtil.MONTH)
            elif column[1] == 'hours':
                types.append(datetime.timedelta)
                if len(column) > 2:
                    if column[2].isdigit():
                        decimals.append(int(column[2]))
                    elif column[2] in ('DATE_TIME', 'TIME', 'DATE'):
                        decimals.append(PoleUtil.TIME)
                    else:
                        decimals.append(PoleUtil.HOURS)
                else:
                    decimals.append(PoleUtil.HOURS)
            elif column[1] in PoleUtil.tipos:
                type_info = PoleUtil.tipos[column[1]]
                types.append(PoleUtil.python_tipo[type_info[0]])
                decimals.append(type_info[2])
                sizes.append(type_info[1])
                formats.append(column[1])
            else:
                raise TypeError(_('Invalid type `%s´. Expected int, long, bool, float, str, datetime, date, time, month or hours.') % (column[1],))
            if column[1] not in PoleUtil.tipos:
                sizes.append(None)
                formats.append(None)
            c = 2

            if len(column) > 2:
                if column[2].isdigit():
                    if column[1] not in ('date', 'time', 'datetime', 'month', 'hours') + tuple(PoleUtil.tipos):
                        decimals.append(int(column[2]))
                elif column[2] == 'edit':
                    if column[1] not in ('date', 'time', 'datetime', 'month', 'hours') + tuple(PoleUtil.tipos):
                        decimals.append(PoleUtil.locale.localeconv()['frac_digits'])
                    editables.append(True)
                elif column[2] not in ('DATE', 'TIME', 'DATE_TIME', 'MONTH', 'HOURS', 'DAYS_HOURS'):
                    raise ValueError(_("Invalid value for decimals ou editable `%s´. Expected digits, 'DATE', 'TIME', 'DATE_TIME', 'MONTH', 'HOURS' or 'DAYS_HOURS' for decimals or 'edit' for editable.") % (column[2],))
                if len(column) == 4:
                    if column[3] == 'edit':
                        if column[2] == 'edit':
                            raise ValueError(_('Expected just one `edit´ for editable.'))
                        editables.append(True)
                    else:
                        raise ValueError(_('Invalid value for editable `%s´. Expected `edit´ for editable, just one.') % (column[3],))
                elif column[2] != 'edit':
                    editables.append(False)
            else:
                if column[1] not in ('date', 'time', 'datetime', 'month', 'hours') + tuple(PoleUtil.tipos):
                    decimals.append(PoleUtil.locale.localeconv()['frac_digits'])
                editables.append(False)
        self.structure(titles, types, decimals, editables, with_colors, sizes, formats)

    def structure(self, titles, types, decimals=None, editables=None, with_colors=False, sizes=None, formats=None, foreing_data=None):
        if not decimals:
            decimals = [PoleUtil.locale.localeconv()['frac_digits']] * len(titles)
        if not editables:
            editables = [False] * len(titles)
        if not len(titles) == len(types) == len(decimals) == len(editables):
            raise ValueError('length of lists titles, types decimals and editables must be iquals!')
        self.__titles = titles
        self.__types = types
        self.__decimals = decimals
        self.__editables = editables
        self.__with_colors = with_colors

        vazio = [None] * len(types)
        self.__sizes = sizes if sizes else vazio
        self.__formats = formats if formats else vazio
        self.__foreing_data = foreing_data if foreing_data else vazio
        self.__structurex = bool(sizes or formats or foreing_data)

        for column in self.get_columns():
            self.remove_column(column)
            column.destroy()
        # Creating a model for locale support by convert_and_format
        self.__model_types = []
        for t in types:
            if t == datetime.date:
                self.__model_types.append(int)
            elif t in (datetime.time, datetime.datetime, datetime.timedelta):
                self.__model_types.append(float)
            else:
                self.__model_types.append(t)
            if t in (int, long, float, datetime.date, datetime.time, datetime.datetime, datetime.timedelta):
                self.__model_types.append(str)
        if with_colors:
            self.__model_types.append(str)  # foreground color
            self.__model_types.append(str)  # background color
        model = self.get_model()
        if model is not None:
            self.set_model(None)
            model.clear()
            del model
        model = gtk.TreeStore(*self.__model_types)
        self.set_model(model)
        # Creating visual columns
        model_pos = 0
        self.__model_pos = []
        for title, t, editable in zip(titles, types, editables):
            self.__model_pos.append(model_pos)
            l = gtk.Label(title.decode('string_escape'))
            l.show()
            column = gtk.TreeViewColumn()
            column.set_widget(l)
            column.set_resizable(True)
            self.append_column(column)
            if t == bool:
                cell = gtk.CellRendererToggle()
                cell.set_property('activatable', editable)
                cell.connect('toggled', self.__editable_callback, len(self.__model_pos) - 1)
                cell.set_property("xalign", .5)
                column.pack_start(cell)
                column.set_property("alignment", .5)
                column.add_attribute(cell, "active", model_pos)
            else:
                cell = gtk.CellRendererText()
                cell.set_property('editable', editable)
                if self.__wrap_width:
                    cell.set_property('wrap-width', self.__wrap_width)
                    cell.set_property('wrap-mode', pango.WRAP_WORD)
                cell.connect('edited', self.__editable_callback, len(self.__model_pos) - 1)
                cell.connect('editing-started', self.__start_editing_callback, len(self.__model_pos) - 1)
                column.pack_start(cell)
                column.add_attribute(cell, "text", model_pos + (t in (int, long, float, datetime.date, datetime.time, datetime.datetime)))
            column.set_sort_column_id(model_pos)
            if t in (int, long, float):
                cell.set_property("xalign", 1.)
                column.set_property("alignment", 1.)
                model_pos += 1
            elif t in (datetime.date, datetime.time, datetime.datetime):
                cell.set_property("xalign", .5)
                column.set_property("alignment", .5)
                model_pos += 1
            # Colors column
            if with_colors:
                if t != bool:
                    column.add_attribute(cell, "foreground", len(self.__model_types) - 2)
                column.add_attribute(cell, "cell-background", len(self.__model_types) - 1)
            model_pos += 1
        # Sentinel column
        column = gtk.TreeViewColumn("")
        cell = gtk.CellRendererText()
        column.pack_start(cell)
        if with_colors:
            if t != bool:
                column.add_attribute(cell, "foreground", len(self.__model_types) - 2)
            column.add_attribute(cell, "cell-background", len(self.__model_types) - 1)
        self.append_column(column)

    def get_structure(self):
        return (self.__titles, self.__types, self.__decimals, self.__editables, self.__with_colors, self.__sizes, self.__formats, self.__foreing_data)

    def __editable_callback(self, renderer, path, *args):
        if isinstance(renderer, gtk.CellRendererToggle):
            column = args[0]
            original = self[path][column][0]
            result = not original
        else:
            result = args[0]
            column = args[1]
            original = self[path][column][0]
        if self.edit_callback is not None:
            result = self.edit_callback(result, self, path, column, self.__titles[:], self.__types[:], self.__decimals[:], self.__with_colors)
        if result is not None:
            self[path][column] = result
        return False

    def __finish_editing(self, editor, event, popup):
        key = event.keyval
        if key == gtk.keysyms.Escape:
            editor.props.text = self.__old_editing_text
            popup.quit()
        elif key in (gtk.keysyms.KP_Enter, gtk.keysyms.Return):
            popup.quit()

    def __start_editing_callback(self, renderer, editable, path, column):
        # print '__start_editing_callback'
        # print 'renderer:', renderer
        # print 'editable:', editable
        # print 'path:', path
        # print 'column:', column
        # print 'gtk.Entry:', isinstance(editable, gtk.Entry)
        # print 'gtk.ComboBox:', isinstance(editable, gtk.ComboBox)
        # print '-' * 100

        x, y = self.get_bin_window().get_origin()
        area = self.get_cell_area(path, self.get_column(column))
        size = (area[2], area[3])
        self.__old_editing_text = new = editable.props.text
        if self.__types[column] in (datetime.date, datetime.datetime, datetime.time):
            position = (x + area[0], y + area[1] + area[3])
            c = Calendar(editable, self.__decimals[column])
            if c.run(position, transient_for=self):
                new = cf(editable.props.text, self.__types[column], self.__decimals[column])[1]
        else:
            position = (x + area[0], y + area[1])
            p = PopupWindow()
            e = Editor()
            e.connect('key-press-event', self.__finish_editing, p)
            tx = self.__formats[column]
            if tx:
                e.config(tx)
                # e.set_max_length(self.__sizes[column])
            elif self.__types[column] in (int, long):
                e.config("int")
            elif self.__types[column] == float:
                e.config("float" + str(self.__decimals[column]))
            # else:
            #    e.config("upper,normalize")
            e.set_has_frame(False)
            e.show()
            p.add(e)
            e.props.text = self.__old_editing_text

            # Out click do cancel
            # if p.run(self, size, position):
            #    new = cf(e.props.text, self.__types[column], self.__decimals[column])[1]

            # Out click do not cancel
            p.run(self, size, position)
            if tx:
                new = cf(e.props.text, tx)[1]
            else:
                new = cf(e.props.text, self.__types[column], self.__decimals[column])[1]

        # print new, old, new != old
        if new != self.__old_editing_text:
            # print 'editing_done'
            editable.set_text(new)
            editable.editing_done()
        editable.remove_widget()
        editable.destroy()
        return False

    def clear(self):
        model = self.get_model()
        if model:
            model.clear()
            return
        raise ValueError(_('No columns structure defined.'))

    def add_data(self, data, to_path_or_iter=None, with_child=False):
        if data in (None, [], [[]], ''):
            return to_path_or_iter
        model = self.get_model()
        if not model:
            raise ValueError(_('No columns structure defined.'))
        if to_path_or_iter is not None:
            if type(to_path_or_iter) in (str, int, long):
                iter = model.get_iter_from_string(str(to_path_or_iter))
            elif type(to_path_or_iter) in (tuple, list):
                iter = model.get_iter(tuple(to_path_or_iter))
            elif isinstance(to_path_or_iter, gtk.TreeIter):
                iter = to_path_or_iter
            else:
                raise TypeError(_('Type `' + str(type(to_path_or_iter)).split("'")[1] + '´of path is not valid. Expected str, int, long, tuple, list (path) or gtk.TreeIter.'))
            if not model.iter_is_valid(iter):
                raise ValueError(_('Path or iter is not valid for this model.'))
        else:
            iter = None
        # Inserting a line
        if type(data) in (tuple, list) and len(data) > 0 and type(data[0]) not in (tuple, list):
            data = [data]
        # Inserting a value
        if type(data) not in (tuple, list) or (len(data) > 0 and type(data[0]) not in (tuple, list)):
            data = [[data]]
        error = False
        last_iter = iter
        if with_child:
            null_line = [0] * len(self.__model_types)
        for register in data:
            formated = []
            for t, tx, decimals, field in zip(self.__types, self.__formats, self.__decimals, register):
                if t in (int, long, float, datetime.date, datetime.time, datetime.datetime):
                    try:
                        f = PoleUtil.convert_and_format(field, tx if tx else t, decimals)
                        if t in (datetime.time, datetime.datetime):
                            f[0] = PoleUtil.convert_and_format(f[0], float)[0]
                        elif t == datetime.date:
                            f[0] = PoleUtil.convert_and_format(f[0], int)[0]
                        formated += f
                    except ValueError or TypeError:
                        PoleLog.log_except()
                        if t in (int, long, float):
                            formated += [t(0), field]
                        else:
                            formated += [t(1900, 1, 1), field]
                        error = True
                elif t == bool:
                    try:
                        formated.append(PoleUtil.convert_and_format(field, tx if tx else t)[0])
                    except ValueError or TypeError:
                        PoleLog.log_except()
                        formated.append(False)
                        error = True
                elif t == str and type(field) in (datetime.date, datetime.datetime):
                    try:
                        formated.append(PoleUtil.convert_and_format(field, tx if tx else t)[1])
                    except (ValueError, TypeError):
                        PoleLog.log_except()
                        formated.append(_('Error!'))
                        error = True
                else:
                    formated.append(PoleUtil.convert_and_format(field, tx if tx else t)[1])
            if self.__with_colors:
                formated += register[-2:]

            # self.freeze_child_notify()
            # self.set_model(None)

            last_iter = model.append(iter, formated)
            if with_child:
                model.append(last_iter, null_line)
            # self.set_model(model)
            # self.thaw_child_notify()

        if error:
            message(self, _("Some values could not be converted or formatted!\n\nThey will be displayed as they are and evalueted by zero (0 ou 0.0) or false."))
        if isinstance(last_iter, gtk.TreeIter):
            return model.get_path(last_iter)
        return last_iter

    def update_line(self, path_or_iter, new_values):
        model = self.get_model()
        if not model:
            raise ValueError(_('No columns structure defined.'))
        try:
            if type(path_or_iter) in (str, int, long):
                iter = model.get_iter_from_string(str(path_or_iter))
            elif type(path_or_iter) in (tuple, list):
                iter = model.get_iter(tuple(path_or_iter))
            elif isinstance(path_or_iter, gtk.TreeIter):
                iter = path_or_iter
            else:
                raise TypeError(_('Type `' + str(type(path_or_iter)).split("'")[1] + '´of path is not valid. Expected str, int, long, tuple, list (path) or gtk.TreeIter.'))
            if not model.iter_is_valid(iter):
                raise ValueError(_('Path or iter is not valid.'))
        except Exception:
            raise ValueError(_('Path or iter is not valid.'))
        # Updating a value
        if type(new_values) not in (tuple, list):
            new_values = [new_values]
        error = False
        formated = []
        for t, tx, decimals, field in zip(self.__types, self.__formats, self.__decimals, new_values):
            if t in (int, long, float, datetime.datetime, datetime.date, datetime.time):
                try:
                    formated += PoleUtil.convert_and_format(field, t, decimals)
                except ValueError or TypeError:
                    PoleLog.log_except()
                    formated += [t(0), field]
                    error = True
            elif t == bool:
                try:
                    formated.append(PoleUtil.convert_and_format(field, tx if tx else t)[0])
                except ValueError or TypeError:
                    PoleLog.log_except()
                    formated.append(False)
                    error = True
            elif t == str and type(field) in (datetime.date, datetime.datetime):
                try:
                    formated.append(PoleUtil.convert_and_format(field, tx if tx else t)[1])
                except (ValueError, TypeError):
                    PoleLog.log_except()
                    formated.append(_('Error!'))
                    error = True
            else:
                formated.append(PoleUtil.convert_and_format(field, tx if tx else t)[1])
        if self.__with_colors:
            formated += new_values[-2:]
        model[path_or_iter] = formated
        if error:
            message(self, _("Some values could not be converted or formatted!\n\nThey will be displayed as they are and evalueted by zero (0 ou 0.0) or false."))

    def __get_line(self, path, bool_to_str=False):
        model_line = self.get_model()[path]
        values = []
        formateds = []
        col = 0
        types = self.__types[:]
        if self.__with_colors:
            types += (str, str)
        for t in types:
            if t in (datetime.datetime, datetime.date, datetime.time):
                values.append(PoleUtil.convert_and_format(model_line[col], t)[0])
            else:
                values.append(model_line[col])
            if t in (int, long, float, datetime.datetime, datetime.date, datetime.time):
                formateds.append(model_line[col+1])
                col += 2
            elif t is bool and bool_to_str:
                formateds.append(PoleUtil.convert_and_format(model_line[col], t)[1])
                col += 1
            else:
                formateds.append(model_line[col])
                col += 1
        if self.__with_colors:
            values += [model_line[-2], model_line[-1]]
            formateds += [model_line[-2], model_line[-1]]
        return [values, formateds]

    def __getitem__(self, path):
        if type(path) == slice:
            model = self.get_model()
            index = path.indices(len(model))
            return tuple([GridRow(self, i, self.__get_line(i), self.__with_colors) for i in range(*index)])
        if type(path) in (tuple, list) and type(path[0]) in (tuple, list):
            return tuple([GridRow(self, i, self.__get_line(i), self.__with_colors) for i in path])
        return GridRow(self, path, self.__get_line(path), self.__with_colors)
        # Antes era assim
        # if type(path) == slice:
        #    model = self.get_model()
        #    index = path.indices(len(model))
        #    values = []
        #    formateds = []
        #    for i in range(*index):
        #        line = self.__get_line(i)
        #        values.append(line[0])
        #        formateds.append(line[1])
        #    return (tuple(values), tuple(formateds))
        # return self.__get_line(path)

    def __setitem__(self, item, value):
        self.update_line(item, value)

    def remove(self, path_iter):
        if isinstance(path_iter, tuple):
            path_iter = self.get_model().get_iter(path_iter)
        elif not isinstance(path_iter, gtk.TreeIter):
            path_iter = self.get_model().get_iter_from_string(str(path_iter))
        return self.get_model().remove(path_iter)

    def is_expanded(self, path_iter):
        if not isinstance(path_iter, (tuple, gtk.TreeIter)):
            path_iter = self.get_model().get_iter_from_string(str(path_iter))
        if isinstance(path_iter, gtk.TreeIter):
            path_iter = self.get_model().get_path(path_iter)
        return self.row_expanded(path_iter)

    def __export_csv_children(self, children, csv, cols, only_expanded_rows):
        for line in children:
            fields = self.__get_line(line.iter, bool_to_str=True)[1][:cols]
            csv.append('\t'.join(('' if x is None else x) for x in fields))
            if not only_expanded_rows or self.row_expanded(line.path):
                self.__export_csv_children(line.iterchildren(), csv,
                                           cols, only_expanded_rows)

    def export_csv(self, filename=None, only_expanded_rows=True):
        csv = ['\t'.join(self.__titles)]
        cols = len(self.__titles)
        model = self.get_model()
        self.__export_csv_children(model, csv, cols, only_expanded_rows)
        csv = '\n'.join(csv) + '\n'
        if filename:
            open(filename, 'w').write(csv)
        else:
            gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD).set_text(csv)

    def __data_matrix_children(self, children, data, cols, only_expanded_rows):
        for line in children:
            data.append(self.__get_line(line.iter)[0][:cols])
            if not only_expanded_rows or self.row_expanded(line.path):
                self.__data_matrix_children(line.iterchildren(), data,
                                            cols, only_expanded_rows)

    def data_matrix(self, only_expanded_rows=True):
        data = []
        cols = len(self.__titles)
        model = self.get_model()
        self.__data_matrix_children(model, data, cols, only_expanded_rows)
        return data

    def wrap_width(self, width):
        self.__wrap_width = width

    def live_load(self, cursor, clean=True, lines=50, parent_lock=None,
                  to_path_or_iter=None, with_child=False):
        if clean:
            self.clear()
        records = True
        pos = 0
        if parent_lock and not isinstance(cursor, (tuple, list)):
            cursor = cursor.fetchall()
        total = len(cursor) if isinstance(cursor, (tuple, list)) else 0
        if parent_lock:
            progress = Processing(parent_lock, _("Loading lines..."),
                                  lines, total, True)
        while records:
            if isinstance(cursor, (tuple, list)):
                self.add_data(cursor[pos:pos + lines],
                              to_path_or_iter=to_path_or_iter,
                              with_child=with_child)
                pos += lines
                records = pos < total
            else:
                records = cursor.fetchmany(lines)
                self.add_data(records,
                              to_path_or_iter=to_path_or_iter,
                              with_child=with_child)
            while gtk.events_pending():
                gtk.main_iteration()
            if parent_lock:
                if not progress.pulse():
                    break
        if parent_lock:
            progress.close()

    def selected(self):
        return self.get_selection().get_selected()[1]

    def selected_rows(self):
        return self.get_selection().get_selected_rows()[1]

    def select(self, line_or_column, column_value=None):
        # selection = self.get_selection()
        if column_value:
            for l in self[:]:
                if l[line_or_column][0] == column_value:
                    self.set_cursor(l.path())
        else:
            if isinstance(line_or_column, gtk.TreeIter):
                line_or_column = self.get_model().get_path(line_or_column)
            self.set_cursor(line_or_column)

    def set_search_column(self, column):
        if isinstance(column, (str, unicode)):
            if column not in self.__titles:
                raise ValueError(_('Invalid or not found column name `' + column + '´.'))
            column = self.__titles.index(column)
        if isinstance(column, (int, long)):
            t = self.__types[column]
            column = self.__model_pos[column]
            if t not in (int, long, float, str, unicode, bool):
                column += 1
            super(Grid, self).set_search_column(column)
        else:
            raise ValueError(_('Invalid or not found column name or number `' + str(column) + '´.'))

    def search_func(self, model, column, key, iter):
        value = model[iter][column]
        if isinstance(value, bool):
            if not key:
                return True
            if key[0].upper() in (_('Y'), 'V', '1'):
                return not value
            if key[0].upper() in (_('N'), ' ', '0'):
                return value
            return True
        elif isinstance(value, (int, long)):
            value = str(value)
            key = re.sub('[^0-9]', '', key)
        elif isinstance(value, float):
            value = str(value)
            decimal = PoleUtil.locale.localeconv()['decimal_point']
            if decimal in key:
                key = '.'.join(re.sub('[^0-9]', '', k)
                               for k in key.split(decimal, 1))
            else:
                key = re.sub('[^0-9]', '', key)
        else:
            value = PoleUtil.normalize(value).lower()
            key = PoleUtil.normalize(key).lower()
        # return False when match, them I use "not in"
        return key not in value

    def cell_clicked(self, widget, event):
        pos = self.get_path_at_pos(int(event.x), int(event.y))
        if pos:
            column = self.get_columns().index(pos[1])
            self.set_search_column(column)


class Processing(gtk.Window):
    def __init__(self, parent, title, step=None,
                 finish=None, stop_button=False):
        self.update_ui()
        super(Processing, self).__init__()
        self.set_title(title)
        self.__bar = gtk.ProgressBar()

        if stop_button:
            hbox = gtk.HBox()
            hbox.pack_start(self.__bar, expand=True, fill=True)
            button = gtk.Button(stock='gtk-stop')
            button.child.child.get_children()[0].show()
            hbox.pack_end(button, expand=False, fill=False)
            button.connect('clicked', self.stop_press)
            self.add(hbox)
        else:
            self.add(self.__bar)

        self.set_transient_for(parent.get_toplevel())
        self.set_modal(True)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_deletable(False)
        self.set_size_request(400, -1)

        self.__step = float(step)/finish if step and finish else 0
        if self.__step:
            self.__bar.set_text(formatar(0, "Porcentagem 2"))

        self.__stop = False

        self.show_all()
        self.update_ui()

    def stop_press(self, args):
        self.__stop = True

    def update_ui(self):
        while gtk.events_pending():
            gtk.main_iteration()

    def pulse(self):
        if self.__step:
            new_frac = self.__bar.get_fraction() + self.__step
            if new_frac > 0.999:
                new_frac = 1.00
            self.__bar.set_fraction(new_frac)
            self.__bar.set_text(formatar(new_frac*100, "Porcentagem 2"))
        else:
            self.__bar.pulse()
        self.update_ui()
        return not self.__stop

    def close(self):
        self.destroy()
        self.update_ui()


def load_module(parent_project, parent_main_window, module_name, title, main_window_name, data=None):
    if parent_main_window:
        parent_main_window.hide()
    loop = glib.MainLoop()
    module = importlib.import_module(module_name)
    if data is None:
        data = []
    if isinstance(parent_main_window, VirtualWidget):
        try:
            parent_main_window = parent_main_window.widget
        except Exception:
            PoleLog.log_except()
    if not isinstance(parent_main_window, gtk.Window):
        PoleLog.log(_('Error: Parent project has no window.'))
        parent_main_window = None
    project = module.Project(parent_project, loop, data)
    try:
        main_window = project.interface.get_object(main_window_name)
    except Exception:
        PoleLog.log_except()
    if not isinstance(main_window, gtk.Window):
        PoleLog.log(_('Error: Module has no window.'))
        main_window = None
    else:
        if parent_main_window is not None:
            main_window.set_transient_for(parent_main_window)
            main_window.set_modal(True)
            main_window.set_title(title + " - " + parent_main_window.get_title())
            main_window.set_icon(parent_main_window.get_icon())
        else:
            main_window.set_title(title)
        main_window.show()
        main_window.present()
    loop.run()
    if main_window:
        main_window.destroy()
        del main_window
    del project
    del module
    if module_name in sys.modules:
        del(sys.modules[module_name])
    if parent_main_window is not None:
        parent_main_window.show()
        parent_main_window.present()
    return data

# Replace GTK classes in XML Glade by PoleGTK classes where propertie
# name start with third element in (GtkClass, PoleGtkClass, start of name)
NEW_CLASSES = (
    ('GtkTreeView', 'Grid', 'gr_'),
    ('GtkEntry', 'Editor', 'ed_'),
    ('GtkWindow', 'PopupWindow', 'popup_'),
    ('GtkButton', 'DateButton', 'dt_'),
    ('GtkComboBox', 'ComboBoxCompletion', 'cc_'),
)


def build_interface(xml_file_or_xml_string=None):
    # Verifying type of xml_file_or_xml_string
    if type(xml_file_or_xml_string) != str:
        raise TypeError(_('Invalid argument'
                          ' "xml_file_or_xml_string" of type `%s´. Expected'
                          ' str.') % (type(xml_file_or_xml_string).__name__,))
    if xml_file_or_xml_string[:6] == '<?xml ':
        xml = xml_file_or_xml_string
    else:
        xml = open(xml_file_or_xml_string).read()
    # Verifying if is xml
    if xml[:6] != '<?xml ':
        raise TypeError(_('Invalid content. Expected XML data.'))
    ui = gtk.Builder()
    # Replacing Gtk classes by Pole classes
    for gtk_class, pole_class, start_of_name in NEW_CLASSES:
        xml = xml.replace('<object class="' + gtk_class + '" id="' + start_of_name,
                          '<object class="' + pole_class + '" id="' + start_of_name)
    # Solving troble with can_focus false
    dont_have_can_focus = ('ListStore', 'Adjustment', 'TextBuffer', 'Action', 'TreeViewColumn', 'CellRendererPixbuf', 'CellRendererText')
    pos = xml.find('<object class="')
    while pos != -1:
        have_can_focus = True
        for gtkclass in dont_have_can_focus:
            if xml[pos + 18:pos + 18 + len(gtkclass)] == gtkclass:
                have_can_focus = False
                break
        if have_can_focus:
            pos = xml.find('>', pos) + 1
            xml = xml[:pos] + '<property name="can_focus">False</property>' + xml[pos:]
        pos = xml.find('<object class="', pos + 70)
    # Solving problem with null to gchararray convertion in columns values
    pos = xml.find('<col ')
    while pos != -1:
        pos = xml.find('>', pos + 5)
        if xml[pos - 1] == '/':
            xml = xml[:pos - 1] + '></col>' + xml[pos + 1:]
        pos = xml.find('<col ', pos + 5)
    # Add XML to interface
    ui.add_from_string(xml)
    return ui


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
# Classe que intermedia um widget do GTK+ para facilitar acesso a consultar e
#     alterar valores de propriedades dos widgets, tal como as propriedades das
#     classes em Python, se comportando como um widget virtual. Dessa forma, não
#     precisa usar as funções GTK widget.set_propriedade(valor) ou
#     widget.get_propriedade(), basta usar widget.propriedade = valor ou
#     widget.propriedade, respectivamente. Para obter o próprio widget,
#     use widget.widget
class VirtualWidget(object):
    def __init__(self, widget):
        object.__setattr__(self, "widget", widget)

    def __getattribute__(self, attr):
        if attr == "widget":
            return object.__getattribute__(self, "widget")
        if attr == "__class__":
            return VirtualWidget
        try:
            obj = object.__getattribute__(self, "widget")
            return object.__getattribute__(obj, attr)
        except:
            try:
                return object.__getattribute__(obj, "get_" + attr)()
            except:
                return object.__getattribute__(obj, attr)

    def __setattr__(self, attr, value):
        try:
            obj = object.__getattribute__(self, "widget")
            object.__getattribute__(obj, attr)
            obj.__setattr__(attr, value)
        except:
            try:
                func = object.__getattribute__(obj, "set_" + attr)
                if isinstance(value, (list, tuple)):
                    func(*value)
                else:
                    func(value)
            except:
                object.__setattr__(obj, attr, value)

    def __getitem__(self, index):
        return object.__getattribute__(self, "widget")[index]

    def __setitem__(self, index, value):
        object.__getattribute__(self, "widget")[index] = value



class Project(object):
    def __init__(self, ui, parent=None, loop=None, data=None):
        self.consulteds_attrs = {}
        if loop is None:
            self.quit = gtk.main_quit
        else:
            self.quit = loop.quit
        self.data = data
        self.parent = parent
        self.interface = build_interface(ui)
        self.interface.connect_signals(self)
        # Criar uma coluna de dados para os combos, por padrão a coluna 0
        # Comente ou altere para a coluna desejada
        for combo in [x for x in self.interface.get_objects()
                      if isinstance(x, gtk.ComboBox)]:
            if not combo.get_has_entry():
                celula = gtk.CellRendererText()
                combo.pack_start(celula, False)
                combo.add_attribute(celula, "text", 0)
            elif combo.get_entry_text_column() == -1:
                combo.set_entry_text_column(0)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Função chamada toda vez que se requer informações de algum
    #     attribute/membro da classe. Aqui interceptamos verificando se já foi
    #     este consultado. Se não foi consultado ainda, procura este nome
    #     dentre os nomes de widgets do Glade. A busca retorna None se não for
    #     nome de um widget ou a instância do widget correspondente ao nome
    #     procurado. Este resultado fica guardado em um dicionário como um
    #     widget virtual, onde o nome do atribuito corresponderá a None ou à
    #     instância do widget virtual. No caso de já ter sido consultado, faz a
    #     procura deste no dicionário, onde se for None, continua com a busca
    #     do attribute normalmente, mas se não for None, isto é, será uma
    #     instância de um widget virtual correspondente, retorna esta.
    def __getattribute__(self, attribute):
        if attribute in object.__getattribute__(self, "consulteds_attrs"):
            if object.__getattribute__(self, "consulteds_attrs")[attribute]:
                return object.__getattribute__(self,
                                               "consulteds_attrs")[attribute]
            return object.__getattribute__(self, attribute)
        widget = object.__getattribute__(self,
                                         "interface").get_object(attribute)
        if widget:
            widget = VirtualWidget(widget)
            object.__getattribute__(self,
                                    "consulteds_attrs")[attribute] = widget
            return widget
        else:
            object.__getattribute__(self,
                                    "consulteds_attrs")[attribute] = None
        return object.__getattribute__(self, attribute)


def try_function(f):
    def action(project, *args, **kwargs):
        try:
            result = f(project, *args, **kwargs)
            return result
        except Exception:
            PoleLog.log_except()
            show_exception(project, args)
            return None
    return action


def read_text(textview, format=True):
    buffer = textview.get_buffer()
    text = strip(buffer.get_text(*buffer.get_bounds()))
    text = re.sub('[\t\r\f\v]', ' ', text)

    if format:
        text = formatar(text, 'Nome Mai')

    return text


def write_text(text, textview, format=True):
    if format:
        text = formatar(text, 'Nome Mai')

    text = re.sub('[\t\r\f\v]', ' ', text)

    buffer = textview.get_buffer()
    buffer.set_text(strip(text))


def set_active_text(combo, text, column=0):
    model = combo.get_model()
    for index, line in enumerate(model):
        if line[column] == text:
            combo.set_active(index)
            return
    combo.set_active(-1)


def get_active_text(combo, column=0):
    index = combo.get_active()
    model = combo.get_model()
    return model[index][column]


def load_store(combo, cursor, active=True):
    model = combo.get_model()
    model.clear()
    for row in cursor:
        model.append(row)
    if active:
        combo.set_active(0)


def hide_window(widget):
    if widget.is_toplevel():
        return widget.hide_on_delete()
    else:
        toplevel = widget.get_toplevel()
        toplevel.hide()


if __name__ == '__main__':
    teste_ui = """<?xml version="1.0"?>
<interface>
  <requires lib="gtk+" version="2.16"/>
  <!-- interface-naming-policy project-wide -->
  <object class="GtkWindow" id="window1">
    <property name="visible">True</property>
    <property name="default_width">440</property>
    <property name="default_height">250</property>
    <signal name="delete-event" handler="quit"/>
    <child>
      <object class="GtkVBox" id="vbox1">
        <property name="visible">True</property>
        <child>
          <object class="GtkTreeView" id="gr_treeview1">
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="tooltip_text" translatable="yes">Grade de Teste
|Código,int
|Descrição,str
|Valor,float,4,edit
|Fracionável,bool,edit
|Mais uma coluna,int
|Data,datetime,DATE
|Hora,datetime,TIME,edit
|Data e Hora,datetime,DATE_TIME,edit
|Mês,datetime,MONTH,edit
|Horas,datetime,HOURS,edit
|Dias e Horas,datetime,DAYS_HOURS,edit
|Dias e Horas,datetime,DATE_TIME,edit
|Valor2,float,edit
|color
</property>
          </object>
          <packing>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
          <object class="GtkLabel" id="label1">
            <property name="label">Teste</property>
            <property name="visible">True</property>
          </object>
          <packing>
            <property name="position">10</property>
          </packing>
        </child>
        <child>
          <object class="GtkButton" id="button1">
            <property name="label" translatable="yes">button</property>
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="receives_default">True</property>
            <signal name="clicked" handler="click"/>
          </object>
          <packing>
            <property name="position">1</property>
          </packing>
        </child>
        <child>
          <object class="GtkButton" id="button2">
            <property name="label" translatable="yes">Update</property>
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="receives_default">True</property>
            <signal name="clicked" handler="update_click"/>
          </object>
          <packing>
            <property name="position">2</property>
          </packing>
        </child>
        <child>
          <object class="GtkHBox" id="hbox1">
            <property name="visible">True</property>
            <child>
              <object class="GtkButton" id="button3">
                <property name="label" translatable="yes">08/2011</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <signal name="clicked" handler="calendar"/>
              </object>
              <packing>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="button4">
                <property name="label" translatable="yes">14/08/1978</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <signal name="clicked" handler="calendar"/>
              </object>
              <packing>
                <property name="position">1</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="button5">
                <property name="label" translatable="yes">14/08/1978 09:35:42</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <signal name="clicked" handler="calendar"/>
              </object>
              <packing>
                <property name="position">2</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="button6">
                <property name="label" translatable="yes">09:35:42</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <signal name="clicked" handler="calendar"/>
              </object>
              <packing>
                <property name="position">3</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="bt_popup">
                <property name="label" translatable="yes">Popup</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <signal name="clicked" handler="calendar"/>
              </object>
              <packing>
                <property name="position">4</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="dt_teste">
                <property name="label" translatable="yes">010101</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <signal name="clicked" handler="calendar"/>
                <property name="tooltip_text" translatable="yes">Teste do botão de data
|MONTH</property>
              </object>
              <packing>
                <property name="position">5</property>
              </packing>
            </child>
            <child>
              <object class="GtkComboBox" id="cc_teste">
                <property name="visible">True</property>
                <property name="model">liststore1</property>
                <property name="wrap_width">1</property>
                <property name="has_entry">True</property>
                <property name="entry_text_column">0</property>
              </object>
              <packing>
                <property name="position">6</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="position">3</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
  <object class="GtkListStore" id="liststore1">
    <columns>
      <!-- column-name Texto -->
      <column type="gchararray"/>
      <!-- column-name Código -->
      <column type="gint"/>
    </columns>
  </object>

</interface>
"""

    # Função chamada pelo evento de clicar o botão
    def click(*args):
        try:
            print error(args[0], 'Teste de erro')
            print info(args[0], 'Teste de erro')
            print warning(args[0], 'Teste de erro')
            print question(args[0], 'Teste de erro?')
            print error('', 'Teste de erro')
        except Exception:
            class X(object):
                def __init__(self):
                    self.interface = ui
            x = X()
            show_exception(x, args)
        # print args
        # dados: matriz de dados
        # Pode vir de um select ou um arquivo
        dados = (("12.345.678", "Junior", "3.000,12", 1, 1, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime(1900, 1, 2, 11, 59, 59), datetime.datetime(1900, 1, 2), datetime.datetime.now(), datetime.datetime.now(), None, 'red'),
                 ("abc", "Teste", "XYZ", "True", 2, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None, 'magenta'),
                 ("1....2,34", "Teste 2", "3.5.0.0,4.6", "False", 3, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None, 'cyan'),
                 (2.9, 123456.54321, 3.9999, 5, 4, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None, 'yellow'),
                 ("1234", "Carlos", "3.500", True, 5, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None, 'green'),
                 ("4.321", "Osvaldo", "4000,34", False, 6, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None, 'white'),
                 ("1234.567", "Leonardo", "5.000,33", 0, 7, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None, 'pink'),
                 ("1234.567", "Leonardo Sim", "5.000,33", "Sim", 8, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), 'yellow', 'blue'),
                 ("1234.567", "Leonardo Não", "5.000,33", "Não", 9, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None, 'royal blue'))
        grade = ui.get_object('gr_treeview1')
        grade.clear()
        grade.add_data(dados)

    def fx(self, text, pos, path, model_pos, model, titles, types, decimals):
        return PoleUtil.convert_and_format(text, types[pos], decimals[pos])

    def update(*args):
        # print args
        grade = ui.get_object('gr_treeview1')
        # print "*" * 100
        # print grade[5][2]
        grade[5]['Valor'] = datetime.datetime.now()
        # print grade[5][2]
        # print grade[5]['Valor']
        # print grade[5][-1]
        grade.get_column(2).get_cell_renderers()[0].set_property('editable', not grade.get_column(2).get_cell_renderers()[0].get_property('editable'))
        grade[1] = ['N'] * 100
        # print grade[6]['Mês']
        grade[6]['Mês'] = grade[6]['Mês'][0] + grade[6]['Valor'][0]
        # print grade[6]['Mês']

    def calendar(*args):
        button = args[0]
        if button == ui.get_object('button3'):
            print Calendar(args[0], PoleUtil.MONTH).run()
        elif button == ui.get_object('button4'):
            print Calendar(args[0], PoleUtil.DATE).run()
        elif button == ui.get_object('button5'):
            print Calendar(args[0], PoleUtil.DATE_TIME).run()
        elif button == ui.get_object('button6'):
            print Calendar(args[0], PoleUtil.TIME).run()
        elif button == ui.get_object('bt_popup'):
            class W(PopupWindow):
                def selecionado(self, grade, linha, coluna):
                    self.retorno = {coluna.get_title():
                                    grade[linha][coluna.get_title()]}
                    self.quit()

                def run(self, caller):
                    s = gtk.ScrolledWindow()
                    s.set_shadow_type(gtk.SHADOW_IN)
                    g = Grid()
                    s.add(g)
                    g.structure(('Código', 'Nome', 'Casado'), (int, str, bool))
                    import random
                    g.add_data([[random.randint(0, 1000), random.random(),
                                 random.choice([True, False])]
                                for i in range(100)])
                    g.connect('row-activated', self.selecionado)
                    self.set_size_request(max(caller.allocation.width, 300),
                                          200)
                    self.add(s)
                    self.retorno = None
                    super(W, self).run(caller)
                    return self.retorno

            print W().run(button)
        elif button == ui.get_object('dt_teste'):
            # print 'X' * 100
            print button.updated

    # ui = gtk.Builder()
    # ui.add_from_string(teste_ui)
    ui = build_interface(teste_ui)
    ui.connect_signals({'click': click, 'quit': gtk.main_quit,
                        'update_click': update, 'calendar': calendar})
    ui.get_object('gr_treeview1').format_callback = fx
    completar = ui.get_object('liststore1')
    completar.append(('Teste1', 1))
    completar.append(('Teste2', 2))
    completar.append(('aTeste3', 3))
    completar.append(('bTeste4', 4))
    completar.append(('cTeste5', 5))
    completar.append(('Junior Polegato', 5))
    completar.append(('Claudio Polegato Junior', 5))
    gtk.main()
    exit(0)

    # Interface de teste
    janela = gtk.Window()

    vbox = gtk.VBox()
    janela.add(vbox)

    rolagem = gtk.ScrolledWindow()
    vbox.pack_start(rolagem)

    grade = Grid()
    rolagem.add(grade)

    botao = gtk.Button("Preencher")
    botao.child.child.get_children()[0].show()
    vbox.pack_start(botao, False)

    # Mostar a interface
    janela.maximize()
    janela.show_all()

    # Operar sobre a grade criada como se fosse do gtk.Builder
    titulos = ("Código", "Nome", "Bônus", "Último")
    tipos = (int, str, float, bool)
    grade.columns(titulos, tipos)

    # Eventos
    janela.connect("delete_event", gtk.main_quit)
    # botao.connect("clicked", ao_clicar_preencher, grade)

    # Inciar o GTK
    gtk.main()
