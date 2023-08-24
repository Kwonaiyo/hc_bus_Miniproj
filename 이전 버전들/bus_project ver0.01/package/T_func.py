import pymssql, requests, xmltodict, time

#데이터베이스에 접근해서 입력받은 정류장이름(ex. 영주삼거리)에 대한 정보를 DB로부터 추출하는 함수.
def get_line_id(input_station_name):
    t_st = time.time()
    rows = []
    con = pymssql.connect(#server="192.168.0.112:1433",
                      host='localhost',
                      database="kwon",
                      user="sa",
                      password="1234")

    cur=con.cursor()
    sql = ""
    sql += " SELECT arsno, nodenm "
    sql += "   FROM Bus_table "
    sql += f" WHERE nodenm = '{input_station_name}'"
    cur.execute(sql)
    rows = cur.fetchall()
    con.close()
    t_ed = time.time()
    print(t_ed-t_st, 'get_line_id')
    if(len(rows) == 0):
        return "입력하신 정류장 이름이 존재하지 않습니다. 다시 입력해 주시기 바랍니다."
    else:
        new_list = [item[0] for item in rows]
        return new_list
    
def get_businfo_byArsno(list_of_arsno, stat_name):
    temp_list = []
    temp_dict_a = {}
    # temp_dict_a['정류장이름'] = stat_name
    t_st = time.time()
    for index in range(len(list_of_arsno)):
        temp_dict_a[f'{index}'] = list_of_arsno[index]
    url = "https://apis.data.go.kr/6260000/BusanBIMS/bitArrByArsno?serviceKey="
    e_key = "9G8oPdgcH%2FkFtfiDs%2B6%2Bt4MLNu1TdiRZRNz3jOhBnZCL3VNsccc2p9%2FTM5nG3AHUXW%2BP0Vk%2BRbUkdzcW%2BIi05A%3D%3D"
    for value in temp_dict_a.values():
        temp_dict = {}
        #get_arsno : 검색에 사용할 arsno 추출
        get_arsno = f"&arsno={f'{value}'}"
        f_url = url + e_key + get_arsno

        temp_dict['arsno'] = value

        content = requests.get(f_url).content # GET요청
        dict_a = xmltodict.parse(content)     # XML을 dictionary로 파싱
        # 필요한 데이터 list 추출
        info_lists = dict_a['response']['body']['items']['item']
        # temp_dict의 'data'키에 추출한 데이터list 값 넣기.
        temp_dict['data'] = info_lists

        temp_list.append(temp_dict)
        # info_lists에서 필요한 정보들만 추출해서 날려줄까?
        # info_lists는 리스트. 내부에 dict들이 요소들로 들어있다. 
        # 파싱은 어떤 페이지(문서, html 등)에서 내가 원하는 데이터를 특정 패턴이나 순서로 추출해 가공하는 것
    t_ed = time.time()
    print(t_ed-t_st, 'get_businfo_byArsno')
    return temp_list
    
def get_needed_info(t_list):
    temp_list = []
    t_st=time.time()
    for num in range(len(t_list)):
        temp_dict = {}
        if 'lineno' in t_list[num]:
            temp_dict['노선번호'] = t_list[num]['lineno']
        if 'bstopid' in t_list[num]:
            temp_dict['정류소ID'] = t_list[num]['bstopid']
        if 'bustype' in t_list[num]:
            temp_dict['버스종류'] = t_list[num]['bustype']
        if 'lineid' in t_list[num]:
            temp_dict['노선ID'] = t_list[num]['lineid']
        if 'nodenm' in t_list[num]:
            temp_dict['정류소명'] = t_list[num]['nodenm']
        if 'min1' in t_list[num]:
            temp_dict['남은시간1'] = t_list[num]['min1']
            temp_dict['남은정류소수1'] = t_list[num]['station1']
        if 'min2' in t_list[num]:
            temp_dict['남은시간2'] = t_list[num]['min2']
            temp_dict['남은정류소수2'] = t_list[num]['station2']
        temp_list.append(temp_dict)
    t_ed=time.time()
    print(t_ed-t_st, 'get_needed_info')

    return temp_list