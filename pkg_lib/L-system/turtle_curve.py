'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 10.03.2021
'''
import turtle
import numpy as np
import tkinter as Tkinter
import time


root = Tkinter.Tk()
START_WIDTH = 1920
START_HEIGHT = 1080

frame = Tkinter.Frame(root, width=START_WIDTH, height=START_HEIGHT)
frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

xscrollbar = Tkinter.Scrollbar(frame, orient=Tkinter.HORIZONTAL)
xscrollbar.grid(row=1, column=0, sticky=Tkinter.E+Tkinter.W)

yscrollbar = Tkinter.Scrollbar(frame, orient=Tkinter.VERTICAL)
yscrollbar.grid(row=0, column=1, sticky=Tkinter.N+Tkinter.S)

canvas = Tkinter.Canvas(frame, width=START_WIDTH, height=START_HEIGHT,
                        scrollregion=(0, 0, START_WIDTH, START_HEIGHT),
                        xscrollcommand=xscrollbar.set,
                        yscrollcommand=yscrollbar.set)

canvas.grid(row=0, column=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)

xscrollbar.config(command=canvas.xview)
yscrollbar.config(command=canvas.yview)

frame.pack()
# canvas.pack()
s = turtle.TurtleScreen(canvas)
turt = turtle.RawTurtle(canvas)



axiom = "F"
axiom_tmp = ""

n = 4
length = 2
angle = 45

turt.speed(0)
turt.shape("turtle")
# drawing_area = turt.Screen()
# color = np.array([255, 245, 219])/255
# drawing_area.bgcolor(*color)
# drawing_area.setup(width=1920, height=1080, startx=1920/4, starty=1080/2)
turt.penup()
turt.setpos((-1920/2+10, -1080/2+10))
turt.pendown()

for a in range(n):
    for i in axiom:
        if i == "F":
            axiom_tmp += "F+F-F-F+F"
        else:
            # + or -
            axiom_tmp += i
    axiom = axiom_tmp
    axiom_tmp = ""

# turt._tracer(0, 0)
for i in axiom:
    if i == "F":
        turt.forward(length)
    elif i == "+":
        turt.left(angle)
    elif i == "-":
        turt.right(angle)
    canvas.config(scrollregion=canvas.bbox(Tkinter.ALL))
# turt._update()

turt.hideturtle()
s.mainloop()
# time.sleep(3)

# while True:
#     time.sleep(1)

if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
