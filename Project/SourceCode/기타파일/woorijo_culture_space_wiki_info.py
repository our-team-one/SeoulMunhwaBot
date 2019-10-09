import sys
import urllib3
import json
import re
import pandas as pd
import requests
import numpy as np

class CulturalFacilityInfo: # 구 이름을 받으면 그 구에 속한 문화공간 정보를 반환하는 클래스

    def __init__(self):
        self.entireFacAddressList = self.getEntireFacAddressList() # 문화 공간 주소 정보 정체
        self.entireFacDetailList = self.getEntireFacDetailList() # 문화 공간 상세 정보 전체
        self.entireTopTenTravelSpotDataFrame = self.getTopTenTravelSpotDataFrame()  # 서울시 TOP 10 관광명소 전체 리스트

    # 서울시 TOP 10 관광명소 전체 리스트 (데이터 프레임) 불러오기
    def getTopTenTravelSpotDataFrame(self):

        url = 'https://raw.githubusercontent.com/our-team-one/SeoulMunhwaBot/master/Project/DataSet/seoullist_final.csv'
        df = pd.read_csv(url, encoding = "utf-8")

        return df

    # 서울시 TOP 10 관광명소 전체 리스트 중 구분에 해당하는 내용만 리스트로 만들어서 반환 (중복제거)
    def getTopTenTravelSpotGubun(self):

        gubun_list = set([])

        df1 = self.entireTopTenTravelSpotDataFrame[['구분']]
        df1_list = df1.values.tolist()

        for row in df1_list:
            gubun_list.add(row[0])

        return list(gubun_list)

    # 서울시 TOP 10 관광명소 전체 리스트 중 사용자가 입력한 구분에 속한
    # 정보만 리스트로 가져온다. 명칭, 이미지, 내용, 링크주소
    # 예 -> '서울관광명소'
    def getTopTenTravelSpotListByGubun(self, search_word, height, width):

        data_list = []

        df1 = self.entireTopTenTravelSpotDataFrame[['구분','명칭','이미지', '내용', '링크주소']]

        df1.replace(np.NaN, '', inplace=True)
        df1_list = df1.values.tolist()

        for row in df1_list:

            if search_word == row[0]:
                name = row[1]
                image = row[2]
                content = row[3]
                home_page = row[4]
                line = name + "<a href = '"  + home_page + "'>" + "<img src = '" +image + "' height =" + str(height) + " width = "+ str(width) + "></a>" + "<p>"+content+"</p>"

                # 서울관광명소<a href='http://..'><img src='http://..**.jpg'></a><p>아아아아</p>
                data_list.append(line)

        return data_list

    # 서울시 문화공간 주소정보 전체 리스트 불러오기
    def getEntireFacAddressList(self):

        API_KEY = "54726871506a6b7936344e41656f79"
        API_URL = "http://openapi.seoul.go.kr:8088/{}/json/SearchCulturalFacilitiesAddressService/{}/{}/".format(API_KEY, 1, 99)
        JSONContent = requests.get(API_URL).json()

        # "SearchCulturalFacilitiesAddressService"
        return JSONContent['SearchCulturalFacilitiesAddressService']['row']

    # 서울시 문화공간 상세정보 전체 리스트 불러오기
    def getEntireFacDetailList(self):

        # 서울시 문화공간 전체 현황
        API_KEY = "6a74756d676a6b7933367050435a59"
        API_URL = "http://openapi.seoul.go.kr:8088/{}/json/SearchCulturalFacilitiesDetailService/{}/{}/".format(API_KEY, 1, 99)
        JSONContent = requests.get(API_URL).json()

        return JSONContent['SearchCulturalFacilitiesDetailService']['row']

    # 사용자가 입력한 구 이름에 속한 문화공간 리스트를 만들어 리턴
    def getFacCodeList(self, search_word):

        facCodeList = []

        # self.entireFacAddressList

        for row in self.entireFacAddressList:

            if type(row["ADDR"]) != type(None):
                if row["ADDR"].find(search_word) != -1:
                    facCodeList.append(row["FAC_CODE"])


        return facCodeList

    # 사용자가 구를 입력할 때 장르 (CODENAME)을 중복 없는 리스트로 만들어서 리턴
    def getCodeNameList(self, search_word):

        se = set([])

        for row in self.entireFacAddressList:

            if type(row["ADDR"]) != type(None):
                if row["ADDR"].find(search_word) != -1:
                    se.add(row["CODENAME"])

        return list(se)

    # 사용자가 장르 (예: 공연장) 을 입력하였을 때 해당되는 구를 가져와야 된다.
    # 먼저 상세정보 테이블을 찾아서 장르 (CODENAME) 에 맞는 문화공간코드를 추출
    # 그리고, 문화공간코드로 구를 찾아서 리스트로 만들어서 리턴
    def getGuNameList(self, search_word):

        se = set([])
        tmp_list = []

        for row in self.entireFacDetailList:
            if search_word == row["CODENAME"]:
                tmp_list.append(row["ADDR"])

        for row in tmp_list:
            if type(row) != type(None):
                lst = re.findall('[가-힣]+구', row)
                se.add(lst[0])

        return list(se)

    # 사용자가 입력한 구에 속한 문화공간코드를 바탕으로 리스트를 만든 후 다시 리스트에서 장르를 키로 해서 조회
    # 최종 데이터를 반환
    def getFacDetailListByAll(self, gu_name, genre, height, width):

        result_list_by_gu = []
        #result_list_by_gu_and_genre = []

        result_list = []

        final_choice = []

        facCodeList = self.getFacCodeList(gu_name)

        # 구로 검색해져 가져온 문화공간코드를 먼저 1차 필터링
        if len(facCodeList) != 0:
            # self.entireFacDetailList
            for row in self.entireFacDetailList:
                if row["FAC_CODE"] in facCodeList:

                    result_list_by_gu.append(row)

                    # fac_name = row["FAC_NAME"]
                    # home_page = row["HOMEPAGE"]
                    # image = row["MAIN_IMG"]
                    # line = fac_name + ", 홈페이지는 " + home_page +  ", <a href = '"  + home_page + "'>" + "<img src = '" +image + "' height =" + str(height) + " width = "+ str(width) + ">&#8205;</a>"

                    # result_list.append(line)

                else:
                    continue

            for row in result_list_by_gu:
                if genre == row["CODENAME"]: # genre 에 매칭되는 것만 추가
                    fac_name = row["FAC_NAME"]
                    home_page = row["HOMEPAGE"]
                    image = row["MAIN_IMG"]
                    line = fac_name +  "<a href = '"  + home_page + "'>" + "<img src = '" +image + "' height =" + str(height) + " width = "+ str(width) + "></a>"

                    result_list.append(line)
                else:
                    continue

        final_choice.append(np.random.choice(result_list))

        return final_choice

    # 사용자가 위키에 물어보기 위해 질문을 던졌을 경우 인공지능이 답변을 찾아내어 반환해주는 로직
    def extractSearchResultFromWiki(self, question):

        openApiURL = "http://aiopen.etri.re.kr:8000/WikiQA"
        accessKey = "0760f666-26d3-44cf-9432-f01710d35cf1"
        #question = dict.get("wiki_sentence")
        type = "hybridqa"

        requestJson = {
        "access_key": accessKey,
        "argument": {
          "question": question,
            "type": type
        }
        }

        http = urllib3.PoolManager()
        response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
        )

        r = response.data.decode('utf-8')
        json_obj = json.loads(r)

        if response.status == 200 and json_obj['result'] == 0:

            if len(json_obj['return_object']['WiKiInfo']['AnswerInfo'])==0:
                if json_obj['return_object']['WiKiInfo']['IRInfo'][0]['sent']=='':
                    bot_answer = "문의 하신 내용에 답변 드리지 못해 죄송합니다."
                else :
                    bot_answer = "문의하신 내용에 적절한 답변은 아닐지 모르나 " + json_obj['return_object']['WiKiInfo']['IRInfo'][0]['sent']
            else :
                if json_obj['return_object']['WiKiInfo']['AnswerInfo'][0]['confidence'] > 0.9 :
                    bot_answer = json_obj['return_object']['WiKiInfo']['AnswerInfo'][0]['answer']
                else :
                    bot_answer = "문의하신 내용에 적절한 답변은 아닐지 모르나 " + json_obj['return_object']['WiKiInfo']['IRInfo'][0]['sent']
        else :
            bot_answer = "ETRI가 연결이 안되서 답변을 드리지 못하고 있습니다."

        return bot_answer

    # 시설소개 관련 html 태그 제거
    def modifyFacDesc(self, fac_desc):

        cleaner = re.compile("<.*?>")

        text = re.sub(cleaner, '', fac_desc)

        text = text.replace("&nbsp;", "")
        text = text.replace("\n", "")
        text = text.replace("\r", "")
        text = text.replace("&#39;", "")
        text = text.strip()

        return text



