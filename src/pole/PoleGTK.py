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
import StringIO
import subprocess
from collections import namedtuple

# Resolver problema de imagens não exibidas nos botões
gtk.settings_get_default().props.gtk_button_images = True
try:
    gtk.settings_get_default().props.gtk_menu_images = True
except Exception:
    print "Fail setting gtk_menu_images = True"

# Resolver problema de tamanho dos botões de fechar abas
gtk.rc_parse_string('''
    style "close-tab-button-style" {
        GtkWidget::focus-padding = 0
        GtkWidget::focus-line-width = 0
        xthickness = 0
        ythickness = 0
    }
    widget "*.close-tab-button" style "close-tab-button-style"''')

logger = logging.getLogger('pole')

cf = PoleUtil.convert_and_format

# Translation
_ = PoleUtil._

# Joins for SQL filter
trans_joins = {_('and'): 'and', _('or'): 'or'}
re_joins = reduce(lambda a, b: a + b, trans_joins.items())

# Operators for SQL filter
sign_ops = (('=', '='), ('<>', '!='), ('≠', '!='),
            ('>=', '>='), ('=>', '>='), ('≥', '>='),
            ('<=', '<='), ('=<', '<='), ('≤', '<='),
            ('!=', '!='), ('<', '<'), ('>', '>'))
trans_ops = ((_('was'), 'was'), (_('in'), 'in'), (_('is'), 'is'),
             (_(r'is\s*not\s*null'), r'is\s*not\s*null'),
             (_(r'is\s*not'), r'is\s*not'),
             (_(r'is\s*null'), r'is\s*null'),
             (_(r'not\s*like'), r'not\s*like'),
             (_(r'not\s*between'), r'not\s*between'),
             (_(r'will\s*be'), r'will\s*be'),
             (_(r'will\s*not\s*be'), r'will\s*not\s*be'),
             (_(r'was\s*not'), r'was\s*not'),
             (_(r'not\s*in'), r'not\s*in'),
             (_('like'), 'like'), (_('between'), 'between'))
re_ops = reduce(lambda a, b: a + b, trans_ops)
trans_ops = dict(tuple((k.replace(r'\s*', ''), v.replace(r'\s*', ' '))
                       for k, v in trans_ops) + tuple(
                       (v.replace(r'\s*', ''), v.replace(r'\s*', ' '))
                       for k, v in trans_ops) + sign_ops)
sign_ops = tuple(a for a, b in sign_ops)

# Date keywords
trans_dts = ((_(r'this\s*month'), r'this\s*month',
              "between trunc(sysdate, 'MONTH')"
              " and add_months(trunc(sysdate, 'MONTH'), 1) - 0.00001"),
             (_(r'next\s*month'), r'next\s*month',
              "between add_months(trunc(sysdate, 'MONTH'), 1)"
              " and add_months(trunc(sysdate, 'MONTH'), 2) - 0.00001"),
             (_(r'last\s*month'), r'last\s*month',
              "between add_months(trunc(sysdate, 'MONTH'), -1)"
              " and trunc(sysdate, 'MONTH') - 0.00001"),

             (_(r'this\s*year'), r'this\s*year',
              "between trunc(sysdate, 'YEAR')"
              " and add_months(trunc(sysdate, 'YEAR'), 12) - 0.00001"),
             (_(r'next\s*year'), r'next\s*year',
              "between add_months(trunc(sysdate, 'YEAR'), 12)"
              " and add_months(trunc(sysdate, 'YEAR'), 24) - 0.00001"),
             (_(r'last\s*year'), r'last\s*year',
              "between add_months(trunc(sysdate, 'YEAR'), -12)"
              " and trunc(sysdate, 'YEAR') - 0.00001"),

             (_(r'this\s*week'), r'this\s*week',
              "between trunc(sysdate) - to_char(sysdate, 'd') + 1"
              " and trunc(sysdate) - to_char(sysdate, 'd') + 7.99999"),
             (_(r'next\s*week'), r'next\s*week',
              "between trunc(sysdate) - to_char(sysdate, 'd') + 8"
              " and trunc(sysdate) - to_char(sysdate, 'd') + 14.99999"),
             (_(r'last\s*week'), r'last\s*week',
              "between trunc(sysdate) - to_char(sysdate, 'd') - 6"
              " and trunc(sysdate) - to_char(sysdate, 'd') + 0.99999"),

             (_(r'yesterday'), r'yesterday',
              "between trunc(sysdate) - 1 and trunc(sysdate) - 0.00001"),
             (_(r'today'), r'today',
              "between trunc(sysdate) and trunc(sysdate) + 0.99999"),
             (_(r'tomorrow'), r'tomorrow',
              "between trunc(sysdate) + 1 and trunc(sysdate) + 1.99999"),

             (_(r'now'), r'now', "sysdate"))

re_dts = reduce(lambda a, b: a + b, zip(*zip(*trans_dts)[:2]))
trans_dts = dict(reduce(lambda a, b: a + b,
                        (((a.replace(r'\s*', ''), c),
                          (b.replace(r'\s*', ''), c))
                         for a, b, c in trans_dts)))

# group 0 => string quote
# group 1 => operator
# group 2 => keyword separator at start
# group 3 => keyword
# group 4 => keyword separator at end
re_filter = re.compile(r'(["\'])|'
                       r'(' + r'|'.join(sign_ops) + ')|'
                       r'([^\.\w]|\A)'
                       r'(' + r'|'.join(re_dts + re_ops + re_joins) + r')'
                       r'([^\.\w]|\Z)', flags=re.I)


def update_ui():
    while gtk.events_pending():
        gtk.main_iteration()


def try_function(f):
    def action(project, *args, **kwargs):
        try:
            result = f(project, *args, **kwargs)
            return result
        except Exception:
            if args and isinstance(args[0], (gtk.Widget, VirtualWidget)):
                change_mouse_pointer(args[0], None)
            PoleLog.log_except()
            show_exception(project, args)
            return None
    return action


def new_tab(notebook, tab_label, tab_content, focus=True, tab_return=None):
    label = gtk.Label(tab_label)
    image = gtk.Image()
    image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
    button = gtk.Button()
    button.set_relief(gtk.RELIEF_NONE)
    button.set_focus_on_click(False)
    button.set_name("close-tab-button")
    button.set_size_request(20, 20)
    button.add(image)
    tab_header = gtk.HBox(spacing=5)
    tab_header.pack_start(label, True, True, 0)
    tab_header.pack_end(button, False, False, 0)
    tab_header.show_all()
    notebook.append_page(tab_content, tab_header)
    notebook.set_menu_label_text(tab_content, tab_label)
    if tab_return is None:
        tab_return = notebook.get_current_page()
    if focus:
        notebook.set_current_page(-1)
    button.connect('clicked', close_tab, notebook,
                   tab_header, tab_content, tab_return)


def close_tab(button, notebook, tab_header, tab_content, tab_return):
    page_num = notebook.page_num(tab_content)
    if (notebook.get_current_page() == page_num
            and tab_return < notebook.get_n_pages()):
        notebook.set_current_page(tab_return)
    notebook.remove_page(page_num)
    tab_header.destroy()
    tab_content.destroy()


message_titles = {gtk.MESSAGE_INFO: _('Information'),
                  gtk.MESSAGE_WARNING: _('Warning'),
                  gtk.MESSAGE_QUESTION: _('Question'),
                  gtk.MESSAGE_ERROR: _('Error')}


def message(widget, text, message_type=gtk.MESSAGE_INFO, title=None):
    # Get toplevel window
    window = None
    if isinstance(widget, (gtk.Widget, VirtualWidget)):
        window = widget.get_toplevel()

    if message_type == gtk.MESSAGE_QUESTION:
        buttons = gtk.BUTTONS_YES_NO
    else:
        buttons = gtk.BUTTONS_CLOSE
    flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT
    dialog = gtk.MessageDialog(window, flags,
                               message_type, buttons)
    dialog.set_markup(text)

    if title is None:
        title = message_titles[message_type]
    dialog.set_title(title)
    result = dialog.run()
    dialog.destroy()
    return result


def input_dialog(widget, text, editor_config=None,
                 default_text='', title=None, visibility=True):
    # Get toplevel window
    window = None
    if isinstance(widget, (gtk.Widget, VirtualWidget)):
        window = widget.get_toplevel()

    dialog = gtk.MessageDialog(window,
                               gtk.DIALOG_MODAL |
                               gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL)
    dialog.set_markup(text)

    if title is None:
        title = _("Give the resquested information")
    dialog.set_title(title)

    ed = Editor()
    ed.set_visibility(visibility)
    if editor_config in (bool, datetime.datetime, datetime.date,
                         datetime.time, datetime.timedelta):
        return_type = editor_config
        pole_type = None
    else:
        if editor_config:
            ed.config(editor_config)
        pole_type = ed._Editor__pole_type
        if pole_type:
            return_type = PoleUtil.python_tipos[PoleUtil.tipos[pole_type].tipo]
        else:
            return_type = editor_config

    if return_type == bool:
        ed.destroy()
        del ed
        ed = gtk.CheckButton()
        ed.set_active(cf(default_text, bool)[0] if default_text else False)
    elif return_type in (datetime.datetime, datetime.date,
                         datetime.time, datetime.timedelta):
        ed.destroy()
        del ed
        ed = DateButton()
        ed.set_label(default_text)
        ed.config(editor_config)
    elif pole_type and PoleUtil.tipos[pole_type].combo:
        ed.destroy()
        del ed
        model = gtk.ListStore(str, return_type)
        for opc in PoleUtil.tipos[pole_type].mascara[1:]:
            model.append(((opc[0] + ' - ' + opc[1] if len(opc) > 1
                           else opc[0]), opc[0]))
        ed = gtk.ComboBox(model)
        cell = gtk.CellRendererText()
        ed.pack_start(cell, True)
        ed.add_attribute(cell, 'text', 0)
        set_active_text(ed, default_text, 1)
    else:
        ed.set_text(default_text)
    dialog.get_message_area().pack_start(ed, expand=False, fill=True)
    dialog.set_default_response(gtk.RESPONSE_OK)
    dialog.show_all()
    result = dialog.run()
    text = (cf(ed.get_active(), bool)[0] if return_type == bool else
            ed.get_label() if return_type in (datetime.datetime,
                                              datetime.date, datetime.time,
                                              datetime.timedelta) else
            get_active_text(ed, 1) if isinstance(ed, gtk.ComboBox) else
            ed.get_text())
    dialog.destroy()
    return (result, text)


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

    glib.timeout_add(timeout, bar.destroy)


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
    window = None
    if isinstance(widget, (gtk.Widget, VirtualWidget)):
        window = widget.get_toplevel()
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
    obj = None
    if isinstance(project, (gtk.Widget, VirtualWidget)):
        obj = project
    if obj is None:
        for obj in args:
            if isinstance(obj, (gtk.Widget, VirtualWidget)):
                break
    if obj is None:
        for obj in project.interface.get_objects():
            if isinstance(obj, (gtk.Widget, VirtualWidget)):
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
            f = (f, [f])
        if isinstance(f, (list, tuple)):
            fx = gtk.FileFilter()
            fx.set_name(f[0])
            if isinstance(f[-1], (str, unicode)):
                f.append([f[-1]])
            for fl in f[-1]:
                fx.add_pattern(fl)
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
            if question(filechooser,
                        _('Overwrite the file?')) == gtk.RESPONSE_YES:
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
        except Exception:
            PoleLog.log_except()
        update_ui()


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
        super(PopupWindow, self).__init__(*args)
        self.set_decorated(False)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        # self.connect('focus-out-event', self.quit)
        # self.connect("button-press-event", self.quit)
        # self.connect("delete-event", self.undelete)
        # For new versions of GTK+
        try:
            self.set_property('has_resize_grip', False)
        except Exception:
            pass
        self.__canceled = False

    def do_delete_event(self, event):
        return True

    def run(self, caller, size=None,
            position=None, center=False, transient_for=None):
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
            status = gtk.gdk.pointer_grab(
                window=self.window, owner_events=True,
                event_mask=gtk.gdk.BUTTON_PRESS_MASK,
                cursor=gtk.gdk.Cursor(gtk.gdk.HAND2))
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
        popup = args[0] if args else self
        if len(args) == 2:
            if args[1] == gtk.RESPONSE_CANCEL:
                self.__canceled = True
            elif args[1].type in (gtk.gdk.BUTTON_PRESS, gtk.gdk._2BUTTON_PRESS,
                                  gtk.gdk._3BUTTON_PRESS):
                w, h = popup.get_size()
                x, y = popup.get_pointer()
                if 0 <= x <= w and 0 <= y <= h:
                    return
                self.__canceled = True
        self.__loop.quit()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Classe Calendar mostra o Calendário quando executada a função run,
