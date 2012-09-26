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
pygtk.require("2.0")
import gtk
import gobject
import glib
from gtk import gdk
import datetime
import PoleUtil
import PoleLog
import unicodedata
import sys
import os
cf = PoleUtil.convert_and_format

# Translation
_ = PoleUtil._

message_titles = {gtk.MESSAGE_INFO: _('Information'),
                  gtk.MESSAGE_WARNING: _('Warning'),
                  gtk.MESSAGE_QUESTION: _('Question'),
                  gtk.MESSAGE_ERROR: _('Error')
                 }

def message(widget, text, message_type = gtk.MESSAGE_INFO, title = None):
    if message_type == gtk.MESSAGE_QUESTION:
        buttons = gtk.BUTTONS_YES_NO
    else:
        buttons = gtk.BUTTONS_CLOSE
    dialog = gtk.MessageDialog(widget.get_toplevel(), message_format = text,
                               type = message_type, buttons = buttons)
    if title is None:
        title = message_titles[message_type]
    dialog.set_title(title)
    result = dialog.run()
    dialog.destroy()
    return result

def load_images_as_icon(path = '.'):
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
        #print 'init 1 popup', self,args
        super(PopupWindow, self).__init__(*args)
        #print 'init 2 popup', self,args
        self.set_decorated(False)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        #self.connect('focus-out-event', self.quit)
        #self.connect("button-press-event", self.quit)
        #self.connect("delete-event", self.undelete)
        # For new versions of GTK+
        try:
            self.set_property('has_resize_grip', False)
        except:
            pass

    def do_delete_event(self, event):
        return True

    def run(self, caller, size = None, position = None, center = False):
        toplevel = caller.get_toplevel()
        self.set_transient_for(toplevel)
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
            status = gtk.gdk.pointer_grab(window = self.window, owner_events = True,
                                          event_mask = gtk.gdk.BUTTON_PRESS_MASK,
                                          cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
            if status in (gtk.gdk.GRAB_SUCCESS, gtk.gdk.GRAB_ALREADY_GRABBED):
                break;
        if status not in (gtk.gdk.GRAB_SUCCESS, gtk.gdk.GRAB_ALREADY_GRABBED):
            toplevel.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.__loop.run()
        gtk.gdk.pointer_ungrab()
        self.hide()

    def do_focus_out_event(self, event):
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
            #print w, h , x, y, self
            if 0 <= x <= w and 0 <= y <= h:
                return
        #popup.__loop.quit()
        self.__loop.quit()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Classe Calendar mostra o Calendário quando executada a função run,
# segurando parado o programa principal naquele ponto de chamada, tal
# como a run do GtkDialog, sendo que Enter emite Ok e Esc emite Cancelar
class Calendar(PopupWindow):
    def __init__(self, caller, calendar_type = PoleUtil.DATE):
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
        if self.__old_date is None:
            date = datetime.datetime.now()
        else:
            date = PoleUtil.convert_and_format(self.__old_date, datetime.datetime, self.__type)[0]
        self.__frame = gtk.Frame()
        self.__frame.set_shadow_type(gtk.SHADOW_IN)
        self.__vbox = gtk.VBox()
        self.__buttons = gtk.HButtonBox()
        self.__ok = gtk.Button(stock = 'gtk-ok')
        self.__arrow = gtk.Image()
        self.__arrow.set_from_stock('gtk-jump-to', gtk.ICON_SIZE_BUTTON)
        self.__today = gtk.Button(label = (_('_Today'), _('_Now'))[self.__type in (1, 2)])
        self.__today.set_image(self.__arrow)
        self.__cancel = gtk.Button(stock = 'gtk-cancel')
        self.__ok.connect('clicked', self.__change_date)
        self.__today.connect('clicked', self.__go_to_now)
        self.__today.connect('button-press-event', self.__double_click)
        self.__cancel.connect('clicked', self.quit)
        self.__buttons.pack_start(self.__ok)
        self.__buttons.pack_start(self.__today)
        self.__buttons.pack_start(self.__cancel)
        if self.__type == PoleUtil.MONTH:
            self.__table = gtk.Table(homogeneous = True)
            toggle = None
            for i in range(12, 0, -1):
                toggle = gtk.RadioButton(toggle, '%02i - ' % i + datetime.date(1900,  i, 1).strftime('%B').capitalize())
                toggle.set_mode(False)
                toggle.set_relief(gtk.RELIEF_NONE)
                toggle.get_children()[0].set_alignment(0.0, 0.5)
                toggle.connect('button-press-event', self.__double_click)
                self.__table.attach(toggle, (i - 1) / 4, (i - 1) / 4 + 1, (i - 1) % 4, (i - 1) % 4 + 1)
            self.__table.get_children()[date.month - 1].set_active(True)
            self.__vbox.set_spacing(15)
            self.__vbox.pack_start(self.__table)
            self.__hbox = gtk.HBox(spacing = 5)
            self.__year = gtk.SpinButton()
            self.__hbox = gtk.HBox(spacing = 5)
            self.__year_label = gtk.Label(_('Year:'))
            self.__year_label.set_alignment(1.0, 0.5)
            self.__year.get_adjustment().set_all(value = date.year,
                                                 lower = 1,
                                                 upper = 9999,
                                                 step_increment = 1,
                                                 page_increment = 10)
            self.__hbox.pack_start(self.__year_label, expand = True, fill = True)
            self.__hbox.pack_start(self.__year, expand = False, fill = False)
            self.__vbox.pack_start(self.__hbox, expand = False, fill = False)
            self.__vbox.pack_start(self.__buttons, expand = False, fill = False)
            self.__frame.add(self.__vbox)
            self.add(self.__frame)
            self.__year.grab_focus()
        if self.__type in (PoleUtil.DATE, PoleUtil.DATE_TIME):
            self.__calendar = gtk.Calendar()
            self.__calendar.select_day(date.day)
            self.__calendar.select_month(date.month - 1, date.year)
            self.__calendar.connect("day-selected-double-click", self.__change_date)
            self.__vbox.pack_start(self.__calendar, expand = False, fill = False)
        if self.__type == PoleUtil.DATE:
            self.__frame.add(self.__buttons)
            self.__vbox.pack_start(self.__frame, expand = False, fill = False)
            self.add(self.__vbox)
        if self.__type in (PoleUtil.TIME, PoleUtil.DATE_TIME):
            self.__vbox_time = gtk.VBox(spacing = 5)
            self.__hbox = gtk.HBox()
            self.__vbox_time.pack_start(self.__hbox)
            self.__vbox_time.pack_start(self.__buttons)
            self.__frame.add(self.__vbox_time)
            self.__vbox.pack_start(self.__frame, expand = False, fill = False)
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
            self.__hbox.pack_start(self.__label, expand = True)
            self.__hbox.pack_start(self.__hour, expand = False)
            self.__hbox.pack_start(self.__label1, expand = False)
            self.__hbox.pack_start(self.__minute, expand = False)
            self.__hbox.pack_start(self.__label2, expand = False)
            self.__hbox.pack_start(self.__second, expand = False)
            self.__hour.get_adjustment().set_all(value = date.hour,
                                                 lower = 0,
                                                 upper = 23,
                                                 step_increment = 1,
                                                 page_increment = 5)
            self.__minute.get_adjustment().set_all(value = date.minute,
                                                   lower = 0,
                                                   upper = 59,
                                                   step_increment = 1,
                                                   page_increment = 5)
            self.__second.get_adjustment().set_all(value = date.second,
                                                   lower = 0,
                                                   upper = 59,
                                                   step_increment = 1,
                                                   page_increment = 5)
        self.__updated = False

    def run(self):
        super(Calendar, self).run(self.__caller)
        return self.__updated
        
    def __double_click(self, *args):
        if args[1].type == gtk.gdk._2BUTTON_PRESS:
            self.__change_date()

    def __go_to_now(self, *args):
        date = datetime.datetime.now()
        if self.__type == PoleUtil.MONTH:
            self.__year.set_value(date.year)
            self.__table.get_children()[date.month - 1].set_active(True)
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
        elif self.__type == PoleUtil.MONTH:
            month = 0
            for child in self.__table.get_children():
                month += 1
                if child.get_active():
                    break
            date = datetime.datetime(int(self.__year.get_value()), month, 1)
        else:
            date = datetime.datetime(1900, 1, 1)
        if self.__type in (PoleUtil.TIME, PoleUtil.DATE_TIME):
            date = date.replace(hour = int(self.__hour.get_value()),
                                minute = int(self.__minute.get_value()),
                                second = int(self.__second.get_value()))
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
            return
        configs = [c.replace('0x00', '|') for c in configs.replace('\|','0x00').split('|')]
        self.set_tooltip_text(configs[0])
        types = {'DATE': PoleUtil.DATE, 'TIME': PoleUtil.TIME, 'DATE_TIME': PoleUtil.DATE_TIME, 'MONTH': PoleUtil.MONTH, 'HOURS': PoleUtil.HOURS, 'DAYS_HOURS': PoleUtil.DAYS_HOURS}
        for c in configs[1:]:
            if c in types:
                self.__type = types[c]
            if c == 'select_then_tab':
                self.__select_then_tab = True

    def do_clicked(self, *args, **kargs):
        old = self.get_label()
        try:
            x = PoleUtil.convert_and_format(old, datetime.datetime, self.__type)[1]
        except ValueError:
            x = PoleUtil.convert_and_format(datetime.datetime.now(), datetime.datetime, self.__type)[1]
        self.set_label(x)
        changed = Calendar(self, self.__type).run()
        self.updated = old != x or changed
        if self.__select_then_tab:
            self.__timer = gobject.timeout_add(500, self.__emit_tab)
        #super(DateButton, self).do_clicked(self, *args, **kargs)

    def __emit_tab(self):
        gobject.source_remove(self.__timer)
        event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
        event.keyval = gtk.keysyms.Tab
        #event.string = ''
        #event.send_event = False
        #event.time = 0
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
    def __init__(self, grid, path):
        self.__grid = grid
        self.__path = path
        self.__line = grid._Grid__get_line(path)
    def __getitem__(self, index):
        if isinstance(index, slice):
            index = index.indices(len(self.__grid._Grid__titles))
            return (tuple([self.__line[0][i] for i in range(*index)]), tuple([self.__line[1][i] for i in range(*index)]))
        if type(index) == str:
            if index not in self.__grid._Grid__titles:
                raise ValueError, _('Invalid or not found column name `' + index + '´.')
            index = self.__grid._Grid__titles.index(index)
        return [self.__line[0][index], self.__line[1][index]]
    def __setitem__(self, index, value):
        model = self.__grid.get_model()
        types = self.__grid._Grid__types
        if type(index) == str:
            if index not in self.__grid._Grid__titles:
                raise ValueError, _('Invalid or not found column name `' + index + '´.')
            index = self.__grid._Grid__titles.index(index)
        if type(index) == int:
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
            if types[index] in (int, float, datetime.date, datetime.time, datetime.datetime):
                line[column], line[column + 1] = formated
            elif types[index] == bool:
                line[column] = formated[0]
            else:
                line[column] = formated[1]
        else:
            raise TypeError, _('Invalid type of column index or name `' + type(index) + '´.')

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
        self.__digits = self.__digits = PoleUtil.locale.localeconv()['frac_digits']
        self.__int = False
        self.__num = False
        self.__old_text = ''

    def do_parser_finished(self, builder):
        configs = self.get_tooltip_text()
        if configs is None or '|' not in configs:
            return
        configs = [c.replace('0x00', '|') for c in configs.replace('\|','0x00').split('|')]
        self.set_tooltip_text(configs[0])
        configs = [[x.strip() for x in i.split(',')] for i in configs[1:]]
        self.__enter_to_tab = "enter_to_tab" in [x[0].lower() for x in configs]
        self.__upper = "upper" in [x[0].lower() for x in configs]
        self.__lower = "lower" in [x[0].lower() for x in configs]
        self.__normalize = "normalize" in [x[0].lower() for x in configs]
        self.__float = "float" in [x[0].lower()[:5] for x in configs]
        if self.__float:
            try:
                self.__digits = int([x[0][5:] for x in configs if x[0].lower()[:5] == "float"][0])
            except Exception:
                #import traceback
                #traceback.print_exc()
                self.__digits = PoleUtil.locale.localeconv()['frac_digits']
        self.__int = "int" in [x[0].lower() for x in configs]
        self.__num = "num" in [x[0].lower() for x in configs]
        if self.__int or self.__float or self.__num:
            self.set_alignment(1)

    def do_key_press_event(self, event):
        #print editor, event
        if self.__enter_to_tab and event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
            event.keyval = gtk.keysyms.Tab
            # Hardware key code
            keymap = gtk.gdk.keymap_get_default()
            keycode, group, level = keymap.get_entries_for_keyval(event.keyval)[0]
            event.hardware_keycode = keycode
            event.group = group
            event.state = level
        else:
            super(Editor, self).do_key_press_event(self, event)

    def do_changed(self, *args, **kargs):
        #print self.__formating
        if self.__formating or self.get_text() == '':
            return
        pos = self.get_position()
        text = self.get_text().decode('utf-8')
        #print text
        size = len(text)
        if self.__int or self.__num:
            text = ''.join([c for c in text if c.isdigit()])
        elif self.__float:
            text = ''.join([c for c in text if c.isdigit() or c == PoleUtil.locale.localeconv()['decimal_point']])
            text = text.split(PoleUtil.locale.localeconv()['decimal_point'])
            text = PoleUtil.locale.localeconv()['decimal_point'].join(text[:2]) + ''.join(text[2:])
        else:
            if self.__normalize:
                text = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
            if self.__upper:
                text = text.upper()
            elif self.__lower:
                text = text.lower()
        self.__formating = True
        self.set_text(text)
        #print pos, size, len(text), text
        self.set_position(pos - (size - len(text)))
        #while gtk.events_pending():
        #    gtk.main_iteration()
        self.__formating = False
        
    def do_focus_out_event(self, *args, **kargs):
        if self.get_text() == '':
            super(Editor, self).do_focus_out_event(self, *args, **kargs)
            return
        self.__formating = True
        if self.__int:
            self.set_text(cf(self.get_text(), int)[1])
        elif self.__float:
            self.set_text(cf(self.get_text(), float, self.__digits)[1])
        self.__formating = False
        super(Editor, self).do_focus_out_event(self, *args, **kargs)
        self.__formating = True

    def do_focus_in_event(self, *args, **kargs):
        self.__formating = False
        self.do_changed()
        super(Editor, self).do_focus_in_event(self, *args, **kargs)

class Grid(gtk.TreeView, gtk.Buildable):
    __gtype_name__ = 'Grid'
    def __init__(self, *args):
        super(Grid, self).__init__(*args)
        #self.set_rules_hint(True)
        #self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

        self.__titles = []
        self.__types = []
        self.__decimals = []
        self.__editables = []
        self.__with_colors = False

        self.__model_types = []

        self.edit_callback = None

        self.__model_pos = []

    def do_parser_finished(self, builder):
        configs = self.get_tooltip_text()
        if configs is None or '|' not in configs:
            return
        configs = [c.replace('0x00', '|') for c in configs.replace('\|','0x00').split('|')]
        #self.set_tooltip_text((configs[0], ' ')[configs[0] == ""])
        self.set_tooltip_text(configs[0])
        configs = [[x.strip() for x in i.split(',')] for i in configs[1:]]
        titles = []
        types = []
        decimals = []
        editables = []
        with_colors = False
        for column in configs:
            if len(column) > 4:
                raise ValueError, _("Invalid values column format, expected max of 4 values: name, type[, decimal][,edit].")
            if len(column) == 1 and column[0] == 'color':
                with_colors = True
                continue
            if len(column) < 2 or len(column) > 4:
                raise ValueError, _('Invalid column parameters. Expected color or title,type[,decimals][,edit].')
            titles.append(column[0])
            if column[1] == 'bool':
                types.append(bool)
            elif column[1] == 'int':
                types.append(int)
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
            else:
                raise TypeError, _('Invalid type `%s´. Expected int, bool, float, str, datetime, date, time, month or hours.') % (column[1],)
            c = 2

            if len(column) > 2:
                if column[2].isdigit():
                    if column[1] not in ('date', 'time', 'datetime', 'month', 'hours'):
                        decimals.append(int(column[2]))
                elif column[2] == 'edit':
                    if column[1] not in ('date', 'time', 'datetime', 'month', 'hours'):
                        decimals.append(PoleUtil.locale.localeconv()['frac_digits'])
                    editables.append(True)
                elif column[2] not in ('DATE', 'TIME', 'DATE_TIME', 'MONTH', 'HOURS', 'DAYS_HOURS'):
                    raise ValueError, _("Invalid value for decimals ou editable `%s´. Expected digits, 'DATE', 'TIME', 'DATE_TIME', 'MONTH', 'HOURS' or 'DAYS_HOURS' for decimals or 'edit' for editable.") % (column[2],)
                if len(column) == 4:
                    if column[3] == 'edit':
                        if column[2] == 'edit':
                            raise ValueError, _('Expected just one `edit´ for editable.')
                        editables.append(True)
                    else:
                        raise ValueError, _('Invalid value for editable `%s´. Expected `edit´ for editable, just one.') % (column[3],)
                elif column[2] != 'edit':
                    editables.append(False)
            else:
                if column[1] not in ('date', 'time', 'datetime', 'month', 'hours'):
                    decimals.append(PoleUtil.locale.localeconv()['frac_digits'])
                editables.append(False)
        self.structure(titles, types, decimals, editables, with_colors)

    def structure(self, titles, types, decimals = None, editables = None, with_colors = False):
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
            if t in (int, float, datetime.date, datetime.time, datetime.datetime, datetime.timedelta):
                self.__model_types.append(str)
        if with_colors:
            self.__model_types.append(str) # foreground color
            self.__model_types.append(str) # background color
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
            l = gtk.Label(title)
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
                cell.connect('edited', self.__editable_callback, len(self.__model_pos) - 1)
                column.pack_start(cell)
                column.add_attribute(cell, "text", model_pos + (t in (int, float, datetime.date, datetime.time, datetime.datetime)))
            column.set_sort_column_id(model_pos)
            if t in (int, float):
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
        self.append_column(gtk.TreeViewColumn(""))

    def get_structure(self):
        return (self.__titles, self.__types, self.__decimals, self.__editables, self.__with_colors)

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

    def clear(self):
        model = self.get_model()
        if model:
            model.clear()
            return
        raise ValueError, _('No columns structure defined.')

    def add_data(self, data, path_or_iter = None):
        if data in (None, [], [[]], ''):
            return path_or_iter
        model = self.get_model()
        if not model:
            raise ValueError, _('No columns structure defined.')
        if path_or_iter is not None:
            try:
                if type(path_or_iter) in (str, int):
                    iter = model.get_iter_from_string(str(path_or_iter))
                elif type(path_or_iter) in (tuple, list):
                    iter = model.get_iter(tuple(path_or_iter))
                elif is_instance(path_or_iter, gtk.TreeIter):
                    iter = path_or_iter
                else:
                    raise TypeError, _('Type `' + str(type(path_or_iter)).split("'")[1] + '´of path is not valid. Expected str, int, tuple, list (path) or gtk.TreeIter.')
                if not model.iter_is_valid(iter):
                    raise ValueError, _('Path or iter is not valid.')
            except Exception:
                raise ValueError, _('Path or iter is not valid.')
        else:
            iter = None
        # Inserting a line
        if type(data) in (tuple, list) and len(data) > 0 and type(data[0]) not in (tuple, list):
            data  = [data]
        # Inserting a value
        if type(data) not in (tuple, list) or (len(data) > 0 and type(data[0]) not in (tuple, list)):
            data = [[data]]
        error = False
        last_iter = iter
        for register in data:
            formated = []
            for t, decimals, field in zip(self.__types, self.__decimals, register):
                if t in (int, float, datetime.date, datetime.time, datetime.datetime):
                    try:
                        f = PoleUtil.convert_and_format(field, t, decimals)
                        if t in (datetime.time, datetime.datetime):
                            f[0] = PoleUtil.convert_and_format(f[0], float)[0]
                        elif t == datetime.date:
                            f[0] = PoleUtil.convert_and_format(f[0], int)[0]
                        formated += f
                    except ValueError or TypeError:
                        PoleLog.log_except()
                        formated += [t(0), field]
                        error = True
                elif t == bool:
                    try:
                        formated.append(PoleUtil.convert_and_format(field, t)[0])
                    except ValueError or TypeError:
                        PoleLog.log_except()
                        formated.append(False)
                        error = True
                else:
                    formated.append(field)
            if self.__with_colors:
                formated += register[-2:]
            last_iter = model.append(iter, formated)
        if error:
            message(self, _("Some values could not be converted or formatted!\n\nThey will be displayed as they are and evalueted by zero (0 ou 0.0) or false."))
        if isinstance(last_iter, gtk.TreeIter):
            return model.get_path(last_iter)
        return last_iter

    def update_line(self, path_or_iter, new_values):
        model = self.get_model()
        if not model:
            raise ValueError, _('No columns structure defined.')
        try:
            if type(path_or_iter) in (str, int):
                iter = model.get_iter_from_string(str(path_or_iter))
            elif type(path_or_iter) in (tuple, list):
                iter = model.get_iter(tuple(path_or_iter))
            elif is_instance(path_or_iter, gtk.TreeIter):
                iter = path_or_iter
            else:
                raise TypeError, _('Type `' + str(type(path_or_iter)).split("'")[1] + '´of path is not valid. Expected str, int, tuple, list (path) or gtk.TreeIter.')
            if not model.iter_is_valid(iter):
                raise ValueError, _('Path or iter is not valid.')
        except Exception:
            raise ValueError, _('Path or iter is not valid.')
        # Updating a value
        if type(new_values) not in (tuple, list):
            new_values = [new_values]
        error = False
        formated = []
        for t, decimals, field in zip(self.__types, self.__decimals, new_values):
            if t in (int, float, datetime.datetime, datetime.date, datetime.time):
                try:
                    formated += PoleUtil.convert_and_format(field, t, decimals)
                except ValueError or TypeError:
                    PoleLog.log_except()
                    formated += [t(0), field]
                    error = True
            elif t == bool:
                try:
                    formated.append(PoleUtil.convert_and_format(field, t)[0])
                except ValueError or TypeError:
                    PoleLog.log_except()
                    formated.append(False)
                    error = True
            else:
                formated.append(field)
        if self.__with_colors:
            formated += new_values[-2:]
        model[path_or_iter] = formated
        if error:
            message(self, _("Some values could not be converted or formatted!\n\nThey will be displayed as they are and evalueted by zero (0 ou 0.0) or false."))

    def __get_line(self, path):
        model_line = self.get_model()[path]
        values = []
        formateds = []
        col = 0
        types = self.__types[:]
        if self.__with_colors:
            types += [str, str]
        for t in types:
            if t in (datetime.datetime, datetime.date, datetime.time):
                values.append(PoleUtil.convert_and_format(model_line[col], t)[0])
            else:
                values.append(model_line[col])
            if t in (int, float, datetime.datetime, datetime.date, datetime.time):
                formateds.append(model_line[col+1])
                col += 2
            else:
                formateds.append(model_line[col])
                col += 1
        return [values, formateds]

    def __getitem__(self, path):
        if type(path) == slice:
            model = self.get_model()
            index = path.indices(len(model))
            return tuple([GridRow(self, i) for i in range(*index)])
        return GridRow(self, path)
        # Antes era assim
        #if type(path) == slice:
        #    model = self.get_model()
        #    index = path.indices(len(model))
        #    values = []
        #    formateds = []
        #    for i in range(*index):
        #        line = self.__get_line(i)
        #        values.append(line[0])
        #        formateds.append(line[1])
        #    return (tuple(values), tuple(formateds))
        #return self.__get_line(path)

    def __setitem__(self, item, value):
        self.update_line(item, value)
        
    def remove(self, path_iter):
        if isinstance(path_iter, tuple):
            path_iter = self.get_model().get_iter(path_iter)
        elif not isinstance(path_iter, gtk.TreeIter):
            path_iter = self.get_model().get_iter_from_string(str(path_iter))
        return self.get_model().remove(path_iter)


def load_module(parent_project, parent_main_window, module_name, title, main_window_name, data = None):
    loop = glib.MainLoop()
    module = __import__(module_name)
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
            parent_main_window.hide()
        else:
            main_window.set_title(title)
        main_window.show()
        main_window.present()
    loop.run()
    if main_window is not None:
        main_window.destroy()
    del main_window
    del project
    del module
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
)

