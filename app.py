import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from logic.mudgee_parser import Parser
from logic.comparison import MudComparer
from logic.mongo_dal import MongoDal
import logic.constants as constants
from logic.mud_generalization import MudGeneralization
import uuid


app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = constants.UPLOAD_FOLDER
app.secret_key = 'super secret key'
mongo_dal = MongoDal('MudRun', 'muds')


@app.route('/')
@app.route('/index')
def index():
    title = 'MudRun - parse and compare muds'
    return render_template('index.html', title=title)

@app.route('/addmud')
def add_mud():
    return render_template('addmud.html')

@app.route('/newindex')
def newindex():
    return render_template('newindex.html')


@app.route('/mudscoordinator')
def mudscoordinator():

    columns = [
        {
            "field": 'state',
            "checkbox": True,
            "align": 'center',
        },
        {
            "field": "mud_name",
            "title": "mud_name",
            "sortable": True,
        },
        {
            "field": "device_type",
            "title": "device type",
            "sortable": True,
        },
        {
            "field": "device_name",
            "title": "device_name",
            "sortable": True,
        },
        {
            "field": "dev_location",
            "title": "device location",
            "sortable": True,
            "align": 'center',
            "clickToSelect": False,
            "formatter": "countryFormatter"
        },
        {
            "field": 'operate',
            "title": 'Mud Operate',
            "align": 'center',
            "clickToSelect": False,
            "events": "window.operateEvents",
            "formatter": "operateFormatter"
        }
    ]

    muds_data = mongo_dal.read_all()
    data = prepare_mud_data(muds_data)
    return render_template("mudscoordinator.html", data=data, columns=columns)

@app.route('/getMudContent', methods = ['GET', 'POST'])
def present_mud_content():
    mud_id = request.args.get('mud_id')
    condition = { "_id" : '{0}'.format(mud_id) }
    mud_data = mongo_dal.read(condition)
    mud_content = mud_data["mud_content"]

    return mud_content


def prepare_mud_data(muds_data):
    documents_length = muds_data.count()
    data = {"total": documents_length,
            "totalNotFiltered": documents_length,
            "rows": []
           }

    for mud_document in muds_data:
        filtered_dict = {k: v for k, v in mud_document.items() if k in constants.DATA_TO_COLUMNS}
        data["rows"].append(filtered_dict)

    return data


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in constants.ALLOWED_EXTENSIONS


@app.route('/uploadMud', methods = ['GET', 'POST'])
def upload_mud():
    # check if the post request has the file part
    if 'mud_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    mud_file = request.files.get('mud_file')

    if mud_file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if mud_file and allowed_file(mud_file.filename):
        mud_content = mud_file.read()
        mud_filename = secure_filename(mud_file.filename)
        mud_file_path = os.path.join(app.config['UPLOAD_FOLDER'], mud_filename)
        mud_file.stream.seek(0)
        mud_file.save(mud_file_path)
    else:
        return "Wrong file format"

    data = request.form.to_dict()
    data['mud_file_path'] = mud_file_path
    data['mud_content'] = mud_content
    data['_id'] = str(uuid.uuid4())

    # insert the given data in to the DB
    mongo_dal.insert(data)

    # redirect to the main page of the app
    return redirect(url_for('mudscoordinator'))


@app.route('/compare', methods=['GET', 'POST'])
def compare_muds():
    first_mud_path = request.form.get('first_mud_path')
    second_mud_path = request.form.get('second_mud_path')
    first_mud_name = request.form.get('first_mud_name')
    second_mud_name = request.form.get('second_mud_name')
    first_mud_location = request.form.get('first_mud_location')
    second_mud_location = request.form.get('second_mud_location')
    device_type = request.form.get('device_type')
    device_name = request.form.get('device_name')

    compare_object = parse_muds_and_compare(first_mud_path, second_mud_path)
    two_directional_dt = compare_object[0]
    compare_metrices = compare_object[1]
    identical_rules = compare_object[2]
    non_similar_rules = compare_object[3]
    similar_rules = compare_object[4]
    related_rules = compare_object[5]
    relations_graph = compare_object[6]

    mud_genaralization = MudGeneralization(identical_rules, non_similar_rules[0], non_similar_rules[1],
                         non_similar_rules[2], non_similar_rules[3], similar_rules[0], similar_rules[1],
                         first_mud_name, first_mud_location, second_mud_name, second_mud_location, device_type, device_name, mongo_dal)

    head, first_file_name = os.path.split(first_mud_path)
    head, second_file_name = os.path.split(second_mud_path)

    return render_template('new_comparison.html', first_direction_dt=two_directional_dt[0],
                           second_direction_dt=two_directional_dt[1], first_mud_filename=first_file_name,
                           second_mud_filename=second_file_name, compare_metrices=compare_metrices,related_rules=related_rules,
                           nodes=relations_graph[0], edges=relations_graph[1],
                           first_mud_location=first_mud_location, second_mud_location=second_mud_location)


