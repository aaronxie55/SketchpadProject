# import
import copy
import os
import pickle
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename

#global vars
# -------------------------------------------------------------------------
current_x, current_y = 0, 0
color = "black"
shape = "free"
action = "draw"
free = True
fill = True
coord = []
temp_shape = -1
id_shape = -1
shapeSet = ["free", "line", "square", "rectangle",
            "circle", "ellipse", "open polygons", "closed polygons"]
colorSet = ["black", "gray", "red", "orange", "yellow", "green",
            "cyan", "blue", "purple", "magenta", "white", ]
toolSet = ["fill", "outline"]
actionSet = ["draw", "move", "cut", "copy", "paste", "group", "ungroup"]
saved_info = []
group_info = []
group_list = []
step_list = []
counter = {"free": 0, "line": 0, "square": 0, "rectangle": 0, "circle": 0,
           "ellipse": 0, "openpolygon": 0, "closedpolygon": 0, "group": 0}


# def function
# ----------------------------------------------------------------------------
# def new color
def chose_color(new_color):
    global color
    color = new_color
    print("Color: "+color)


# new sketch
def new_sketch():
    global group_info, group_list, counter, step_list
    counter = {"free": 0, "line": 0, "square": 0, "rectangle": 0, "circle": 0,
               "ellipse": 0, "openpolygon": 0, "closedpolygon": 0, "group": 0}
    group_info = []
    group_list = []
    step_list = []
    canvas.delete('all')


# def new shape
def chose_shape(new_shape):
    global shape, free
    if new_shape != "free":
        free = False
    else:
        free = True
    shape = new_shape
    print("Shape: " + shape)
    print("Free mode: {}".format(free))


# def new tool
def chose_tool(new_tool):
    global fill
    if new_tool == "fill":
        fill = True
    elif new_tool == "outline":
        fill = False
    print("Fill: {}".format(fill))


# def new action
def chose_action(new_action):
    global action
    action = new_action
    # Mode notice
    canvas.delete("action_mode")
    canvas.create_text(100, 10, text="Mode: " +
                       action, tags="action_mode")
    print("Action: " + action)


# def size functino for square and circle
def max_size(e):
    global current_x, current_y
    dx, dy = e.x - current_x, e.y - current_y
    signx = 1 if dx >= 0 else -1
    signy = 1 if dy >= 0 else -1
    size = max(abs(dx), abs(dy))
    new_x = current_x + size*signx
    new_y = current_y + size*signy
    return new_x, new_y


# def lamada function for menu bar
def shape_lambda(var):
    return lambda: chose_shape(var)


def color_lambda(var):
    return lambda: chose_color(var)


def tool_lambda(var):
    return lambda: chose_tool(var)


def action_lambda(var):
    return lambda: chose_action(var)


# def delete temp shape
def del_temp(var):
    if var != -1:
        canvas.delete(var)


# def get tag with closest to mouse left click
def identify(e):
    closest = canvas.find_closest(e.x, e.y)[0]
    tags = canvas.gettags(closest)
    print(tags)
    return tags


# def group shape
def group_shapes(e):
    global counter, group_list
    counter["group"] = counter["group"] + 1
    group_tag = []
    for i in group_info:
        canvas.itemconfig(
            i[0], tags=("group_"+str(counter["group"]), canvas.gettags(i)))
        group_tag.append(i[0])
    group_list.append(("group_"+str(counter["group"]), group_tag))
    print(group_list)
    print("Group created: group_"+str(counter["group"]))


# def ungroup shape
def ungroup_shapes(e):
    global id_shape, group_list
    print("id_shape[0]:" + id_shape[0])
    print("group_list[0]:" + group_list[0][0])
    print(str(group_list[0][1][0]))
    print("find_withtag: "+str(canvas.find_withtag(id_shape[0])))
    j = int(id_shape[0][6:]) - 1
    print("j: " + str(j))
    k = 0

    if id_shape[0][:5] == ("group"):

        for i in canvas.find_withtag(id_shape[0]):

            canvas.itemconfig(i, tags=group_list[j][1][k])
            k += 1

        print("Group ungrouped: "+id_shape[0])
    else:
        print("Not group")


