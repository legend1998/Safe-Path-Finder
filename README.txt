__________________ This is the user guide __________________


*********************** first page - HomePage  ************************************


    first in the top a form is present it has ----->
        
        source - (string field) this field will be automatically filled when you click on the map 

        destination - (string field) this field also filled automatically 

        WARNING - don't fill above field by self.

        Grid Size - (slider)  use this slider to choose the grid size default is 0.1 and its range is 1(6) to 0.02(20) 

        threshold - (number)  use this field to select the proper crime threshold what you want.

        submit - (button) after completing the form click this submit button to get the result as path,
                 if any errors happen it will above th map.
        
        reset  - (button) to reset the form click this button.

    second it shows the Montreal central surounded by the blue color box inside map

        Use - user have to click on this map to select the source and destination
                after first click it will automatically fill source field in the above form
                and after second click it will automatically fill destination field.

NOTE :::

1. if the destination or source is surrounded by higher crime rate than after 10 seconds
    it will show above the map.

2. This uses A* algorithm to find the path and it is optimal as it estimates
    equal to the actual cost not mre than actual.



*************************  2nd page result Page --->  *********************************************




first is navbar contains home and cluster wise area(third page) -click here to get the exact location of each crime.

after that there is two part 

    first is showing map with path from source to destination with grided area,

    green marker for source and red marker for destination

    if grid color is red it shows local area has more crime than threshold or dangerous
    and white grid shows local area has less crime than threshold or area is optimal

     NOTE :::
    if you click on each grid a popup will appear with crime rate of that local area

        it has also a sidebar where it shows

            total cost = cost for moving from source to destination
            avg =        avg of the all crime in grid
            std daviation = std daviation of the crime of all 


    second is showing two different graph 

        one for crime rate with different color on each grid or local area

        and second is generated with help of threshold, in which yellow contains more crime 
        while blue contains less crime



************************** end ***********************************