def main(dict):

    #bot_answer = ""

    if dict.get("node") == "wiki" :

        question = dict.get("wiki_sentence")

        cfi = CulturalFacilityInfo()

        bot_answer = cfi.extractSearchResultFromWiki(question)

        return { 'message': bot_answer }

    # 사용자가 구를 입력했을 때 구에 해당하는 모든 장르를 리턴
    if dict.get("node") == "culture_gu" :

        final_result = []
        no_data_msg = "귀하가 입력하신 단어에 맞는 검색결과가 없습니다. 다시 입력하여 주세요."

        gu_name = dict.get("region")
        #gu_name = "송파구"
        cfi = CulturalFacilityInfo()

        final_result = cfi.getCodeNameList(gu_name)

        if len(final_result) == 0:
            final_result.append(no_data_msg)

        return { 'message': final_result }

    # 사용자가 장르를 입력했을 때 장르에 해당하는 모든 구를 리턴
    if dict.get("node") == "culture_genre" :

        final_result = []
        no_data_msg = "귀하가 입력하신 단어에 맞는 검색결과가 없습니다. 다시 입력하여 주세요."

        genre = dict.get("genre")
        cfi = CulturalFacilityInfo()

        final_result = cfi.getGuNameList(genre)

        if len(final_result) == 0:
            final_result.append(no_data_msg)

        return { 'message': final_result }

    if dict.get("node") == "culture_all" :

        final_result = []
        no_data_msg = "귀하가 입력하신 단어에 맞는 검색결과가 없습니다. 다시 입력하여 주세요."

        gu_name = dict.get("region")
        genre = dict.get("genre")

        cfi = CulturalFacilityInfo()

        final_result = cfi.getFacDetailListByAll(gu_name, genre, 100, 100)

        if len(final_result) == 0:
            final_result.append(no_data_msg)

        return { 'message': final_result }

    # TOP 10에 속한 구분을 다 반환한다.
    if dict.get("node") == "callback_top" :

        final_result = []
        no_data_msg = "카테고리 없음"

        cfi = CulturalFacilityInfo()

        final_result = cfi.getTopTenTravelSpotGubun()

        if len(final_result) == 0:
            final_result.append(no_data_msg)

        return { 'message': final_result }

    # callback_top_cate
    # 사용자가 선택한 구분명에 따른 TOP 10 정보를 반환
    # '서울관광명소'
    if dict.get("node") == "callback_top_cate" :

        final_result = []
        no_data_msg = "카테고리에 맞는 데이터 없음"

        category = dict.get("category")

        cfi = CulturalFacilityInfo()

        final_result = cfi.getTopTenTravelSpotListByGubun(category, 100, 100)

        if len(final_result) == 0:
            final_result.append(no_data_msg)

        return { 'message': final_result }