# set new tag while copy
def set_new_tag(tag):
    global counter
    tag_type, suffix = tag.split('_')
    counter[tag_type] = counter[tag_type]+1
    new_tag = tag_type+"_"+str(counter[tag_type])
    return new_tag


# def save function
def save():
    save_info = {}
    save_info["counter"] = counter
    save_info["objects"] = []

    shapes = canvas.find_all()
    for current_shapes in shapes:
        tags_list = canvas.itemcget(current_shapes, "tags").split(" ")
        shape_info = {}
        shape_info["options"] = {}
        shape_info["type"] = canvas.type(current_shapes)
        #shape_info["options"]["outline"] = canvas.itemcget(id, "outline")
        shape_info["options"]["fill"] = canvas.itemcget(current_shapes, "fill")
        shape_info["options"]["tags"] = tags_list
        shape_info["coords"] = canvas.coords(current_shapes)
        save_info["objects"].append(shape_info)

    file_name = asksaveasfilename()
    if file_name == '':
        print("No file name input")
        return
    with open(file_name, 'wb') as data_info:
        pickle.dump(save_info, data_info)


# def load funciton
def load():
    func_list = {
        "line": getattr(canvas, "create_line"),
        "rectangle": getattr(canvas, "create_rectangle"),
        "oval": getattr(canvas, "create_oval"),
        "polygon": getattr(canvas, "create_polygon"),
    }
    file_name = askopenfilename()
    if file_name == '':
        print("No file_name input, no loading")
    if os.path.isfile(file_name):
        with open(file_name, 'rb') as data_info:
            save_info = pickle.load(data_info)
    new_sketch()
    counter = save_info["counter"]
    for shape in save_info["objects"]:
        func_list[shape["type"]](shape["coords"], shape["options"])


# def Mode notice function
def action_notice():
    canvas.create_text(100, 10, text="Mode: " + action)


# def undo function
def undo():
    global step_list
    unique_list = []

    for x in step_list:
        if x not in unique_list:
            unique_list.append(x)
    step_list = unique_list
    canvas.delete(step_list[-1])
    print(step_list)
    step_list.remove(step_list[-1])

# def uniqe function for step list


def unique(list1):
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

# def draw function
# ------------------------------------------------------------------------------------


def draw_free(e):
    global current_x, current_y, counter, step_list
    canvas.create_line((current_x, current_y, e.x, e.y),
                       fill=color, tags="free_"+str(counter["free"]))
    step_list.append("free_"+str(counter["free"]))
    current_x, current_y = e.x, e.y


def draw_line(e):
    global current_x, current_y, temp_shape, step_list
    del_temp(temp_shape)
    temp_shape = canvas.create_line(
        (current_x, current_y, e.x, e.y), fill=color, tags="line_"+str(counter["line"]))
    step_list.append("line_"+str(counter["line"]))


def drawShapes(e):
    global current_x, current_y, temp_shape, shape, step_list
    del_temp(temp_shape)
    if ((shape == "square") and fill):
        new_x, new_y = max_size(e)
        # print("new x: {}".format(new_x))
        temp_shape = canvas.create_rectangle(
            (current_x, current_y, new_x, new_y), fill=color, outline=color, tags="square_"+str(counter["square"]))
        step_list.append("square_"+str(counter["square"]))
    elif ((shape == "square")):
        new_x, new_y = max_size(e)
        temp_shape = canvas.create_rectangle(
            (current_x, current_y, new_x, new_y), outline=color, tags="square_"+str(counter["square"]))
        step_list.append("square_"+str(counter["square"]))
    elif ((shape == "rectangle") and fill):
        temp_shape = canvas.create_rectangle(
            (current_x, current_y, e.x, e.y), fill=color, outline=color, tags="rectangle_"+str(counter["rectangle"]))
        step_list.append("rectangle_"+str(counter["rectangle"]))
    elif ((shape == "rectangle")):
        temp_shape = canvas.create_rectangle(
            (current_x, current_y, e.x, e.y), outline=color, tags="rectangle_"+str(counter["rectangle"]))
        step_list.append("rectangle_"+str(counter["rectangle"]))
    elif ((shape == "circle") and fill):
        new_x, new_y = max_size(e)
        temp_shape = canvas.create_oval(
            (current_x, current_y, new_x, new_y), fill=color, outline=color, tags="circle_"+str(counter["circle"]))
        step_list.append("circle_"+str(counter["circle"]))
    elif ((shape == "circle")):
        new_x, new_y = max_size(e)
        temp_shape = canvas.create_oval(
            (current_x, current_y, new_x, new_y), outline=color, tags="circle_"+str(counter["circle"]))
        step_list.append("circle_"+str(counter["circle"]))
    elif ((shape == "ellipse") and fill):
        temp_shape = canvas.create_oval(
            (current_x, current_y, e.x, e.y), fill=color, outline=color, tags="ellipse_"+str(counter["ellipse"]))
        step_list.append("ellipse_"+str(counter["ellipse"]))
    elif ((shape == "ellipse")):
        temp_shape = canvas.create_oval(
            (current_x, current_y, e.x, e.y), outline=color, tags="ellipse_"+str(counter["ellipse"]))
        step_list.append("ellipse_"+str(counter["ellipse"]))


