import sys
import requests
import pandas as pd
import re
import json
#import xmltodict as x2d
#import geocoder

# 파라메터로 '동작구'를 넣어서 호출했을 때 나오는 결과
# API URL: http://openapi.seoul.go.kr:8088/54726871506a6b7936344e41656f79/json/SearchCulturalFacilitiesAddressService/1/5/%EB%8F%99%EC%9E%91%EA%B5%AC/
# {
#     "SearchCulturalFacilitiesAddressService":{
#         "list_total_count":8,
#         "RESULT":{
#             "CODE":"INFO-000",
#             "MESSAGE":"정상 처리되었습니다"
#         },
#         "row":[
#             {
#                 "FAC_CODE":"100825",
#                 "SUBJCODE":6.0,
#                 "CODENAME":"문화예술회관",
#                 "FAC_NAME":"사당문화회관",
#                 "ADDR":"서울  동작구 사당동 248-6 )"
#             },
#             {
#                 "FAC_CODE":"100157",
#                 "SUBJCODE":8.0,
#                 "CODENAME":"도서관",
#                 "FAC_NAME":"동작도서관",
#                 "ADDR":"서울  동작구 노량진동 310-150 )"
#             },
#             {
#                 "FAC_CODE":"100824",
#                 "SUBJCODE":11.0,
#                 "CODENAME":"기타",
#                 "FAC_NAME":"흑석체육센터",
#                 "ADDR":"서울  동작구 흑석동  현충로 73"
#             },
#             {
#                 "FAC_CODE":"100828",
#                 "SUBJCODE":8.0,
#                 "CODENAME":"도서관",
#                 "FAC_NAME":"동작구 통합도서관",
#                 "ADDR":"서울  동작구 대방동 49-6 )"
#             },
#             {
#                 "FAC_CODE":"100822",
#                 "SUBJCODE":11.0,
#                 "CODENAME":"기타",
#                 "FAC_NAME":"동작구청",
#                 "ADDR":"서울  동작구 노량진동 47-2 )"
#             }
#         ]
#     }
# }



# 잘못된 구를 입력했을 때 나오는 결과 - 예) 소사구
# {
#     "RESULT":{
#         "CODE":"INFO-200",
#         "MESSAGE":"해당하는 데이터가 없습니다."
#     }
# }


# 특정 문화공간코드에 해당하는 상세정보 100157
# {
#     "SearchCulturalFacilitiesDetailService":{
#         "list_total_count":1,
#         "RESULT":{
#             "CODE":"INFO-000",
#             "MESSAGE":"정상 처리되었습니다"
#         },
#         "row":[
#             {
#                 "FAC_CODE":"100157",
#                 "SUBJCODE":8.0,
#                 "CODENAME":"도서관",
#                 "FAC_NAME":"동작도서관",
#                 "MAIN_IMG":"http://culture.seoul.go.kr/data/cf/20111020170003.jpg",
#                 "ADDR":"서울  동작구 노량진동 310-150 )",
#                 "PHNE":"02-823-6417",
#                 "FAX":"02-812-6511",
#                 "HOMEPAGE":"http://djlib.sen.go.kr/",
#                 "OPENHOUR":"",
#                 "ENTR_FEE":"",
#                 "CLOSEDAY":"",
#                 "OPEN_DAY":"",
#                 "SEAT_CNT":"",
#                 "X_COORD":37.5059908,
#                 "Y_COORD":126.9401667,
#                 "ETC_DESC":"■ 대 지 : 1,910 ㎡ (579평)\r\n■ 건 물 : 1,974㎡ (597평), 철근조 지상3층 지하1층",
#                 "FAC_DESC":"<p>동작도서관은 1991년 5월 6일에 개관한 동작구 공공도서관으로 현재 9만 여권의 장서와 각종 간행물, 멀티미디어자료를 갖추고 21C를 열어가는 정보문화센터로서, 지역 주민들의 정보문화욕구 충족을 위한 각종 프로그램을 개설 하여 이용자들의 생활 속의 소중한 문화공간으로 끊임없이 발전하고 있습니다.<br />\r\n\r\n\r\n\r\n<br />\r\n\r\n\r\n\r\n</p><p><img style=&quot;border: 1px solid rgb(255, 255, 255); float: left;&quot; src=&quot;/data/cf/20111020170920.jpg&quot; /></p>",
#                 "ENTRFREE":"0"
#             }
#         ]
#     }
# }


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
                line = fac_name + "<a href = '" + home_page + "'>" + "<img src = '" +image + "' height =" + str(height) + " width = "+ str(width) + ">" + "</a>"

                result_list.append(line)

            else:
                continue

        return result_list

    # fac code & code name search
    # "동작구"에 관한 문화공간코드 상세정보 데이터 중 장르에 관련된 정보만 따로 추출
    def getFacDetailListTwo(self, facCodeList, genre, height, width):

        result_list = []

        result_list_by_genre = []

        for facCode in facCodeList:

            json_content = self.getFacDetailRowByFacCode(facCode)

            if "SearchCulturalFacilitiesDetailService" in json_content.keys(): # 데이터가 있다면
                row = json_content['SearchCulturalFacilitiesDetailService']['row']
                # row[0]["FAC_DESC"] 시설소개 텍스트 수정
                #row[0]["FAC_DESC"] = self.modifyFacDesc(row[0]["FAC_DESC"])
                # fac_name = row[0]["FAC_NAME"]
                # home_page = row[0]["HOMEPAGE"]
                # image = row[0]["MAIN_IMG"]
                # line = fac_name + "<a href = '" + home_page + "'>" + "<img src = '" +image + "' height =" + str(height) + " width = "+ str(width) + ">" + "</a>"



                result_list.append(row)

            else:
                continue


        # CODENAME 이 '도서관' 인 것만 row 로 추가

        for dic in result_list:
            # "CODENAME"
            if dic[0]["CODENAME"] == genre:

                fac_name = dic[0]["FAC_NAME"]
                home_page = dic[0]["HOMEPAGE"]
                image = dic[0]["MAIN_IMG"]
                line = fac_name + "<a href = '" + home_page + "'>" + "<img src = '" +image + "' height =" + str(height) + " width = "+ str(width) + ">" + "</a>"

                result_list_by_genre.append(line)
            else:
                continue


        return result_list_by_genre


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

    # columns = ['문화공간코드', '장르분류코드', '장르분류명', '문화공간명', '대표이미지', '주소', '전화번호',
    #       '팩스번호', '홈페이지', '관람시간', '관람료', '휴관일', '개관일자', '객석수',
    #       'X좌표', 'Y좌표', '기타사항', '시설소개', '무료구분']

    final_result = ""
    no_data_msg = "서울시에 속한 구가 아닙니다. 올바른 구 이름을 입력하여 주십시오."

    gu_name = dict.get("region")[1:]
    genre = dict.get("codename")

    cfi = CulturalFacilityInfo(1, 5)

    isDataExist = cfi.getRegionData(gu_name)

    if isDataExist == True:
        facCodeResult = cfi.getFacCodeList()
        #final_result = cfi.getFacDetailList(facCodeResult, 100, 100)

        # getFacDetailListTwo
        final_result = cfi.getFacDetailListTwo(facCodeResult, genre, 100, 100)

    else:
        final_result = no_data_msg

    return { "result" : final_result }