def build_interface(xml_file_or_xml_string = None):
    # Verifying type of xml_file_or_xml_string
    if type(xml_file_or_xml_string) != str:
        raise TypeError, _('Invalid argument "xml_file_or_xml_string" of type `%s´. Expected str.') % (type(xml_file_or_xml_string).__name__,)
    if xml_file_or_xml_string[:6] == '<?xml ':
        xml = xml_file_or_xml_string
    else:
        xml = open(xml_file_or_xml_string).read()
    # Verifying if is xml
    if xml[:6] != '<?xml ':
        raise TypeError, _('Invalid content. Expected XML data.')
    ui = gtk.Builder()
    # Replacing Gtk classes by Pole classes
    for gtk_class, pole_class, start_of_name in NEW_CLASSES:
        xml = xml.replace('<object class="' + gtk_class + '" id="' + start_of_name,
                          '<object class="' + pole_class + '" id="' + start_of_name)
    # Solving troble with can_focus false
    pos = xml.find('<object class="')
    while pos != -1:
        if xml[pos + 18:pos + 23] not in ('ListS', 'Adjus', 'TextB', 'Actio'):
            #print xml[pos:pos + 40]
            pos = xml.find('>', pos) + 1
            xml = xml[:pos] + '<property name="can_focus">False</property>' + xml[pos:]
        pos = xml.find('<object class="', pos + 70)
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
    def __getattribute__(self, attribute):
        if attribute == "widget":
            return object.__getattribute__(self, attribute)
        if attribute == "__class__":
            return VirtualWidget
        try:
            resultado = object.__getattribute__(object.__getattribute__(self,
                                                      "widget"), attribute)
            return resultado
        except:
           try:
                resultado = object.__getattribute__(object.__getattribute__(
                                        self, "widget"), "get_" + attribute)
                return resultado()
           except:
                pass
        return None
    def __setattr__(self, attribute, valor):
        try:
            obj = object.__getattribute__(self, "widget")
            consulta = object.__getattribute__(obj, attribute)
            obj.__setattr__(attribute, valor)
        except:
            try:
                consulta = object.__getattribute__(obj, "set_" + attribute)
                consulta(valor)
            except:
                object.__setattr__(obj, attribute, valor)
        return
    def __getitem__(self, index):
        return object.__getattribute__(self, "widget")[index]
    def __setitem__(self, index, value):
        object.__getattribute__(self, "widget")[index] = value

