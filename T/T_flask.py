from flask import Flask, render_template, request, json
import T_func

input_station_name = ""

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("T_home.html")

@app.route("/result", methods=["GET"])
def res():
    global input_station_name
    input_station_name = request.args.get("input_station_name")
    arsnos = T_func.get_line_id(input_station_name)
    # arsnos : 정류소명에 해당하는 arsno, nodenm들이 담겨있는 list
    if type(arsnos) == str: # arsnos 아무것도 못받아왔으면 메시지 출력
        return arsnos

    # 받아온 arsno list랑 정류소 이름을 가지고 버스도착시간 뽑아내자
    info_lists = T_func.get_businfo_byArsno(arsnos, input_station_name)
    get_list = T_func.get_needed_info(info_lists)
    # temp_list = []
    # for i in range(len(info_lists)):
    #     temp_list.append(info_lists[i]['data'])
    json_list = json.dumps(info_lists, ensure_ascii=False)

    return render_template("T_result.html", info_list = json_list, st_nm = input_station_name, gt_list = get_list)

@app.route("/result2", methods=["GET"])
def res2():
    pass

if __name__==("__main__"):
    app.run(host="localhost", port=5000, debug=True)