def draw_closed_poly(e):
    global coord, step_list
    if fill:
        canvas.create_polygon(coord, outline=color, fill=color,
                              tags="closedpolygon_"+str(counter["closedpolygon"]))
        step_list.append("closedpolygon_"+str(counter["closedpolygon"]))
    else:
        canvas.create_polygon(coord, outline=color, fill="",
                              tags="closedpolygon_"+str(counter["closedpolygon"]))
        step_list.append("closedpolygon_"+str(counter["closedpolygon"]))


def draw_open_poly(e):
    global coord
    canvas.create_line(coord, fill=color,
                       tags="openpolygon_"+str(counter["openpolygon"]))
    step_list.append("openpolygon_"+str(counter["openpolygon"]))


# func for paste
def draw_copied(e):
    global saved_info
    func_list = {
        "line": getattr(canvas, "create_line"),
        "rectangle": getattr(canvas, "create_rectangle"),
        "oval": getattr(canvas, "create_oval"),
        "polygon": getattr(canvas, "create_polygon"),
    }
    tag_used = {}
    saved = copy.deepcopy(saved_info)
    if not saved:
        return
    diff_x = e.x-saved[0]["coords"][0]
    diff_y = e.y-saved[0]["coords"][1]
    print(len(saved[0]["coords"]))
    for shape in saved:
        for i in range(0, len(saved[0]["coords"]), 2):
            shape["coords"][i] = shape["coords"][i]+diff_x
            shape["coords"][i+1] = shape["coords"][i+1]+diff_y
        if shape["options"]["tags"] != '':
            used = shape["options"]["tags"].split(" ")
            new = []
            for current_tag in used:
                if current_tag not in ("{}", "current"):
                    if current_tag not in tag_used:
                        tag_used[current_tag] = set_new_tag(current_tag)
                    new.append(tag_used[current_tag])
            shape["options"]["tags"] = new
        func_list[shape["type"]](shape["coords"], shape["options"])
        print(shape)


# def action
# ----------------------------------------------------------------------------
def move_shape(e):
    global current_x, current_y
    new_x = e.x - current_x
    new_y = e.y - current_y
    canvas.move(id_shape[0], new_x, new_y)
    current_x, current_y = e.x, e.y


def save_shape(e):
    global saved_info, id_shape
    saved_info = []
    id_shape = id_shape[0]
    for id in canvas.find_withtag(id_shape):
        shape_info = {}
        shape_info["options"] = {}
        shape_info["type"] = canvas.type(id)
        shape_info["options"]["fill"] = canvas.itemcget(id, "fill")
    #    shape_info["options"]["outline"] = canvas.itemcget(id, "outline")
        shape_info["options"]["tags"] = canvas.itemcget(id, "tags")
        shape_info["coords"] = canvas.coords(id)
        print(shape_info["coords"])
        print(shape_info["type"])
        saved_info.append(shape_info)