# segurando parado o programa principal naquele ponto de chamada, tal
# como a run do GtkDialog, sendo que Enter emite Ok e Esc emite Cancelar
class Calendar(PopupWindow):
    def __init__(self, caller, calendar_type=PoleUtil.DATE):
        super(Calendar, self).__init__()
        self.__caller = caller
        self.__pole = None
        if (isinstance(calendar_type, (str, unicode))
                and calendar_type in PoleUtil.tipos):
            self.__pole = calendar_type
            self.__type = PoleUtil.tipos[calendar_type].casas
        else:
            self.__type = calendar_type
        if isinstance(caller, gtk.Entry):
            self.__set_new_date = caller.set_text
            self.__old_date = caller.get_text()
        else:
            self.__set_new_date = caller.set_label
            self.__old_date = caller.get_label()
        self.connect("key-press-event", self.__key_press)
        # If date is not valid, use now
        if not self.__old_date or not re.sub('[^1-9]', '', self.__old_date):
            date = datetime.datetime.now()
            if self.__type == PoleUtil.HOLLERITH:
                date = cf(date, datetime.date, PoleUtil.MONTH)[1]
        elif self.__type == PoleUtil.HOLLERITH:
            date = self.__old_date
        else:
            date = cf(self.__old_date, self.__pole if self.__pole
                      else datetime.datetime, self.__type)[0]
        self.__frame = gtk.Frame()
        self.add(self.__frame)
        self.__frame.set_shadow_type(gtk.SHADOW_IN)
        self.__vbox = gtk.VBox(spacing=5)
        self.__vbox.set_border_width(5)
        self.__frame.add(self.__vbox)
        self.__buttons = gtk.Table()
        # self.__buttons.set_row_spacings(5)
        # self.__buttons.set_col_spacings(5)
        self.__ok = gtk.Button(stock='gtk-ok')
        self.__ok.child.child.get_children()[0].show()
        self.__arrow = gtk.Image()
        self.__arrow.set_from_stock('gtk-jump-to', gtk.ICON_SIZE_BUTTON)
        self.__today = gtk.Button(label=(_('_Now') if self.__type in (1, 2)
                                         else _('_Today')))
        self.__today.set_image(self.__arrow)
        self.__today.child.child.get_children()[0].show()
        self.__cancel = gtk.Button(stock='gtk-cancel')
        self.__cancel.child.child.get_children()[0].show()
        self.__clear = gtk.Button(stock='gtk-clear')
        self.__clear.child.child.get_children()[0].show()
        self.__clear.connect('clicked', self.__clear_return)
        self.__ok.connect('clicked', self.__change_date)
        self.__today.connect('clicked', self.__go_to_now)
        self.__today.connect('button-press-event', self.__double_click)
        self.__cancel.connect('clicked', self.quit, gtk.RESPONSE_CANCEL)
        self.__buttons.attach(self.__today, 0, 1, 0, 1)
        self.__buttons.attach(self.__clear, 1, 2, 0, 1)
        self.__buttons.attach(self.__ok, 0, 1, 1, 2)
        self.__buttons.attach(self.__cancel, 1, 2, 1, 2)
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
                toggle = gtk.RadioButton(toggle, '%02i - %s' % (
                    i, datetime.date(1900,  i, 1).strftime('%B').capitalize()))
                toggle.set_mode(False)
                toggle.set_relief(gtk.RELIEF_NONE)
                toggle.get_children()[0].set_alignment(0.0, 0.5)
                toggle.connect('button-press-event', self.__double_click)
                self.__table.attach(toggle, (i - 1) / 4, (i - 1) / 4 + 1,
                                    (i - 1) % 4, (i - 1) % 4 + 1)
            month = (int(date[:2]) if self.__type == PoleUtil.HOLLERITH
                     else date.month)
            year = (int(date[3:]) if self.__type == PoleUtil.HOLLERITH
                    else date.year)
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
            self.__calendar.connect("day-selected-double-click",
                                    self.__change_date)
            self.__vbox.pack_start(self.__calendar, expand=False, fill=False)
        if self.__type == PoleUtil.DATE:
            self.__vbox.pack_start(self.__buttons, expand=False, fill=False)
        if self.__type in (PoleUtil.TIME, PoleUtil.DATE_TIME):
            self.__vbox_time = gtk.VBox(spacing=5)
            self.__hbox = gtk.HBox()
            self.__vbox_time.pack_start(self.__hbox)
            self.__vbox_time.pack_start(self.__buttons)
            self.__vbox.pack_start(self.__vbox_time, expand=False, fill=False)
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
            self.__hour.get_adjustment().set_all(lower=0,
                                                 upper=23,
                                                 value=23,
                                                 step_increment=1,
                                                 page_increment=5)
            self.__hour.get_adjustment().set_all(value=date.hour)
            self.__minute.get_adjustment().set_all(lower=0,
                                                   upper=59,
                                                   value=59,
                                                   step_increment=1,
                                                   page_increment=5)
            self.__minute.get_adjustment().set_all(value=date.minute)
            self.__second.get_adjustment().set_all(lower=0,
                                                   upper=59,
                                                   value=59,
                                                   step_increment=1,
                                                   page_increment=5)
            self.__second.get_adjustment().set_all(value=date.second)
        self.__updated = False

    def run(self, position=None, center=False, transient_for=None):
        super(Calendar, self).run(self.__caller, (-1, -1), position,
                                  center, transient_for)
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
            date = datetime.datetime(1, 1, 1)
        if self.__type in (PoleUtil.TIME, PoleUtil.DATE_TIME):
            date = date.replace(hour=int(self.__hour.get_value()),
                                minute=int(self.__minute.get_value()),
                                second=int(self.__second.get_value()))
        new_date = cf(date, self.__pole if self.__pole else datetime.datetime,
                      self.__type)[1]
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

    def __clear_return(self, *args):
        self.__updated = None
        self.quit()


class DateButton(gtk.Button, gtk.Buildable):
    __gtype_name__ = 'DateButton'
    __gsignals__ = {
        "clicked": "override",
    }

    def __init__(self, *args):
        super(DateButton, self).__init__(*args)
        self.__pole_type = None
        self.__type = PoleUtil.DATE
        self.updated = False
        self.__select_then_tab = False

    def do_parser_finished(self, builder):
        configs = self.get_tooltip_text()
        if configs is None or '|' not in configs:
            self.__default_date()
            return
        configs = [c.replace('0x00', '|')
                   for c in configs.replace('\\|', '0x00').split('|', 1)]
        self.set_tooltip_text(configs[0])
        self.config(configs[1])

    def config(self, configs):
        if configs in (datetime.datetime, datetime.date,
                       datetime.time, datetime.timedelta):
            configs = {datetime.datetime: 'DATE_TIME',
                       datetime.date: 'DATE', datetime.time: 'TIME',
                       datetime.timedelta: 'DAYS_HOURS'}[configs]

        types = {'DATE': PoleUtil.DATE, 'TIME': PoleUtil.TIME,
                 'DATE_TIME': PoleUtil.DATE_TIME, 'MONTH': PoleUtil.MONTH,
                 'HOURS': PoleUtil.HOURS, 'DAYS_HOURS': PoleUtil.DAYS_HOURS,
                 'HOURS_MIN': PoleUtil.HOURS_MIN,
                 'DAYS_HOURS_MIN': PoleUtil.DAYS_HOURS_MIN,
                 'HOLLERITH': PoleUtil.HOLLERITH}
        self.__pole_type = None
        if configs in types.values():
            self.__type = configs
        else:
            configs = [x.strip() for x in configs.split(',')]
            for c in configs:
                if c in PoleUtil.tipos:
                    self.__type = PoleUtil.tipos[c].casas
                    self.__pole_type = c
                elif c.isdigit() and int(c) in types.values():
                    self.__type = int(c)
                elif c.upper() in types:
                    self.__type = types[c.upper()]
                elif c.lower() == 'select_then_tab':
                    self.__select_then_tab = True

        self.__default_date()

    def __default_date(self):
        # If date didn't have at least one of z number, use now
        z = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        if (not self.get_label() or
                not sum(map(lambda x: x in z, self.get_label()))):
            now = datetime.datetime.now()
            if self.__pole_type:
                self.set_label(cf(now, self.__pole_type)[1])
            else:
                conv_type = (self.__type if self.__type != PoleUtil.HOLLERITH
                             else PoleUtil.MONTH)
                self.set_label(cf(now, datetime.datetime, conv_type)[1])

    def do_clicked(self, *args, **kargs):
        old = self.get_label()
        if self.__type != PoleUtil.HOLLERITH:
            try:
                x = (cf(old, self.__pole_type) if self.__pole_type else
                     cf(old, datetime.datetime, self.__type))[1]
            except ValueError:
                now = datetime.datetime.now()
                x = (cf(now, self.__pole_type) if self.__pole_type else
                     cf(now, datetime.datetime, self.__type))[1]
            self.set_label(x)
        changed = Calendar(self, self.__type).run()
        self.updated = (self.__type != PoleUtil.HOLLERITH and
                        old != x) or changed
        if self.__select_then_tab:
            self.__timer = gobject.timeout_add(1, self.__emit_tab)
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
            index = index.indices(len(self.__grid._Grid__titles) +
                                  2 * self.__with_colors)
            return (tuple([self.__line[0][i] for i in range(*index)]),
                    tuple([self.__line[1][i] for i in range(*index)]))
        if type(index) == str:
            if index not in self.__grid._Grid__titles:
                raise ValueError(_('Invalid or not found column name `%s´.'
                                   ) % index)
            index = self.__grid._Grid__titles.index(index)
        return [self.__line[0][index], self.__line[1][index]]

    def __setitem__(self, index, value):
        model = self.__grid.get_model()
        types = self.__grid._Grid__types
        if type(index) == str:
            if index not in self.__grid._Grid__titles:
                raise ValueError(_('Invalid or not found column name `%s´.'
                                   ) % index)
            index = self.__grid._Grid__titles.index(index)
        if type(index) in (int, long):
            column = self.__grid._Grid__model_pos[index]
            try:
                formated = self.__grid._Grid__formats[index]
                formated = cf(value, formated if formated else types[index],
                              self.__grid._Grid__decimals[index])
            except ValueError or TypeError:
                PoleLog.log_except()
                message(self.__grid, _("This value could not be"
                                       " converted or formatted.\n\n"
                                       "This value is ignored and the"
                                       " previous value will not change."))
                return
            line = model[self.__path]
            if types[index] in (datetime.time, datetime.datetime,
                                datetime.timedelta):
                formated[0] = cf(formated[0], float)[0]
            elif types[index] == datetime.date:
                formated[0] = cf(formated[0], int)[0]
            if types[index] in (int, float, long, datetime.date, datetime.time,
                                datetime.datetime, datetime.timedelta):
                line[column], line[column + 1] = formated
            elif types[index] == bool:
                line[column] = formated[0]
            else:
                line[column] = formated[1]
            self.__line[0][index], self.__line[1][index] = formated
        else:
            raise TypeError(_('Invalid type of column index or name `' +
                              type(index) + '´.'))

    def path(self):
        return self.__path

    def is_expanded(self):
        return self.__grid.row_expanded(self.__path)


