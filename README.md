# cms_ivy_tool
this tool will support checking cms file when exporting from ivy

you need to install package in requirements file with command below:

pip install -r requirements.txt

after installing all dependences sucessfully! To run application please run command :  

python pythonscript.py -f "excel_file_you_want_to_compare.xls" -p "path_to_cms_folder"

'-f' option : the .xls you want to compare
'-p' option : the path to cms folder

example:
python pythonscript.py -f "desk_individual_customer_abc.xls" -p "C:/WORK/workspace/desk_individual_customer_abc/cms"
Note : You could put the desk_individual_customer_abc.xls file with the same with script or you absulute path