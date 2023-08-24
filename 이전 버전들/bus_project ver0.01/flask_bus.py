from flask import Flask, render_template, request, jsonify, json
import package.pkg_bus as pb
import package.T_func as T_fn
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("bus_home.html")

# 화면2 - 버스정류장을 검색하면 어느방향으로 갈지 선택할 수 있는 창이 열림
@app.route("/result", methods = ["GET"])
def result():
    start = int(datetime.today().strftime("%S"))
    bus_station_name = request.args.get("bus_station_name") # 홈 화면에서 버스 정류장 명을 받아옴
    arsno_list = pb.get_bus_id(bus_station_name) # 버스 정류장 명을 바탕으로 정류소번호(arsno)를 가져옴
    
    info_lists = pb.get_bus_info_ByArsno(arsno_list) # 정류소번호(arsno)를 바탕으로 노선id를 가져옴
    lineid = []  # 해찬 코드에서는 이게 lineid로 사용되었었음.
    lineid = pb.get_lineid(info_lists)

    arsno = [] # 노선id들을 바탕으로 각 버스의 현재 입력된 정류장id와 다음정류장 이름을 가져옴
    arsno.append(pb.get_bus_arsno(lineid, bus_station_name))
        #get_bus_arsno : API 3번
        # => API로 정보들 받아와서, 정류장 이름하고 하나하나 대조해서 맞는거 나오면 그 다음 정류장 이름 받아오게 하는 함수..
    ##############################pb.get_bus_arsno(lineid_list, bus_station_name)
    #         # arsno.append(lineid[i][j])
    # # 여기까지 11초~13초
    # # 정류장id와 정류장 이름이 몇 번 나왔는지 카운트 해줌
    counts = {} # 다음 정류장을 어떤것이 많이 나왔는지 카운트 함
    for lists in arsno:
        for dictionaries in lists:
            for key, value in dictionaries.items():
                pair = (key, value)
                counts[pair] = counts.get(pair, 0) + 1 # 뭔지 모름 나중에 해석해봐야함
    # 여기까지 위와 거의 동일
    # # 그 중에서 정류장id가 다른것 중 가장 높은 카운트만 분류해줌 - 다음 정류장으로 어떤 정류장이 더 많은지 알 수 있음
    result_dict = {} # counts에서 가장 많이 나온 정류장 두 개를 추려냄
    # 근데 5, 3, 3으로 같은거 두개 있으면 어떤거 두개를 가져올지 해결해야함. 
    for (numeric_part, name_part), count in counts.items():
        if numeric_part in result_dict:
            if count > result_dict[numeric_part][1]:
                result_dict[numeric_part] = (name_part, count)
        else:
            result_dict[numeric_part] = (name_part, count)

    # Convert the result_dict into a list of dictionaries with the desired format
    result_list = [{"arsno": numeric_part, "bstopnm": name_part} for numeric_part, (name_part, count) in result_dict.items()] # 뭔지 모름 나중에 해석해봐야함
    
    #result_list =[{'bstopid': '01001', 'bstopnm': '동일파크맨션'}, 
    #              {'bstopid': '01002', 'bstopnm': '시민아파트'}]

    # result_list를 json으로 덤핑해서 웹으로 뿌려준다.
    result_list = json.dumps(result_list, ensure_ascii=False)


    return render_template("bus_result.html",result_list=result_list, bus_station_name = bus_station_name) #결과와 정류장 이름 보냄
    #return render_template("bus_result.html",result_list=result_list)
    # end = int(datetime.today().strftime("%S"))
    # return render_template("bus_sample.html", lineid=result_list, time = end-start)

@app.route("/final_result", methods = ["POST"])
def final_result():
    value = request.form.get('value')  # value : 클릭한 버튼(다음정류장)의 arsno
    temp_list = []
    temp_list = pb.get_finalinfo_byValue(value)
    send_list = json.dumps(temp_list, ensure_ascii=False)


    return render_template("bus_final_result.html", value = value, raw_list=send_list)


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)