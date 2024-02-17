import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import *
from tkinter.font import BOLD
import winsound
import threading

# class MorseCoder, based on Tkinter
class MorseCoder(tk.Tk):
    
    # variables used in class for determining character position and list indexes and selection states

    delChar = ""                    # character to be deleted (by backspace or delete)
    
    # starting and ending character position of the selection in textbox/codebox
    sel_start = ''
    sel_end = ''
    mc_sel_start = ''
    mc_sel_end = '' 
    
    # state of the selection in textbox/codebox
    selection_flag = False
    m_selection_flag = False
    
    letter_list = []                # list of the translated text characters, with coordinates
    letter = ''                     # coded letter to be inserted in letter_list

    # cursor index for character in letter_list; start and end indexes for determining positions
    idx_cursor = 0
    idx_start = 0
    idx_end = 0
    
    # cursor coordinates in textbox/codebox
    cur_pos = None
    m_cur_pos = None

    # flag for cursor focus
    textField_focus_flag = True

    # flags for playing morse code
    mc_pause = False
    mc_stop = False

    # morse code
    m_code = {
        #letters
        'a' : '.- ', 'b': '-... ', 'c': '-.-. ', 'd': '-.. ', 'e': '. ', 'f': '..-. ', 'g': '--. ',
        'h': '.... ', 'i': '.. ', 'j': '.--- ', 'k': '-.- ', 'l': '.-.. ', 'm': '-- ', 'n': '-. ',
        'o': '--- ', 'p': '.--. ', 'q': '--.- ', 'r': '.-. ', 's': '... ', 't': '- ', 'u': '..- ',
        'v': '...- ', 'w': '.-- ', 'x': '-..- ', 'y': '-.-- ', 'z': '--.. ', ' ': '  ',
        #numbers
        '1': '.---- ', '2': '..--- ', '3': '...-- ', '4': '....- ', '5': '..... ',
        '6': '-.... ', '7': '--... ', '8': '---.. ', '9': '----. ', '0': '---- ',
        #punctuation
        ',': '--..-- ', #comma
        '.': '.-.-.- ', #full stop
        '?': '..--.. ', #question mark
        "'": '.----. ', #apostrophe
        ':': '---... ', #colon or division sign
        ';': '-.-.-. ', #semicolon
        '/': '-..-. ', #slash
        '-': '-....- ', #dash
        '``': '.-..-. ', #inverted commas
        '_': '..--.- ', #underscore
        '"': '.-..-. ', #quotation mark
        '$': '...-..- ', #dollar sign
        '=': '-...- ', #double hyphen
        '+': '.-.-. ', #cross
        '@': '.--.-. ', #'at' sign 
        '\n': '\n'
        # - = 3 time units
        # . = 1 time unit
        # gap between letters = 3 time units
        # gap between words = 7 time units
        # gap between dashes and dots = 1 time unit
        }

    # --- method for turning string to morse code
    # string = "good day"
    # x = " ".join(list(map(lambda ch: m_code[ch], string)))


    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        # defining program window
        self.minsize(400,550)
        self.resizable(False, False)
        
        self.frame0 = tk.Frame(width=400, height=500)
        self.frame0.pack()
        self.frame1 = tk.Frame(self.frame0, height=50, width=400)
        self.frame1.pack()

        # operating buttons
        self.button_new = tk.Button(self.frame1, text='New', width=8, command=self.new_)
        self.button_new.pack(side=tk.LEFT, padx=7, pady=10)
        self.button_open = tk.Button(self.frame1, text='Open', width=8, command=self.open_)
        self.button_open.pack(side=tk.LEFT, padx=7, pady=10)
        self.button_save = tk.Button(self.frame1, text='Save', width=8, command=self.save_)
        self.button_save.pack(side=tk.LEFT, padx=7, pady=10)
        self.button_help = tk.Button(self.frame1, text='Help', width = 8, command = self.help_)
        self.button_help.pack(side=tk.LEFT, padx=7, pady=10)
        self.button_exit = tk.Button(self.frame1, text='Exit', width=8, command=self.exit_)
        self.button_exit.pack(side=tk.LEFT, padx=7, pady=10)

        # frames and key bindings for textbox
        self.frame2 = tk.Frame().pack()
        self.label1 = tk.Label(self.frame2, text='Insert text: ').pack()
        self.textField = tk.Text(self.frame2, height=10, width=50)
        self.textField.pack(padx=10, pady=5, side=tk.TOP)
        self.textField.focus()
        self.textField.bind('<KeyPress>', self.toMorse)
        self.textField.bind('<Shift-KeyRelease>', self.bind_)
        self.textField.bind('<KeyPress-BackSpace>', self.delete_)
        self.textField.bind('<KeyPress-Delete>', self.delete_)
        self.textField.bind('<ButtonRelease>', self.cursor_pos)
        self.textField.bind('<<Selection>>', self.selection)
        self.textField.bind('<KeyPress-space>', self.insert_blank)
        self.textField.bind('<Return>', self.insert_blank)
        self.textField.bind('<Tab>', self.change_focus_)
        self.textField.bind('<Control-v>', self.paste_)

        # frames and key bindings for codebox
        self.frame3 = tk.Frame().pack()
        self.label2 = tk.Label(self.frame3, text='Morse Code:').pack()
        self.morseField = tk.Text(self.frame3, height=15, width=50)
        self.morseField.pack(padx=10, pady=5)
        self.morseField.bind('<KeyPress>', self.fromMorse)
        self.morseField.bind('<KeyPress-BackSpace>', self.m_delete_)
        self.morseField.bind('<KeyPress-Delete>', self.m_delete_)
        self.morseField.bind('<ButtonRelease>', self.m_cursor_pos)
        self.morseField.bind('<<Selection>>', self.m_selection)
        self.morseField.bind('<KeyRelease-Return>', self.m_insert_blank)
        # self.morseField.bind('<KeyPress-space>', self.m_insert_blank)
        self.morseField.bind('<Tab>', self.change_focus_)
        self.morseField.bind('<Control-v>', self.m_paste_)

        # defining morse code player buttons
        self.frame4 = tk.Frame()
        self.frame4.pack()
        photo1 = tk.PhotoImage(file = 'play-small.gif')
        self.play= tk.Button(self.frame4, command = self.play_morse, image = photo1)
        self.play.image = photo1
        self.play.pack(side=tk.LEFT, padx=5, pady=5)

        photo2 = tk.PhotoImage(file = 'pause-small.gif')
        self.pause = tk.Button(self.frame4, command = self.pause_morse, image = photo2)
        self.pause.image = photo2
        self.pause.pack(side=tk.LEFT, padx=5, pady=5)

        photo3 = tk.PhotoImage(file = 'stop-small.gif')
        self.stop= tk.Button(self.frame4, command = self.stop_morse, image = photo3)
        self.stop.image = photo3
        self.stop.pack(side=tk.LEFT, padx=5, pady=5)
        
    
    # modifier function for binding capital letter (shift + letter) 
    def bind_(self, event, modifier = "Shift", letter = "", callback = None):
        if modifier and letter:
            letter = "-" + event.char
        self.textField.bind('<{}{}>'.format(modifier, letter.upper()), callback)

    
    # function for translating text to morse code;
    # function is passed an event (character from keyboard input), which is translated with a m_code dictionary and
    # inserted into codebox on current cursor position;
    # coordinates (row, start and end position of coded character) and letter_list index are then calculated and inserted
    # as one element in the letter_list on appropriate list index
    def toMorse(self, event):
        try:
            char = event.char.lower()
            self.morseField.insert(tk.INSERT, self.m_code[char])
            row = int(self.morseField.index('insert').split('.')[0])
            coor1 = int(self.morseField.index('insert -' + str(len(self.m_code[char])) + 'c').split('.')[1])
            coor2 = int(self.morseField.index('insert -1c').split('.')[1])
            self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) + int(self.textField.index('insert').split('.')[1])
            element = [self.m_code[char], row, coor1, coor2]
            self.letter_list.insert(self.idx_cursor, element)
           
            # calculating coordinates of the characters after inserted character
            mark = self.morseField.index('insert')
            for element in self.letter_list[self.idx_cursor +1:]:
                element[1] = int(self.morseField.index('insert').split('.')[0])
                element[2] = int(self.morseField.index('insert').split('.')[1])
                element[3] = element[2] + len(element[0])-1 
                insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
            self.morseField.mark_set('insert', mark)

        except KeyError:
          pass
    
    
    # function for translating morse code to text;
    # function is passed an event (character from keyboard: '-', '.' or ' ') and added to letter string. After 'space' event,
    # letter string is translated via dictionary and appropriate letter is inserted into the textbox on cursor position;
    # coordinates (row, start and end coded character position) and letter_list index are then calculated and inserted 
    # as one element in letter_list on appropriate list index
    def fromMorse(self, event):
        if  event.char in ['.', '-', ' '] or event.keysym.lower() in ['backspace', 'space', 'return', 'delete', 'alt_l', 'control_l', 'shift_l']:
            try:
                if event.char == '\r': del self.letter_list ['\r']
                self.letter += event.char
                
                # inserting coded character in a list after 'space'
                # in the event of 'triple space', space is added to the textbox on cursor position (further space input is blocked)
                if event.char == ' ':
                    if self.morseField.get('insert -2c', 'insert') == '  ' and (event.keysym.lower() == 'space' or event.char == ' '):
                        row = int(self.morseField.index('insert').split('.')[0])
                        coor1 = int(self.morseField.index('insert -1c').split('.')[1])
                        coor2 = coor1 + 1
                        self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) + int(self.textField.index('insert').split('.')[1])
                        if self.morseField.get('insert -3c', 'insert') == '   ':
                            self.letter = self.letter[0:-1]
                            return "break"
                        
                        else:
                            self.textField.insert('insert', ' ')
                            self.letter_list[self.idx_cursor] = ['  ', row, coor1, coor2]
                            self.letter = ''
                            self.morseField.mark_set('insert', self.letter_list[self.idx_cursor+1][1])

                    # calculating coordinates and letter_list index and adding appropriate letter to the textbox on cursor position
                    else:
                        row = int(self.morseField.index('insert').split('.')[0])
                        coor1 = int(self.morseField.index('insert -' + str(len(self.letter) -1) + 'c').split('.')[1])
                        coor2 = int(self.morseField.index('insert').split('.')[1])
                        element = [self.letter, row, coor1, coor2]
                        self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) + int(self.textField.index('insert').split('.')[1])
                        self.letter_list.insert(self.idx_cursor, element)
                        self.letter = ''
                        for k, v in self.m_code.items():
                            if self.letter_list[self.idx_cursor][0] == v:
                                self.textField.insert('insert', k)

                    # calculating coordinates of coded characters after new coded character input                        
                    mark = self.morseField.index('insert')
                    for element in self.letter_list[self.idx_cursor +1:]:
                        element[1] = int(self.morseField.index('insert').split('.')[0]) #if element[0] != '\n' else int(self.morseField.index('insert -1c').split('.')[0])
                        element[2] = int(self.morseField.index('insert').split('.')[1]) +1 if '.0' not in self.morseField.index('insert') and int(self.morseField.index('insert').split('.')[1]) != element[2] else int(self.morseField.index('insert').split('.')[1])
                        element[3] = element[2] + len(element[0])-1 
                        insert_iter = '+' + str(len(element[0])+1) + 'c' 
                        self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
                    self.morseField.mark_set('insert', mark)

                
                   
            
            except:
                pass

        else:
            # warning message for wrong input
            message = ' <<< WRONG INPUT >>> '
            self.textField.tag_add('test','insert', 'insert')
            self.textField.tag_configure('test', background='red', foreground='white', font=BOLD)
            self.textField.insert('insert', message, ('test'))
            
            self.textField.after(1000, lambda: self.textField.delete('end-' + str(len(message)+1) + 'c', 'end'))
            
            # input_error = messagebox.showwarning('Warning!', '''Wrong character input. Please, use only provided characters accordingly:
            #                                         \n'.' - Dot \n'-' - Dash \n' ' - Empty space''')
            return "break"
        
    
    # function for determining cursor position in textbox
    def cursor_pos(self, event):
        if self.selection_flag == True:
            self.selection_flag = False
            return
        
        # resetting selection flags on every click
        self.sel_start, self.sel_end = '', ''
        self.mc_sel_start, self.mc_sel_end = '', ''
        self.letter = ''
        self.morseField.tag_delete('start'), self.textField.tag_delete('start')

        # calculating row, list index position and 'insert' mark for codebox
        self.cur_pos = self.textField.index(tk.INSERT)
        row = int(self.cur_pos.split('.')[0])
        self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) +  int(self.cur_pos.split('.')[1])
        
        text_indice = self.textField.get(str(row) + '.0', self.cur_pos)
        self.m_cur_pos = str(len(''.join(list(map(lambda ch: self.m_code[ch.lower()], text_indice)))))
        self.morseField.mark_set('insert', str(row) + '.0+' + self.m_cur_pos + 'c')
             
    
    # function for determining cursor position in codebox
    def m_cursor_pos(self, event):
        if self.m_selection_flag == True:
            self.m_selection_flag = False
            return 

        # resetting selection flags on every click
        self.sel_start, self.sel_end = '', ''
        self.mc_sel_start, self.mc_sel_end = '', ''
        self.letter = ''

        # calculating cursor coordinates
        self.morseField.tag_delete('start'), self.textField.tag_delete('start')
        coor1, coor2 = 0, 0
        row = int(self.morseField.index('insert').split('.')[0])
        self.m_cur_pos = int(self.morseField.index('insert').split('.')[1])

        # calculating list index
        for idx in range(len(self.letter_list)):
            if self.m_cur_pos >= self.letter_list[idx][2] and self.m_cur_pos <= self.letter_list[idx][3] and row == self.letter_list[idx][1]:
                self.idx_cursor = idx
                row = self.letter_list[idx][1]
                coor1 = self.letter_list[idx][2]
                coor2 = self.letter_list[idx][3]

        # calculating coordinates if click is out of range of written text, or at zero position
        if coor1 == 0 and coor2 == 0 and self.m_cur_pos != 0:
            self.idx_cursor = len(self.letter_list) -1
            row = int(self.letter_list[-1][1])
            coor1 = int(self.letter_list[-1][2])
            coor2 = int(self.letter_list[-1][3])
        
        elif coor1 == 0 and coor2 == 0 and self.m_cur_pos == 0:
            self.idx_cursor = len(self.letter_list) -1
            row = int(self.morseField.index('insert').split('.')[0])
            self.textField.mark_set('insert', str(row) + '.0')

        # calculating and highlighting coded letter in textbox and codebox    
        if coor2:
            self.textField.mark_set('insert', '1.0+' + str(self.idx_cursor +1) + 'c')
            self.textField.tag_delete('start')
            self.textField.tag_add('start', str(row) + '.0+' + str(self.idx_cursor - sum(1 for i in self.letter_list if i[1] < row)) + 'c')
            self.textField.tag_configure('start', background = 'red', foreground = 'white')

            self.morseField.mark_set('insert', str(row) + '.0+' +str(coor2+1) + 'c')
            self.morseField.tag_delete('start')
            self.morseField.tag_add('start', str(row) + '.0+' + str(coor1) + 'c', str(row) + '.0+' + str(coor2+1) + 'c')
            self.morseField.tag_configure('start', background = 'red', foreground = 'white')

    
    # function for handling selection in textbox
    def selection(self, event):

        # resetting selection tags and setting selection flag on True
        self.selection_flag = True
        self.morseField.tag_delete('start'), self.textField.tag_delete('start')
        self.letter = ''

        # calculating coordinates and setting new selection tags
        try:
            row_start = int(self.textField.index(SEL_FIRST).split('.')[0])
            row_end = int(self.textField.index(SEL_LAST).split('.')[0])
            
            self.idx_start = len(self.textField.get('1.0', SEL_FIRST))
            self.idx_end = len(self.textField.get('1.0', SEL_LAST))

            self.sel_start = self.textField.index(SEL_FIRST)
            self.sel_end = self.textField.index(SEL_LAST)
            self.mc_sel_start = str(row_start) + '.0+' + str(self.letter_list[self.idx_start][2]) + 'c'
            self.mc_sel_end = str(row_end) + '.0+' + str(self.letter_list[self.idx_end -1][3] +1) + 'c'

            self.morseField.tag_delete('start')
            self.morseField.tag_add('start', self.mc_sel_start, self.mc_sel_end)
            self.morseField.tag_config('start', background='blue', foreground='white')
        except:
            pass
    
    
    # function for handling selection in codebox
    def m_selection(self, event):

        # resetting selection tags and setting selection flag on True
        self.m_selection_flag = True
        self.morseField.tag_delete('start'), self.textField.tag_delete('start')
        self.letter = ''

        # calculating coordinates and setting new selection tags
        try:
            sel_start = int(self.morseField.index(SEL_FIRST).split('.')[1])
            row_start = int(self.morseField.index(SEL_FIRST).split('.')[0])
            sel_end = int((self.morseField.index(SEL_LAST)).split('.')[1])
            row_end = int(self.morseField.index(SEL_LAST).split('.')[0])

            # calculating which element to be highlighted
            for idx, element in enumerate(self.letter_list):
                if element[2] <= sel_start and element[3] >= sel_start and element[1] == row_start:
                    self.mc_sel_start = str(element[1]) + '.0' + '+' + str(element[2]) + 'c'
                    self.sel_start =  '1.0' + '+' + str(idx)+ 'c'
                elif element[2] <= sel_end and element[3] >= sel_end and element[1] == row_end:
                    self.mc_sel_end = str(element[1]) + '.0' + '+' + str(element[3]+1) + 'c'
                    self.sel_end = '1.0' + '+' + str(idx +1) + 'c'

            # calculating start and end list indexes of the selection
            self.idx_start = len(self.textField.get('1.0', self.sel_start))
            self.idx_end = len(self.textField.get('1.0', self.sel_end))

            # adding selection tags for textbox and codebox
            self.morseField.tag_delete('start')
            self.morseField.tag_add('start', self.mc_sel_start, self.mc_sel_end)
            self.morseField.tag_configure('start', background='green', foreground='white')

            self.textField.tag_delete('start')
            self.textField.tag_add('start', self.sel_start, self.sel_end)
            self.textField.tag_configure('start', background='blue', foreground='white')
           
        except:
            pass
        return "break"

    
    # function for handling deletion in textbox;
    # delete event is triggered by pressing 'delete' or 'backspace' on keyboard;
    # cursor position, row and letter_list index are calculater, and letter string is set to ''; 
    # selection check is being made, and if its True, selection is deleted, and coordinates of remaining letter_list elements are recalculated;
    # if selection check if False, del_Char will be selected (depending on which button is pressed - 'delete' or 'backspace), deleted, and coordinates
    # of the remaining letter_list elements will be recalculated
    # insert mark is then set on appropriate position
    def delete_(self, event):
        self.cur_pos = self.textField.index(tk.INSERT)
        row = int(self.cur_pos.split('.')[0])
        self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) +  int(self.cur_pos.split('.')[1])
        self.letter = ''

        # selection check
        if self.mc_sel_end:
            self.morseField.delete(self.mc_sel_start, self.mc_sel_end)
            del self.letter_list[self.idx_start:self.idx_end]

            self.textField.mark_set('insert', self.sel_start)
            self.morseField.mark_set('insert', self.mc_sel_start)
            self.idx_cursor = self.idx_start

            # recalculating coordinates of the remaining elements
            for element in self.letter_list[self.idx_cursor:]:
                element[1] = int(self.morseField.index('insert').split('.')[0])
                element[2] = int(self.morseField.index('insert').split('.')[1])
                element[3] = element[2] + len(element[0])-1 
                insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
            self.morseField.mark_set('insert', self.mc_sel_start)
            
            # resetting selection flags
            self.sel_start, self.sel_end = '', ''
            self.mc_sel_start, self.mc_sel_end = '', ''
            self.selection_flag = False
    
        # selection check is False
        elif self.mc_sel_start == '' and self.mc_sel_end == '':
            
            # determining which key is pressed and handling event accordingly
            try:
                if (event.keysym).lower() == 'backspace':
                    del_char = self.textField.get('insert-1c').lower()
                    del_morse = str(len(self.m_code[del_char]))
                    self.morseField.delete('insert-' + del_morse + 'c', 'insert')

                    mark = self.morseField.index('insert')
                    if (self.idx_cursor + 1) != len(self.letter_list) and self.idx_cursor != 0:
                        
                        del self.letter_list[self.idx_cursor-1]

                        for element in self.letter_list[self.idx_cursor-1:]:
                            element[1] = int(self.morseField.index('insert').split('.')[0])
                            element[2] = int(self.morseField.index('insert').split('.')[1])
                            element[3] = element[2] + len(element[0])-1 
                            insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                            self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
                        

                    elif (self.idx_cursor + 1) == len(self.letter_list):
                        del self.letter_list[self.idx_cursor]

                        for element in self.letter_list[self.idx_cursor-1:]:
                            element[1] = int(self.morseField.index('insert').split('.')[0])
                            element[2] = int(self.morseField.index('insert').split('.')[1])
                            element[3] = element[2] + len(element[0])-1 
                            insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                            self.morseField.mark_set('insert', 'insert-1c' + insert_iter)

                    self.morseField.mark_set('insert', mark)
             
                elif (event.keysym).lower() == 'delete':
                    del_char = self.textField.get('insert').lower()
                    del_morse = str(len(self.m_code[del_char]))
                    mark = self.morseField.index('insert')

                    if (self.idx_cursor) < len(self.letter_list):
                        self.morseField.delete('insert', 'insert+' + del_morse + 'c')
                        del self.letter_list[self.idx_cursor]
                      
                        for element in self.letter_list[self.idx_cursor:]:
                            element[1] = int(self.morseField.index('insert').split('.')[0])
                            element[2] = int(self.morseField.index('insert').split('.')[1])
                            element[3] = element[2] + len(element[0])-1 
                            insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                            self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
                    
                    else:
                        pass
                    
                    self.morseField.mark_set('insert', mark)

            except KeyError or IndexError:
                pass
            
            self.selection_flag = False
            

    # function for handling deletion in codebox
    # delete event is triggered by pressing 'delete' or 'backspace' on keyboard;
    # cursor position, row and letter_list index are calculater, and letter string is set to ''; 
    # selection check is being made, if True, selection is deleted, coordinates of remaining elements are recalculated;
    # if selection check if False, del_Char will be selected (depending on which button is pressed - 'delete' or
    # 'backspace), deleted, and coordinates of the remaining letter_list elements will be recalculated;
    # insert mark is then set on appropriate position
    def m_delete_(self, event):

        row = int(self.morseField.index('insert -1c').split('.')[0])
        self.m_cur_pos = int(self.morseField.index('insert -1c').split('.')[1])
        self.letter = ''

        for idx in range(len(self.letter_list)):
            if self.m_cur_pos >= self.letter_list[idx][2] and self.m_cur_pos <= self.letter_list[idx][3] and row == self.letter_list[idx][1]:
                self.idx_cursor = idx
                row = self.letter_list[idx][1]

        # selection check and calculation of start and end selection positions  
        if self.mc_sel_end:
            self.textField.delete(self.sel_start, self.sel_end)
            self.morseField.delete(self.mc_sel_start, self.mc_sel_end)
            del self.letter_list[self.idx_start: self.idx_end]

            self.textField.mark_set('insert', self.sel_start)
            self.morseField.mark_set('insert', self.mc_sel_start)
            self.idx_cursor = self.idx_start
            
            mark = self.morseField.index('insert')

            # recalculating coordinates of the remaining letter_list elements
            for element in self.letter_list[self.idx_cursor:]:
                element[1] = int(self.morseField.index('insert').split('.')[0])
                element[2] = int(self.morseField.index('insert').split('.')[1])
                element[3] = element[2] + len(element[0])-1 
                insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                self.morseField.mark_set('insert', 'insert-1c' + insert_iter)

            self.morseField.mark_set('insert', self.mc_sel_start)

            self.sel_start, self.sel_end = '', ''
            self.mc_sel_start, self.mc_sel_end = '', ''
            self.selection_flag = False
            return "break"

        # if selection check is False
        elif self.mc_sel_start == '' and self.mc_sel_end == '':
 
            # determining which key is pressed ('delete' or 'backspace') and handling event accordingly
            if (event.keysym).lower() == 'backspace' and self.morseField.index('insert') != '1.0':
                del_start = str(self.letter_list[self.idx_cursor][1]) + '.' + str(self.letter_list[self.idx_cursor][2])
                del_end = str(self.letter_list[self.idx_cursor][1]) + '.' + str(self.letter_list[self.idx_cursor][3])
                self.morseField.delete(del_start, del_end)
                self.textField.delete('insert -1c', 'insert')

                # in case the selected character is newline ('\n')
                if self.letter_list[self.idx_cursor][0] == '\n':
                    x = self.morseField.get(del_start + '+1c', END)
                    if x == '\n':
                        del self.letter_list[self.idx_cursor]
                        return
                    
                    else:
                        self.morseField.delete(del_start, END)
                        self.morseField.insert('insert', ' ' + x) if x != '\n' or x!= '\n\n' else self.morseField.insert('insert', x)
                        self.morseField.mark_set('insert', del_start + '+1c') if x!= 'n' or x!= '\n\n' else self.morseField.mark_set('insert', 'insert -1c')

                del self.letter_list[self.idx_cursor]

                # recalculating coordinates of the remaining letter_list elements
                mark = self.morseField.index('insert')
                for element in self.letter_list[self.idx_cursor:]:
                    element[1] = int(self.morseField.index('insert').split('.')[0]) #if nl == False else int(self.morseField.index('insert').split('.')[0]) -1
                    element[2] = int(self.morseField.index('insert').split('.')[1]) -1 if '.0' not in self.morseField.index('insert') else int(self.morseField.index('insert').split('.')[1])
                    element[3] = element[2] + len(element[0])-1 
                    insert_iter = '+' + str(len(element[0])) + 'c' if element[0] != '\n' else '+' + str(len(element[0])+1) + 'c' #if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                    self.morseField.mark_set('insert', 'insert' + insert_iter)
                    
                self.morseField.mark_set('insert', mark)

            elif (event.keysym).lower() == 'delete' and (self.idx_cursor) < len(self.letter_list):
                if self.idx_cursor != 0:
                    del_start = str(self.letter_list[self.idx_cursor +1][1]) + '.' + str(self.letter_list[self.idx_cursor +1][2])
                    del_end = str(self.letter_list[self.idx_cursor +1][1]) + '.' + str(self.letter_list[self.idx_cursor +1][3])
                    self.morseField.delete(del_start, del_end)
                    self.textField.delete('insert')

                    if self.letter_list[self.idx_cursor +1][0] == '\n':
                        x = self.morseField.get(del_start + '+1c', END)
                        if x == '\n':
                            del self.letter_list[self.idx_cursor +1]
                            return
                    
                        else:
                            self.morseField.delete(del_start, END)
                            self.morseField.insert('insert', ' '+  x) if x != '\n' or x!= '\n\n' else self.morseField.insert('insert', x)
                            self.morseField.mark_set('insert', del_start) if x!= 'n' or x!= '\n\n' else self.morseField.mark_set('insert', 'insert -1c')

                    del self.letter_list[self.idx_cursor +1]

                    mark = self.morseField.index('insert')
                    for element in self.letter_list[self.idx_cursor +1:]:
                        element[1] = int(self.morseField.index('insert').split('.')[0]) #if int(self.morseField.index('insert').split('.')[0]) == int(self.morseField.index('insert +1c').split('.')[0]) else int(self.morseField.index('insert +1c').split('.')[0])
                        element[2] = int(self.morseField.index('insert').split('.')[1])
                        element[3] = element[2] + len(element[0])-1 
                        insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                        self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
                
                    self.morseField.mark_set('insert', mark)

                else:
                    del_start = str(self.letter_list[self.idx_cursor][1]) + '.' + str(self.letter_list[self.idx_cursor][2])
                    del_end = str(self.letter_list[self.idx_cursor][1]) + '.' + str(self.letter_list[self.idx_cursor][3]+1)
                    self.morseField.delete(del_start, del_end)
                    self.textField.delete('insert -1c')
                    del self.letter_list[self.idx_cursor]

                    mark = self.morseField.index('insert')
                    for element in self.letter_list[self.idx_cursor:]:
                        element[1] = int(self.morseField.index('insert').split('.')[0])
                        element[2] = int(self.morseField.index('insert').split('.')[1])
                        element[3] = element[2] + len(element[0])-1
                        insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                        self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
                    
                    self.morseField.mark_set('insert', mark)
                    return "break"
            else:
                pass
            self.letter = ''
            self.selection_flag = False


    # function for handling empty space events (spacebar or return)
    def insert_blank(self, event):
        # blocking more than three (3) space inputs
        if (event.keysym).lower() == 'space':
            if self.morseField.get('insert -3c', 'insert -1c') == '  ':
                return "break"

            # calculating coordinates and letter_list index and inserting empty space in letter_list and codebox
            self.morseField.insert(tk.INSERT, self.m_code[' '])
            row = int(self.morseField.index('insert').split('.')[0]) 
            self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) + int(self.textField.index('insert').split('.')[1])
            coor1 = int(self.morseField.index('insert -' + str(len(self.m_code[' '])) + 'c').split('.')[1])
            coor2 = int(self.morseField.index('insert -1c').split('.')[1])
            element = [self.m_code[' '], row, coor1, coor2]
            self.letter_list.insert(self.idx_cursor, element)
            
        # calculating coordinates and letter_list index and inserting return in letter_list and codebox
        elif (event.keysym).lower() == 'return':
            self.morseField.insert(tk.INSERT, '\n')
            row = int(self.morseField.index('insert -1c').split('.')[0])
            coor1 = int(self.morseField.index('insert -' + str(len(self.m_code['\n'])) + 'c').split('.')[1])
            coor2 = int(self.morseField.index('insert -1c').split('.')[1])
            self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) + int(self.textField.index('insert').split('.')[1])
            
            element = ['\n', row, coor1, coor2]
            self.letter_list.insert(self.idx_cursor, element)

        mark = self.morseField.index('insert')
        
        # recalculating coordinates of letter_list elements after return/space input
        for element in self.letter_list[self.idx_cursor+1:]:
                        element[1] = int(self.morseField.index('insert').split('.')[0])
                        element[2] = int(self.morseField.index('insert').split('.')[1])
                        element[3] = element[2] + len(element[0])-1 
                        insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                        self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
                        
        self.morseField.mark_set('insert', mark)

      

    # function for handling empty space events (return) *spacebar event is handled by fromMorse function
    def m_insert_blank(self, event):
        
        # in the event of incomplete morse code input, appropriate character will be added to textbox and letter_list after return input
        if (event.keysym).lower() == 'return':

            if self.letter and self.letter[-1] != ' ':
                self.letter += ' '
                self.morseField.insert('insert -1c', ' ')

                # calculating coordinates of incomplete coded character to be inserted into letter_list
                row = int(self.morseField.index('insert -1c').split('.')[0])
                coor1 = int(self.morseField.index('insert -' + str(len(self.letter) +1) + 'c').split('.')[1])
                coor2 = int(self.morseField.index('insert -2c').split('.')[1])
                self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) + int(self.textField.index('insert').split('.')[1])
                element = [self.letter, row, coor1, coor2]
                self.letter_list.insert(self.idx_cursor, element)
                self.letter = ''

                for k, v in self.m_code.items():
                    if self.letter_list[self.idx_cursor][0] == v:
                        self.textField.insert('insert', k)

            
            self.textField.insert(tk.INSERT, '\n')

            # calculating coordinates of 'return' character
            row = int(self.morseField.index('insert -1c').split('.')[0])
            coor1 = int(self.morseField.index('insert -1c').split('.')[1])
            coor2 = int(self.morseField.index('insert -1c').split('.')[1])
            self.idx_cursor = sum(1 for i in self.letter_list if i[1] < row) + int(self.textField.index('insert -1c').split('.')[1])
           
            element = ['\n', row, coor1, coor2]
            self.letter_list.insert(self.idx_cursor, element)
            
            # recalculating coordinates of the letter_list elements after return input
            mark = self.morseField.index('insert')
            for element in self.letter_list[self.idx_cursor +1:]:
                element[1] = int(self.morseField.index('insert').split('.')[0])
                element[2] = int(self.morseField.index('insert').split('.')[1])
                element[3] = element[2] + len(element[0])-1 
                insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
            
            self.morseField.mark_set('insert', mark)
           
        elif (event.keysym).lower() == 'tab':
            self.textField.insert(tk.INSERT, '    ')


    # function for handling pausing of morse code via seperate thread
    def pause_morse(self):
        thread2 = threading.Thread(target = self.pause_)
        thread2.start()

    # determining pause/unpause flag
    def pause_(self):
        if self.mc_pause == True:
            self.mc_pause = False
        else:
            self.mc_pause = True

    # function for handling stopping of morse code via seperate thread
    def stop_morse(self):
        thread3 = threading.Thread(target = self.stop_)
        thread3.start()

    # setting stop flag
    def stop_(self):
        self.mc_stop = True

    # functiong for handling playing of morse code via seperate thread
    def play_morse(self):
        thread1 = threading.Thread(target = self.play_)
        thread1.start()

    # function for checking if pause/unpause or stop is pressed on every iterration and acting accordingly
    def play_(self):
        self.mc_stop, self.mc_pause = False, False

        inputCode = self.morseField.get('1.0', 'end')
        i = 2
        while i <= len(inputCode)+1:
            if self.mc_stop == True: return
            elif self.mc_pause == True: continue
            elif self.mc_pause == False:

                if inputCode[i-2] == " " and inputCode[i-1] == " " and inputCode[i] == " ":
                    winsound.Beep(50, 700)
                elif inputCode[i-2] == " ":
                    winsound.Beep(50, 300)
                elif inputCode[i-2] == ".":
                    winsound.Beep(1000, 100)
                    winsound.Beep(50, 100)
                elif inputCode[i-2] == "-":
                    winsound.Beep(1000, 300)
                    winsound.Beep(50, 100)
                
                i+=1
            
   
    # function for reseting program state
    def reset_(self):
        self.textField.delete('1.0', END)
        self.morseField.delete('1.0', END)

        self.delChar, self.letter = '', ''
        self.letter_list = []

        self.sel_start, self.sel_end = '', ''
        self.mc_sel_start, self.mc_sel_end = '', ''
        self.idx_cursor = 0

        self.idx_start, self.idx_end = 0, 0
        self.selection_flag, self.m_selection_flag = False, False
        self.cur_pos, self.m_cur_pos = None, None

    
    # changing focus from textField to morseField
    def change_focus_(self, event):
        if self.textField_focus_flag == True:
            self.morseField.focus()
            self.textField_focus_flag = False
        else: 
            self.textField.focus()
            self.textField_focus_flag = True
        return "break"


    # function for initalizing list of morse code characters with coordinates
    def code_list_(self, code, opt):

        if opt == 'open':
            morse_list = []
            ch = ''
          
            for el in code:
                self.letter_list.insert(self.idx_cursor, [self.m_code[el], 0, 0, 0])
                self.idx_cursor +=1
            
            self.morseField.mark_set('insert', '1.0')
            for element in self.letter_list:
                element[1] = int(self.morseField.index('insert').split('.')[0])
                element[2] = int(self.morseField.index('insert').split('.')[1])
                element[3] = element[2] + len(element[0])-1 
                insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
        
        elif opt == 'paste':
            morse_list = []
            ch = ''

            self.textField.insert('insert', code)
           
            for el in code:
                self.morseField.insert('insert', self.m_code[el])
                self.letter_list.insert(self.idx_cursor, [self.m_code[el], 0, 0, 0])
                self.idx_cursor +=1
            
            self.morseField.mark_set('insert', '1.0')
            for element in self.letter_list:
                element[1] = int(self.morseField.index('insert').split('.')[0])
                element[2] = int(self.morseField.index('insert').split('.')[1])
                element[3] = element[2] + len(element[0])-1 
                insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
            

        elif opt == 'm_paste':
            morse_list = []
            ch = ''

            for el in code:
                if el in ('-', '.'):
                    ch+= el
                elif el == ' ':
                    ch+= el
                    morse_list.append([ch, 0, 0, 0])
                    ch = ''
                elif el == '\n' and ch == '':
                    morse_list.append(['\n', 0, 0, 0])
                    ch = ''
                elif el == '\n' and ch != '':
                    ch+= ' '
                    morse_list.append([ch, 0, 0, 0])
                    morse_list.append(['\n', 0, 0, 0])
                    ch = ''
            
            for i in range(1, len(morse_list)-1):
                if morse_list[i-1][0] == ' ' and morse_list[i][0] == ' ':
                    morse_list[i-1][0] = '  '
                    del morse_list[i] 
            for el in morse_list:
                self.morseField.insert('insert', el[0])
                self.letter_list.insert(self.idx_cursor +1, el)
                self.idx_cursor +=1
            
            for ch in morse_list:
                for k, v in self.m_code.items():
                    if ch[0] == v:
                        self.textField.insert('insert', k)
            
            self.morseField.mark_set('insert', '1.0')
            for element in self.letter_list:
                element[1] = int(self.morseField.index('insert').split('.')[0])
                element[2] = int(self.morseField.index('insert').split('.')[1])
                element[3] = element[2] + len(element[0])-1 
                insert_iter = '+' + str(len(element[0])+1) + 'c' if self.morseField.index('insert') != '1.0' else '+' + str(len(element[0])) + 'c'
                self.morseField.mark_set('insert', 'insert-1c' + insert_iter)
            

        
    
    def paste_(self, event):
        
        paste_text = self.textField.selection_get(selection='CLIPBOARD')
        self.code_list_(paste_text, 'paste')
        
        return "break"
    
    def m_paste_(self, event):
        
        code = self.morseField.selection_get(selection='CLIPBOARD')
        self.code_list_(code, 'm_paste')
        
        return "break"
        

    # function for handling New File option
    def new_(self):
        clicked_new = messagebox.askyesnocancel('New File', 'All progress will be lost. Do you want to save current code?')
        if clicked_new:
            self.save_()
            self.reset_()
            

        elif clicked_new == False:
            self.reset_()
            
        elif clicked_new == None:
            pass
        

    # function for handling Open File option
    def open_(self):
        if self.morseField.get('1.0', 'end') != '\n':
            clicked_open = messagebox.askyesnocancel('Open File', 'All progress will be lost. Do you want to save current code?')
            if clicked_open:
                self.save_()
                self.reset_()
            
            elif clicked_open==None:
                return
            
            elif clicked_open == False:
                self.reset_()

        self.filename = filedialog.askopenfile(initialdir=' ', title='Open File: ', defaultextension='txt', filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        try:
            text = self.filename.readlines()
            write_text = False
            write_morse = False
            for line in text:
                if line.strip() == 'Text entered:':
                    write_text = True
                    continue
                elif line.strip() == 'Morse code:':
                    write_morse = True
                    continue
                elif line.strip() == '-||-':
                    write_text = False
                    write_morse = False
                    continue
                elif write_text:
                    self.textField.insert('end', line)
                elif write_morse:
                    self.morseField.insert('end', line)
        except:
            pass
        
        code = self.textField.get('1.0', 'end-1c')
        self.code_list_(code, 'open')

    
    # function for handling Save file option
    def save_(self):
        self.filename = filedialog.asksaveasfile(initialdir=' ', title='Save As: ', defaultextension='txt', filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        text = 'Text entered:\n' + self.textField.get('1.0', 'end -1c') + '\n-||-\n'
        morse = 'Morse code:\n' + self.morseField.get('1.0', 'end -1c') + '\n-||-\n'
        self.filename.write(text)
        self.filename.write(morse)
        self.filename.close()

    
    # function for handling Help option
    def help_(self):
        clicked_help = messagebox.showinfo('Help',
        '''         ----- MorseCoder ----- Version 1.01

            How to use program:
        1. For translating text into morse code, please enter your text into designated textbox.
           Program will automatically translate your text into morse code.
        2. For translating morse code into text, please enter your morse code into designated codebox.
           Program will automatically translate your morse code into text.
        3. For entering morse code, please, use only designated characters:
                .   - for "dot" 
                -   - for "dash"
                "  " - double space for space
        4. Press Tab to change between input boxes.
        5. Press "Play" button to play your morse code.
        6. Press "Pause" button to pause/unpause morse code playing.
        7. Press "Stop" button to stop morse code playing.
        ''')

        # if clicked_help:
        #     self.destroy()
    
    def exit_(self):
        self.destroy()



################################################################################

# starting the application
win = MorseCoder()
win.mainloop()
