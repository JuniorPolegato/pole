/* -*- Mode: C; tab-width: 8; indent-tabs-mode: t; c-basic-offset: 8 -*- */
/*
 * Copyright (C) 2001 Ximian, Inc.
 * Copyright (C) 2007 Vincent Geddes.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 * Authors:
 *   Chema Celorio <chema@celorio.com>
 *   Paolo Borelli <pborelli@katamail.com>
 *   Vincent Geddes <vgeddes@gnome.org>
 */

#include <config.h>

#include "glade-window.h"

#include <gladeui/glade.h>
#include <gladeui/glade-design-view.h>
#include <gladeui/glade-popup.h>
#include <gladeui/glade-inspector.h>

#include <string.h>
#include <glib/gstdio.h>
#include <glib/gi18n.h>
#include <gdk/gdkkeysyms.h>
#include <gtk/gtk.h>

#ifdef MAC_INTEGRATION
#  include <ige-mac-integration.h>
#endif


#define ACTION_GROUP_STATIC             "GladeStatic"
#define ACTION_GROUP_PROJECT            "GladeProject"
#define ACTION_GROUP_PROJECTS_LIST_MENU "GladeProjectsList"

#define READONLY_INDICATOR (_("[Read Only]"))

#define URL_USER_MANUAL      "http://glade.gnome.org/manual/index.html"
#define URL_DEVELOPER_MANUAL "http://glade.gnome.org/docs/index.html"

#define CONFIG_GROUP_WINDOWS        "Glade Windows"
#define GLADE_WINDOW_DEFAULT_WIDTH  720
#define GLADE_WINDOW_DEFAULT_HEIGHT 540
#define CONFIG_KEY_X                "x"
#define CONFIG_KEY_Y                "y"
#define CONFIG_KEY_WIDTH            "width"
#define CONFIG_KEY_HEIGHT           "height"
#define CONFIG_KEY_DETACHED         "detached"

#define GLADE_WINDOW_GET_PRIVATE(object) (G_TYPE_INSTANCE_GET_PRIVATE ((object),  \
					  GLADE_TYPE_WINDOW,                      \
					  GladeWindowPrivate))

enum {
	DOCK_PALETTE,
	DOCK_INSPECTOR,
	DOCK_EDITOR,
	N_DOCKS
};

typedef struct {
	GtkWidget	    *widget;		/* the widget with scrollbars */
	GtkWidget	    *paned;		/* GtkPaned in the main window containing which part */
	gboolean	     first_child;	/* whether this widget is packed with gtk_paned_pack1() */
	gboolean	     detached;		/* whether this widget should be floating */
	char		    *title;		/* window title, untranslated */
	char		    *id;		/* id to use in config file */
	GdkRectangle         window_pos;	/* x and y == G_MININT means unset */
} ToolDock;

struct _GladeWindowPrivate
{
	GladeApp            *app;
	
	GtkWidget           *main_vbox;
	
	GtkWidget           *notebook;
	GladeDesignView     *active_view;
	gint                 num_tabs;
	
	GtkWidget           *inspectors_notebook;

	GtkWidget           *statusbar;                     /* A pointer to the status bar. */
	guint                statusbar_menu_context_id;     /* The context id of the menu bar */
	guint                statusbar_actions_context_id;  /* The context id of actions messages */

	GtkUIManager        *ui;		            /* The UIManager */
	guint                projects_list_menu_ui_id;      /* Merge id for projects list menu */

	GtkActionGroup      *static_actions;	            /* All the static actions */
	GtkActionGroup      *project_actions;               /* All the project actions */
	GtkActionGroup      *projects_list_menu_actions;    /* Projects list menu actions */

	GtkRecentManager    *recent_manager;
	GtkWidget           *recent_menu;

	gchar               *default_path;         /* the default path for open/save operations */
	
	GtkToggleToolButton *selector_button;      /* the widget selector button (replaces the one in the palette) */
	GtkToggleToolButton *drag_resize_button;   /* sets the pointer to drag/resize mode */
	gboolean             setting_pointer_mode; /* avoid feedback signal loops */

	GtkToolItem         *undo;                 /* customized buttons for undo/redo with history */
	GtkToolItem         *redo;
	
	GtkWidget           *toolbar;              /* Actions are added to the toolbar */
	gint                 actions_start;        /* start of action items */

	GtkWidget           *center_pane;
	/* paned windows that tools get docked into/out of */
	GtkWidget           *left_pane;
	GtkWidget           *right_pane;

	GdkRectangle         position;
	ToolDock	     docks[N_DOCKS];
};

static void refresh_undo_redo                (GladeWindow      *window);

static void recent_chooser_item_activated_cb (GtkRecentChooser *chooser,
					      GladeWindow      *window);

static void check_reload_project             (GladeWindow      *window,
					      GladeProject     *project);

static void glade_window_config_save (GladeWindow *window);


G_DEFINE_TYPE (GladeWindow, glade_window, GTK_TYPE_WINDOW)

static void
about_dialog_activate_link_func (GtkAboutDialog *dialog, const gchar *link, GladeWindow *window)
{
	GtkWidget *warning_dialog;
	gboolean retval;
	
	retval = glade_util_url_show (link);
	
	if (!retval)
	{
		warning_dialog = gtk_message_dialog_new (GTK_WINDOW (dialog),
							 GTK_DIALOG_MODAL,
							 GTK_MESSAGE_ERROR,
							 GTK_BUTTONS_OK,
							 _("Could not display the URL '%s'"),
							 link);
						 
		gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (warning_dialog),
							  _("No suitable web browser could be found."));
						 	
		gtk_window_set_title (GTK_WINDOW (warning_dialog), "");
		
		g_signal_connect_swapped (warning_dialog, "response",
					  G_CALLBACK (gtk_widget_destroy),
					  warning_dialog);
				
		gtk_widget_show (warning_dialog);
	}	

}

/* locates the help file "glade.xml" with respect to current locale */
static gchar*
locate_help_file ()
{
	const gchar* const* locales = g_get_language_names ();

	/* check if user manual has been installed, if not, GLADE_GNOMEHELPDIR is empty */
	if (strlen (GLADE_GNOMEHELPDIR) == 0)
		return NULL;

	for (; *locales; locales++)
	{
		gchar *path;
		
		path = g_build_path (G_DIR_SEPARATOR_S, GLADE_GNOMEHELPDIR, "glade", *locales, "glade.xml", NULL);

		if (g_file_test (path, G_FILE_TEST_EXISTS))
		{
			return (path);
		}
		g_free (path);
	}
	
	return NULL;
}

static gboolean
help_show (const gchar *link_id)
{
	gchar *file, *url, *command;
	gboolean retval;
	gint exit_status = -1;
	GError *error = NULL; 	

	file = locate_help_file ();
	if (file == NULL)
		return FALSE;

	if (link_id != NULL) {
		url = g_strconcat ("ghelp://", file, "?", link_id, NULL);
	} else {
		url = g_strconcat ("ghelp://", file, NULL);	
	}

	command = g_strconcat ("gnome-open ", url, NULL);
			
	retval = g_spawn_command_line_sync (command,
					    NULL,
					    NULL,
					    &exit_status,
					    &error);

	if (!retval) {
		g_error_free (error);
		error = NULL;
	}		
	
	g_free (command);
	g_free (file);
	g_free (url);
	
	return retval && !exit_status;
}


/* the following functions are taken from gedit-utils.c */

static gchar *
str_middle_truncate (const gchar *string,
		     guint        truncate_length)
{
	GString     *truncated;
	guint        length;
	guint        n_chars;
	guint        num_left_chars;
	guint        right_offset;
	guint        delimiter_length;
	const gchar *delimiter = "\342\200\246";

	g_return_val_if_fail (string != NULL, NULL);

	length = strlen (string);

	g_return_val_if_fail (g_utf8_validate (string, length, NULL), NULL);

	/* It doesnt make sense to truncate strings to less than
	 * the size of the delimiter plus 2 characters (one on each
	 * side)
	 */
	delimiter_length = g_utf8_strlen (delimiter, -1);
	if (truncate_length < (delimiter_length + 2)) {
		return g_strdup (string);
	}

	n_chars = g_utf8_strlen (string, length);

	/* Make sure the string is not already small enough. */
	if (n_chars <= truncate_length) {
		return g_strdup (string);
	}

	/* Find the 'middle' where the truncation will occur. */
	num_left_chars = (truncate_length - delimiter_length) / 2;
	right_offset = n_chars - truncate_length + num_left_chars + delimiter_length;

	truncated = g_string_new_len (string,
				      g_utf8_offset_to_pointer (string, num_left_chars) - string);
	g_string_append (truncated, delimiter);
	g_string_append (truncated, g_utf8_offset_to_pointer (string, right_offset));
		
	return g_string_free (truncated, FALSE);
}

/*
 * Doubles underscore to avoid spurious menu accels - taken from gedit-utils.c
 */
static gchar * 
escape_underscores (const gchar* text,
		    gssize       length)
{
	GString *str;
	const gchar *p;
	const gchar *end;

	g_return_val_if_fail (text != NULL, NULL);

	if (length < 0)
		length = strlen (text);

	str = g_string_sized_new (length);

	p = text;
	end = text + length;

	while (p != end)
	{
		const gchar *next;
		next = g_utf8_next_char (p);

		switch (*p)
		{
			case '_':
				g_string_append (str, "__");
				break;
			default:
				g_string_append_len (str, p, next - p);
				break;
		}

		p = next;
	}

	return g_string_free (str, FALSE);
}

typedef enum
{
	FORMAT_NAME_MARK_UNSAVED        = 1 << 0,
	FORMAT_NAME_ESCAPE_UNDERSCORES  = 1 << 1,
	FORMAT_NAME_MIDDLE_TRUNCATE     = 1 << 2
} FormatNameFlags;

#define MAX_TITLE_LENGTH 100

static gchar *
get_formatted_project_name_for_display (GladeProject *project, FormatNameFlags format_flags)
{
	gchar *name, *pass1, *pass2, *pass3;
	
	g_return_val_if_fail (project != NULL, NULL);
	
	name = glade_project_get_name (project);
	
	if ((format_flags & FORMAT_NAME_MARK_UNSAVED)
	    && glade_project_get_modified (project))
		pass1 = g_strdup_printf ("*%s", name);
	else
		pass1 = g_strdup (name);
		
	if (format_flags & FORMAT_NAME_ESCAPE_UNDERSCORES)
		pass2 = escape_underscores (pass1, -1);
	else
		pass2 = g_strdup (pass1);
		
	if (format_flags & FORMAT_NAME_MIDDLE_TRUNCATE)
		pass3 = str_middle_truncate (pass2, MAX_TITLE_LENGTH);
	else
		pass3 = g_strdup (pass2); 

	g_free (name);
	g_free (pass1);	
	g_free (pass2);
	
	return pass3;
}

static gchar *
replace_home_dir_with_tilde (const gchar *path)
{
#ifdef G_OS_UNIX
	gchar *tmp;
	gchar *home;

	g_return_val_if_fail (path != NULL, NULL);

	/* Note that g_get_home_dir returns a const string */
	tmp = (gchar *) g_get_home_dir ();

	if (tmp == NULL)
		return g_strdup (path);

	home = g_filename_to_utf8 (tmp, -1, NULL, NULL, NULL);
	if (home == NULL)
		return g_strdup (path);

	if (strcmp (path, home) == 0)
	{
		g_free (home);
		
		return g_strdup ("~");
	}

	tmp = home;
	home = g_strdup_printf ("%s/", tmp);
	g_free (tmp);

	if (g_str_has_prefix (path, home))
	{
		gchar *res;

		res = g_strdup_printf ("~/%s", path + strlen (home));

		g_free (home);
		
		return res;		
	}

	g_free (home);

	return g_strdup (path);
#else
	return g_strdup (path);
#endif
}

static void
refresh_title (GladeWindow *window)
{
	GladeProject *project;
	gchar *title, *name = NULL;

	if (window->priv->active_view)
	{
		project = glade_design_view_get_project (window->priv->active_view);

		name = get_formatted_project_name_for_display (project, 
							       FORMAT_NAME_MARK_UNSAVED |
							       FORMAT_NAME_MIDDLE_TRUNCATE);
		
		if (glade_project_get_readonly (project) != FALSE)
			title = g_strdup_printf ("%s %s", name, READONLY_INDICATOR);
		else
			title = g_strdup_printf ("%s", name);
		
		g_free (name);
	}
	else
	{
		title = g_strdup (_("User Interface Designer"));
	}
	
	gtk_window_set_title (GTK_WINDOW (window), title);

	g_free (title);
}

static const gchar*
get_default_path (GladeWindow *window)
{
	return window->priv->default_path;
}

static void
update_default_path (GladeWindow *window, GladeProject *project)
{
	gchar *path;
	
	g_return_if_fail (glade_project_get_path (project) != NULL);

	path = g_path_get_dirname (glade_project_get_path (project));

	g_free (window->priv->default_path);
	window->priv->default_path = g_strdup (path);

	g_free (path);
}