class ComboBoxEntryCompletion(gtk.ComboBoxEntry, gtk.Buildable):
    __gtype_name__ = 'ComboBoxEntryCompletion'

    def __init__(self, *args, **kargs):
        super(ComboBoxEntryCompletion, self).__init__(*args, **kargs)
        self.__completion = gtk.EntryCompletion()
        self.__completion.set_model(self.get_model())
        self.__completion.set_minimum_key_length(1)
        self.__completion.set_text_column(0)
        self.__completion.set_match_func(self.match_func)
        self.__completion.connect('match-selected', self.on_match_selected)

    def do_parser_finished(self, builder):
        self.child.set_completion(self.__completion)
        self.__completion.set_model(self.get_model())

    def config(self, configs):
        configs = [x.strip() for x in configs.split(',')]
        self.__enter_to_tab = "enter_to_tab" in [x.lower() for x in configs]

        # Creating or using float type from PoleUtil.tipos
        have_float = [x for x in configs if x[:5] == "float"]
        if have_float:
            pole_type = PoleUtil.new_float_type(have_float[0])
        # Else search for type in PoleUtil.tipos
        else:
            pole_type = None
            for config in configs:
                if config in PoleUtil.tipos:
                    pole_type = config
                    break

        if pole_type:
            type_info = PoleUtil.tipos[pole_type]
            ptype = PoleUtil.python_tipos[type_info[0]]
            if ptype == str:
                mask = [m for m in type_info[5].split(' ') if len(m) > 0]
                self.__upper = "upper" in mask
                self.__lower = "lower" in mask
                self.__normalize = "normalize" in mask
                self.__limits = [(m[0], m[1], int(m[2:]))
                                 for m in mask if '>' in m or '<' in m]
            self.__characters = type_info[4]
            if '-' in self.__characters:
                self.__characters = re.sub('-', '', self.__characters) + '-'
        else:
            self.__upper = "upper" in configs
            self.__lower = "lower" in configs
            self.__normalize = "normalize" in configs
            self.__limits = None
            self.__characters = None
        self.__pole_type = pole_type

    def set_model(self, model):
        super(ComboBoxEntryCompletion, self).set_model(model)
        self.__completion.set_model(model)

    def match_func(self, completion, key, iter, column=0):
        key = PoleUtil.formatar(key, "Livre Mai").replace(' ', '.*')
        model = completion.get_model()
        text = PoleUtil.formatar(model.get_value(iter, column), "Livre Mai")
        return re.search(key, text)

    def on_match_selected(self, completion, model, iter):
        text = model.get_value(iter, 0)
        self.set_active_text(text)

    def set_active_text(self, text, column=0):
        set_active_text(self, text, column, self.__pole_type)

    def get_active_text(self, column=0):
        return get_active_text(self, column, self.__pole_type,
                               self.__upper, self.__lower, self.__normalize)


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
        self.__old_text = ''
        self.__characters = None
        self.__max_length = 0
        self.__pole_type = None
        self.__limits = []
        self.__insert = False

    def do_parser_finished(self, builder):
        configs = self.get_tooltip_text()
        if configs is None or '|' not in configs:
            return
        configs = [c.replace('0x00', '|')
                   for c in configs.replace('\\|', '0x00').split('|', 1)]
        self.set_tooltip_text(configs[0])
        self.config(configs[1])

    def config(self, configs):
        configs = [x.strip() for x in configs.split(',')]
        self.__enter_to_tab = "enter_to_tab" in [x.lower() for x in configs]

        # Creating or using float type from PoleUtil.tipos
        have_float = [x for x in configs if x[:5] == "float"]
        if have_float:
            pole_type = PoleUtil.new_float_type(have_float[0])
        # Else search for type in PoleUtil.tipos
        else:
            pole_type = None
            for config in configs:
                if config in PoleUtil.tipos:
                    pole_type = config
                    break

        if pole_type:
            type_info = PoleUtil.tipos[pole_type]
            ptype = PoleUtil.python_tipos[type_info[0]]
            if ptype == str and not PoleUtil.tipos[pole_type].combo:
                mask = [m for m in type_info[5].split(' ') if len(m) > 0]
                self.__upper = "upper" in mask
                self.__lower = "lower" in mask
                self.__normalize = "normalize" in mask
                self.__limits = [(m[0], m[1], int(m[2:]))
                                 for m in mask if '>' in m or '<' in m]
            else:
                self.__upper = "upper" in configs
                self.__lower = "lower" in configs
                self.__normalize = "normalize" in configs
                self.__limits = []
            self.__pole_type = pole_type
            self.__characters = type_info[4]
            if '-' in self.__characters:
                self.__characters = re.sub('-', '', self.__characters) + '-'
            # self.__max_length = type_info[1]
            # if self.get_max_length() == self.__max_length:
            #     self.set_max_length(0)
            self.__max_length = self.get_max_length()  # max len from layout
            self.set_max_length(0)  # no max len for formated
            # self.set_width_chars(type_info[1]) # Depends on layout
            self.set_alignment(type_info[8])
        else:
            self.__upper = "upper" in configs
            self.__lower = "lower" in configs
            self.__normalize = "normalize" in configs

    def do_key_press_event(self, event):
        if self.__enter_to_tab and event.keyval in (gtk.keysyms.Return,
                                                    gtk.keysyms.KP_Enter):
            event.keyval = gtk.keysyms.Tab
            # Hardware key code
            keymap = gtk.gdk.keymap_get_default()
            keycode, group, level = keymap.get_entries_for_keyval(event.keyval)[0]
            event.hardware_keycode = keycode
            event.group = group
            event.state = level
        else:
            # super(Editor, self).do_key_press_event(self, event)
            self.__insert = (
                event.keyval in (gtk.keysyms.v, gtk.keysyms.V)
                and (event.state & gtk.keysyms.Control_L
                     or event.state & gtk.keysyms.Control_R)
                or event.keyval == gtk.keysyms.Insert
                and (event.state & gtk.keysyms.Shift_L
                     or event.state & gtk.keysyms.Shift_R))

            gtk.Entry.do_key_press_event(self, event)
            return (event.keyval in (gtk.keysyms.Right, gtk.keysyms.Left))

    def do_changed(self, *args, **kargs):
        if self.__formating or self.get_text() == '' or not self.has_focus():
            return
        pos = self.get_position()
        text = self.get_text().decode('utf-8')
        size = len(text)

        if self.__normalize:
            text = unicodedata.normalize('NFKD',
                                         text).encode('ascii', 'ignore')
        if self.__upper:
            text = text.upper()
        elif self.__lower:
            text = text.lower()

        if self.__pole_type:
            pole_type = PoleUtil.tipos[self.__pole_type][0]
            c = text[pos if pos < size else pos - 1]
            if c == PoleUtil.dp and pole_type == 6:  # decimal point & float
                text = (text[:pos].replace(c, '') +
                        c + text[pos + 1:].replace(c, ''))
            if self.__characters:
                text = re.sub('[^' + self.__characters + ']', '', text)
            if PoleUtil.tipos[self.__pole_type][0] in (3, 6):  # int or float
                s = 1 if text[0:1] in ('+', '-') else 0
                if '-' in text[s:] or '+' in text[s:]:
                    i = min(x for x in (text[s:].find('+'), text[s:].find('-'))
                            if x > -1) + s
                    text = text[i] + text[s:i] + text[i + 1:]
            if PoleUtil.dp in text and pole_type == 6:  # decimal point & float
                i = text.index(PoleUtil.dp)
                text = text[:i + 1] + text[i + 1:].replace(PoleUtil.dp, '')

        elif self.__characters:
            text = re.sub('[^' + self.__characters + ']', '', text)

        self.__formating = True
        self.set_text(text)
        if len(text) != size:
            glib.timeout_add(1, self.set_position, pos - (size - len(text)) + (not self.__insert))
        self.__formating = False

    def do_focus_out_event(self, *args, **kargs):
        if self.get_text() == '':
            # super(Editor, self).do_focus_out_event(self, *args, **kargs)
            gtk.Entry.do_focus_out_event(self, *args, **kargs)
            return
        self.__formating = True
        # if self.get_max_length() == self.__max_length:
        self.set_max_length(0)
        if self.__pole_type:
            self.set_text(PoleUtil.formatar(self.get_text(), self.__pole_type))
        self.__formating = False
        # super(Editor, self).do_focus_out_event(*args, **kargs)
        gtk.Entry.do_focus_out_event(self, *args, **kargs)
        self.__formating = True

    def do_focus_in_event(self, *args, **kargs):
        self.__formating = False
        self.do_changed()
        # super(Editor, self).do_focus_in_event(self, *args, **kargs)
        # if self.get_max_length() == 0:
        self.set_max_length(self.__max_length)
        gtk.Entry.do_focus_in_event(self, *args, **kargs)


