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

axiom = "22220110"
axiom_tmp = ""
rules = {"0": "1[0]0", "1": "21"}
itarations = 15
length = 10
angle = 20
deviation = 5
thick = 15
tree_level = 1

turt.speed(0)
s.tracer(0)
s.delay(0)
# turt._tracer(0)
# turt.shape("turtle")
# drawing_area = turt.Screen()
# color = np.array([255, 245, 219])/255
# drawing_area.bgcolor(*color)
# drawing_area.setup(width=1920, height=1080, startx=1920/4, starty=1080/2)
turt.penup()
turt.setheading(90)
# turt.setpos((-1920/4+10, -1080/2+10))
turt.setpos((0, -1080/2+10))
turt.pendown()
turt.pensize(thick)

for a in range(itarations):
    for i in axiom:
        rand = randint(1, 10)
        if i == "0":
            if rand < 6:
                axiom_tmp += '1[-20][+20]'
            elif rand == 6:
                axiom_tmp += '1[-0][+0]'
                # tree_level += 1
            elif rand == 7:
                axiom_tmp += '1[-2][+2]'
            elif rand == 8:
                axiom_tmp += '[-20]22[+20]'
            elif rand == 9:
                axiom_tmp += ']0[2]2['
            elif rand == 10:
                axiom_tmp += '2'
                # tree_level -= 1
        elif i == "1":
            axiom_tmp += '21'
        elif i == "2":
            if randint(1, 10) <= 1 and tree_level > 2:
                axiom_tmp += '3[^30]'
            else:
                axiom_tmp += "2"
        elif i == "[":
            axiom_tmp += i
            tree_level += 1
        elif i == "]":
            axiom_tmp += i
            tree_level -= 1

        # if i in rules:
        #     axiom_tmp += rules[i]
        else:
            axiom_tmp += i
    axiom = axiom_tmp
    axiom_tmp = ""

stack = []

# turt._tracer(0, 0)
print(axiom)
for i in axiom:
    eps = randint(-deviation, deviation)
    turt.pencolor("#543700")
    if i == "0":
        # leaf
        rand = randint(0, 9)
        if rand < 2:
            turt.pencolor("#3cff00")
        elif (rand >= 2) and (rand < 6):
            turt.pencolor("#26a300")
        else:
            turt.pencolor("#145400")
        turt.pensize(3)
        turt.forward(length)
    elif i == "1":
        turt.forward(length)
    elif i == "2":
        if randint(0, 9) < 6:
            turt.forward(length)

    elif i == "3":
        if randint(0, 9) < 6:
            turt.forward(length)

    elif i == "[":

        stack.append(thick)
        stack.append(turt.heading())
        stack.append(turt.ycor())
        stack.append(turt.xcor())
        thick *= 0.75
        turt.pensize(thick)
        turt.right(angle + eps)
    elif i == "]":
        turt.penup()
        turt.setx(stack.pop())
        turt.sety(stack.pop())
        turt.setheading(stack.pop())
        turt.pensize(stack.pop())
        turt.left(angle + eps)
        turt.pendown()

    elif i == "-":
        turt.left(angle + eps)
    elif i == "+":
        turt.right(angle + eps)
    elif i == "^":
        rand = randint(-30, 30)
        if rand < 0:
            turt.right(rand - deviation)
        else:
            turt.right(rand + eps)
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