static gboolean
window_state_event_cb (GtkWidget *widget,
			   GdkEventWindowState *event,
			   GladeWindow *window)
{
	if (event->changed_mask &
	    (GDK_WINDOW_STATE_MAXIMIZED | GDK_WINDOW_STATE_FULLSCREEN))
	{
		gboolean show;

		show = !(event->new_window_state &
			(GDK_WINDOW_STATE_MAXIMIZED | GDK_WINDOW_STATE_FULLSCREEN));

		gtk_statusbar_set_has_resize_grip (GTK_STATUSBAR (window->priv->statusbar), show);
	}

	return FALSE;
}

static GtkWidget *
create_recent_chooser_menu (GladeWindow *window, GtkRecentManager *manager)
{
	GtkWidget *recent_menu;
	GtkRecentFilter *filter;

	recent_menu = gtk_recent_chooser_menu_new_for_manager (manager);

	gtk_recent_chooser_set_local_only (GTK_RECENT_CHOOSER (recent_menu), TRUE);
	gtk_recent_chooser_set_show_icons (GTK_RECENT_CHOOSER (recent_menu), FALSE);
	gtk_recent_chooser_set_sort_type (GTK_RECENT_CHOOSER (recent_menu), GTK_RECENT_SORT_MRU);
	gtk_recent_chooser_menu_set_show_numbers (GTK_RECENT_CHOOSER_MENU (recent_menu), TRUE);

	filter = gtk_recent_filter_new ();
	gtk_recent_filter_add_application (filter, g_get_application_name());
	gtk_recent_chooser_set_filter (GTK_RECENT_CHOOSER (recent_menu), filter);

	return recent_menu;
}

static void
activate_action (GtkToolButton *toolbutton,
				      GladeWidgetAction *action) 
{
	GladeWidget *widget;
	
	if ((widget = g_object_get_data (G_OBJECT (toolbutton), "glade-widget")))
		glade_widget_adaptor_action_activate (widget->adaptor,
						      widget->object,
						      action->klass->path);
}

static void
action_notify_sensitive (GObject *gobject,
			 GParamSpec *arg1,
			 GtkWidget *item)
{
	GladeWidgetAction *action = GLADE_WIDGET_ACTION (gobject);
	gtk_widget_set_sensitive (item, action->sensitive);
}

static void
action_disconnect (gpointer data, GClosure *closure)
{
	g_signal_handlers_disconnect_matched (data, G_SIGNAL_MATCH_FUNC,
					      0, 0, NULL,
					      action_notify_sensitive,
					      NULL);
}

static void
clean_actions (GladeWindow *window)
{
	GtkContainer *container = GTK_CONTAINER (window->priv->toolbar);
	GtkToolbar *bar = GTK_TOOLBAR (window->priv->toolbar);
	GtkToolItem *item;
	
	if (window->priv->actions_start)
	{
		while ((item = gtk_toolbar_get_nth_item (bar, window->priv->actions_start)))
			gtk_container_remove (container, GTK_WIDGET (item));
	}
}

static void
add_actions (GladeWindow *window,
	     GladeWidget *widget,
	     GList       *actions)
{
	GtkToolbar *bar = GTK_TOOLBAR (window->priv->toolbar);
	GtkToolItem *item = gtk_separator_tool_item_new ();
	gint n = 0;
	GList *l;

	gtk_toolbar_insert (bar, item, -1);
	gtk_widget_show (GTK_WIDGET (item));

	if (window->priv->actions_start == 0)
		window->priv->actions_start = gtk_toolbar_get_item_index (bar, item);
			
	for (l = actions; l; l = g_list_next (l))
	{
		GladeWidgetAction *a = l->data;
		
		if (!a->klass->important) continue;
		
		if (a->actions)
		{
			g_warning ("Trying to add a group action to the toolbar is unsupported");
			continue;
		}

		item = gtk_tool_button_new_from_stock ((a->klass->stock) ? a->klass->stock : "gtk-execute");
		if (a->klass->label)
			gtk_tool_button_set_label (GTK_TOOL_BUTTON (item),
						   a->klass->label);
		
		g_object_set_data (G_OBJECT (item), "glade-widget", widget);

		/* We use destroy_data to keep track of notify::sensitive callbacks
		 * on the action object and disconnect them when the toolbar item
		 * gets destroyed.
		 */
		g_signal_connect_data (item, "clicked",
				       G_CALLBACK (activate_action),
				       a, action_disconnect, 0);
			
		gtk_widget_set_sensitive (GTK_WIDGET (item), a->sensitive);

		g_signal_connect (a, "notify::sensitive",
				  G_CALLBACK (activate_action),
				  GTK_WIDGET (item));
		
		gtk_toolbar_insert (bar, item, -1);
		gtk_tool_item_set_homogeneous (item, FALSE);
		gtk_widget_show (GTK_WIDGET (item));
		n++;
	}
	
	if (n == 0)
		clean_actions (window);
}

static void
project_selection_changed_cb (GladeProject *project, GladeWindow *window)
{
	GladeWidget *glade_widget = NULL;
	GList *list;
	gint num;

	/* This is sometimes called with a NULL project (to make the label
	 * insensitive with no projects loaded)
	 */
	g_return_if_fail (GLADE_IS_WINDOW (window));

	/* Only update the toolbar & workspace if the selection has changed on
	 * the currently active project.
	 */
	if (project && (project == glade_app_get_project ()))
	{
		list = glade_project_selection_get (project);
		num = g_list_length (list);
		
		if (num == 1 && !GLADE_IS_PLACEHOLDER (list->data))
		{
			glade_widget = glade_widget_get_from_gobject (G_OBJECT (list->data));

			glade_widget_show (glade_widget);

			clean_actions (window);
			if (glade_widget->actions)
				add_actions (window, glade_widget, glade_widget->actions);
		}	
	}
}

static GladeDesignView *
get_active_view (GladeWindow *window)
{
	g_return_val_if_fail (GLADE_IS_WINDOW (window), NULL);

	return window->priv->active_view;
}

static gchar *
format_project_list_item_tooltip (GladeProject *project)
{
	gchar *tooltip, *path, *name;

	if (glade_project_get_path (project))
	{
		path = replace_home_dir_with_tilde (glade_project_get_path (project));
		
		if (glade_project_get_readonly (project))
		{
                        /* translators: referring to the action of activating a file named '%s'.
                         *              we also indicate to users that the file may be read-only with
                         *              the second '%s' */
			tooltip = g_strdup_printf (_("Activate '%s' %s"),
					   	   path,
					   	   READONLY_INDICATOR);
		}
		else
		{
                       /* translators: referring to the action of activating a file named '%s' */
			tooltip = g_strdup_printf (_("Activate '%s'"), path);
		}
		g_free (path);
	}
	else
	{
		name = glade_project_get_name (project);
                 /* FIXME add hint for translators */
		tooltip = g_strdup_printf (_("Activate '%s'"), name);
		g_free (name);
	}
	
	return tooltip;
}

static void
refresh_projects_list_item (GladeWindow *window, GladeProject *project)
{
	GtkAction *action;
	gchar *project_name;
	gchar *tooltip;
	
	/* Get associated action */
	action = GTK_ACTION (g_object_get_data (G_OBJECT (project), "project-list-action"));

	/* Set action label */
	project_name = get_formatted_project_name_for_display (project,
							       FORMAT_NAME_MARK_UNSAVED |
							       FORMAT_NAME_ESCAPE_UNDERSCORES |
							       FORMAT_NAME_MIDDLE_TRUNCATE);
							
	g_object_set (action, "label", project_name, NULL);

	/* Set action tooltip */
	tooltip = format_project_list_item_tooltip (project);
	g_object_set (action, "tooltip", tooltip, NULL);
	
	g_free (tooltip);
	g_free (project_name);
}

static void
refresh_next_prev_project_sensitivity (GladeWindow *window)
{
	GladeDesignView  *view;
	GtkAction *action;
	gint view_number;
	
	view = get_active_view (window);

	if (view != NULL)
	{
		view_number = gtk_notebook_page_num (GTK_NOTEBOOK (window->priv->notebook), GTK_WIDGET (view));
		g_return_if_fail (view_number >= 0);
	
		action = gtk_action_group_get_action (window->priv->project_actions, "PreviousProject");
		gtk_action_set_sensitive (action, view_number != 0);
	
		action = gtk_action_group_get_action (window->priv->project_actions, "NextProject");
		gtk_action_set_sensitive (action, 
				 	 view_number < gtk_notebook_get_n_pages (GTK_NOTEBOOK (window->priv->notebook)) - 1);
	}
	else
	{
		action = gtk_action_group_get_action (window->priv->project_actions, "PreviousProject");
		gtk_action_set_sensitive (action, FALSE);
		
		action = gtk_action_group_get_action (window->priv->project_actions, "NextProject");
		gtk_action_set_sensitive (action, FALSE);
	}
}

static void
new_cb (GtkAction *action, GladeWindow *window)
{
	glade_window_new_project (window);
}

static void
project_notify_handler_cb (GladeProject *project, GParamSpec *spec, GladeWindow *window)
{
	GtkAction *action;

	if (strcmp (spec->name, "modified") == 0)	
	{
		refresh_title (window);
		refresh_projects_list_item (window, project);
	}
	else if (strcmp (spec->name, "read-only") == 0)	
	{
		action = gtk_action_group_get_action (window->priv->project_actions, "Save");
		gtk_action_set_sensitive (action,
				  	  !glade_project_get_readonly (project));
	}
	else if (strcmp (spec->name, "has-selection") == 0)	
	{
		action = gtk_action_group_get_action (window->priv->project_actions, "Cut");
		gtk_action_set_sensitive (action,
				  	  glade_project_get_has_selection (project));

		action = gtk_action_group_get_action (window->priv->project_actions, "Copy");
		gtk_action_set_sensitive (action,
				  	  glade_project_get_has_selection (project));

		action = gtk_action_group_get_action (window->priv->project_actions, "Delete");
		gtk_action_set_sensitive (action,
				 	  glade_project_get_has_selection (project));
	}
}

static void
clipboard_notify_handler_cb (GladeClipboard *clipboard, GParamSpec *spec, GladeWindow *window)
{
	GtkAction *action;

	if (strcmp (spec->name, "has-selection") == 0)	
	{
		action = gtk_action_group_get_action (window->priv->project_actions, "Paste");
		gtk_action_set_sensitive (action,
				 	  glade_clipboard_get_has_selection (clipboard));
	}
}

static void
on_selector_button_toggled (GtkToggleToolButton *button, GladeWindow *window)
{
	if (window->priv->setting_pointer_mode)
		return;

	if (gtk_toggle_tool_button_get_active (window->priv->selector_button))
	{
		glade_palette_deselect_current_item (glade_app_get_palette(), FALSE);
		glade_app_set_pointer_mode (GLADE_POINTER_SELECT);
	}
	else
		gtk_toggle_tool_button_set_active (window->priv->selector_button, TRUE);
}

static void
on_drag_resize_button_toggled (GtkToggleToolButton *button, GladeWindow *window)
{
	if (window->priv->setting_pointer_mode)
		return;

	if (gtk_toggle_tool_button_get_active (window->priv->drag_resize_button))
		glade_app_set_pointer_mode (GLADE_POINTER_DRAG_RESIZE);
	else
		gtk_toggle_tool_button_set_active (window->priv->drag_resize_button, TRUE);

}

static void
on_pointer_mode_changed (GladeApp           *app,
			 GParamSpec         *pspec,
			 GladeWindow *window)
{
	window->priv->setting_pointer_mode = TRUE;

	if (glade_app_get_pointer_mode () == GLADE_POINTER_SELECT)
		gtk_toggle_tool_button_set_active (window->priv->selector_button, TRUE);
	else
		gtk_toggle_tool_button_set_active (window->priv->selector_button, FALSE);

	if (glade_app_get_pointer_mode () == GLADE_POINTER_DRAG_RESIZE)
		gtk_toggle_tool_button_set_active (window->priv->drag_resize_button, TRUE);
	else
		gtk_toggle_tool_button_set_active (window->priv->drag_resize_button, FALSE);

	window->priv->setting_pointer_mode = FALSE;
}

static void
set_sensitivity_according_to_project (GladeWindow *window, GladeProject *project)
{
	GtkAction *action;

	action = gtk_action_group_get_action (window->priv->project_actions, "Save");
	gtk_action_set_sensitive (action,
			          !glade_project_get_readonly (project));

	action = gtk_action_group_get_action (window->priv->project_actions, "Cut");
	gtk_action_set_sensitive (action,
				  glade_project_get_has_selection (project));

	action = gtk_action_group_get_action (window->priv->project_actions, "Copy");
	gtk_action_set_sensitive (action,
				  glade_project_get_has_selection (project));

	action = gtk_action_group_get_action (window->priv->project_actions, "Paste");
	gtk_action_set_sensitive (action,
				  glade_clipboard_get_has_selection
					(glade_app_get_clipboard ()));

	action = gtk_action_group_get_action (window->priv->project_actions, "Delete");
	gtk_action_set_sensitive (action,
				  glade_project_get_has_selection (project));

	refresh_next_prev_project_sensitivity (window);

}

