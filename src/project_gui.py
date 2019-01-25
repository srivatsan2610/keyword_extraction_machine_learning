'''
Summary :
this is the gui code for the project

Author : Srivatsan Ananthakrishnan
Main reference : https://www.tutorialspoint.com/python/python_gui_programming.htm, the main reference for all the code which i used in this py is from the above link

Note:
I had an issue with the progress bar not showing up when needed and the gui app freezes(going to Not responding state) even when the program is running fine,
to solve this, I checked in google and made it as multi threading
#reference link : https://stackoverflow.com/questions/16400533/why-ttk-progressbar-appears-after-process-in-tkinter
'''
 
import tkinter
from tkinter import messagebox
import tkinter.ttk as ttk
from web_topic_analyzer import WebTopicAnalyzer
import datetime
import threading
import time

actual_url = ""
#import words
import requests

tokens = []


class project_GUI:
    def __init__(self,master):
        self.master = master
        #giving the title for the gui 
        self.master.title("Web Page Key-Phrase Extractor")
        #self.master.geometry("2000x2000+0+0")

        #declaring all the frames needed for the application
        #frames

        self.frame_header = tkinter.Frame(self.master,height = 50,width = 1000)
        self.frame_url = tkinter.Frame(self.master,height = 50,width = 1000)
        self.frame_buttons = tkinter.Frame(self.master,height = 50,width = 1000)
        self.frame_progress_bar = tkinter.Frame(self.master,height = 50, width = 1000)
        self.frame_output_heading = tkinter.Frame(self.master,height = 100,width = 1000)
        self.frame_output_set_1 = tkinter.Frame(self.master,height = 200,width = 1000)
        self.frame_output_set_2 = tkinter.Frame(self.master,height = 200,width = 1000)
        self.frame_output_set_3 = tkinter.Frame(self.master,height = 20,width = 1000)
        self.frame_warning = tkinter.Frame(self.master,height = 20,width = 1000)

        #packing all the frames
        
        self.frame_header.pack()
        self.frame_url.pack()
        self.frame_buttons.pack()
        self.frame_output_heading.pack()
        self.frame_progress_bar.pack()
        self.frame_output_set_1.pack()
        self.frame_output_set_2.pack()
        self.frame_output_set_3.pack()
        self.frame_warning.pack()
        
        #variable to store the url which the user gives
        self.current_url= tkinter.StringVar()

        #label for header text title, ie for the heading which comes up in the app 
        
        self.title_label = tkinter.Label(self.frame_header, text = "Web Page Key-Phrase Extractor", anchor = "center", fg = "brown", height = 2)
        self.title_label.config(font = ("Calibri", 40))
        self.title_label.pack()

        #progress bar to show the progress of the program execution

        #self.loading_text = tkinter.Label(self.frame_progress_bar, bd = 4, font = "Calibri", fg = "brown" , anchor = "center", height = 2)
        self.progress_bar = ttk.Progressbar(self.frame_progress_bar, orient='horizontal', length="400", mode='determinate')
        #self.progress_bar.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP)
        
        #label for user text

        self.enter_url_label = tkinter.Label(self.frame_url,text = "Enter the URL     ")
        self.enter_url_label.config(font = ("Calibri", 16))

        self.enter_url_label.pack(side= "left")

        #label to be displayed when too little tokens are expected

        self.warning_message_label = tkinter.Label(self.frame_warning,text = "Warning: Too small text data input, fewer or unpredictable keywords expected",height = 2,anchor = "center",fg="brown",font = ("calibri",15),justify = "center")

        #entry widget for user to enter the url


        self.enter_user_url_label = tkinter.Entry(self.frame_url,width=100,textvariable = self.current_url)

        self.enter_user_url_label.pack(side= "left")
        #this one is to place the cursor in the Entry widget when the app loads. 
        self.enter_user_url_label.focus()
        

        #button

        #reset button
        self.reset_button = tkinter.Button(self.frame_buttons,text = "Reset",width = 10,command = self.on_reset)
        self.reset_button.pack(side = "left")

        #extract button
        self.extract_button = tkinter.Button(self.frame_buttons,text = "Extract",width=10,command=lambda:self.start_thread(None))
        #start thread concept , took it from https://stackoverflow.com/questions/16400533/why-ttk-progressbar-appears-after-process-in-tkinter
        self.extract_button.pack(side = "left")

        #label to hold the heading when the output keywords are getting displayed
        self.label_op1 = tkinter.Label(self.frame_output_heading)
        self.labels= []
        #creating 15 dynamic labels and storing their names in the list, so that all those can be accessed later
        #three different label definitions mainly to have 5 labels in one row.
        #the application will display max of 15 tokens, each 5 in each row
        for i in range(15):
             if i < 5:
                 label = tkinter.Label(self.frame_output_set_1, height = 3, justify = "center", anchor = "center",pady = 2,font = ("Calibri",12), fg= "brown",wraplength = 100, relief = "ridge",width = 20, padx = 1)
             if i >=5 and i < 10:
                 label = tkinter.Label(self.frame_output_set_2, height = 3 ,justify = "center",anchor = "center",pady = 2,font = ("Calibri",12), fg = "brown",wraplength = 100 ,relief = "ridge",width = 20, padx = 1)
             if i >= 10:
                 label = tkinter.Label(self.frame_output_set_3,height = 3, justify = "center",anchor = "center",pady = 2, font = ("Calibri",12), fg = "brown",wraplength = 100, relief = "ridge",width = 20, padx = 1)
             self.labels.append(label) 

 
    def check_url(self,url):
        ''' This function is to verify the user entered url'''
        try:
            request = requests.get(url)
            if request.status_code == 200 and ("text/html" in request.headers["content-type"]):  #if the status code is 200 and content type is text/html, then alone the corresponding url can be processed
                return True
            else:
                return False

        except:
            return False

   
    def on_reset(self):
        ''' this function will be executed when the button reset is clicked'''
        self.enter_user_url_label.delete(0,'end') #delete the content of the Entry widget
        self.label_op1.pack_forget() #remove the label
        self.progress_bar.pack_forget() #remove the progress bar
        self.warning_message_label.pack_forget() #remove warning label
        for label in self.labels: #remove all the token labels
            label.pack_forget()


    def no_url(self):
        '''this function will be executed when the url entered by the user does not exist'''
        tkinter.messagebox.showerror("Error","Website does not exist or it is forbidden, Please check it!") #show a error message box

       
        
    def on_extract(self):
        ''' This function will be executed when the user clicks extract button'''
        #pack the label
        #please_wait_label.pack_forget()
         #call reset first
        actual_url = self.current_url.get() #get the user entered url to this variable
        self.label_op1.pack_forget()
        
        self.warning_message_label.pack_forget()
        for label in self.labels: #remove all the token labels
            label.pack_forget()
        
        if self.check_url(actual_url) == True:  #check is the url is valid
            
           self.reset_button.config(state = "disabled") #disable the reset button, when the extraction process is going on
           self.extract_button.config(state = "disabled")
           a = datetime.datetime.now()
           analyzer = WebTopicAnalyzer(actual_url); #call the actual function
           process_result = analyzer.process(); #get the result in the process_result variable
           if 'is_input_small' in process_result:
               self.warning_message_label.pack(side="top")
           if 'error' in process_result: #if error
            tkinter.messagebox.showerror("Error",process_result['error']); #show the error
            self.reset_button.config(state = "normal") #after showing the error, enable the reset and extract buttons
            self.extract_button.config(state = "normal")
           elif 'words' in process_result: #if no error
            tokens = process_result['words']; #get the words to the tokens variable
            self.label_op1.config(text = "Tokens for the webpage", height = 3, anchor = "center", fg = "brown" , font = ("calibri",20)) #label to show the heading 
            self.label_op1.pack(side = "top")
            
            for label_index in range(len(tokens)): #now set these returned tokens to the dynamic labels which I created before
                if label_index < 5:
                    self.labels[label_index].config(text = str(tokens[label_index]))
                    self.labels[label_index].pack(fill= "x",side = "left")
                elif label_index >= 5 and label_index < 10:
                    self.labels[label_index].config(text = str(tokens[label_index]))
                    self.labels[label_index].pack(fill= "x",side = "left")
                else:
                    self.labels[label_index].config(text = str(tokens[label_index]))
                    self.labels[label_index].pack(fill= "x",side = "left")

            #self.loading_text.pack_forget()
            self.reset_button.config(state = "normal") #here when the extraction is done , reset button will then be active again
            self.extract_button.config(state = "normal")
            b = datetime.datetime.now()
            c = b - a
            print("Total time taken : ", c.seconds, " seconds")
           
          
            
        else:
            self.no_url()  #if url is not valid, call this function


    #had an issue with the progress bar not showing up when needed and the gui app freezes even when the program is running fine, to solve this, I checked in google and made it as multi threading
    #reference link : https://stackoverflow.com/questions/16400533/why-ttk-progressbar-appears-after-process-in-tkinter
            
    def start_thread(self, event):
        ''' to start the multi threading'''
        global foo_thread
        foo_thread = threading.Thread(target=self.on_extract)
        foo_thread.daemon = True
        self.progress_bar.pack(expand=True, fill=tkinter.BOTH, side=tkinter.TOP)
        self.progress_bar.start()
        foo_thread.start()
        self.master.after(20, self.check_thread)

    
    def check_thread(self):
        """to check whether the thread is still running, this is to make the gui app alive, even when the total execution takes more time """
        if foo_thread.is_alive():
            self.master.after(20, self.check_thread)
        else: #once the process is done, stop the progress bar and remove the progress bar
            
            self.progress_bar.stop()
            self.progress_bar.pack_forget();

   

master = tkinter.Tk()
master.state('zoomed') #this one is to make the app geometry to the screen size
p = project_GUI(master)

master.mainloop()


