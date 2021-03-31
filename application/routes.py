#ALL of the routes should be kept in this file 

#import app from the __init__ file 
from application import app
from flask import render_template, request
from includes.implement_ML import evaluate_recording, assign_class

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
@app.route('/results', methods = ['GET','POST'])  
def results():  
    if request.method == 'POST':  
        f = request.files['file']
        #save the upload to a file locally
        f.save(f.filename)  
        
        #from that file, make a prediction
        pred, valid_input = evaluate_recording(f.filename)
                
        #pred = evaluate_recording("http://drive.google.com/uc?export=view&id=114sSMDHPLrbjoj6xFDRtmAeVSqrOPAZk")
        if valid_input:
            pred_class = assign_class(pred)
            
            pred = pred[0][0]
            percent = 25 * (pred + 2)
            if percent > 100:
                percent = 100
            elif percent < 0:
                percent = 0
        
        
        else:
            percent = 0
            pred_class = "invalid"
            
        ret_val = render_template("results.html", submitted = True, valid_input = valid_input, name = f.filename, pred = round(percent, 3), pred_class = pred_class, results = True)  
    
    else: #if entering the results page by clicking 

        ret_val = render_template("results.html", submitted = False, valid_input = False, name = "no_file", pred = "no_file", pred_class = "no_file", results = True)
        
            
    return ret_val