static void
recent_add (GladeWindow *window, const gchar *path)
{
	GtkRecentData *recent_data;
	gchar *uri;
	GError *error = NULL;

	uri = g_filename_to_uri (path, NULL, &error);
	if (error)
	{	
		g_warning ("Could not convert uri \"%s\" to a local path: %s", uri, error->message);
		g_error_free (error);
		return;
	}

	recent_data = g_slice_new (GtkRecentData);

	recent_data->display_name   = NULL;
	recent_data->description    = NULL;
	recent_data->mime_type      = "application/x-glade";
	recent_data->app_name       = (gchar *) g_get_application_name ();
	recent_data->app_exec       = g_strjoin (" ", g_get_prgname (), "%u", NULL);
	recent_data->groups         = NULL;
	recent_data->is_private     = FALSE;

	gtk_recent_manager_add_full (window->priv->recent_manager,
				     uri,
				     recent_data);

	g_free (uri);
	g_free (recent_data->app_exec);
	g_slice_free (GtkRecentData, recent_data);

}

static void
recent_remove (GladeWindow *window, const gchar *path)
{
	gchar *uri;
	GError *error = NULL;

	uri = g_filename_to_uri (path, NULL, &error);
	if (error)
	{	
		g_warning ("Could not convert uri \"%s\" to a local path: %s", uri, error->message);
		g_error_free (error);
		return;
	}

	gtk_recent_manager_remove_item (window->priv->recent_manager,
					uri,
					NULL);
	
	g_free (uri);
}

/* switch to a project and check if we need to reload it.
 *
 */
static void
switch_to_project (GladeWindow *window, GladeProject *project)
{
	GladeWindowPrivate *priv = window->priv;
	guint i, n = gtk_notebook_get_n_pages (GTK_NOTEBOOK (priv->notebook)); 

	/* increase project popularity */
	recent_add (window, glade_project_get_path (project));
	update_default_path (window, project);	

	for (i = 0; i < n; i++)
	{
		GladeProject *project_i;
		GtkWidget    *view;
	
		view = gtk_notebook_get_nth_page (GTK_NOTEBOOK (priv->notebook), i);
		project_i = glade_design_view_get_project (GLADE_DESIGN_VIEW (view));	
		
		if (project == project_i)
		{
			gtk_notebook_set_current_page (GTK_NOTEBOOK (priv->notebook), i);
			break;
		}
	}
	check_reload_project (window, project);
}

static void
projects_list_menu_activate_cb (GtkAction *action, GladeWindow *window)
{
	gint n;

	if (gtk_toggle_action_get_active (GTK_TOGGLE_ACTION (action)) == FALSE)
		return;

	n = gtk_radio_action_get_current_value (GTK_RADIO_ACTION (action));
	gtk_notebook_set_current_page (GTK_NOTEBOOK (window->priv->notebook), n);
}

static void
refresh_projects_list_menu (GladeWindow *window)
{
	GladeWindowPrivate *p = window->priv;
	GList *actions, *l;
	GSList *group = NULL;
	gint n, i;
	guint id;

	if (p->projects_list_menu_ui_id != 0)
		gtk_ui_manager_remove_ui (p->ui, p->projects_list_menu_ui_id);

	/* Remove all current actions */
	actions = gtk_action_group_list_actions (p->projects_list_menu_actions);
	for (l = actions; l != NULL; l = l->next)
	{
		g_signal_handlers_disconnect_by_func (GTK_ACTION (l->data),
						      G_CALLBACK (projects_list_menu_activate_cb), window);
 		gtk_action_group_remove_action (p->projects_list_menu_actions, GTK_ACTION (l->data));
	}
	g_list_free (actions);

	n = gtk_notebook_get_n_pages (GTK_NOTEBOOK (p->notebook));

	id = (n > 0) ? gtk_ui_manager_new_merge_id (p->ui) : 0;

	/* Add an action for each project */
	for (i = 0; i < n; i++)
	{
		GtkWidget *view;
		GladeProject *project;
		GtkRadioAction *action;
		gchar action_name[32];
		gchar *project_name;
		gchar *tooltip;
		gchar accel[7];

		view = gtk_notebook_get_nth_page (GTK_NOTEBOOK (p->notebook), i);
		project = glade_design_view_get_project (GLADE_DESIGN_VIEW (view));


		/* NOTE: the action is associated to the position of the tab in
		 * the notebook not to the tab itself! This is needed to work
		 * around the gtk+ bug #170727: gtk leaves around the accels
		 * of the action. Since the accel depends on the tab position
		 * the problem is worked around, action with the same name always
		 * get the same accel.
		 */
                g_snprintf (action_name, sizeof (action_name), "Tab_%d", i);
		project_name = get_formatted_project_name_for_display (project,
								       FORMAT_NAME_MARK_UNSAVED |
								       FORMAT_NAME_MIDDLE_TRUNCATE |
								       FORMAT_NAME_ESCAPE_UNDERSCORES);				       
		tooltip = format_project_list_item_tooltip (project);

		/* alt + 1, 2, 3... 0 to switch to the first ten tabs */
                if (i < 10)
                        g_snprintf (accel, sizeof (accel), "<alt>%d", (i + 1) % 10);
                else
                        accel[0] = '\0';

		action = gtk_radio_action_new (action_name, 
					       project_name,
					       tooltip, 
					       NULL,
					       i);

		/* Link action and project */
		g_object_set_data (G_OBJECT (project), "project-list-action", action);
		g_object_set_data (G_OBJECT (action), "project", project);

		/* note that group changes each time we add an action, so it must be updated */
		gtk_radio_action_set_group (action, group);
		group = gtk_radio_action_get_group (action);

		gtk_action_group_add_action_with_accel (p->projects_list_menu_actions,
							GTK_ACTION (action),
							accel);

		g_signal_connect (action, "activate",
				  G_CALLBACK (projects_list_menu_activate_cb),
				  window);

		gtk_ui_manager_add_ui (p->ui, id,
				       "/MenuBar/ProjectMenu/ProjectsListPlaceholder",
				       action_name, action_name,
				       GTK_UI_MANAGER_MENUITEM,
				       FALSE);

		if (GLADE_DESIGN_VIEW (view) == p->active_view)
			gtk_toggle_action_set_active (GTK_TOGGLE_ACTION (action), TRUE);

		g_object_unref (action);

		g_free (project_name);
		g_free (tooltip);
	}

	p->projects_list_menu_ui_id = id;
}

static void
open_cb (GtkAction *action, GladeWindow *window)
{
	GtkWidget *filechooser;
	gchar     *path = NULL, *default_path;

	filechooser = glade_util_file_dialog_new (_("Open\342\200\246"), NULL,
						  GTK_WINDOW (window),
						  GLADE_FILE_DIALOG_ACTION_OPEN);


	default_path = g_strdup (get_default_path (window));
	if (default_path != NULL)
	{
		gtk_file_chooser_set_current_folder (GTK_FILE_CHOOSER (filechooser), default_path);
		g_free (default_path);
	}

	if (gtk_dialog_run (GTK_DIALOG(filechooser)) == GTK_RESPONSE_OK)
		path = gtk_file_chooser_get_filename (GTK_FILE_CHOOSER (filechooser));

	gtk_widget_destroy (filechooser);

	if (!path)
		return;
	
	glade_window_open_project (window, path);
	g_free (path);
}

static void
save (GladeWindow *window, GladeProject *project, const gchar *path)
{
	GError   *error = NULL;
	gchar    *display_name, *display_path = g_strdup (path);
	time_t    mtime;
	GtkWidget *dialog;
	GtkWidget *button;
	gint       response;

	/* check for external modification to the project file */
	mtime = glade_util_get_file_mtime (glade_project_get_path (project), NULL);
	 
	if (mtime > glade_project_get_file_mtime (project)) {
	
		dialog = gtk_message_dialog_new (GTK_WINDOW (window),
						 GTK_DIALOG_MODAL,
						 GTK_MESSAGE_WARNING,
						 GTK_BUTTONS_NONE,
						 _("The file %s has been modified since reading it"),
						 glade_project_get_path (project));
						 
		gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (dialog), 				 
							  _("If you save it, all the external changes could be lost. Save it anyway?"));
							  
		gtk_window_set_title (GTK_WINDOW (dialog), "");
		
	        button = gtk_button_new_with_mnemonic (_("_Save Anyway"));
	        gtk_button_set_image (GTK_BUTTON (button),
	        		      gtk_image_new_from_stock (GTK_STOCK_SAVE,
	        		      				GTK_ICON_SIZE_BUTTON));
	        gtk_widget_show (button);

		gtk_dialog_add_action_widget (GTK_DIALOG (dialog), button, GTK_RESPONSE_ACCEPT);	        		      			
	        gtk_dialog_add_button (GTK_DIALOG (dialog), _("_Don't Save"), GTK_RESPONSE_REJECT);			 
						 
		gtk_dialog_set_default_response	(GTK_DIALOG (dialog), GTK_RESPONSE_REJECT);
		
		response = gtk_dialog_run (GTK_DIALOG (dialog));
		
		gtk_widget_destroy (dialog);
		
		if (response == GTK_RESPONSE_REJECT)
		{
			g_free (display_path);
			return;
		}
	}
		  
	/* Interestingly; we cannot use `path' after glade_project_reset_path
	 * because we are getting called with glade_project_get_path (project) as an argument.
	 */
	if (!glade_project_save (project, path, &error))
	{
		/* Reset path so future saves will prompt the file chooser */
		glade_project_reset_path (project);

		if (error)
		{
			glade_util_ui_message (GTK_WIDGET (window), GLADE_UI_ERROR, NULL, 
					       _("Failed to save %s: %s"),
					       display_path, error->message);
			g_error_free (error);
		}
		g_free (display_path);
		return;
	}
	
	glade_app_update_instance_count (project);

	/* Get display_name here, it could have changed with "Save As..." */
	display_name = glade_project_get_name (project);

	recent_add (window, glade_project_get_path (project));
	update_default_path (window, project);

	/* refresh names */
	refresh_title (window);
	refresh_projects_list_item (window, project);

	glade_util_flash_message (window->priv->statusbar,
				  window->priv->statusbar_actions_context_id,
				  _("Project '%s' saved"), display_name);

	g_free (display_path);
	g_free (display_name);
}

static void
save_as (GladeWindow *window)
{
 	GladeProject *project, *another_project;
 	GtkWidget    *filechooser;
 	GtkWidget    *dialog;
	gchar *path = NULL;
	gchar *real_path, *ch, *project_name;
	
	project = glade_design_view_get_project (window->priv->active_view);
	
	if (project == NULL)
		return;

	filechooser = glade_util_file_dialog_new (_("Save As\342\200\246"), project,
						  GTK_WINDOW (window),
						  GLADE_FILE_DIALOG_ACTION_SAVE);

	if (glade_project_get_path (project))
	{
		gtk_file_chooser_set_filename (GTK_FILE_CHOOSER (filechooser), glade_project_get_path (project));
	}
	else	
	{
		gchar *default_path = g_strdup (get_default_path (window));
		if (default_path != NULL)
		{
			gtk_file_chooser_set_current_folder (GTK_FILE_CHOOSER (filechooser), default_path);
			g_free (default_path);
		}

		project_name = glade_project_get_name (project);
		gtk_file_chooser_set_current_name (GTK_FILE_CHOOSER (filechooser), project_name);
		g_free (project_name);
	}
	
 	if (gtk_dialog_run (GTK_DIALOG(filechooser)) == GTK_RESPONSE_OK)
		path = gtk_file_chooser_get_filename (GTK_FILE_CHOOSER (filechooser));
	
 	gtk_widget_destroy (filechooser);
 
 	if (!path)
 		return;

	ch = strrchr (path, '.');
	if (!ch || strchr (ch, G_DIR_SEPARATOR))
		real_path = g_strconcat (path, ".glade", NULL);
	else 
		real_path = g_strdup (path);
	
	g_free (path);

	/* checks if selected path is actually writable */
	if (glade_util_file_is_writeable (real_path) == FALSE)
	{
		dialog = gtk_message_dialog_new (GTK_WINDOW (window),
						 GTK_DIALOG_MODAL,
						 GTK_MESSAGE_ERROR,
						 GTK_BUTTONS_OK,
						 _("Could not save the file %s"),
						 real_path);
						 
		gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (dialog),
							  _("You do not have the permissions "
							    "necessary to save the file."));
						 	
		gtk_window_set_title (GTK_WINDOW (dialog), "");

		g_signal_connect_swapped (dialog, "response",
					  G_CALLBACK (gtk_widget_destroy),
					  dialog);

		gtk_widget_show (dialog);
		g_free (real_path);
		return;
	}

	/* checks if another open project is using selected path */
	if ((another_project = glade_app_get_project_by_path (real_path)) != NULL)
	{
		if (project != another_project) {

			glade_util_ui_message (GTK_WIDGET (window), 
					       GLADE_UI_ERROR, NULL,
				     	       _("Could not save file %s. Another project with that path is open."), 
					       real_path);

			g_free (real_path);
			return;
		}

	}

	save (window, project, real_path);

	g_free (real_path);
}

static void
save_cb (GtkAction *action, GladeWindow *window)
{
	GladeProject *project;

	project = glade_design_view_get_project (window->priv->active_view);

	if (project == NULL)
	{
		/* Just in case the menu-item or button is not insensitive */
		glade_util_ui_message (GTK_WIDGET (window), GLADE_UI_WARN, NULL,
				       _("No open projects to save"));
		return;
	}

	if (glade_project_get_path (project) != NULL) 
	{
		save (window, project, glade_project_get_path (project));
 		return;
	}

	/* If instead we dont have a path yet, fire up a file selector */
	save_as (window);
}

