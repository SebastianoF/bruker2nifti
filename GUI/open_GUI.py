import Tkinter as tk
from bruker2nifti.study_converter import convert_a_study

'''
No drag and drop on mac: 
we suggest
http://osxdaily.com/2013/06/19/copy-file-folder-path-mac-os-x/
And follow
https://www.podfeet.com/blog/tutorials-5/automator-shortcut-tutorial/
'''


class BrukerToNifti(tk.Tk, object):
    def __init__(self):
        super(BrukerToNifti, self).__init__()

        # Window settings:

        self.title('From bruker to nifti - interface')
        self.geometry('450x150')

        # Widgets:

        self.label_pfo_input = tk.Label(self, text='Folder path input')
        self.entry_pfo_input = tk.Entry(self, bd=2)

        self.label_pfo_output = tk.Label(self, text='Folder path output')
        self.entry_pfo_output = tk.Entry(self, bd=2)

        self.label_study_name = tk.Label(self, text='Study name (optional)')
        self.entry_study_name = tk.Entry(self, bd=2)

        self.CheckVar_cs = tk.IntVar(value=1)  # correct slope default True
        self.CheckVar_ac = tk.IntVar(value=0)  # get acquisition parameters default False
        self.CheckVar_me = tk.IntVar(value=0)  # get method default False
        self.CheckVar_rc = tk.IntVar(value=0)  # get reco default False

        self.radio_button_correct_slope = tk.Checkbutton(self, text='correct slope', variable=self.CheckVar_cs)
        self.radio_button_get_acqp      = tk.Checkbutton(self, text='get acqp', variable=self.CheckVar_ac)
        self.radio_button_get_method    = tk.Checkbutton(self, text='get method', variable=self.CheckVar_me)
        self.radio_button_get_reco      = tk.Checkbutton(self, text='get reco', variable=self.CheckVar_rc)

        self.button_convert = tk.Button(self, text='Convert', command=self.convert)

        # geometry

        self.label_pfo_input.grid(row=0, column=0)
        self.entry_pfo_input.grid(row=0, column=1, columnspan=3)

        self.label_pfo_output.grid(row=1, column=0)
        self.entry_pfo_output.grid(row=1, column=1, columnspan=3)

        self.label_study_name.grid(row=2, column=0)
        self.entry_study_name.grid(row=2, column=1, columnspan=3)

        self.radio_button_correct_slope.grid(row=3, column=0)
        self.radio_button_get_acqp.grid(row=3, column=1)
        self.radio_button_get_method.grid(row=3, column=2)
        self.radio_button_get_reco.grid(row=3, column=3)

        self.button_convert.grid(row=4, column=2, columnspan=2)

    # main command
    def convert(self):

        print 'GUI bruker2nifti'
        print('Input path: {}'.format(self.entry_pfo_input.get()))
        print('Output path: {}'.format(self.entry_pfo_output.get()))
        print('Study name: {}'.format(self.entry_study_name.get()))

        print('Correct slope : {}'.format(self.CheckVar_cs.get()))
        print('Get acpq      : {}'.format(self.CheckVar_ac.get()))
        print('get method    : {}'.format(self.CheckVar_me.get()))
        print('get reco      : {}'.format(self.CheckVar_rc.get()))

        convert_a_study(self.entry_pfo_input.get(),
                        self.entry_pfo_output.get(),
                        study_name=self.entry_study_name.get(),
                        correct_slope=self.CheckVar_cs.get(),
                        get_acqp=self.CheckVar_ac.get(),
                        get_method=self.CheckVar_me.get(),
                        get_reco=self.CheckVar_rc.get())


if __name__ == '__main__':
    root = BrukerToNifti()
    root.mainloop()
