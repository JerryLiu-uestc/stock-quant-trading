import tkinter as tk

def click(button_text):
    if button_text == "=":
        try:
            result = eval(entry.get())
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(result))
        except:
            entry.delete(0, tk.END)
            entry.insert(tk.END, "错误")
    elif button_text == "C":
        entry.delete(0, tk.END)
    else:
        entry.insert(tk.END, button_text)

root = tk.Tk()
root.title("计算器")
root.resizable(False, False)

entry = tk.Entry(root, width=20, font=("Arial", 20), justify="right")
entry.grid(row=0, column=0, columnspan=4)

buttons = [
    '7','8','9','/',
    '4','5','6','*',
    '1','2','3','-',
    'C','0','=','+'
]

row = 1
col = 0
for btn in buttons:
    tk.Button(
        root, text=btn, width=5, height=2,
        font=("Arial", 14),
        command=lambda b=btn: click(b)
    ).grid(row=row, column=col)
    col += 1
    if col > 3:
        col = 0
        row += 1

root.mainloop()