static void
save_as_cb (GtkAction *action, GladeWindow *window)
{
	save_as (window);
}
static gboolean
confirm_close_project (GladeWindow *window, GladeProject *project)
{
	GtkWidget *dialog;
	gboolean close = FALSE;
	gchar *msg, *project_name = NULL;
	gint ret;
	GError *error = NULL;

	project_name = glade_project_get_name (project);

	msg = g_strdup_printf (_("Save changes to project \"%s\" before closing?"),
			       project_name);

	dialog = gtk_message_dialog_new (GTK_WINDOW (window),
					 GTK_DIALOG_MODAL,
					 GTK_MESSAGE_WARNING,
					 GTK_BUTTONS_NONE,
					 "%s",
					 msg);
	gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (dialog),
						  "%s",
						  _("Your changes will be lost if you don't save them."));
	gtk_window_set_position (GTK_WINDOW (dialog), GTK_WIN_POS_CENTER);

	gtk_dialog_add_buttons (GTK_DIALOG (dialog),
				_("_Close without Saving"), GTK_RESPONSE_NO,
				GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL,
				GTK_STOCK_SAVE, GTK_RESPONSE_YES, NULL);

	gtk_dialog_set_alternative_button_order (GTK_DIALOG (dialog),
						 GTK_RESPONSE_YES,
						 GTK_RESPONSE_CANCEL,
						 GTK_RESPONSE_NO,
						 -1);

	gtk_dialog_set_default_response	(GTK_DIALOG (dialog), GTK_RESPONSE_YES);

	ret = gtk_dialog_run (GTK_DIALOG (dialog));
	switch (ret) {
	case GTK_RESPONSE_YES:
		/* if YES we save the project: note we cannot use save_cb
		 * since it saves the current project, while the modified 
                 * project we are saving may be not the current one.
		 */
		if (glade_project_get_path (project) != NULL)
		{
			if ((close = glade_project_save
			     (project, glade_project_get_path (project), &error)) == FALSE)
			{

				glade_util_ui_message
					(GTK_WIDGET (window), GLADE_UI_ERROR, NULL, 
					 _("Failed to save %s to %s: %s"),
					 project_name, glade_project_get_path (project), error->message);
				g_error_free (error);
			}
		}
		else
		{
			GtkWidget *filechooser;
			gchar *path = NULL;
			gchar *default_path;

			filechooser =
				glade_util_file_dialog_new (_("Save\342\200\246"), project,
							    GTK_WINDOW (window),
							    GLADE_FILE_DIALOG_ACTION_SAVE);
	
			default_path = g_strdup (get_default_path (window));
			if (default_path != NULL)
			{
				gtk_file_chooser_set_current_folder (GTK_FILE_CHOOSER (filechooser), default_path);
				g_free (default_path);
			}

			gtk_file_chooser_set_current_name
				(GTK_FILE_CHOOSER (filechooser), project_name);

			
			if (gtk_dialog_run (GTK_DIALOG(filechooser)) == GTK_RESPONSE_OK)
				path = gtk_file_chooser_get_filename (GTK_FILE_CHOOSER (filechooser));

			gtk_widget_destroy (filechooser);

			if (!path)
				break;

			save (window, project, path);

			g_free (path);

			close = FALSE;
		}
		break;
	case GTK_RESPONSE_NO:
		close = TRUE;
		break;
	case GTK_RESPONSE_CANCEL:
	case GTK_RESPONSE_DELETE_EVENT:
		close = FALSE;
		break;
	default:
		g_assert_not_reached ();
		close = FALSE;
	}

	g_free (msg);
	g_free (project_name);
	gtk_widget_destroy (dialog);
	
	return close;
}

static void
do_close (GladeWindow *window, GladeDesignView *view)
{
	gint n;
	
	n = gtk_notebook_page_num (GTK_NOTEBOOK (window->priv->notebook), GTK_WIDGET (view));
	
	g_object_ref (view);
	
	gtk_notebook_remove_page (GTK_NOTEBOOK (window->priv->notebook), n);
	
	g_object_unref (view);	
}

static void
close_cb (GtkAction *action, GladeWindow *window)
{
	GladeDesignView *view;
	GladeProject *project;
	gboolean close;
	
	view = window->priv->active_view;

	project = glade_design_view_get_project (view);

	if (view == NULL)
		return;

	if (glade_project_get_modified (project))
	{
		close = confirm_close_project (window, project);
			if (!close)
				return;
	}
	do_close (window, view);
}

static void
quit_cb (GtkAction *action, GladeWindow *window)
{
	GList *list;

	for (list = glade_app_get_projects (); list; list = list->next)
	{
		GladeProject *project = GLADE_PROJECT (list->data);

		if (glade_project_get_modified (project))
		{
			gboolean quit = confirm_close_project (window, project);
			if (!quit)
				return;
		}
	}

	while (glade_app_get_projects ())
	{
		GladeProject *project = GLADE_PROJECT (glade_app_get_projects ()->data);
		do_close (window, glade_design_view_get_from_project (project));
	}

	glade_window_config_save (window);

	gtk_main_quit ();

}

static void
copy_cb (GtkAction *action, GladeWindow *window)
{
	glade_app_command_copy ();
}

static void
cut_cb (GtkAction *action, GladeWindow *window)
{
	glade_app_command_cut ();
}

static void
paste_cb (GtkAction *action, GladeWindow *window)
{
	glade_app_command_paste (NULL);
}

static void
delete_cb (GtkAction *action, GladeWindow *window)
{
	if (!glade_app_get_project ())
	{
		g_warning ("delete should not be sensitive: we don't have a project");
		return;
	}
	glade_app_command_delete ();
}

static void
preferences_cb (GtkAction *action, GladeWindow *window)
{
	GladeProject *project;

	if (!window->priv->active_view)
		return;

	project = glade_design_view_get_project (window->priv->active_view);

	glade_project_preferences (project);
}

static void
undo_cb (GtkAction *action, GladeWindow *window)
{
	if (!glade_app_get_project ())
	{
		g_warning ("undo should not be sensitive: we don't have a project");
		return;
	}
	glade_app_command_undo ();
}

static void
redo_cb (GtkAction *action, GladeWindow *window)
{
	if (!glade_app_get_project ())
	{
		g_warning ("redo should not be sensitive: we don't have a project");
		return;
	}
	glade_app_command_redo ();
}

static void
doc_search_cb (GladeEditor        *editor,
	       const gchar        *book,
	       const gchar        *page,
	       const gchar        *search,
	       GladeWindow *window)
{
	glade_util_search_devhelp (book, page, search);
}

static void
previous_project_cb (GtkAction *action, GladeWindow *window)
{
	gtk_notebook_prev_page (GTK_NOTEBOOK (window->priv->notebook));
}

static void
next_project_cb (GtkAction *action, GladeWindow *window)
{
	gtk_notebook_next_page (GTK_NOTEBOOK (window->priv->notebook));
}

static void
notebook_switch_page_cb (GtkNotebook *notebook,
			     GtkNotebookPage *page,
			     guint page_num,
			     GladeWindow *window)
{
	GladeDesignView *view;
	GladeProject *project;
	GtkAction *action;
	gchar *action_name;

	view = GLADE_DESIGN_VIEW (gtk_notebook_get_nth_page (notebook, page_num));

	/* CHECK: I don't know why but it seems notebook_switch_page is called
	two times every time the user change the active tab */
	if (view == window->priv->active_view)
		return;

	window->priv->active_view = view;
	
	project = glade_design_view_get_project (view);

	/* FIXME: this does not feel good */
	glade_app_set_project (project);

	refresh_title (window);
	set_sensitivity_according_to_project (window, project);
	
	/* switch to the project's inspector */
	gtk_notebook_set_current_page (GTK_NOTEBOOK (window->priv->inspectors_notebook), page_num);	
	
	/* activate the corresponding item in the project menu */
	action_name = g_strdup_printf ("Tab_%d", page_num);
	action = gtk_action_group_get_action (window->priv->projects_list_menu_actions,
					      action_name);

	/* sometimes the action doesn't exist yet, and the proper action
	 * is set active during the documents list menu creation
	 * CHECK: would it be nicer if active_view was a property and we monitored the notify signal?
	 */
	if (action != NULL)
		gtk_toggle_action_set_active (GTK_TOGGLE_ACTION (action), TRUE);

	g_free (action_name);
}

static void
notebook_tab_added_cb (GtkNotebook *notebook,
			   GladeDesignView *view,
			   guint page_num,
			   GladeWindow *window)
{
	GladeProject *project;
	GtkWidget    *inspector;

	++window->priv->num_tabs;
	
	project = glade_design_view_get_project (view);

	g_signal_connect (G_OBJECT (project), "notify::modified",
			  G_CALLBACK (project_notify_handler_cb),
			  window);	
	g_signal_connect (G_OBJECT (project), "selection-changed",
			  G_CALLBACK (project_selection_changed_cb), window);
	g_signal_connect (G_OBJECT (project), "notify::has-selection",
			  G_CALLBACK (project_notify_handler_cb),
			  window);
	g_signal_connect (G_OBJECT (project), "notify::read-only",
			  G_CALLBACK (project_notify_handler_cb),
			  window);

	/* create inspector */
	inspector = glade_inspector_new ();
	gtk_widget_show (inspector);
	glade_inspector_set_project (GLADE_INSPECTOR (inspector), project);
		
	gtk_notebook_append_page (GTK_NOTEBOOK (window->priv->inspectors_notebook), inspector, NULL);
	

	set_sensitivity_according_to_project (window, project);

	refresh_projects_list_menu (window);

	refresh_title (window);

	project_selection_changed_cb (glade_app_get_project (), window);
		
	if (window->priv->num_tabs > 0)
		gtk_action_group_set_sensitive (window->priv->project_actions, TRUE);

}

static void
notebook_tab_removed_cb (GtkNotebook *notebook,
			     GladeDesignView *view,
			     guint page_num,
			     GladeWindow *window)
{
	GladeProject   *project;

	--window->priv->num_tabs;

	if (window->priv->num_tabs == 0)
		window->priv->active_view = NULL;

	project = glade_design_view_get_project (view);	

	g_signal_handlers_disconnect_by_func (G_OBJECT (project),
					      G_CALLBACK (project_notify_handler_cb),
					      window);
	g_signal_handlers_disconnect_by_func (G_OBJECT (project),
					      G_CALLBACK (project_selection_changed_cb),
					      window);


	gtk_notebook_remove_page (GTK_NOTEBOOK (window->priv->inspectors_notebook), page_num);

	clean_actions (window);

	/* FIXME: this function needs to be preferably called somewhere else */
	glade_app_remove_project (project);

	refresh_projects_list_menu (window);

	refresh_title (window);

	project_selection_changed_cb (glade_app_get_project (), window);
		
	if (window->priv->active_view)
		set_sensitivity_according_to_project (window, glade_design_view_get_project (window->priv->active_view));
	else
		gtk_action_group_set_sensitive (window->priv->project_actions, FALSE);	

}

static void
recent_chooser_item_activated_cb (GtkRecentChooser *chooser, GladeWindow *window)
{
	gchar *uri, *path;
	GError *error = NULL;

	uri = gtk_recent_chooser_get_current_uri (chooser);

	path = g_filename_from_uri (uri, NULL, NULL);
	if (error)
	{
		g_warning ("Could not convert uri \"%s\" to a local path: %s", uri, error->message);
		g_error_free (error);
		return;
	}

	glade_window_open_project (window, path);

	g_free (uri);
	g_free (path);
}

static void
palette_appearance_change_cb (GtkRadioAction *action,
				  GtkRadioAction *current,
				  GladeWindow *window)
{
	gint value;

	value = gtk_radio_action_get_current_value (action);

	glade_palette_set_item_appearance (glade_app_get_palette (), value);

}

static void
palette_toggle_small_icons_cb (GtkAction *action, GladeWindow *window)
{
	glade_palette_set_use_small_item_icons (glade_app_get_palette(),
						gtk_toggle_action_get_active (GTK_TOGGLE_ACTION (action)));
}

static gboolean
on_dock_deleted (GtkWidget *widget,
		 GdkEvent  *event,
		 GtkAction *dock_action)
{
	gtk_toggle_action_set_active (GTK_TOGGLE_ACTION (dock_action), TRUE);
	return TRUE;
}

static gboolean
on_dock_resized (GtkWidget         *window,
		 GdkEventConfigure *event,
		 ToolDock          *dock)
{
	dock->window_pos.width = event->width;
	dock->window_pos.height = event->height;

	gtk_window_get_position (GTK_WINDOW (window),
				 &dock->window_pos.x,
				 &dock->window_pos.y);

	return FALSE;
}

