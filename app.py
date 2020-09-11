from flask import Flask, render_template,redirect,request,url_for,flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField,IntegerField
from wtforms.validators import InputRequired
from operation import get_cord,get_geojson_grid,dynamic_grid,with_threshold,astar
import folium
from folium import plugins
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from folium.plugins import MarkerCluster
app = Flask(__name__)
app.config['SECRET_KEY']='verysecretnoonecanknowit'
app.debug=True


# global variable 
position=[]
grid_size=6
threshold=80


# form for user input
class locationinput(FlaskForm):
    source=StringField('source',validators=[InputRequired()])
    destination =StringField('destination',validators=[InputRequired()])


@app.route('/')
def map():
    form=locationinput()
    return render_template("map.html",form=form)

@app.route('/',methods=['POST'])
def path():
    form=locationinput()
    if not form.validate_on_submit:
        redirect('/')
    #extract the cordiantes from the input
    src=form.source.data.split()
    dest=form.destination.data.split()  
    src[0]=float(src[0][7:src[0].find(',')])
    src[1]=float(src[1][0:len(src[1])-1])
    dest[0]=float(dest[0][7:dest[0].find(',')])
    dest[1]=float(dest[1][0:len(dest[1])-1])
    position.clear()

    global grid_size,threshold
    grid_size=int(request.form["grid_size"])
    threshold=int(request.form["threshold"])

    # generate the multipyer to make the grid according to the data or can be said as reshaping

    multiplyer=grid_size/4
    multiplyer*=100

    src[0]-=45.49
    src[1]+=73.590
    dest[0]-=45.49
    dest[1]+=73.590

    src[0]*=multiplyer
    src[1]*=multiplyer
    dest[1]*=multiplyer
    dest[0]*=multiplyer

    src[0]=int(src[0])
    src[1]=int(src[1])
    dest[0]=int(dest[0])
    dest[1]=int(dest[1])

    position.append((src[0],src[1]))
    position.append((dest[0],dest[1]))
    #if marked marker is outside the grid then again enter valid input
    if(src[0]<0 or src[1]<0 or src[0]>=grid_size or src[1]>=grid_size or dest[0]<0 or dest[1]< 0 or dest[0]>=grid_size or dest[1]>=grid_size):
        flash("due to blocks no path is found plese select inside the map","danger")
        return redirect('/')
    return redirect(url_for('result'))



@app.route('/test',methods=['POST','GET'])
def result():

    try:
        x=position[0]
        y=position[0]
    except:
        flash("select source and destination",'danger')
        return redirect(url_for('path'))

    # make the map

    m=folium.Map(location=[45.51,-73.57] ,zoom_start=1)
    m.fit_bounds([[45.49,-73.59],[45.49,-73.55],[45.53,-73.55],[45.53,-73.59]],max_zoom=20)
    m.add_child(folium.LatLngPopup())

    # get the cordinates
    cordinates=get_cord()

    #draw the grids
    grid=get_geojson_grid(n=grid_size)

    # get the base (included all the information of each gridbox and get the mean)
    base,mean=dynamic_grid(cordinates=cordinates,grid_size=grid_size)

    #get the maze (contains the block area and less crime area) with std daviation
    maze,std_dev=with_threshold(base=base,threshold=threshold,grid_size=grid_size)
    std_dev=round(std_dev,2)
    
    # draw the grid
    for i, geo_json in enumerate(grid):
        row=int(i/grid_size)
        col=int(i%grid_size)
        color =plt.cm.Reds(maze[row][col])
        color= mpl.colors.to_hex(color)
        gj = folium.GeoJson(geo_json,
                            style_function=lambda feature, color=color: {
                                                                            'fillColor': color,
                                                                            'color':"black",
                                                                            'weight': 2,
                                                                            'dashArray': '5, 5',
                                                                            'fillOpacity': 0.55,
                                                                        })
        popup = folium.Popup("total crime:{}".format(base[row][col]))
        gj.add_child(popup)
        m.add_child(gj)
    #path plotting
    # get path with cost
    path_with_cost = astar(maze,position[0],position[1])
    data=None
    if  path_with_cost:
        if type(path_with_cost) is str:
            flash(message="due blocks no path is found plese change threshold or grid size to get there",category="success")
            return redirect('/')
        else:
            folium.PolyLine(path_with_cost[0]).add_to(m)
            folium.Marker(path_with_cost[0][0] ,icon=folium.Icon(color='green')).add_to(m)
            folium.Marker(path_with_cost[0][len(path_with_cost[0])-1],icon=folium.Icon(color='red')).add_to(m)
            data={'cost':round(path_with_cost[1],2),'mean':round(mean,2),'std_dev':round(std_dev,2),'threshold':threshold}
    else:
        flash("time is up the optimal path is not found","danger")
        return redirect("/")
    m.save("templates/out.html")
    return render_template("index.html",data=data)

@app.route('/cluster')
def show():
    return render_template('cluster.html')



if __name__ == "__main__":
    app.run(debug=True)