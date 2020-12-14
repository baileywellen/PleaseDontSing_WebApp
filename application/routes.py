#ALL of the routes should be kept in this file 

#import app from the __init__ file 
from application import app
from flask import render_template, request, jsonify
from includes.implement_ML import evaluate_recording, assign_class
import os

#create a route to run the simple app 
@app.route("/")
#below, we make another one off of the root route
@app.route("/index")
#each of these things are called "decorators"
@app.route("/home")
#all of the above are aliases for the others 

def index():
    #return "<h1> Hello, World!!! Testing AGAIN </h1>"
    #to replace the above, we will use the render_template function
    #you can pass additional parameters to render_template
    return render_template("index.html", index = True)


#make our other functions for other tabs in our site 
@app.route("/about")
def about():
    #the final parameter is a step towards highlighting the tab that is open
    return render_template("about.html", about = True)

@app.route("/rate")
def rate():
    #the final parameter is a step towards highlighting the tab that is open
    return render_template("rate.html", rate = True)

#process the audio    
@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']
        #save the upload to a file locally
        f.save(f.filename)  
        #from that file, make a prediction
        pred = evaluate_recording(f.filename)[0][0]
        
        percentage = pred - (-2) / 4
        pred_class = assign_class(pred)
        
        #remove the file locally
        os.remove(f.filename)
        
        return render_template("results.html", name = f.filename, pred = pred, percentage = percentage, pred_class = pred_class)  
    

    
    