static void
toggle_dock_cb (GtkAction *action, GladeWindow *window)
{
	GtkWidget *toplevel, *alignment;
	ToolDock *dock;
	guint dock_type;

	dock_type = GPOINTER_TO_UINT (g_object_get_data (G_OBJECT (action), "glade-dock-type"));
	g_return_if_fail (dock_type < N_DOCKS);

	dock = &window->priv->docks[dock_type];

	if (gtk_toggle_action_get_active (GTK_TOGGLE_ACTION (action)))
	{
		toplevel = gtk_widget_get_toplevel (dock->widget);

		g_object_ref (dock->widget);
		gtk_container_remove (GTK_CONTAINER 
				      (GTK_BIN (toplevel)->child), dock->widget);

		if (dock->first_child)
			gtk_paned_pack1 (GTK_PANED (dock->paned), dock->widget, FALSE, FALSE);
		else
			gtk_paned_pack2 (GTK_PANED (dock->paned), dock->widget, FALSE, FALSE);
		g_object_unref (dock->widget);

		gtk_widget_show (dock->paned);
		dock->detached = FALSE;

		gtk_widget_destroy (toplevel);
	} else {
		toplevel = gtk_window_new (GTK_WINDOW_TOPLEVEL);

		/* Add a little padding on top to match the bottom */
		alignment = gtk_alignment_new (0.5, 0.5, 1.0, 1.0);
		gtk_alignment_set_padding (GTK_ALIGNMENT (alignment),
					   4, 0, 0, 0);
		gtk_container_add (GTK_CONTAINER (toplevel), alignment);
		gtk_widget_show (alignment);

		gtk_window_set_default_size (GTK_WINDOW (toplevel),
					     dock->window_pos.width,
					     dock->window_pos.height);

		if (dock->window_pos.x > G_MININT && dock->window_pos.y > G_MININT)
			gtk_window_move (GTK_WINDOW (toplevel),
					 dock->window_pos.x,
					 dock->window_pos.y);

		gtk_window_set_title (GTK_WINDOW (toplevel), dock->title);
		g_object_ref (dock->widget);
		gtk_container_remove (GTK_CONTAINER (dock->paned), dock->widget);
		gtk_container_add (GTK_CONTAINER (alignment), dock->widget);
		g_object_unref (dock->widget);

		g_signal_connect (G_OBJECT (toplevel), "delete-event",
				  G_CALLBACK (on_dock_deleted), action);
		g_signal_connect (G_OBJECT (toplevel), "configure-event",
				  G_CALLBACK (on_dock_resized), dock);

		if (!GTK_PANED (dock->paned)->child1 &&
		    !GTK_PANED (dock->paned)->child2)
			gtk_widget_hide (dock->paned);


		gtk_window_add_accel_group (GTK_WINDOW (toplevel), 
					    gtk_ui_manager_get_accel_group (window->priv->ui));

		g_signal_connect (G_OBJECT (toplevel), "key-press-event",
				  G_CALLBACK (glade_utils_hijack_key_press), window);

		dock->detached = TRUE;

		gtk_window_present (GTK_WINDOW (toplevel));
	}
}

static void
show_help_cb (GtkAction *action, GladeWindow *window)
{
	GtkWidget *dialog;
	gboolean retval;
	
	retval = help_show (NULL);
	if (retval)
		return;
	
	/* fallback to displaying online user manual */ 
	retval = glade_util_url_show (URL_USER_MANUAL);	

	if (!retval)
	{
		dialog = gtk_message_dialog_new (GTK_WINDOW (window),
						 GTK_DIALOG_MODAL,
						 GTK_MESSAGE_ERROR,
						 GTK_BUTTONS_OK,
						 _("Could not display the online user manual"));
						 
		gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (dialog),
							  _("No suitable web browser executable could be found "
							    "to be executed and to display the URL: %s"),
							    URL_USER_MANUAL);
						 	
		gtk_window_set_title (GTK_WINDOW (dialog), "");

		g_signal_connect_swapped (dialog, "response",
					  G_CALLBACK (gtk_widget_destroy),
					  dialog);

		gtk_widget_show (dialog);
		
	}
}

static void 
show_developer_manual_cb (GtkAction *action, GladeWindow *window)
{
	GtkWidget *dialog;
	gboolean retval;
	
	if (glade_util_have_devhelp ())
	{
		glade_util_search_devhelp ("gladeui", NULL, NULL);
		return;	
	}
	
	retval = glade_util_url_show (URL_DEVELOPER_MANUAL);	

	if (!retval)
	{
		dialog = gtk_message_dialog_new (GTK_WINDOW (window),
						 GTK_DIALOG_MODAL,
						 GTK_MESSAGE_ERROR,
						 GTK_BUTTONS_OK,
						 _("Could not display the online developer reference manual"));
						 
		gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (dialog),
							  _("No suitable web browser executable could be found "
							    "to be executed and to display the URL: %s"),
							    URL_DEVELOPER_MANUAL);
						 	
		gtk_window_set_title (GTK_WINDOW (dialog), "");

		g_signal_connect_swapped (dialog, "response",
					  G_CALLBACK (gtk_widget_destroy),
					  dialog);

		gtk_widget_show (dialog);
	}	
}

static void 
about_cb (GtkAction *action, GladeWindow *window)
{
	static const gchar * const authors[] =
		{ "Chema Celorio <chema@ximian.com>",
		  "Joaquin Cuenca Abela <e98cuenc@yahoo.com>",
		  "Paolo Borelli <pborelli@katamail.com>",
		  "Archit Baweja <bighead@users.sourceforge.net>",
		  "Shane Butler <shane_b@operamail.com>",
		  "Tristan Van Berkom <tvb@gnome.org>",
		  "Ivan Wong <email@ivanwong.info>",
		  "Juan Pablo Ugarte <juanpablougarte@gmail.com>",
		  "Vincent Geddes <vincent.geddes@gmail.com>",
		  NULL };
		  
	static const gchar * const artists[] =
		{ "Vincent Geddes <vgeddes@gnome.org>",
		  "Andreas Nilsson <andreas@andreasn.se>",
		  NULL };
		  
	static const gchar * const documenters[] =
		{ "GNOME Documentation Team <gnome-doc-list@gnome.org>",
		  "Sun GNOME Documentation Team <gdocteam@sun.com>",
		  NULL };		  		  

	static const gchar license[] =
		N_("Glade is free software; you can redistribute it and/or modify "
		  "it under the terms of the GNU General Public License as "
		  "published by the Free Software Foundation; either version 2 of the "
		  "License, or (at your option) any later version."
		  "\n\n"
		  "Glade is distributed in the hope that it will be useful, "
		  "but WITHOUT ANY WARRANTY; without even the implied warranty of "
		  "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
		  "GNU General Public License for more details."
		  "\n\n"
		  "You should have received a copy of the GNU General Public License "
		  "along with Glade; if not, write to the Free Software "
		  "Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, "
		  "MA 02110-1301, USA.");

	static const gchar copyright[] =
		"Copyright \xc2\xa9 2001-2006 Ximian, Inc.\n"
		"Copyright \xc2\xa9 2001-2006 Joaquin Cuenca Abela, Paolo Borelli, et al.\n"
		"Copyright \xc2\xa9 2001-2008 Tristan Van Berkom, Juan Pablo Ugarte, et al.";
	
	gtk_show_about_dialog (GTK_WINDOW (window),
			       "name", g_get_application_name (),
			       "logo-icon-name", "glade-3",
			       "authors", authors,
			       "artists", artists,
			       "documenters", documenters,			       			       
			       "translator-credits", _("translator-credits"),
			       "comments", _("A user interface designer for GTK+ and GNOME."),
			       "license", _(license),
			       "wrap-license", TRUE,
			       "copyright", copyright,
			       "version", PACKAGE_VERSION,
			       "website", "http://glade.gnome.org",
			       NULL);
}

static const gchar ui_info[] =
"<ui>"
"  <menubar name='MenuBar'>"
"    <menu action='FileMenu'>"
"      <menuitem action='New'/>"
"      <menuitem action='Open'/>"
"      <menuitem action='OpenRecent'/>"
"      <separator/>"
"      <menuitem action='Save'/>"
"      <menuitem action='SaveAs'/>"
"      <separator/>"
"      <menuitem action='Close'/>"
"      <menuitem action='Quit'/>"
"    </menu>"
"    <menu action='EditMenu'>"
"      <menuitem action='Undo'/>"
"      <menuitem action='Redo'/>"
"      <separator/>"
"      <menuitem action='Cut'/>"
"      <menuitem action='Copy'/>"
"      <menuitem action='Paste'/>"
"      <menuitem action='Delete'/>"
"      <separator/>"
"      <menuitem action='Preferences'/>"
"    </menu>"
"    <menu action='ViewMenu'>"
"      <menu action='PaletteAppearance'>"
"        <menuitem action='IconsAndLabels'/>"
"        <menuitem action='IconsOnly'/>"
"        <menuitem action='LabelsOnly'/>"
"        <separator/>"
"        <menuitem action='UseSmallIcons'/>"
"      </menu>"
"      <separator/>"
"      <menuitem action='DockPalette'/>"
"      <menuitem action='DockInspector'/>"
"      <menuitem action='DockEditor'/>"
"    </menu>"
"    <menu action='ProjectMenu'>"
"      <menuitem action='PreviousProject'/>"
"      <menuitem action='NextProject'/>"
"      <separator/>"
"      <placeholder name='ProjectsListPlaceholder'/>"
"    </menu>"
"    <menu action='HelpMenu'>"
"      <menuitem action='HelpContents'/>"
"      <menuitem action='DeveloperReference'/>"
"      <separator/>"
"      <menuitem action='About'/>"
"    </menu>"
"  </menubar>"
"  <toolbar  name='ToolBar'>"
"    <toolitem action='New'/>"
"    <toolitem action='Open'/>"
"    <toolitem action='Save'/>"
"    <separator/>"
"    <toolitem action='Cut'/>"
"    <toolitem action='Copy'/>"
"    <toolitem action='Paste'/>"
"  </toolbar>"
"</ui>";

static GtkActionEntry static_entries[] = {
	{ "FileMenu", NULL, N_("_File") },
	{ "EditMenu", NULL, N_("_Edit") },
	{ "ViewMenu", NULL, N_("_View") },
	{ "ProjectMenu", NULL, N_("_Projects") },
	{ "HelpMenu", NULL, N_("_Help") },
	{ "UndoMenu", NULL, NULL },
	{ "RedoMenu", NULL, NULL },
	
	/* FileMenu */
	{ "New", GTK_STOCK_NEW, NULL, "<control>N",
	  N_("Create a new project"), G_CALLBACK (new_cb) },
	
	{ "Open", GTK_STOCK_OPEN, N_("_Open\342\200\246") ,"<control>O",
	  N_("Open a project"), G_CALLBACK (open_cb) },

	{ "OpenRecent", NULL, N_("Open _Recent") },	
	
	{ "Quit", GTK_STOCK_QUIT, NULL, "<control>Q",
	  N_("Quit the program"), G_CALLBACK (quit_cb) },

	/* ViewMenu */
	{ "PaletteAppearance", NULL, N_("Palette _Appearance") },
	
	/* HelpMenu */
	{ "About", GTK_STOCK_ABOUT, NULL, NULL,
	  N_("About this application"), G_CALLBACK (about_cb) },

	{ "HelpContents", GTK_STOCK_HELP, N_("_Contents"), "F1",
	  N_("Display the user manual"), G_CALLBACK (show_help_cb) },

	{ "DeveloperReference", NULL, N_("_Developer Reference"), NULL,
	  N_("Display the developer reference manual"), G_CALLBACK (show_developer_manual_cb) }
};

static guint n_static_entries = G_N_ELEMENTS (static_entries);

static GtkActionEntry project_entries[] = {

	/* FileMenu */
	{ "Save", GTK_STOCK_SAVE, NULL, "<control>S",
	  N_("Save the current project"), G_CALLBACK (save_cb) },
	
	{ "SaveAs", GTK_STOCK_SAVE_AS, N_("Save _As\342\200\246"), NULL,
	  N_("Save the current project with a different name"), G_CALLBACK (save_as_cb) },
	
	{ "Close", GTK_STOCK_CLOSE, NULL, "<control>W",
	  N_("Close the current project"), G_CALLBACK (close_cb) },

	/* EditMenu */	
	{ "Undo", GTK_STOCK_UNDO, NULL, "<control>Z",
	  N_("Undo the last action"),	G_CALLBACK (undo_cb) },
	
	{ "Redo", GTK_STOCK_REDO, NULL, "<shift><control>Z",
	  N_("Redo the last action"),	G_CALLBACK (redo_cb) },
	
	{ "Cut", GTK_STOCK_CUT, NULL, NULL,
	  N_("Cut the selection"), G_CALLBACK (cut_cb) },
	
	{ "Copy", GTK_STOCK_COPY, NULL, NULL,
	  N_("Copy the selection"), G_CALLBACK (copy_cb) },
	
	{ "Paste", GTK_STOCK_PASTE, NULL, NULL,
	  N_("Paste the clipboard"), G_CALLBACK (paste_cb) },
	
	{ "Delete", GTK_STOCK_DELETE, NULL, "Delete",
	  N_("Delete the selection"), G_CALLBACK (delete_cb) },

	{ "Preferences", GTK_STOCK_PREFERENCES, NULL, "<control>P",
	  N_("Modify project preferences"), G_CALLBACK (preferences_cb) },
	  
	/* ProjectsMenu */
	{ "PreviousProject", NULL, N_("_Previous Project"), "<control>Page_Up",
	  N_("Activate previous project"), G_CALLBACK (previous_project_cb) },

	{ "NextProject", NULL, N_("_Next Project"), "<control>Page_Down",
	  N_("Activate next project"), G_CALLBACK (next_project_cb) }


};
static guint n_project_entries = G_N_ELEMENTS (project_entries);

