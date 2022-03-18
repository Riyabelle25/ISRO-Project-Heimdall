#  MP_ISRO_T8
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Contents
- [Overview](#overview)
- [Features](#features)
- [Download](#download)
- [Tech Stack](#tech-stack)
- [Development](#development)


## Overview
**Project Heimdall** is a stand-alone web-based application using <a href="https://streamlit.io/">Streamlit.io</a> to identify and categorize X-ray bursts. 

Submission for the Inter-IIT Tech Meet's Mid Prep event: ISRO'S Web-Based Automatic Identifiaction Of Solar Bursts In X-Ray Light Curves 

Team: **MP_ISRO_T8**

Visit 


### Visit our deployed webapp <a href="https://project-isro-heimdall.herokuapp.com/">here</a> <br/>
### To setup locally🔧⚙️
<br/>

Create a virtual environment, using:
```
virtualenv venv
```
To activate virtual environment:
```
source venv/bin/activate
```
Now, after activating the virtual environment we need to install dependencies used for our project:
```
pip install -r requirements.txt
```
### To run app 🏃 
```
streamlit run app.py
```

## Demo 

First screen has an upload option for uploading .lc files, which will be used to extract data using <a href="https://www.astropy.org/">Astropy</a>, and further will be processed to draw graphs.
![image](https://user-images.githubusercontent.com/59011370/159001786-a3c85b1b-b82e-4317-ae21-148c4ece3fe4.png)

Tadaa 🥳 We are done 🥁

Finally, we have plotted our graphs and tables, with information about them as shown below:

![raw_data_input](https://user-images.githubusercontent.com/59011370/158999454-13fde19d-3b5b-4be6-8877-76d1abff66cd.png)
![noise_red](https://user-images.githubusercontent.com/59011370/158999452-a927a40c-22ad-4e4e-9872-ee4201182e23.png)
![peaks](https://user-images.githubusercontent.com/59011370/158999453-2d0488c5-ab69-4e1d-81a4-25b22c6cb0c8.png)
![analysis](https://user-images.githubusercontent.com/59011370/158999445-1166537e-afde-4dc5-9ce4-ede61d576e1b.png)

## Why use our app?

Our web app has some beautiful dynamic graphs that are interactive, means draggable and scrollable. It also display coordinates on hovering, making the analysis very easy. <br/>
![gif](https://user-images.githubusercontent.com/59011370/159001213-2f3d8976-0ce8-4bea-abb7-5f154fbe6bdd.gif)
<br/>

Made with ❤️ by **Luminaires**