class Grid(gtk.TreeView, gtk.Buildable):

    __gtype_name__ = 'Grid'

    def __init__(self, *args):
        super(Grid, self).__init__(*args)
        # self.set_rules_hint(True)
        # self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
        self.set_show_expanders(False)
        self.__updating = False

        self.__titles = []
        self.__types = []
        self.__decimals = []
        self.__editables = []
        self.__with_colors = False

        self.__structurex = False
        self.__sizes = []
        self.__formats = []

        self.__model_types = []

        self.__crud = None
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
                   for c in configs.replace('\\|', '0x00').split('|', 1)]
        self.set_tooltip_text(configs[0])
        self.config(configs[1])

    def config(self, configs):
        configs = [[x.strip() for x in i.split(',')]
                   for i in configs.split('|')]
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
            elif column[1] == 'str':
                types.append(str)
            elif column[1] == 'date':
                types.append(datetime.date)
                decimals.append(PoleUtil.DATE)
            elif column[1] == 'time':
                types.append(datetime.time)
                if (len(column) > 2 and
                        column[2] in ('HOURS_MIN', 'DAYS_HOURS_MIN')):
                    decimals.append(PoleUtil.HOURS_MIN)
                elif (len(column) > 2 and column[2].isdigit() and
                      int(column[2]) in (PoleUtil.TIME, PoleUtil.HOURS,
                                         PoleUtil.DAYS_HOURS,
                                         PoleUtil.HOURS_MIN,
                                         PoleUtil.DAYS_HOURS_MIN)):
                    decimals.append(int(column[2]))
                else:
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
                    elif column[2] == 'HOURS_MIN':
                        decimals.append(PoleUtil.HOURS_MIN)
                    elif column[2] == 'DAYS_HOURS_MIN':
                        decimals.append(PoleUtil.DAYS_HOURS_MIN)
                    else:
                        decimals.append(PoleUtil.DATE_TIME)
                else:
                    decimals.append(PoleUtil.DATE_TIME)
            elif column[1] == 'month':
                types.append(datetime.date)
                decimals.append(PoleUtil.MONTH)
            elif column[1] in ('hours', 'timedelta'):
                types.append(datetime.timedelta)
                if len(column) > 2:
                    if column[2].isdigit():
                        decimals.append(
                            int(column[2])
                            if int(column[2]) in (
                                PoleUtil.DAYS_HOURS, PoleUtil.DAYS_HOURS_MIN,
                                PoleUtil.HOURS_MIN, PoleUtil.HOURS)
                            else PoleUtil.HOURS)
                    elif column[2] == 'DAYS_HOURS':
                        decimals.append(PoleUtil.DAYS_HOURS)
                    elif column[2] == 'DAYS_HOURS_MIN':
                        decimals.append(PoleUtil.DAYS_HOURS_MIN)
                    elif column[2] == 'HOURS_MIN':
                        decimals.append(PoleUtil.HOURS_MIN)
                    else:
                        decimals.append(PoleUtil.HOURS)
                else:
                    decimals.append(PoleUtil.HOURS)
            elif column[1] in PoleUtil.tipos:
                if (column[1] == 'float' and len(column) > 2
                        and column[2].isdigit()):
                    _decimals = str(int(column[2]))
                    pole_type = PoleUtil.new_float_type('float' + _decimals)
                else:
                    pole_type = column[1]
                type_info = PoleUtil.tipos[pole_type]
                types.append(PoleUtil.python_tipos[type_info[0]])
                decimals.append(type_info[2])
                sizes.append(type_info[1])
                formats.append(pole_type)
            else:
                raise TypeError(_('Invalid type `%s´. Expected int, long, bool, float, str, datetime, date, time, month or hours.') % (column[1],))
            if column[1] not in PoleUtil.tipos:
                sizes.append(None)
                formats.append(None)

            if len(column) > 2:
                if column[2].isdigit():
                    if column[1] not in ('date', 'time', 'datetime', 'month', 'hours') + tuple(PoleUtil.tipos):
                        decimals.append(int(column[2]))
                elif column[2] == 'edit':
                    if column[1] not in ('date', 'time', 'datetime', 'month', 'hours') + tuple(PoleUtil.tipos):
                        decimals.append(PoleUtil.local['frac_digits'])
                    editables.append(True)
                elif column[2] not in ('DATE', 'TIME', 'DATE_TIME', 'MONTH', 'HOURS', 'DAYS_HOURS', 'HOURS_MIN', 'DAYS_HOURS_MIN'):
                    raise ValueError(_("Invalid value for decimals ou editable `%s´. Expected digits, 'DATE', 'TIME', 'DATE_TIME', 'MONTH', 'HOURS', 'DAYS_HOURS', 'HOURS_MIN' or 'DAYS_HOURS_MIN' for decimals or 'edit' for editable.") % (column[2],))
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
                    decimals.append(PoleUtil.local['frac_digits'])
                editables.append(False)
        self.structure(titles, types, decimals, editables, with_colors, sizes, formats)

    def structure(self, titles, types, decimals=None, editables=None,
                  with_colors=False, sizes=None, formats=None):
        if not decimals:
            decimals = [PoleUtil.local['frac_digits']] * len(titles)
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
        self.__structurex = bool(sizes or formats)

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
            lb = gtk.Label(title.decode('string_escape'))
            lb.show()
            column = gtk.TreeViewColumn()
            column.set_widget(lb)
            column.set_resizable(True)
            self.append_column(column)
            if t == bool:
                cell = gtk.CellRendererToggle()
                cell.set_property('activatable', editable)
                cell.connect('toggled', self.__editable_callback, None, len(self.__model_pos) - 1)
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
                column.add_attribute(cell, "text", model_pos + (t in (int, long, float, datetime.date, datetime.time, datetime.datetime, datetime.timedelta)))
            column.set_sort_column_id(model_pos)
            if t in (int, long, float):
                cell.set_property("xalign", 1.)
                column.set_property("alignment", 1.)
                model_pos += 1
            elif t in (datetime.date, datetime.time, datetime.datetime, datetime.timedelta):
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
                column.add_attribute(cell, "foreground",
                                     len(self.__model_types) - 2)
            column.add_attribute(cell, "cell-background",
                                 len(self.__model_types) - 1)
        self.append_column(column)

    def get_structure(self):
        return (self.__titles, self.__types, self.__decimals, self.__editables,
                self.__with_colors, self.__sizes, self.__formats)

    @try_function
    def __editable_callback(self, renderer, path, result, column):
        if self[path][column][1] == result:
            return
        path_cursor = self.get_cursor()[0]
        if path_cursor:
            path_cursor = ':'.join(str(i) for i in path_cursor)
        if path != path_cursor:
            return
        if isinstance(renderer, gtk.CellRendererToggle):
            result = not self[path][column][0]
        if self.edit_callback is not None:
            result = self.edit_callback(result, self, path, column,
                                        self.__titles[:], self.__types[:],
                                        self.__decimals[:], self.__with_colors)
        if self.__crud:
            result = self.crud_update({self.__fields[column]:
                                       None if result is None or result == ''
                                       else cf(result, self.__formats[column]
                                               if self.__formats[column]
                                               else self.__types[column],
                                               self.__decimals[column])[0]})
        if result is not None:
            self[path][column] = result
        pos = self.get_cursor()
        if not pos[0]:
            pos = (path, pos[1])
        self.set_cursor_on_cell(*pos)

    def __finish_editing(self, editor, event, popup):
        key = event.keyval
        if key == gtk.keysyms.Escape:
            editor.props.text = self.__old_editing_text
            popup.quit()
        elif key in (gtk.keysyms.KP_Enter, gtk.keysyms.Return):
            popup.quit()

    def __start_editing_callback(self, renderer, editable, path, column):
        self.set_cursor_on_cell(*self.get_cursor())
        x, y = self.get_bin_window().get_origin()
        area = self.get_cell_area(path, self.get_column(column))
        size = (area[2], area[3])
        self.__old_editing_text = new = editable.props.text
        tx = self.__formats[column]
        if self.__types[column] in (datetime.date, datetime.datetime,
                                    datetime.time, datetime.timedelta):
            position = (x + area[0], y + area[1] + area[3])
            c = Calendar(editable, tx if tx else self.__decimals[column])
            r = c.run(position, transient_for=self)
            if r is None:
                new = ''
            elif r:
                new = editable.props.text
            c.destroy()
        else:
            old = cf(self.__old_editing_text,
                     tx if tx else self.__types[column],
                     self.__decimals[column])[0]
            position = (x + area[0], y + area[1])
            p = PopupWindow()
            if (self.__crud and self.__joins and
                    re.search(r'\W%s(\W|\Z)' % self.__fields[column],
                              self.__joins, flags=re.I)):
                area2 = self.get_cell_area(path, self.get_column(column + 1))
                size = (area[2] + area2[2] + 5, area[3])
                model = gtk.ListStore(str, self.__types[column])
                e = ComboBoxEntryCompletion(model)
                e.do_parser_finished(None)
                join = re.split(r'\s*(?:(?:inner|left|right)\s+){0,1}join\s',
                                self.__joins, flags=re.I)[1:]
                join = filter(lambda x: self.__fields[column].lower()
                              in x.lower(), join)[0]
                tab, where = re.split(r'\son\s', join, flags=re.I)
                key = filter(lambda x: x, re.findall(
                    r'([^\s]*)\s*=\s*{field}|{field}\s*=\s*([^\s]*)'.
                    format(field=self.__fields[column]),
                    where, flags=re.I)[0])[0]
                where = re.sub(
                    r'[^\s]*\s*[^\s]*\s*=\s*{field}\s*[^\s]*\s*|'
                    r'[^\s]*\s*{field}\s*=\s*[^\s]*\s*[^\s]*\s*'.
                    format(field=self.__fields[column]), '',
                    where, flags=re.I)
                where = ' where ' + where if where else ''
                # ▷⤐⤘⟿⤳⥤⤑⥲⬳⤇⟹⇛⇝
                # ➊🖉⛔👈🛇💻🕲📵🔞🚫🚭🚳🚷⛔🐧📂📖📬📭🖊🖋🚏🗄🧲🔒🖆🔏🔑
                descr = key + " || ' ⤳ ' || " + self.__fields[column + 1]
                sql = ("select {descr}, {key} from {tab}{where} order by 2".
                       format(key=key, descr=descr, tab=tab, where=where))
                cursor = self.__crud.cursor()
                cursor.execute(sql)
                gobject.timeout_add(1, load_store, e, cursor, old, 1)
                e.child.connect('key-press-event', self.__finish_editing, p)
            elif tx and PoleUtil.tipos[tx].combo:
                size = (size[0], size[1] + 5)
                model = gtk.ListStore(str, self.__types[column])
                for opc in PoleUtil.tipos[tx].mascara[1:]:
                    model.append(((opc[0] + ' ⤳ ' + opc[1] if len(opc) > 1
                                   else opc[0]), opc[0]))
                e = gtk.ComboBox(model)
                cell = gtk.CellRendererText()
                e.pack_start(cell, True)
                e.add_attribute(cell, 'text', 0)
                gobject.idle_add(e.popup)
            else:
                e = Editor()
                e.connect('key-press-event', self.__finish_editing, p)
            if not tx or not PoleUtil.tipos[tx].combo:
                if tx:
                    e.config(tx)
                    # e.set_max_length(self.__sizes[column])
                elif self.__types[column] in (int, long):
                    e.config("int")
                elif self.__types[column] == float:
                    e.config("float" + str(self.__decimals[column]))
            # else:
            #    e.config("upper,normalize")
            e.props.has_frame = False
            e.show()
            p.add(e)
            if isinstance(e, Editor):
                e.props.text = self.__old_editing_text
            else:
                if not isinstance(e, ComboBoxEntryCompletion):
                    set_active_text(e, old, 1)

            # Out click do cancel
            # if p.run(self, size, position):
            #    new = cf(e.props.text, self.__types[column],
            #             self.__decimals[column])[1]

            p.run(self, size, position)

            if not isinstance(e, Editor):
                def new_loop_quit():
                    if e.get_property('popup-shown'):
                        return True
                    if (datetime.datetime.now() - t).total_seconds() < 0.25:
                        e.popup()
                        return True
                    p._PopupWindow__loop.quit()
                    return False
                while e.get_property('popup-shown'):
                    if isinstance(e, ComboBoxEntryCompletion):
                        p.show_all()
                    update_ui()
                    t = datetime.datetime.now()
                    gobject.timeout_add(100, new_loop_quit)
                    p._PopupWindow__loop.run()

            text = (e.props.text if isinstance(e, Editor) else
                    e.get_active_text(1) if isinstance(e, ComboBoxCompletion)
                    else get_active_text(e, 1))
            if tx:
                new = cf(text, tx)[1]
            else:
                new = cf(text, self.__types[column],
                         self.__decimals[column])[1]
            p.destroy()

        # Need out of this function to finish editing mode
        glib.timeout_add(1, self.__remove_editable, editable, new)

    def __remove_editable(self, editable, new):
        if new != self.__old_editing_text:
            editable.set_text(new)
        editable.editing_done()
        editable.remove_widget()
        editable.destroy()
        self.grab_focus()

    def clear(self):
        model = self.get_model()
        if model:
            model.clear()
            model.set_sort_column_id(-2, 0)
            return
        raise ValueError(_('No columns structure defined.'))

    def add_data(self, data, into_path_or_iter=None,
                 with_child=False, model=None,
                 position=None, before=None, after=None):
        if data in (None, [], [[]], ''):
            return into_path_or_iter
        if model is None:
            model = self.get_model()
        if not model:
            raise ValueError(_('No columns structure defined.'))
        if into_path_or_iter is not None:
            self.set_show_expanders(True)
            if type(into_path_or_iter) in (str, int, long):
                iter = model.get_iter_from_string(str(into_path_or_iter))
            elif type(into_path_or_iter) in (tuple, list):
                iter = model.get_iter(tuple(into_path_or_iter))
            elif isinstance(into_path_or_iter, gtk.TreeIter):
                iter = into_path_or_iter
            else:
                raise TypeError(_('Type `' + str(type(into_path_or_iter)).
                                  split("'")[1] + '´of path is not valid.'
                                  ' Expected str, int, long, tuple,'
                                  ' list (path) or gtk.TreeIter.'))
            if not model.iter_is_valid(iter):
                raise ValueError(_('Path or iter is'
                                   ' not valid for this model.'))
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
                if t in (int, long, float, datetime.date, datetime.time, datetime.datetime, datetime.timedelta):
                    try:
                        f = cf(field, tx if tx else t, decimals)
                        if t in (datetime.time, datetime.datetime, datetime.timedelta):
                            f[0] = cf(f[0], float)[0]
                        elif t == datetime.date:
                            f[0] = cf(f[0], int)[0]
                        formated += f
                    except ValueError or TypeError:
                        PoleLog.log_except()
                        if t in (int, long, float):
                            formated += [t(0), field]
                        else:
                            formated += [0, field]
                        error = True
                elif t == bool:
                    try:
                        formated.append(cf(field, tx if tx else t)[0])
                    except ValueError or TypeError:
                        PoleLog.log_except()
                        formated.append(False)
                        error = True
                elif t == str and type(field) in (datetime.date, datetime.datetime, datetime.time, datetime.timedelta):
                    try:
                        formated.append(cf(field, tx if tx else t)[1])
                    except (ValueError, TypeError):
                        PoleLog.log_except()
                        formated.append(_('Error!'))
                        error = True
                else:
                    formated.append(cf(field, tx if tx else t)[1])
            if self.__with_colors:
                formated += register[-2:]

            # self.freeze_child_notify()
            # self.set_model(None)

            # new_model = gtk.TreeStore(*[m.get_column_type(i)
            #                             for i in range(m.get_n_columns())])
            order_by = model.get_sort_column_id()
            if order_by[0] is not None:
                model.set_sort_column_id(-2, 0)
                update_ui()

            if not (position or before or after):
                last_iter = model.append(iter, formated)
            elif position:
                last_iter = model.insert(iter, position, formated)
            elif before:
                last_iter = model.insert_before(iter, before, formated)
            elif after:
                last_iter = model.insert_after(iter, after, formated)
            if with_child:
                model.append(last_iter, null_line)

            if order_by[0] is not None:
                model.set_sort_column_id(*order_by)

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
            if t in (int, long, float, datetime.date, datetime.time, datetime.datetime, datetime.timedelta):
                try:
                    f = cf(field, tx if tx else t, decimals)
                    if t in (datetime.time, datetime.datetime, datetime.timedelta):
                        f[0] = cf(f[0], float)[0]
                    elif t == datetime.date:
                        f[0] = cf(f[0], int)[0]
                    formated += f
                except ValueError or TypeError:
                    PoleLog.log_except()
                    if t in (int, long, float):
                        formated += [t(0), field]
                    else:
                        formated += [0, field]
                    error = True
            elif t == bool:
                try:
                    formated.append(cf(field, tx if tx else t)[0])
                except ValueError or TypeError:
                    PoleLog.log_except()
                    formated.append(False)
                    error = True
            else:  # elif t == str and type(field) in (datetime.date, datetime.datetime):
                try:
                    formated.append(cf(field, tx if tx else t)[1])
                except (ValueError, TypeError):
                    PoleLog.log_except()
                    formated.append(_('Error!'))
                    error = True
            # else:
            #     formated.append(cf(field, tx if tx else t)[1])
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
        for t, tx, decimals in zip(self.__types, self.__formats, self.__decimals):
            if t in (datetime.datetime, datetime.date, datetime.time, datetime.timedelta):
                values.append(cf(model_line[col+1], tx if tx else t, decimals)[0])
            else:
                values.append(model_line[col])
            if t in (int, long, float, datetime.datetime, datetime.date, datetime.time, datetime.timedelta):
                formateds.append(model_line[col+1])
                col += 2
            elif t is bool and bool_to_str:
                formateds.append(cf(model_line[col], t)[1])
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
            return tuple([GridRow(self, i, self.__get_line(i, True), self.__with_colors) for i in range(*index)])
        if type(path) in (tuple, list) and type(path[0]) in (tuple, list):
            return tuple([GridRow(self, i, self.__get_line(i, True), self.__with_colors) for i in path])
        return GridRow(self, path, self.__get_line(path, True), self.__with_colors)
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

    def __setitem__(self, path_iter, value):
        self.update_line(path_iter, value)

    def __delitem__(self, path_iter):
        self.remove(path_iter)

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
            csv.append('\t'.join(('' if x is None
                                  else x.replace('\n', '\\n').
                                  replace('\t', '\\t'))
                                 for x in fields))
            if not only_expanded_rows or self.row_expanded(line.path):
                self.__export_csv_children(line.iterchildren(), csv,
                                           cols, only_expanded_rows)

    def get_csv(self, only_expanded_rows=True):
        csv = ['\t'.join(self.__titles)]
        cols = len(self.__titles)
        model = self.get_model()
        self.__export_csv_children(model, csv, cols, only_expanded_rows)
        return '\n'.join(csv) + '\n'

    def export_csv(self, filename=None, only_expanded_rows=True):
        csv = self.get_csv(only_expanded_rows)
        if filename:
            if isinstance(filename, (file, StringIO.StringIO)):
                filename.write(csv)
            else:
                with open(filename, 'w') as f:
                    f.write(csv)
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

    def live_load(self, cursor, clean=True, lines=100, parent_lock=None,
                  into_path_or_iter=None, with_child=False, warn=False):
        if self.__updating:
            if warn:
                warning(self, _("Please wait..."))
            return
        self.__updating = True
        if clean:
            self.clear()

        model = self.get_model()
        order_by = model.get_sort_column_id()
        if order_by[0] is not None:
            self.set_model(None)
            model.set_sort_column_id(-2, 0)

        records = True
        pos = 0
        if parent_lock and not isinstance(cursor, (tuple, list)):
            progress = Processing(parent_lock, _("Getting lines..."))
            data = []
            progress.pulse()
            try:
                _lines = cursor.fetchmany(lines)
                while _lines:
                    data.extend(_lines)
                    progress.pulse()
                    del _lines
                    _lines = cursor.fetchmany(lines)
                cursor = data
            finally:
                del data
                progress.close()
        total = len(cursor) if isinstance(cursor, (tuple, list)) else 0
        if parent_lock:
            progress = Processing(parent_lock, _("Loading lines..."),
                                  lines, total, True)
        else:
            change_mouse_pointer(self, 'watch')
        try:
            while records:
                if isinstance(cursor, (tuple, list)):
                    self.add_data(cursor[pos:pos + lines],
                                  into_path_or_iter=into_path_or_iter,
                                  with_child=with_child, model=model)
                    pos += lines
                    records = pos < total
                else:
                    records = cursor.fetchmany(lines)
                    self.add_data(records,
                                  into_path_or_iter=into_path_or_iter,
                                  with_child=with_child, model=model)
                if parent_lock:
                    if not progress.pulse():
                        break
                else:
                    update_ui()
        finally:
            if parent_lock:
                progress.close()
            else:
                change_mouse_pointer(self, None)
        self.__updating = False

        if order_by[0] is not None:
            self.set_model(model)
            model.set_sort_column_id(*order_by)

    def selected(self):
        s = self.get_selection()
        if not s:
            return s
        if s.get_mode() == gtk.SELECTION_MULTIPLE:
            s = s.get_selected_rows()[1]
            if not s:
                return s
            return s[0]
        return s.get_selected()[1]

    def selected_rows(self):
        return self.get_selection().get_selected_rows()[1]

    def select(self, line_or_column, column_value=Exception, follow=True):

        def _select(children, column_values):
            for line in children:
                if all(self[line.iter][c][0] == v for c, v in column_values):
                    self.set_cursor(line.path)
                    break
                _select(line.iterchildren(), column_values)

        if column_value != Exception:
            if not isinstance(line_or_column, (tuple, list)):
                line_or_column = [line_or_column]
                column_value = [column_value]
            _select(self.get_model(), zip(line_or_column, column_value))
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
        if not key:
            return True
        value = model[iter][column]
        where = ('start' if key[0] == '<'
                 else 'end' if key[0] == '>'
                 else 'in')
        if where != 'in':
            key = key[1:]
        if isinstance(value, bool):
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
            decimal = PoleUtil.local['decimal_point']
            if decimal in key:
                key = '.'.join(re.sub('[^0-9]', '', k)
                               for k in key.split(decimal, 1))
            else:
                key = re.sub('[^0-9]', '', key)
        else:
            value = PoleUtil.normalize(value).lower()
            key = PoleUtil.normalize(key).lower()

        # return False when match
        if where == 'start':
            return key != value[:len(key)]
        if where == 'end':
            return key != value[-len(key):]
        return key not in value

    def cell_clicked(self, widget, event):
        pos = self.get_path_at_pos(int(event.x), int(event.y))
        if pos:
            column = self.get_columns().index(pos[1])
            self.set_search_column(column)

    def crud(self, db_connection, args,
             create_enabled=True, delete_enabled=True):
        self.__crud = db_connection
        if not self.__crud:
            return
        self.__crud_create_enabled = create_enabled
        self.__crud_delete_enabled = delete_enabled

        self.config('|'.join(args['config']))
        self.__table = args['table']
        self.__joins = args.get('joins')
        self.__joins = " " + self.__joins if self.__joins else ""
        self.__fields = [field.split('@')[0] for field in args['fields']]
        # + -> key | * -> ignored for create | = -> unique info | - -> not null
        self.__keys = [field.strip('*+-=') for field in self.__fields
                       if '+' in (field.lstrip('*-=')[0],
                                  field.rstrip('*-=')[-1])]
        self.__ignoreds = [field.strip('*+-=') for field in self.__fields
                           if '*' in (field.lstrip('+-=')[0],
                                      field.rstrip('+-=')[-1])]
        self.__uniques = [field.strip('*+-=') for field in self.__fields
                          if '=' in (field.lstrip('+-*')[0],
                                     field.rstrip('+-*')[-1])]
        self.__not_null = [field.strip('*+-=') for field in self.__fields
                           if '-' in (field.lstrip('+=*')[0],
                                      field.rstrip('+=*')[-1])]
        self.__fields = [field.strip('*+-=').split('@', 1)[0]
                         for field in self.__fields]
        self.__requests = [field for field in self.__fields
                           if field not in self.__ignoreds]
        self.__where = args.get('where')
        self.__group = args.get('group')
        self.__group = " group by " + self.__group if self.__group else ""
        self.__order = args.get('order')
        self.__order = " order by " + self.__order if self.__order else ""
        defaults = list(args.get('defaults', []))
        defaults += [('c@' + field.strip('*+-=')).split('@', 2)
                     for field in args['fields'] if '@' in field]
        self.__use_gridform = args.get('grid_form')

        # defatuls: [['<cru>', '<field>', <value>], ...]
        # <cru>: 'c' for create, 'r' for read and/or 'u' for update
        self.__defaults_create = {}  # will be initial value of field
        self.__defaults_read = {}    # will do a 'and' filter for reading
        self.__defaults_update = {}  # will disable field editing
        for cru, field, value in defaults:
            if 'c' in cru:
                self.__defaults_create[field] = value
            if 'r' in cru:
                self.__defaults_read[field] = value
            if 'u' in cru:
                self.__defaults_update[field] = value

        self.__nicks = [field.split('.')[0] if '.' in field else ''
                        for field in self.__fields]
        split = self.__table.split()
        self.__main_nick = (split[1]
                            if len(split) > 1 and split[1] in self.__nicks
                            else '')
        self.__main_table = split[0]
        self.__main_fields_map = [nick == self.__main_nick
                                  for nick in self.__nicks]
        self.__main_fields = [
            field for field, main in zip(self.__fields, self.__main_fields_map)
            if main]
        self.__foreign_keys = [
            field for field, xfk in zip(self.__fields,
                                        self.__main_fields_map[1:]) if not xfk]
        if not self.__keys:
            self.__keys = self.__main_fields
        self.__main_where = " and ".join(field + ' = :' + str(n)
                                         for n, field in
                                         enumerate(self.__keys))

        self.__join_fields = {}
        joins = [re.split(r'\s+on\s+', join, maxsplit=1, flags=re.I)
                 for join in re.split(
                    r'\s*(?:(?:inner|left|right)\s+){0,1}join\s+',
                    self.__joins, flags=re.I)[1:]]
        for n, (main, field) in enumerate(zip(self.__main_fields_map,
                                              self.__fields)):
            if not main:
                continue
            # key field of foreign table
            key = None
            for tab, where in joins:
                key = re.findall(
                    r'([^\s]*)\s*=\s*{field}|{field}\s*=\s*([^\s]*)'.
                    format(field=field), where, flags=re.I)
                if key:
                    key = ''.join(key[0])
                    break
            if not key:
                continue
            # Remove foreign key from auxiliar where clause
            where = re.sub(
                r'[^\s]*\s*[^\s]*\s*=\s*{field}\s*[^\s]*\s*|'
                r'[^\s]*\s*{field}\s*=\s*[^\s]*\s*[^\s]*\s*'.
                format(field=field), '',
                where, flags=re.I)
            where = ' where ' + where if where else ''
            # ▷⤐⤘⟿⤳⥤⤑⥲⬳⤇⟹⇛⇝
            descr = key + " || ' ⤳ ' || " + self.__fields[n + 1]
            sql = ("select {descr}, {key} from {tab}{where} order by 2".
                   format(key=key, descr=descr, tab=tab, where=where))
            self.__join_fields[field] = sql

    def crud_enable_create(self, enable=True):
        self.__crud_create_enabled = enable

    def crud_enable_delete(self, enable=True):
        self.__crud_delete_enabled = enable

    def crud_create(self, pre_fixed_values=None):
        if not self.__crud or not self.__crud_create_enabled:
            return False

        # Initial values from grid selected row or '' for each field
        values = self.selected()
        if values:
            values = list(self[values][:][1])
        else:
            values = [''] * len(self.__fields)

        # Empty ignored fields
        for field in self.__ignoreds:
            values[self.__fields.index(field)] = ''

        # Default create values override initial values
        for field, value in self.__defaults_create.items():
            values[self.__fields.index(field)] = get_value(value)

        # Pre-fixed values override others values
        if isinstance(pre_fixed_values, (list, tuple)):
            values = list(pre_fixed_values) + values[len(pre_fixed_values):]
        elif isinstance(pre_fixed_values, dict):
            for k, v in pre_fixed_values:
                if k in self.__fields:
                    values[self.__fields.index(k)] = v
                else:
                    values[self.__titles.index(k)] = v

        # Empty None values
        for i in range(len(values)):
            if values[i] is None:
                values[i] = ''

        # For each field, create FormModel line or ask the value
        form_lines = []
        for i, (main_field, field) in enumerate(zip(self.__main_fields_map,
                                                    self.__fields)):
            if not main_field:
                if i and self.__fields[i - 1] in self.__join_fields:
                    form_lines[-1] = form_lines[-1]._replace(
                        icons=form_lines[-1].icons + '🧲',
                        join=self.__join_fields[self.__fields[i - 1]])
                else:
                    form_lines[-1] = form_lines[-1]._replace(
                        icons=form_lines[-1].icons + '⚙🔏', editable=False)
                continue
            # ➊🖉⛔👈🛇💻🕲📵🔞🚫🚭🚳🚷⛔🐧📂📖📬📭🖊🖋🚏🗄🧲🔒🖆🔏🔑
            # + -> 🔑  |  * -> 🔏  |  - -> 👈  |  = -> ➊
            # 🧲 -> foreign key  |  🖆  -> edited | ⚙ -> calculeted
            icons = ('<span color="Orange">' +
                     ' '.join(('🔑' if field in self.__keys else
                               '👈' if field in self.__not_null else '',
                               '🔏' if field in self.__ignoreds else '',
                               '➊' if field in self.__uniques else '')) +
                     '</span>')
            form_lines.append(FormModel(label=self.__titles[i], text=values[i],
                                        type=self.__types[i].__name__,
                                        decimals=self.__decimals[i],
                                        pole_type=self.__formats[i],
                                        key=False, icons=icons,
                                        editable=field not in self.__ignoreds))
            if field in self.__requests:
                resp, txt = input_dialog(self, self.__titles[i] + '  ' + icons,
                                         self.__formats[i] if self.__formats[i]
                                         else (self.__types[i].__name__ +
                                               str(self.__decimals[i])),
                                         values[i])
                if resp != gtk.RESPONSE_OK:
                    return
            else:
                txt = values[i]
            values[i] = ('' if txt == '' else
                         cf(txt, self.__formats[i] if self.__formats[i] else
                            self.__types[i], self.__decimals[i])
                         [self.__types[i] == bool])
        values = [v for v, m in zip(values, self.__main_fields_map) if m]

        create_fields, values = zip(*[
            (field, value) for field, value in zip(self.__main_fields, values)
            if value is not None and value != ''])

        create_sql = (
            "insert into " + self.__main_table + " " + self.__main_nick +
            " (" + ", ".join(create_fields) + ") values (:" +
            ", :".join(str(n) for n in range(len(create_fields))) + ")")

        cursor = self.__crud.cursor()
        try:
            cursor.execute(create_sql, values)
            self.__crud.commit()
        except Exception:
            self.__crud.rollback()
            cursor.close()
            raise

        where = " and ".join(field + ' = :' + str(n)
                             for n, field in enumerate(create_fields))
        where, values = self.__crud_null_correction(where, values)
        sql = ("select " + ", ".join(self.__fields) +
               " from " + self.__table + self.__joins +
               " where " + where + self.__group)
        cursor.execute(sql, values)
        try:
            self.select(self.add_data(cursor.fetchall()[-1]))
        except Exception:
            PoleLog.log_except()
        cursor.close()

    def crud_read(self, where=None):
        if not self.__crud:
            return False

        line_key_value = self.selected()
        if line_key_value:
            line_key_value = self[line_key_value][0][0]

        if not where:
            where = get_value(self.__where)
            if not where:
                where = ''
                for field, value in self.__defaults_read.items():
                    where += field + " = '" + get_value(value) + "'"
            if isinstance(self.__where, (Grid, GridRow, gtk.TreeView)):
                where = ("{%s} = '%s'" % (self.__where._Grid__titles[0], where)
                         if where else '1=2')

        if where == '?':
            detail(self, _("Filter help"),
                   _("The filter must be in the format:\n\n"
                     "{{column}}|field|expression operator value\n"
                     "[junction {{column}}|field|expression operator value"
                     " ...]\n"
                     "\nOperators:\n{signs}\n{ops}\n"
                     "\nJunctions:\n{joins}\n"
                     "\nDate keywords:\n{dates}\n"
                     "\nExamples:\n"
                     "{{Code}} < 100 and {{Description}} = \"CABO*AC*5?MM*\"\n"
                     "{{Description}} = null\n"
                     "{{Date}} is not null\n"
                     "length({{Description}}) < 5\n"
                     "substr({{Date}}, 4, 4) = '2018'\n"
                     "to_number(substr({{Date}}, 4, 4)) <= 2017\n"
                     "{{Date}} is today\n"
                     "{{Date}} was yesterday\n"
                     "trunc({{Date}}) = '18/04/2019'\n"
                     "\nSee SQL expressions in:\n"
                     "http://pgdocptbr.sourceforge.net/pg80/functions.html").
                   format(signs=' | '.join(sign_ops),
                          ops=' | '.join(sorted(o.replace(r'\s*', ' ')
                                                for o in re_ops[::2])),
                          joins=' | '.join(j.replace(r'\s*', ' ')
                                           for j in re_joins[::2]),
                          dates=' | '.join(d.replace(r'\s*', ' ')
                                           for d in re_dts[::2])),
                   _("Information"))
            return

        if where:
            for title, field in zip(self.__titles, self.__fields):
                where = where.replace('{' + title + '}', ' %s ' % field)
            i = e = 0
            parts = []
            part = left = []
            right = []
            dt_filter = join = op = None
            while e < len(where):
                # group 0 => string quote
                # group 1 => operator
                # group 2 => keyword separator at start
                # group 3 => keyword
                # group 4 => keyword separator at end
                x = re_filter.search(where[e:])
                if not x and not op:
                    raise Exception(_('Filter mistake!'))
                if not x:
                    s = len(where)
                    break
                quote, operator, sep1, keyword, sep2 = x.groups()
                s = x.start() + e
                e += x.end() - bool(sep2)
                if keyword:
                    keyword = re.sub(r'\s+', '', keyword.lower())
                if quote:
                    part.append(where[i:s])
                    s = e - 1
                    while True:
                        x = re.search(quote, where[e:])
                        if not x:
                            raise Exception(_('String mistake! %s at %i.') %
                                            (quote, s))
                        e += x.end()
                        if where[e - 2] != '\\':
                            break
                    value = (where[s + 1:e - 1].
                             replace('%', '\\%').replace('_', '\\_').
                             replace('\\*', '\0').replace('\\?', '\1').
                             replace('\\"', '"').replace("\\'", "'").
                             replace("'", "''").
                             replace('*', '%').replace('?', '_').
                             replace('\0', '*').replace('\1', '?'))
                    part.append("'" + value + "'")
                elif operator or keyword in trans_ops:
                    left.append(where[i:s] + (sep1 if sep1 else ''))
                    if not ''.join(left).strip():
                        raise Exception(_('Left side mistake!'))
                    op = trans_ops[operator if operator else keyword]
                    part = right
                    if op[-4:] == 'null':
                        op = op[:-4]
                        part.append('null')
                    if op in ('was not', 'will not be'):
                        op = 'is not'
                    elif op in ('was', 'will be'):
                        op = 'is'
                elif keyword in trans_dts:
                    part.append(where[i:s] + sep1)
                    dt_filter = trans_dts[keyword]
                    if dt_filter[:8] == 'between ':
                        d1, d2 = dt_filter[8:].split(' and ')
                        if not op or op in ('in', 'not in', 'between',
                                            '>', '>=', '<') and not join:
                            part.append(d1)
                        elif op == '<=' or op == 'between' and join:
                            part.append(d2)
                        elif 'not' in op or op == '!=':
                            op = 'not between'
                            join = 'and'
                            part.extend((d1, join, d2))
                        else:
                            op = 'between'
                            join = 'and'
                            part.extend((d1, join, d2))
                else:  # join
                    if dt_filter and join:
                        part.insert(-2, where[i:s] + sep1)
                    part.append(where[i:s] + sep1)
                    if not op:
                        part.append(keyword)
                        continue
                    if 'between' in op.lower() and not join:
                        join = trans_joins.get(keyword, keyword)
                        if join != 'and':
                            raise Exception(_('Between operator fail!'))
                        part.append(join)
                        i = e
                        continue

                    right = ' '.join(trans_dts.get(x, x)
                                     for x in right).strip()
                    if not right:
                        raise Exception(_('Right side mistake!'))
                    left = ' '.join(trans_dts.get(x, x) for x in left).strip()
                    if right[0] == "'" and ('%' in right or '_' in right):
                        if op == '=':
                            op = 'like'
                        elif op in ('!=', '<>', '≠'):
                            op = 'not like'
                    if 'like' in op.lower():
                        p = right.rfind("'") + 1
                        right = right[:p] + " escape '\\'" + right[p:]
                    elif right.lower() in (_('null'), 'null'):
                        if 'is' not in op:
                            op = ('is' if op in ('=', 'was', 'will be')
                                  else 'is not')
                        right = 'null'
                    elif op in ('is not', 'was not', 'will not be'):
                        op = '!='
                    elif op in ('is', 'was', 'will be'):
                        op = '='
                    join = trans_joins.get(keyword, keyword)
                    parts.append(' '.join((left, op, right, join)))
                    part = left = []
                    right = []
                    dt_filter = op = join = None
                i = e
            if dt_filter and join:
                right.insert(-2, where[i:])
            right.append(where[i:])
            right = ' '.join(trans_dts.get(x, x) for x in right).strip()
            if not right:
                raise Exception(_('Right side mistake!'))
            left = ' '.join(trans_dts.get(x, x) for x in left).strip()
            if right[0] == "'" and ('%' in right or '_' in right):
                if op in ('=', 'is', 'was', 'will be'):
                    op = 'like'
                elif op in ('!=', '<>', '≠',
                            'is not', 'was not', 'will not be'):
                    op = 'not like'
            if 'like' in op.lower():
                p = right.rfind("'") + 1
                right = right[:p] + " escape '\\'" + right[p:]
            elif right.lower() in (_('null'), 'null'):
                if 'is' not in op:
                    op = ('is' if op in ('=', 'was', 'will be')
                          else 'is not')
                right = 'null'
            elif op in ('is not', 'was not', 'will not be'):
                op = '!='
            elif op in ('is', 'was', 'will be'):
                op = '='
            parts.append(' '.join((left, op, right)))
            where = re.sub(r'\%s' % PoleUtil.dp + r'([0-9])',
                           r'.\1', ' '.join(parts))
            where = re.sub(r'\s+', ' ', where).replace('( ', '(')

        sql = ("select " + ", ".join(self.__fields) +
               " from " + self.__table + self.__joins +
               (" where " + where if where else "") +
               self.__group + self.__order)
        print '-' * 100
        # print sql
        # print '.' * 100
        print 'where:', where
        print '-' * 100
        self.clear()
        cursor = self.__crud.cursor()
        change_mouse_pointer(self, 'watch')
        try:
            cursor.execute(sql)
        except Exception:
            change_mouse_pointer(self, None)
            raise
        change_mouse_pointer(self, None)
        self.live_load(cursor, parent_lock=self)
        cursor.close()
        if line_key_value:
            self.select(0, line_key_value)

    def crud_update(self, update_fields_values):
        # Default update values override initial values
        for field, value in self.__defaults_update.items():
            update_fields_values[field] = get_value(value)

        return self.crud_delete('update', update_fields_values)

    def __crud_null_correction(self, where, args):
        args = self.__crud_bool_time_correction(args)
        for i in range(len(args) - 1, -1, -1):
            if args[i] == '':
                del args[i]
                where = where.replace('= :%i' % i, 'is null')
        return where, args

    def __crud_bool_time_correction(self, values):
        return [cf(v, bool)[1] if isinstance(v, bool) else
                cf(v, datetime.datetime)[0] if isinstance(v, datetime.time)
                else v for v in values]

    def crud_delete(self, mode='delete', update_fields_values={}):
        if not self.__crud or (mode == 'delete'
                               and not self.__crud_delete_enabled):
            return

        line = self.selected()
        if not line:
            return

        if question(self, _("Do you really want %s?") %
                    (_('to update') if mode == 'update' else
                     _('to delete'))) != gtk.RESPONSE_YES:
            return

        sql_args = ['' if showed == '' else value
                    for field, value, showed in
                    zip(self.__fields, *self[line][:]) if field in self.__keys]

        where, args = self.__crud_null_correction(self.__main_where, sql_args)

        if mode == 'update':
            update_fields, update_values = [list(x) for x in
                                            zip(*update_fields_values.items())]
            for field in self.__main_fields:
                data = self.get_data(field)
                if data:
                    if field not in update_fields:
                        update_fields.append(field)
                        update_values.append(get_value(data))
            update_values = self.__crud_bool_time_correction(update_values)
        else:
            update_fields, update_values = [[], []]

        n_main_fields = len(self.__main_fields)

        sql = (mode + " " + self.__main_table + " " + self.__main_nick +
               (" set " + ", ".join(field + " = :" + str(n + n_main_fields)
                                    for n, field in enumerate(update_fields))
                if mode == 'update' else "") +
               " where " + where)

        cursor = self.__crud.cursor()
        try:
            cursor.execute(sql, update_values + args)
            lines = cursor.rowcount
            self.__crud.rollback()
        except Exception:
            self.__crud.rollback()
            cursor.close()
            raise
        cursor.close()

        if not lines:
            error(self, _('No lines found for %s!') % _('to ' + mode))
            return
        elif lines > 1:
            if question(self, _("Do you want %s %s line(s)?") %
                        (_('to ' + mode), cf(lines, int)[1])
                        ) != gtk.RESPONSE_YES:
                return

        cursor = self.__crud.cursor()
        try:
            cursor.execute(sql, update_values + args)
            self.__crud.commit()
        except Exception:
            self.__crud.rollback()
            cursor.close()
            raise

        if mode == 'update':
            for field, value in update_fields_values.items():
                if field not in self.__keys:
                    continue
                sql_args[self.__keys.index(field)] = value
            where, args = self.__crud_null_correction(self.__main_where,
                                                      sql_args)
            sql = ("select " + ", ".join(self.__fields) +
                   " from " + self.__table + self.__joins +
                   " where " + where + self.__group)
            cursor.execute(sql, args)
            self.update_line(self.selected(), cursor.fetchone())
        else:
            path, column = self.get_cursor()
            path = list(path)
            if len(path) > 1 and path[-1] == 0:
                del path[-1]
            elif path[-1] > 0:
                path[-1] -= 1
            path = tuple(path)
            self.remove(self.selected())
            self.set_cursor_on_cell(path, column)
        cursor.close()

    @try_function
    def do_key_press_event(self, ev):
        # Start editing when pressed F2
        if ev.keyval in (gtk.keysyms.F2, gtk.keysyms.KP_F2):
            self.set_cursor(*self.get_cursor(), start_editing=True)

        # If not CRUD enabled, go out
        elif not self.__crud:
            pass

        # Create / Insert
        elif ev.keyval in (gtk.keysyms.Insert, gtk.keysyms.equal,
                           gtk.keysyms.plus, gtk.keysyms.KP_Insert,
                           gtk.keysyms.KP_Add):
            self.crud_create()

        # Read / Select
        elif ev.keyval in (gtk.keysyms.F5, ):
            self.crud_read()

        # Update
        # In __editable_callback function

        # Delete
        elif ev.keyval in (gtk.keysyms.Delete, gtk.keysyms.minus,
                           gtk.keysyms.underscore, gtk.keysyms.KP_Subtract,
                           gtk.keysyms.KP_Delete):
            self.crud_delete()

        gtk.TreeView.do_key_press_event(self, ev)
        return True


