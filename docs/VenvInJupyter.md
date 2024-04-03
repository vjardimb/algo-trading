# Using a Virtual Environment in a Jupyter Notebook

Although jupyter can directly identify your venv when changing the Jupyter kernel, prior steps are still needed in order
to properly use the python packages installed in it.

As shown in the requeriments.txt file, the ipykernel needs to be included in your venv. If it's not, do:

```bash
pip install ipykernel==6.29.4
```

Next you need to add your virtual environment to Jupyter by typing:

```bash
python -m ipykernel install --user --name=<venv-name>
```

This should print the following:

```bash
Installed kernelspec <venv-name> in /home/user/.local/share/jupyter/kernels/<venv-name>
```

In this folder you will find a kernel.json file which should look the following way if you did everything correctly:

```json
{
 "argv": [
  "/home/user/anaconda3/envs/<venv-name>/bin/python",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": <venv-name>,
 "language": "python"
}
```

Now, you can use your installed packages in a jupyter notebook. Just remember to choose the right kernel before running 
your notebook.