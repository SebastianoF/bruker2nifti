import os

try:
    # for Python2
    import Tkinter as tk
    import tkFileDialog
except ImportError:
    # for Python3
    import tkinter as tk
    from tkinter import filedialog as tkFileDialog

import webbrowser

from bruker2nifti.converter import Bruker2Nifti
from bruker2nifti.__init__ import __version__ as version


class BrukerToNiftiGUI(tk.Tk, object):
    """
    Graphical user interface class to access Bruker to Nifti converter.
    """
    def __init__(self, in_pfo_input=None, in_pfo_output=None, in_study_name=None):

        super(BrukerToNiftiGUI, self).__init__()

        # Window settings:

        self.title('From bruker to nifti - interface - version {}'.format(version))
        self.geometry('715x180')

        # Widgets:

        self.header = tk.Label(self, text=' Bruker 2 nifti Converter ', font="Verdana 14")

        self.label_pfo_input = tk.Label(self, text='Folder path input')
        self.entry_pfo_input = tk.Entry(self, bd=2, width=50)

        if in_pfo_input is not None:
            self.entry_pfo_input.insert(0, in_pfo_input)

        self.label_pfo_output = tk.Label(self, text='Folder path output')
        self.entry_pfo_output = tk.Entry(self, bd=2, width=50)

        if in_pfo_output is not None:
            self.entry_pfo_output.insert(0, in_pfo_output)

        self.label_study_name = tk.Label(self, text='Study name (optional)')
        self.entry_study_name = tk.Entry(self, bd=2, width=50)

        if in_study_name is not None:
            self.entry_study_name.insert(0, in_study_name)

        self.CheckVar_cs = tk.IntVar(value=1)  # correct slope default True
        self.CheckVar_ac = tk.IntVar(value=0)  # get acquisition parameters default False
        self.CheckVar_me = tk.IntVar(value=0)  # get method default False
        self.CheckVar_rc = tk.IntVar(value=0)  # get reco default False

        self.radio_button_correct_slope = tk.Checkbutton(self, text='correct slope', variable=self.CheckVar_cs)
        self.radio_button_get_acqp      = tk.Checkbutton(self, text='get acqp', variable=self.CheckVar_ac)
        self.radio_button_get_method    = tk.Checkbutton(self, text='get method', variable=self.CheckVar_me)
        self.radio_button_get_reco      = tk.Checkbutton(self, text='get reco', variable=self.CheckVar_rc)

        self.button_browse_input = tk.Button(self, text='Browse', command=self.button_browse_callback_pfo_input)
        self.button_browse_output = tk.Button(self, text='Browse', command=self.button_browse_callback_pfo_output)
        self.button_help = tk.Button(self, text='?', command=self.open_help, fg='blue', font="times 14 bold")
        self.button_convert = tk.Button(self, text='Convert', command=self.convert, highlightbackground="#1291E9")

        self.label_option_menu = tk.Label(self, text='Output NifTi version:', compound='right')
        self.option_menu_value = tk.StringVar(self)
        self.option_menu_value.set('1')
        self.option_menu = tk.OptionMenu(self, self.option_menu_value, '1', '2')

        # geometry

        self.header.grid(row=0, column=1, columnspan=3)

        self.label_pfo_input.grid(row=1, column=0)
        self.entry_pfo_input.grid(row=1, column=1, columnspan=3)
        self.button_browse_input.grid(row=1, column=4)

        self.label_pfo_output.grid(row=2, column=0)
        self.entry_pfo_output.grid(row=2, column=1, columnspan=3)
        self.button_browse_output.grid(row=2, column=4)

        self.label_study_name.grid(row=3, column=0)
        self.entry_study_name.grid(row=3, column=1, columnspan=3)

        self.radio_button_correct_slope.grid(row=4, column=0)
        self.radio_button_get_acqp.grid(row=4, column=1)
        self.radio_button_get_method.grid(row=4, column=2)
        self.radio_button_get_reco.grid(row=4, column=3)

        self.button_convert.grid(row=5, column=4)
        # self.button_help.place(relx=.941, rely=.001)
        self.button_help.grid(row=0, column=4)

        self.label_option_menu.grid(row=5, column=0)
        self.option_menu.grid(row=5, column=1)

    # main commands

    def button_browse_callback_pfo_input(self):
        filename = tkFileDialog.askdirectory()
        filename = os.path.abspath(filename)
        self.entry_pfo_input.delete(0, tk.END)
        self.entry_pfo_input.insert(0, filename)

    def button_browse_callback_pfo_output(self):
        filename = tkFileDialog.askdirectory()
        filename = os.path.abspath(filename)
        self.entry_pfo_output.delete(0, tk.END)
        self.entry_pfo_output.insert(0, filename)

    @staticmethod
    def open_help():
        webbrowser.open('https://github.com/SebastianoF/bruker2nifti/wiki/Graphical-User-Interface-Examples')

    def convert(self):

        print(' --- GUI bruker2nifti --- ')
        print('Input path: {}'.format(self.entry_pfo_input.get()))
        print('Output path: {}'.format(self.entry_pfo_output.get()))
        print('Study name: {}'.format(self.entry_study_name.get()))

        print('Correct slope : {}'.format(self.CheckVar_cs.get()))
        print('Get acpq      : {}'.format(self.CheckVar_ac.get()))
        print('get method    : {}'.format(self.CheckVar_me.get()))
        print('get reco      : {}'.format(self.CheckVar_rc.get()))
        print('get NifTi-    : {}'.format(self.option_menu_value.get()))

        bru = Bruker2Nifti(self.entry_pfo_input.get(),
                           self.entry_pfo_output.get(),
                           study_name=self.entry_study_name.get())

        bru.correct_slope = self.CheckVar_cs.get()
        bru.get_acqp = self.CheckVar_ac.get()
        bru.get_method = self.CheckVar_me.get()
        bru.get_reco = self.CheckVar_rc.get()
        bru.nifti_version = int(self.option_menu_value.get())

        bru.convert()

        del bru

        print('\nbruker2Nifti verision {} - Have a nice day!'.format(version))


def open_gui(in_pfo_input=None, in_pfo_output=None, in_study_name=None):
    """
    To open the Graphical user interface accessing Bruker2Nifti converter.
    :param in_pfo_input: [None] input path to folder (pfo) where the bruker folder structure is located.
    It that will initialise the corresponding field entry on the GUI.
    :param in_pfo_output: [None] input path to folder (pfo) where the corresponding folder structure with nifti images
    and selected parameter files will be located.
    :param in_study_name: [None] to initialise the optional study name field.
    :return: Will open the gui.
    """
    root = BrukerToNiftiGUI(in_pfo_input=in_pfo_input, in_pfo_output=in_pfo_output, in_study_name=in_study_name)
    root.mainloop()


if __name__ == '__main__':
    open_gui()