@app.route('/UploadAndCompare', methods=['GET', 'POST'])
def upload_and_compare():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'first_mud' not in request.files and 'second_mud' not in request.files:
            flash('No file part')
            return redirect(request.url)

    first_mud = request.files['first_mud']
    second_mud = request.files['second_mud']

    # if user does not select file, browser also
    # submit an empty part without filename
    if first_mud.filename == '' or second_mud.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if first_mud and allowed_file(first_mud.filename) and second_mud and allowed_file(second_mud.filename):
        first_mud_filename = secure_filename(first_mud.filename)
        second_mud_filename = secure_filename(second_mud.filename)
        first_mud.save(os.path.join(app.config['UPLOAD_FOLDER'], first_mud_filename))
        second_mud.save(os.path.join(app.config['UPLOAD_FOLDER'], second_mud_filename))

        compare_object = parse_muds_and_compare(first_mud_filename, second_mud_filename, False)
        two_directional_dt = compare_object[0]
        compare_metrices = compare_object[1]
        related_rules = compare_object[2]
        relations_graph = compare_object[3]

        '''
        return render_template('comparison.html', first_direction_dt=two_directional_dt[0],
                               second_direction_dt=two_directional_dt[1], first_mud_filename=first_mud_filename,
                               second_mud_filename=second_mud_filename, compare_metrices=compare_metrices)
        '''

        a = related_rules[0].keys()
        for ace in a:
            print(ace.name)


        return render_template('new_comparison.html', first_direction_dt=two_directional_dt[0],
                           second_direction_dt=two_directional_dt[1], first_mud_filename=first_mud_filename,
                           second_mud_filename=second_mud_filename, compare_metrices=compare_metrices, related_rules=related_rules,
                           nodes=relations_graph[0], edges=relations_graph[1])

    else:
        return "Wrong file format"


def parse_muds_and_compare(first_mud_file, second_mud_file, full_path=True):

    if full_path:
        first_mud_file_path = first_mud_file
        second_mud_file_path = second_mud_file
    else:
        first_mud_file_path = os.path.join(constants.UPLOAD_FOLDER, first_mud_file)
        second_mud_file_path = os.path.join(constants.UPLOAD_FOLDER, second_mud_file)

    # first mud
    first_mud_parser = Parser(first_mud_file_path)
    first_mud_parser.parse_metadata()
    first_mud_parser.parse_access_lists()

    # second mud
    second_mud_parser = Parser(second_mud_file_path)
    second_mud_parser.parse_metadata()
    second_mud_parser.parse_access_lists()

    # compare muds
    mud_comparer = MudComparer(first_mud_parser.mud, second_mud_parser.mud)
    mud_comparer.compare_muds()
    nodes, ages = mud_comparer.create_relations_graph()

    # calculates compare metrices
    first_metric = mud_comparer.odd_rules_out_of_total_rules()
    second_metric = mud_comparer.odd_rules_without_similar_rules_out_of_total_rules()
    third_metric = mud_comparer.generalization_rating()

    metrices = (first_metric, second_metric, third_metric)
    identical_rules = mud_comparer.final_identical_dt
    related_rules = (mud_comparer.first_from_related_aces, mud_comparer.first_to_related_aces)
    non_similar_rules = (mud_comparer.non_similar_first_from_aces, mud_comparer.non_similar_first_to_aces,
                         mud_comparer.non_similar_second_from_aces, mud_comparer.non_similar_second_to_aces)
    similar_rules = (mud_comparer.similar_first_from_related_aces, mud_comparer.similar_first_to_related_aces)
    graph = (nodes, ages)

    return mud_comparer.two_directional_comparison, metrices, identical_rules, non_similar_rules, \
           similar_rules, related_rules, graph

    '''
    return mud_comparer.two_directional_comparison, (first_metric, second_metric, third_metric),\
            (mud_comparer.first_from_related_aces, mud_comparer.first_to_related_aces), (nodes, ages)
    '''


'''
def compare_muds(first_mud_filename, second_mud_filename):
    # first mud
    first_mud_filename = os.path.join(app.config['UPLOAD_FOLDER'], first_mud_filename)
    first_mud_parser = Parser(first_mud_filename)
    first_mud_parser.parse_metadata()
    first_mud_parser.parse_access_lists()

    # second mud
    second_mud_filename = os.path.join(app.config['UPLOAD_FOLDER'], second_mud_filename)
    second_mud_parser = Parser(second_mud_filename)
    second_mud_parser.parse_metadata()
    second_mud_parser.parse_access_lists()

    first_direction_dt = first_mud_parser.mud.compare_muds(second_mud_parser.mud)
    second_direction_dt = second_mud_parser.mud.compare_muds(first_mud_parser.mud)
    return (first_direction_dt, second_direction_dt)
'''

if __name__ == '__main__':
    app.run()
