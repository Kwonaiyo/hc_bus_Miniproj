import pymssql
import requests, xmltodict
from bs4 import BeautifulSoup

def get_bus_id(bus_station_name):
    rows = []
    con = pymssql.connect(#server="192.168.0.112:1433",
                      host='localhost',
                      database="kwon",
                      user="sa",
                      password="1234")

    cur=con.cursor()
    sql = ""
    sql += " SELECT ARSNO "
    sql += "   FROM Bus_table "
    sql += f" WHERE NODENM = '{bus_station_name}'"
    cur.execute(sql)
    rows = cur.fetchall()
    con.close()
    if(len(rows) == 0):
        return "입력하신 정류장 이름이 존재하지 않습니다. 다시 입력해 주시기 바랍니다."
    else:
        new_list = [item[0] for item in rows]
    return new_list

def get_bus_lineid(arsno):
    change_values = []
    for i in range(0,len(arsno),2):
        url = f"https://apis.data.go.kr/6260000/BusanBIMS/bitArrByArsno?arsno={arsno[i]}&serviceKey="
        key = "eGd64%2BKKwReSBNO%2FuYgP91ORnHfKn5a8%2BbWxTQXQdqOrGeRVtf%2B%2BFZufsB1Tz6osqB5cnIOjuFycCi9qnp8iIA%3D%3D"
        url_key = url + key
        content = requests.get(url_key).content
        dict=xmltodict.parse(content)
        dict_s = dict["response"]["body"]["items"]["item"]
        for j in range(len(dict_s)):
            change_values.append(dict_s[j]["lineid"]) #리스트 안에 딕셔너리이기 때문에 하나하나 값을 넣어줌
    return change_values

def get_bus_arsno(lineid_list, bus_station_name):
    # temp_list = []
    # temp_dict_a = {}
    # for index in range(len(lineid_list)):
    #     temp_dict_a[f'{index}'] = lineid_list[index]
    url = f"https://apis.data.go.kr/6260000/BusanBIMS/busInfoByRouteId?lineid={lineid_list}&serviceKey="
    key = "eGd64%2BKKwReSBNO%2FuYgP91ORnHfKn5a8%2BbWxTQXQdqOrGeRVtf%2B%2BFZufsB1Tz6osqB5cnIOjuFycCi9qnp8iIA%3D%3D"
    
    url_key = url + key
    content = requests.get(url_key).content
    dict=xmltodict.parse(content)
    dict_s = dict["response"]["body"]["items"]["item"]
    # for value in temp_dict_a.values():
    #     temp_dict = {}
    #     temp_lineid = f'lineid={value}&serviceKey='
    #     url_key = url + temp_lineid + key

    #     temp_dict['lineid'] = value
    #     content = requests.get(url_key).content
    #     dict=xmltodict.parse(content)
    #     dict_s = dict["response"]["body"]["items"]["item"]
    #     temp_dict['data'] = dict_s

    #     temp_list.append(temp_dict)

    arsno_nextname = []  # arsno, 다음 정류장 이름
################################################################################################################################
    dict_length = len(dict_s)
    count = 0
    for i in range(dict_length):
        if bus_station_name == dict_s[i]["bstopnm"]:
            dict_arsno_nextname = {}
            dict_arsno_nextname[dict_s[i]["arsno"]] = dict_s[i+1]["bstopnm"]
            i = dict_length - i
            count += 1
            arsno_nextname.append(dict_arsno_nextname) # 마지막 정류장일 경우도 있어서 수정 해야함 (인덱스 값을 받아서 해보기)
            if count == 2:
                break;
################################################################################################################################
    wish = {'bstopnm':f'{bus_station_name}'}
    # first_index = dict_s.index(wish)
    last_index = dict_s.rindex(wish)

    # dict_arsno_firstname = {}
    # dict_arsno_firstname[dict_s[first_index]["arsno"]] = dict_s[first_index+1]["bstopnm"]
    # arsno_nextname.append(dict_arsno_firstname)

    dict_arsno_lastname = {}
    dict_arsno_lastname[dict_s[last_index]["arsno"]] = dict_s[last_index+1]["bstopnm"]
    arsno_nextname.append(dict_arsno_lastname)

#============================================================================================================


    return temp_list #딕셔너리 형식으로 넘겨줌 (arsno:bstopnm)

def get_finalinfo_byValue(arsno):
    temp_list = []
    # temp_dict_a['정류장이름'] = stat_name
    url = f"https://apis.data.go.kr/6260000/BusanBIMS/bitArrByArsno?arsno={arsno}&serviceKey="
    e_key = "9G8oPdgcH%2FkFtfiDs%2B6%2Bt4MLNu1TdiRZRNz3jOhBnZCL3VNsccc2p9%2FTM5nG3AHUXW%2BP0Vk%2BRbUkdzcW%2BIi05A%3D%3D"

    f_url = url + e_key

    content = requests.get(f_url).content # GET요청
    dict_a = xmltodict.parse(content)     # XML을 dictionary로 파싱

    # 필요한 데이터 list 추출
    temp_list = dict_a['response']['body']['items']['item']

    return temp_list
    