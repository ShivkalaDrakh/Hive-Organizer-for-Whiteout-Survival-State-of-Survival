# Hive Organizer</center> 
### A tool for Whiteout Survival and State of Survival

The Hive Organizer is a tool for alliance leaders and co-leaders to optimize and organize the hive of the alliance.
Easy to build from scratch, load a predefined hive, edit your own, and allocate your alliance members!

Move members around by DnD there cities, enter terrain obstacles or move a whole bunch of buildings with one simple
action!
### Build your Hive
Add Cities, Flags, HQ, Trap and Obstacles (Rocks) 
![Picture of sample Hive](Screenshot%20Setup.png)
<video src="https://github.com/user-attachments/assets/7c7a467b-9162-4bcf-947a-20a0cebf8be1"/>
### Assign Member Positions
Just Click on the Member name and the city position (in Assign Mode)
![Picture of sample Hive with assigned Members](Screenshot%20Assign.png)

The City is then assigned to the Member, the number on the City corresponding to the number in the Member List. After assignining, the next unassigned member will be selected (V0.2.3) so that you can just click through the cities without the need to selecting the member name anew everytime.

A Mouse-over over the City shows the name of the alliance member. Overwritting and re-positioning is just as easy.

Also by klicking on the Member name on the list, the city in the Hive is highlighted, making it much easier to find a member in the Hive!
<video src="https://github.com/user-attachments/assets/f4c41542-892d-4315-a686-26d2deba61eb"/>
### Different Zoom for clearer editing
Whether you need your whole Hive to be visible or prefer bigger blocks for member assignment or building, you can use different zoom settings
![picture of Zoom Mode](Screenshot%20zoom.png)

### Using differnt grid sizes
By left-clicking on the Grid button you can toggle the grid on and off. By right-clicking on the grid button, you can toggle the grid size between 6x6 (default) and 2x2.

### Re-build and modify
Whether you want to just move a few buildings around or a whole block of Cities and Flags, just right-click-drag 
an area and move the seleced buildings in one go.
![Select multiple Buildings](Screenshot%20Select.png)

![Move seleced Buildings](Screenshot%20Moved.png)

When building with flags, it is often important to see the complete covered area. To ease this, V0.2.3 introduced the possibility to show the covered area on top of the buildings.

![Show Floor on top of Buildings](Screenshot%20Top%20Floor.png)

### Isometric View
As the game has a 45° isometric view, it is not always easy to get the game grid correctly alligned with the buildings.
Therefore, the Hive can be displayed in Ismetric View to have the same orientation as in the game!
![Isometric View of the Hive, including Assignments](Screenshot%20Isometric.png)

And also in the isometric view you can choose different Zoom settings and print the Hive as a PNG file.
![Isometric View of the Hive in Zoom Mode, including Assignments](Screenshot%20Isometric_zoom.png)

### Trap and City Coordinates 
By entering the Trap Coordinates as given by the game, all grid coordinates are updated to those coordinates and all assignened member cities show the coordinates next to their name.
After finishing to put in the Trap Coordinates, selcect "Update Coordinates" from the Members List Config Menu!

### Additional Columns for Members List (V0.3)
In the Members List Config Menu you can select (currently) 3 additional columns to be displayed: 
"Power", "Level", and "Rank". They are displayed by default, but can be deselected in the Menu.

The values can be editied either right in the Hive Organizer or by editing either 
MembersList *.txt file or *.hb file in any text editor.
![Selection of additional Columns for Members List](Screenshot%20ML%20columns.png)

### Color Themes (V0.3)
Version 0.3 introduces Color Themes! The default theme is set to a palette resembling the one from WOS. But others can be found in the save folder.
You can also generate your own color palette!
![Selection of Colors for a building](Screenshot%20Color%20palette.png)
Each building type as well as the floor and the background can be changed via the "Colors" Menu and then saved using the "File" Menu.
The current palette is automatically saved with the Hive if you save the Hive!

You can also share your palette with others! Or send it to me and I will add it to the GitHub files!
![Using the "Colorful" palette theme](Screenshot%20Colorful.png)

## Getting started
You can either download 
* The Python code + the "hive" folder.
  Only standard libraries are used, so no need for any packages to be installed
* For Windows there is a single execuble file (![hive_organizer.exe](Executable/hive_organizer.exe)) in the
  "Executable" folder. Just download and run it!
  That's all you need for the Windows application.
  However, the App is obviously not in the Microsoft Store, so Windows will complain about unauthorized software.
  
### Just play with it
This is a very early version of the tool, so just try it out, and send me some feedback!
Whether it's a bug report, a feature you'd like to have added, general criticism or just a few nice words,
everything is appreciated!

Have Fun!

### Examples
An example Hive and example Member lists are in the "save" folder 
(automatic initial directory for all save and load functions)