# def mouse movement
# -------------------------------------------------------------------------------------
def mouse_left(e):
    global current_x, current_y, temp_shape, coord, id_shape, group_info
    if action == "draw":
        temp_shape = -1
        current_x, current_y = e.x, e.y
        if shape == "free":
            counter["free"] += 1
        if shape == "line":
            counter["line"] += 1
        if shape == "square":
            counter["square"] += 1
        if shape == "rectangle":
            counter["rectangle"] += 1
        if shape == "circle":
            counter["circle"] += 1
        if shape == "ellipse":
            counter["ellipse"] += 1
        if shape == "closed polygons":
            coord.append(e.x)
            coord.append(e.y)
            print(coord)
        if shape == "open polygons":
            coord.append(e.x)
            coord.append(e.y)
            print(coord)
    elif action == "move":
        id_shape = identify(e)
        current_x, current_y = e.x, e.y
    elif action == "cut":
        id_shape = identify(e)
        save_shape(e)
        canvas.delete(id_shape)
    elif action == "copy":
        id_shape = identify(e)
        save_shape(e)
    elif action == "group":
        id_shape = identify(e)
        group_info.append(id_shape)
        print(group_info)
        print(id_shape)
    elif action == "ungroup":
        id_shape = identify(e)
        print(id_shape)
        ungroup_shapes(e)


def mouse_drag(e):
    global step_list
    if action == "draw":
        if shape == "free":
            draw_free(e)

        elif shape == "line":
            draw_line(e)

        else:
            drawShapes(e)

    elif action == "move":
        move_shape(e)


def mouse_right(e):
    global coord, group_info
    if action == "draw":
        if shape == "closed polygons":
            draw_closed_poly(e)
            counter["closedpolygon"] += 1
            coord = []
        elif shape == "open polygons":
            draw_open_poly(e)
            counter["openpolygon"] += 1
            coord = []
    if action == "paste":
        draw_copied(e)
    if action == "group":
        group_shapes(e)
        group_info = []


# def mouse_released(e):
#     global current_x, current_y, new_x, new_y, shape
#     new_x, new_y = e.x, e.y
#     if shape == "line":
#         draw_line(current_x, current_y, new_x, new_y)
#     elif shape == "square":
#         drawShapes(e, "square")

# create GUI
# -----------------------------------------------------------------------------------
window = Tk()
window.title('SketchPad')
window.state('zoomed')
window.config(bg='white')

window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)


# config menu bar
menubar = Menu(window)
window.config(menu=menubar)
filemenu = Menu(menubar, tearoff=0)
shapemenu = Menu(menubar, tearoff=0)
colormenu = Menu(menubar, tearoff=0)
toolmenu = Menu(menubar, tearoff=0)
actionmenu = Menu(menubar, tearoff=0)


menubar.add_cascade(label='File', menu=filemenu)
menubar.add_cascade(label='Shape', menu=shapemenu)
menubar.add_cascade(label='Color', menu=colormenu)
menubar.add_cascade(label='Tool', menu=toolmenu)
menubar.add_cascade(label='Action', menu=actionmenu)


# File menu
filemenu.add_command(label='New Sketch', command=new_sketch)
filemenu.add_command(label="Undo", command=undo)
filemenu.add_command(label="Redo")
filemenu.add_command(label="Save", command=save)
filemenu.add_command(label="Load", command=load)
# Shape menu
for i in shapeSet:
    shapemenu.add_command(label=i, command=shape_lambda(i))
# Color menu
for i in colorSet:
    colormenu.add_command(label=i, command=color_lambda(i))
# Tool menu
for i in toolSet:
    toolmenu.add_command(label=i, command=tool_lambda(i))
# Action menu
for i in actionSet:
    actionmenu.add_command(label=i, command=action_lambda(i))


# create Canvas
canvas = Canvas(window, background='white')
canvas.grid(row=0, column=0, sticky='nsew')
canvas.bind('<Button-1>', mouse_left)
canvas.bind('<B1-Motion>', mouse_drag)
canvas.bind('<Button-3>', mouse_right)


# canvas.bind('<ButtonRelease-1>', mouse_released)

window.mainloop()