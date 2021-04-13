'''
* Created by Zhenia Syryanyy (Yevgen Syryanyy)
* e-mail: yuginboy@gmail.com
* Last modified: 10.03.2021
'''
import turtle
import numpy as np
import tkinter as Tkinter
import time
from random  import randint


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



axiom = "0"
axiom_tmp = ""

itarations = 8
length = 2
angle = 35
deviation = 35

turt.speed(0)
turt.shape("turtle")
# drawing_area = turt.Screen()
# color = np.array([255, 245, 219])/255
# drawing_area.bgcolor(*color)
# drawing_area.setup(width=1920, height=1080, startx=1920/4, starty=1080/2)
turt.penup()
turt.setheading(90)
turt.setpos((-1920/4+10, -1080/2+10))
turt.setpos((0, -1080/2+10))
turt.pendown()

for a in range(itarations):
    for i in axiom:
        if i == "0":
            axiom_tmp += "1[0]0"
        elif i == "1":
            axiom_tmp += '11'
        else:
            axiom_tmp += i
    axiom = axiom_tmp
    axiom_tmp = ""

stack = []
s.tracer(0)
# turt._tracer(0, 0)
print(axiom)
for i in axiom:
    eps = randint(-deviation, deviation)
    if i == "1":
        turt.forward(length)
    elif i == "0":
        turt.forward(length)
    elif i == "[":
        stack.append(turt.heading())
        stack.append(turt.ycor())
        stack.append(turt.xcor())

        turt.right(angle + eps)
    elif i == "]":
        turt.penup()
        turt.setx(stack.pop())
        turt.sety(stack.pop())
        turt.setheading(stack.pop())
        turt.left(angle + eps)
        turt.pendown()
    canvas.config(scrollregion=canvas.bbox(Tkinter.ALL))
# turt._update()

turt.hideturtle()
s.update()
s.mainloop()
# time.sleep(3)

# while True:
#     time.sleep(1)

if __name__ == '__main__':
    print('-> you run ', __file__, ' file in the main mode (Top-level script environment)')
