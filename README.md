# 2020-Election-Forecast
In this project, I used python to generate candidate win probabilities in the 2020 presidential election as well as generate state-by-state win probabilities. 
I built on my data gathering and file processing experience, while experimenting with new method of data analysis in python. 
This project revolves around building normal distributions for margin on a state-by-state basis, as well as on a national basis.
Using national error relative to the expected popular vote outcome, I can build a state-by-state normal distribution adjusted for this error.
At this point, win probabilities are determined for each state, and the election is simulated.
I run 10,000 simulations of the presidential, outputing candidate win probabilities and average electoral votes to the module, and writing a state-by-state probability breakdown as well as a electoral outcome distribution to separate txt files. 
This was an exercise in rapid design and implementation of a complex yet elegant model to fit within the time constraints of a rapidly-approaching election.
It was a particularly valuable exercise in applying new data analysis techniques through built-in python functionality.
