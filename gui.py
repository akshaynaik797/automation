from tkinter import Tk, Label, Entry, StringVar, Button, ttk, messagebox


my_date = ''
mygui = Tk(className='Automation')
mygui.geometry("900x200")


mssno = StringVar()
mssno_label = Label(mygui, text="MSS NO", width=10).grid(row=1, column=0)
mssno_entry = Entry(mygui, textvariable=mssno).grid(row=1, column=1, pady=15)
# mssno.set("01/08/2020 00:00:01")

hosp_id = StringVar()
hosp_id_label = Label(mygui, text="Hospital ID", width=10).grid(row=1, column=2)
hosp_id_entry = Entry(mygui, textvariable=hosp_id).grid(row=1, column=3)
# hosp_id.set("01/09/2020 00:00:01")


def process_values(*args):
    pass


def send_values():
    if mssno.get() != '' and hosp_id.get() != '':
        result = process_values(mssno.get(), hosp_id.get())
        if result is True:
            print('Report generated')
            messagebox.showinfo(title='Success', message='Report generated')
        else:
            messagebox.showerror(title='Error', message='Job failed, see logs')
    else:
        messagebox.showerror(title="Error", message='Enter values in all fields')

loginButton = Button(mygui, text="Process", command=send_values).grid(row=2, column=1)
closeButton = Button(mygui, text="Close", command=mygui.destroy).grid(row=2, column=2)
mygui.mainloop()
