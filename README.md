TARGET AD
==============================

Insight Project.
Predicting Alzheimer’s Disease for effective clinical trials. 
Uses data from NACC https://www.alz.washington.edu/WEB/researcher_home.html
Predicts from a subset of patients with Mild Cognitive Impairment who is most likely to develop Alzheimer's
(random forest classifier) and time to diagnosis (random survival forest)


Project Organization
------------

    ├── LICENSE
    ├── app.py		   <- Where the dash app lives
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         and a short `_` delimited description, e.g.
    │                         `1.0_jqp_initial_data_exploration`.
    │           
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   
    │
   


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