class Project(object):
    def __init__(self, ui, parent = None, loop = None, data = None):
        self.consulteds_attributes = {}
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
                           if type(x) == gtk.ComboBox]:
            celula = gtk.CellRendererText()
            combo.pack_start(celula)
            combo.add_attribute(celula, "text", 0)
        # Resolver problema de imagens não exibidas nos botões
        # Comente caso queira o comportamento configurado no Gnome, pois
        #     a partir da versão 2.28 por padrão não mostra, sendo que
        #     para alterar o padrão edite via
        #     "Aplicativos->Sistema->Editor de configurações"
        #     a chave "/desktop/gnome/interface/buttons_have_icons" ou execute
        #     "gconftool --toggle /desktop/gnome/interface/buttons_have_icons"
        for botao in [x for x in self.interface.get_objects()
                                                      if type(x) == gtk.Button]:
            try:
                botao.child.child.get_children()[0].show()
            except:
                pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # ##
    # Função chamada toda vez que se requer informações de algum attribute/membro
    #     da classe. Aqui interceptamos verificando se já foi este consultado.
    #     Se não foi consultado ainda, procura este nome dentre os nomes de
    #     widgets do Glade. A busca retorna None se não for nome de um
    #     widget ou a instância do widget correspondente ao nome procurado. Este
    #     resultado fica guardado em um dicionário como um widget virtual,
    #     onde o nome do atribuito corresponderá a None ou à instância do widget
    #     virtual. No caso de já ter sido consultado, faz a procura deste no
    #     dicionário, onde se for None, continua com a busca do attribute
    #     normalmente, mas se não for None, isto é, será uma instância de um
    #     widget virtual correspondente, retorna essa instância.
    def __getattribute__(self, attribute):
        if attribute in object.__getattribute__(self, "consulteds_attributes"):
            if object.__getattribute__(self, "consulteds_attributes")[attribute]:
                return object.__getattribute__(self,
                                              "consulteds_attributes")[attribute]
            return object.__getattribute__(self, attribute)
        widget = object.__getattribute__(self, "interface").get_object(attribute)
        if widget:
            widget = VirtualWidget(widget)
            object.__getattribute__(self,
                                   "consulteds_attributes")[attribute] = widget
            return widget
        else:
            object.__getattribute__(self,
                                       "consulteds_attributes")[attribute] = None
        return object.__getattribute__(self, attribute)