static GtkToggleActionEntry view_entries[] = {

	{ "UseSmallIcons", NULL, N_("_Use Small Icons"), NULL,
	  N_("Show items using small icons"),
	  G_CALLBACK (palette_toggle_small_icons_cb), FALSE },

	{ "DockPalette", NULL, N_("Dock _Palette"), NULL,
	  N_("Dock the palette into the main window"),
	  G_CALLBACK (toggle_dock_cb), TRUE },

	{ "DockInspector", NULL, N_("Dock _Inspector"), NULL,
	  N_("Dock the inspector into the main window"),
	  G_CALLBACK (toggle_dock_cb), TRUE },

	{ "DockEditor", NULL, N_("Dock Prop_erties"), NULL,
	  N_("Dock the editor into the main window"),
	  G_CALLBACK (toggle_dock_cb), TRUE },

};
static guint n_view_entries = G_N_ELEMENTS (view_entries);

static GtkRadioActionEntry radio_entries[] = {

	{ "IconsAndLabels", NULL, N_("Text beside icons"), NULL, 
	  N_("Display items as text beside icons"), GLADE_ITEM_ICON_AND_LABEL },

	{ "IconsOnly", NULL, N_("_Icons only"), NULL, 
	  N_("Display items as icons only"), GLADE_ITEM_ICON_ONLY },

	{ "LabelsOnly", NULL, N_("_Text only"), NULL, 
	  N_("Display items as text only"), GLADE_ITEM_LABEL_ONLY },
};
static guint n_radio_entries = G_N_ELEMENTS (radio_entries);

static void
menu_item_selected_cb (GtkWidget *item, GladeWindow *window)
{
	GtkAction *action;
	gchar *tooltip;

#if (GTK_MAJOR_VERSION == 2) && (GTK_MINOR_VERSION < 16)
	action = gtk_widget_get_action (item);
#else
	action = gtk_activatable_get_related_action (GTK_ACTIVATABLE (item));
#endif
	g_object_get (G_OBJECT (action), "tooltip", &tooltip, NULL);

	if (tooltip != NULL)
		gtk_statusbar_push (GTK_STATUSBAR (window->priv->statusbar),
				    window->priv->statusbar_menu_context_id, tooltip);

	g_free (tooltip);
}

static void
menu_item_deselected_cb (GtkItem *item, GladeWindow *window)
{
	gtk_statusbar_pop (GTK_STATUSBAR (window->priv->statusbar),
			   window->priv->statusbar_menu_context_id);
}

static void
ui_connect_proxy_cb (GtkUIManager *ui,
		         GtkAction    *action,
		         GtkWidget    *proxy,
		         GladeWindow *window)
{	
	if (GTK_IS_MENU_ITEM (proxy))
	{
		g_signal_connect(G_OBJECT(proxy), "select",
				 G_CALLBACK (menu_item_selected_cb), window);
		g_signal_connect(G_OBJECT(proxy), "deselect", 
				 G_CALLBACK (menu_item_deselected_cb), window);
	}
}

static void
ui_disconnect_proxy_cb (GtkUIManager *manager,
                     	    GtkAction *action,
                            GtkWidget *proxy,
                            GladeWindow *window)
{
	if (GTK_IS_MENU_ITEM (proxy))
	{
		g_signal_handlers_disconnect_by_func
                	(proxy, G_CALLBACK (menu_item_selected_cb), window);
		g_signal_handlers_disconnect_by_func
			(proxy, G_CALLBACK (menu_item_deselected_cb), window);
	}
}

static GtkWidget *
construct_menu (GladeWindow *window)
{
	GError *error = NULL;
	
	window->priv->static_actions = gtk_action_group_new (ACTION_GROUP_STATIC);
	gtk_action_group_set_translation_domain (window->priv->static_actions, GETTEXT_PACKAGE);

	gtk_action_group_add_actions (window->priv->static_actions,
				      static_entries,
				      n_static_entries,
				      window);
	gtk_action_group_add_toggle_actions (window->priv->static_actions, 
					     view_entries,
					     n_view_entries, 
					     window);
	gtk_action_group_add_radio_actions (window->priv->static_actions, radio_entries,
					    n_radio_entries, GLADE_ITEM_ICON_ONLY,
					    G_CALLBACK (palette_appearance_change_cb), window);

	window->priv->project_actions = gtk_action_group_new (ACTION_GROUP_PROJECT);
	gtk_action_group_set_translation_domain (window->priv->project_actions, GETTEXT_PACKAGE);

	gtk_action_group_add_actions (window->priv->project_actions,
				      project_entries,
				      n_project_entries,
				      window);

	window->priv->projects_list_menu_actions = 
		gtk_action_group_new (ACTION_GROUP_PROJECTS_LIST_MENU);
	gtk_action_group_set_translation_domain (window->priv->projects_list_menu_actions, 
						 GETTEXT_PACKAGE);
	
	window->priv->ui = gtk_ui_manager_new ();

	g_signal_connect(G_OBJECT(window->priv->ui), "connect-proxy",
			 G_CALLBACK (ui_connect_proxy_cb), window);
	g_signal_connect(G_OBJECT(window->priv->ui), "disconnect-proxy",
			 G_CALLBACK (ui_disconnect_proxy_cb), window);

	gtk_ui_manager_insert_action_group (window->priv->ui, window->priv->static_actions, 0);
	gtk_ui_manager_insert_action_group (window->priv->ui, window->priv->project_actions, 1);
	gtk_ui_manager_insert_action_group (window->priv->ui, window->priv->projects_list_menu_actions, 3);
	
	gtk_window_add_accel_group (GTK_WINDOW (window), 
				    gtk_ui_manager_get_accel_group (window->priv->ui));

	glade_app_set_accel_group (gtk_ui_manager_get_accel_group (window->priv->ui));

	if (!gtk_ui_manager_add_ui_from_string (window->priv->ui, ui_info, -1, &error))
	{
		g_message ("Building menus failed: %s", error->message);
		g_error_free (error);
	}
	
	return gtk_ui_manager_get_widget (window->priv->ui, "/MenuBar");
}

enum
{
	TARGET_URI_LIST
};

static GtkTargetEntry drop_types[] =
{
	{"text/uri-list", 0, TARGET_URI_LIST}
};

static void
drag_data_received (GtkWidget *widget,
			GdkDragContext *context,
			gint x, gint y,
			GtkSelectionData *selection_data,
			guint info, guint time, GladeWindow *window)
{
	gchar **uris, **str;
	gchar *data;

	if (info != TARGET_URI_LIST)
		return;

	/* On MS-Windows, it looks like `selection_data->data' is not NULL terminated. */
	data = g_new (gchar, selection_data->length + 1);
	memcpy (data, selection_data->data, selection_data->length);
	data[selection_data->length] = 0;

	uris = g_uri_list_extract_uris (data);

	for (str = uris; *str; str++)
	{
		GError *error = NULL;
		gchar *path = g_filename_from_uri (*str, NULL, &error);

		if (path)
		{
			glade_window_open_project (window, path);
		}
		else
		{
			g_warning ("Could not convert uri to local path: %s", error->message); 

			g_error_free (error);
		}
		g_free (path);
	}
	g_strfreev (uris);
}

static gboolean
delete_event (GtkWindow *w, GdkEvent *event, GladeWindow *window)
{
	quit_cb (NULL, window);
	
	/* return TRUE to stop other handlers */
	return TRUE;	
}

static GtkWidget *
create_selector_tool_button (GtkToolbar *toolbar)
{
	GtkToolItem  *button;
	GtkWidget    *image;
	gchar        *image_path;
	
	image_path = g_build_filename (glade_app_get_pixmaps_dir (), "selector.png", NULL);
	image = gtk_image_new_from_file (image_path);
	g_free (image_path);
	
	button = gtk_toggle_tool_button_new ();
	gtk_toggle_tool_button_set_active (GTK_TOGGLE_TOOL_BUTTON (button), TRUE);
	
	gtk_tool_button_set_icon_widget (GTK_TOOL_BUTTON (button), image);
	gtk_tool_button_set_label (GTK_TOOL_BUTTON (button), _("Select"));
	
	gtk_tool_item_set_tooltip_text (GTK_TOOL_ITEM (button),
				        _("Select widgets in the workspace"));
	
	gtk_widget_show (GTK_WIDGET (button));
	gtk_widget_show (image);
	
	return GTK_WIDGET (button);
}

static GtkWidget *
create_drag_resize_tool_button (GtkToolbar *toolbar)
{
	GtkToolItem  *button;
	GtkWidget    *image;
	gchar        *image_path;
	
	image_path = g_build_filename (glade_app_get_pixmaps_dir (), "drag-resize.png", NULL);
	image = gtk_image_new_from_file (image_path);
	g_free (image_path);
	
	button = gtk_toggle_tool_button_new ();
	gtk_toggle_tool_button_set_active (GTK_TOGGLE_TOOL_BUTTON (button), TRUE);
	
	gtk_tool_button_set_icon_widget (GTK_TOOL_BUTTON (button), image);
	gtk_tool_button_set_label (GTK_TOOL_BUTTON (button), _("Drag Resize"));
	
	gtk_tool_item_set_tooltip_text (GTK_TOOL_ITEM (button),
				        _("Drag and resize widgets in the workspace"));
	
	gtk_widget_show (GTK_WIDGET (button));
	gtk_widget_show (image);
	
	return GTK_WIDGET (button);
}

static void
add_project (GladeWindow *window, GladeProject *project)
{
	GtkWidget *view;

 	g_return_if_fail (GLADE_IS_PROJECT (project));
 	
 	view = glade_design_view_new (project);	
	gtk_widget_show (view);

	/* Pass ownership of the project to the app */
	glade_app_add_project (project);
	g_object_unref (project);

	gtk_notebook_append_page (GTK_NOTEBOOK (window->priv->notebook), GTK_WIDGET (view), NULL);
	gtk_notebook_set_current_page (GTK_NOTEBOOK (window->priv->notebook), -1);	

	/* Kick the inspector in the balls here... */
	glade_project_selection_changed (project);
}

void
glade_window_new_project (GladeWindow *window)
{
	GladeProject *project;
	
	g_return_if_fail (GLADE_IS_WINDOW (window));

	project = glade_project_new ();
	if (!project)
	{
		glade_util_ui_message (GTK_WIDGET (window), 
				       GLADE_UI_ERROR, NULL,
				       _("Could not create a new project."));
		return;
	}
	add_project (window, project);
}

static gboolean
open_project (GladeWindow *window, const gchar *path)
{
	GladeProject *project;
	
	project = glade_project_load (path);
	if (!project)
	{
		recent_remove (window, path);
		return FALSE;
	}
	
	add_project (window, project);

	/* increase project popularity */		
	recent_add (window, glade_project_get_path (project));
	update_default_path (window, project);
	
	return TRUE;

}

static void
check_reload_project (GladeWindow *window, GladeProject *project)
{
	GladeDesignView *view;
	gchar           *path;
	gint             ret;
	
	GtkWidget *dialog;
	GtkWidget *button;
	gint       response;
	
	/* Reopen the project if it has external modifications.
	 * Prompt for permission to reopen.
	 */
	if ((glade_util_get_file_mtime (glade_project_get_path (project), NULL)
	    <= glade_project_get_file_mtime (project)))
	{
		return;
	}

	if (glade_project_get_modified (project))
	{
		dialog = gtk_message_dialog_new (GTK_WINDOW (window),
						 GTK_DIALOG_MODAL,
						 GTK_MESSAGE_WARNING,
						 GTK_BUTTONS_NONE,
						 _("The project %s has unsaved changes"),
						 glade_project_get_path (project));
						 
		gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (dialog), 				 
							  _("If you reload it, all unsaved changes "
							    "could be lost. Reload it anyway?"));			
	}
	else
	{
		dialog = gtk_message_dialog_new (GTK_WINDOW (window),
						 GTK_DIALOG_MODAL,
						 GTK_MESSAGE_WARNING,
						 GTK_BUTTONS_NONE,
						 _("The project file %s has been externally modified"),
						 glade_project_get_path (project));
						 
		gtk_message_dialog_format_secondary_text (GTK_MESSAGE_DIALOG (dialog), 				 
							  _("Do you want to reload the project?"));
							  
	}
	
	gtk_window_set_title (GTK_WINDOW (dialog), "");
	
	button = gtk_button_new_with_mnemonic (_("_Reload"));
	gtk_button_set_image (GTK_BUTTON (button),
        		      gtk_image_new_from_stock (GTK_STOCK_REFRESH,
        		      				GTK_ICON_SIZE_BUTTON));
	gtk_widget_show (button);

	gtk_dialog_add_button (GTK_DIALOG (dialog), GTK_STOCK_CANCEL, GTK_RESPONSE_REJECT);
	gtk_dialog_add_action_widget (GTK_DIALOG (dialog), button, GTK_RESPONSE_ACCEPT);
	gtk_dialog_set_alternative_button_order (GTK_DIALOG (dialog),
						 GTK_RESPONSE_ACCEPT,
						 GTK_RESPONSE_REJECT,
						 -1);

					 
	gtk_dialog_set_default_response	(GTK_DIALOG (dialog), GTK_RESPONSE_REJECT);
	
	response = gtk_dialog_run (GTK_DIALOG (dialog));
	
	gtk_widget_destroy (dialog);
	
	if (response == GTK_RESPONSE_REJECT)
	{
		return;
	}	
		
	/* Reopen */ 
	view = glade_design_view_get_from_project (project);
	path = g_strdup (glade_project_get_path (project));

	do_close (window, view);
	ret = open_project (window, path);
	g_free (path);
}

