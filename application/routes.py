#ALL of the routes should be kept in this file 

#import app from the __init__ file 
from application import app
from flask import render_template, request
from includes.implement_ML import evaluate_recording, assign_class

#the following are for the image in the results:
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt 


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



def plot_results(percent, pred_class):
    # set up the figure
    fig = plt.figure(edgecolor = 'black')
    ax = fig.add_subplot(1,1,1)
    ax.set_xlim(-2,102)
    ax.set_ylim(0,6)
    
    # draw lines
    xmin = -2
    xmax = 102
    y = 5
    height = 0.5
    
    plt.hlines(y, xmin, xmax)
    plt.vlines(xmin, y - height / 2., y + height / 2.)
    plt.vlines(xmax, y - height / 2., y + height / 2.)
    plt.vlines(50, y - height / 5., y + height / 5.)
  
    # draw a point on the line
    plt.plot(percent, y,'ro',  ms = 15, color = 'orange')
    #change the fonts 
    body_font = {'fontname':'Arial'}
    header_font = {'fontname':'Helvetica'}
    
    
    # add numbers
    plt.text(xmin - 1, y, 'our ears are bleeding', horizontalalignment='right', **body_font, fontsize = 8)
    plt.text(xmax + 1, y, 'you should go on American Idol!', horizontalalignment='left', **body_font, fontsize = 8)
    plt.text(50, y - 1, 'not too bad, \n but nothing to write home about...', horizontalalignment='center',**body_font, fontsize = 8)
    plt.text(50, y - 2, "We rate you a {} / 100".format(percent), horizontalalignment='center',**header_font,  fontsize=12)
    plt.title("You sound {}!".format(pred_class), **header_font, fontsize=18)
    
    
    #plt.suptitle(title_string, , fontsize=18)
    #plt.title(subtitle_string, fontsize=10)
    plt.axis('off')
    #adjust the formatting 
    plt.tight_layout()
    
    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    
    # Encode PNG image to base64 string
    png_image_encoded = "data:image/png;base64,"
    png_image_encoded += base64.b64encode(pngImage.getvalue()).decode('utf8')
    
    #plt.show()
    
    #save the photo to the directory we are in
    #plt.savefig("./score_image.png")
    
    return png_image_encoded
    
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
                
            #create an image from the recording 
            image_prepared = plot_results(round(percent,3), pred_class)
            
            ret_val = render_template("results.html", submitted = True, valid_input = valid_input, name = f.filename, pred = round(percent, 3), pred_class = pred_class, image = image_prepared, results = True)  

        
        else:
            percent = 0
            pred_class = "invalid"
            
            #we won't have an image created if the uploaded file was corrupted
            ret_val = render_template("results.html", submitted = True, valid_input = valid_input, name = f.filename, pred = round(percent, 3), pred_class = pred_class, results = True)  
    
    else: #if entering the results page by clicking 

        ret_val = render_template("results.html", submitted = False, valid_input = False, name = "no_file", pred = "no_file", pred_class = "no_file", results = True)
        
            
    return ret_val