FormModel = namedtuple('Form', 'label checked text join_result'
                       ' type decimals pole_type editable key icons'
                       ' default join'
                       ' show_checkbox show_text show_join_result'
                       ' label_color text_color'
                       ' old_checked old_text old_join_result edited')
FormModel.__new__.func_defaults = (_('Field:'), False, _('Empty'), None,
                                   str, 0, None, True, False, None,
                                   _('Default'), None,
                                   False, True, True, None, None,
                                   False, None, None, False)


class GridForm(Grid):

    __gtype_name__ = 'GridForm'

    def __init__(self, *args, **kwargs):
        super(GridForm, self).__init__(*args, **kwargs)
        self.__old_editing_text = ''
        model = self.get_model()
        if model is not None:
            self.set_model(None)
            model.clear()
            del model
        model = gtk.ListStore(str, bool, str, str, str, int, str, bool, bool,
                              str, str, str, bool, bool, bool, str, str,
                              bool, str, str, bool)
        self.set_model(model)

        col1 = gtk.TreeViewColumn(_("Field"))
        cell1 = gtk.CellRendererText()
        col1.pack_start(cell1)
        col1.add_attribute(cell1, 'text', FormModel._fields.index('label'))
        cell1.set_property('xalign', 1)  # label aligned to right
        col1.add_attribute(cell1, 'foreground',
                           FormModel._fields.index('label_color'))
        self.append_column(col1)

        col2 = gtk.TreeViewColumn(_("Value"))
        self.append_column(col2)

        # Célula para visualizar o bool [✓]
        cell2 = gtk.CellRendererToggle()
        col2.pack_start(cell2, expand=False)
        col2.add_attribute(cell2, "active",
                           FormModel._fields.index('checked'))
        col2.add_attribute(cell2, "activatable",
                           FormModel._fields.index('editable'))
        col2.add_attribute(cell2, 'sensitive',
                           FormModel._fields.index('editable'))
        col2.add_attribute(cell2, 'visible',
                           FormModel._fields.index('show_checkbox'))
        cell2.connect('toggled', self.__editable_callback)

        # Célula para visualizar o texto
        cell3 = gtk.CellRendererText()
        col2.pack_start(cell3, expand=False)
        col2.add_attribute(cell3, 'text', FormModel._fields.index('text'))
        col2.add_attribute(cell3, 'editable',
                           FormModel._fields.index('editable'))
        col2.add_attribute(cell3, 'visible',
                           FormModel._fields.index('show_text'))
        col2.add_attribute(cell3, 'foreground',
                           FormModel._fields.index('text_color'))
        # cell3.set_property('background', 'Light Gray')
        cell3.connect('editing-started', self.__start_editing_callback)
        cell3.connect('edited', self.__editable_callback)

        # Resultado do join
        cell4 = gtk.CellRendererText()
        col2.pack_start(cell4, expand=True)
        col2.add_attribute(cell4, 'text',
                           FormModel._fields.index('join_result'))
        col2.add_attribute(cell4, 'editable',
                           FormModel._fields.index('editable'))
        col2.add_attribute(cell4, 'visible',
                           FormModel._fields.index('show_join_result'))
        col2.add_attribute(cell4, 'foreground',
                           FormModel._fields.index('text_color'))
        # cell4.set_property('background', 'Light Blue')
        cell4.connect('editing-started', self.__start_editing_callback)
        cell4.connect('edited', self.__editable_callback)

        # Fim da grade / marca de obrigatório
        col3 = gtk.TreeViewColumn()
        cell5 = gtk.CellRendererText()
        col3.pack_start(cell5)
        col3.add_attribute(cell5, 'text', FormModel._fields.index('icons'))
        cell5.set_property('foreground', 'Gold')
        self.append_column(col3)

    def structure(self, titles, types, decimals=None, editables=None,
                  with_colors=False, sizes=None, formats=None):
        print 'titles:', titles
        print 'types:', types
        print 'decimals:', decimals
        print 'editables:', editables
        print 'with_colors:', with_colors
        print 'sizes:', sizes
        print 'formats:', formats

    def __finish_editing(self, editor, event, popup):
        key = event.keyval
        if key == gtk.keysyms.Escape:
            editor.props.text = self.__old_editing_text
            popup.quit()
        elif key in (gtk.keysyms.KP_Enter, gtk.keysyms.Return):
            popup.quit()
        update_ui()
        self.grab_focus()

    def __remove_editable(self, editable, new):
        print 'new:', repr(new)
        print '__old_editing_text:', repr(self.__old_editing_text)
        if new != self.__old_editing_text:
            editable.set_text('' if new is None else new)
        editable.editing_done()
        editable.remove_widget()
        editable.destroy()
        update_ui()
        self.grab_focus()

    def __start_editing_callback(self, renderer, editable, path):
        print '__start_editing_callback:', (renderer, editable, path)
        form_model = self.get_model()
        reg = FormModel(*tuple(form_model[path]))
        print 'Tipo:', reg.type
        x, y = self.get_bin_window().get_origin()
        area = self.get_cell_area(path, self.get_column(1))
        size = (area[2], area[3])
        print 'editable.props.text:', repr(editable.props.text)
        self.__old_editing_text = new = editable.props.text
        tx = reg.type
        # Creating or using float type from PoleUtil.tipos
        if tx[:5] == "float":
            try:
                decimals = int(tx[5:])
            except Exception:
                decimals = PoleUtil.local['frac_digits']
            tx = 'float' + str(decimals)
            if tx not in PoleUtil.tipos:
                fs = '0.' + '0' * decimals
                PoleUtil.tipos[tx] = PoleUtil.T(
                    6, 14, decimals, False,
                    PoleUtil.cs["números"] + PoleUtil.dp + '+-',
                    "{0},;-{0},;{0}".format(fs), 1, 3, 100)
        elif tx[:7] == "<type '":
            tx = tx[7:-2]
        try:
            tp = PoleUtil.python_tipos[PoleUtil.tipos[tx].tipo]
        except Exception:
            show_exception(self, None)
            tx = 'str'
            tp = PoleUtil.python_tipos[PoleUtil.tipos[tx].tipo]
        decimals = PoleUtil.tipos[tx].casas
        print 'Tipo:', tx, '(', decimals, ')'
        if tp in (datetime.date, datetime.datetime,
                  datetime.time, datetime.timedelta):
            position = (x + area[0], y + area[1] + area[3])
            c = Calendar(editable, tx if tx else decimals)
            r = c.run(position, transient_for=self)
            if r is None:
                new = ''
            elif r:
                new = editable.props.text
            c.destroy()
        else:
            position = (x + area[0], y + area[1])
            p = PopupWindow()
            if reg.join:
                model = gtk.ListStore(str, tp)
                e = ComboBoxEntryCompletion(model)
                e.do_parser_finished(None)
                cursor = self.__crud.cursor()
                cursor.execute(reg.join)
                gobject.timeout_add(1, load_store, e, cursor)
                e.child.connect('key-press-event', self.__finish_editing, p)
            elif tx and PoleUtil.tipos[tx].combo:
                size = (size[0], size[1] + 5)
                model = gtk.ListStore(str, str if tp == bool else tp)
                for opc in PoleUtil.tipos[tx].mascara[1:]:
                    model.append(((opc[0] + ' - ' + opc[1] if len(opc) > 1
                                   else opc[0]), opc[0]))
                e = gtk.ComboBox(model)
                cell = gtk.CellRendererText()
                e.pack_start(cell, True)
                e.add_attribute(cell, 'text', 0)
                gobject.idle_add(e.popup)
            else:
                e = Editor()
                e.set_alignment(0)
                e.connect('key-press-event', self.__finish_editing, p)
            if not tx or not PoleUtil.tipos[tx].combo:
                if tx:
                    e.config(tx)
                    # e.set_max_length(self.__sizes[column])
                elif tp in (int, long):
                    e.config("int")
                elif tp == float:
                    e.config("float" + str(decimals))
            # else:
            #    e.config("upper,normalize")
            e.props.has_frame = False
            e.show()
            p.add(e)
            if isinstance(e, Editor):
                e.props.text = self.__old_editing_text
            else:
                old = cf(self.__old_editing_text, tx if tx else tp, decimals)[0]
                if isinstance(e, ComboBoxEntryCompletion):
                    gobject.timeout_add(2, e.set_active_text, old, 0)
                else:
                    set_active_text(e, old, 1)

            # Out click do cancel
            # if p.run(self, size, position):
            #    new = cf(e.props.text, self.__types[column],
            #             self.__decimals[column])[1]

            # Out click do not cancel
            p.run(self, size, position)
            print 'e:', e
            if isinstance(e, gtk.ComboBox):
                print 'e.active:', e.get_active()
                print('e.text:', get_active_text(e, 0),
                      get_active_text(e, 1))
            text = (
                e.props.text if isinstance(e, Editor) else
                e.get_active_text(1) if isinstance(e, ComboBoxCompletion)
                else get_active_text(e, 0)
                if isinstance(e, ComboBoxEntryCompletion)
                else get_active_text(e, 1))
            if reg.join:
                new = text
            elif tx:
                new = cf(text, tx)[1]
            else:
                new = cf(text, tp, decimals)[1]
            print 'new:', repr(new)
            p.destroy()

        # Need out of this function to finish editing mode
        glib.timeout_add(1, self.__remove_editable, editable, new)

    def __editable_callback(self, renderer, path, result=None):
        print '__editable_callback:', (renderer, path, result)
        form_model = self.get_model()
        reg = FormModel(*tuple(form_model[path]))
        print 'Tipo:', reg.type
        print 'result:', result
        print 'reg.checked:', reg.checked
        print 'reg.text:', reg.text
        print 'reg.show_checkbox:', reg.show_checkbox
        checked = reg.checked
        text = reg.text
        join_result = reg.join_result
        if reg.show_checkbox:
            try:
                tp = (bool if reg.type in ("bool", "<type 'bool'>")
                      else PoleUtil.python_tipos[PoleUtil.tipos[reg.type].tipo])
            except Exception:
                show_exception(self, None)
                tp = str
            print 'tp:', tp
            print 'gtk.CellRendererToggle:', isinstance(renderer,
                                                        gtk.CellRendererToggle)
            if isinstance(renderer, gtk.CellRendererToggle):
                checked = not reg.checked
                if tp == bool:
                    text = PoleUtil.cf(checked, bool)[1]
            else:
                try:
                    print 'result:', result
                    txt_to_bool = PoleUtil.cf(result, bool)[0]
                    print 'txt_to_bool:', txt_to_bool
                    if reg.checked != txt_to_bool:
                        checked = txt_to_bool
                except Exception:
                    PoleLog.log_except()
                    show_exception(self, None)
        print 'reg.show_join_result:', reg.show_join_result
        if reg.show_join_result:
            join_result = result
            result = result.split(' ⤳ ', 1)[0]
        print 'join_result:', join_result
        print 'result:', result
        if reg.text != result and not isinstance(renderer, gtk.CellRendererToggle):
            text = result
        edited = checked != reg.old_checked or text != reg.old_text
        form_model[path][FormModel._fields.index('edited')] = edited
        form_model[path][
            FormModel._fields.index('label_color')] = 'Green' if edited else None
        form_model[path][FormModel._fields.index('checked')] = checked
        form_model[path][FormModel._fields.index('text')] = text
        form_model[path][FormModel._fields.index('join_result')] = join_result
        print 'Novo checked:', form_model[path][FormModel._fields.index('checked')]
        print 'Novo text:', form_model[path][FormModel._fields.index('text')]
        print 'Novo join_res:', form_model[path][FormModel._fields.index('join_result')]

    def do_cell_clicked(self, widget, event):
        print 'cell_clicked:', (widget, event)
        form_model = self.get_model()
        pos = self.get_path_at_pos(int(event.x), int(event.y))
        print 'pos:', pos
        if pos:
            row = form_model[pos[0]]
            reg = FormModel(*tuple(row))
            column = self.get_columns().index(pos[1])
            print 'column:', column
            print 'row/reg:', reg
            if column == 0 and reg.edited:
                resp = question(self,
                                _('Restore original data for %s?') % reg.label)
                if resp == gtk.RESPONSE_YES:
                    row[FormModel._fields.index('label_color')] = None
                    row[FormModel._fields.index('edited')] = False
                    row[FormModel._fields.index('checked')] = reg.old_checked
                    row[FormModel._fields.index('text')] = reg.old_text
                    row[FormModel._fields.index('join_result')] = reg.old_join_result

    def crud(self, *args, **kwargs):
        super(GridForm, self).crud(*args, **kwargs)

        print '__crud               :', self._Grid__crud
        print '__crud_create_enabled:', self._Grid__crud_create_enabled
        print '__crud_delete_enabled:', self._Grid__crud_delete_enabled
        print '__table              :', self._Grid__table
        print '__joins              :', self._Grid__joins
        print '__fields             :', self._Grid__fields
        print '__defaults           :', self._Grid__defaults
        print '__keys               :', self._Grid__keys
        print '__ignoreds           :', self._Grid__ignoreds
        print '__uniques            :', self._Grid__uniques
        print '__requireds          :', self._Grid__requireds
        print '__requests           :', self._Grid__requests
        print '__where              :', self._Grid__where
        print '__group              :', self._Grid__group
        print '__order              :', self._Grid__order
        print '__update2            :', self._Grid__update2
        print '__nicks              :', self._Grid__nicks
        print '__main_nick          :', self._Grid__main_nick
        print '__main_table         :', self._Grid__main_table
        print '__main_fields_map    :', self._Grid__main_fields_map
        print '__main_fields        :', self._Grid__main_fields
        print '__foreign_keys       :', self._Grid__foreign_keys
        print '__main_where         :', self._Grid__main_where
        print '__create_fields      :', self._Grid__create_fields
        print '__create_where       :', self._Grid__create_where
        # print 'model                :', self.model