/** 
 * glade_window_open_project: 
 * @window: a #GladeWindow
 * @path: the filesystem path of the project
 *
 * Opens a project file. If the project is already open, switch to that
 * project.
 * 
 * Returns: #TRUE if the project was opened
 */
gboolean
glade_window_open_project (GladeWindow *window,
			   const gchar *path)
{
	GladeProject *project;

	g_return_val_if_fail (GLADE_IS_WINDOW (window), FALSE);
	g_return_val_if_fail (path != NULL, FALSE);

	/* dont allow a project to be opened twice */
	project = glade_app_get_project_by_path (path);	 
	if (project)
	{
		/* just switch to the project */	
		switch_to_project (window, project);
		return TRUE;
	}
	else
	{
		return open_project (window, path);
	}
}



static void
change_menu_label (GladeWindow *window,
					const gchar *path,
					const gchar *action_label,
					const gchar *action_description)
{
	GtkBin *bin;
	GtkLabel *label;
	gchar *text;
	gchar *tmp_text;

	g_assert (GLADE_IS_WINDOW (window));
	g_return_if_fail (path != NULL);
	g_return_if_fail (action_label != NULL);

	bin = GTK_BIN (gtk_ui_manager_get_widget (window->priv->ui, path));
	label = GTK_LABEL (gtk_bin_get_child (bin));

	if (action_description == NULL)
		text = g_strdup (action_label);
	else
	{
		tmp_text = escape_underscores (action_description, -1);
		text = g_strdup_printf ("%s: %s", action_label, tmp_text);		
		g_free (tmp_text);
	}
	
	gtk_label_set_text_with_mnemonic (label, text);

	g_free (text);
}

static void
refresh_undo_redo (GladeWindow *window)
{
	GladeCommand *undo = NULL, *redo = NULL;
	GladeProject *project;
	GtkAction    *action;
	gchar        *tooltip;

	project = glade_app_get_project ();

	if (project != NULL)
	{
		undo = glade_project_next_undo_item (project);
		redo = glade_project_next_redo_item (project);
	}

	/* Refresh Undo */
	action = gtk_action_group_get_action (window->priv->project_actions, "Undo");
	gtk_action_set_sensitive (action, undo != NULL);
	
	change_menu_label
		(window, "/MenuBar/EditMenu/Undo", _("_Undo"), undo ? undo->description : NULL);

	tooltip = g_strdup_printf (_("Undo: %s"), undo ? undo->description : _("the last action"));
	g_object_set (action, "tooltip", tooltip, NULL);
	g_free (tooltip);

	/* Refresh Redo */
	action = gtk_action_group_get_action (window->priv->project_actions, "Redo");
	gtk_action_set_sensitive (action, redo != NULL);

	change_menu_label
		(window, "/MenuBar/EditMenu/Redo", _("_Redo"), redo ? redo->description : NULL);

	tooltip = g_strdup_printf (_("Redo: %s"), redo ? redo->description : _("the last action"));
	g_object_set (action, "tooltip", tooltip, NULL);
	g_free (tooltip);

	/* Refresh menus */
	gtk_menu_tool_button_set_menu (GTK_MENU_TOOL_BUTTON (window->priv->undo), glade_project_undo_items (project));
	gtk_menu_tool_button_set_menu (GTK_MENU_TOOL_BUTTON (window->priv->redo), glade_project_redo_items (project));

}

static void
update_ui (GladeApp *app, GladeWindow *window)
{      
	if (window->priv->active_view)
		gtk_widget_queue_draw (GTK_WIDGET (window->priv->active_view));

	refresh_undo_redo (window);
}

static void
glade_window_dispose (GObject *object)
{
	GladeWindow *window = GLADE_WINDOW (object);
	
	if (window->priv->app)
	{
		g_object_unref (window->priv->app);
		window->priv->app = NULL;
	}

	G_OBJECT_CLASS (glade_window_parent_class)->dispose (object);
}

static void
glade_window_finalize (GObject *object)
{
	guint i;

	g_free (GLADE_WINDOW (object)->priv->default_path);

	for (i = 0; i < N_DOCKS; i++)
	{
		ToolDock *dock = &GLADE_WINDOW (object)->priv->docks[i];
		g_free (dock->title);
		g_free (dock->id);
	}

	G_OBJECT_CLASS (glade_window_parent_class)->finalize (object);
}


static gboolean
glade_window_configure_event (GtkWidget         *widget,
			      GdkEventConfigure *event)
{
	GladeWindow *window = GLADE_WINDOW (widget);
	gboolean retval;

	window->priv->position.width = event->width;
	window->priv->position.height = event->height;

	retval = GTK_WIDGET_CLASS(glade_window_parent_class)->configure_event (widget, event);

	gtk_window_get_position (GTK_WINDOW (widget),
				 &window->priv->position.x,
				 &window->priv->position.y);

	return retval;
}

static void
key_file_set_window_position (GKeyFile     *config,
			      GdkRectangle *position,
			      const char   *id,
			      gboolean      detached,
			      gboolean      save_detached)
{
	char *key_x, *key_y, *key_width, *key_height, *key_detached;

	key_x = g_strdup_printf ("%s-" CONFIG_KEY_X, id);
	key_y = g_strdup_printf ("%s-" CONFIG_KEY_Y, id);
	key_width = g_strdup_printf ("%s-" CONFIG_KEY_WIDTH, id);
	key_height = g_strdup_printf ("%s-" CONFIG_KEY_HEIGHT, id);
	key_detached = g_strdup_printf ("%s-" CONFIG_KEY_DETACHED, id);

	/* we do not want to save position of docks which
	 * were never detached */
	if (position->x > G_MININT)
		g_key_file_set_integer (config, CONFIG_GROUP_WINDOWS,
					key_x, position->x);
	if (position->y > G_MININT)
		g_key_file_set_integer (config, CONFIG_GROUP_WINDOWS,
					key_y, position->y);

	g_key_file_set_integer (config, CONFIG_GROUP_WINDOWS,
				key_width, position->width);
	g_key_file_set_integer (config, CONFIG_GROUP_WINDOWS,
				key_height, position->height);

	if (save_detached)
		g_key_file_set_boolean (config, CONFIG_GROUP_WINDOWS,
					key_detached, detached);

	g_free (key_detached);
	g_free (key_height);
	g_free (key_width);
	g_free (key_y);
	g_free (key_x);
}

static void
save_windows_config (GladeWindow *window, GKeyFile *config)
{
	guint i;

	for (i = 0; i < N_DOCKS; ++i)
	{
		ToolDock *dock = &window->priv->docks[i];
		key_file_set_window_position (config, &dock->window_pos, dock->id, 
					      dock->detached, TRUE);
	}

	key_file_set_window_position (config, &window->priv->position, 
				      "main", FALSE, FALSE);
}

static void 
save_paned_position (GKeyFile *config, GtkWidget *paned, const gchar *name)
{
	g_key_file_set_integer (config, name, "position", 
				gtk_paned_get_position (GTK_PANED (paned)));
}

static void
glade_window_config_save (GladeWindow *window)
{
	GKeyFile *config = glade_app_get_config ();
	
	save_windows_config (window, config);
	
	/* Save main window paned positions */
	save_paned_position (config, window->priv->center_pane, "center_pane");
	save_paned_position (config, window->priv->left_pane, "left_pane");
	save_paned_position (config, window->priv->right_pane, "right_pane");
	
	glade_app_config_save ();
}

static int
key_file_get_int (GKeyFile   *config,
		  const char *group,
		  const char *key,
		  int         default_value)
{
	if (g_key_file_has_key (config, group, key, NULL))
		return g_key_file_get_integer (config, group, key, NULL);
	else
		return default_value;
}

static void
key_file_get_window_position (GKeyFile     *config,
			      const char   *id,
			      GdkRectangle *pos,
			      gboolean     *detached)
{
	char *key_x, *key_y, *key_width, *key_height, *key_detached;

	key_x = g_strdup_printf ("%s-" CONFIG_KEY_X, id);
	key_y = g_strdup_printf ("%s-" CONFIG_KEY_Y, id);
	key_width = g_strdup_printf ("%s-" CONFIG_KEY_WIDTH, id);
	key_height = g_strdup_printf ("%s-" CONFIG_KEY_HEIGHT, id);
	key_detached = g_strdup_printf ("%s-" CONFIG_KEY_DETACHED, id);

	pos->x = key_file_get_int (config, CONFIG_GROUP_WINDOWS, key_x, pos->x);
	pos->y = key_file_get_int (config, CONFIG_GROUP_WINDOWS, key_y, pos->y);
	pos->width = key_file_get_int (config, CONFIG_GROUP_WINDOWS, key_width, pos->width);
	pos->height = key_file_get_int (config, CONFIG_GROUP_WINDOWS, key_height, pos->height);

	if (detached && g_key_file_has_key (config, CONFIG_GROUP_WINDOWS, key_detached, NULL))
		*detached = g_key_file_get_boolean (config, CONFIG_GROUP_WINDOWS, key_detached, NULL);

	g_free (key_x);
	g_free (key_y);
	g_free (key_width);
	g_free (key_height);
	g_free (key_detached);
}

static void
glade_window_set_initial_size (GladeWindow *window, GKeyFile *config)
{
	GdkRectangle position = {
		G_MININT, G_MININT, GLADE_WINDOW_DEFAULT_WIDTH, GLADE_WINDOW_DEFAULT_HEIGHT
	};

	key_file_get_window_position (config, "main", &position, NULL);

	gtk_window_set_default_size (GTK_WINDOW (window), position.width, position.height);

	if (position.x > G_MININT && position.y > G_MININT)
		gtk_window_move (GTK_WINDOW (window), position.x, position.y);
}

static void
load_paned_position (GKeyFile *config, GtkWidget *pane, const gchar *name, gint default_position)
{
	gtk_paned_set_position (GTK_PANED (pane),
				key_file_get_int (config, name, "position", default_position));
}

static void
glade_window_config_load (GladeWindow *window)
{
	GKeyFile *config = glade_app_get_config ();
	
	glade_window_set_initial_size (window, config);
	
	load_paned_position (config, window->priv->center_pane, "center_pane", 400);
	load_paned_position (config, window->priv->left_pane, "left_pane", 200);
	load_paned_position (config, window->priv->right_pane, "right_pane", 220);
}

static void
show_dock_first_time (GladeWindow    *window,
		      guint           dock_type,
		      const char     *action_id)
{
	GKeyFile *config;
	int detached = -1;
	GtkAction *action;
	ToolDock *dock;

	action = gtk_action_group_get_action (window->priv->static_actions, action_id);
	g_object_set_data (G_OBJECT (action), "glade-dock-type", GUINT_TO_POINTER (dock_type));

	dock = &window->priv->docks[dock_type];
	config = glade_app_get_config ();

	key_file_get_window_position (config, dock->id, &dock->window_pos, &detached);

	if (detached == 1)
		gtk_toggle_action_set_active (GTK_TOGGLE_ACTION (action), FALSE);
}

static void
setup_dock (ToolDock   *dock,
	    GtkWidget  *dock_widget,
	    guint       default_width,
	    guint       default_height,
	    const char *window_title,
	    const char *id,
	    GtkWidget  *paned,
	    gboolean    first_child)
{
	dock->widget = dock_widget;
	dock->window_pos.x = dock->window_pos.y = G_MININT;
	dock->window_pos.width = default_width;
	dock->window_pos.height = default_height;
	dock->title = g_strdup (window_title);
	dock->id = g_strdup (id);
	dock->paned = paned;
	dock->first_child = first_child;
	dock->detached = FALSE;
}

static gboolean
glade_window_save_and_execute(GladeSignalEditor *editor,
							  gchar* handler,
							  GladeWindow *window)
{
	GladeProject *project;
	gchar *project_path;

	save_cb (NULL, window);

	project = glade_design_view_get_project (window->priv->active_view);
	if (project)
	{
		project_path = glade_project_get_path (project);
		if (project_path)
		{
			gchar* command_line = g_strdup_printf("%s/bin/glade-code-generator \"%s\" \"%s\"", g_get_home_dir(), project_path, handler);
			g_spawn_command_line_async(command_line, NULL);
			g_free(command_line);
			return TRUE;
		}
	}
	return FALSE;
}

