from flask import Flask, render_template, request, json
import package.pkg_bus as pb
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

serviceKey_w0 = "Zo8DtP0l1dZzEqd62aLF1nboaBPHPbRAHyy%2BFnTW1qj%2Fn%2FjvtQXUbaFWU7yvun2vmhoFRgAEAU7e7RyPN2CMzA%3D%3D"
base_url = f"https://apis.data.go.kr/6260000/BusanBIMS/busInfo?serviceKey={serviceKey_w0}"

@app.route("/")
def start():
    return render_template("app.html")

@app.route("/app_bus", methods=['GET', 'POST'])
def bus_route():
    buses = []
    search_attempted = False  # 검색 시도를 기본값으로 False 설정

    if request.method == 'POST':
        search_attempted = True  # 검색을 시도했을 때 True로 변경
        bus_number_query = request.form.get('bus_number')
        url = f"{base_url}&lineno={bus_number_query}"

        content = requests.get(url, verify=False).content
        soup = BeautifulSoup(content, 'html.parser')

        items = soup.find_all('item')
        for item in items:
            bus = {
                'buslinenum': item.find('buslinenum').text if item.find('buslinenum') else '',    # 노선번호
                'bustype': item.find('bustype').text if item.find('bustype') else '',             # 버스종류
                'startpoint': item.find('startpoint').text if item.find('startpoint') else '',    # 기점
                'endpoint': item.find('endpoint').text if item.find('endpoint') else '',          # 종점
                'firsttime': item.find('firsttime').text if item.find('firsttime') else '',       # 첫 차
                'endtime': item.find('endtime').text if item.find('endtime') else '',             # 막 차
                'headway': item.find('headway').text if item.find('headway') else '',             # 배차간격(분)
                'headwaynorm': item.find('headwaynorm').text if item.find('headwaynorm') else '', # 배차간격(평일)
                'headwaypeak': item.find('headwaypeak').text if item.find('headwaypeak') else '', # 배차간격(출퇴근)
                'headwayholi': item.find('headwayholi').text if item.find('headwayholi') else ''  # 배차간격(휴일)
            }
            buses.append(bus)

    return render_template("app_bus.html", buses = buses, search_attempted=search_attempted)

@app.route("/<string:bus_num>")
def bus_detail(bus_num):
    url = f"{base_url}&lineno={bus_num}"
    content = requests.get(url, verify=False).content
    soup = BeautifulSoup(content, 'html.parser')

    items = soup.find_all('item')
    bus = {}
    bus_id = None
    for item in items:
        # 노선 번호가 정확히 일치하는 항목만 선택
        if item.find('buslinenum') and item.find('buslinenum').text == bus_num:
            bus_id = item.find('lineid').text
            bus = {
                'buslinenum': item.find('buslinenum').text,                                       # 노선번호
                'bustype': item.find('bustype').text if item.find('bustype') else '',             # 버스종류
                'startpoint': item.find('startpoint').text if item.find('startpoint') else '',    # 기점
                'endpoint': item.find('endpoint').text if item.find('endpoint') else '',          # 종점
                'firsttime': item.find('firsttime').text if item.find('firsttime') else '',       # 첫 차
                'endtime': item.find('endtime').text if item.find('endtime') else '',             # 막 차
                'headway': item.find('headway').text if item.find('headway') else '',             # 배차간격(분)
                'headwaynorm': item.find('headwaynorm').text if item.find('headwaynorm') else '', # 배차간격(평일)
                'headwaypeak': item.find('headwaypeak').text if item.find('headwaypeak') else '', # 배차간격(출퇴근)
                'headwayholi': item.find('headwayholi').text if item.find('headwayholi') else ''  # 배차간격(휴일)
            }
            break

    # 노선의 경로 정보를 가져오는 API
    route_url = f"https://apis.data.go.kr/6260000/BusanBIMS/busInfoByRouteId?serviceKey={serviceKey_w0}&lineid={bus_id}"
    route_content = requests.get(route_url, verify=False).content
    route_soup = BeautifulSoup(route_content, 'html.parser')

    route_items = route_soup.find_all('item')

    # 경로 정보의 개수에 따른 zfill 값을 설정 -> 자릿수만큼 0 채우기
    zfill_value = 3 if len(route_items) >= 100 else 2

    stops = [item.find('bstopidx').text.zfill(zfill_value) + " " + item.find('bstopnm').text for item in route_items if item.find('bstopnm')]
    bus['stops'] = stops  # 경로 정보를 'stops' 키에 추가

    return render_template("bus_detail.html", bus=bus)


@app.route("/home")
def home():
    return render_template("bus_home.html")

# 화면2 - 버스정류장을 검색하면 어느방향으로 갈지 선택할 수 있는 창이 열림
@app.route("/result", methods = ["GET"])
def result():
    bus_station_name = request.args.get("bus_station_name") # 홈 화면에서 버스 정류장 명을 받아옴
    if bus_station_name == "" :
        warning = "정류장 명을 적어주시기 바랍니다."
        return render_template("bus_home.html", warning=warning)
    
    arsnos = pb.get_bus_id(bus_station_name) # 버스 정류장 명을 바탕으로 정류장 id를 가져옴
    if len(arsnos) == 0 :
        warning = "입력하신 정류장 이름이 존재하지 않습니다. 다시 입력해 주시기 바랍니다."
        return render_template("bus_home.html", warning=warning)
    state = True;
    while state:
        try:
            lineid = pb.get_bus_lineid(arsnos) # 정류장 id를 바탕으로 노선id를 가져옴

            arsno = [] # 노선id들을 바탕으로 각 버스의 현재 입력된 정류장id와 다음정류장 이름을 가져옴
            for i in range(len(lineid)):
                arsno.append(pb.get_bus_arsno(lineid[i], bus_station_name))
            state = False
        except:
            continue

    # 정류장id와 정류장 이름이 몇 번 나왔는지 카운트 
    counts = {} # 다음 정류장을 어떤것이 많이 나왔는지 카운트
    for lists in arsno:
        for dictionaries in lists:
            for key, value in dictionaries.items():
                pair = (key, value)
                counts[pair] = counts.get(pair, 0) + 1
    # # 그 중에서 정류장id가 다른것 중 가장 높은 카운트만 분류해줌 - 다음 정류장으로 어떤 정류장이 더 많은지 알 수 있음
    result_dict = {}
    for (numeric_part, name_part), count in counts.items():
        if numeric_part in result_dict:
            if count > result_dict[numeric_part][1]:
                result_dict[numeric_part] = (name_part, count)
        else:
            result_dict[numeric_part] = (name_part, count)

    result_list = [{"arsno": numeric_part, "bstopnm": name_part} for numeric_part, (name_part, count) in result_dict.items()] 
    result_list = json.dumps(result_list, ensure_ascii=False)

    return render_template("bus_result.html",result_list=result_list, bus_station_name = bus_station_name)


@app.route("/final_result", methods = ["POST"])
def final_result():
    value = request.form.get('value')  # value : 클릭한 버튼(다음정류장)의 arsno
    name = request.form.get('name')    # name  : 클릭한 버튼의 bstopnm
    temp_list = []
    temp_list = pb.get_finalinfo_byValue(value)
    send_list = json.dumps(temp_list, ensure_ascii=False)

    return render_template("bus_final_result.html", value = value, raw_list=send_list, name_a=name)


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)