class Processing(gtk.Window):
    def __init__(self, parent, title, step=None,
                 finish=None, stop_button=False):
        update_ui()
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
        update_ui()

    def stop_press(self, args):
        self.__stop = True

    def pulse(self):
        if self.__step:
            new_frac = self.__bar.get_fraction() + self.__step
            if new_frac > 0.999:
                new_frac = 1.00
            self.__bar.set_fraction(new_frac)
            self.__bar.set_text(formatar(new_frac*100, "Porcentagem 2"))
        else:
            self.__bar.pulse()
        update_ui()
        return not self.__stop

    def close(self):
        self.destroy()
        update_ui()


def load_module(parent_project, parent_main_window, module_name, title,
                main_window_name, data=None, new_process=False):
    if parent_main_window:
        parent_main_window.hide()
        update_ui()
    loop = glib.MainLoop()
    if data is None:
        data = []

    if new_process:
        sub = subprocess.Popen(module_name,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = sub.communicate(title)
        data.append(out)
        data.append(err)
        if err:
            error(parent_main_window, err)

        loop.quit()
        if parent_main_window is not None:
            parent_main_window.show()
            update_ui()
            t = gtk.gdk.x11_get_server_time(parent_main_window.get_window())
            parent_main_window.present_with_time(t)
            update_ui()
        return data

    module = importlib.import_module(module_name)
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
            parent_project.active_window = main_window
            main_window.set_transient_for(parent_main_window)
            main_window.set_modal(True)
            main_window.set_title(title + " - " + parent_main_window.get_title())
            main_window.set_icon(parent_main_window.get_icon())
        else:
            main_window.set_title(title)
        main_window.show()
        t = gtk.gdk.x11_get_server_time(main_window.get_window())
        main_window.present_with_time(t)
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
        t = gtk.gdk.x11_get_server_time(parent_main_window.get_window())
        parent_main_window.present_with_time(t)
    return data


# Replace GTK classes in XML Glade by PoleGTK classes where propertie
# name start with third element in (GtkClass, PoleGtkClass, start of name)
NEW_CLASSES = (
    ('GtkTreeView', 'Grid', 'gr_'),
    ('GtkTreeView', 'GridForm', 'gf_'),
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
    dont_have_can_focus = ('ListStore', 'Adjustment', 'TextBuffer', 'Action',
                           'TreeViewColumn', 'CellRendererPixbuf',
                           'CellRendererText')
    pos = xml.find('<object class="')
    while pos != -1:
        have_can_focus = True
        for gtkclass in dont_have_can_focus:
            if xml[pos + 18:pos + 18 + len(gtkclass)] == gtkclass:
                have_can_focus = False
                break
        if have_can_focus:
            pos = xml.find('>', pos) + 1
            xml = (xml[:pos] +
                   '<property name="can_focus">False</property>' + xml[pos:])
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


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Classe que intermedia um widget do GTK+ para facilitar acesso a consultar e
#     alterar valores de propriedades dos widgets, tal como as propriedades das
#     classes em Python, se comportando como um widget virtual. Dessa forma,
#     não precisa usar as funções GTK widget.set_propriedade(valor) ou
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
        except Exception:
            try:
                return object.__getattribute__(obj, "get_" + attr)()
            except Exception:
                return object.__getattribute__(obj, attr)

    def __setattr__(self, attr, value):
        try:
            obj = object.__getattribute__(self, "widget")
            if isinstance(obj, gtk.Notebook) and attr == 'current_page':
                raise 'Call set_current_page for gtk.Notebook'
            object.__getattribute__(obj, attr)
            obj.__setattr__(attr, value)
        except Exception:
            try:
                func = object.__getattribute__(obj, "set_" + attr)
                if isinstance(value, (list, tuple)):
                    func(*value)
                else:
                    func(value)
            except Exception:
                object.__setattr__(obj, attr, value)

    def __getitem__(self, index):
        return object.__getattribute__(self, "widget")[index]

    def __setitem__(self, index, value):
        object.__getattribute__(self, "widget")[index] = value

    def __delitem__(self, index):
        del object.__getattribute__(self, "widget")[index]


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
            if not combo.get_has_entry() and not combo.get_cells():
                celula = gtk.CellRendererText()
                combo.pack_start(celula, False)
                combo.add_attribute(celula, "text", 0)
            elif combo.get_has_entry() and combo.get_entry_text_column() == -1:
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


def read_text(textview, format=True):
    buffer = textview.get_buffer()
    text = strip(buffer.get_text(*buffer.get_bounds()))
    text = re.sub('[\t\r\f\v]', ' ', text)

    if format:
        text = formatar(text, 'Livre Mai')

    return text


def write_text(text, textview, format=True):
    if format:
        text = formatar(text, 'Livre Mai')

    text = re.sub('[\t\r\f\v]', ' ', text)

    buffer = textview.get_buffer()
    buffer.set_text(strip(text))


def set_active_text(combo, text, column=0, pole_type=None):
    model = combo.get_model()
    for index, line in enumerate(model):
        if (pole_type
                and cf(line[column], pole_type)[0] == cf(text, pole_type)[0]
                or line[column] == text):
            combo.set_active(index)
            if isinstance(combo.child, gtk.Entry):
                combo.child.select_region(0, -1)
            return
    combo.set_active(-1)


def get_active_text(combo, column=0,
                    pole_type=None, upper=None, lower=None, normalize=None):
    index = combo.get_active()
    if index < 0:
        return None
    model = combo.get_model()
    value = model[index][column]
    if pole_type:
        value = cf(value, pole_type)[1]
    else:
        if normalize:
            value = PoleUtil.normalize(value)
        if upper:
            value = value.upper()
        elif lower:
            value = value.lower()
    return value


def load_store(combo, cursor, active=True, column=-1):
    model = combo.get_model()
    combo.set_model(None)
    model.clear()
    for n, row in enumerate(cursor):
        model.append(row)
        if n % 100 == 0:
            update_ui()
    combo.set_model(model)
    if column == -1:
        if active:
            combo.set_active(0)
    else:
        set_active_text(combo, active, column)


def hide_window(widget):
    # if widget.is_toplevel():
    #     return widget.hide_on_delete()
    # else:
    toplevel = widget.get_toplevel()
    toplevel.hide()
    return True


def copy_to_clipboard(text, modal_to=None):
    gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD).set_text(text)
    if modal_to:
        info(modal_to, _("Data copied to memory!"))


def all_grids_to_clipboard(parent):
    csvs = []

    def __exportar(parent, csvs):
        if not isinstance(parent, gtk.Container):
            return
        for child in parent.children():
            if isinstance(child, Grid):
                csvs.append(child.get_csv())
            else:
                __exportar(child, csvs)

    __exportar(parent, csvs)

    gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD).set_text(
        '\n\n'.join(csvs))