static void
glade_window_init (GladeWindow *window)
{
	GladeWindowPrivate *priv;

	GtkWidget *vbox;
	GtkWidget *hpaned1;
	GtkWidget *hpaned2;
	GtkWidget *vpaned;
	GtkWidget *menubar;
	GtkWidget *palette;
	GtkWidget *dockitem;
	GtkWidget *widget;
	GtkWidget *sep;
	GtkAction *undo_action, *redo_action;
	GtkAccelGroup *accel_group;	

	window->priv = priv = GLADE_WINDOW_GET_PRIVATE (window);
	
	priv->default_path = NULL;
	
	priv->app = glade_app_new ();

	vbox = gtk_vbox_new (FALSE, 0);
	gtk_container_add (GTK_CONTAINER (window), vbox);

	/* menubar */
	menubar = construct_menu (window);
	gtk_box_pack_start (GTK_BOX (vbox), menubar, FALSE, TRUE, 0);
	gtk_widget_show (menubar);

	/* toolbar */
	priv->toolbar = gtk_ui_manager_get_widget (priv->ui, "/ToolBar");
	gtk_box_pack_start (GTK_BOX (vbox), priv->toolbar, FALSE, TRUE, 0);
	gtk_widget_show (priv->toolbar);

	/* undo/redo buttons */
	priv->undo = gtk_menu_tool_button_new_from_stock (GTK_STOCK_UNDO);
	priv->redo = gtk_menu_tool_button_new_from_stock (GTK_STOCK_REDO);
	gtk_widget_show (GTK_WIDGET (priv->undo));
	gtk_widget_show (GTK_WIDGET (priv->redo));
	gtk_menu_tool_button_set_arrow_tooltip_text (GTK_MENU_TOOL_BUTTON (priv->undo),
						     _("Go back in undo history"));
	gtk_menu_tool_button_set_arrow_tooltip_text (GTK_MENU_TOOL_BUTTON (priv->redo),
						     _("Go forward in undo history"));

	sep = GTK_WIDGET (gtk_separator_tool_item_new ());
	gtk_widget_show (sep);
	gtk_toolbar_insert (GTK_TOOLBAR (priv->toolbar), GTK_TOOL_ITEM (sep), 3);
	gtk_toolbar_insert (GTK_TOOLBAR (priv->toolbar), GTK_TOOL_ITEM (priv->undo), 4);
	gtk_toolbar_insert (GTK_TOOLBAR (priv->toolbar), GTK_TOOL_ITEM (priv->redo), 5);

	undo_action = gtk_ui_manager_get_action (priv->ui, "/MenuBar/EditMenu/Undo");
	redo_action = gtk_ui_manager_get_action (priv->ui, "/MenuBar/EditMenu/Redo");
	
#if (GTK_MAJOR_VERSION == 2) && (GTK_MINOR_VERSION < 16)
	gtk_action_connect_proxy (undo_action, GTK_WIDGET (priv->undo));
	gtk_action_connect_proxy (redo_action, GTK_WIDGET (priv->redo));
#else
	gtk_activatable_set_related_action (GTK_ACTIVATABLE (priv->undo), undo_action);
	gtk_activatable_set_related_action (GTK_ACTIVATABLE (priv->redo), redo_action);
#endif
	
	/* main contents */
	hpaned1 = gtk_hpaned_new ();
	hpaned2 = gtk_hpaned_new ();
	vpaned = gtk_vpaned_new ();
	priv->center_pane = hpaned1;
	priv->left_pane = hpaned2;
	priv->right_pane = vpaned;
	
	gtk_container_set_border_width (GTK_CONTAINER (hpaned1), 2);

	gtk_box_pack_start (GTK_BOX (vbox), hpaned1, TRUE, TRUE, 0);
	gtk_paned_pack1 (GTK_PANED (hpaned1), hpaned2, TRUE, FALSE);
	gtk_paned_pack2 (GTK_PANED (hpaned1), vpaned, FALSE, FALSE);

	/* divider position between tree and editor */	
	gtk_paned_set_position (GTK_PANED (vpaned), 150);

	gtk_widget_show_all (hpaned1);
	gtk_widget_show_all (hpaned2);
	gtk_widget_show_all (vpaned);

	/* notebook */
	priv->notebook = gtk_notebook_new ();
	gtk_notebook_set_show_tabs (GTK_NOTEBOOK (priv->notebook), FALSE);
	gtk_notebook_set_show_border (GTK_NOTEBOOK (priv->notebook), FALSE);
	gtk_paned_pack2 (GTK_PANED (hpaned2), priv->notebook, TRUE, FALSE);
	gtk_widget_show (priv->notebook);

	/* palette */
	palette = GTK_WIDGET (glade_app_get_palette ());
	glade_palette_set_show_selector_button (GLADE_PALETTE (palette), FALSE);
	gtk_paned_pack1 (GTK_PANED (hpaned2), palette, FALSE, FALSE);
	setup_dock (&priv->docks[DOCK_PALETTE], palette, 200, 540, 
		    _("Palette"), "palette", hpaned2, TRUE);
	gtk_widget_show (palette);

	/* inspectors */
	priv->inspectors_notebook = gtk_notebook_new ();	
	gtk_notebook_set_show_tabs (GTK_NOTEBOOK (priv->inspectors_notebook), FALSE);
	gtk_notebook_set_show_border (GTK_NOTEBOOK (priv->inspectors_notebook), FALSE);	
	gtk_widget_show (priv->inspectors_notebook);	
	gtk_paned_pack1 (GTK_PANED (vpaned), priv->inspectors_notebook, FALSE, FALSE); 
	setup_dock (&priv->docks[DOCK_INSPECTOR], priv->inspectors_notebook, 300, 540,
		    _("Inspector"), "inspector", vpaned, TRUE);

	/* editor */
	dockitem = GTK_WIDGET (glade_app_get_editor ());
	gtk_paned_pack2 (GTK_PANED (vpaned), dockitem, TRUE, FALSE);
	gtk_widget_show_all (dockitem);	
	setup_dock (&priv->docks[DOCK_EDITOR], dockitem, 500, 700,
		    _("Properties"), "properties", vpaned, FALSE);

	show_dock_first_time (window, DOCK_PALETTE, "DockPalette");
	show_dock_first_time (window, DOCK_INSPECTOR, "DockInspector");
	show_dock_first_time (window, DOCK_EDITOR, "DockEditor");

	/* signal editor */
	g_signal_connect (G_OBJECT (glade_app_get_editor()->signal_editor),
	                  "handler-editing-started",
	                  G_CALLBACK (glade_signal_editor_handler_editing_started_default_impl),
	                  NULL);
	g_signal_connect (G_OBJECT (glade_app_get_editor()->signal_editor),
	                  "userdata-editing-started",
	                  G_CALLBACK (glade_signal_editor_userdata_editing_started_default_impl),
	                  NULL);

	g_signal_connect (G_OBJECT (glade_app_get_editor()->signal_editor),
	                  "save-and-execute-clicked",
	                  G_CALLBACK (glade_window_save_and_execute),
	                  window);

	/* status bar */
	priv->statusbar = gtk_statusbar_new ();
	priv->statusbar_menu_context_id = gtk_statusbar_get_context_id (GTK_STATUSBAR (priv->statusbar),
										"menu");
	priv->statusbar_actions_context_id = gtk_statusbar_get_context_id (GTK_STATUSBAR (priv->statusbar),
										   "actions");	
	gtk_box_pack_end (GTK_BOX (vbox), priv->statusbar, FALSE, TRUE, 0);
	gtk_widget_show (priv->statusbar);


	gtk_widget_show (vbox);
	
	/* recent files */	
	priv->recent_manager = gtk_recent_manager_get_default ();

	priv->recent_menu = create_recent_chooser_menu (window, priv->recent_manager);

	g_signal_connect (priv->recent_menu,
			  "item-activated",
			  G_CALLBACK (recent_chooser_item_activated_cb),
			  window);
			  
	widget = gtk_ui_manager_get_widget (priv->ui, "/MenuBar/FileMenu/OpenRecent");
	gtk_menu_item_set_submenu (GTK_MENU_ITEM (widget), priv->recent_menu);		  
	
	/* palette selector & drag/resize buttons */
	sep = GTK_WIDGET (gtk_separator_tool_item_new());
	gtk_widget_show (GTK_WIDGET (sep));
	gtk_toolbar_insert (GTK_TOOLBAR (priv->toolbar), GTK_TOOL_ITEM (sep), -1);

	priv->selector_button = 
		GTK_TOGGLE_TOOL_BUTTON (create_selector_tool_button (GTK_TOOLBAR (priv->toolbar)));	
	gtk_toolbar_insert (GTK_TOOLBAR (priv->toolbar), 
			    GTK_TOOL_ITEM (priv->selector_button), -1);

	priv->drag_resize_button = 
		GTK_TOGGLE_TOOL_BUTTON (create_drag_resize_tool_button 
					(GTK_TOOLBAR (priv->toolbar)));	
	gtk_toolbar_insert (GTK_TOOLBAR (priv->toolbar), 
			    GTK_TOOL_ITEM (priv->drag_resize_button), -1);
	
	gtk_toggle_tool_button_set_active (priv->selector_button, TRUE);
	gtk_toggle_tool_button_set_active (priv->drag_resize_button, FALSE);

	g_signal_connect (G_OBJECT (priv->selector_button), "toggled",
			  G_CALLBACK (on_selector_button_toggled), window);
	g_signal_connect (G_OBJECT (priv->drag_resize_button), "toggled",
			  G_CALLBACK (on_drag_resize_button_toggled), window);
	g_signal_connect (G_OBJECT (glade_app_get()), "notify::pointer-mode",
			  G_CALLBACK (on_pointer_mode_changed), window);
	
	
	/* support for opening a file by dragging onto the project window */
	gtk_drag_dest_set (GTK_WIDGET (window),
			   GTK_DEST_DEFAULT_ALL,
			   drop_types, G_N_ELEMENTS (drop_types),
			   GDK_ACTION_COPY | GDK_ACTION_MOVE);

	g_signal_connect (G_OBJECT (window), "drag-data-received",
			  G_CALLBACK (drag_data_received), window);

	g_signal_connect (G_OBJECT (window), "delete_event",
			  G_CALLBACK (delete_event), window);
			  
			  
	/* GtkNotebook signals  */
	g_signal_connect (priv->notebook,
			  "switch-page",
			  G_CALLBACK (notebook_switch_page_cb),
			  window);
	g_signal_connect (priv->notebook,
			  "page-added",
			  G_CALLBACK (notebook_tab_added_cb),
			  window);
	g_signal_connect (priv->notebook,
			  "page-removed",
			  G_CALLBACK (notebook_tab_removed_cb),
			  window);
			  
	/* GtkWindow events */
	g_signal_connect (window, "window-state-event",
			  G_CALLBACK (window_state_event_cb),
			  window);

	g_signal_connect (G_OBJECT (window), "key-press-event",
			  G_CALLBACK (glade_utils_hijack_key_press), window);

       /* GladeApp signals */
	g_signal_connect (G_OBJECT (priv->app), "update-ui",
			  G_CALLBACK (update_ui),
			  window);

	/* Clipboard signals */
	g_signal_connect (G_OBJECT (glade_app_get_clipboard ()), "notify::has-selection",
			  G_CALLBACK (clipboard_notify_handler_cb),
			  window);

	
	gtk_about_dialog_set_url_hook ((GtkAboutDialogActivateLinkFunc) about_dialog_activate_link_func, window, NULL);

	glade_app_set_window (GTK_WIDGET (window));

	accel_group = gtk_ui_manager_get_accel_group(priv->ui);

	gtk_window_add_accel_group (GTK_WINDOW (glade_app_get_clipboard_view ()), accel_group);
	
	/* Load widget state */
	glade_window_config_load (window);

#ifdef MAC_INTEGRATION
	{
		/* Fix up the menubar for MacOSX Quartz builds */
		gtk_widget_hide (menubar);
		ige_mac_menu_set_menu_bar (GTK_MENU_SHELL (menubar));
		
		widget = gtk_ui_manager_get_widget (window->priv->ui, "/MenuBar/FileMenu/Quit");
		ige_mac_menu_set_quit_menu_item (GTK_MENU_ITEM (widget));
	}
#endif


}

static void
glade_window_class_init (GladeWindowClass *klass)
{
	GObjectClass *object_class;
	GtkWidgetClass *widget_class;

	object_class = G_OBJECT_CLASS (klass);
	widget_class = GTK_WIDGET_CLASS (klass);

	object_class->dispose  = glade_window_dispose;
	object_class->finalize = glade_window_finalize;

	widget_class->configure_event = glade_window_configure_event;

	g_type_class_add_private (klass, sizeof (GladeWindowPrivate));
}


GtkWidget *
glade_window_new (void)
{
	return g_object_new (GLADE_TYPE_WINDOW, NULL);
}

void
glade_window_check_devhelp (GladeWindow *window)
{
	g_return_if_fail (GLADE_IS_WINDOW (window));
	
	if (glade_util_have_devhelp ())
	{
		GladeEditor *editor = glade_app_get_editor ();
		glade_editor_show_info (editor);
		
		g_signal_handlers_disconnect_by_func (editor, doc_search_cb, window);
		
		g_signal_connect (editor, "gtk-doc-search",
				  G_CALLBACK (doc_search_cb), window);
		
	}
}

