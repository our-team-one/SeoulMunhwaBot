
import sys
import urllib3
import json
import re
import pandas as pd
import requests

class CulturalFacilityInfo: # 구 이름을 받으면 그 구에 속한 문화공간 정보를 반환하는 클래스

    def __init__(self, SIDX, EIDX):
        self.API_START_IDX = SIDX
#        self.API_COUNT_STEP = step
        self.API_END_IDX = EIDX
        self.API_START_IDX = 1
        self.API_END_IDX = 50
        self.JSONContentForFacAddr = "" # 문화 공간의 주소 정보
        self.JSONContentForFacDetail = "" # 문화 공간의 상세 정보

    def getRegionData(self, search_word): # 예) '동작구'를 검색

        # 서울시 문화위치정보 주소 검색
        API_KEY = "54726871506a6b7936344e41656f79"
        API_URL = "http://openapi.seoul.go.kr:8088/{}/json/SearchCulturalFacilitiesAddressService/{}/{}/{}/".format(API_KEY, self.API_START_IDX, self.API_END_IDX, search_word)
        self.JSONContentForFacAddr = requests.get(API_URL).json()

        if "SearchCulturalFacilitiesAddressService" in self.JSONContentForFacAddr.keys(): # 데이터가 존재하면 True
            return True
        else:
            return False

    def getFacCodeList(self):

        # 구에 맞는 문화 공간 코드 추출하여 리스트로 만든 후 반환 - 예: '동작구'
        facCodeList = []

        data_list = self.JSONContentForFacAddr["SearchCulturalFacilitiesAddressService"]["row"]

        for idx in range(len(data_list)):
            facCodeList.append(data_list[idx]["FAC_CODE"])

        return facCodeList

    def getFacDetailList(self, facCodeList, height, width):

        result_list = []
        # 칼럼이 따로 필요없음

        # [['문화공간코드', '장르분류코드', '장르분류명', '문화공간명', '대표이미지', '주소', '전화번호', ...]] # columns row #0
        # [{"FAC_CODE":"101231", "SUBJCODE":3.0, "CODENAME":"박물관/기념관", "FAC_NAME":"서울한방진흥센터", "MAIN_IMG":"", "ADDR":"서울특별시 동대문구 약령중앙로 26", # data row #1
        # "PHNE":"02-969-9241", "FAX":"", "HOMEPAGE":"kmedi.ddm.go.kr/", ... }] data row #1
        count = 0

        for facCode in facCodeList:
            count += 1

            json_content = self.getFacDetailRowByFacCode(facCode)

            if count == 4:
                break

            if "SearchCulturalFacilitiesDetailService" in json_content.keys(): # 데이터가 있다면
                row = json_content['SearchCulturalFacilitiesDetailService']['row']
                # row[0]["FAC_DESC"] 시설소개 텍스트 수정
                #row[0]["FAC_DESC"] = self.modifyFacDesc(row[0]["FAC_DESC"])
                fac_name = row[0]["FAC_NAME"]
                home_page = row[0]["HOMEPAGE"]
                image = row[0]["MAIN_IMG"]
                line = fac_name + ", 홈페이지는 " + home_page +  ", <a href = '"  + home_page + "'>" + "<img src = '" +image + "' height =" + str(height) + " width = "+ str(width) + ">&#8205;</a>"
                #<a href="' + image + '">&#8205;</a>
                #line = fac_name + "<a href = '" + home_page + "'>" + "<img src = '" +image + "' height =" + str(height) + " width = "+ str(width) + ">" + "</a>"

                result_list.append(line)

            else:
                continue

        return result_list

    def getFacDetailRowByFacCode(self, facCode):

        # 서울시 문화공간 현황
        API_KEY = "6a74756d676a6b7933367050435a59"
        API_URL = "http://openapi.seoul.go.kr:8088/{}/json/SearchCulturalFacilitiesDetailService/{}/{}/{}/".format(API_KEY, self.API_START_IDX, self.API_END_IDX, facCode)
        JSONContent = requests.get(API_URL).json()

        return JSONContent

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
    
    if dict.get("gubun")[1:] == "w" :
        
        openApiURL = "http://aiopen.etri.re.kr:8000/WikiQA"
        accessKey = "0760f666-26d3-44cf-9432-f01710d35cf1"
        question = dict.get("wiki")[1:]
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
        
    if dict.get("gubun")[1:] == "g" :
        
# =============================================================================
#         columns = ['문화공간코드', '장르분류코드', '장르분류명', '문화공간명', '대표이미지', '주소', '전화번호',
#                    '팩스번호', '홈페이지', '관람시간', '관람료', '휴관일', '개관일자', '객석수',
#                    'X좌표', 'Y좌표', '기타사항', '시설소개', '무료구분']
# 
#         gu_name = "송파구"
#         #gu_name = dict.get("guname")[1:]
#         cfi = CulturalFacutlyInfo(1, 50, columns)
# 
#         isDataExist = cfi.getGuData(gu_name)
# 
#         if isDataExist == True:
#             facCodeResult = cfi.getFacCodeList()
#             df = cfi.getFacDetailDataFrame(facCodeResult)
#     
#             mungong = df['문화공간명'].tolist()
#             bot_answer = mungong
# =============================================================================
      
        final_result = ""
        no_data_msg = "서울시에 속한 구가 아닙니다. 올바른 구 이름을 입력하여 주십시오."

        gu_name = dict.get("regionName")[1:]
        #gu_name = "송파구"
        cfi = CulturalFacilityInfo(1, 5)

        isDataExist = cfi.getRegionData(gu_name)

        if isDataExist == True:
            facCodeResult = cfi.getFacCodeList()
            final_result = cfi.getFacDetailList(facCodeResult, 100, 100)
        else:
            final_result = no_data_msg

        bot_answer = final_result

    return { 'message': bot_answer }