__get_TreeModelRow = gtk.ListStore(int)
__get_TreeModelRow.append((0,))
TreeModelRow = __get_TreeModelRow[0].__class__
del __get_TreeModelRow


def get_value(x):
    if isinstance(x, VirtualWidget):
        x = x.widget
    if isinstance(x, gtk.Entry):
        x = x.get_text()
    elif isinstance(x, (gtk.Label, gtk.Button)):
        x = x.get_label()
    elif isinstance(x, gtk.ComboBox):
        x = get_active_text(x)
    elif isinstance(x, TreeModelRow):
        x = x[0]
    elif isinstance(x, GridRow):
        x = x[0][0] if x[0][1] else None
    elif isinstance(x, gtk.TreeModel):
        s = x[0].get_selection()
        if not s:
            x = None
        elif s.get_mode() == gtk.SELECTION_MULTIPLE:
            s = s.get_selected_rows()[1]
            x = x = x[0][s[0]][0] if s else None
        else:
            s = s.get_selected()[1]
            x = x = x[0][s][0] if s else None
    elif isinstance(x, Grid):
        line = x.selected()
        x = x[line][0][0] if line and x[line][0][1] else None
    elif isinstance(x, (list, tuple, dict)):
        if isinstance(x[0], gtk.ComboBox):
            x = get_active_text(x[0], int(x[1]) if len(x) > 1 else 0)
        elif isinstance(x[0], (list, tuple, dict, TreeModelRow)):
            x = x[0][x[1]]
        elif isinstance(x[0], GridRow):
            x = x[0][x[1]][x[2] if x > 2 else 0]
        elif isinstance(x[0], gtk.TreeModel):
            s = x[0].get_selection()
            if not s:
                x = None
            elif s.get_mode() == gtk.SELECTION_MULTIPLE:
                s = s.get_selected_rows()[1]
                x = x = x[0][s[0]][x[1]] if s else None
            else:
                s = s.get_selected()[1]
                x = x = x[0][s][x[1]] if s else None
        elif isinstance(x[0], Grid):
            line = x[0].selected()
            x = (x[0][x[1]][x[2]][x[3]
                 if x > 3 else 0] if line and x[0][x[1]][x[2]][1] else None)
    return x


