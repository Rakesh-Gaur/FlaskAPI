from flask import Flask, jsonify, request
from utils.elastic_conn import connect_db
from utils.schedule_post import schedule_task
from config import Config


app = Flask(__name__)

es_db = connect_db()

# Get API 
@app.route('/get_data', methods=['GET'])
def get_data():
    all_data = []
    try:
        match_all = {
                        "size": 100,
                        "query": {
                            "match_all": {}
                        }
                    }
        resp = es_db.search(
                            index = Config.DB_INDEX,
                            body = match_all,
                            scroll = '3s' 
                        )

        # keep track of pass scroll _id
        old_scroll_id = resp['_scroll_id']
        while len(resp['hits']['hits']):

            all_data.extend([record['_source'] for record in resp['hits']['hits']])
           
            resp = es_db.scroll(
                                scroll_id = old_scroll_id,
                                scroll = '3s'
                            )
            old_scroll_id = resp['_scroll_id']
        return jsonify({
            "success" : True,
            "messsage" : "Records fetched successfully.",
            "status_code": 200,
            "data": all_data,
            "total_result" : len(all_data)
        })
    except Exception as e:
        return jsonify({
            "success" : False,
            "messsage" : "Something went wrong.",
            "status_code": 500
        })

# Get API with parameter (roll_no and name)
@app.route('/get_student', methods=['GET'])
def get_student():
    if request.args.get('roll_no') and request.args.get('name'):
        roll_no = request.args.get('roll_no')
        name = request.args.get('name')
        _query = {
                "query": {
                    "bool": {
                        "must": [{"match": {"name": name}},
                                 {"match": {"roll_no": roll_no}
                        }]
                    }
                }
            }    
        try:
            student = es_db.search(index=Config.DB_INDEX, body=_query)                
            return jsonify({
                "success" : True,
                "messsage" : "Record fetched successfully.",
                "status_code": 200,
                "data":student._body['hits']['hits'][0]['_source']
            })
        except Exception as e:
            return jsonify({
                "success" : False,
                "messsage" : "Student record not found.",
                "status_code": 404
            })    
    else:
        return jsonify({
            "success" : False,
            "messsage" : "roll_no and name are required.",
            "status_code": 400
        })


@app.route('/delete_data', methods=['DELETE'])
def delete_data():
    results = es_db.delete_by_query(index=Config.DB_INDEX, body={"query": {"match_all": {}}})
    return jsonify({
            "success" : True,
            "messsage" : "Record deleted successfully.",
            "status_code": 200
        })

# POST API for insert student records
@app.route('/insert_data', methods=['POST'])
def insert_data():
    try:
        if not request.json.get('roll_no'):
            return jsonify({
                "success" : False,
                "messsage" : "roll_no is required.",
                "status_code": 400
            })
        name = request.json.get('name')
        gender = request.json.get('gender')
        roll_no = request.json.get('roll_no')
        nationality = request.json.get('nationality')

        body = {
            'name': name,
            'gender': gender,
            'roll_no': roll_no,
            'nationality': nationality
        }
        try:
            if es_db.get(index=Config.DB_INDEX, id = roll_no):
                return jsonify({
                    "success" : False,
                    "messsage" : "Record already exist.",
                    "status_code": 302
                })

        except Exception as e:
            pass

        result = es_db.index(index=Config.DB_INDEX, id=roll_no, body=body, request_timeout=Config.TIMEOUT)
        if result.body:
            return jsonify({
                "success" : True,
                "messsage" : "Record successfully created.",
                "status_code": 200
            })
    except Exception as e:
        return jsonify({
            "success" : False,
            "messsage" : "Something went wrong.",
            "status_code": 500
        })

if __name__ == '__main__':
    schedule_task()
    app.run(debug=Config.DEBUG, host=Config.SERVER_HOST)