def try_function(f):
    def action(project, *args, **kwargs):
        try:
            result = f(project, *args, **kwargs)
            return result
        except Exception as error:
            PoleLog.log_except()
            try:
                error_type = str(type(error)).split("'")[1].split('.')[-1]
            except:
                error_type = str(type(error))
            if len(args) > 1 and isinstance(args[1], gtk.Widget):
                obj = args[1]
            else:
                for obj in project.interface.get_objects():
                    if isinstance(obj, gtk.Widget):
                        break
            if isinstance(obj, gtk.Widget):
                message(obj.get_toplevel(), str(error).strip() + _('\n\nFunction: ') + str(f).split()[1], gtk.MESSAGE_ERROR, title = error_type)
            else:
                PoleLog.log(error_type + ': ' + str(error).strip() + _('\n\nFunction: ') + str(f).split()[1])
            return None
    return action

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
          </object>
          <packing>
            <property name="position">3</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
</interface>
"""

    # Função chamada pelo evento de clicar o botão
    def click(*args):
        #print args
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
                 ("1234.567", "Leonardo Não", "5.000,33", "Não", 9, datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), None, 'royal blue'),
                )
        grade = ui.get_object('gr_treeview1')
        grade.clear()
        grade.add_data(dados)
        
    def fx(self, text, pos, path, model_pos, model, titles, types, decimals):
        #eliezer print (self, text, pos)
        return PoleUtil.convert_and_format(text, types[pos], decimals[pos])

    def update(*args):
        #print args
        grade = ui.get_object('gr_treeview1')
        #print "*" * 100
        
        
        import datetime
        #print grade[5][2]
        grade[5]['Valor'] = datetime.datetime.now()
        #print grade[5][2]
        #print grade[5]['Valor']
        #print grade[5][-1]
        grade.get_column(2).get_cell_renderers()[0].set_property('editable', not grade.get_column(2).get_cell_renderers()[0].get_property('editable'))
        grade[1] = ['N'] * 100
        #print grade[6]['Mês']
        grade[6]['Mês'] = grade[6]['Mês'][0] + grade[6]['Valor'][0]
        #print grade[6]['Mês']

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
                    self.retorno = {coluna.get_title(): grade[linha][coluna.get_title()]}
                    self.quit()
                def run(self, caller):
                    s = gtk.ScrolledWindow()
                    s.set_shadow_type(gtk.SHADOW_IN)
                    g = Grid()
                    s.add(g)
                    g.structure(('Código', 'Nome', 'Casado'), (int, str, bool))#, editables = (True, True, True))
                    import random
                    g.add_data([[random.randint(0,1000), random.random(), random.choice([True, False])] for i in range(100)])
                    g.connect('row-activated', self.selecionado)
                    self.set_size_request(max(caller.allocation.width, 300), 200)
                    self.add(s)
                    self.retorno = None
                    super(W, self).run(caller)
                    return self.retorno
            print W().run(button)
        elif button == ui.get_object('dt_teste'):
            #print 'X' * 100
            print button.updated

    #ui = gtk.Builder()
    #ui.add_from_string(teste_ui)
    ui = build_interface(teste_ui)
    ui.connect_signals({'click': click, 'quit': gtk.main_quit, 'update_click': update, 'calendar': calendar})
    ui.get_object('gr_treeview1').format_callback = fx
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
    botao.connect("clicked", ao_clicar_preencher, grade)

    # Inciar o GTK
    gtk.main()