def change_mouse_pointer(widget, cursor=None):
    if cursor is not None and not isinstance(cursor, gtk.gdk.Cursor):
        try:
            cursor = gtk.gdk.Cursor(cursor)
        except Exception:
            cursor = None
    win = widget.get_toplevel()
    win.realize()
    win.get_window().set_cursor(cursor)
    update_ui()


# Notify

try:
    import notify2
    notify2.init('pole', 'glib')
except Exception:
    print "Fail to start notify system."


def notify(title, message, icon=None, insistent=0,
           callback=None, actions=[], user_data=None):

    def __closed_notice(notice, *args):
        if notice.get_data('finished'):
            return
        action = args[0] if args else None
        if insistent and not action:
            glib.timeout_add(insistent * 1000, notify, title, message, icon,
                             insistent, callback, actions, user_data)
        notice.set_data('finished', True)
        if callback:
            callback(action, title, message, icon, insistent,
                     callback, actions, user_data)

    notice = notify2.Notification(title, message, icon)
    notice.set_data('finished', False)
    notice.connect('closed', __closed_notice)
    for action in actions:
        notice.add_action(action, action, __closed_notice)
    if insistent:
        notice.set_urgency(notify2.URGENCY_CRITICAL)
        notice.set_timeout(notify2.EXPIRES_NEVER)
    notice.show()
    if callback:
        callback('#!notice', title, notice, icon, insistent,
                 callback, actions, user_data)


if __name__ == '__main__':
    '''                       "Data,date,edit",
                           "Hora,time,edit",
                           "Data e hora,datetime,edit",
                           "Mês,month,edit",
                           "Horas,hours,edit",
                           "Data e hora 2,datetime,DATE_TIME,edit",
                           "Data 2,datetime,DATE,edit",
                           "Hora 2,datetime,TIME,edit",
                           "Mês 2,datetime,MONTH,edit",
                           "Horas 2,datetime,HOURS,edit",
                           "Dias e horas 2,datetime,DAYS_HOURS,edit",
                           "Horas 3,hours,DATE_TIME,edit",
                           "Horas 4,hours,DATE,edit",
                           "Horas 5,hours,TIME,edit",
    '''

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
                <property name="label"
                 translatable="yes">14/08/1978 09:35:42</property>
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
                <property name="tooltip_text" translatable="yes">
Teste do botão de data
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
            print error(args[0], 'Teste de erro')
        except Exception:
            class X(object):
                def __init__(self):
                    self.interface = ui
            x = X()
            show_exception(x, args)
        # print args
        # dados: matriz de dados
        # Pode vir de um select ou um arquivo
        now = datetime.datetime.now()
        dados = (("12.345.678", "Junior", "3.000,12", 1, 1, now, now, now, now,
                  datetime.datetime(1, 1, 2, 11, 59, 59),
                  datetime.datetime(1, 1, 2), now, now, None, 'red'),
                 ("abc", "Teste", "XYZ", "True", 2, now, now, now, now, now,
                  now, now, now, None, 'magenta'),
                 ("1....2,34", "Teste 2", "3.5.0.0,4.6", "False", 3, now, now,
                  now, now, now, now, now, now, None, 'cyan'),
                 (2.9, 123456.54321, 3.9999, 5, 4, now, now, now, now, now,
                  now, now, now, None, 'yellow'),
                 ("1234", "Carlos", "3.500", True, 5, now, now, now, now, now,
                  now, now, now, None, 'green'),
                 ("4.321", "Osvaldo", "4000,34", False, 6, now, now, now, now,
                  now, now, now, now, None, 'white'),
                 ("1234.567", "Leonardo", "5.000,33", 0, 7, now, now, now, now,
                  now, now, now, now, None, 'pink'),
                 ("1234.567", "Leonardo Sim", "5.000,33", "Sim", 8, now, now,
                  now, now, now, now, now, now, 'yellow', 'blue'),
                 ("1234.567", "Leonardo Não", "5.000,33", "Não", 9, now, now,
                  now, now, now, now, now, now, None, 'royal blue'))
        grade = ui.get_object('gr_treeview1')
        grade.clear()
        grade.add_data(dados)

    def fx(text, grid, path, column, titles, types, decimals, with_colors):
        print '****** fx *******'
        print 'text:', text
        print 'grid:', grid
        print 'path:', path
        print 'column:', column
        print 'titles:', titles
        print 'types:', types
        print 'decimals:', decimals
        print 'with_colors:', with_colors
        print 'return:', cf(text, types[column], decimals[column])
        return text  # cf(text, types[column], decimals[column])[0]

    def update(*args):
        # print args
        grade = ui.get_object('gr_treeview1')
        # print "*" * 100
        # print grade[5][2]
        grade[5]['Valor'] = datetime.datetime.now()
        # print grade[5][2]
        # print grade[5]['Valor']
        # print grade[5][-1]
        grade.get_column(2).get_cell_renderers()[0].set_property(
            'editable', not grade.get_column(
                2).get_cell_renderers()[0].get_property('editable'))
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
    ui.get_object('gr_treeview1').edit_callback = fx
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
    # botao.child.child.get_children()[0].show()
    vbox.pack_start(botao, False)

    # Mostar a interface
    janela.maximize()
    janela.show_all()

    # Operar sobre a grade criada como se fosse do gtk.Builder
    titulos = ("Código", "Nome", "Bônus", "Último")
    tipos = (int, str, float, bool)
    grade.structure(titulos, tipos)

    # Eventos
    janela.connect("delete_event", gtk.main_quit)
    # botao.connect("clicked", ao_clicar_preencher, grade)

    # Inciar o GTK
    gtk.main()
